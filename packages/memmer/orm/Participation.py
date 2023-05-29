# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Optional

import datetime

from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .Base import Base
from .Member import Member
from .Session import Session


class Participation(Base):
    __tablename__ = "participations"

    member_id: Mapped[int] = mapped_column(
        ForeignKey(Member.id, onupdate="CASCADE", ondelete="CASCADE"), primary_key=True
    )
    session_id: Mapped[int] = mapped_column(
        ForeignKey(Session.id, onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    since: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    until: Mapped[Optional[datetime.datetime]]
