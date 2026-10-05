#!/usr/bin/env python3

# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

import unittest
from decimal import Decimal

from memmer.queries import FeeComponent, FeeBreakdown, format_fee_summary


def to_german(source: str) -> str:
    return {"Base fee": "Grundbeitrag"}.get(source, source)


def base(amount):
    return FeeComponent("base", "Basic fee (adults)", Decimal(amount), Decimal(1), Decimal(amount))


def session(amount, ratio, name):
    ratio = Decimal(str(ratio))
    return FeeComponent("session", name, Decimal(amount), ratio, Decimal(amount) * ratio)


def discount(ratio):
    ratio = Decimal(str(ratio))
    return FeeComponent("discount", "", Decimal(0), ratio, Decimal(0))


def onetime(amount, reason):
    return FeeComponent("onetime", reason, Decimal(amount), Decimal(1), Decimal(amount))


class TestFeeSummary(unittest.TestCase):
    def test_example(self):
        breakdown = FeeBreakdown(
            components=[
                base(4),
                session(16, 1, "Hip Hop I"),
                session(22, "0.75", "Latein"),
                discount(1),
                onetime(15, "Aufnahmegebühr"),
            ]
        )
        self.assertEqual(
            format_fee_summary(breakdown, to_german),
            "4€ (Grundbeitrag) + 16€ (Hip Hop I) + 75% * 22€ (Latein) + 15€ (Aufnahmegebühr)",
        )

    def test_discount_wraps_monthly_part_only(self):
        breakdown = FeeBreakdown(
            components=[base(4), session(16, 1, "Kurs"), discount("0.5"), onetime(10, "X")]
        )
        self.assertEqual(
            format_fee_summary(breakdown, to_german),
            "50% * (4€ (Grundbeitrag) + 16€ (Kurs)) + 10€ (X)",
        )

    def test_override(self):
        breakdown = FeeBreakdown(
            components=[
                FeeComponent("override", "", Decimal(99), Decimal(1), Decimal(99)),
                onetime(15, "Y"),
            ]
        )
        self.assertEqual(format_fee_summary(breakdown, to_german), "99€ + 15€ (Y)")

    def test_cents_are_shown_only_when_present(self):
        breakdown = FeeBreakdown(components=[onetime(Decimal("12.50"), "Z")])
        self.assertEqual(format_fee_summary(breakdown, to_german), "12.50€ (Z)")

    def test_overflow_drops_explanations_by_relevance(self):
        breakdown = FeeBreakdown(
            components=[
                base(4),
                session(16, 1, "HipHop"),
                discount(1),
                onetime(15, "Aufnahme"),
            ]
        )
        full = "4€ (Grundbeitrag) + 16€ (HipHop) + 15€ (Aufnahme)"
        self.assertEqual(format_fee_summary(breakdown, to_german), full)

        # Just too long for the full form: the base explanation goes first.
        self.assertEqual(
            format_fee_summary(breakdown, to_german, max_length=len(full) - 1),
            "4€ + 16€ (HipHop) + 15€ (Aufnahme)",
        )
        # Tighter still: the session explanation goes next, one-time fee kept.
        self.assertEqual(
            format_fee_summary(breakdown, to_german, max_length=30),
            "4€ + 16€ + 15€ (Aufnahme)",
        )
        # Tighter still: even the one-time explanation goes.
        self.assertEqual(
            format_fee_summary(breakdown, to_german, max_length=20),
            "4€ + 16€ + 15€",
        )

    def test_overflow_falls_back_to_ellipsis(self):
        breakdown = FeeBreakdown(
            components=[base(4), session(16, 1, "HipHop"), onetime(15, "A")]
        )
        summary = format_fee_summary(breakdown, to_german, max_length=5)
        self.assertLessEqual(len(summary), 5)
        self.assertTrue(summary.endswith("…"))


if __name__ == "__main__":
    unittest.main()
