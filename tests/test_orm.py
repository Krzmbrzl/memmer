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

from memmer.orm import Base, Member, Session, Gender


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
            "gender": Gender.Diverse,
            "street": "Famous road",
            "street_number": "8A",
            "postal_code": "13476",
            "city": "King's town",
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

    def test_add_member_bank_details(self):
        parameters = {
            "first_name": "Elvis",
            "last_name": "Presley",
            "birthday": datetime.date(year=1935, month=1, day=8),
            "gender": Gender.Male,
            "street": "Famous road",
            "street_number": "8A",
            "postal_code": "13476",
            "city": "King's town",
            "sepa_mandate_date": datetime.date(year=1987, month=3, day=21),
            "iban": "AD1400080001001234567890",
            "bic": "NOSCCATTXXX",
            "account_owner": "Someone else",
        }

        # First verify that the parameters work as-is
        with self.Session() as session:
            member = Member(**parameters)

            session.add(member)
            session.commit()
            session.delete(member)
            session.commit()

        # Now check that omitting any of iban, bic and account_owner is only allowed, if sepa_mandate_date is not set either
        for delete_mandate in [False, True]:
            for current in ["iban", "bic", "account_owner"]:
                params = parameters.copy()
                del params[current]
                if delete_mandate:
                    del params["sepa_mandate_date"]

                if not delete_mandate:
                    with self.assertRaises(sqlalchemy.exc.IntegrityError):
                        with self.Session() as session:
                            member = Member(**params)
                            session.add(member)
                            session.commit()
                else:
                    with self.Session() as session:
                        member = Member(**params)
                        session.add(member)
                        session.commit()

                        # Setting the mandate now should still error
                        with self.assertRaises(sqlalchemy.exc.IntegrityError):
                            member.sepa_mandate_date = datetime.date(
                                year=1978, month=12, day=15
                            )
                            session.commit()

                        session.rollback()  # rollback the errored commit from above
                        session.delete(member)
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
