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
from sqlalchemy import select

from memmer.orm import Base, Member, Session, FixedCost, OneTimeFee, Setting
from memmer import BasicFeeAdultsKey, BasicFeeYouthsKey, BasicFeeTrainersKey
from memmer.queries.tally import assemble_monthly_fee_assets


working_dir = os.path.dirname(os.path.realpath(__file__))
test_data_dir = os.path.join(working_dir, "test_data")


def date_hook(json_dict):
    for key, value in json_dict.items():
        try:
            json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            pass
    return json_dict


class TestTallyAssembly(unittest.TestCase):
    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)

        with open(os.path.join(test_data_dir, "members.json")) as f:
            members = json.load(f, object_hook=date_hook)["members"]

        with self.Session() as session:
            for member in members:
                session.add(Member(**member))
            session.add_all(
                [
                    FixedCost(name=BasicFeeAdultsKey, cost=Decimal(5)),
                    FixedCost(name=BasicFeeYouthsKey, cost=Decimal(4)),
                    FixedCost(name=BasicFeeTrainersKey, cost=Decimal(1)),
                ]
            )
            session.add_all(
                [
                    Setting(name=Setting.TALLY_E2E_ID_TEMPLATE, value="M{mem_id}"),
                    Setting(name=Setting.TALLY_PURPOSE, value="Mitgliedsbeitrag"),
                ]
            )
            session.commit()

    def __get(self, session, first_name):
        return session.scalars(
            select(Member).where(Member.first_name == first_name)
        ).one()

    def test_exited_members_are_skipped_unless_they_owe_one_time_fees(self):
        collection_date = datetime.date(2026, 11, 2)
        past = datetime.date(2020, 1, 1)

        with self.Session() as session:
            # Exited with nothing owed -> excluded entirely.
            self.__get(session, "Marilyn").exit_date = past
            # Exited but still owes a one-time fee -> billed for that fee only
            # (the monthly fee is zero because of the exit).
            dirk = self.__get(session, "Dirk")
            dirk.exit_date = past
            dirk.one_time_fees = [OneTimeFee(reason="Restschuld", amount=Decimal(20))]
            session.flush()

            assets = assemble_monthly_fee_assets(
                session, collection_date, clear_onetimecosts=False
            )
            billed = {a.debitor.first_name: a.amount for a in assets}

            self.assertNotIn("Marilyn", billed)
            self.assertEqual(billed.get("Dirk"), Decimal(20))
            # Active members are unaffected.
            self.assertIn("Sally", billed)
            self.assertIn("Sam", billed)


if __name__ == "__main__":
    unittest.main()
