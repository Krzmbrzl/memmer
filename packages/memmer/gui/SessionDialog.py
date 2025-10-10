# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_SessionDialog import Ui_SessionDialog

from typing import Optional

from collections import Counter
from decimal import Decimal
import re

from PySide6.QtCore import QModelIndex, QPersistentModelIndex
from PySide6.QtWidgets import QHeaderView, QMessageBox

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
        self.delete_button.clicked.connect(self.__delete_triggered)
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.__save_triggered)

        self.fixed_fee_button.toggled.connect(
            lambda checked: self.__fixed_fee_model_selected() if checked else None
        )
        self.hourly_fee_button.toggled.connect(
            lambda checked: self.__hourly_fee_model_selected() if checked else None
        )

        self.trainer_table.activated.connect(self.__trainer_activated)
        self.trainer_table.model().rowsInserted.connect(self.__trainer_count_changed)
        self.trainer_table.model().rowsRemoved.connect(self.__trainer_count_changed)

        self.potential_trainers_table.activated.connect(
            self.__potential_trainer_activated
        )

        self.session_member_table.activated.connect(self.__session_member_activated)
        self.session_member_table.model().rowsInserted.connect(
            self.__session_member_count_changed
        )
        self.session_member_table.model().rowsRemoved.connect(
            self.__session_member_count_changed
        )

        self.remaining_member_table.activated.connect(self.__remaining_member_activated)

    def __init_state(self):
        self.__trainer_count_changed()
        self.__session_member_count_changed()

        if self.session is None:
            self.delete_button.setEnabled(False)
            self.save_button.setText(self.tr("Create"))
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

    def __trainer_activated(self, idx: QModelIndex | QPersistentModelIndex):
        from_model = self.trainer_table.model()
        to_model = self.potential_trainers_table.model()

        assert isinstance(from_model, MemberModel)
        assert isinstance(to_model, MemberModel)

        member = from_model.member_for(idx)

        if member:
            from_model.make_inactive(member)
            to_model.make_active(member)

    def __potential_trainer_activated(self, idx: QModelIndex | QPersistentModelIndex):
        from_model = self.potential_trainers_table.model()
        to_model = self.trainer_table.model()

        assert isinstance(from_model, MemberModel)
        assert isinstance(to_model, MemberModel)

        member = from_model.member_for(idx)

        if member:
            from_model.make_inactive(member)
            to_model.make_active(member)

    def __session_member_activated(self, idx: QModelIndex | QPersistentModelIndex):
        from_model = self.session_member_table.model()
        to_model = self.remaining_member_table.model()

        assert isinstance(from_model, MemberModel)
        assert isinstance(to_model, MemberModel)

        member = from_model.member_for(idx)

        if member:
            from_model.make_inactive(member)
            to_model.make_active(member)

    def __remaining_member_activated(self, idx: QModelIndex | QPersistentModelIndex):
        from_model = self.remaining_member_table.model()
        to_model = self.session_member_table.model()

        assert isinstance(from_model, MemberModel)
        assert isinstance(to_model, MemberModel)

        member = from_model.member_for(idx)

        if member:
            from_model.make_inactive(member)
            to_model.make_active(member)

    def __delete_triggered(self):
        if not self.session:
            return

        button = QMessageBox.question(
            self,
            self.tr("Delete session?"),
            self.tr("Are you sure you want to delete session '{}'?").format(
                self.session.name
            ),
        )

        if button != QMessageBox.StandardButton.Yes:
            return

        self.parent_mainwindow().session_about_to_be_deleted.emit(self.session)

        self.sessions().remove(self.session)

        self.sql_session().delete(self.session)
        self.parent_mainwindow().session_deleted.emit(self.session)

        self.accept()

    def __save_triggered(self):
        created_session = False
        if not self.session:
            self.session = Session()
            created_session = True

        changed = False

        set_name = self.name_edit.text().strip()
        assert len(set_name) > 0
        if self.session.name != set_name:
            self.session.name = set_name
            changed = True

        if self.fixed_fee_button.isChecked():
            if self.session.membership_fee is None:
                # TODO: Delete hourly fee
                pass

            set_fee = Decimal(f"{self.fixed_fee_edit.value():.2f}")
            if self.session.membership_fee != set_fee:
                self.session.membership_fee = set_fee
                changed = True
        else:
            assert self.hourly_fee_button.isChecked()
            # TODO

        trainer_model = self.trainer_table.model()
        assert isinstance(trainer_model, MemberModel)
        set_trainers = trainer_model.get_members()
        if set(set_trainers) != set(self.session.trainers):
            self.session.trainers = set_trainers
            changed = True

        session_member_model = self.session_member_table.model()
        assert isinstance(session_member_model, MemberModel)
        set_participants = session_member_model.get_members()
        if set(set_participants) != set(self.session.members):
            self.session.members = set_participants
            changed = True

        if created_session:
            self.sessions().append(self.session)

            self.sql_session().add(self.session)
            self.parent_mainwindow().session_created.emit(self.session)
        elif changed:
            self.parent_mainwindow().session_changed.emit(self.session)

        self.accept()
