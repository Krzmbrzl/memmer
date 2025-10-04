from .compiled_ui_files.ui_MemberDialog import Ui_MemberDialog

from typing import Optional
from datetime import datetime, date

from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import QDate, QDateTime, Qt

from memmer.gui import (
    MemmerDialog,
    MemberModel,
    SessionModel,
    SessionParticipationModel,
    OneTimeFeeModel,
)
from memmer.orm import Member, Session
from memmer.utils import nominal_year_diff
from memmer.queries import get_relatives

from sqlalchemy import select

default_date = QDate(1870, 1, 1)


class MemberDialog(MemmerDialog, Ui_MemberDialog):
    def __init__(self, member: Optional[Member] = None, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.member = member

        self.__create_models()

        self.__connect_signals()

        self.__init_state()

    def __create_models(self):
        # TODO: Obtain list from buffer / manager
        sessions = list(self.session().scalars(select(Session)).all())
        members = list(self.session().scalars(select(Member)).all())

        self.sessions_table.setModel(
            SessionParticipationModel(
                member=self.member, sessions=sessions, parent=self.sessions_table
            )
        )
        self.sessions_table.horizontalHeader().setSectionResizeMode(
            SessionModel.Column.Name, QHeaderView.ResizeMode.Stretch
        )

        relatives = get_relatives(self.session(), self.member) if self.member else []
        self.relatives_table.setModel(
            MemberModel(members=relatives, parent=self.relatives_table)
        )
        self.relatives_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.relatives_table.horizontalHeader().setSectionResizeMode(
            MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
        )

        for current in relatives:
            members.remove(current)

        # TODO: Determine likely relatives
        self.likely_relatives_table.setModel(
            MemberModel(members=[], parent=self.relatives_table)
        )
        self.likely_relatives_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.likely_relatives_table.horizontalHeader().setSectionResizeMode(
            MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
        )

        self.potential_relatives_table.setModel(
            MemberModel(members=members, parent=self.potential_relatives_table)
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
        self.cancel_button.clicked.connect(self.close)
        self.birthday_edit.dateChanged.connect(self.__birthday_changed)
        self.exited_checkbox.toggled.connect(self.__exited_state_changed)

        self.sepa_mandate_checkbox.toggled.connect(self.__sepa_mandate_given)
        self.monthly_fee_overwrite_checkbox.toggled.connect(
            self.__fee_overwrite_toggled
        )

    def __init_state(self):
        # Set all to known default values
        self.birthday_edit.setDate(default_date)
        self.entry_date_edit.setDate(default_date)
        self.exit_date_edit.setDate(default_date)
        self.sepa_mandate_date_edit.setDate(default_date)

        if self.member is None:
            # Set entry date to today
            self.entry_date_edit.setDate(QDateTime.currentDateTime().date())
            # TODO: Add admission fee as one-time cost
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
            self.bic_edit.setText(member.bic)
            self.account_owner_edit.setText(member.account_owner)

        # TODO: populate sessions and relatives

        # TODO: check if fee overwrite exists
        self.__recompute_monthly_fee()

    def __birthday_changed(self, birthday: QDate):
        if birthday == default_date:
            return

        py_birthday = birthday.toPython()
        assert isinstance(py_birthday, date)
        age = nominal_year_diff(py_birthday, datetime.now().date())

        self.age_label.setText(self.tr(f"({age} years)"))

        self.__recompute_monthly_fee()

    def __exited_state_changed(self, enabled: bool):
        self.exit_date_edit.setEnabled(enabled)

        if enabled and self.exit_date_edit.date() == default_date:
            # Init to today
            self.exit_date_edit.setDate(QDateTime.currentDateTime().date())

        self.__recompute_monthly_fee()

    def __sepa_mandate_given(self, given: bool):
        self.sepa_mandate_date_edit.setEnabled(given)
        self.iban_edit.setEnabled(given)
        self.bic_edit.setEnabled(given)
        self.account_owner_edit.setEnabled(given)

        if given and self.sepa_mandate_date_edit.date() == default_date:
            self.sepa_mandate_date_edit.setDate(QDateTime.currentDateTime().date())

    def __fee_overwrite_toggled(self, overwrite: bool):
        self.monthly_fee_edit.setEnabled(overwrite)

        if not overwrite:
            self.__recompute_monthly_fee()

    def __recompute_monthly_fee(self):
        # TODO compute fee without requiring to save the member details yet
        # -> maybe use a dummy member created only for fee computation?
        pass
