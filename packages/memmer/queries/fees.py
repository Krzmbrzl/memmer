# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Callable, List, Optional

from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date, datetime

from sqlalchemy.orm import Session
from sqlalchemy import select

import memmer.orm as morm
from memmer import BasicFeeAdultsKey, BasicFeeYouthsKey, BasicFeeTrainersKey
from memmer.queries import get_relatives
from memmer.utils import nominal_year_diff, is_active

from .fixed_costs import get_fixed_cost


@dataclass
class FeeComponent:
    """One contribution to a member's fee, recorded as the fee is computed.

    ``kind`` is one of ``base``, ``session``, ``onetime``, ``discount`` or
    ``override``. ``base_amount`` is the undiscounted figure, ``ratio`` the
    factor applied to it (e.g. ``0.75`` for the second session or a sibling
    discount), and ``amount`` the resulting contribution. For a ``discount``
    component ``base_amount``/``amount`` are the monthly sum before/after the
    discount, so the breakdown can show the discount without re-deriving it."""

    kind: str
    label: str
    base_amount: Decimal
    ratio: Decimal
    amount: Decimal


@dataclass
class FeeBreakdown:
    """The itemized components behind a member's total fee.

    ``total`` is taken straight from :func:`compute_total_fee`, so the breakdown
    never re-implements the fee arithmetic and cannot drift from it."""

    components: List[FeeComponent] = field(default_factory=list)
    total: Decimal = Decimal(0)


def delete_all(collection, indices):
    for i in sorted(indices, reverse=True):
        del collection[i]

    return collection


def compute_discount(
    session: Session,
    member: morm.Member,
    target_date: date,
    member_id: Optional[int] = None,
) -> Decimal:
    """Computes a discount factor that has to be applied to the given member's fee.

    ``member`` may be a transient stand-in for a persisted member (e.g. the
    unsaved member the GUI previews), whose own ``id`` isn't populated. Pass
    ``member_id`` so the tie-break ranks it as its persisted self; it defaults
    to ``member.id`` for ordinary, persisted members.
    """
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

    effective_member_id = member.id if member_id is None else member_id

    def tie_break_id(index):
        # Used only to deterministically pick a single member when several tie
        # on fee. The member under evaluation is ranked by its real id (which
        # for a transient preview member is supplied via ``member_id``). A
        # missing id (a never-saved member) sorts after any persisted one, so
        # None is never compared with an int.
        current_id = (
            effective_member_id if index == member_index else relatives[index].id
        )
        return (current_id is None, current_id if current_id is not None else 0)

    if len(adult_indices) >= 2 and len(child_indices) >= 2:
        # Family discount
        sorted_adults = sorted(adult_indices, key=lambda x: fees[x], reverse=True)
        # Only two adults can take part in the family discount
        sorted_adults = sorted_adults[0:2]

        overall = child_indices + sorted_adults
        overall = sorted(
            overall, key=lambda x: (fees[x], *tie_break_id(x)), reverse=True
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
            highest_paying = sorted(filtered, key=tie_break_id)[0]

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
    record: Optional[Callable[[FeeComponent], None]] = None,
) -> Decimal:
    """Computes the given member's monthly fee.

    When ``record`` is given, it is invoked with a :class:`FeeComponent` for
    each contribution as it is computed, so a caller can obtain an itemized
    breakdown without re-implementing any of the logic below."""

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
        if record is not None:
            record(
                FeeComponent(
                    kind="override",
                    label="",
                    base_amount=override.amount,
                    ratio=Decimal(1),
                    amount=override.amount,
                )
            )
        return override.amount

    member_age: int = nominal_year_diff(member.birthday, target_date)

    fee: Decimal = Decimal(0)

    if not member.is_honorary_member:
        # Base fee
        if len(member.trained_sessions) > 0:
            # Trainer
            base_key = BasicFeeTrainersKey
        elif member_age < 18:
            base_key = BasicFeeYouthsKey
        else:
            base_key = BasicFeeAdultsKey

        base_fee = get_fixed_cost(session=session, key=base_key)
        fee += base_fee
        if record is not None:
            record(
                FeeComponent(
                    kind="base",
                    label=base_key,
                    base_amount=base_fee,
                    ratio=Decimal(1),
                    amount=base_fee,
                )
            )

    # Fetch all of the member's participations up front, keyed by session, so
    # the loop below doesn't issue one SELECT per participating session.
    participations = {
        p.session_id: p
        for p in session.scalars(
            select(morm.Participation).where(
                morm.Participation.member_id == member.id
            )
        ).all()
    }

    # Then add the training fees for the actively participating sessions. Keep
    # the session name alongside the fee so a breakdown can name each course.
    session_fees: List[tuple] = []
    for current_session in member.participating_sessions:
        participation = participations.get(current_session.id)

        if participation is None or (
            participation.since <= target_date
            and (participation.until is None or participation.until > target_date)
        ):
            session_fees.append((current_session.membership_fee, current_session.name))

    # Sort by fee only (with the name as a deterministic tie-break) so the sum
    # is identical regardless of insertion order.
    session_fees = sorted(session_fees, key=lambda e: (e[0], e[1]), reverse=True)
    # The most expensive session has to be payed 100%, the second expensive 75% and all others are for free
    if len(session_fees) >= 1:
        amount, name = session_fees[0]
        fee += amount
        if record is not None:
            record(
                FeeComponent(
                    kind="session",
                    label=name,
                    base_amount=amount,
                    ratio=Decimal(1),
                    amount=amount,
                )
            )
    if len(session_fees) >= 2:
        amount, name = session_fees[1]
        contribution = Decimal("0.75") * amount
        fee += contribution
        if record is not None:
            record(
                FeeComponent(
                    kind="session",
                    label=name,
                    base_amount=amount,
                    ratio=Decimal("0.75"),
                    amount=contribution,
                )
            )

    if apply_discounts:
        discount = compute_discount(
            session=session, member=member, target_date=target_date
        )
        discounted = fee * discount
        if record is not None:
            record(
                FeeComponent(
                    kind="discount",
                    label="",
                    base_amount=fee,
                    ratio=discount,
                    amount=discounted,
                )
            )
        fee = discounted

    return fee


def compute_total_fee(
    session: Session,
    member: morm.Member,
    target_date: date = datetime.now().date(),
    record: Optional[Callable[[FeeComponent], None]] = None,
) -> Decimal:
    """Computes the current fee of the given member. The total fee consists of the
    monthly fee plus all outstanding one-time fees.

    ``record`` behaves as in :func:`compute_monthly_fee`; one-time fees are
    emitted as ``onetime`` components in addition to the monthly ones."""

    fee = compute_monthly_fee(
        session=session, member=member, target_date=target_date, record=record
    )

    for current_fee in member.one_time_fees:
        fee += current_fee.amount
        if record is not None:
            record(
                FeeComponent(
                    kind="onetime",
                    label=current_fee.reason,
                    base_amount=current_fee.amount,
                    ratio=Decimal(1),
                    amount=current_fee.amount,
                )
            )

    return fee


def collect_fee_breakdown(
    session: Session,
    member: morm.Member,
    target_date: date = datetime.now().date(),
) -> FeeBreakdown:
    """Returns the itemized breakdown behind the member's total fee.

    This is a thin wrapper around :func:`compute_total_fee`: it records the
    components it already computes and keeps that function's return value as the
    authoritative total. It contains no fee logic of its own."""

    breakdown = FeeBreakdown()
    breakdown.total = compute_total_fee(
        session=session,
        member=member,
        target_date=target_date,
        record=breakdown.components.append,
    )
    return breakdown
