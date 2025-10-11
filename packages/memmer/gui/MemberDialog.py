# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_MemberDialog import Ui_MemberDialog

from typing import Optional
from datetime import datetime, date
from decimal import Decimal
import re

from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import (
    QDate,
    QDateTime,
    Qt,
    QModelIndex,
    QPersistentModelIndex,
    Signal,
    QSignalBlocker,
)

from memmer.gui import (
    MemmerDialog,
    MemberModel,
    SessionModel,
    SessionParticipationModel,
    OneTimeFeeModel,
)
from memmer import AdmissionFeeKey
from memmer.orm import Member, Session, FixedCost
from memmer.utils import nominal_year_diff
from memmer.queries import get_relatives, compute_monthly_fee, compute_discount

from sqlalchemy import select

from schwifty import IBAN
from schwifty.exceptions import SchwiftyException

from pgeocode import Nominatim


default_date = QDate(1870, 1, 1)


class MemberDialog(MemmerDialog, Ui_MemberDialog):
    __monthly_fee_changed = Signal(Decimal, Decimal)
    __fee_related_data_changed = Signal()

    def __init__(self, member: Optional[Member] = None, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.member = member

        self.__create_models()

        self.__connect_signals()

        self.__init_state()

        self.__fee_related_data_changed.emit()

    def __create_models(self):
        self.sessions_table.setModel(
            SessionParticipationModel(
                member=self.member, sessions=self.sessions(), parent=self.sessions_table
            )
        )
        self.sessions_table.horizontalHeader().setSectionResizeMode(
            SessionModel.Column.Name, QHeaderView.ResizeMode.Stretch
        )

        relatives = (
            get_relatives(self.sql_session(), self.member) if self.member else []
        )
        self.relatives_table.setModel(
            MemberModel(
                members=self.members(), active=relatives, parent=self.relatives_table
            )
        )
        self.relatives_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.relatives_table.horizontalHeader().setSectionResizeMode(
            MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
        )

        # TODO: Determine likely relatives
        self.likely_relatives_table.setModel(
            MemberModel(members=self.members(), active=[], parent=self.relatives_table)
        )
        self.likely_relatives_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.likely_relatives_table.horizontalHeader().setSectionResizeMode(
            MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
        )

        if self.member:
            # Don't offer oneself as relative
            relatives.append(self.member)

        self.potential_relatives_table.setModel(
            MemberModel(
                members=self.members(),
                inactive=relatives,
                parent=self.potential_relatives_table,
            )
        )
        self.potential_relatives_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.potential_relatives_table.horizontalHeader().setSectionResizeMode(
            MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
        )

        self.one_time_fees_table.setModel(
            OneTimeFeeModel(member=self.member, parent=self.one_time_fees_table)
        )
        self.one_time_fees_table.horizontalHeader().setSectionResizeMode(
            OneTimeFeeModel.Column.Reason, QHeaderView.ResizeMode.Stretch
        )

    def __connect_signals(self):
        self.cancel_button.clicked.connect(self.reject)

        self.birthday_edit.dateChanged.connect(self.__birthday_changed)
        self.postal_code_edit.textEdited.connect(self.__deduce_city_from_postal_code)
        self.entry_date_edit.dateChanged.connect(
            lambda _: self.__fee_related_data_changed.emit()
        )
        self.exited_checkbox.toggled.connect(self.__exited_state_changed)
        self.exit_date_edit.dateChanged.connect(
            lambda _: self.__fee_related_data_changed.emit()
        )

        self.sepa_mandate_checkbox.toggled.connect(self.__sepa_mandate_given)
        self.iban_edit.textChanged.connect(self.__format_iban)
        self.iban_edit.textChanged.connect(self.__deduce_data_from_iban)
        self.monthly_fee_overwrite_checkbox.toggled.connect(
            self.__fee_overwrite_toggled
        )

        self.relatives_table.activated.connect(self.__relative_activated)
        self.likely_relatives_table.activated.connect(self.__likely_relative_activated)
        self.potential_relatives_table.activated.connect(
            self.__potential_relative_activated
        )

        self.__fee_related_data_changed.connect(
            lambda: self.async_exec(self.__recompute_monthly_fee)
        )
        self.__monthly_fee_changed.connect(self.__update_monthly_fee)

    def __init_state(self):
        # Set all to known default values
        self.birthday_edit.setDate(default_date)
        self.entry_date_edit.setDate(default_date)
        self.exit_date_edit.setDate(default_date)
        self.sepa_mandate_date_edit.setDate(default_date)

        if self.member is None:
            # Set entry date to today
            self.entry_date_edit.setDate(QDateTime.currentDateTime().date())

            # Handle admission fee (if any)
            fee = (
                self.sql_session()
                .scalars(select(FixedCost).where(FixedCost.name == AdmissionFeeKey))
                .one_or_none()
            )
            if fee is not None:
                model = self.one_time_fees_table.model()
                assert isinstance(model, OneTimeFeeModel)
                model.add_fee(reason=self.tr("Admissing fee"), amount=fee.cost)
        else:
            self.load(self.member)

    def load(self, member: Member):
        # General
        self.gender_combo.setCurrentIndex(member.gender.value)
        self.first_name_edit.setText(member.first_name)
        self.last_name_edit.setText(member.last_name)
        self.birthday_edit.setDate(
            QDate.fromString(member.birthday.isoformat(), Qt.DateFormat.ISODate)
        )
        self.street_edit.setText(member.street)
        self.street_number_edit.setText(member.street_number)
        self.postal_code_edit.setText(member.postal_code)
        self.city_edit.setText(member.city)
        self.city_edit.setEnabled(len(member.city) == 0)

        if member.phone_number:
            self.phone_number_edit.setText(member.phone_number)
        if member.email_address:
            self.email_edit.setText(member.email_address)

        self.honorary_member_checkbox.setChecked(member.is_honorary_member)

        self.entry_date_edit.setDate(
            QDate.fromString(member.entry_date.isoformat(), Qt.DateFormat.ISODate)
        )

        if member.exit_date:
            self.exited_checkbox.setChecked(True)
            self.exit_date_edit.setDate(
                QDate.fromString(member.exit_date.isoformat(), Qt.DateFormat.ISODate)
            )

        # Payment
        if member.sepa_mandate_date:
            self.sepa_mandate_checkbox.setChecked(True)
            self.sepa_mandate_date_edit.setDate(
                QDate.fromString(
                    member.sepa_mandate_date.isoformat(), Qt.DateFormat.ISODate
                )
            )

            self.iban_edit.setText(member.iban)
            # Note: BIC and institute are inferred from IBAN
            self.account_owner_edit.setText(member.account_owner)

        self.__fee_related_data_changed.emit()

    def __birthday_changed(self, birthday: QDate):
        if birthday == default_date:
            return

        py_birthday = birthday.toPython()
        assert isinstance(py_birthday, date)
        age = nominal_year_diff(py_birthday, datetime.now().date())

        self.age_label.setText(self.tr(f"({age} years)"))

        self.__fee_related_data_changed.emit()

    def __exited_state_changed(self, enabled: bool):
        self.exit_date_edit.setEnabled(enabled)

        if enabled and self.exit_date_edit.date() == default_date:
            # Init to today
            self.exit_date_edit.setDate(QDateTime.currentDateTime().date())

        self.__fee_related_data_changed.emit()

    def __sepa_mandate_given(self, given: bool):
        self.sepa_mandate_date_edit.setEnabled(given)
        self.iban_edit.setEnabled(given)
        self.account_owner_edit.setEnabled(given)

        if given and self.sepa_mandate_date_edit.date() == default_date:
            self.sepa_mandate_date_edit.setDate(QDateTime.currentDateTime().date())

    def __fee_overwrite_toggled(self, overwrite: bool):
        self.monthly_fee_edit.setEnabled(overwrite)

        if not overwrite:
            self.__fee_related_data_changed.emit()

    def __update_monthly_fee(self, base_fee: Decimal, discount: Decimal):
        self.base_fee_label.setText(f"{base_fee:.2f}€")
        self.discount_label.setText(f"{int(100 * discount):3d}%")

        if not self.monthly_fee_overwrite_checkbox.isChecked():
            fee = base_fee * discount

            self.monthly_fee_edit.setValue(float(fee))

    def __recompute_monthly_fee(self):
        # Create dummy member object with the current data
        dummy = Member()
        dummy.birthday = self.birthday_edit.date().toPython()  # type: ignore
        dummy.entry_date = self.entry_date_edit.date().toPython()  # type: ignore
        if self.exited_checkbox.isChecked():
            dummy.exit_date = self.exit_date_edit.date().toPython()  # type: ignore
        dummy.is_honorary_member = self.honorary_member_checkbox.isChecked()

        participation_model = self.sessions_table.model()
        assert isinstance(participation_model, SessionParticipationModel)
        dummy.participating_sessions = participation_model.get_participated_sessions()

        relatives_model = self.relatives_table.model()
        assert isinstance(relatives_model, MemberModel)
        dummy.relatives = relatives_model.get_members()  # type: ignore

        fee = compute_monthly_fee(
            session=self.sql_session(),
            member=dummy,
            apply_discounts=False,
            target_date=datetime.now().date(),
        )
        discount = compute_discount(
            session=self.sql_session(), member=dummy, target_date=datetime.now().date()
        )

        self.__monthly_fee_changed.emit(fee, discount)

    def __relative_activated(self, idx: QModelIndex | QPersistentModelIndex):
        member_id = idx.data(MemberModel.MemberIdRole)

        from_model = self.relatives_table.model()
        to_model = self.likely_relatives_table.model()

        assert isinstance(from_model, MemberModel)
        assert isinstance(to_model, MemberModel)

        from_model.make_inactive(member_id=member_id)
        to_model.make_active(member_id=member_id)

        self.__fee_related_data_changed.emit()

    def __likely_relative_activated(self, idx: QModelIndex | QPersistentModelIndex):
        member_id = idx.data(MemberModel.MemberIdRole)

        from_model = self.likely_relatives_table.model()
        to_model = self.relatives_table.model()

        assert isinstance(from_model, MemberModel)
        assert isinstance(to_model, MemberModel)

        from_model.make_inactive(member_id=member_id)
        to_model.make_active(member_id=member_id)

        self.__fee_related_data_changed.emit()

    def __potential_relative_activated(self, idx: QModelIndex | QPersistentModelIndex):
        member_id = idx.data(MemberModel.MemberIdRole)

        from_model = self.potential_relatives_table.model()
        to_model = self.relatives_table.model()

        assert isinstance(from_model, MemberModel)
        assert isinstance(to_model, MemberModel)

        from_model.make_inactive(member_id=member_id)
        to_model.make_active(member_id=member_id)

        self.__fee_related_data_changed.emit()

    def __format_iban(self, text: str):
        text = text.upper()

        cursor_pos = self.iban_edit.cursorPosition()

        num_spaces_before_cursor = text[:cursor_pos].count(" ")

        # Remove spaces
        text = text.replace(" ", "")

        # Insert a space every 4 characters
        text = re.sub(r"(.{4})", r"\1 ", text).strip()

        # Re-position cursor accordingly
        pos_without_spaces = cursor_pos - num_spaces_before_cursor
        cursor_pos = (
            pos_without_spaces
            + pos_without_spaces // 4
            - (1 if pos_without_spaces % 4 == 0 else 0)
        )

        # To avoid endless recursion
        blocker = QSignalBlocker(self.iban_edit)
        self.iban_edit.setText(text)
        blocker.unblock()

        self.iban_edit.setCursorPosition(cursor_pos)

    def __deduce_data_from_iban(self, text):
        try:
            iban = IBAN(text)

            assert iban.bic is not None
            self.bic_edit.setText(iban.bic)

            if iban.bank_name is not None:
                self.institute_edit.setText(iban.bank_name)
            else:
                self.institute_edit.setText(self.tr("Unknown"))

        except SchwiftyException:
            # Invalid IBAN
            self.bic_edit.clear()
            self.institute_edit.clear()

    def __deduce_city_from_postal_code(self, text: str):
        # TODO: country should be configurable
        zip_code_locator = Nominatim(country="de", unique=False)

        try:
            code = int(text)
        except:
            return

        places = zip_code_locator.query_postal_code(code)["place_name"]
        assert len(places) > 0

        if len(places) == 1:
            self.city_selection_stack.setCurrentWidget(self.city_edit_page)
            if type(places[0]) is not str:
                # Unknown postal code
                self.city_edit.clear()
                self.city_edit.setEnabled(True)
            else:
                self.city_edit.setText(places[0])  # type: ignore
                self.city_edit.setEnabled(False)
        else:
            self.city_selection_stack.setCurrentWidget(self.city_combo_page)
            self.city_combo.clear()
            self.city_combo.addItems([x for x in places])
            self.city_combo.setCurrentIndex(0)
