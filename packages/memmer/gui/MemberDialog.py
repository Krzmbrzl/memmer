# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_MemberDialog import Ui_MemberDialog

from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import re

from PySide6.QtWidgets import QHeaderView, QMessageBox, QLineEdit, QDateEdit
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import (
    QDate,
    QDateTime,
    QEvent,
    QObject,
    Qt,
    QModelIndex,
    QPersistentModelIndex,
    QRegularExpression,
    Signal,
    QSignalBlocker,
)

from memmer.gui import (
    MemmerDialog,
    MemberModel,
    SessionModel,
    SessionParticipationModel,
    OneTimeFeeModel,
    OneTimeFeeAmountDelegate,
    FormValidator,
    Issue,
    error,
    warning,
)
from memmer import AdmissionFeeKey
from memmer.orm import Member, FixedCost, Gender, OneTimeFee, FeeOverride
from memmer.utils import (
    nominal_year_diff,
    container_unordered_equals,
    IbanProblemKind,
    iban_problem,
    normalize_iban,
    is_valid_bic,
    is_valid_email,
    count_digits,
    is_plausible_phone_number,
    is_plausible_street_number,
)
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

# Marks dates that haven't been set (yet)
default_date = QDate(1870, 1, 1)


def _regex_validator(pattern: str, parent) -> QRegularExpressionValidator:
    return QRegularExpressionValidator(QRegularExpression(pattern), parent)


class _UnsetDatePopupFix(QObject):
    """Opens the calendar popup of an unset date at the current month"""

    def __init__(self, date_edit: QDateEdit):
        super().__init__(date_edit)

        self.date_edit = date_edit
        date_edit.calendarWidget().installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Show and self.date_edit.date() == default_date:
            today = QDate.currentDate()
            self.date_edit.calendarWidget().setCurrentPage(today.year(), today.month())

        return False


class MemberDialog(MemmerDialog, Ui_MemberDialog):
    __monthly_fee_changed = Signal(Decimal, Decimal)
    __fee_related_data_changed = Signal()

    def __init__(self, member: Optional[Member] = None, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.member = member
        # None if unknown (e.g. not a German postal code)
        self.__postal_code_known: Optional[bool] = None

        self.__create_models()

        self.__restrict_inputs()

        self.__connect_signals()

        self.__init_state()

        # After initialization so that it doesn't count as user input
        self.__setup_validation()

        if self.member is not None:
            # Make problems in existing data visible right away
            self.validator.reveal_all()

        self.__fee_related_data_changed.emit()

    def __restrict_inputs(self):
        for edit in [
            self.first_name_edit,
            self.last_name_edit,
            self.street_edit,
            self.city_edit,
            self.account_owner_edit,
        ]:
            edit.setMaxLength(100)
        self.email_edit.setMaxLength(254)

        self.street_number_edit.setValidator(
            _regex_validator(r"[0-9A-Za-z /-]{0,15}", self)
        )
        self.postal_code_edit.setValidator(
            _regex_validator(r"[0-9A-Za-z -]{0,10}", self)
        )
        self.phone_number_edit.setValidator(
            _regex_validator(r"[0-9+()/ -]{0,30}", self)
        )
        self.iban_edit.setValidator(_regex_validator(r"[A-Za-z0-9 ]{0,42}", self))
        self.bic_edit.setValidator(_regex_validator(r"[A-Za-z0-9]{0,11}", self))

        self.gender_combo.setPlaceholderText(self.tr("Please select…"))

        for date_edit in [
            self.birthday_edit,
            self.entry_date_edit,
            self.exit_date_edit,
            self.sepa_mandate_date_edit,
        ]:
            # The minimum is displayed as special value
            date_edit.setMinimumDate(default_date)
            date_edit.setSpecialValueText(self.tr("Not set"))
            _UnsetDatePopupFix(date_edit)

        today = QDate.currentDate()
        self.birthday_edit.setMaximumDate(today)
        self.sepa_mandate_date_edit.setMaximumDate(today)

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
        self.one_time_fees_table.setItemDelegateForColumn(
            OneTimeFeeModel.Column.Amount,
            OneTimeFeeAmountDelegate(self.one_time_fees_table),
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

        # Runs on the GUI thread: it uses the shared SQLAlchemy session, which
        # is not thread-safe
        self.__fee_related_data_changed.connect(self.__recompute_monthly_fee)
        self.__monthly_fee_changed.connect(self.__update_monthly_fee)

    def __setup_validation(self):
        self.validator = FormValidator(self, self.save_button)
        add = self.validator.add_check

        add(self.__check_gender, [self.gender_combo])
        add(
            lambda: self.__check_name(
                self.first_name_edit, self.tr("Please enter the first name")
            ),
            [self.first_name_edit],
        )
        add(
            lambda: self.__check_name(
                self.last_name_edit, self.tr("Please enter the last name")
            ),
            [self.last_name_edit],
        )
        add(self.__check_birthday, [self.birthday_edit])
        add(
            self.__check_duplicate,
            [self.birthday_edit],
            triggers=[
                self.first_name_edit.textChanged,
                self.last_name_edit.textChanged,
            ],
            reveal_on=[
                self.birthday_edit.dateChanged,
                self.first_name_edit.editingFinished,
                self.last_name_edit.editingFinished,
            ],
        )

        add(
            lambda: self.__check_required(
                self.street_edit, self.tr("Please enter the street")
            ),
            [self.street_edit],
        )
        add(self.__check_street_number, [self.street_number_edit])
        # Runs after __deduce_city_from_postal_code as that is connected first
        add(
            self.__check_postal_code,
            [self.postal_code_edit],
            triggers=[self.postal_code_edit.textEdited],
        )
        add(
            self.__check_city,
            [self.city_selection_stack],
            triggers=[
                self.city_edit.textChanged,
                self.city_combo.currentTextChanged,
                self.postal_code_edit.textEdited,
            ],
            reveal_on=[
                self.city_edit.editingFinished,
                self.city_combo.currentIndexChanged,
                self.postal_code_edit.editingFinished,
            ],
        )

        add(self.__check_phone_number, [self.phone_number_edit])
        add(self.__check_email, [self.email_edit])

        add(
            self.__check_entry_date,
            [self.entry_date_edit],
            triggers=[self.birthday_edit.dateChanged],
        )
        add(
            self.__check_exit_date,
            [self.exit_date_edit],
            triggers=[self.entry_date_edit.dateChanged],
            reveal_on=[self.exit_date_edit.dateChanged, self.exited_checkbox.toggled],
        )

        mandate_toggled = self.sepa_mandate_checkbox.toggled
        add(
            self.__check_sepa_mandate_date,
            [self.sepa_mandate_date_edit],
            triggers=[mandate_toggled],
        )
        add(self.__check_iban, [self.iban_edit], triggers=[mandate_toggled])
        add(
            self.__check_bic,
            [self.bic_edit],
            triggers=[mandate_toggled, self.iban_edit.textChanged],
            reveal_on=[self.bic_edit.editingFinished, self.iban_edit.editingFinished],
        )
        add(
            lambda: (
                self.__check_required(
                    self.account_owner_edit,
                    self.tr("Please enter the account owner for the SEPA mandate"),
                )
                if self.sepa_mandate_checkbox.isChecked()
                else None
            ),
            [self.account_owner_edit],
            triggers=[mandate_toggled],
        )

        fees = self.one_time_fees_table.model()
        fee_signals = [fees.dataChanged, fees.rowsInserted, fees.rowsRemoved]
        add(
            self.__check_one_time_fees,
            [self.one_time_fees_table],
            reveal_on=fee_signals,
        )

    def __check_one_time_fees(self) -> Optional[Issue]:
        model = self.one_time_fees_table.model()
        assert isinstance(model, OneTimeFeeModel)

        for fee in model.get_fees():
            if len(fee.reason.strip()) == 0:
                return error(
                    self.tr("Please enter a reason for the fee of {amount} €").format(
                        amount=f"{fee.amount:.2f}"
                    )
                )
        for fee in model.get_fees():
            if fee.amount == 0:
                return warning(
                    self.tr("The fee '{reason}' is 0 € and has no effect").format(
                        reason=fee.reason
                    )
                )
            if fee.amount < 0:
                return warning(
                    self.tr(
                        "The fee '{reason}' is negative and will be credited"
                    ).format(reason=fee.reason)
                )
        return None

    def __check_required(self, edit: QLineEdit, message: str) -> Optional[Issue]:
        return error(message) if len(edit.text().strip()) == 0 else None

    def __check_gender(self) -> Optional[Issue]:
        if self.gender_combo.currentIndex() < 0:
            return error(self.tr("Please select the gender"))
        return None

    def __check_name(self, edit: QLineEdit, missing_msg: str) -> Optional[Issue]:
        if len(edit.text().strip()) == 0:
            return error(missing_msg)
        if count_digits(edit.text()) > 0:
            return warning(self.tr("Names usually don't contain digits"))
        return None

    def __check_birthday(self) -> Optional[Issue]:
        birthday = self.birthday_edit.date()
        if birthday == default_date:
            return error(self.tr("Please enter the birthday"))

        age = nominal_year_diff(birthday.toPython(), datetime.now().date())  # type: ignore
        if age > 100:
            return warning(
                self.tr("That makes {age} years – please double-check").format(age=age)
            )
        return None

    def __check_duplicate(self) -> Optional[Issue]:
        first_name = self.first_name_edit.text().strip().casefold()
        last_name = self.last_name_edit.text().strip().casefold()
        birthday = self.birthday_edit.date().toPython()

        for other in self.members():
            if (
                other is not self.member
                and other.birthday == birthday
                and other.first_name.casefold() == first_name
                and other.last_name.casefold() == last_name
            ):
                return warning(
                    self.tr(
                        "A member with this name and birthday already exists – is this a duplicate?"
                    )
                )
        return None

    def __check_street_number(self) -> Optional[Issue]:
        text = self.street_number_edit.text().strip()
        if len(text) == 0:
            return error(self.tr("Please enter the street number"))
        if not is_plausible_street_number(text):
            return warning(
                self.tr("Unusual street number (expected e.g. 12, 12a or 12-14)")
            )
        return None

    def __check_postal_code(self) -> Optional[Issue]:
        text = self.postal_code_edit.text().strip()
        if len(text) == 0:
            return error(self.tr("Please enter the postal code"))
        if not (len(text) == 5 and text.isdigit()):
            return warning(self.tr("German postal codes consist of 5 digits"))
        if self.__postal_code_known is False:
            return warning(
                self.tr("Unknown postal code – please double-check and enter the city")
            )
        return None

    def __check_city(self) -> Optional[Issue]:
        if self.city_selection_stack.currentWidget() == self.city_combo_page:
            city = self.city_combo.currentText()
        else:
            city = self.city_edit.text()

        if len(city.strip()) == 0:
            return error(self.tr("Please enter the city"))
        return None

    def __check_phone_number(self) -> Optional[Issue]:
        text = self.phone_number_edit.text().strip()
        if len(text) > 0 and not is_plausible_phone_number(text):
            return error(
                self.tr(
                    "Not a valid phone number (at least 6 digits, '+' only at the start)"
                )
            )
        return None

    def __check_email(self) -> Optional[Issue]:
        text = self.email_edit.text().strip()
        if len(text) > 0 and not is_valid_email(text):
            return error(
                self.tr("Not a valid email address (expected e.g. name@example.com)")
            )
        return None

    def __check_entry_date(self) -> Optional[Issue]:
        entry = self.entry_date_edit.date()
        if entry == default_date:
            return error(self.tr("Please enter the entry date"))

        birthday = self.birthday_edit.date()
        if birthday != default_date and entry < birthday:
            return error(self.tr("The entry date can't be before the birthday"))

        if entry > QDate.currentDate():
            return warning(self.tr("The entry date lies in the future"))
        return None

    def __check_exit_date(self) -> Optional[Issue]:
        if not self.exited_checkbox.isChecked():
            return None

        exit_date = self.exit_date_edit.date()
        if exit_date == default_date:
            return error(self.tr("Please enter the exit date"))
        if exit_date < self.entry_date_edit.date():
            return error(self.tr("The exit date can't be before the entry date"))
        return None

    def __check_sepa_mandate_date(self) -> Optional[Issue]:
        if (
            self.sepa_mandate_checkbox.isChecked()
            and self.sepa_mandate_date_edit.date() == default_date
        ):
            return error(self.tr("Please enter the date the SEPA mandate was given"))
        return None

    def __check_iban(self) -> Optional[Issue]:
        if not self.sepa_mandate_checkbox.isChecked():
            return None

        text = self.iban_edit.text()
        if len(text.strip()) == 0:
            return error(self.tr("Please enter the IBAN for the SEPA mandate"))

        problem = iban_problem(text)
        if problem is None:
            return None

        match problem.kind:
            case IbanProblemKind.InvalidCharacters:
                msg = self.tr("An IBAN only consists of letters and digits")
            case IbanProblemKind.UnknownCountry:
                msg = self.tr(
                    "Unknown country code '{country}' – an IBAN starts with a country code such as DE"
                ).format(country=problem.country)
            case IbanProblemKind.WrongLength:
                msg = self.tr(
                    "IBANs from {country} have {expected} characters, but this one has {actual}"
                ).format(
                    country=problem.country,
                    expected=problem.expected_length,
                    actual=problem.actual_length,
                )
            case IbanProblemKind.InvalidChecksum:
                msg = self.tr(
                    "This IBAN is invalid (checksum mismatch) – probably a typo"
                )
            case IbanProblemKind.InvalidStructure:
                msg = self.tr(
                    "This IBAN doesn't match the format used in {country}"
                ).format(country=problem.country)
            case IbanProblemKind.UnknownBank:
                msg = self.tr("This IBAN refers to an unknown bank")
            case IbanProblemKind.NotInSepaZone:
                msg = self.tr(
                    "{country} is not part of the SEPA zone – direct debit isn't possible"
                ).format(country=problem.country)
            case _:
                msg = self.tr("This IBAN is invalid")

        return error(msg)

    def __check_bic(self) -> Optional[Issue]:
        if not self.bic_edit.isEnabled():
            # Deduced from the IBAN (or IBAN invalid, which is reported there)
            return None

        text = self.bic_edit.text().strip()
        if len(text) == 0:
            return error(self.tr("The bank is unknown – please enter the BIC manually"))
        if not is_valid_bic(text):
            return error(self.tr("Not a valid BIC (8 or 11 letters and digits)"))
        return None

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
                model.add_fee(reason=self.tr("Admission fee"), amount=fee.cost)
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
            # Note: BIC and institute are inferred from IBAN, if possible
            if len(self.bic_edit.text()) == 0 and member.bic:
                self.bic_edit.setText(member.bic)
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

        self.age_label.setText(self.tr("({age} years)").format(age=age))

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
        self.__deduce_data_from_iban(self.iban_edit.text())

        if given and self.sepa_mandate_date_edit.date() == default_date:
            self.sepa_mandate_date_edit.setDate(QDateTime.currentDateTime().date())

        if given and len(self.account_owner_edit.text().strip()) == 0:
            name = f"{self.first_name_edit.text().strip()} {self.last_name_edit.text().strip()}"
            self.account_owner_edit.setText(name.strip())

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
            iban = IBAN(normalize_iban(text))
        except SchwiftyException:
            # Invalid IBAN
            self.bic_edit.clear()
            self.bic_edit.setEnabled(False)
            self.institute_edit.clear()
            return

        # Banks unknown to schwifty require manual BIC entry
        self.bic_edit.setEnabled(
            iban.bic is None and self.sepa_mandate_checkbox.isChecked()
        )
        if iban.bic is not None:
            self.bic_edit.setText(str(iban.bic))

        if iban.bank_name is not None:
            self.institute_edit.setText(iban.bank_name)
        else:
            self.institute_edit.setText(self.tr("Unknown"))

    def __deduce_city_from_postal_code(self, text: str):
        # TODO: country should be configurable
        zip_code_locator = Nominatim(country="de", unique=False)

        code = text.strip()
        if not (len(code) == 5 and code.isdigit()):
            # Incomplete or not a German postal code
            self.__postal_code_known = None
            self.city_selection_stack.setCurrentWidget(self.city_edit_page)
            self.city_edit.clear()
            self.city_edit.setEnabled(True)
            return

        self.city_edit.setEnabled(False)

        places = zip_code_locator.query_postal_code(code)["place_name"]
        assert len(places) > 0

        self.__postal_code_known = type(places[0]) is str

        if len(places) == 1:
            self.city_selection_stack.setCurrentWidget(self.city_edit_page)
            if not self.__postal_code_known:
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
        if not self.validator.validate():
            return

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
        if set_first_name != self.member.first_name:
            self.member.first_name = set_first_name
            changed = True

        set_last_name = self.last_name_edit.text().strip()
        if set_last_name != self.member.last_name:
            self.member.last_name = set_last_name
            changed = True

        set_birthday: date = self.birthday_edit.date().toPython()  # type: ignore
        if set_birthday != self.member.birthday:
            self.member.birthday = set_birthday
            changed = True

        set_street = self.street_edit.text().strip()
        if set_street != self.member.street:
            self.member.street = set_street
            changed = True

        set_street_number = self.street_number_edit.text().strip()
        if set_street_number != self.member.street_number:
            self.member.street_number = set_street_number
            changed = True

        set_postal_code = self.postal_code_edit.text().strip()
        if set_postal_code != self.member.postal_code:
            self.member.postal_code = set_postal_code
            changed = True

        if self.city_selection_stack.currentWidget() == self.city_edit_page:
            set_city = self.city_edit.text().strip()
        else:
            assert self.city_selection_stack.currentWidget() == self.city_combo_page
            set_city = self.city_combo.currentText()
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
        if set_entry != self.member.entry_date:
            self.member.entry_date = set_entry
            changed = True

        set_exit: Optional[date] = self.exit_date_edit.date().toPython() if self.exited_checkbox.isChecked() else None  # type: ignore
        if set_exit != self.member.exit_date:
            self.member.exit_date = set_exit
            changed = True

        set_sepa: date = self.sepa_mandate_date_edit.date().toPython() if self.sepa_mandate_checkbox.isChecked() else None  # type: ignore
        if set_sepa != self.member.sepa_mandate_date:
            self.member.sepa_mandate_date = set_sepa
            changed = True

        set_iban = normalize_iban(self.iban_edit.text().strip())
        if len(set_iban) == 0:
            set_iban = None
        if set_iban != self.member.iban:
            self.member.iban = set_iban
            changed = True

        set_bic = self.bic_edit.text().strip().upper()
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
            # Assigns the ID
            self.sql_session().flush()

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
