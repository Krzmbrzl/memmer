# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Any

from datetime import date

from memmer.orm import Member

from sqlalchemy import Select, or_


def is_active(member: Member, target_date: date) -> bool:
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
