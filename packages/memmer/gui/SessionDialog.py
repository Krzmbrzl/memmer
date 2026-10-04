# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_SessionDialog import Ui_SessionDialog

from typing import Optional

from decimal import Decimal
import re

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtWidgets import QHeaderView, QMessageBox

from memmer.gui import (
    MemmerDialog,
    MemberModel,
    GenericSortFilterProxyModel,
    FormValidator,
    Issue,
    error,
    warning,
)
from memmer.orm import Session, Member
from memmer.utils import is_active


def is_inactive(member: Member) -> bool:
    return not is_active(member=member)


def _member_sort_orders():
    return [
        (MemberModel.Column.LastName, Qt.SortOrder.AscendingOrder),
        (MemberModel.Column.FirstName, Qt.SortOrder.AscendingOrder),
        (MemberModel.Column.City, Qt.SortOrder.AscendingOrder),
    ]


def _member_model(table) -> MemberModel:
    """Returns a table's MemberModel, unwrapping a sort/filter proxy if present"""
    model = table.model()
    if isinstance(model, GenericSortFilterProxyModel):
        model = model.sourceModel()
    assert isinstance(model, MemberModel)
    return model


def _member_at(table, idx: QModelIndex | QPersistentModelIndex) -> Optional[Member]:
    """Resolves the member at a view index, mapping through a proxy if present"""
    model = table.model()
    if isinstance(model, GenericSortFilterProxyModel):
        idx = model.mapToSource(idx)
    return _member_model(table).member_for(idx)


class SessionDialog(MemmerDialog, Ui_SessionDialog):
    def __init__(self, session: Optional[Session] = None, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.session = session

        self.__create_models()

        self.__connect_signals()

        self.__init_state()

        # After initialization so that it doesn't count as user input
        self.__setup_validation()

        if self.session is not None:
            self.validator.reveal_all()

    def __setup_validation(self):
        self.validator = FormValidator(self, self.save_button)

        self.validator.add_check(self.__check_name, [self.name_edit])
        self.validator.add_check(self.__check_fee, [self.fixed_fee_edit])

    def __check_name(self) -> Optional[Issue]:
        name = self.name_edit.text().strip()
        if len(name) == 0:
            return error(self.tr("Please enter a name"))

        for other in self.sessions():
            if other is not self.session and other.name.casefold() == name.casefold():
                return error(
                    self.tr("A session named '{name}' already exists").format(
                        name=other.name
                    )
                )
        return None

    def __check_fee(self) -> Optional[Issue]:
        if self.fixed_fee_edit.value() == 0:
            return warning(self.tr("Participation will be free of charge"))
        return None

    def __create_models(self):
        trainers = self.session.trainers if self.session is not None else []
        # No inactive_predicate here: the already-associated trainers must stay
        # visible (and thus be preserved on save) even if some have become
        # inactive. The predicate only hides inactive members from the
        # candidate list below, so they can't be newly added.
        self.trainer_table.setModel(
            MemberModel(
                members=self.members(),
                active=trainers,
                parent=self.trainer_table,
            )
        )
        self.trainer_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.trainer_table.horizontalHeader().setSectionResizeMode(
            MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
        )
        potential_trainers_proxy = GenericSortFilterProxyModel(
            sort_orders=_member_sort_orders(), parent=self.potential_trainers_table
        )
        potential_trainers_proxy.setSourceModel(
            MemberModel(
                members=self.members(),
                inactive=trainers,
                inactive_predicate=is_inactive,
                parent=self.potential_trainers_table,
            )
        )
        self.potential_trainers_table.setModel(potential_trainers_proxy)
        self.potential_traininers_filter.attach(potential_trainers_proxy)
        self.potential_trainers_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.potential_trainers_table.horizontalHeader().setSectionResizeMode(
            MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
        )

        participants = self.session.members if self.session is not None else []
        # No inactive_predicate here: the already-associated participants must
        # stay visible (and thus be preserved on save) even if some have become
        # inactive. The predicate only hides inactive members from the
        # candidate list below, so they can't be newly added.
        self.session_member_table.setModel(
            MemberModel(
                members=self.members(),
                active=participants,
                parent=self.session_member_table,
            )
        )
        self.session_member_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.session_member_table.horizontalHeader().setSectionResizeMode(
            MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
        )
        remaining_member_proxy = GenericSortFilterProxyModel(
            sort_orders=_member_sort_orders(), parent=self.remaining_member_table
        )
        remaining_member_proxy.setSourceModel(
            MemberModel(
                members=self.members(),
                inactive=participants,
                inactive_predicate=is_inactive,
                parent=self.remaining_member_table,
            )
        )
        self.remaining_member_table.setModel(remaining_member_proxy)
        self.remaining_member_filter.attach(remaining_member_proxy)
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

        self.name_edit.setMaxLength(100)

        # Would be saved without a fee
        self.hourly_fee_button.setEnabled(False)
        self.hourly_fee_button.setToolTip(self.tr("Not supported yet"))

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
        member = _member_at(self.trainer_table, idx)

        if member:
            _member_model(self.trainer_table).make_inactive(member)
            _member_model(self.potential_trainers_table).make_active(member)

    def __potential_trainer_activated(self, idx: QModelIndex | QPersistentModelIndex):
        member = _member_at(self.potential_trainers_table, idx)

        if member:
            _member_model(self.potential_trainers_table).make_inactive(member)
            _member_model(self.trainer_table).make_active(member)

    def __session_member_activated(self, idx: QModelIndex | QPersistentModelIndex):
        member = _member_at(self.session_member_table, idx)

        if member:
            _member_model(self.session_member_table).make_inactive(member)
            _member_model(self.remaining_member_table).make_active(member)

    def __remaining_member_activated(self, idx: QModelIndex | QPersistentModelIndex):
        member = _member_at(self.remaining_member_table, idx)

        if member:
            _member_model(self.remaining_member_table).make_inactive(member)
            _member_model(self.session_member_table).make_active(member)

    def __show_db_error(self, error: Exception):
        QMessageBox.critical(
            self,
            self.tr("Database error"),
            self.tr("The operation failed. Reason given:\n{error}").format(error=error),
        )

    def __delete_triggered(self):
        if not self.session:
            return

        button = QMessageBox.question(
            self,
            self.tr("Delete session?"),
            self.tr("Are you sure you want to delete session '{name}'?").format(
                name=self.session.name
            ),
        )

        if button != QMessageBox.StandardButton.Yes:
            return

        session = self.session
        self.parent_mainwindow().session_about_to_be_deleted.emit(session)

        session_id = session.id

        def delete_task(sql_session):
            assert sql_session is not None
            stored = sql_session.get(Session, session_id)
            if stored is not None:
                sql_session.delete(stored)

        def on_deleted(_):
            if session in self.sessions():
                self.sessions().remove(session)
            # Detach the members from the deleted session's snapshot so their
            # participating_sessions stay consistent (back_populates).
            session.members = []
            session.trainers = []
            self.parent_mainwindow().session_deleted.emit(session)
            self.accept()

        self.db().submit(
            delete_task, on_success=on_deleted, on_error=self.__show_db_error
        )

    def __save_triggered(self):
        if not self.validator.validate():
            return

        created_session = self.session is None
        session_id = self.session.id if self.session is not None else None

        set_name = self.name_edit.text().strip()
        fixed_fee = self.fixed_fee_button.isChecked()
        set_fee = Decimal(f"{self.fixed_fee_edit.value():.2f}") if fixed_fee else None

        trainer_model = self.trainer_table.model()
        assert isinstance(trainer_model, MemberModel)
        set_trainers = trainer_model.get_members()
        trainer_ids = [m.id for m in set_trainers]

        session_member_model = self.session_member_table.model()
        assert isinstance(session_member_model, MemberModel)
        set_participants = session_member_model.get_members()
        participant_ids = [m.id for m in set_participants]

        current = self.session
        if created_session or current is None:
            name_changed = fee_changed = trainers_changed = participants_changed = True
        else:
            name_changed = current.name != set_name
            fee_changed = fixed_fee and current.membership_fee != set_fee
            trainers_changed = {m.id for m in current.trainers} != set(trainer_ids)
            participants_changed = {m.id for m in current.members} != set(
                participant_ids
            )

        changed = (
            created_session
            or name_changed
            or fee_changed
            or trainers_changed
            or participants_changed
        )

        def save_task(sql_session):
            assert sql_session is not None
            if session_id is None:
                session = Session()
                sql_session.add(session)
            else:
                session = sql_session.get(Session, session_id)
                assert session is not None

            session.name = set_name
            if set_fee is not None:
                session.membership_fee = set_fee

            sql_session.flush()

            if trainers_changed:
                session.trainers = [sql_session.get(Member, mid) for mid in trainer_ids]
            if participants_changed:
                session.members = [
                    sql_session.get(Member, mid) for mid in participant_ids
                ]

            sql_session.flush()
            return session.id

        def on_saved(new_id: int):
            # Update the detached snapshot in place, reusing the shared Member
            # instances so identity stays consistent across snapshots.
            if created_session:
                snapshot = Session()
                snapshot.id = new_id
                snapshot.name = set_name
                if set_fee is not None:
                    snapshot.membership_fee = set_fee
                snapshot.trainers = set_trainers
                snapshot.members = set_participants
                self.sessions().append(snapshot)
                self.session = snapshot
                self.parent_mainwindow().session_created.emit(snapshot)
            else:
                assert current is not None
                current.name = set_name
                if set_fee is not None:
                    current.membership_fee = set_fee
                if trainers_changed:
                    current.trainers = set_trainers
                if participants_changed:
                    current.members = set_participants
                if changed:
                    self.parent_mainwindow().session_changed.emit(current)
            self.accept()

        self.db().submit(save_task, on_success=on_saved, on_error=self.__show_db_error)
