#!/usr/bin/env python3

# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

import unittest
import json
import os
import datetime
from decimal import Decimal

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.exc
from sqlalchemy import select

from memmer.orm import Base, Member, Session, Relation, FixedCost
from memmer.queries import (
    are_related,
    make_relation,
    drop_relation,
    get_relatives,
    get_fixed_cost,
    compute_monthly_fee,
)
from memmer import (
    AdmissionFeeKey,
    BasicFeeAdultsKey,
    BasicFeeYouthsKey,
    ProcessingFeeKey,
)


working_dir = os.path.dirname(os.path.realpath(__file__))
test_data_dir = os.path.join(working_dir, "test_data")


def get_users(session):
    sally = session.scalars(
        select(Member).where(
            (Member.first_name == "Sally") & (Member.last_name == "Smoldriski")
        )
    ).first()
    sam = session.scalars(
        select(Member).where(
            (Member.first_name == "Sam") & (Member.last_name == "Smoldriski")
        )
    ).first()
    dirk = session.scalars(
        select(Member).where(
            (Member.first_name == "Dirk") & (Member.last_name == "Nowitzki")
        )
    ).first()

    assert sally != None
    assert sam != None
    assert dirk != None

    return (sally, sam, dirk)


def get_sessions(session):
    shortSession = session.scalars(
        select(Session).where(Session.name == "Short session")
    ).first()
    mediumSession = session.scalars(
        select(Session).where(Session.name == "Medium session")
    ).first()
    longSession = session.scalars(
        select(Session).where(Session.name == "Long session")
    ).first()

    assert shortSession != None
    assert mediumSession != None
    assert longSession != None

    return (shortSession, mediumSession, longSession)


# Taken from https://stackoverflow.com/a/16310732/3907364
def date_hook(json_dict):
    for key, value in json_dict.items():
        try:
            json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%d").date()
        except:
            pass
    return json_dict


class TestOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = sqlalchemy.create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.Session = sqlalchemy.orm.sessionmaker(bind=cls.engine)

        with open(os.path.join(test_data_dir, "members.json"), "r") as memberFile:
            membersJSON = json.load(memberFile, object_hook=date_hook)
        with open(os.path.join(test_data_dir, "sessions.json"), "r") as sessionFile:
            sessionsJSON = json.load(sessionFile, object_hook=date_hook)

        with cls.Session() as session:
            for currentMember in membersJSON["members"]:
                memberObj = Member(**currentMember)

                session.add(memberObj)
                session.commit()
            for currentSession in sessionsJSON["sessions"]:
                sessionObj = Session(**currentSession)

                session.add(sessionObj)

            # Establish relationships
            sally = session.scalars(
                select(Member).where(
                    (Member.first_name == "Sally") & (Member.last_name == "Smoldriski")
                )
            ).first()
            sam = session.scalars(
                select(Member).where(
                    (Member.first_name == "Sam") & (Member.last_name == "Smoldriski")
                )
            ).first()
            assert sally != None
            assert sam != None
            session.add(Relation(first_id=sally.id, second_id=sam.id))

            # set fixed costs
            fixed_costs = [
                FixedCost(name=AdmissionFeeKey, cost=15),
                FixedCost(name=BasicFeeAdultsKey, cost=5),
                FixedCost(name=BasicFeeYouthsKey, cost=4),
                FixedCost(name=ProcessingFeeKey, cost=15),
            ]
            session.add_all(fixed_costs)

            session.commit()

    def test_relationships(self):
        with self.Session() as session:
            sally, sam, dirk = get_users(session)

            # Check current relations
            self.assertTrue(are_related(session, sam, sally))
            self.assertTrue(are_related(session, sally, sam))
            self.assertFalse(are_related(session, sally, dirk))
            self.assertFalse(are_related(session, dirk, sally))

            # Add dirk into the relation
            make_relation(session, sally, dirk)
            make_relation(session, dirk, sam)

            self.assertTrue(are_related(session, sam, sally))
            self.assertTrue(are_related(session, sally, dirk))
            self.assertTrue(are_related(session, dirk, sam))

            # Remove dirk again
            drop_relation(session, sally, dirk)
            drop_relation(session, dirk, sam)

            self.assertTrue(are_related(session, sam, sally))
            self.assertFalse(are_related(session, sally, dirk))
            self.assertFalse(are_related(session, dirk, sam))

            # Get relatives
            self.assertListEqual(get_relatives(session, sally), [sam])
            self.assertListEqual(get_relatives(session, sam), [sally])
            self.assertListEqual(get_relatives(session, dirk), [])

    def test_monthly_fee_calculation(self):
        with self.Session() as session:
            sally, sam, dirk = get_users(session)
            shortSession, mediumSession, longSession = get_sessions(session)

            youth_base_fee = get_fixed_cost(session, BasicFeeYouthsKey)
            adult_base_fee = get_fixed_cost(session, BasicFeeAdultsKey)

            # Youth basic fee
            self.assertEqual(
                compute_monthly_fee(session, sally),
                youth_base_fee,
            )
            # Adult basic fee
            self.assertEqual(
                compute_monthly_fee(session, dirk),
                adult_base_fee,
            )
            # Youth basic fee with sibling discount
            self.assertEqual(
                compute_monthly_fee(session, sam),
                youth_base_fee / 2,
            )

            # The most expensive sibling has to pay fully
            sam.participating_sessions.append(mediumSession)
            sally.participating_sessions.append(shortSession)
            self.assertEqual(
                compute_monthly_fee(session, sam),
                youth_base_fee + 20,
            )
            self.assertEqual(
                compute_monthly_fee(session, sally),
                (youth_base_fee + 16) / 2,
            )

            # First session costs 100%, second 75% and all other are free
            dirk.participating_sessions.append(longSession)
            dirk.participating_sessions.append(shortSession)
            dirk.participating_sessions.append(mediumSession)
            self.assertEqual(
                compute_monthly_fee(session, dirk),
                adult_base_fee + 28 + Decimal(20 * 0.75),
            )


if __name__ == "__main__":
    unittest.main()
