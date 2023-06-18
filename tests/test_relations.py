#!/usr/bin/env python3

# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

import unittest

import datetime
from decimal import Decimal

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.exc
from sqlalchemy import select

from memmer.orm import Base, Member, Session


class TesRelations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = sqlalchemy.create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.Session = sqlalchemy.orm.sessionmaker(bind=cls.engine)

        with cls.Session() as session:
            alice = Member(
                first_name="Alice",
                last_name="Aliceton",
                birthday=datetime.date(year=1978, month=2, day=1),
                street="Alice's street",
                street_number="42",
                postal_code="61452",
                city="Alicetown",
                iban="IE12BOFI90000112345678",
                bic="KHYBPKKAJHE",
                account_owner="Alice",
                sepa_mandate_date=datetime.date(year=2000, month=11, day=13),
            )
            bob = Member(
                first_name="Bob",
                last_name="Bobbington",
                birthday=datetime.date(year=1978, month=2, day=1),
                street="Bob's street",
                street_number="7",
                postal_code="73125",
                city="Bobtown",
                iban="IE12BOFI90000112345678",
                bic="KHYBPKKAJHE",
                account_owner="Bob",
                sepa_mandate_date=datetime.date(year=1990, month=8, day=1),
            )
            session1 = Session(name="Session 1", membership_fee=Decimal("15"))
            session2 = Session(name="Session 2", membership_fee=Decimal("0"))

            session.add_all([alice, bob, session1, session2])
            session.commit()

    def test_session_participation(self):
        with self.Session() as session:
            session1 = session.scalars(
                select(Session).where(Session.name == "Session 1")
            ).first()
            session2 = session.scalars(
                select(Session).where(Session.name == "Session 2")
            ).first()
            alice = session.scalars(
                select(Member).where(Member.first_name == "Alice")
            ).first()
            bob = session.scalars(
                select(Member).where(Member.first_name == "Bob")
            ).first()

            self.assertIsNotNone(session1)
            self.assertIsNotNone(session2)
            self.assertIsNotNone(alice)
            self.assertIsNotNone(bob)

            assert (
                session1 != None and session2 != None and alice != None and bob != None
            )

            session1.members.append(bob)

            self.assertEqual(len(bob.participating_sessions), 1)
            self.assertEqual(bob.participating_sessions[0], session1)

            alice.participating_sessions.append(session1)
            alice.participating_sessions.append(session2)

            self.assertEqual(len(bob.participating_sessions), 1)
            self.assertEqual(bob.participating_sessions[0], session1)
            self.assertEqual(len(alice.participating_sessions), 2)
            self.assertEqual(len(session1.members), 2)
            self.assertEqual(len(session2.members), 1)

            session.commit()

    def test_trainer_association(self):
        with self.Session() as session:
            session1 = session.scalars(
                select(Session).where(Session.name == "Session 1")
            ).first()
            session2 = session.scalars(
                select(Session).where(Session.name == "Session 2")
            ).first()
            alice = session.scalars(
                select(Member).where(Member.first_name == "Alice")
            ).first()
            bob = session.scalars(
                select(Member).where(Member.first_name == "Bob")
            ).first()

            self.assertIsNotNone(session1)
            self.assertIsNotNone(session2)
            self.assertIsNotNone(alice)
            self.assertIsNotNone(bob)

            assert (
                session1 != None and session2 != None and alice != None and bob != None
            )

            session1.trainers.append(alice)

            self.assertEqual(len(alice.trained_sessions), 1)
            self.assertEqual(alice.trained_sessions[0], session1)

            bob.trained_sessions.append(session1)
            bob.trained_sessions.append(session2)

            self.assertEqual(len(session1.trainers), 2)
            self.assertCountEqual(session1.trainers, [alice, bob])
            self.assertEqual(session2.trainers, [bob])

            session.commit()


if __name__ == "__main__":
    unittest.main()
