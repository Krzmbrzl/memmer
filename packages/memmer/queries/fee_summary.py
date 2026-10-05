# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

"""Renders a member's fee breakdown into a short, human-readable summary such
as ``4€ (Grundbeitr.) + 16€ (Hip Hop I) + 75% * 22€ (Latein) + 15€
(Aufnahmegebühr)`` for the SEPA remittance line.

This module is deliberately free of any Qt/translation dependency: the only
translatable label (the base fee) is supplied through an injected ``translate``
callable, while session and one-time-fee names come verbatim from the
database."""

from typing import Callable, List, Tuple

from decimal import Decimal

from .fees import FeeBreakdown

# Source label; translated via the injected callable. Course and one-time-fee
# names are database text and are never translated.
BASE_FEE_LABEL = "Base fee"

# The SEPA remittance field (<Ustrd>) is capped at 140 characters.
MAX_REMITTANCE_LENGTH = 140


def _money(amount: Decimal) -> str:
    quantized = amount.quantize(Decimal("0.01"))
    if quantized == quantized.to_integral_value():
        return "{}€".format(int(quantized))
    return "{:.2f}€".format(quantized)


def _percent(ratio: Decimal) -> str:
    percent = ratio * 100
    return "{:.0f}%".format(percent)


def _parenthesize(text: str) -> str:
    return "({})".format(text)


def format_fee_summary(
    breakdown: FeeBreakdown,
    translate: Callable[[str], str],
    max_length: int = MAX_REMITTANCE_LENGTH,
) -> str:
    """Formats ``breakdown`` into a summary at most ``max_length`` chars long.

    When too long, each component's parenthetical explanation is dropped in
    ascending order of relevance (base fee, then sessions, then one-time fees);
    if the result still does not fit, it is truncated with an ellipsis."""
    components = breakdown.components

    discount = next(
        (c.ratio for c in components if c.kind == "discount"), Decimal(1)
    )

    # Each atom: (relevance, value, explanation). A lower relevance is dropped
    # (its explanation hidden) first when the summary has to be shortened.
    monthly: List[Tuple[int, str, str]] = []
    onetime: List[Tuple[int, str, str]] = []

    for component in components:
        if component.kind == "override":
            monthly.append((0, _money(component.amount), ""))
        elif component.kind == "base":
            monthly.append(
                (0, _money(component.amount), _parenthesize(translate(BASE_FEE_LABEL)))
            )
        elif component.kind == "session":
            if component.ratio == 1:
                value = _money(component.base_amount)
            else:
                value = "{} * {}".format(
                    _percent(component.ratio), _money(component.base_amount)
                )
            monthly.append((1, value, _parenthesize(component.label)))
        elif component.kind == "onetime":
            onetime.append((2, _money(component.amount), _parenthesize(component.label)))

    def render(hidden_relevances) -> str:
        def term(atom: Tuple[int, str, str]) -> str:
            relevance, value, explanation = atom
            if explanation and relevance not in hidden_relevances:
                return "{} {}".format(value, explanation)
            return value

        monthly_str = " + ".join(term(a) for a in monthly)
        if discount != 1 and monthly_str:
            # The monthly fee is scaled as a whole; one-time fees are not.
            monthly_str = "{} * ({})".format(_percent(discount), monthly_str)

        parts: List[str] = []
        if monthly_str:
            parts.append(monthly_str)
        parts.extend(term(a) for a in onetime)
        return " + ".join(parts)

    # Progressively drop explanations: base (0), then sessions (1), then
    # one-time fees (2).
    for hidden in (set(), {0}, {0, 1}, {0, 1, 2}):
        summary = render(hidden)
        if len(summary) <= max_length:
            return summary

    # Everything stripped and still too long: hard-truncate with an ellipsis.
    return summary[: max_length - 1] + "…"
