#!/usr/bin/env python3

from typing import List

from memmer.generated.pain import PaymentInstructionInformation4

from xsdata.formats.dataclass.parsers import XmlParser

import argparse
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class PaymentInfo:
    amount: Decimal
    member_id: str
    name: str


def extractPayments(info: PaymentInstructionInformation4) -> List[PaymentInfo]:
    payments: List[PaymentInfo] = []
    for current in info.drct_dbt_tx_inf:
        assert current.instd_amt is not None
        assert current.instd_amt.ccy == "EUR"
        assert current.instd_amt.value is not None
        amount = current.instd_amt.value
        assert current.pmt_id is not None
        assert current.pmt_id.end_to_end_id is not None
        member_id = current.pmt_id.end_to_end_id
        if current.ultmt_dbtr is None:
            name = "Unknown"
        else:
            assert current.ultmt_dbtr.nm is not None
            name = current.ultmt_dbtr.nm

        payments.append(PaymentInfo(amount=amount, member_id=member_id, name=name))

    return payments


def main() -> None:
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("first")
    arg_parser.add_argument("second")

    args = arg_parser.parse_args()

    first_content = open(args.first, "r").read()
    second_content = open(args.second, "r").read()

    parser = XmlParser()
    first_info = parser.from_string(first_content).cstmr_drct_dbt_initn.pmt_inf
    second_info = parser.from_string(second_content).cstmr_drct_dbt_initn.pmt_inf

    assert len(first_info) == 1
    assert len(second_info) == 1

    first_payments = extractPayments(first_info[0])
    second_payments = extractPayments(second_info[0])

    first_payments.sort(key=lambda x: x.member_id)
    second_payments.sort(key=lambda x: x.member_id)

    first_strays = [
        x
        for x in first_payments
        if not any(x.member_id == y.member_id for y in second_payments)
    ]
    second_strays = [
        x
        for x in second_payments
        if not any(x.member_id == y.member_id for y in first_payments)
    ]

    for current in first_strays:
        first_payments.remove(current)
    for current in second_strays:
        second_payments.remove(current)

    assert len(first_payments) == len(second_payments)

    total_diff = Decimal(0)

    for i in range(len(first_payments)):
        first = first_payments[i]
        second = second_payments[i]

        assert first.member_id == second.member_id

        if first.amount != second.amount:
            total_diff += first.amount - second.amount
            print(
                "Different amount for {:25s}: {:5.2f}€ vs {:5.2f}€".format(
                    first.name, first.amount, second.amount
                )
            )

    print()
    print(
        "Diff due to different amounts for members first - second: {}€".format(
            total_diff
        )
    )

    if len(first_strays) > 0:
        print()
        print(
            "Payments contained in first but not in second ({}):".format(
                len(first_strays)
            )
        )
        summed = Decimal(0)
        for current in first_strays:
            print(
                "  {:25s} ({}): {:5.2f}€".format(
                    current.name, current.member_id, current.amount
                )
            )
            total_diff += current.amount
            summed += current.amount
        print()
        print("Total more payments in first: {}".format(summed))
    if len(second_strays) > 0:
        print()
        print(
            "Payments contained in second but not in first ({}):".format(
                len(second_strays)
            )
        )
        summed = Decimal(0)
        for current in second_strays:
            print(
                "  {:25s} ({}): {:5.2f}€".format(
                    current.name, current.member_id, current.amount
                )
            )
            total_diff -= current.amount
            summed += current.amount
        print()
        print("Total more payments in second: {}".format(summed))

    print()
    print("Total payment diff first - second: {}€".format(total_diff))


if __name__ == "__main__":
    main()
