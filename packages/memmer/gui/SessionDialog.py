# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_SessionDialog import Ui_SessionDialog

from typing import Optional

import re

from PySide6.QtWidgets import QHeaderView

from memmer.gui import MemmerDialog, MemberModel
from memmer.orm import Session, Member
from memmer.utils import is_active


def is_inactive(member: Member) -> bool:
    return not is_active(member=member)


class SessionDialog(MemmerDialog, Ui_SessionDialog):
    def __init__(self, session: Optional[Session] = None, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.session = session

        self.__create_models()

        self.__connect_signals()

        self.__init_state()

    def __create_models(self):
        trainers = self.session.trainers if self.session is not None else []
        self.trainer_table.setModel(
            MemberModel(
                members=self.members(),
                active=trainers,
                inactive_predicate=is_inactive,
                parent=self.trainer_table,
            )
        )
        self.trainer_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.trainer_table.horizontalHeader().setSectionResizeMode(
            MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
        )
        self.potential_trainers_table.setModel(
            MemberModel(
                members=self.members(),
                inactive=trainers,
                inactive_predicate=is_inactive,
                parent=self.potential_trainers_table,
            )
        )
        self.potential_trainers_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.potential_trainers_table.horizontalHeader().setSectionResizeMode(
            MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
        )

        participants = self.session.members if self.session is not None else []
        self.session_member_table.setModel(
            MemberModel(
                members=self.members(),
                active=participants,
                inactive_predicate=is_inactive,
                parent=self.session_member_table,
            )
        )
        self.session_member_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.session_member_table.horizontalHeader().setSectionResizeMode(
            MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
        )
        self.remaining_member_table.setModel(
            MemberModel(
                members=self.members(),
                inactive=participants,
                inactive_predicate=is_inactive,
                parent=self.remaining_member_table,
            )
        )
        self.remaining_member_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.remaining_member_table.horizontalHeader().setSectionResizeMode(
            MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
        )

    def __connect_signals(self):
        self.cancel_button.clicked.connect(self.reject)

        self.fixed_fee_button.toggled.connect(
            lambda checked: self.__fixed_fee_model_selected() if checked else None
        )
        self.hourly_fee_button.toggled.connect(
            lambda checked: self.__hourly_fee_model_selected() if checked else None
        )

        self.trainer_table.model().rowsInserted.connect(self.__trainer_count_changed)
        self.trainer_table.model().rowsRemoved.connect(self.__trainer_count_changed)

        self.session_member_table.model().rowsInserted.connect(
            self.__session_member_count_changed
        )
        self.session_member_table.model().rowsRemoved.connect(
            self.__session_member_count_changed
        )

    def __init_state(self):
        self.__trainer_count_changed()
        self.__session_member_count_changed()

        if self.session is None:
            return

        self.name_edit.setText(self.session.name)

        if self.session.membership_fee is not None:
            self.fee_stack.setCurrentWidget(self.fixed_fee_widget)
            self.fixed_fee_button.setChecked(True)
            self.fixed_fee_edit.setValue(float(self.session.membership_fee))
        else:
            self.fee_stack.setCurrentWidget(self.hourly_fee_widget)
            self.hourly_fee_button.setChecked(True)
            # TODO

    def __fixed_fee_model_selected(self):
        self.fee_stack.setCurrentWidget(self.fixed_fee_widget)

    def __hourly_fee_model_selected(self):
        self.fee_stack.setCurrentWidget(self.hourly_fee_widget)

    def __trainer_count_changed(self, *_):
        title = self.trainers_group.title()

        title = re.sub(r" \([^()]*\)$", "", title)

        title += f" ({self.trainer_table.model().rowCount()})"

        self.trainers_group.setTitle(title)

    def __session_member_count_changed(self, *_):
        title = self.session_member_group.title()

        title = re.sub(r" \([^()]*\)$", "", title)

        title += f" ({self.session_member_table.model().rowCount()})"

        self.session_member_group.setTitle(title)
