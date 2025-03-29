#!/usr/bin/env python3
from typing import List, Dict, Sequence, Set

import argparse
from datetime import date, datetime
from dataclasses import dataclass, field

from memmer.utils import (
    interactive_connect,
    load_config,
    ConnectionParameter,
    restrict_to_active_members,
)
from memmer.orm import Member

from sqlalchemy import select


@dataclass(unsafe_hash=True)
class Address:
    street: str
    street_number: str
    postal_code: str
    city: str

    def __str__(self) -> str:
        return f"{self.street} {self.street_number}, {self.postal_code} {self.city}"


@dataclass
class ContactInformation:
    email: Dict[str, List[Member]] = field(default_factory=dict)
    members_with_email: Set[Member] = field(default_factory=set)
    phone: Dict[str, List[Member]] = field(default_factory=dict)
    members_with_phone: Set[Member] = field(default_factory=set)
    mail: Dict[Address, List[Member]] = field(default_factory=dict)


def enumerate_contact_information(members: Sequence[Member]) -> ContactInformation:
    info = ContactInformation()

    for current in members:
        if current.email_address is not None:
            if current.email_address not in info.email:
                info.email[current.email_address] = []

            info.email[current.email_address].append(current)
            info.members_with_email.add(current)

        if current.phone_number is not None:
            sanitized = current.phone_number.replace(" ", "").replace("+", "00")
            if sanitized not in info.phone:
                info.phone[sanitized] = []

            info.phone[sanitized].append(current)
            info.members_with_phone.add(current)

        address = Address(
            street=current.street,
            street_number=current.street_number,
            postal_code=current.postal_code,
            city=current.city,
        )

        if address not in info.mail:
            info.mail[address] = []

        info.mail[address].append(current)

    return info


def format_user_list(members: Sequence[Member]) -> str:
    return ", ".join([f"{x.first_name} {x.last_name}" for x in members])


def format_results(
    info: ContactInformation,
    include_phone: bool = True,
    include_email: bool = True,
    include_mail: bool = True,
    filter_mail: bool = True,
) -> str:
    formatted = ""

    if include_email:
        formatted += "Email\n"
        for email_address in info.email:
            formatted += (
                f"- {email_address} -> {format_user_list(info.email[email_address])}\n"
            )

        formatted += "\n"

    if include_mail:
        formatted += "Addresses\n"

        for address in info.mail:
            if filter_mail:
                candidates = [
                    x for x in info.mail[address] if x not in info.members_with_email
                ]
            else:
                candidates = info.mail[address]

            if len(candidates) == 0:
                continue

            formatted += f"- {address} -> {format_user_list(candidates)}\n"

        formatted += "\n"

    if include_phone:
        formatted += "Phone numbers\n"

        for phone_number in info.phone:
            formatted += (
                f"- {phone_number} -> {format_user_list(info.phone[phone_number])}\n"
            )

        formatted += "\n"

    return formatted


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--target-date",
        help="The date for which to query users. Only members that have not left before this date are considered",
        type=date.fromisoformat,
        default=datetime.now().date(),
    )
    parser.add_argument(
        "--min-age", help="Minimum age of members to consider", type=int, default=None
    )
    parser.add_argument(
        "--max-age", help="Maximum age of members to consider", type=int, default=None
    )
    parser.add_argument(
        "--all-addresses",
        help="Instead of listing only the address of members for which we don't have an email address, list all",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--include-phone",
        help="Also print phone numbers",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    config = load_config()
    params = ConnectionParameter.from_config(config)

    session, tunnel = interactive_connect(params=params)

    with session:
        query = select(Member)

        ref_date: date = args.target_date

        if args.min_age is not None:
            query = query.where(
                Member.birthday
                <= datetime(
                    year=ref_date.year - args.min_age,
                    month=ref_date.month,
                    day=ref_date.month,
                )
            )
        if args.max_age is not None:
            query = query.where(
                Member.birthday
                >= datetime(
                    year=ref_date.year - args.max_age,
                    month=ref_date.month,
                    day=ref_date.month,
                )
            )

        query = restrict_to_active_members(query=query, target_date=ref_date)

        members = session.scalars(query).all()

        info = enumerate_contact_information(members=members)

        print(
            format_results(
                info,
                filter_mail=not args.all_addresses,
                include_phone=args.include_phone,
            )
        )

    if tunnel is not None:
        tunnel.close()


if __name__ == "__main__":
    main()
