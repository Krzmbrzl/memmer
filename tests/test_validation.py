#!/usr/bin/env python3

# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

import unittest

from memmer.utils import (
    IbanProblemKind,
    iban_problem,
    is_valid_bic,
    is_valid_email,
    is_plausible_phone_number,
    is_plausible_street_number,
)


class TestValidation(unittest.TestCase):
    def test_iban(self):
        self.assertIsNone(iban_problem("DE75512108001245126199"))
        self.assertIsNone(iban_problem("de75 5121 0800 1245 1261 99"))
        self.assertIsNone(iban_problem("NL91ABNA0417164300"))

        problem = iban_problem("DE7551210800124512619")
        assert problem is not None
        self.assertEqual(problem.kind, IbanProblemKind.WrongLength)
        self.assertEqual(problem.country, "DE")
        self.assertEqual(problem.expected_length, 22)
        self.assertEqual(problem.actual_length, 21)

        problem = iban_problem("DE75512108001245126198")
        assert problem is not None
        self.assertEqual(problem.kind, IbanProblemKind.InvalidChecksum)

        problem = iban_problem("XX75512108001245126199")
        assert problem is not None
        self.assertEqual(problem.kind, IbanProblemKind.UnknownCountry)
        self.assertEqual(problem.country, "XX")

        problem = iban_problem("DE75ZZZZ08001245126199")
        assert problem is not None
        self.assertEqual(problem.kind, IbanProblemKind.InvalidStructure)

        problem = iban_problem("DE75-5121")
        assert problem is not None
        self.assertEqual(problem.kind, IbanProblemKind.InvalidCharacters)

    def test_bic(self):
        self.assertTrue(is_valid_bic("SOGEDEFFXXX"))
        self.assertTrue(is_valid_bic("sogedeff"))
        self.assertFalse(is_valid_bic("XXXX"))
        self.assertFalse(is_valid_bic(""))

    def test_email(self):
        self.assertTrue(is_valid_email("james.bond@mi6.co.uk"))
        self.assertTrue(is_valid_email(" a@b.de "))
        self.assertFalse(is_valid_email("james.bond"))
        self.assertFalse(is_valid_email("james@bond"))
        self.assertFalse(is_valid_email("james bond@mi6.uk"))
        self.assertFalse(is_valid_email("a@b.c"))

    def test_phone_number(self):
        self.assertTrue(is_plausible_phone_number("+49 711 123456"))
        self.assertTrue(is_plausible_phone_number("0711/123456"))
        self.assertFalse(is_plausible_phone_number("12345"))
        self.assertFalse(is_plausible_phone_number("0711+123456"))

    def test_street_number(self):
        for valid in ["12", "12a", "12 b", "12-14", "12 / 1", "3a-3c"]:
            self.assertTrue(is_plausible_street_number(valid), valid)
        for invalid in ["", "a12", "12abc", "twelve"]:
            self.assertFalse(is_plausible_street_number(invalid), invalid)


if __name__ == "__main__":
    unittest.main()
