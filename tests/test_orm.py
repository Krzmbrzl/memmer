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

from memmer.orm import Base, Member, Session


class TestORM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = sqlalchemy.create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.Session = sqlalchemy.orm.sessionmaker(bind=cls.engine)

    def test_add_member(self):
        mandatory_parameter = {
            "first_name": "Elvis",
            "last_name": "Presley",
            "birthday": datetime.date(year=1935, month=1, day=8),
            "street": "Famous road",
            "street_number": "8A",
            "postal_code": "13476",
            "city": "King's town",
            "iban": "IE12BOFI90000112345678",
            "bic": "KHYBPKKAJHE",
            "account_owner": "Elvis's dad",
        }

        # First verify that the parameters work as-is
        with self.Session() as session:
            member = Member(**mandatory_parameter)

            session.add(member)
            session.commit()

            # Get rid of the entry again
            session.delete(member)
            session.commit()

        # Now, verify that omitting even a single of these parameters leads to an error
        for i in range(len(mandatory_parameter)):
            params = mandatory_parameter.copy()
            del params[list(params.keys())[i]]

            with self.assertRaises(sqlalchemy.exc.IntegrityError):
                with self.Session() as session:
                    member = Member(**params)
                    session.add(member)
                    session.commit()

    def test_add_session(self):
        mandatory_parameter = {
            "name": "Awesome session",
            "membership_fee": Decimal("19.99"),
        }

        # First verify that the parameters work as-is
        with self.Session() as session:
            trainingSession = Session(**mandatory_parameter)

            session.add(trainingSession)
            session.commit()

            # Get rid of the entry again
            session.delete(trainingSession)
            session.commit()

        # Now, verify that omitting even a single of these parameters leads to an error
        for i in range(len(mandatory_parameter)):
            params = mandatory_parameter.copy()
            del params[list(params.keys())[i]]

            with self.assertRaises(sqlalchemy.exc.IntegrityError):
                with self.Session() as session:
                    trainingSession = Session(**params)
                    session.add(trainingSession)
                    session.commit()


if __name__ == "__main__":
    unittest.main()
