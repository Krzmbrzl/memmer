from .compiled_ui_files.ui_TallyWidget import Ui_TallyWidget

from PySide6.QtCore import Signal, QDate

from memmer.gui import MemmerWidget

import datetime


class TallyWidget(MemmerWidget, Ui_TallyWidget):
    main_menu_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.__connect_signals()

        self.__init_state()

    def __connect_signals(self):
        self.back_button.clicked.connect(self.main_menu_requested.emit)
        self.year_spinner.valueChanged.connect(self.__update_collection_date)
        self.month_combo.currentIndexChanged.connect(self.__update_collection_date)

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

    def __update_collection_date(self):
        selected_year = self.year_spinner.value()
        selected_month = self.month_combo.currentIndex() + 1

        assert selected_month >= 1
        assert selected_month <= 12

        min_collection_date = (
            datetime.datetime.now() + datetime.timedelta(days=2)
        ).date()

        selected_date = datetime.date(year=selected_year, month=selected_month, day=1)

        # Collection date must be later or equal to min_collection_date
        collection_date = max(min_collection_date, selected_date)

        # Collection date can't be a Saturday or Sunday
        day_offset = 0
        if collection_date.weekday() >= 5:
            day_offset = 7 - collection_date.weekday()
            assert day_offset > 0

        collection_date += datetime.timedelta(days=day_offset)

        self.collection_date_input.setDate(
            QDate(collection_date.year, collection_date.month, collection_date.day)
        )
