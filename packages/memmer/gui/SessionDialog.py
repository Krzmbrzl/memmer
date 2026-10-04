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

        self.parent_mainwindow().session_about_to_be_deleted.emit(self.session)

        self.sessions().remove(self.session)
        self.sql_session().delete(self.session)

        self.parent_mainwindow().session_deleted.emit(self.session)

        self.accept()

    def __save_triggered(self):
        if not self.validator.validate():
            return

        created_session = False
        if not self.session:
            self.session = Session()
            created_session = True

        changed = False

        set_name = self.name_edit.text().strip()
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
