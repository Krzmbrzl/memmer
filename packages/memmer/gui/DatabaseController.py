# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Any, Callable, Optional, Tuple

from concurrent.futures import Future

from PySide6.QtCore import QObject, Signal, Slot

from sqlalchemy.orm import Session

from memmer.utils import DatabaseThread


class DatabaseController(QObject):
    """GUI-facing wrapper around :class:`DatabaseThread`.

    All database access is submitted to the single DB thread; results are
    marshalled back to the GUI thread so the ``on_success``/``on_error``
    callbacks run there and may safely touch Qt widgets. The GUI thread never
    touches the session directly."""

    # Emitted when a task failed and the caller passed no on_error handler, so
    # failures are never silently swallowed. Carries the error message.
    unhandled_error = Signal(str)

    # Carries a zero-argument callable to be invoked on the GUI thread. Emitted
    # from the DB thread, so the (auto) connection to the slot is queued.
    __deliver = Signal(object)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self.__db = DatabaseThread()
        self.__deliver.connect(self.__run_on_gui_thread)

    def submit(
        self,
        fn: Callable[[Optional[Session]], Any],
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> "Future":
        """Runs ``fn(session)`` on the DB thread, delivering the outcome to the
        GUI thread via the callbacks."""
        return self.__deliver_future(self.__db.submit(fn), on_success, on_error)

    def establish(
        self,
        connector: Callable[[], Tuple[Session, Any]],
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> "Future":
        """Establishes the connection on the DB thread (see
        :meth:`DatabaseThread.establish`)."""
        return self.__deliver_future(
            self.__db.establish(connector), on_success, on_error
        )

    def teardown(
        self,
        commit: bool,
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> "Future":
        """Commits or rolls back, then closes the session and tunnel."""
        return self.__deliver_future(self.__db.teardown(commit), on_success, on_error)

    def commit(
        self,
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> "Future":
        return self.submit(lambda session: session.commit(), on_success, on_error)

    def rollback(
        self,
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> "Future":
        return self.submit(lambda session: session.rollback(), on_success, on_error)

    def shutdown(self) -> None:
        self.__db.shutdown(wait=False)

    def __deliver_future(
        self,
        future: "Future",
        on_success: Optional[Callable[[Any], None]],
        on_error: Optional[Callable[[Exception], None]],
    ) -> "Future":
        def when_done(completed: "Future") -> None:
            # Runs on the DB thread; capture the outcome and hand the delivery
            # over to the GUI thread.
            try:
                result = completed.result()
                error: Optional[Exception] = None
            except Exception as exc:  # noqa: BLE001 - reported to the caller
                result = None
                error = exc

            def deliver() -> None:
                if error is not None:
                    if on_error is not None:
                        on_error(error)
                    else:
                        self.unhandled_error.emit(str(error))
                elif on_success is not None:
                    on_success(result)

            self.__deliver.emit(deliver)

        future.add_done_callback(when_done)
        return future

    @Slot(object)
    def __run_on_gui_thread(self, fn: Callable[[], None]) -> None:
        fn()
