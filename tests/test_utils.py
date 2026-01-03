#!/usr/bin/env python3

# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

import unittest
from datetime import date

from memmer.utils import nominal_year_diff, container_unordered_equals


class TestOperations(unittest.TestCase):
    def test_nominal_year_diff(self):
        self.assertEqual(
            nominal_year_diff(
                date(year=2020, month=1, day=21), date(year=2023, month=5, day=4)
            ),
            3,
        )
        self.assertEqual(
            nominal_year_diff(
                date(year=2020, month=6, day=21), date(year=2023, month=5, day=4)
            ),
            2,
        )
        self.assertEqual(
            nominal_year_diff(
                date(year=2020, month=5, day=5), date(year=2023, month=5, day=4)
            ),
            2,
        )

        self.assertEqual(
            nominal_year_diff(
                date(year=2020, month=5, day=4), date(year=2020, month=5, day=4)
            ),
            0,
        )
        self.assertEqual(
            nominal_year_diff(
                date(year=2020, month=5, day=3), date(year=2020, month=5, day=4)
            ),
            0,
        )
        self.assertEqual(
            nominal_year_diff(
                date(year=2020, month=4, day=12), date(year=2020, month=5, day=4)
            ),
            0,
        )

        self.assertEqual(
            nominal_year_diff(
                date(year=2021, month=5, day=4), date(year=2020, month=5, day=4)
            ),
            -1,
        )
        self.assertEqual(
            nominal_year_diff(
                date(year=2020, month=6, day=8), date(year=2020, month=5, day=4)
            ),
            -1,
        )
        self.assertEqual(
            nominal_year_diff(
                date(year=2020, month=5, day=5), date(year=2020, month=5, day=4)
            ),
            -1,
        )

        self.assertEqual(
            nominal_year_diff(
                date(year=2021, month=11, day=8), date(year=2020, month=5, day=4)
            ),
            -2,
        )

    def test_container_unordered_equals(self):
        self.assertTrue(
            container_unordered_equals("ab", "ab")
        )
        self.assertFalse(
            container_unordered_equals("abd", "abc")
        )
        self.assertTrue(
            container_unordered_equals(["ab", "ac"], ["ab", "ac"])
        )
        self.assertTrue(
            container_unordered_equals(set(["ab", "ac"]), set(["ab", "ac"]))
        )

        def cmp_first_letter(lhs, rhs):
            return lhs[0] == rhs[0]

        self.assertTrue(
            container_unordered_equals(["ab", "ac"], ["ae", "af"], eq_cmp=cmp_first_letter)
        )
        self.assertTrue(
            container_unordered_equals(set(["ab", "ac"]), set(["ae", "af"]), eq_cmp=cmp_first_letter)
        )




if __name__ == "__main__":
    unittest.main()
