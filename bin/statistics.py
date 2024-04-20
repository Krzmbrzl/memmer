#!/usr/bin/env python3

import argparse
import datetime
import os

from memmer.orm import Member, Gender
from memmer.utils import nominal_year_diff

from sqlalchemy import create_engine, select, or_, func
from sqlalchemy.orm import Session

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from matplotlib.dates import DateFormatter
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea, HPacker, VPacker


# TODO: Translate labels for plots


def get_active_members(session: Session, date: datetime.date):
    return session.scalars(
        select(Member)
        .where(or_(Member.exit_date == None, Member.exit_date > date))
        .where(Member.entry_date <= date)
    ).all()


def count_active_members(session: Session, date: datetime.date) -> int:
    return session.scalars(
        select(func.count())
        .select_from(Member)
        .where(or_(Member.exit_date == None, Member.exit_date > date))
        .where(Member.entry_date <= date)
    ).one()


def count_leaves(session: Session, date: datetime.date, delta: datetime.timedelta):
    return session.scalars(
        select(func.count())
        .select_from(Member)
        .where(Member.exit_date <= date)
        .where(Member.exit_date > date - delta)
    ).one()


def count_joins(session: Session, date: datetime.date, delta: datetime.timedelta):
    return session.scalars(
        select(func.count())
        .select_from(Member)
        .where(Member.entry_date <= date)
        .where(Member.entry_date > date - delta)
    ).one()


def create_member_history(
    session: Session,
    target_date: datetime.date,
    since_date: datetime.date,
    output_path: str,
):
    member_counts = []
    joins = []
    leaves = []
    dates = []
    current = since_date
    delta = datetime.timedelta(weeks=1)
    while current <= target_date:
        member_counts.append(count_active_members(session=session, date=current))
        joins.append(count_joins(session=session, date=current, delta=delta))
        leaves.append(-count_leaves(session=session, date=current, delta=delta))
        dates.append(current)
        current += delta

    total_color = "#1f77b4"
    join_color = "#2ca02c"
    leave_color = "#ff7f0e"

    plt.plot(dates, member_counts, color=total_color)
    plt.ylim(bottom=0, top=None)
    plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Anzahl Mitglieder", color=total_color)
    plt.title("Entwicklung Mitgliederzahlen")
    plt.annotate(
        member_counts[0], (dates[0], member_counts[0] - 5), ha="center", va="top"
    )
    plt.annotate(
        member_counts[-1], (dates[-1], member_counts[-1] - 5), ha="center", va="top"
    )

    plt.twinx()
    bar_width = 0.8 * delta
    plt.bar(
        dates,
        [x if x != 0 else float("nan") for x in joins],
        width=bar_width, # type: ignore
        color=join_color,
    )
    plt.bar(
        dates,
        [x if x != 0 else float("nan") for x in leaves],
        width=bar_width, # type: ignore
        color=leave_color,
    )

    plt.ylabel("An-/Abmeldungen")
    plt.ylim(bottom=1.2 * min(leaves), top=1.2 * max(joins))
    plt.axhline(y=0, xmin=0.03, color="black", linewidth=plt.rcParams["axes.linewidth"])

    plt.tight_layout()
    plt.savefig(os.path.join(output_path, "member_history.pdf"))


def create_active_member_stats(
    session: Session, target_date: datetime.date, output_path: str
):
    active_members = get_active_members(session=session, date=target_date)

    # Gender distribution
    n_females = 0
    n_males = 0
    n_diverse = 0
    n_active = 0
    ages = []
    for current in active_members:
        if current.gender == Gender.Female:
            n_females += 1
        elif current.gender == Gender.Male:
            n_males += 1
        elif current.gender == Gender.Diverse:
            n_diverse += 1

        ages.append(nominal_year_diff(first=current.birthday, second=target_date))
        if len(current.participating_sessions) > 0:
            n_active += 1

    total = n_males + n_females + n_diverse

    data = [n_females, n_males]
    labels = ["weiblich", "männlich"]

    if n_diverse > 0:
        data.append(n_diverse)
        labels.append("divers")

    plt.subplot(2, 2, 1)
    plt.pie(data, labels=labels, autopct="%.1f%%")

    plt.subplot(2, 2, 2)
    plt.pie(
        [n_active, total - n_active],
        labels=["aktiv", "passiv"],
        autopct="%.1f%%",
        explode=[0, 0.2],
        startangle=90,
    )

    plt.subplot(2, 2, (3, 4))
    plt.hist(ages, weights=[1 / total] * total, bins=range(0, 100, 5), rwidth=0.9)
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.xlabel("Alter / Jahre")

    plt.suptitle(f"Mitglieder ({total})")
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_path, "active_member_stats.pdf"), bbox_inches="tight"
    )


def create_statistics(
    session: Session,
    target_date: datetime.date,
    since_date: datetime.date,
    output_path: str,
):
    create_active_member_stats(
        session=session, target_date=target_date, output_path=output_path
    )
    plt.close()
    create_member_history(
        session=session,
        target_date=target_date,
        since_date=since_date,
        output_path=output_path,
    )
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db-path", help="Path to the SQLite DB", required=True, metavar="PATH"
    )
    parser.add_argument(
        "--target-date",
        help="Date to generate the statistics for (in ISO format)",
        type=datetime.date.fromisoformat,
        metavar="DATE",
        default=datetime.datetime.now().date(),
    )
    parser.add_argument(
        "--since-date",
        help="Earliest date to consider (in ISO format)",
        type=datetime.date.fromisoformat,
        metavar="DATE",
        default=datetime.datetime.now().date() - datetime.timedelta(days=365),
    )
    parser.add_argument(
        "--out-path",
        help="Path to the directory into which to write the created diagrams",
        type=str,
        metavar="PATH",
        default=".",
    )

    args = parser.parse_args()

    engine = create_engine("sqlite:///{}".format(args.db_path))
    with Session(bind=engine) as session:
        create_statistics(
            session=session,
            target_date=args.target_date,
            since_date=args.since_date,
            output_path=args.out_path,
        )


if __name__ == "__main__":
    main()
