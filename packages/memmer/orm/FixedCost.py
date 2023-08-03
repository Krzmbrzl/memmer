# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from decimal import Decimal

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .Base import Base


class FixedCost(Base):
    __tablename__ = "fixedcosts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    cost: Mapped[Decimal]
