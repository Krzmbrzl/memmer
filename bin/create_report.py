#!/usr/bin/env python3

import argparse
import datetime

from openpyxl import Workbook

from memmer.orm import Member, Gender

from sqlalchemy import create_engine, func, select, or_
from sqlalchemy.orm import Session


def create_dtv_report(session: Session, output_path: str, target_date: datetime.date):
    earliest_year = (
        session.scalars(
            select(Member.birthday).order_by(Member.birthday.asc()).limit(1)
        )
        .one()
        .year
    )
    this_year = datetime.datetime.now().year

    workbook = Workbook()
    worksheet = workbook.active
    assert worksheet is not None
    worksheet.append(["Jahrgang", "Männlich", "Weiblich"])  # type: ignore

    for current_year in reversed(range(earliest_year, this_year + 1, 1)):
        from_date = datetime.date(year=current_year, month=1, day=1)
        to_date = datetime.date(year=current_year + 1, month=1, day=1)

        query = (
            select(func.count())
            .select_from(Member)
            .filter(or_(Member.exit_date == None, Member.exit_date > target_date))
            .filter(Member.entry_date <= target_date)
            .filter(Member.birthday >= from_date)
            .filter(Member.birthday < to_date)
        )

        male_count = session.scalars(query.filter(Member.gender == Gender.Male)).one()
        female_count = session.scalars(
            query.filter(Member.gender == Gender.Female)
        ).one()

        if female_count != 0 or male_count != 0:
            worksheet.append([current_year, male_count, female_count])  # type: ignore

    workbook.save(output_path)


def main():
    parser = argparse.ArgumentParser(description="Utility to create various reports")

    parser.add_argument(
        "--kind", choices=["DTV"], required=True, help="The kind of report to create"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to which to write the created report",
        metavar="PATH",
        required=True,
    )
    parser.add_argument(
        "--db-path", help="Path to the SQLite DB", required=True, metavar="PATH"
    )
    parser.add_argument(
        "--target-date",
        help="Date to generate the report for (in ISO format)",
        type=datetime.date.fromisoformat,
        metavar="DATE",
        required=True,
    )

    args = parser.parse_args()

    engine = create_engine("sqlite:///{}".format(args.db_path))
    with Session(bind=engine) as session:
        if args.kind == "DTV":
            create_dtv_report(
                session=session, output_path=args.output, target_date=args.target_date
            )
        else:
            raise RuntimeError("Unknown report kind '{}'".format(args.kind))


if __name__ == "__main__":
    main()
