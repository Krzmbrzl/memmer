# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Optional, List

import datetime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .Base import Base


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Personal data
    first_name: Mapped[str]
    last_name: Mapped[str]
    birthday: Mapped[datetime.datetime]

    # Address
    street: Mapped[str]
    street_number: Mapped[str]
    postal_code: Mapped[str]
    city: Mapped[str]

    # Contact information
    phone_number: Mapped[Optional[str]]
    email_address: Mapped[Optional[str]]

    # Account details
    iban: Mapped[str]
    bic: Mapped[str]
    account_owner: Mapped[str]

    use_sepa_debit: Mapped[bool]

    # Relations
    participating_sessions: Mapped[List["Session"]] = relationship( # type: ignore
        back_populates="members", secondary="participations"
    )
    trained_sessions: Mapped[List["Session"]] = relationship( # type: ignore
        back_populates="trainers", secondary="trainers"
    )
