#!/usr/bin/env python3

# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

import unittest
import json
import os
import datetime

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.exc
from sqlalchemy import select

from memmer.orm import Base, Member, Session, Relation
from memmer.queries import are_related, make_relation, drop_relation, get_relatives


working_dir = os.path.dirname(os.path.realpath(__file__))
test_data_dir = os.path.join(working_dir, "test_data")


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

            session.commit()

    def test_relationships(self):
        with self.Session() as session:
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
            yoshi = session.scalars(
                select(Member).where(
                    (Member.first_name == "Yoshi") & (Member.last_name == "Young")
                )
            ).first()
            assert sally != None
            assert sam != None
            assert yoshi != None

            # Check current relations
            self.assertTrue(are_related(session, sam, sally))
            self.assertTrue(are_related(session, sally, sam))
            self.assertFalse(are_related(session, sally, yoshi))
            self.assertFalse(are_related(session, yoshi, sally))

            # Add yoshi into the relation
            make_relation(session, sally, yoshi)
            make_relation(session, yoshi, sam)

            self.assertTrue(are_related(session, sam, sally))
            self.assertTrue(are_related(session, sally, yoshi))
            self.assertTrue(are_related(session, yoshi, sam))

            # Remove yoshi again
            drop_relation(session, sally, yoshi)
            drop_relation(session, yoshi, sam)

            self.assertTrue(are_related(session, sam, sally))
            self.assertFalse(are_related(session, sally, yoshi))
            self.assertFalse(are_related(session, yoshi, sam))

            # Get relatives
            self.assertListEqual(get_relatives(session, sally), [sam])
            self.assertListEqual(get_relatives(session, sam), [sally])
            self.assertListEqual(get_relatives(session, yoshi), [])


if __name__ == "__main__":
    unittest.main()
