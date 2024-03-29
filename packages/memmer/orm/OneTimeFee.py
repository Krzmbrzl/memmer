# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from decimal import Decimal
import datetime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from .Base import Base
from .Member import Member


class OneTimeFee(Base):
    __tablename__ = "onetimecosts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(
        ForeignKey(Member.id, onupdate="CASCADE", ondelete="CASCADE")
    )
    reason: Mapped[str]
    amount: Mapped[Decimal]

    member: Mapped[Member] = relationship(passive_deletes=True)


class ArchivedOneTimeFee(Base):
    __tablename__ = "archived_onetimecosts"

    @classmethod
    def fromFee(cls, fee: OneTimeFee):
        return cls(member_id=fee.member_id, reason=fee.reason, amount=fee.amount)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(
        ForeignKey(Member.id, onupdate="CASCADE", ondelete="CASCADE")
    )
    reason: Mapped[str]
    amount: Mapped[Decimal]
    billed: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
