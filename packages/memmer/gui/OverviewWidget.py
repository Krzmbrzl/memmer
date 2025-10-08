# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_OverviewWidget import Ui_OverviewWidget

from typing import Optional

from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import Signal, Qt, QModelIndex, QPersistentModelIndex

from memmer.gui import MemmerWidget, MemberModel, SessionModel, MemberDialog
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

        self.member_table.activated.connect(self.__member_activated)

    def __init_state(self):
        pass

    def opened(self, first_time: bool):
        if first_time:
            # TODO: store member/session list in MainWindow instead of fetching it here
            members = list(self.session().scalars(select(Member)).all())
            sessions = list(self.session().scalars(select(Session)).all())

            self.member_table.setModel(
                MemberModel(members=members, parent=self.member_table)
            )

            self.member_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            self.member_table.horizontalHeader().setSectionResizeMode(
                MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
            )
            self.member_table.sortByColumn(
                MemberModel.Column.LastName, Qt.SortOrder.AscendingOrder
            )

            self.session_table.setModel(SessionModel(sessions, self.session_table))

            self.session_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            self.session_table.horizontalHeader().setSectionResizeMode(
                SessionModel.Column.Participants,
                QHeaderView.ResizeMode.ResizeToContents,
            )
            self.session_table.sortByColumn(
                SessionModel.Column.Name, Qt.SortOrder.AscendingOrder
            )

    def __member_activated(self, index: QModelIndex | QPersistentModelIndex):
        model = index.model()
        assert isinstance(model, MemberModel)
        member: Optional[Member] = model.member_for(index)

        if member is not None:
            dialog = MemberDialog(member=member, parent=self)

            dialog.show()
