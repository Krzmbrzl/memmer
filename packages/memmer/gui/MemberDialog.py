# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_MemberDialog import Ui_MemberDialog

from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import re

from PySide6.QtWidgets import QHeaderView, QMessageBox
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
from memmer.orm import Member, FixedCost, Gender, OneTimeFee, FeeOverride
from memmer.utils import nominal_year_diff, container_unordered_equals
from memmer.queries import (
    get_relatives,
    compute_monthly_fee,
    compute_discount,
    get_relatives,
    clear_relations,
    set_relatives,
)

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
        self.delete_button.clicked.connect(self.__delete_triggered)
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.__save_triggered)

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
            self.delete_button.setEnabled(False)
            self.save_button.setText(self.tr("Create"))

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

        existing_fee_overwrite = (
            self.sql_session()
            .scalars(select(FeeOverride).where(FeeOverride.member_id == member.id))
            .one_or_none()
        )
        if existing_fee_overwrite is not None:
            self.monthly_fee_overwrite_checkbox.setChecked(True)
            self.monthly_fee_edit.setValue(float(existing_fee_overwrite.amount))
        else:
            self.monthly_fee_overwrite_checkbox.setChecked(False)

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
            self.city_edit.setEnabled(False)
        except:
            self.city_edit.clear()
            self.city_edit.setEnabled(True)
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

    def __delete_triggered(self):
        if not self.member:
            return

        button = QMessageBox.question(
            self,
            self.tr("Delete member?"),
            self.tr(
                "Are you sure you want to delete the member '{first_name} {last_name}'?"
            ).format(
                first_name=self.member.first_name, last_name=self.member.last_name
            ),
        )

        if button != QMessageBox.StandardButton.Yes:
            return

        self.parent_mainwindow().member_about_to_be_deleted.emit(self.member)

        self.members().remove(self.member)
        self.sql_session().delete(self.member)

        self.parent_mainwindow().member_deleted.emit(self.member)

        self.accept()

    def __save_triggered(self):
        created_member = False
        if not self.member:
            self.member = Member()
            created_member = True

        changed = False

        set_gender = Gender(value=self.gender_combo.currentIndex())
        if set_gender != self.member.gender:
            self.member.gender = set_gender
            changed = True

        set_first_name = self.first_name_edit.text().strip()
        assert len(set_first_name) > 0
        if set_first_name != self.member.first_name:
            self.member.first_name = set_first_name
            changed = True

        set_last_name = self.last_name_edit.text().strip()
        assert len(set_last_name) > 0
        if set_last_name != self.member.last_name:
            self.member.last_name = set_last_name
            changed = True

        set_birthday: date = self.birthday_edit.date().toPython()  # type: ignore
        if set_birthday != self.member.birthday:
            self.member.birthday = set_birthday
            changed = True

        set_street = self.street_edit.text().strip()
        assert len(set_street) > 0
        if set_street != self.member.street:
            self.member.street = set_street
            changed = True

        set_street_number = self.street_number_edit.text().strip()
        assert len(set_street_number)
        if set_street_number != self.member.street_number:
            self.member.street_number = set_street_number
            changed = True

        set_postal_code = self.postal_code_edit.text().strip()
        assert len(set_postal_code) > 0
        if set_postal_code != self.member.postal_code:
            self.member.postal_code = set_postal_code
            changed = True

        if self.city_selection_stack.currentWidget() == self.city_edit_page:
            set_city = self.city_edit.text().strip()
        else:
            assert self.city_selection_stack.currentWidget() == self.city_combo_page
            set_city = self.city_combo.currentText()
        assert len(set_city) > 0
        if set_city != self.member.city:
            self.member.city = set_city
            changed = True

        set_phone_number = self.phone_number_edit.text().strip()
        if len(set_phone_number) == 0:
            set_phone_number = None
        if set_phone_number != self.member.phone_number:
            self.member.phone_number = set_phone_number
            changed = True

        set_mail = self.email_edit.text().strip()
        if len(set_mail) == 0:
            set_mail = None
        if set_mail != self.member.email_address:
            self.member.email_address = set_mail
            changed = True

        set_honary = self.honorary_member_checkbox.isChecked()
        if set_honary != self.member.is_honorary_member:
            self.member.is_honorary_member = set_honary
            changed = True

        set_entry: date = self.entry_date_edit.date().toPython()  # type: ignore
        assert set_entry != default_date
        if set_entry != self.member.entry_date:
            self.member.entry_date = set_entry
            changed = True

        set_exit: Optional[date] = self.exit_date_edit.date().toPython() if self.exited_checkbox.isChecked() else None  # type: ignore
        assert set_exit != default_date
        if set_exit != self.member.exit_date:
            self.member.exit_date = set_exit
            changed = True

        set_sepa: date = self.sepa_mandate_date_edit.date().toPython() if self.sepa_mandate_checkbox.isChecked() else None  # type: ignore
        assert set_sepa != default_date
        if set_sepa != self.member.sepa_mandate_date:
            self.member.sepa_mandate_date = set_sepa
            changed = True

        set_iban = self.iban_edit.text().strip().replace(" ", "")
        if len(set_iban) == 0:
            set_iban = None
        if set_iban != self.member.iban:
            self.member.iban = set_iban
            changed = True

        set_bic = self.bic_edit.text().strip()
        if len(set_bic) == 0:
            set_bic = None
        if set_bic != self.member.bic:
            self.member.bic = set_bic
            changed = True

        set_owner = self.account_owner_edit.text().strip()
        if len(set_owner) == 0:
            set_owner = None
        if set_owner != self.member.account_owner:
            self.member.account_owner = set_owner
            changed = True

        existing_fee_overwrite = (
            self.sql_session()
            .scalars(select(FeeOverride).where(FeeOverride.member_id == self.member.id))
            .one_or_none()
            if not created_member
            else None
        )

        fee_override_to_be_added: Optional[FeeOverride] = None
        if self.monthly_fee_overwrite_checkbox.isChecked():
            set_overwrite = Decimal(f"{self.monthly_fee_edit.value():.2f}")
            if existing_fee_overwrite is None:
                changed = True
                fee_override_to_be_added = FeeOverride(amount=set_overwrite)
            elif set_overwrite != existing_fee_overwrite.amount:
                changed = True
                existing_fee_overwrite.amount = set_overwrite
        elif existing_fee_overwrite is not None:
            self.sql_session().delete(existing_fee_overwrite)
            changed = True

        one_time_fees_to_be_set: Optional[List[OneTimeFee]] = None
        one_time_fee_model = self.one_time_fees_table.model()
        assert isinstance(one_time_fee_model, OneTimeFeeModel)
        set_one_time_fees = one_time_fee_model.get_fees()
        if not container_unordered_equals(
            set_one_time_fees,
            self.member.one_time_fees,
            eq_cmp=lambda l, r: l.reason == r.reason and l.amount == r.amount,
        ):
            one_time_fees_to_be_set = [
                OneTimeFee(reason=x.reason, amount=x.amount) for x in set_one_time_fees
            ]
            changed = True

        session_model = self.sessions_table.model()
        assert isinstance(session_model, SessionParticipationModel)
        set_sessions = session_model.get_participated_sessions()
        if not container_unordered_equals(
            set_sessions, self.member.participating_sessions
        ):
            self.member.participating_sessions = set_sessions
            changed = True

        relatives_to_be_set: List[Member] = []
        relatives = (
            get_relatives(session=self.sql_session(), member=self.member)
            if not created_member
            else []
        )
        relatives_model = self.relatives_table.model()
        assert isinstance(relatives_model, MemberModel)
        desired_relatives = relatives_model.get_members()
        if not container_unordered_equals(desired_relatives, relatives):
            if len(relatives) > 0:
                clear_relations(session=self.sql_session(), member=self.member)
            relatives_to_be_set = desired_relatives
            changed = True

        if created_member:
            self.members().append(self.member)

            self.sql_session().add(self.member)

        # We can only add these things once we are certain that self.member
        # is a DB entry and hence has an assigned ID
        assert self.member.id is not None
        if fee_override_to_be_added is not None:
            fee_override_to_be_added.member_id = self.member.id

            print(f"Adding overwrite {fee_override_to_be_added}")
            self.sql_session().add(fee_override_to_be_added)

        if one_time_fees_to_be_set is not None:
            # Remove previously set one-time-fees
            for current in self.member.one_time_fees:
                self.sql_session().delete(current)

            self.member.one_time_fees.clear()

            # Add new fees
            for current in one_time_fees_to_be_set:
                self.member.one_time_fees.append(current)
                assert current.member == self.member

        set_relatives(
            session=self.sql_session(),
            member=self.member,
            relatives=relatives_to_be_set,
        )

        if created_member:
            self.parent_mainwindow().member_created.emit(self.member)
        elif changed:
            self.parent_mainwindow().member_changed.emit(self.member)

        self.accept()
