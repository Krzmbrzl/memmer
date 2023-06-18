# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import List

from decimal import Decimal

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column

from .Base import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    membership_fee: Mapped[Decimal]

    # Relations
    members: Mapped[List["Member"]] = relationship(  # type:ignore
        back_populates="participating_sessions", secondary="participations"
    )
    trainers: Mapped[List["Member"]] = relationship(  # type: ignore
        back_populates="trained_sessions", secondary="trainers"
    )
