# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Any, Callable, Optional, Tuple

import queue
import threading
from concurrent.futures import Future

from sqlalchemy.orm import Session

# Sentinel that makes the worker loop exit
_SHUTDOWN = object()


class DatabaseThread:
    """Owns a SQLAlchemy ``Session`` and runs every access to it on one thread.

    SQLAlchemy sessions (and the ORM objects bound to them) must not be used
    from multiple threads concurrently. This class confines a single session to
    one dedicated worker thread and serializes all operations through a queue,
    so callers from any thread can submit work via :meth:`submit` without ever
    touching the session themselves.

    The session is created and torn down on the worker thread as well (see
    :meth:`establish`/:meth:`teardown`), so it is never handed across threads.
    """

    def __init__(self):
        self.__session: Optional[Session] = None
        self.__tunnel: Any = None
        self.__queue: "queue.Queue" = queue.Queue()
        self.__thread = threading.Thread(
            target=self.__run, name="memmer-db", daemon=True
        )
        self.__thread.start()

    def submit(self, fn: Callable[[Optional[Session]], Any]) -> "Future":
        """Schedules ``fn(session)`` to run on the DB thread.

        Returns a ``Future`` that resolves with ``fn``'s result or the
        exception it raised. ``session`` is ``None`` until :meth:`establish`
        has completed."""
        future: "Future" = Future()
        self.__queue.put((fn, future))
        return future

    def establish(self, connector: Callable[[], Tuple[Session, Any]]) -> "Future":
        """Runs ``connector()`` on the DB thread and adopts its session/tunnel.

        ``connector`` returns ``(session, tunnel)``; both are created on and
        remain owned by the worker thread."""

        def task(_: Optional[Session]) -> None:
            session, tunnel = connector()
            self.__session = session
            self.__tunnel = tunnel

        return self.submit(task)

    def teardown(self, commit: bool) -> "Future":
        """Commits or rolls back, closes the session and stops the tunnel."""

        def task(session: Optional[Session]) -> None:
            if session is not None:
                if commit:
                    session.commit()
                else:
                    session.rollback()
                session.close()
            if self.__tunnel is not None:
                self.__tunnel.stop()
            self.__session = None
            self.__tunnel = None

        return self.submit(task)

    def shutdown(self, wait: bool = True) -> None:
        """Stops the worker thread. Pending tasks already queued still run."""
        self.__queue.put(_SHUTDOWN)
        if wait:
            self.__thread.join()

    def __run(self) -> None:
        while True:
            item = self.__queue.get()
            if item is _SHUTDOWN:
                break

            fn, future = item
            if not future.set_running_or_notify_cancel():
                continue

            try:
                result = fn(self.__session)
            except Exception as exc:  # noqa: BLE001 - propagated via the future
                future.set_exception(exc)
            else:
                future.set_result(result)
