# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Any, List, Sequence

from datetime import date, datetime

from memmer.orm import Member

from sqlalchemy import Select, or_


def active_members(
    members: Sequence[Member], target_date: date = datetime.now().date()
) -> List[Member]:
    """The members active at ``target_date`` (the list companion to
    :func:`is_active`): a member who has already entered and not yet exited."""
    return [member for member in members if is_active(member, target_date)]


def is_active(member: Member, target_date: date = datetime.now().date()) -> bool:
    if member.entry_date > target_date:
        # No member yet
        return False

    if member.exit_date is None:
        return True

    return member.exit_date > target_date


def restrict_to_active_members(query: Select[Any], target_date: date) -> Select[Any]:
    return query.where(
        or_(Member.exit_date == None, Member.exit_date > target_date)
    ).where(Member.entry_date <= target_date)
