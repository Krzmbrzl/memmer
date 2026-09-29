# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Optional, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import re

from schwifty import IBAN, BIC, registry
from schwifty.exceptions import (
    SchwiftyException,
    InvalidCountryCode,
    InvalidLength,
    InvalidChecksumDigits,
    InvalidStructure,
    InvalidBankCode,
    InvalidBBANChecksum,
)


class IbanProblemKind(Enum):
    InvalidCharacters = auto()
    UnknownCountry = auto()
    WrongLength = auto()
    InvalidChecksum = auto()
    InvalidStructure = auto()
    UnknownBank = auto()
    NotInSepaZone = auto()
    Other = auto()


@dataclass
class IbanProblem:
    kind: IbanProblemKind
    country: str = ""
    expected_length: int = 0
    actual_length: int = 0


def _iban_spec(country: str) -> Optional[Tuple[int, bool]]:
    """Returns the IBAN length and whether the country is part of the SEPA zone"""
    try:
        if hasattr(registry, "get_iban_spec"):
            spec = registry.get_iban_spec(country)  # type: ignore
        else:
            # schwifty < 2026.7
            spec = registry.get("iban")[country]  # type: ignore
    except (KeyError, SchwiftyException):
        return None

    return (spec["iban_length"], spec["in_sepa_zone"])


def normalize_iban(text: str) -> str:
    return text.replace(" ", "").upper()


def iban_problem(text: str) -> Optional[IbanProblem]:
    """Returns the reason why the given IBAN is invalid or None if it is valid"""
    iban = normalize_iban(text)
    country = iban[:2]

    if not re.fullmatch(r"[A-Z0-9]*", iban):
        return IbanProblem(IbanProblemKind.InvalidCharacters)

    spec = _iban_spec(country)
    if spec is None:
        return IbanProblem(IbanProblemKind.UnknownCountry, country=country)

    expected_length, in_sepa_zone = spec
    if len(iban) != expected_length:
        return IbanProblem(
            IbanProblemKind.WrongLength,
            country=country,
            expected_length=expected_length,
            actual_length=len(iban),
        )

    try:
        IBAN(iban)
    except InvalidCountryCode:
        return IbanProblem(IbanProblemKind.UnknownCountry, country=country)
    except InvalidLength:
        return IbanProblem(
            IbanProblemKind.WrongLength,
            country=country,
            expected_length=expected_length,
            actual_length=len(iban),
        )
    except (InvalidChecksumDigits, InvalidBBANChecksum):
        return IbanProblem(IbanProblemKind.InvalidChecksum, country=country)
    except InvalidStructure:
        return IbanProblem(IbanProblemKind.InvalidStructure, country=country)
    except InvalidBankCode:
        return IbanProblem(IbanProblemKind.UnknownBank, country=country)
    except SchwiftyException:
        return IbanProblem(IbanProblemKind.Other, country=country)

    if not in_sepa_zone:
        return IbanProblem(IbanProblemKind.NotInSepaZone, country=country)

    return None


def is_valid_bic(text: str) -> bool:
    try:
        BIC(text.strip().upper())
        return True
    except SchwiftyException:
        return False


def is_valid_email(text: str) -> bool:
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s.]{2,}", text.strip()) is not None


def count_digits(text: str) -> int:
    return sum(c.isdigit() for c in text)


def is_plausible_phone_number(text: str) -> bool:
    text = text.strip()
    return count_digits(text) >= 6 and "+" not in text[1:]


def is_plausible_street_number(text: str) -> bool:
    # e.g. 12, 12a, 12 b, 12-14, 12/1
    return (
        re.fullmatch(r"\d+\s?[a-zA-Z]?(\s?[-/]\s?\d+\s?[a-zA-Z]?)?", text.strip())
        is not None
    )
