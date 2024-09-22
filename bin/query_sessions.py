#!/usr/bin/env python3

from typing import List

import argparse
from datetime import datetime

from memmer.utils import (
    interactive_connect,
    load_config,
    ConnectionParameter,
    restrict_to_active_members,
    nominal_year_diff,
)
from memmer.orm import Session, Member

from sqlalchemy import select
from sqlalchemy.orm import Session as SQLSession


def interactive_selection(session: SQLSession) -> List[int]:
    print("Which of the following sessions do you want to query?")

    for i, current in enumerate(
        session.scalars(select(Session).order_by(Session.name.asc())).all()
    ):
        print(f"[{i+1:3d}] '{current.name}'")

    print("")

    selection = input(
        "Enter the numeric IDs of the sessions you want to query (separated by a space)\n"
    )

    selection = selection.split()
    selection = [int(x) for x in selection]

    return selection


def main():
    parser = argparse.ArgumentParser(
        description="Queries information about existing sessions and their members"
    )

    parser.add_argument(
        "sessions",
        nargs="*",
        type=int,
        help="The session IDs of the sessions to query. If none is given, an overview of existing sessions is printed",
    )

    args = parser.parse_args()

    config = load_config()
    params = ConnectionParameter.from_config(config)

    session, tunnel = interactive_connect(params=params)

    with session:
        if len(args.sessions) > 0:
            session_ids: List[int] = args.sessions
        else:
            session_ids = interactive_selection(session)

        all_sessions = session.scalars(
            select(Session).order_by(Session.name.asc())
        ).all()

        for current in session_ids:
            if current <= 0:
                print(f"Invalid session ID {current} - IDs must be > 0")
                continue

            if current > len(all_sessions):
                print(
                    f"Session ID {current} is out of range (max: {len(all_sessions)})"
                )
                continue

            current -= 1

            selected = all_sessions[current]

            active_members = session.scalars(
                restrict_to_active_members(
                    select(Member)
                    .where(Member.participating_sessions.any(Session.id == selected.id))
                    .order_by(
                        Member.last_name.asc(), Member.first_name.asc(), Member.id.asc()
                    ),
                    target_date=datetime.now().date(),
                )
            ).all()

            print(
                f"Session '{selected.name}' (total: {len(active_members)}, monthly fee: {selected.membership_fee}€)"
            )

            for i, member in enumerate(active_members):
                age = nominal_year_diff(member.birthday, datetime.now().date())

                print(f"{i+1:3d} - {member.last_name}, {member.first_name} ({age} y/o)")

            print()

    if tunnel is not None:
        tunnel.close()


if __name__ == "__main__":
    main()
