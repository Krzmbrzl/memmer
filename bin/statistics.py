#!/usr/bin/env python3

import datetime

from memmer.orm import Member, Gender

from sqlalchemy import create_engine, func, select, or_
from sqlalchemy.orm import Session


def restrict_to_active(query):
    today = datetime.datetime.now()
    return query.filter(or_(Member.exit_date == None, Member.exit_date > today)).filter(
        Member.entry_date <= today
    )


def main():
    engine = create_engine(
        "sqlite:///{}".format("/home/robert/TSZ Calw/tsz_calw.sqlite")
    )
    with Session(bind=engine) as session:
        member_count_query = select(func.count()).select_from(Member)
        member_count_query = restrict_to_active(member_count_query)
        member_count_query = member_count_query.where(Member.birthday < datetime.datetime(year=2002, month=3, day=31))

        print(f"Current members: {session.scalars(member_count_query).one()}")


if __name__ == "__main__":
    main()
