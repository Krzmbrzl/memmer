# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_TallyWidget import Ui_TallyWidget

from typing import Optional

from PySide6.QtCore import Signal, QDate
from PySide6.QtWidgets import QMessageBox

from memmer.gui import MemmerWidget, FormValidator, Issue, error
from memmer.queries import create_tally

import datetime
import os


def _min_collection_date() -> datetime.date:
    return (datetime.datetime.now() + datetime.timedelta(days=2)).date()


def _to_qdate(date: datetime.date) -> QDate:
    return QDate(date.year, date.month, date.day)


class TallyWidget(MemmerWidget, Ui_TallyWidget):
    main_menu_requested = Signal()

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

        def create_impl():
            try:
                create_tally(
                    self.sql_session(),
                    output_dir=output_dir,
                    collection_date=collection_date,
                )
            except Exception as e:
                self.status_changed.emit(self.tr("Creating the tally failed"))

                def show_error(err=e):
                    QMessageBox.critical(
                        self,
                        self.tr("Creating the tally failed"),
                        self.tr(
                            "The tally could not be created. Reason given:\n{error}"
                        ).format(error=err),
                    )

                self.run_in_gui_thread(show_error)
                return

            self.status_changed.emit(self.tr("Tally created"))

        self.async_exec(create_impl)

        self.status_changed.emit(self.tr("Creating tally…"))
