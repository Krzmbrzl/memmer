from .compiled_ui_files.ui_OverviewWidget import Ui_OverviewWidget

from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import Signal

from memmer.gui import MemmerWidget, MemberModel, SessionModel
from memmer.orm import Member, Session

from sqlalchemy import select


class OverviewWidget(MemmerWidget, Ui_OverviewWidget):
    main_menu_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.__connect_signals()

        self.__init_state()

    def __connect_signals(self):
        self.back_button.clicked.connect(self.main_menu_requested.emit)

    def __init_state(self):
        pass

    def opened(self, first_time: bool):
        if first_time:
            # TODO: store member/session list in MainWindow instead of fetching it here
            members = list(self.session().scalars(select(Member)).all())
            sessions = list(self.session().scalars(select(Session)).all())

            self.member_table.setModel(MemberModel(members, self.member_table))

            self.member_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            self.member_table.horizontalHeader().setSectionResizeMode(
                MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
            )

            self.session_table.setModel(SessionModel(sessions, self.session_table))

            self.session_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            self.session_table.horizontalHeader().setSectionResizeMode(
                SessionModel.Column.Participants,
                QHeaderView.ResizeMode.ResizeToContents,
            )
