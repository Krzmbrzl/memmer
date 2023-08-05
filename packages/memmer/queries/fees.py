# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import List

from decimal import Decimal
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import delete

import memmer.orm as morm
from memmer import BasicFeeAdultsKey, BasicFeeYouthsKey
from memmer.queries import get_relatives

from .fixed_costs import get_fixed_cost


def get_age(member: morm.Member) -> int:
    """Gets the age of the given member in full years"""
    today = date.today()

    age = today.year - member.birthday.year

    if today.month > member.birthday.month:
        age += 1
    elif today.month == member.birthday.month and today.day >= member.birthday.day:
        age += 1

    return age


def compute_monthly_fee(
    session: Session, member: morm.Member, account_for_siblings: bool = True
) -> Decimal:
    """Computes the given member's monthly fee"""
    member_age: int = get_age(member)

    fee: Decimal = Decimal(0)

    # First part: base fee
    if member_age < 18:
        fee += get_fixed_cost(session=session, key=BasicFeeYouthsKey)
    else:
        fee += get_fixed_cost(session=session, key=BasicFeeAdultsKey)

    # Then add the training fees for the actively participating sessions
    session_fees: List[Decimal] = []
    for current_session in member.participating_sessions:
        session_fees.append(current_session.membership_fee)

    session_fees = sorted(session_fees, reverse=True)
    # The most expensive session has to be payed 100%, the second expensive 75% and all others are for free
    if len(session_fees) >= 1:
        fee += session_fees[0]
    if len(session_fees) >= 2:
        fee += Decimal(0.75) * session_fees[1]

    # Potentially account for siblings that might reduce the fee:
    # The most expensive child pays full, everyone else pays only 50%
    # (only siblings < 18 years old are considered)
    if account_for_siblings and member_age < 18:
        relatives = get_relatives(session=session, member=member)
        relatives = [x for x in relatives if get_age(x) < 18]
        relative_fees = [
            compute_monthly_fee(
                session=session, member=current, account_for_siblings=False
            )
            for current in relatives
        ]

        if max(relative_fees) > fee:
            fee /= 2
        elif max(relative_fees) == fee:
            # There is a tie in terms of the fee -> now we have to uniquely determine
            # the sibling who has to pay fully
            candidates = [
                relatives[i] for i in range(len(relatives)) if relative_fees[i] == fee
            ]
            candidates.append(member)

            candidate_names = [
                current.first_name + current.last_name for current in candidates
            ]
            # We assume that there are no duplicates in here
            assert len(candidate_names) == len(set(candidate_names))

            full_paying_name = sorted(candidate_names)[0]

            if member.first_name + member.last_name != full_paying_name:
                fee /= 2

    return fee


def compute_total_fee(session: Session, member: morm.Member) -> Decimal:
    """Computes the current fee of the given member. The total fee consists of the
    monthly fee plus all outstanding one-time fees"""

    fee = compute_monthly_fee(session, member)

    for current_fee in member.one_time_fees:
        fee += current_fee.amount

    return fee


def clear_one_time_fees(session: Session, member: morm.Member) -> None:
    """Deletes all one-time fees associated with the given member"""
    for current_fee in member.one_time_fees:
        session.execute(
            delete(morm.OneTimeFee).where(morm.OneTimeFee.id == current_fee.id)
        )
