# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_TallyWidget import Ui_TallyWidget

from typing import Optional

from PySide6.QtCore import Signal, Slot, QDate
from PySide6.QtWidgets import QMessageBox

from memmer.gui import MemmerWidget, FormValidator, Issue, error, TallyResultDialog
from memmer.queries import create_tally, TallyResult
from memmer.member_text import MemberTranslator
from memmer.utils import has_uncommitted_changes

import datetime
import os
import time


def _min_collection_date() -> datetime.date:
    return (datetime.datetime.now() + datetime.timedelta(days=2)).date()


def _to_qdate(date: datetime.date) -> QDate:
    return QDate(date.year, date.month, date.day)


class _PendingChangesError(RuntimeError):
    """Raised when a tally is attempted while the session has uncommitted
    changes, which must be committed first so the tally's own changes are the
    only thing a failure could roll back."""


class TallyWidget(MemmerWidget, Ui_TallyWidget):
    main_menu_requested = Signal()
    # Emitted while a tally is being created so the main window can block
    # editing (no other change may be staged during the atomic tally task).
    busy_changed = Signal(bool)
    # Emitted from the DB thread as the tally is assembled: (processed, total)
    # members. Queued to the GUI thread, where it drives the progress bar.
    progress_updated = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.__connect_signals()

        self.__init_state()

        self.__setup_validation()

    def __setup_validation(self):
        self.validator = FormValidator(self, self.create_button)

        self.validator.add_check(
            self.__check_collection_date, [self.collection_date_input]
        )
        self.validator.add_check(self.__check_out_dir, [self.out_dir_input])

    def __check_collection_date(self) -> Optional[Issue]:
        collection_date = self.collection_date_input.date().toPython()
        assert isinstance(collection_date, datetime.date)

        if collection_date < _min_collection_date():
            return error(
                self.tr("The collection date must be at least 2 days in the future")
            )
        if collection_date.weekday() >= 5:
            return error(self.tr("Direct debits can't be collected on weekends"))
        return None

    def __check_out_dir(self) -> Optional[Issue]:
        path = self.out_dir_input.path.strip()
        if len(path) == 0:
            return error(self.tr("Please choose where to save the tally"))
        if not os.path.exists(path):
            return error(self.tr("This directory doesn't exist"))
        if not os.path.isdir(path):
            return error(self.tr("This is not a directory"))
        if not os.access(path, os.W_OK):
            return error(
                self.tr("You don't have permission to write to this directory")
            )
        return None

    def __connect_signals(self):
        self.back_button.clicked.connect(self.main_menu_requested.emit)
        self.year_spinner.valueChanged.connect(self.__update_collection_date)
        self.month_combo.currentIndexChanged.connect(self.__update_collection_date)
        self.create_button.clicked.connect(self.__create_tally)
        self.progress_updated.connect(self.__on_progress)

    def __init_state(self):
        day_threshold = 20

        now = datetime.datetime.now()

        if now.month == 12 and now.day > day_threshold:
            # Select upcoming year
            self.year_spinner.setValue(now.year + 1)
        else:
            # Select current year
            self.year_spinner.setValue(now.year)

        assert now.month > 0
        month_idx = now.month - 1
        if now.day > day_threshold:
            # Select upcoming month
            self.month_combo.setCurrentIndex((month_idx + 1) % 12)
        else:
            # Select current month
            self.month_combo.setCurrentIndex(month_idx)

    def opened(self, first_time: bool):
        # The app may have been running for days
        self.collection_date_input.setMinimumDate(_to_qdate(_min_collection_date()))

        if first_time:
            tally_dir = self.config().tally_dir
            if tally_dir is not None:
                self.out_dir_input.path = tally_dir

    def __update_collection_date(self):
        selected_year = self.year_spinner.value()
        selected_month = self.month_combo.currentIndex() + 1

        assert selected_month >= 1
        assert selected_month <= 12

        min_collection_date = _min_collection_date()

        selected_date = datetime.date(year=selected_year, month=selected_month, day=1)

        # Collection date must be later or equal to min_collection_date
        collection_date = max(min_collection_date, selected_date)

        # Collection date can't be a Saturday or Sunday
        day_offset = 0
        if collection_date.weekday() >= 5:
            day_offset = 7 - collection_date.weekday()
            assert day_offset > 0

        collection_date += datetime.timedelta(days=day_offset)

        self.collection_date_input.setDate(_to_qdate(collection_date))

    def __create_tally(self):
        if not self.validator.validate():
            return

        qt_date = self.collection_date_input.date()
        collection_date = datetime.date(
            year=qt_date.year(), month=qt_date.month(), day=qt_date.day()
        )

        output_dir = self.out_dir_input.path.strip()
        self.config().tally_dir = output_dir

        self.__run_tally(output_dir, collection_date)

    def __set_busy(self, busy: bool):
        self.create_button.setEnabled(not busy)
        self.back_button.setEnabled(not busy)
        self.busy_changed.emit(busy)

    def __start_progress(self):
        self.__progress_start = time.monotonic()
        # Busy (indeterminate) until the first member is reported, so the user
        # sees something is happening even during the initial member query.
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(True)
        self.progress_label.setText(self.tr("Preparing…"))
        self.progress_label.setVisible(True)

    def __stop_progress(self):
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

    @Slot(int, int)
    def __on_progress(self, current: int, total: int):
        if self.progress_bar.maximum() != total:
            self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

        elapsed = time.monotonic() - self.__progress_start
        if current > 0 and elapsed > 0:
            rate = current / elapsed
            remaining = int((total - current) / rate) if rate > 0 else 0
            self.progress_label.setText(
                self.tr(
                    "{current} / {total} members · ~{seconds}s left ({rate}/s)"
                ).format(
                    current=current,
                    total=total,
                    seconds=remaining,
                    rate="{:.0f}".format(rate),
                )
            )
        else:
            self.progress_label.setText(
                self.tr("{current} / {total} members").format(
                    current=current, total=total
                )
            )

    def __run_tally(self, output_dir: str, collection_date: datetime.date):
        self.__set_busy(True)
        self.__start_progress()
        self.status_changed.emit(self.tr("Creating tally…"))

        # Reported from the DB thread; throttle to ~10 updates/s (but always
        # emit the final tick) so a large club doesn't flood the signal queue.
        last_emit = [0.0]

        def report_progress(current: int, total: int):
            now = time.monotonic()
            if current == total or now - last_emit[0] >= 0.1:
                last_emit[0] = now
                self.progress_updated.emit(current, total)

        def tally_task(session):
            assert session is not None
            # The tally archives one-time fees; require a clean session so that
            # a rollback (on failure or on an explicit discard) can only ever
            # undo the tally's own changes, never unrelated unsaved edits.
            if has_uncommitted_changes(session):
                raise _PendingChangesError()
            try:
                # Deliberately not committed here: the user reviews the result
                # first and then decides to keep (commit) or discard (rollback).
                return create_tally(
                    session,
                    output_dir=output_dir,
                    collection_date=collection_date,
                    progress_callback=report_progress,
                    # Built on the DB thread, where it is also used, so the
                    # QTranslator never crosses threads.
                    summary_translator_factory=lambda language: MemberTranslator(
                        language
                    ).translate,
                )
            except Exception:
                session.rollback()
                raise

        def on_success(result: TallyResult):
            self.__stop_progress()
            # Stay busy while the user decides; the session still holds the
            # uncommitted tally changes.
            dialog = TallyResultDialog(result, parent=self)
            dialog.exec()

            if dialog.decision == "keep":
                self.__keep_tally()
            else:
                self.__discard_tally(result.output_path)

        def on_error(error):
            self.__stop_progress()
            self.__set_busy(False)
            if isinstance(error, _PendingChangesError):
                self.status_changed.emit(self.tr("Commit required"))
                answer = QMessageBox.question(
                    self,
                    self.tr("Unsaved changes"),
                    self.tr(
                        "There are unsaved changes. They must be committed before a "
                        "tally can be created. Commit them now and create the tally?"
                    ),
                    buttons=QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No,
                )
                if answer == QMessageBox.StandardButton.Yes:
                    self.__commit_then_tally(output_dir, collection_date)
                else:
                    self.status_changed.emit(self.tr("Tally cancelled"))
                return

            self.status_changed.emit(self.tr("Creating the tally failed"))
            QMessageBox.critical(
                self,
                self.tr("Creating the tally failed"),
                self.tr(
                    "The tally could not be created. Reason given:\n{error}"
                ).format(error=error),
            )

        self.db().submit(tally_task, on_success=on_success, on_error=on_error)

    def __keep_tally(self):
        self.status_changed.emit(self.tr("Saving tally…"))

        def on_success(_):
            self.__set_busy(False)
            self.status_changed.emit(self.tr("Tally created"))

        def on_error(error):
            self.__set_busy(False)
            self.status_changed.emit(self.tr("Saving the tally failed"))
            QMessageBox.critical(
                self,
                self.tr("Saving the tally failed"),
                self.tr(
                    "The tally could not be saved. Reason given:\n{error}"
                ).format(error=error),
            )

        self.db().commit(on_success=on_success, on_error=on_error)

    def __discard_tally(self, output_path: str):
        self.status_changed.emit(self.tr("Discarding tally…"))

        def on_success(_):
            # The rollback restored the archived one-time fees; drop the now
            # orphaned file too so a re-run starts from a clean slate.
            try:
                os.remove(output_path)
            except OSError:
                pass
            self.__set_busy(False)
            self.status_changed.emit(self.tr("Tally discarded"))

        def on_error(error):
            self.__set_busy(False)
            self.status_changed.emit(self.tr("Discarding the tally failed"))
            QMessageBox.critical(
                self,
                self.tr("Discarding the tally failed"),
                self.tr(
                    "The tally could not be discarded. Reason given:\n{error}"
                ).format(error=error),
            )

        self.db().rollback(on_success=on_success, on_error=on_error)

    def __commit_then_tally(self, output_dir: str, collection_date: datetime.date):
        self.__set_busy(True)
        self.status_changed.emit(self.tr("Committing changes…"))

        def on_error(error):
            self.__set_busy(False)
            self.status_changed.emit(self.tr("Commit failed"))
            QMessageBox.critical(
                self,
                self.tr("Commit failed"),
                self.tr(
                    "The changes could not be committed. Reason given:\n{error}"
                ).format(error=error),
            )

        self.db().commit(
            on_success=lambda _: self.__run_tally(output_dir, collection_date),
            on_error=on_error,
        )
