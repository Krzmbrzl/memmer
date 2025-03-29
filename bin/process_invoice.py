#!/usr/bin/env python3

from typing import List

import argparse
import csv
from io import StringIO
from decimal import Decimal
from datetime import date, datetime

from memmer.utils import interactive_connect, load_config, ConnectionParameter
from memmer.queries import create_tally, Asset
from memmer.orm import Setting, Member

from sqlalchemy import select
from sqlalchemy.orm import Session as SQLSession


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--invoice",
        help="Path to the CSV representing the invoice",
        metavar="PATH",
        required=True,
    )
    parser.add_argument(
        "--out-dir",
        help="Directory into which to write the generated file",
        default=".",
        metavar="PATH",
    )
    parser.add_argument(
        "--collection-date",
        help="Date at which the due amounts shall be collected",
        default=datetime.now().date(),
        type=date.fromisoformat,
    )

    args = parser.parse_args()

    contents = open(args.invoice, "r").read()
    # Skip header
    contents = contents[contents.index("\n") + 1 :]

    reader = csv.reader(StringIO(contents))

    config = load_config()
    params = ConnectionParameter.from_config(config)

    session, tunnel = interactive_connect(params=params)

    assets: List[Asset] = []

    e2e_id_template = session.scalars(
        select(Setting.value).where(Setting.name == Setting.TALLY_E2E_ID_TEMPLATE)
    ).one()

    with session:
        for line in reader:
            assert len(line) == 5
            last_name, first_name, description, price, tax_rate = line

            member = session.scalars(
                select(Member)
                .where(Member.first_name == first_name)
                .where(Member.last_name == last_name)
            ).one()

            assets.append(
                Asset(
                    debitor=member,
                    purpose=description,
                    amount=Decimal(price)
                    * Decimal("{:.3f}".format(1 + float(tax_rate) / 100)),
                    e2e_id=e2e_id_template,
                )
            )

        if len(assets) > 0:
            create_tally(
                session=session,
                output_dir=args.out_dir,
                collection_date=args.collection_date,
                assets=assets,
            )

            print(f"PAIN message generated successfully in directory '{args.out_dir}'")
            print()

            answer = input(
                "Do you want to persist the generated tally in the database? [y|n] "
            )
            while answer.lower() not in ["y", "n"]:
                answer = input("Please input either 'y' for 'yes' or 'n' for 'no' ")

            if answer.lower() == "y":
                session.commit()

            if answer.lower() == "y":
                session.commit()

    if tunnel is not None:
        tunnel.close()


if __name__ == "__main__":
    main()
