#!/usr/bin/env python3

from typing import Dict

import argparse
import datetime
import xml.etree.cElementTree as ET

from openpyxl import Workbook

from memmer.orm import Member, Gender, Setting
from memmer.utils import (
    interactive_connect,
    load_config,
    ConnectionParameter,
    restrict_to_active_members,
)

from sqlalchemy import func, select
from sqlalchemy.orm import Session


def get_member_counts_by_cohort(
    session: Session, target_date: datetime.date
) -> Dict[int, Dict[Gender, int]]:
    earliest_year = (
        session.scalars(
            select(Member.birthday).order_by(Member.birthday.asc()).limit(1)
        )
        .one()
        .year
    )
    this_year = datetime.datetime.now().year

    counts_per_year: Dict[int, Dict[Gender, int]] = dict()

    for current_year in reversed(range(earliest_year, this_year + 1, 1)):
        from_date = datetime.date(year=current_year, month=1, day=1)
        to_date = datetime.date(year=current_year + 1, month=1, day=1)

        query = (
            select(func.count())
            .select_from(Member)
            .filter(Member.birthday >= from_date)
            .filter(Member.birthday < to_date)
        )

        query = restrict_to_active_members(query=query, target_date=target_date)

        counts = dict()
        for gender in Gender:
            counts[gender] = session.scalars(
                query.filter(Member.gender == gender)
            ).one()

        total_count = sum(counts.values())

        if total_count > 0:
            counts_per_year[current_year] = counts

    return counts_per_year


def create_dtv_report(session: Session, output_path: str, target_date: datetime.date):
    workbook = Workbook()
    worksheet = workbook.active
    assert worksheet is not None
    worksheet.append(["Jahrgang", "Männlich", "Weiblich"])  # type: ignore

    for year, count_per_gender in get_member_counts_by_cohort(
        session=session, target_date=target_date
    ).items():
        assert (
            count_per_gender[Gender.Diverse] == 0
        ), "DTV report does not support genders other than male and female"
        worksheet.append(
            [year, count_per_gender[Gender.Male], count_per_gender[Gender.Female]]
        )

    workbook.save(output_path)


def create_wlsb_report(session: Session, output_path: str, target_date: datetime.date):
    members = ET.Element("Mitglieder")

    software = ET.SubElement(members, "Software")
    ET.SubElement(software, "Schluessel").text = "Memmer"

    club = ET.SubElement(members, "Verein")
    ET.SubElement(club, "Nummer").text = session.scalars(
        select(Setting.value).where(Setting.name == Setting.CLUB_NUMBER)
    ).one()
    ET.SubElement(club, "Bezeichnung").text = session.scalars(
        select(Setting.value).where(Setting.name == Setting.CLUB_NAME)
    ).one()
    ET.SubElement(club, "Ansprechpartner").text = session.scalars(
        select(Setting.value).where(Setting.name == Setting.CLUB_CONTACT_PERSON)
    ).one()

    # Note that we currently assume that all members have the same association
    # The report would in principle allow for multiple associations (per member)
    association = session.scalars(
        select(Setting.value).where(Setting.name == Setting.CLUB_ASSOCIATION_NUMERIC)
    ).one()

    for year, count_per_gender in get_member_counts_by_cohort(
        session=session, target_date=target_date
    ).items():
        counts_A = ET.SubElement(members, "Zahlen")
        ET.SubElement(counts_A, "Typ").text = "A"
        ET.SubElement(counts_A, "Fachverband").text = ""
        ET.SubElement(counts_A, "Jahrgang").text = str(year)

        counts_B = ET.SubElement(members, "Zahlen")
        ET.SubElement(counts_B, "Typ").text = "B"
        ET.SubElement(counts_B, "Fachverband").text = str(association)
        ET.SubElement(counts_B, "Jahrgang").text = str(year)

        for gender, count in count_per_gender.items():
            if gender == Gender.Female:
                tag = "AnzahlW"
            elif gender == Gender.Male:
                tag = "AnzahlM"
            elif gender == Gender.Diverse:
                tag = "AnzahlD"
            else:
                raise RuntimeError(f"Unhandled gender '{gender}'")

            ET.SubElement(counts_A, tag).text = str(count)
            ET.SubElement(counts_B, tag).text = str(count)

        # Until we support "unspecified" as a proper value in the Gender enum, we just report the count as zero
        ET.SubElement(counts_A, "AnzahlO").text = str(0)
        ET.SubElement(counts_B, "AnzahlO").text = str(0)

    # Write out
    tree = ET.ElementTree(members)
    ET.indent(tree)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description="Utility to create various reports")

    parser.add_argument(
        "--kind",
        choices=["DTV", "WLSB"],
        required=True,
        help="The kind of report to create",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to which to write the created report",
        metavar="PATH",
        required=True,
    )
    parser.add_argument(
        "--target-date",
        help="Date to generate the report for (in ISO format)",
        type=datetime.date.fromisoformat,
        metavar="DATE",
        required=True,
    )

    args = parser.parse_args()

    config = load_config()
    params = ConnectionParameter.from_config(config)

    session, tunnel = interactive_connect(params=params)

    with session:
        if args.kind == "DTV":
            create_dtv_report(
                session=session, output_path=args.output, target_date=args.target_date
            )
        elif args.kind == "WLSB":
            create_wlsb_report(
                session=session, output_path=args.output, target_date=args.target_date
            )
        else:
            raise RuntimeError("Unknown report kind '{}'".format(args.kind))

    if tunnel is not None:
        tunnel.close()


if __name__ == "__main__":
    main()
