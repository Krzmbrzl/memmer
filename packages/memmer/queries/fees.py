# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import List

from decimal import Decimal
from datetime import date, datetime

from sqlalchemy.orm import Session
from sqlalchemy import select

import memmer.orm as morm
from memmer import BasicFeeAdultsKey, BasicFeeYouthsKey, BasicFeeTrainersKey
from memmer.queries import get_relatives
from memmer.utils import nominal_year_diff, is_active

from .fixed_costs import get_fixed_cost


def delete_all(collection, indices):
    for i in sorted(indices, reverse=True):
        del collection[i]

    return collection


def compute_discount(
    session: Session, member: morm.Member, target_date: date
) -> Decimal:
    """Computes a discount factor that has to be applied to the given member's fee"""
    relatives = get_relatives(session=session, member=member)

    relatives = [x for x in relatives if is_active(x, target_date)]

    if len(relatives) == 0:
        return Decimal(1)

    # Also include the current member in the set of relatives
    relatives.append(member)

    fees = [
        compute_monthly_fee(
            session=session, member=x, apply_discounts=False, target_date=target_date
        )
        for x in relatives
    ]

    child_indices = []
    adult_indices = []
    for i in range(len(relatives)):
        if nominal_year_diff(relatives[i].birthday, target_date) < 18:
            child_indices.append(i)
        else:
            adult_indices.append(i)

    assert len(child_indices) + len(adult_indices) == len(relatives)
    member_index = len(relatives) - 1
    assert relatives[member_index] == member

    if len(adult_indices) >= 2 and len(child_indices) >= 2:
        # Family discount
        sorted_adults = sorted(adult_indices, key=lambda x: fees[x], reverse=True)
        # Only two adults can take part in the family discount
        sorted_adults = sorted_adults[0:2]

        overall = child_indices + sorted_adults
        overall = sorted(
            overall, key=lambda x: (fees[x], relatives[x].id), reverse=True
        )

        if member_index in overall:
            if overall.index(member_index) >= 4:
                if member_index in child_indices:
                    # These go for free
                    return Decimal(0)
            elif overall.index(member_index) >= 2:
                return Decimal("0.5")

        # No discount for this family member
        return Decimal(1)

    if member_index in child_indices and len(child_indices) >= 2:
        # Sibling discount
        child_fees = sorted([fees[i] for i in child_indices], reverse=True)
        assert child_fees[0] == max(child_fees)

        if fees[member_index] < child_fees[0]:
            # 50% discount for siblings that don't have the most expensive monthly fee
            return Decimal("0.5")

        if child_fees[0] == child_fees[1]:
            # There are multiple children paying the highest monthly fee
            # Only one of them has to pay fully
            filtered = [x for x in child_indices if fees[x] == child_fees[0]]
            highest_paying = sorted(filtered, key=lambda x: relatives[x].id)[0]

            if member_index != highest_paying:
                return Decimal("0.5")

        # No discount for this sibling
        return Decimal(1)

    # No discount applies
    return Decimal(1)


def compute_monthly_fee(
    session: Session,
    member: morm.Member,
    apply_discounts: bool = True,
    target_date: date = datetime.now().date(),
) -> Decimal:
    """Computes the given member's monthly fee"""

    if member.exit_date is not None and member.exit_date <= target_date:
        return Decimal(0)
    if member.entry_date > target_date:
        return Decimal(0)

    # First check if there exists a fee override for this member as this will make any of the below
    # superfluous
    override = session.scalar(
        select(morm.FeeOverride).where(morm.FeeOverride.member_id == member.id)
    )

    if not override is None:
        return override.amount

    member_age: int = nominal_year_diff(member.birthday, target_date)

    fee: Decimal = Decimal(0)

    if not member.is_honorary_member:
        # Base fee
        if len(member.trained_sessions) > 0:
            # Trainer
            fee += get_fixed_cost(session=session, key=BasicFeeTrainersKey)
        elif member_age < 18:
            fee += get_fixed_cost(session=session, key=BasicFeeYouthsKey)
        else:
            fee += get_fixed_cost(session=session, key=BasicFeeAdultsKey)

    # Then add the training fees for the actively participating sessions
    session_fees: List[Decimal] = []
    for current_session in member.participating_sessions:
        participation = session.scalar(
            select(morm.Participation)
            .where(morm.Participation.member_id == member.id)
            .where(morm.Participation.session_id == current_session.id)
        )
        assert participation != None

        if participation.since <= target_date and (
            participation.until is None or participation.until > target_date
        ):
            session_fees.append(current_session.membership_fee)

    session_fees = sorted(session_fees, reverse=True)
    # The most expensive session has to be payed 100%, the second expensive 75% and all others are for free
    if len(session_fees) >= 1:
        fee += session_fees[0]
    if len(session_fees) >= 2:
        fee += Decimal(0.75) * session_fees[1]

    if apply_discounts:
        discount = compute_discount(
            session=session, member=member, target_date=target_date
        )
        fee *= discount

    return fee


def compute_total_fee(
    session: Session, member: morm.Member, target_date: date = datetime.now().date()
) -> Decimal:
    """Computes the current fee of the given member. The total fee consists of the
    monthly fee plus all outstanding one-time fees"""

    fee = compute_monthly_fee(session=session, member=member, target_date=target_date)

    for current_fee in member.one_time_fees:
        fee += current_fee.amount

    return fee
