# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from decimal import Decimal
import datetime
import zlib

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .Base import Base


class Tally(Base):
    __tablename__ = "tallies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creation_time: Mapped[datetime.datetime]
    collection_date: Mapped[datetime.date]
    total_amount: Mapped[Decimal]
    compressed_contents: Mapped[bytes]

    @property
    def contents(self) -> str:
        return zlib.decompress(self.compressed_contents).decode("utf-8")

    @contents.setter
    def contents(self, value: str):
        self.compressed_contents = zlib.compress(value.encode("utf-8"))
