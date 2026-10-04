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
    GenericSortFilterProxyModel,
    FormValidator,
    Issue,
    error,
    warning,
)
from memmer import AdmissionFeeKey
from memmer.orm import Member, Session, FixedCost, Gender, OneTimeFee, FeeOverride
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

        # Snapshots of the stored relations/fee override at load time, so that
        # the save handler can tell on the GUI thread whether they changed.
        self.__initial_relative_ids: set[int] = set()
        self.__initial_fee_override: Optional[Decimal] = None

        self.__create_models()

        self.__restrict_inputs()

        self.__connect_signals()

        # Populating the widgets fires __fee_related_data_changed many times
        # (every setDate/setChecked plus load()'s explicit emit). Block the
        # dialog's own signals so the expensive fee recompute runs just once,
        # after everything is in place, instead of piling redundant tasks onto
        # the DB thread. The signal belongs to self, so blocking self covers
        # both the widget-handler emits and the explicit ones.
        with QSignalBlocker(self):
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

    def __relatives_of(self, member: Member) -> List[Member]:
        """The member's relatives, as the shared detached snapshot instances.

        The relation lookup runs on the DB thread and returns ids, which are
        then resolved against self.members() so every Member the dialog handles
        is the same detached instance (keeps identity checks consistent)."""

        def fetch(session):
            assert session is not None
            return [r.id for r in get_relatives(session, member)]

        ids = self.db().run_sync(fetch)
        by_id = {m.id: m for m in self.members()}
        return [by_id[i] for i in ids if i in by_id]

    def __create_models(self):
        self.sessions_table.setModel(
            SessionParticipationModel(
                member=self.member, sessions=self.sessions(), parent=self.sessions_table
            )
        )
        self.sessions_table.horizontalHeader().setSectionResizeMode(
            SessionModel.Column.Name, QHeaderView.ResizeMode.Stretch
        )

        relatives = self.__relatives_of(self.member) if self.member else []
        self.__initial_relative_ids = {m.id for m in relatives}
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

        potential_proxy = GenericSortFilterProxyModel(
            sort_orders=_member_sort_orders(), parent=self.potential_relatives_table
        )
        potential_proxy.setSourceModel(
            MemberModel(
                members=self.members(),
                inactive=relatives,
                parent=self.potential_relatives_table,
            )
        )
        self.potential_relatives_table.setModel(potential_proxy)
        self.potential_relatives_search.attach(potential_proxy)
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

        self.tabWidget.currentChanged.connect(self.__tab_changed)

        # The recompute runs its query on the DB thread and reports the result
        # back via __monthly_fee_changed on the GUI thread.
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
            def fetch_admission_fee(session):
                fee = session.scalars(
                    select(FixedCost).where(FixedCost.name == AdmissionFeeKey)
                ).one_or_none()
                return fee.cost if fee is not None else None

            admission_fee = self.db().run_sync(fetch_admission_fee)
            if admission_fee is not None:
                model = self.one_time_fees_table.model()
                assert isinstance(model, OneTimeFeeModel)
                model.add_fee(reason=self.tr("Admission fee"), amount=admission_fee)
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

        def fetch_fee_override(session):
            override = session.scalars(
                select(FeeOverride).where(FeeOverride.member_id == member.id)
            ).one_or_none()
            return override.amount if override is not None else None

        existing_override_amount = self.db().run_sync(fetch_fee_override)
        self.__initial_fee_override = existing_override_amount
        if existing_override_amount is not None:
            self.monthly_fee_overwrite_checkbox.setChecked(True)
            self.monthly_fee_edit.setValue(float(existing_override_amount))
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
        # Gather the current input on the GUI thread; the fee itself is computed
        # on the DB thread (it queries fixed costs, participations and relations).
        birthday = self.birthday_edit.date().toPython()
        entry_date = self.entry_date_edit.date().toPython()
        exit_date = (
            self.exit_date_edit.date().toPython()
            if self.exited_checkbox.isChecked()
            else None
        )
        is_honorary = self.honorary_member_checkbox.isChecked()

        participation_model = self.sessions_table.model()
        assert isinstance(participation_model, SessionParticipationModel)
        # Only the id and fee are read by the computation. Capture those rather
        # than the snapshot Session objects, so attaching them to the transient
        # dummy can't back-populate (and thereby pollute) any shared/attached
        # Session.members collection.
        session_specs = [
            (s.id, s.membership_fee)
            for s in participation_model.get_participated_sessions()
        ]

        relatives_model = self.relatives_table.model()
        assert isinstance(relatives_model, MemberModel)
        # `relatives` is a plain attribute (not an ORM relationship), so the
        # detached snapshot members can be used directly without back-population.
        relatives = relatives_model.get_members()

        target_date = datetime.now().date()

        def compute(session):
            assert session is not None
            # A transient member carrying the current, unsaved input.
            dummy = Member()
            dummy.birthday = birthday  # type: ignore
            dummy.entry_date = entry_date  # type: ignore
            if exit_date is not None:
                dummy.exit_date = exit_date  # type: ignore
            dummy.is_honorary_member = is_honorary
            dummy.participating_sessions = [
                Session(id=sid, membership_fee=fee) for sid, fee in session_specs
            ]
            dummy.relatives = relatives  # type: ignore

            fee = compute_monthly_fee(
                session=session,
                member=dummy,
                apply_discounts=False,
                target_date=target_date,
            )
            discount = compute_discount(
                session=session, member=dummy, target_date=target_date
            )
            return (fee, discount)

        self.db().submit(
            compute,
            on_success=lambda result: self.__monthly_fee_changed.emit(*result),
        )

    def __relative_activated(self, idx: QModelIndex | QPersistentModelIndex):
        member_id = idx.data(MemberModel.MemberIdRole)

        from_model = _member_model(self.relatives_table)
        to_model = _member_model(self.likely_relatives_table)

        from_model.make_inactive(member_id=member_id)
        to_model.make_active(member_id=member_id)

        self.__fee_related_data_changed.emit()

    def __likely_relative_activated(self, idx: QModelIndex | QPersistentModelIndex):
        member_id = idx.data(MemberModel.MemberIdRole)

        from_model = _member_model(self.likely_relatives_table)
        to_model = _member_model(self.relatives_table)

        from_model.make_inactive(member_id=member_id)
        to_model.make_active(member_id=member_id)

        self.__fee_related_data_changed.emit()

    def __potential_relative_activated(self, idx: QModelIndex | QPersistentModelIndex):
        # idx belongs to the filter proxy; the id role is forwarded to the source
        member_id = idx.data(MemberModel.MemberIdRole)

        from_model = _member_model(self.potential_relatives_table)
        to_model = _member_model(self.relatives_table)

        from_model.make_inactive(member_id=member_id)
        to_model.make_active(member_id=member_id)

        self.__fee_related_data_changed.emit()

    def __tab_changed(self, index: int):
        if self.tabWidget.widget(index) is self.relatives_tab:
            self.__update_likely_relatives()

    def __current_city(self) -> str:
        if self.city_selection_stack.currentWidget() == self.city_edit_page:
            return self.city_edit.text().strip()
        return self.city_combo.currentText().strip()

    def __update_likely_relatives(self):
        """Splits the non-relatives into 'likely' and 'potential' ones.

        A member is considered a likely relative if they share this member's
        bank account (IBAN) or full address, together with that member's own
        relatives."""
        likely_model = _member_model(self.likely_relatives_table)
        potential_model = _member_model(self.potential_relatives_table)

        # Reconsider everyone that isn't an actual relative
        candidates = likely_model.get_members() + potential_model.get_members()

        city = self.__current_city()
        street = self.street_edit.text().strip()
        street_number = self.street_number_edit.text().strip()
        iban = normalize_iban(self.iban_edit.text())

        def is_likely(member: Member) -> bool:
            if iban and member.iban == iban:
                return True
            return bool(
                city
                and street
                and street_number
                and member.city == city
                and member.street == street
                and member.street_number == street_number
            )

        candidate_ids = {c.id for c in candidates}
        base_likely = [c for c in candidates if is_likely(c)]

        # Relatives of a likely relative are likely relatives, too. Resolve all
        # the relations in a single DB-thread task (returns ids only).
        def relatives_of_likely(session):
            extra = set()
            for candidate in base_likely:
                extra.update(r.id for r in get_relatives(session, candidate))
            return extra

        likely_ids = {c.id for c in base_likely}
        likely_ids.update(
            rid
            for rid in self.db().run_sync(relatives_of_likely)
            if rid in candidate_ids
        )

        for candidate in candidates:
            if candidate.id in likely_ids:
                potential_model.make_inactive(member=candidate)
                likely_model.make_active(member=candidate)
            else:
                likely_model.make_inactive(member=candidate)
                potential_model.make_active(member=candidate)

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

    def __show_db_error(self, error: Exception):
        QMessageBox.critical(
            self,
            self.tr("Database error"),
            self.tr("The operation failed. Reason given:\n{error}").format(error=error),
        )

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

        member = self.member
        self.parent_mainwindow().member_about_to_be_deleted.emit(member)

        member_id = member.id

        def delete_task(session):
            assert session is not None
            stored = session.get(Member, member_id)
            if stored is not None:
                session.delete(stored)

        def on_deleted(_):
            if member in self.members():
                self.members().remove(member)
            # Drop the member from the sessions' in-memory snapshots so their
            # participant counts no longer include it (back_populates updates
            # Session.members).
            member.participating_sessions = []
            member.trained_sessions = []
            self.parent_mainwindow().member_deleted.emit(member)
            self.accept()

        self.db().submit(
            delete_task, on_success=on_deleted, on_error=self.__show_db_error
        )

    def __save_triggered(self):
        if not self.validator.validate():
            return

        created_member = self.member is None
        member_id = self.member.id if self.member is not None else None

        # Gather all input on the GUI thread; the actual DB work happens in a
        # single task on the DB thread.
        if self.city_selection_stack.currentWidget() == self.city_edit_page:
            set_city = self.city_edit.text().strip()
        else:
            assert self.city_selection_stack.currentWidget() == self.city_combo_page
            set_city = self.city_combo.currentText()

        def or_none(text: str) -> Optional[str]:
            text = text.strip()
            return text if len(text) > 0 else None

        # Without a mandate the account details must not be persisted: the
        # fields are only disabled (not cleared) when the mandate is removed, so
        # reading them unconditionally would keep stale bank data on the member.
        mandate_given = self.sepa_mandate_checkbox.isChecked()

        scalars = {
            "gender": Gender(value=self.gender_combo.currentIndex()),
            "first_name": self.first_name_edit.text().strip(),
            "last_name": self.last_name_edit.text().strip(),
            "birthday": self.birthday_edit.date().toPython(),
            "street": self.street_edit.text().strip(),
            "street_number": self.street_number_edit.text().strip(),
            "postal_code": self.postal_code_edit.text().strip(),
            "city": set_city,
            "phone_number": or_none(self.phone_number_edit.text()),
            "email_address": or_none(self.email_edit.text()),
            "is_honorary_member": self.honorary_member_checkbox.isChecked(),
            "entry_date": self.entry_date_edit.date().toPython(),
            "exit_date": (
                self.exit_date_edit.date().toPython()
                if self.exited_checkbox.isChecked()
                else None
            ),
            "sepa_mandate_date": (
                self.sepa_mandate_date_edit.date().toPython() if mandate_given else None
            ),
            "iban": (
                or_none(normalize_iban(self.iban_edit.text()))
                if mandate_given
                else None
            ),
            "bic": (
                (self.bic_edit.text().strip().upper() or None)
                if mandate_given
                else None
            ),
            "account_owner": (
                or_none(self.account_owner_edit.text()) if mandate_given else None
            ),
        }

        fee_override = (
            Decimal(f"{self.monthly_fee_edit.value():.2f}")
            if self.monthly_fee_overwrite_checkbox.isChecked()
            else None
        )

        one_time_fee_model = self.one_time_fees_table.model()
        assert isinstance(one_time_fee_model, OneTimeFeeModel)
        one_time_fees = [(f.reason, f.amount) for f in one_time_fee_model.get_fees()]

        session_model = self.sessions_table.model()
        assert isinstance(session_model, SessionParticipationModel)
        # Keep the snapshot Session objects (for the in-memory snapshot update)
        # and their ids (for the DB task).
        set_sessions = session_model.get_participated_sessions()
        participating_ids = [s.id for s in set_sessions]

        relatives_model = self.relatives_table.model()
        assert isinstance(relatives_model, MemberModel)
        relative_ids = [m.id for m in relatives_model.get_members()]

        # Work out what changed (compared against the loaded snapshot) so that
        # unchanged associations aren't rewritten and the right signal fires.
        current = self.member
        relatives_changed = set(relative_ids) != self.__initial_relative_ids
        fee_override_changed = fee_override != self.__initial_fee_override
        if created_member or current is None:
            scalars_changed = True
            participations_changed = True
            one_time_fees_changed = True
        else:
            scalars_changed = any(
                getattr(current, field) != value for field, value in scalars.items()
            )
            participations_changed = {
                s.id for s in current.participating_sessions
            } != set(participating_ids)
            one_time_fees_changed = not container_unordered_equals(
                one_time_fees,
                [(f.reason, f.amount) for f in current.one_time_fees],
            )

        changed = (
            created_member
            or scalars_changed
            or fee_override_changed
            or relatives_changed
            or participations_changed
            or one_time_fees_changed
        )

        def save_task(session):
            assert session is not None
            if member_id is None:
                member = Member()
                session.add(member)
            else:
                member = session.get(Member, member_id)
                assert member is not None

            for field, value in scalars.items():
                setattr(member, field, value)

            # Flush so a new member gets its id before we attach related rows.
            session.flush()

            if participations_changed:
                member.participating_sessions = [
                    session.get(Session, sid) for sid in participating_ids
                ]

            if one_time_fees_changed:
                for existing in list(member.one_time_fees):
                    session.delete(existing)
                member.one_time_fees.clear()
                for reason, amount in one_time_fees:
                    member.one_time_fees.append(
                        OneTimeFee(reason=reason, amount=amount)
                    )

            if fee_override_changed:
                existing_override = session.scalars(
                    select(FeeOverride).where(FeeOverride.member_id == member.id)
                ).one_or_none()
                if fee_override is not None:
                    if existing_override is None:
                        session.add(
                            FeeOverride(member_id=member.id, amount=fee_override)
                        )
                    else:
                        existing_override.amount = fee_override
                elif existing_override is not None:
                    session.delete(existing_override)

            if relatives_changed:
                set_relatives(
                    session=session,
                    member=member,
                    relatives=[session.get(Member, rid) for rid in relative_ids],
                )

            session.flush()
            return member.id

        def on_saved(member_id: int):
            # Update the detached snapshot in place, reusing the shared Session
            # instances so identity stays consistent across the member and
            # session snapshots (the models resolve relationships via index()).
            if created_member:
                snapshot = Member()
                snapshot.id = member_id
                for field, value in scalars.items():
                    setattr(snapshot, field, value)
                snapshot.participating_sessions = set_sessions
                snapshot.one_time_fees = [
                    OneTimeFee(reason=reason, amount=amount)
                    for reason, amount in one_time_fees
                ]
                self.members().append(snapshot)
                self.member = snapshot
                self.parent_mainwindow().member_created.emit(snapshot)
            else:
                assert current is not None
                for field, value in scalars.items():
                    setattr(current, field, value)
                if participations_changed:
                    current.participating_sessions = set_sessions
                if one_time_fees_changed:
                    current.one_time_fees = [
                        OneTimeFee(reason=reason, amount=amount)
                        for reason, amount in one_time_fees
                    ]
                if changed:
                    self.parent_mainwindow().member_changed.emit(current)
            self.accept()

        self.db().submit(save_task, on_success=on_saved, on_error=self.__show_db_error)
