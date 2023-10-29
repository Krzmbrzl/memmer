# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .Base import Base


class Setting(Base):
    __tablename__ = "settings"

    name: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str]

    TALLY_E2E_ID_TEMPLATE = "tally_end_to_end_template"
    TALLY_PURPOSE = "tally_purpose"
    TALLY_CREDITOR_NAME = "tally_creditor_name"
    TALLY_CREDITOR_IBAN = "tally_creditor_iban"
    TALLY_CREDITOR_BIC = "tally_creditor_bic"
    TALLY_CREDITOR_ID = "tally_creditor_identification"
