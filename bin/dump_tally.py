#!/usr/bin/env python3

import sqlalchemy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from memmer.orm import Tally

import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tally_num", type=int, nargs="?")

    args = parser.parse_args()

    connection_url = sqlalchemy.engine.URL.create(
        drivername="sqlite",
        # username="James Bond",
        # password="Shaken, not stirred",
        # host="localhost",
        database="tsz_calw_members",
    )
    engine = create_engine(connection_url, echo=False)

    with Session(bind=engine) as session:
        tallies = session.scalars(select(Tally).order_by(Tally.collection_date)).all()

        if len(tallies) == 0:
            print("There are no tallies available")
            return

        if args.tally_num is None:
            print("The following tallies are available:")

            for i, tally in enumerate(tallies):
                print(f"  [{i+1:3d}]: Tally from {tally.collection_date.isoformat()}")

            print("Call this script again with the index to the tally you wish to dump")
        else:
            args.tally_num -= 1
            if args.tally_num >= len(tallies):
                print(
                    f"ERROR: Index {args.tally_num} is out of range (only have {len(tallies)} tallies"
                )
                return

            print(tallies[args.tally_num].contents)


if __name__ == "__main__":
    main()
