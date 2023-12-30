# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Optional

import datetime

from sqlalchemy.orm import Session
from sqlalchemy import delete, select

from memmer.orm import Participation, Member, ArchivedOneTimeFee, OneTimeFee


def clear_outdated_entries(session: Session) -> None:
    """Remove all outdated entries in the database"""
    today = datetime.datetime.now().date()
    three_months_ago = today - datetime.timedelta(days=3 * 30)

    session.execute(delete(Participation).where(Participation.until < today))
    session.execute(delete(Member).where(Member.exit_date < today))
    session.execute(
        delete(ArchivedOneTimeFee).where(ArchivedOneTimeFee.billed < three_months_ago)
    )


def archive_onetimecosts(session: Session, member: Optional[Member]) -> None:
    """Moves all one-time costs (associated with the given member) into the archive table"""
    if member is not None:
        fees = member.one_time_fees
    else:
        fees = session.scalars(select(OneTimeFee)).all()

    for fee in fees:
        archived = ArchivedOneTimeFee.fromFee(fee)
        session.add(archived)
        session.delete(fee)
