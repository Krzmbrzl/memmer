# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import List, Optional, Tuple

from memmer.orm import Member, Session

from sqlalchemy import select
from sqlalchemy.orm import subqueryload


class DataManager:
    """Holds detached snapshots of all members and sessions.

    Everything is loaded in a single task on the DB thread, with the
    relationships the GUI reads eager-loaded, and then expunged. The GUI thus
    only ever touches detached ORM instances and can never trigger a lazy load
    (and therefore a query) on its own thread.

    ``controller`` is anything exposing ``submit(fn) -> Future`` that runs
    ``fn(session)`` on the DB thread (the DatabaseController)."""

    def __init__(self, controller):
        self.__members: Optional[List[Member]] = None
        self.__sessions: Optional[List[Session]] = None

        # Kicks off the load on the DB thread right away; the result is awaited
        # lazily on first access.
        self.__future = controller.submit(DataManager.__load)

    @property
    def members(self) -> List[Member]:
        self.__ensure_loaded()
        assert self.__members is not None
        return self.__members

    @property
    def sessions(self) -> List[Session]:
        self.__ensure_loaded()
        assert self.__sessions is not None
        return self.__sessions

    def __ensure_loaded(self) -> None:
        if self.__members is None:
            self.__members, self.__sessions = self.__future.result()

    @staticmethod
    def __load(session) -> Tuple[List[Member], List[Session]]:
        members = session.scalars(
            select(Member)
            .options(subqueryload(Member.one_time_fees))
            .options(subqueryload(Member.participating_sessions))
            .options(subqueryload(Member.trained_sessions))
        ).all()
        sessions = session.scalars(
            select(Session)
            .options(subqueryload(Session.members))
            .options(subqueryload(Session.trainers))
        ).all()

        # Detach everything so the GUI holds snapshots, not live objects.
        session.expunge_all()

        return (list(members), list(sessions))
