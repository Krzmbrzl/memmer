# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import List

from concurrent.futures import ThreadPoolExecutor

from memmer import (
    AdmissionFeeKey,
    BasicFeeAdultsKey,
    BasicFeeYouthsKey,
    BasicFeeTrainersKey,
)
from memmer.orm import Member, Session, FixedCost, FeeOverride

from sqlalchemy import select
from sqlalchemy import orm
from sqlalchemy.orm import subqueryload


class DataManager:
    def __init__(self, session: orm.Session):
        self.sql_session = session

        self.__members: List[Member] = []
        self.__sessions: List[Session] = []

        self.executor = ThreadPoolExecutor(max_workers=1)

        self.member_fetcher = self.executor.submit(self.__fetch_members)
        self.session_fetcher = self.executor.submit(self.__fetch_sessions)
        self.executor.submit(self.__fetch_session_participations)
        self.executor.submit(self.__fetch_one_time_fees)
        self.executor.submit(self.__fetch_session_trainers)
        self.executor.submit(self.__fetch_fixed_costs)

    @property
    def members(self) -> List[Member]:
        self.member_fetcher.result()

        return self.__members

    @property
    def sessions(self) -> List[Session]:
        self.session_fetcher.result()

        return self.__sessions

    def __fetch_members(self):
        self.__members = list(self.sql_session.scalars(select(Member)).all())

    def __fetch_sessions(self):
        self.__sessions = list(self.sql_session.scalars(select(Session)).all())

    def __fetch_one_time_fees(self):
        self.sql_session.scalars(
            select(Member).options(subqueryload(Member.one_time_fees))
        ).all()

    def __fetch_session_participations(self):
        self.sql_session.scalars(
            select(Member).options(subqueryload(Member.participating_sessions))
        ).all()
        self.sql_session.scalars(
            select(Session).options(subqueryload(Session.members))
        ).all()

    def __fetch_session_trainers(self):
        self.sql_session.scalars(
            select(Member).options(subqueryload(Member.trained_sessions))
        ).all()
        self.sql_session.scalars(
            select(Session).options(subqueryload(Session.trainers))
        ).all()

    def __fetch_fixed_costs(self):
        for key in [
            AdmissionFeeKey,
            BasicFeeAdultsKey,
            BasicFeeYouthsKey,
            BasicFeeTrainersKey,
        ]:
            self.sql_session.scalars(
                select(FixedCost).where(FixedCost.name == key)
            ).one()

