# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Optional, List

import datetime
import enum

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import CheckConstraint

from .Base import Base


class Gender(enum.Enum):
    Male = 0
    Female = 1
    Diverse = 2


class Member(Base):
    __tablename__ = "members"
    __table_args__ = (
        CheckConstraint("iban IS NOT NULL OR sepa_mandate_date IS NULL"),
        CheckConstraint("bic IS NOT NULL OR sepa_mandate_date IS NULL"),
        CheckConstraint("account_owner IS NOT NULL OR sepa_mandate_date IS NULL"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Personal data
    first_name: Mapped[str]
    last_name: Mapped[str]
    birthday: Mapped[datetime.date]
    gender: Mapped[Gender]

    # Address
    street: Mapped[str]
    street_number: Mapped[str]
    postal_code: Mapped[str]
    city: Mapped[str]

    # Contact information
    phone_number: Mapped[Optional[str]]
    email_address: Mapped[Optional[str]]

    # Account details
    iban: Mapped[Optional[str]]
    bic: Mapped[Optional[str]]
    account_owner: Mapped[Optional[str]]

    sepa_mandate_date: Mapped[Optional[datetime.date]]

    entry_date: Mapped[datetime.date] = mapped_column(default=datetime.datetime.utcnow)
    exit_date: Mapped[Optional[datetime.date]]

    # Honorary members don't have to pay the base fee
    is_honorary_member: Mapped[bool] = mapped_column(default=False)

    # Relations
    participating_sessions: Mapped[List["Session"]] = relationship(  # type: ignore
        back_populates="members", secondary="participations", passive_deletes=True
    )
    trained_sessions: Mapped[List["Session"]] = relationship(  # type: ignore
        back_populates="trainers", secondary="trainers", passive_deletes=True
    )

    one_time_fees: Mapped[List["OneTimeFee"]] = relationship(  # type:ignore
        back_populates="member", passive_deletes=True
    )

    def __str__(self):
        return "{}, {} ({})".format(self.last_name, self.first_name, self.city)
