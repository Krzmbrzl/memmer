# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Dict, Any, Optional, Callable, List, Union

from decimal import Decimal, InvalidOperation
from gettext import gettext as _
import datetime
import re
from pathlib import Path
import json
import os
from datetime import date

import PySimpleGUI as sg

import pgeocode

from schwifty import IBAN
from schwifty.exceptions import SchwiftyException

from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError

from memmer.gui import Layout
from memmer.orm import Member, Session, OneTimeFee, FeeOverride, FixedCost, Setting
from memmer.utils import nominal_year_diff
from memmer.queries import (
    compute_monthly_fee,
    get_relatives,
    set_relatives,
    create_sepa_payment_initiation_message,
    CreditorInfo,
)
from memmer import AdmissionFeeKey

from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import create_engine, URL, select, delete, event

zip_code_locator = pgeocode.Nominatim(country="de")


config_path = Path.joinpath(Path.home(), ".memmer_config.json")


@event.listens_for(SQLSession, "after_flush")
def log_flush(session, flush_context):
    session.info["flushed"] = True


@event.listens_for(SQLSession, "after_commit")
@event.listens_for(SQLSession, "after_rollback")
def reset_flushed(session):
    if "flushed" in session.info:
        del session.info["flushed"]


def has_uncommitted_changes(session: SQLSession):
    return (
        any(session.new)
        or any(session.deleted)
        or any([x for x in session.dirty if session.is_modified(x)])
        or session.info.get("flushed", False)
    )


def set_validation_state(element, valid: bool) -> None:
    if type(element) == sg.Input:
        default_bg = sg.theme_input_background_color()
    elif type(element) == sg.Text:
        default_bg = sg.theme_text_element_background_color()
    else:
        default_bg = sg.theme_background_color()

    element.update(background_color="red" if not valid else default_bg)
    if element.metadata is None:
        element.metadata = {"valid": valid}
    else:
        element.metadata["valid"] = valid


def validate_email(element):
    mail = element.get().strip()

    valid = re.fullmatch(r"[^@]+@[^@]+\.[^@]+", mail) is not None

    set_validation_state(element, valid)

    if valid and mail != element.get():
        element.update(value=mail)


def validate_non_empty(element, strip: bool = True) -> bool:
    if strip:
        if element.get().strip() == "":
            set_validation_state(element, False)
            return False
        else:
            set_validation_state(element, True)
            if element.get() != element.get().strip():
                element.update(value=element.get().strip())
            return True
    else:
        if element.get() == "":
            set_validation_state(element, False)
            return False
        else:
            set_validation_state(element, True)
            return True


def validate_date(element) -> Optional[datetime.date]:
    try:
        # Parse in a date in any known format
        date: datetime.datetime = datetime.datetime.fromisoformat(element.get())

        set_validation_state(element, True)

        # Make sure we represent the date in ISO format
        formatted = date.date().isoformat()
        if formatted != element.get():
            element.update(value=date.date().isoformat())

        return date.date()
    except ValueError:
        set_validation_state(element, False)


def validate_iban(element) -> Optional[IBAN]:
    try:
        iban = IBAN(element.get().strip())

        set_validation_state(element, True)

        if iban.formatted != element.get():
            element.update(value=iban.formatted)

        return iban

    except SchwiftyException:
        set_validation_state(element, False)


def validate_amount(element) -> Optional[Decimal]:
    if not validate_non_empty(element):
        return None

    try:
        decimal = Decimal(element.get())

        if 100 * decimal - int(decimal * 100) != Decimal("0"):
            # We only want to decimal places
            set_validation_state(element, False)
            return None

        set_validation_state(element, True)

        return decimal
    except InvalidOperation:
        set_validation_state(element, False)
        return None


def validate_int(element) -> Optional[int]:
    try:
        code = int(element.get())

        set_validation_state(element, True)

        return code
    except ValueError:
        set_validation_state(element, False)


def filter_list(list_element, filter_string: str, data_key: str = "all_values"):
    filter_string = filter_string.lower()
    dict_metadata = False
    all_values: Optional[List[Any]] = None

    if list_element.metadata is not None and type(list_element.metadata) is dict:
        dict_metadata = True
        all_values = list_element.metadata.get(data_key, None)

    if all_values is None:
        all_values = list_element.get_list_values()

    if dict_metadata:
        list_element.metadata[data_key] = all_values
    elif list_element.metadata is None:
        list_element.metadata = {data_key: all_values}

    # Apply filter
    assert all_values is not None
    filtered = [x for x in all_values if filter_string in str(x).lower()]

    list_element.update(values=filtered)


ONETIMEFEE_REASON_WIDTH: int = 40
ONETIMEFEE_AMOUNT_WIDTH: int = 10
MAX_ONETIME_FEES: int = 3


class MemmerGUI:
    CONNECTOR_CONNECTIONTYPE_COMBO: str = "-CONNECTOR_CONNECTIONTYPE_COMBO-"
    CONNECTOR_DB_FRAME: str = "-CONNECTOR_DB_FRAME-"
    CONNECTOR_SSH_FRAME: str = "-CONNECTOR_SSH_FRAME-"
    CONNECTOR_DBBACKEND_COMBO: str = "-CONNECTOR_DBBACKEND_COMBO-"
    CONNECTOR_CONNECT_BUTTON: str = "-CONNECTOR_CONNECT_EVENT-"
    CONNECTOR_HOST_INPUT: str = "-CONNECTOR_HOST_INPUT-"
    CONNECTOR_USER_INPUT: str = "-CONNECTOR_USER_INPUT-"
    CONNECTOR_PASSWORD_INPUT: str = "-CONNECTOR_PASSWORD_FIELD-"
    CONNECTOR_PORT_INPUT: str = "-CONNECTOR_PORT_INPUT-"
    CONNECTOR_DBNAME_INPUT: str = "-CONNECTOR_DBNAME_INPUT-"
    CONNECTOR_SSHUSER_INPUT: str = "-CONNECTOR_SSHUSER_INPUT-"
    CONNECTOR_SSHPORT_INPUT: str = "-CONNECTOR_SSHPORT_INPUT-"
    CONNECTOR_SSHPASSWORD_INPUT: str = "-CONNECTOR_SSHPASSWORD_INPUT-"
    CONNECTOR_SSHPRIVATEKEY_INPUT: str = "-CONNECTOR_SSHPRIVATEKEY_INPUT-"
    CONNECTOR_SSHPRIVATEKEY_BROWSE_BUTTON: str = (
        "-CONNECTOR_SSHPRIVATEKEY_BROWSE_BUTTON-"
    )
    CONNECTOR_COLUMN: str = "-CONNECTOR_COLUMN-"

    OVERVIEW_MANAGEMENT_BUTTON: str = "-OVERVIEW_MANAGEMENT_BUTTON-"
    OVERVIEW_TALLY_BUTTON: str = "-OVERVIEW_TALLY_BUTTON-"
    OVERVIEW_COLUMN: str = "-OVERVIEW_COLUMN-"

    MANAGEMENT_MEMBERSEARCH_INPUT: str = "MANAGEMENT_MEMBERSEARCH_INPUT-"
    MANAGEMENT_MEMBER_LISTBOX: str = "-MANAGEMENT_MEMBER_LISTBOX-"
    MANAGEMENT_ADDMEMBER_BUTTON: str = "-MANAGEMENT_ADDMEMBER_BUTTON-"
    MANAGEMENT_SESSIONSEARCH_INPUT: str = "MANAGEMENT_SESSIONSEARCH_INPUT-"
    MANAGEMENT_SESSION_LISTBOX: str = "-MANAGEMENT_SESSION_LISTBOX-"
    MANAGEMENT_ADDSESSION_BUTTON: str = "-MANAGEMENT_ADDSESSION_BUTTON-"
    MANAGEMENT_COLUMN: str = "-MANAGEMENT_COLUMN-"

    USEREDITOR_GENERAL_TAB: str = "-USEREDITOR_GENERAL_TAB-"
    USEREDITOR_PAYMENT_TAB: str = "-USEREDITOR_PAYMENT_TAB-"
    USEREDITOR_SESSIONS_TAB: str = "-USEREDITOR_SESSIONS_TAB-"
    USEREDIT_FIRSTNAME_INPUT: str = "-USEREDIT_FIRSTNAME_INPUT-"
    USEREDIT_LASTNAME_INPUT: str = "-USEREDIT_LASTNAME_INPUT-"
    USEREDIT_BIRTHDAY_INPUT: str = "-USEREDIT_BIRTHDAY_INPUT-"
    USEREDIT_AGE_LABEL: str = "-USEREDIT_AGE_LABEL-"
    USEREDIT_STREET_INPUT: str = "-USEREDIT_STREET_INPUT-"
    USEREDIT_STREETNUM_INPUT: str = "-USEREDIT_STREETNUM_INPUT-"
    USEREDIT_POSTALCODE_INPUT: str = "-USEREDIT_POSTALCODE_INPUT-"
    USEREDIT_CITY_INPUT: str = "-USEREDIT_CITY_INPUT-"
    USEREDIT_PHONE_INPUT: str = "-USEREDIT_PHONE_INPUT-"
    USEREDIT_EMAIL_INPUT: str = "-USEREDIT_EMAIL_INPUT-"
    USEREDIT_ENTRYDATE_INPUT: str = "-USEREDIT_ENTRYDATE_INPUT-"
    USEREDIT_EXITDATE_INPUT: str = "-USEREDIT_EXITDATE_INPUT-"
    USEREDIT_HONORABLEMEMBER_CHECKBOX: str = "-USEREDIT_HONORABLEMEMBER_CHECKBOX-"
    USEREDIT_IBAN_INPUT: str = "-USEREDIT_IBAN_INPUT-"
    USEREDIT_BIC_INPUT: str = "-USEREDIT_BIC_INPUT-"
    USEREDIT_CREDITINSTITUTE_INPUT: str = "-USEREDIT_CREDITINSTITUTE_INPUT-"
    USEREDIT_ACCOUNTOWNER_INPUT: str = "-USEREDIT_ACCOUNTOWNER_INPUT-"
    USEREDIT_SEPAMANDATEDATE_INPUT: str = "-USEREDIT_SEPAMANDATEDATE_INPUT-"
    USEREDIT_MONTHLYFEE_INPUT: str = "-USEREDIT_MONTHLYFEE_INPUT-"
    USEREDIT_FEEOVERWRITE_CHECK: str = "-USEREDIT_FEEOVERWRITE_CHECK-"
    USEREDIT_ONETIMEFEES_CONTAINER: str = "-USEREDIT_ONETIMEFEES_CONTAINER-"
    USEREDIT_CANCEL_BUTTON: str = "-USEREDIT_CANCEL_BUTTON-"
    USEREDIT_SAVE_BUTTON: str = "-USEREDIT_SAVE_BUTTON-"
    USEREDIT_DELETE_BUTTON: str = "-USEREDIT_DELETE_BUTTON-"
    USEREDIT_TABGROUP: str = "-USEREDIT_TABGROUP-"
    USEREDIT_SESSION_NAME_LABEL: str = "-USEREDIT_SESSION_SESSION_LABEL-"
    USEREDIT_SESSION_PARTICIPANT_LABEL: str = "-USEREDIT_SESSION_PARTICIPANT_LABEL-"
    USEREDIT_SESSION_TRAINER_LABEL: str = "-USEREDIT_SESSION_TRAINER_LABEL-"
    USEREDIT_RELATIVES_TAB: str = "-USEREDIT_RELATIVES_TAB-"
    USEREDIT_RELATIVES_LISTBOX: str = "-USEREDIT_RELATIVES_LISTBOX-"
    USEREDIT_LIKELYRELATIVES_LISTBOX: str = "-USEREDIT_LIKELYRELATIVES_LISTBOX-"
    USEREDIT_POTENTIALRELATIVES_LISTBOX: str = "-USEREDIT_POTENTIALRELATIVES_LISTBOX-"
    USEREDIT_POTENTIALRELATIVESSEARCH_INPUT: str = (
        "-USEREDIT_POTENTIALRELATIVESSEARCH_INPUT-"
    )
    USEREDITOR_COLUMN: str = "-USEREDITOR_COLUMN-"

    SESSIONEDIT_NAME_INPUT: str = "-SESSIONEDIT_NAME_INPUT-"
    SESSIONEDIT_FEE_INPUT: str = "-SESSIONEDIT_FEE_INPUT-"
    SESSIONEDIT_CANCEL_BUTTON: str = "-SESSIONEDIT_CANCEL_BUTTON-"
    SESSIONEDIT_SAVE_BUTTON: str = "-SESSIONEDIT_SAVE_BUTTON-"
    SESSIONEDIT_DELETE_BUTTON: str = "-SESSIONEDIT_DELETE_BUTTON-"
    SESSIONEDIT_COLUMN: str = "-SESSIONEDIT_COLUMN-"

    def __init__(self):
        self.layout: Layout = [[]]
        self.event_processors: Dict[str, List[Callable[[Dict[Any, Any]], Any]]] = {}
        self.ssh_tunnel: Optional[SSHTunnelForwarder] = None
        self.session: Optional[SQLSession] = None
        self.config: Optional[Dict[str, str]] = None

        self.create_connector()
        self.create_overview()
        self.create_management()
        self.create_usereditor()
        self.create_sessioneditor()

    def connect(self, event: str, processor: Callable[[Dict[Any, Any]], Any]):
        if not event in self.event_processors:
            self.event_processors[event] = [processor]
        else:
            self.event_processors[event].append(processor)

    def prompted_commit(self):
        if self.session:
            if has_uncommitted_changes(self.session):
                # There are uncommitted changes
                result = sg.popup_yes_no(
                    _("Do you want to persist your modifications?"),
                    title=_("Persist changes?"),
                )

                # TODO: Handle translations
                if result == "Yes":
                    self.session.commit()

    def write_to_config(self, key: str, value: Optional[str]):
        if self.config is None:
            self.config = {}

        if value is None and key in self.config:
            del self.config[key]
        elif value is not None:
            self.config[key] = value

    def get_config(self) -> Optional[Dict[str, str]]:
        if not self.config is None:
            return self.config

        if not Path.is_file(config_path):
            return {}

        with open(config_path, "r") as config_file:
            try:
                self.config = json.load(config_file)

                return self.config
            except ValueError as e:
                sg.popup_ok(
                    _("Failed to parse config file ('{}'): {}").format(config_path, e),
                    title=_("Malformatted config"),
                )
                # Get rid of that malformed file
                try:
                    os.remove(config_path)
                except:
                    pass

    def create_connector(self):
        db_labels: Layout = [
            [sg.Text(_("Backend:"))],
            [sg.Text(_("User:"))],
            [sg.Text(_("Password:"))],
            [sg.Text(_("Host:"))],
            [sg.Text(_("Port:"))],
            [sg.Text(_("Database:"))],
        ]

        db_inputs: Layout = [
            [
                sg.Combo(
                    values=["PostgreSQL", "MySQL", "SQLite"],
                    default_value="PostgreSQL",
                    enable_events=True,
                    readonly=True,
                    key=self.CONNECTOR_DBBACKEND_COMBO,
                )
            ],
            [sg.Input(key=self.CONNECTOR_USER_INPUT)],
            [sg.Input(key=self.CONNECTOR_PASSWORD_INPUT, password_char="*")],
            [sg.Input(key=self.CONNECTOR_HOST_INPUT)],
            [sg.Input(key=self.CONNECTOR_PORT_INPUT)],
            [sg.Input(key=self.CONNECTOR_DBNAME_INPUT)],
        ]

        ssh_labels: Layout = [
            [sg.Text(_("User:"))],
            [sg.Text(_("Port:"))],
            [sg.Text(_("Password:"))],
            [sg.Text(_("Private key:"))],
        ]

        ssh_inputs: Layout = [
            [sg.Input(key=self.CONNECTOR_SSHUSER_INPUT)],
            [sg.Input(key=self.CONNECTOR_SSHPORT_INPUT)],
            [sg.Input(key=self.CONNECTOR_SSHPASSWORD_INPUT, password_char="*")],
            [
                sg.Input(key=self.CONNECTOR_SSHPRIVATEKEY_INPUT),
                sg.FileBrowse(
                    button_text="…",
                    key=self.CONNECTOR_SSHPRIVATEKEY_BROWSE_BUTTON,
                    initial_folder=Path.home(),
                ),
            ],
        ]

        connector_layout: Layout = [
            [
                sg.Text(_("Connection type:")),
                sg.Combo(
                    values=["Regular", "SSH-Tunnel"],
                    default_value="Regular",
                    key=self.CONNECTOR_CONNECTIONTYPE_COMBO,
                    enable_events=True,
                    readonly=True,
                ),
            ],
            [sg.HorizontalSeparator()],
            [
                sg.Frame(
                    title=_("Database"),
                    layout=[[sg.Column(layout=db_labels), sg.Column(layout=db_inputs)]],
                    key=self.CONNECTOR_DB_FRAME,
                    expand_x=True,
                )
            ],
            [
                sg.Frame(
                    title=_("SSH"),
                    layout=[
                        [sg.Column(layout=ssh_labels), sg.Column(layout=ssh_inputs)]
                    ],
                    key=self.CONNECTOR_SSH_FRAME,
                    visible=False,
                    expand_x=True,
                )
            ],
            [sg.Button(button_text=_("Connect"), key=self.CONNECTOR_CONNECT_BUTTON)],
        ]

        self.connect(
            self.CONNECTOR_CONNECTIONTYPE_COMBO, self.on_connection_type_changed
        )
        self.connect(self.CONNECTOR_CONNECT_BUTTON, self.on_connect_button_pressed)
        self.connect(self.CONNECTOR_DBBACKEND_COMBO, self.on_db_backend_changed)

        self.layout[0].append(
            sg.Column(
                layout=connector_layout,
                visible=False,
                key=self.CONNECTOR_COLUMN,
                expand_x=True,
                expand_y=True,
            )
        )

    def set_value_and_fire_event(self, key: str, value: Any):
        self.window[key].update(value=value)
        self.window.write_event_value(key, value)

    def open_connector(self):
        config = self.get_config()

        if config is not None:
            connect_type = config.get("connector_type", None)
            db_backend = config.get("connector_db_backend", None)
            db_user = config.get("connector_db_user", None)
            db_host = config.get("connector_db_host")
            db_port = config.get("connector_db_port")
            db_name = config.get("connector_db_name")
            ssh_user = config.get("connector_ssh_user")
            ssh_port = config.get("connector_ssh_port")
            ssh_key = config.get("connector_ssh_key")

            if connect_type is not None and connect_type in ["Regular", "SSH-Tunnel"]:
                self.set_value_and_fire_event(
                    self.CONNECTOR_CONNECTIONTYPE_COMBO, connect_type
                )
            if db_backend is not None and db_backend in [
                "SQLite",
                "MySQL",
                "PostgreSQL",
            ]:
                self.set_value_and_fire_event(
                    self.CONNECTOR_DBBACKEND_COMBO, db_backend
                )
            if db_user is not None:
                self.set_value_and_fire_event(self.CONNECTOR_USER_INPUT, db_user)
            if db_host is not None:
                self.set_value_and_fire_event(self.CONNECTOR_HOST_INPUT, db_host)
            if db_port is not None:
                self.set_value_and_fire_event(self.CONNECTOR_PORT_INPUT, db_port)
            if db_name is not None:
                self.set_value_and_fire_event(self.CONNECTOR_DBNAME_INPUT, db_name)
            if ssh_user is not None:
                self.set_value_and_fire_event(self.CONNECTOR_SSHUSER_INPUT, ssh_user)
            if ssh_port is not None:
                self.set_value_and_fire_event(self.CONNECTOR_SSHPORT_INPUT, ssh_port)
            if ssh_key is not None:
                self.set_value_and_fire_event(
                    self.CONNECTOR_SSHPRIVATEKEY_INPUT, ssh_key
                )

        self.window[self.CONNECTOR_COLUMN].update(visible=True)

    def on_connection_type_changed(self, values: Dict[Any, Any]):
        selected_type = values[self.CONNECTOR_CONNECTIONTYPE_COMBO]

        remote_options_disabled = values[self.CONNECTOR_DBBACKEND_COMBO] == "SQLite"

        if selected_type == "Regular":
            self.window[self.CONNECTOR_SSH_FRAME].update(visible=False)
            self.window[self.CONNECTOR_PORT_INPUT].update(
                disabled=remote_options_disabled
            )
            self.window[self.CONNECTOR_HOST_INPUT].update(
                disabled=remote_options_disabled
            )
        else:
            assert selected_type == "SSH-Tunnel"
            self.window[self.CONNECTOR_SSH_FRAME].update(visible=True)
            self.window[self.CONNECTOR_PORT_INPUT].update(disabled=False)
            self.window[self.CONNECTOR_HOST_INPUT].update(disabled=False)

    def on_db_backend_changed(self, values: Dict[Any, Any]):
        selected_backend = values[self.CONNECTOR_DBBACKEND_COMBO]

        remote_options_disabled = selected_backend == "SQLite"
        reuse_for_ssh = values[self.CONNECTOR_CONNECTIONTYPE_COMBO] == "SSH-Tunnel"

        self.window[self.CONNECTOR_HOST_INPUT].update(
            disabled=remote_options_disabled and not reuse_for_ssh
        )
        self.window[self.CONNECTOR_PORT_INPUT].update(
            disabled=remote_options_disabled and not reuse_for_ssh
        )
        self.window[self.CONNECTOR_USER_INPUT].update(disabled=remote_options_disabled)
        self.window[self.CONNECTOR_PASSWORD_INPUT].update(
            disabled=remote_options_disabled
        )

    def on_connect_button_pressed(self, values: Dict[Any, Any]):
        if values[self.CONNECTOR_CONNECTIONTYPE_COMBO] == "SSH-Tunnel":
            # Establish SSH tunnel
            try:
                if not self.ssh_tunnel is None:
                    self.ssh_tunnel.stop()

                remote_port = (
                    int(values[self.CONNECTOR_PORT_INPUT])
                    if values[self.CONNECTOR_PORT_INPUT] != ""
                    else 80
                )

                self.ssh_tunnel = SSHTunnelForwarder(
                    ssh_address_or_host=values[self.CONNECTOR_HOST_INPUT],
                    ssh_port=int(values[self.CONNECTOR_SSHPORT_INPUT])
                    if values[self.CONNECTOR_SSHPORT_INPUT].strip() != ""
                    else 22,
                    ssh_username=values[self.CONNECTOR_SSHUSER_INPUT],
                    ssh_password=values[self.CONNECTOR_SSHPASSWORD_INPUT]
                    if values[self.CONNECTOR_SSHPASSWORD_INPUT] != ""
                    else None,
                    ssh_pkey=values[self.CONNECTOR_SSHPRIVATEKEY_INPUT],
                    remote_bind_address=(
                        "127.0.0.1",
                        remote_port,
                    ),
                )

                self.ssh_tunnel.start()
            except BaseSSHTunnelForwarderError as e:
                sg.popup_ok(_("Failed to establish ssh tunnel: ") + str(e))
                return

        # Process DB backend that shall be used
        if values[self.CONNECTOR_DBBACKEND_COMBO] == "SQLite":
            backend = "sqlite"

            if values[self.CONNECTOR_DBNAME_INPUT] == "":
                sg.popup_ok(
                    _(
                        "Warning: Using in-memory (temporary) SQLite database not supported"
                    )
                )
                return
        elif values[self.CONNECTOR_DBBACKEND_COMBO] == "PostgreSQL":
            backend = "postgres"
        else:
            assert values[self.CONNECTOR_DBBACKEND_COMBO] == "MySQL"
            backend = "mysql"

        # Figure out what host and port to connect the DB to
        if backend == "sqlite":
            host = None
            port = None
        else:
            port = (
                self.ssh_tunnel.local_bind_port
                if self.ssh_tunnel is not None
                else values[self.CONNECTOR_PORT_INPUT]
            )
            host = (
                self.ssh_tunnel.local_bind_host
                if self.ssh_tunnel is not None
                else values[self.CONNECTOR_HOST_INPUT]
            )

        try:
            connect_url = URL.create(
                drivername=backend,
                username=values[self.CONNECTOR_USER_INPUT]
                if backend != "sqlite"
                else None,
                port=port,
                host=host,
                database=values[self.CONNECTOR_DBNAME_INPUT],
            )

            print("Connecting DB via ", connect_url)

            engine = create_engine(connect_url)

            self.session = SQLSession(bind=engine)

            # Save connection values
            self.write_to_config(
                "connector_type", values[self.CONNECTOR_CONNECTIONTYPE_COMBO]
            )
            self.write_to_config(
                "connector_db_backend", values[self.CONNECTOR_DBBACKEND_COMBO]
            )
            self.write_to_config("connector_db_user", values[self.CONNECTOR_USER_INPUT])
            self.write_to_config("connector_db_host", values[self.CONNECTOR_HOST_INPUT])
            self.write_to_config("connector_db_port", values[self.CONNECTOR_PORT_INPUT])
            self.write_to_config(
                "connector_db_name", values[self.CONNECTOR_DBNAME_INPUT]
            )
            self.write_to_config(
                "connector_ssh_user", values[self.CONNECTOR_SSHUSER_INPUT]
            )
            self.write_to_config(
                "connector_ssh_port", values[self.CONNECTOR_SSHPORT_INPUT]
            )
            self.write_to_config(
                "connector_ssh_key", values[self.CONNECTOR_SSHPRIVATEKEY_INPUT]
            )

            # Switch to overview
            self.window[self.CONNECTOR_COLUMN].update(visible=False)
            self.open_overview()
        except Exception as e:
            sg.popup_ok(_("Invalid connection parameters!\n{}".format(e)))

    def create_overview(self):
        overview: Layout = [
            [
                sg.Button(
                    button_text=_("Management"), key=self.OVERVIEW_MANAGEMENT_BUTTON
                )
            ],
            [sg.Button(button_text=_("Create tally"), key=self.OVERVIEW_TALLY_BUTTON)],
        ]

        self.connect(self.OVERVIEW_MANAGEMENT_BUTTON, self.on_management_button_pressed)
        self.connect(self.OVERVIEW_TALLY_BUTTON, self.on_tally_button_pressed)

        self.layout[0].append(
            sg.Column(
                layout=overview,
                visible=False,
                key=self.OVERVIEW_COLUMN,
                expand_x=True,
                expand_y=True,
            )
        )

    def open_overview(self):
        # TODO: Check permissions on DB and hide inappropriate actions
        self.window[self.OVERVIEW_COLUMN].update(visible=True)

    def on_management_button_pressed(self, values: Dict[Any, Any]):
        self.window[self.OVERVIEW_COLUMN].update(visible=False)
        self.open_management()

    def on_tally_button_pressed(self, values: Dict[Any, Any]):
        assert self.session != None

        creditor_name = (
            self.session.scalars(
                select(Setting).where(Setting.name == Setting.TALLY_CREDITOR_NAME)
            )
            .one()
            .value
        )
        creditor_iban = (
            self.session.scalars(
                select(Setting).where(Setting.name == Setting.TALLY_CREDITOR_IBAN)
            )
            .one()
            .value
        )
        creditor_bic = (
            self.session.scalars(
                select(Setting).where(Setting.name == Setting.TALLY_CREDITOR_BIC)
            )
            .one()
            .value
        )
        creditor_id = (
            self.session.scalars(
                select(Setting).where(Setting.name == Setting.TALLY_CREDITOR_ID)
            )
            .one()
            .value
        )

        message = create_sepa_payment_initiation_message(
            session=self.session,
            msg_id="TODO-Find-better-id",
            creditor_info=CreditorInfo(
                name=creditor_name,
                iban=creditor_iban,
                bic=creditor_bic,
                identification=creditor_id,
            ),
            collection_date=date(year=2023, month=11, day=1),
        )

        print(message)

        # sg.popup_ok(_("Not yet implemented"))

    def create_management(self):
        user_management: Layout = [
            [sg.Button(_("Add member"), key=self.MANAGEMENT_ADDMEMBER_BUTTON)],
            [sg.HorizontalSeparator()],
            [
                sg.Text(_("Search:")),
                sg.Input(key=self.MANAGEMENT_MEMBERSEARCH_INPUT, enable_events=True),
            ],
            [
                sg.Listbox(
                    values=[],
                    select_mode="LISTBOX_SELECT_MODE_SINGLE",
                    key=self.MANAGEMENT_MEMBER_LISTBOX,
                    bind_return_key=True,
                    expand_x=True,
                    expand_y=True,
                )
            ],
        ]
        session_management: Layout = [
            [sg.Button(_("Add session"), key=self.MANAGEMENT_ADDSESSION_BUTTON)],
            [sg.HorizontalSeparator()],
            [
                sg.Text(_("Search:")),
                sg.Input(key=self.MANAGEMENT_SESSIONSEARCH_INPUT, enable_events=True),
            ],
            [
                sg.Listbox(
                    values=[],
                    select_mode="LISTBOX_SELECT_MODE_SINGLE",
                    key=self.MANAGEMENT_SESSION_LISTBOX,
                    bind_return_key=True,
                    expand_x=True,
                    expand_y=True,
                )
            ],
        ]

        combined: Layout = [
            [
                sg.Frame(
                    title=_("Members"),
                    layout=user_management,
                    expand_x=True,
                    expand_y=True,
                )
            ],
            [
                sg.Frame(
                    title=_("Sessions"),
                    layout=session_management,
                    expand_x=True,
                    expand_y=True,
                )
            ],
        ]

        self.connect(
            self.MANAGEMENT_MEMBERSEARCH_INPUT,
            lambda values: filter_list(
                self.window[self.MANAGEMENT_MEMBER_LISTBOX],
                values[self.MANAGEMENT_MEMBERSEARCH_INPUT],
            ),
        )
        self.connect(
            self.MANAGEMENT_SESSIONSEARCH_INPUT,
            lambda values: filter_list(
                self.window[self.MANAGEMENT_SESSION_LISTBOX],
                values[self.MANAGEMENT_SESSIONSEARCH_INPUT],
            ),
        )

        self.connect(self.MANAGEMENT_ADDMEMBER_BUTTON, self.on_addmember_button_pressed)
        self.connect(
            self.MANAGEMENT_ADDSESSION_BUTTON, self.on_addsession_button_pressed
        )
        self.connect(self.MANAGEMENT_MEMBER_LISTBOX, self.on_memberlist_activated)
        self.connect(self.MANAGEMENT_SESSION_LISTBOX, self.on_sessionlist_activated)

        self.layout[0].append(
            sg.Column(
                layout=combined,
                visible=False,
                key=self.MANAGEMENT_COLUMN,
                expand_x=True,
                expand_y=True,
            )
        )

    def open_management(self):
        self.window[self.MANAGEMENT_COLUMN].update(visible=True)

        assert self.session is not None

        # Populate member and session lists

        members = self.session.scalars(
            select(Member)
            .order_by(Member.last_name.asc())
            .order_by(Member.first_name.asc())
        ).all()

        self.window[self.MANAGEMENT_MEMBER_LISTBOX].update(values=members)

        sessions = self.session.scalars(
            select(Session).order_by(Session.name.asc())
        ).all()

        self.window[self.MANAGEMENT_SESSION_LISTBOX].update(values=sessions)

    def on_addmember_button_pressed(self, values: Dict[Any, Any]):
        self.window[self.MANAGEMENT_COLUMN].update(visible=False)
        self.open_usereditor()

    def on_addsession_button_pressed(self, values: Dict[Any, Any]):
        self.window[self.MANAGEMENT_COLUMN].update(visible=False)
        self.open_sessioneditor()

    def on_memberlist_activated(self, values: Dict[Any, Any]):
        selected_entries = len(values[self.MANAGEMENT_MEMBER_LISTBOX])

        if selected_entries == 0:
            return
        elif selected_entries > 1:
            sg.popup_ok(_("Selecting more than one member at once is not implemented"))
            return

        assert selected_entries == 1

        # Open user editor for that user
        self.window[self.MANAGEMENT_COLUMN].update(visible=False)
        self.open_usereditor(values[self.MANAGEMENT_MEMBER_LISTBOX][0])

    def on_sessionlist_activated(self, values: Dict[Any, Any]):
        selected_entries = len(values[self.MANAGEMENT_SESSION_LISTBOX])

        if selected_entries == 0:
            return
        elif selected_entries > 1:
            sg.popup_ok(_("Selecting more than one session at once is not implemented"))
            return

        assert selected_entries == 1

        # Open session editor for that session
        self.window[self.MANAGEMENT_COLUMN].update(visible=False)
        self.open_sessioneditor(values[self.MANAGEMENT_SESSION_LISTBOX][0])

    def create_usereditor(self):
        personal: Layout = [
            [
                sg.Column(
                    layout=[
                        [sg.Text(_("First name:"))],
                        [sg.Text(_("Last name:"))],
                        [sg.Text(_("Birthday:"))],
                    ]
                ),
                sg.Column(
                    layout=[
                        [sg.Input(key=self.USEREDIT_FIRSTNAME_INPUT)],
                        [sg.Input(key=self.USEREDIT_LASTNAME_INPUT)],
                        [
                            sg.Input(
                                key=self.USEREDIT_BIRTHDAY_INPUT, enable_events=True
                            ),
                            sg.Text(text="", key=self.USEREDIT_AGE_LABEL),
                        ],
                    ]
                ),
            ]
        ]

        address: Layout = [
            [
                sg.Column(
                    layout=[
                        [sg.Text(_("Street:"))],
                        [sg.Text(_("Street number:"))],
                        [sg.Text(_("Postal code:"))],
                        [sg.Text(_("City:"))],
                    ]
                ),
                sg.Column(
                    layout=[
                        [sg.Input(key=self.USEREDIT_STREET_INPUT)],
                        [sg.Input(key=self.USEREDIT_STREETNUM_INPUT)],
                        [
                            sg.Input(
                                key=self.USEREDIT_POSTALCODE_INPUT, enable_events=True
                            )
                        ],
                        [sg.Input(key=self.USEREDIT_CITY_INPUT, disabled=True)],
                    ]
                ),
            ]
        ]

        contact: Layout = [
            [
                sg.Column(
                    layout=[
                        [sg.Text(_("Phone number:"))],
                        [sg.Text(_("Email:"))],
                    ]
                ),
                sg.Column(
                    layout=[
                        [sg.Input(key=self.USEREDIT_PHONE_INPUT)],
                        [sg.Input(key=self.USEREDIT_EMAIL_INPUT, enable_events=True)],
                    ]
                ),
            ]
        ]

        membership: Layout = [
            [
                sg.Column(
                    layout=[
                        [sg.Text(_("Entry date:"))],
                        [sg.Text(_("Exit date:"))],
                    ]
                ),
                sg.Column(
                    layout=[
                        [
                            sg.Input(
                                key=self.USEREDIT_ENTRYDATE_INPUT, enable_events=True
                            )
                        ],
                        [
                            sg.Input(
                                key=self.USEREDIT_EXITDATE_INPUT, enable_events=True
                            )
                        ],
                    ]
                ),
            ],
            [
                sg.Checkbox(
                    text=_("Honorable member"),
                    default=False,
                    key=self.USEREDIT_HONORABLEMEMBER_CHECKBOX,
                )
            ],
        ]

        self.connect(self.USEREDIT_BIRTHDAY_INPUT, self.on_member_birthday_changed)
        self.connect(self.USEREDIT_EMAIL_INPUT, self.on_member_email_changed)
        self.connect(self.USEREDIT_ENTRYDATE_INPUT, self.on_member_entrydate_changed)
        self.connect(self.USEREDIT_EXITDATE_INPUT, self.on_member_exitdate_changed)
        self.connect(self.USEREDIT_POSTALCODE_INPUT, self.on_postal_code_changed)

        general_tab: Layout = [
            [sg.Frame(title=_("Personal"), layout=personal, expand_x=True)],
            [sg.HorizontalSeparator()],
            [sg.Frame(title=_("Address"), layout=address, expand_x=True)],
            [sg.HorizontalSeparator()],
            [sg.Frame(title=_("Contact"), layout=contact, expand_x=True)],
            [sg.HorizontalSeparator()],
            [sg.Frame(title=_("Membership"), layout=membership, expand_x=True)],
        ]

        bank_details: Layout = [
            [
                sg.Column(
                    layout=[
                        [sg.Text(_("SEPA mandate date:"))],
                        [sg.Text(_("IBAN:"))],
                        [sg.Text(_("BIC:"))],
                        [sg.Text(_("Institute:"))],
                        [sg.Text(_("Account owner:"))],
                    ]
                ),
                sg.Column(
                    layout=[
                        [
                            sg.Input(
                                key=self.USEREDIT_SEPAMANDATEDATE_INPUT,
                                enable_events=True,
                            )
                        ],
                        [sg.Input(key=self.USEREDIT_IBAN_INPUT, enable_events=True)],
                        [sg.Input(key=self.USEREDIT_BIC_INPUT, disabled=True)],
                        [
                            sg.Input(
                                key=self.USEREDIT_CREDITINSTITUTE_INPUT, disabled=True
                            )
                        ],
                        [sg.Input(key=self.USEREDIT_ACCOUNTOWNER_INPUT)],
                    ]
                ),
            ]
        ]

        fees: Layout = [
            [
                sg.Column(
                    layout=[
                        [sg.Text(_("Monthly fee:"))],
                        [sg.Text(_("One-time fees:"))],
                        [sg.VPush()],
                    ],
                    expand_y=True,
                ),
                sg.Column(
                    layout=[
                        [
                            sg.Input(
                                default_text="0",
                                disabled=True,
                                key=self.USEREDIT_MONTHLYFEE_INPUT,
                                enable_events=True,
                            ),
                            sg.Checkbox(
                                text=_("Overwrite"),
                                default=False,
                                key=self.USEREDIT_FEEOVERWRITE_CHECK,
                                enable_events=True,
                            ),
                        ],
                        [
                            sg.Column(
                                layout=[
                                    [
                                        sg.Text(
                                            text=_("Reason"),
                                            size=(ONETIMEFEE_REASON_WIDTH, 1),
                                        ),
                                        sg.Text(
                                            text=_("Amount"),
                                            size=(ONETIMEFEE_AMOUNT_WIDTH, 1),
                                        ),
                                    ],
                                    [sg.HorizontalSeparator()],
                                    *[
                                        [
                                            sg.Input(
                                                size=(ONETIMEFEE_REASON_WIDTH, 1),
                                                key="-onetimefee_reason_{}-".format(i),
                                            ),
                                            sg.Input(
                                                size=(ONETIMEFEE_AMOUNT_WIDTH, 1),
                                                key="-onetimefee_amount_{}-".format(i),
                                                enable_events=True,
                                            ),
                                        ]
                                        for i in range(MAX_ONETIME_FEES)
                                    ],
                                ],
                                key=self.USEREDIT_ONETIMEFEES_CONTAINER,
                            )
                        ],
                    ]
                ),
            ],
        ]

        payment_tab: Layout = [
            [sg.Frame(title=_("Bank details"), layout=bank_details, expand_x=True)],
            [sg.HorizontalSeparator()],
            [sg.Frame(title=_("Fees"), layout=fees, expand_x=True)],
        ]

        self.connect(
            self.USEREDIT_SEPAMANDATEDATE_INPUT,
            self.on_member_sepa_mandate_date_changed,
        )
        self.connect(self.USEREDIT_IBAN_INPUT, self.on_member_iban_changed)
        self.connect(self.USEREDIT_MONTHLYFEE_INPUT, self.on_member_monthly_fee_changed)
        self.connect(
            self.USEREDIT_FEEOVERWRITE_CHECK, self.on_member_fee_overwrite_changed
        )
        for i in range(MAX_ONETIME_FEES):
            self.connect("-onetimefee_reason_{}-".format(i), self.on_onetimefee_changed)
            self.connect("-onetimefee_amount_{}-".format(i), self.on_onetimefee_changed)

        name_width: int = 40
        participant_width: int = len(_("Participant"))
        trainer_width: int = len(_("Trainer"))

        sessions_tab: Layout = [
            [
                sg.Text(
                    text=_("Session"),
                    size=(name_width, 1),
                    key=self.USEREDIT_SESSION_NAME_LABEL,
                ),
                sg.Text(
                    text=_("Participant"),
                    size=(participant_width, 1),
                    key=self.USEREDIT_SESSION_PARTICIPANT_LABEL,
                ),
                sg.Text(
                    text=_("Trainer"),
                    size=(trainer_width, 1),
                    key=self.USEREDIT_SESSION_TRAINER_LABEL,
                ),
            ],
            [sg.HorizontalSeparator()],
        ]

        relatives_tab: Layout = [
            [sg.Text(text=_("Relatives"))],
            [
                sg.Listbox(
                    values=[],
                    select_mode="LISTBOX_SELECT_MODE_SINGLE",
                    key=self.USEREDIT_RELATIVES_LISTBOX,
                    bind_return_key=True,
                    expand_x=True,
                    expand_y=True,
                )
            ],
            [sg.HorizontalSeparator()],
            [sg.Text(text=_("Likely relatives"))],
            [
                sg.Listbox(
                    values=[],
                    select_mode="LISTBOX_SELECT_MODE_SINGLE",
                    key=self.USEREDIT_LIKELYRELATIVES_LISTBOX,
                    bind_return_key=True,
                    expand_x=True,
                    expand_y=True,
                )
            ],
            [sg.HorizontalSeparator()],
            [
                sg.Text(text=_("Search:")),
                sg.Input(
                    key=self.USEREDIT_POTENTIALRELATIVESSEARCH_INPUT, enable_events=True
                ),
            ],
            [sg.Text(text=_("Potential relatives"))],
            [
                sg.Listbox(
                    values=[],
                    select_mode="LISTBOX_SELECT_MODE_SINGLE",
                    key=self.USEREDIT_POTENTIALRELATIVES_LISTBOX,
                    bind_return_key=True,
                    expand_x=True,
                    expand_y=True,
                )
            ],
        ]

        self.connect(
            self.USEREDIT_POTENTIALRELATIVESSEARCH_INPUT,
            lambda values: filter_list(
                self.window[self.USEREDIT_POTENTIALRELATIVES_LISTBOX],
                values[self.USEREDIT_POTENTIALRELATIVESSEARCH_INPUT],
            ),
        )

        self.connect(
            self.USEREDIT_RELATIVES_LISTBOX, self.on_useredit_relatives_list_activated
        )
        self.connect(
            self.USEREDIT_LIKELYRELATIVES_LISTBOX,
            self.on_useredit_likelyrelatives_list_activated,
        )
        self.connect(
            self.USEREDIT_POTENTIALRELATIVES_LISTBOX,
            self.on_useredit_potentialrelatives_list_activated,
        )

        editor: Layout = [
            [
                sg.TabGroup(
                    layout=[
                        [
                            sg.Tab(
                                title=_("General"),
                                layout=general_tab,
                                key=self.USEREDITOR_GENERAL_TAB,
                            ),
                            sg.Tab(
                                title=_("Payment"),
                                layout=payment_tab,
                                key=self.USEREDITOR_PAYMENT_TAB,
                            ),
                            sg.Tab(
                                title=_("Sessions"),
                                layout=sessions_tab,
                                key=self.USEREDITOR_SESSIONS_TAB,
                                metadata={
                                    "number_of_sessions": 0,
                                    "name_width": 40,
                                    "participant_width": len(_("Participant")),
                                    "trainer_width": len(_("Trainer")),
                                },
                            ),
                            sg.Tab(
                                title=_("Relatives"),
                                layout=relatives_tab,
                                key=self.USEREDIT_RELATIVES_TAB,
                            ),
                        ]
                    ],
                    key=self.USEREDIT_TABGROUP,
                    expand_x=True,
                    expand_y=True,
                    metadata={},
                    enable_events=True,
                ),
            ],
            [
                sg.Push(),
                sg.Button(button_text=_("Cancel"), key=self.USEREDIT_CANCEL_BUTTON),
                sg.Button(button_text=_("Save"), key=self.USEREDIT_SAVE_BUTTON),
                sg.Button(button_text=_("Delete"), key=self.USEREDIT_DELETE_BUTTON),
            ],
        ]

        self.connect(
            self.USEREDIT_RELATIVES_TAB, self.on_useredit_relatives_tab_activated
        )

        self.connect(self.USEREDIT_CANCEL_BUTTON, self.on_useredit_cancel_pressed)
        self.connect(self.USEREDIT_SAVE_BUTTON, self.on_useredit_save_pressed)
        self.connect(self.USEREDIT_DELETE_BUTTON, self.on_useredit_delete_pressed)

        self.layout[0].append(
            sg.Column(
                layout=editor,
                visible=False,
                key=self.USEREDITOR_COLUMN,
                expand_x=True,
                expand_y=True,
            )
        )

    def open_usereditor(self, user: Optional[Member] = None):
        assert self.session is not None

        # Clear elements
        for current in [
            self.USEREDIT_FIRSTNAME_INPUT,
            self.USEREDIT_LASTNAME_INPUT,
            self.USEREDIT_BIRTHDAY_INPUT,
            self.USEREDIT_STREET_INPUT,
            self.USEREDIT_STREETNUM_INPUT,
            self.USEREDIT_POSTALCODE_INPUT,
            self.USEREDIT_CITY_INPUT,
            self.USEREDIT_PHONE_INPUT,
            self.USEREDIT_EMAIL_INPUT,
            self.USEREDIT_ENTRYDATE_INPUT,
            self.USEREDIT_EXITDATE_INPUT,
            self.USEREDIT_SEPAMANDATEDATE_INPUT,
            self.USEREDIT_IBAN_INPUT,
            self.USEREDIT_BIC_INPUT,
            self.USEREDIT_CREDITINSTITUTE_INPUT,
            self.USEREDIT_ACCOUNTOWNER_INPUT,
            *["-onetimefee_reason_{}-".format(i) for i in range(MAX_ONETIME_FEES)],
            *["-onetimefee_amount_{}-".format(i) for i in range(MAX_ONETIME_FEES)],
        ]:
            self.window[current].update(value="")
            set_validation_state(self.window[current], True)
            self.window[current].metadata = None

        for current in [
            self.USEREDIT_RELATIVES_LISTBOX,
            self.USEREDIT_LIKELYRELATIVES_LISTBOX,
            self.USEREDIT_POTENTIALRELATIVES_LISTBOX,
        ]:
            self.window[current].update(values=[])

        self.window[self.USEREDIT_HONORABLEMEMBER_CHECKBOX].update(value=False)
        self.window[self.USEREDIT_FEEOVERWRITE_CHECK].update(value=False)

        for i in range(
            self.window[self.USEREDITOR_SESSIONS_TAB].metadata["number_of_sessions"]
        ):
            self.window["-user_session_name_{}-".format(i)].update(
                visible=False, value=""
            )
            self.window["-user_session_name_{}-".format(i)].metadata = None
            self.window["-user_session_participant_{}-".format(i)].update(
                visible=False, value=False
            )
            self.window["-user_session_trainer_{}-".format(i)].update(
                visible=False, value=False
            )

        self.window[self.USEREDITOR_GENERAL_TAB].select()  # type: ignore

        if user is not None:
            # Populate general data
            self.window[self.USEREDIT_FIRSTNAME_INPUT].update(value=user.first_name)
            self.window[self.USEREDIT_LASTNAME_INPUT].update(value=user.last_name)
            self.window[self.USEREDIT_BIRTHDAY_INPUT].update(
                value=user.birthday.isoformat()
            )
            self.window[self.USEREDIT_STREET_INPUT].update(value=user.street)
            self.window[self.USEREDIT_STREETNUM_INPUT].update(value=user.street_number)
            self.window[self.USEREDIT_POSTALCODE_INPUT].update(value=user.postal_code)
            self.window[self.USEREDIT_CITY_INPUT].update(value=user.city)
            self.window[self.USEREDIT_PHONE_INPUT].update(
                value=user.phone_number if user.phone_number is not None else ""
            )
            self.window[self.USEREDIT_EMAIL_INPUT].update(
                value=user.email_address if user.email_address is not None else ""
            )
            self.window[self.USEREDIT_ENTRYDATE_INPUT].update(
                value=user.entry_date.isoformat()
            )
            self.window[self.USEREDIT_EXITDATE_INPUT].update(
                value=user.exit_date.isoformat() if user.exit_date is not None else ""
            )
            self.window[self.USEREDIT_HONORABLEMEMBER_CHECKBOX].update(
                value=user.is_honorary_member
            )

            # Populate payment data
            self.window[self.USEREDIT_HONORABLEMEMBER_CHECKBOX].update(
                value=user.is_honorary_member
            )
            if user.sepa_mandate_date is not None:
                self.window[self.USEREDIT_SEPAMANDATEDATE_INPUT].update(
                    value=user.sepa_mandate_date.isoformat()
                )
                self.set_value_and_fire_event(self.USEREDIT_IBAN_INPUT, user.iban)
                self.window[self.USEREDIT_BIC_INPUT].update(value=user.bic)
                self.window[self.USEREDIT_ACCOUNTOWNER_INPUT].update(
                    value=user.account_owner
                )

            fee_overwrite = self.session.scalar(
                select(FeeOverride).where(FeeOverride.member_id == user.id)
            )
            if fee_overwrite is not None:
                self.window[self.USEREDIT_FEEOVERWRITE_CHECK].update(value=True)
                self.window[self.USEREDIT_MONTHLYFEE_INPUT].update(
                    value="{:.2f}".format(fee_overwrite.amount)
                )
            else:
                self.window[self.USEREDIT_MONTHLYFEE_INPUT].update(
                    value="{:.2f}".format(
                        compute_monthly_fee(session=self.session, member=user)
                    )
                )

            onetime_fees = self.session.scalars(
                select(OneTimeFee).where(OneTimeFee.member_id == user.id)
            ).all()
            assert (
                len(onetime_fees) <= MAX_ONETIME_FEES
            ), "Amount of one-time fees ({}) exceeds assumed max. amount ({})".format(
                len(onetime_fees), MAX_ONETIME_FEES
            )
            for i, fee in enumerate(onetime_fees):
                self.window["-onetimefee_reason_{}-".format(i)].update(value=fee.reason)
                self.window["-onetimefee_amount_{}-".format(i)].update(
                    value="{:.2f}".format(fee.amount)
                )

            # Note: sessions are populated below by populate_user_sessions

            self.window[self.USEREDIT_TABGROUP].metadata = {"user": user}
            self.window[self.USEREDIT_DELETE_BUTTON].update(disabled=False)
        else:
            # Setup admission fee, if there is any
            admission_fee = self.session.scalar(
                select(FixedCost).where(FixedCost.name == AdmissionFeeKey)
            )
            if admission_fee is not None and admission_fee.cost != 0:
                self.window["-onetimefee_reason_0-"].update(value=_("Admission fee"))
                self.window["-onetimefee_amount_0-"].update(
                    value="{:.2f}".format(admission_fee.cost)
                )

            self.window[self.USEREDIT_TABGROUP].metadata = {}
            self.window[self.USEREDIT_DELETE_BUTTON].update(disabled=True)

            self.window[self.USEREDIT_MONTHLYFEE_INPUT].update(
                value=_("Save and re-load to compute fee")
            )

        self.populate_user_sessions(user)
        self.populate_user_relatives(user)

        self.window[self.USEREDITOR_COLUMN].update(visible=True)

    def populate_user_sessions(self, member: Optional[Member]):
        assert self.session is not None

        sessions = self.session.scalars(select(Session)).all()

        n_existing_rows: int = self.window[self.USEREDITOR_SESSIONS_TAB].metadata[
            "number_of_sessions"
        ]

        name_width: int = self.window[self.USEREDITOR_SESSIONS_TAB].metadata[
            "name_width"
        ]
        participant_width: int = self.window[self.USEREDITOR_SESSIONS_TAB].metadata[
            "participant_width"
        ]
        trainer_width: int = self.window[self.USEREDITOR_SESSIONS_TAB].metadata[
            "trainer_width"
        ]

        if len(sessions) > n_existing_rows:
            # Create missing rows
            for i in range(n_existing_rows, len(sessions)):
                self.window.extend_layout(
                    self.window[self.USEREDITOR_SESSIONS_TAB],
                    [
                        [
                            sg.Text(
                                text="",
                                size=(name_width, 1),
                                key="-user_session_name_{}-".format(i),
                            ),
                            sg.Checkbox(
                                text="",
                                size=(participant_width, 1),
                                key="-user_session_participant_{}-".format(i),
                            ),
                            sg.Checkbox(
                                text="",
                                size=(trainer_width, 1),
                                key="-user_session_trainer_{}-".format(i),
                            ),
                        ]
                    ],
                )
            self.window[self.USEREDITOR_SESSIONS_TAB].metadata[
                "number_of_sessions"
            ] = len(sessions)
            n_existing_rows = len(sessions)

        # Actually populate the rows with contents
        for i, current_session in enumerate(sessions):
            session_name = self.window["-user_session_name_{}-".format(i)]
            session_name.update(value=current_session.name, visible=True)
            session_name.metadata = {"session_id": current_session.id}
            member_takes_part_in_session = (
                current_session in member.participating_sessions
                if member is not None
                else False
            )
            self.window["-user_session_participant_{}-".format(i)].update(
                value=member_takes_part_in_session,
                visible=True,
            )
            self.window["-user_session_trainer_{}-".format(i)].update(
                value=current_session in member.trained_sessions
                if member is not None
                else False,
                visible=True,
            )

    def populate_user_relatives(self, user: Optional[Member]):
        assert self.session is not None
        # At this point we'll only populate the actual relatives and put everyone else
        # in the "potential relatives" box. The decision whether or not someone might be
        # a "likely relative" will be made once the relatives tab is opened
        if user is not None:
            relatives = get_relatives(session=self.session, member=user)
            self.window[self.USEREDIT_RELATIVES_LISTBOX].update(values=relatives)
        else:
            relatives = []

        members = self.session.scalars(select(Member).order_by(Member.last_name))
        members = [x for x in members if not x in relatives and not x == user]
        self.window[self.USEREDIT_POTENTIALRELATIVES_LISTBOX].update(values=members)

    def on_member_birthday_changed(self, values: Dict[Any, Any]):
        date = validate_date(self.window[self.USEREDIT_BIRTHDAY_INPUT])

        if date is not None:
            self.window[self.USEREDIT_AGE_LABEL].update(
                value=_("({:d} years)").format(
                    nominal_year_diff(date, datetime.datetime.now().date())
                )
            )

            if nominal_year_diff(date, datetime.datetime.now().date()) < 0:
                set_validation_state(self.window[self.USEREDIT_BIRTHDAY_INPUT], False)
        else:
            self.window[self.USEREDIT_AGE_LABEL].update(value="")

    def on_member_email_changed(self, values: Dict[Any, Any]):
        if values[self.USEREDIT_EMAIL_INPUT] == "":
            # Leaving this empty is allowed
            set_validation_state(self.window[self.USEREDIT_EMAIL_INPUT], True)
        else:
            validate_email(self.window[self.USEREDIT_EMAIL_INPUT])

    def on_member_entrydate_changed(self, values: Dict[Any, Any]):
        validate_date(self.window[self.USEREDIT_ENTRYDATE_INPUT])

    def on_member_exitdate_changed(self, values: Dict[Any, Any]):
        if values[self.USEREDIT_EXITDATE_INPUT] == "":
            # Leaving this empty is allowed
            set_validation_state(self.window[self.USEREDIT_EXITDATE_INPUT], True)
        else:
            validate_date(self.window[self.USEREDIT_EXITDATE_INPUT])

    def on_postal_code_changed(self, values: Dict[Any, Any]):
        global zip_code_locator

        code = validate_int(self.window[self.USEREDIT_POSTALCODE_INPUT])
        if not code is None:
            zip_code = zip_code_locator.query_postal_code(code)

            city = zip_code["place_name"]

            if type(city) == str:
                self.window[self.USEREDIT_CITY_INPUT].update(value=city, disabled=True)
            else:
                self.window[self.USEREDIT_CITY_INPUT].update(disabled=False)

    def on_member_sepa_mandate_date_changed(self, values: Dict[Any, Any]):
        if values[self.USEREDIT_SEPAMANDATEDATE_INPUT] == "":
            # Leaving this empty is allowed
            set_validation_state(self.window[self.USEREDIT_SEPAMANDATEDATE_INPUT], True)
        else:
            date = validate_date(self.window[self.USEREDIT_SEPAMANDATEDATE_INPUT])

            if date is not None and date > datetime.datetime.now().date():
                # Mandate date can't be in the future
                set_validation_state(
                    self.window[self.USEREDIT_SEPAMANDATEDATE_INPUT], False
                )

    def on_member_iban_changed(self, values: Dict[Any, Any]):
        if values[self.USEREDIT_IBAN_INPUT] == "":
            # Leaving this empty is allowed
            set_validation_state(self.window[self.USEREDIT_IBAN_INPUT], True)
            self.window[self.USEREDIT_BIC_INPUT].update(value="")
            self.window[self.USEREDIT_CREDITINSTITUTE_INPUT].update(value="")
        else:
            iban = validate_iban(self.window[self.USEREDIT_IBAN_INPUT])

            if not iban is None:
                if not iban.bic is None:
                    self.window[self.USEREDIT_BIC_INPUT].update(
                        value=iban.bic, disabled=True
                    )
                else:
                    self.window[self.USEREDIT_BIC_INPUT].update(
                        value="", disabled=False
                    )

                if iban.bank_name is not None:
                    self.window[self.USEREDIT_CREDITINSTITUTE_INPUT].update(
                        value=iban.bank_name
                    )
                else:
                    self.window[self.USEREDIT_CREDITINSTITUTE_INPUT].update(
                        value=_("Unknown")
                    )

    def on_member_monthly_fee_changed(self, values: Dict[Any, Any]):
        validate_amount(self.window[self.USEREDIT_MONTHLYFEE_INPUT])

    def on_member_fee_overwrite_changed(self, values: Dict[Any, Any]):
        if values[self.USEREDIT_FEEOVERWRITE_CHECK]:
            self.window[self.USEREDIT_MONTHLYFEE_INPUT].update(disabled=False)
        else:
            # TODO: Re-compute regular monthly fee and write that into the respective field
            self.window[self.USEREDIT_MONTHLYFEE_INPUT].update(disabled=True)
            self.window[self.USEREDIT_MONTHLYFEE_INPUT].update(
                value=_("Save and re-load to compute fee")
            )

    def on_onetimefee_changed(self, values: Dict[Any, Any]):
        for i in range(MAX_ONETIME_FEES):
            reason = self.window["-onetimefee_reason_{}-".format(i)]
            amount = self.window["-onetimefee_amount_{}-".format(i)]

            if reason.get().strip() != "":
                validate_non_empty(amount)
            if amount.get().strip() != "":
                validate_non_empty(reason)
                validate_amount(amount)

    def on_useredit_cancel_pressed(self, values: Dict[Any, Any]):
        self.window[self.USEREDITOR_COLUMN].update(visible=False)
        self.open_management()

    def validate_useredit_contents(self) -> Optional[str]:
        # Check presence of mandatory fields
        if self.window[self.USEREDIT_FIRSTNAME_INPUT].get().strip() == "":
            return _("Missing first name")
        elif self.window[self.USEREDIT_LASTNAME_INPUT].get().strip() == "":
            return _("Missing last name")
        elif self.window[self.USEREDIT_BIRTHDAY_INPUT].get().strip() == "":
            return _("Missing birthday")
        elif self.window[self.USEREDIT_STREET_INPUT].get().strip() == "":
            return _("Missing street")
        elif self.window[self.USEREDIT_STREETNUM_INPUT].get().strip() == "":
            return _("Missing street number")
        elif self.window[self.USEREDIT_POSTALCODE_INPUT].get().strip() == "":
            return _("Missing postal code")
        elif self.window[self.USEREDIT_CITY_INPUT].get().strip() == "":
            return _("Missing city")
        elif self.window[self.USEREDIT_ENTRYDATE_INPUT].get().strip() == "":
            return _("Missing entry date")

        if self.window[self.USEREDIT_SEPAMANDATEDATE_INPUT].get().strip() != "":
            if self.window[self.USEREDIT_IBAN_INPUT].get().strip() == "":
                return _("If a SEPA mandate is configured, an IBAN is required")
            elif self.window[self.USEREDIT_BIC_INPUT].get().strip() == "":
                return _("If a SEPA mandate is configured, the BIC is required")
            elif self.window[self.USEREDIT_ACCOUNTOWNER_INPUT].get().strip() == "":
                return _(
                    "If a SEPA mandate is configured, the account owner is required"
                )

        return None

    def on_useredit_save_pressed(self, values: Dict[Any, Any]):
        assert self.session is not None

        error_msg = self.validate_useredit_contents()
        if not error_msg is None:
            sg.popup_ok(
                _("Invalid member data: {}").format(error_msg), title=_("Invalid data")
            )
            return

        field_map = {
            "first_name": self.USEREDIT_FIRSTNAME_INPUT,
            "last_name": self.USEREDIT_LASTNAME_INPUT,
            "birthday": self.USEREDIT_BIRTHDAY_INPUT,
            "street": self.USEREDIT_STREET_INPUT,
            "street_number": self.USEREDIT_STREETNUM_INPUT,
            "postal_code": self.USEREDIT_POSTALCODE_INPUT,
            "city": self.USEREDIT_CITY_INPUT,
            "phone_number": self.USEREDIT_PHONE_INPUT,
            "email_address": self.USEREDIT_EMAIL_INPUT,
            "iban": self.USEREDIT_IBAN_INPUT,
            "bic": self.USEREDIT_BIC_INPUT,
            "account_owner": self.USEREDIT_ACCOUNTOWNER_INPUT,
            "sepa_mandate_date": self.USEREDIT_SEPAMANDATEDATE_INPUT,
            "entry_date": self.USEREDIT_ENTRYDATE_INPUT,
            "exit_date": self.USEREDIT_EXITDATE_INPUT,
            "is_honorary_member": self.USEREDIT_HONORABLEMEMBER_CHECKBOX,
        }

        value_map: Dict[str, Optional[Union[str, bool, datetime.date]]] = {}

        validated_fields = list(field_map.values())
        for i in range(MAX_ONETIME_FEES):
            validated_fields.append("-onetimefee_reason_{}-".format(i))
            validated_fields.append("-onetimefee_amount_{}-".format(i))

        for current in validated_fields:
            if type(self.window[current].metadata) == dict and not self.window[
                current
            ].metadata.get("valid", True):
                # This field has been considered invalid
                sg.popup_ok(_("There are fields with invalid data").format(current))
                return

        for current in field_map.keys():
            value: Optional[Union[str, bool, datetime.date]] = self.window[
                field_map[current]
            ].get()

            if type(value) == str:
                value = value.strip()

                if value == "":
                    value = None
                else:
                    if current.endswith("_date") or current == "birthday":
                        # Convert to date
                        value = datetime.datetime.fromisoformat(value).date()
                    elif current == "iban":
                        # While we want to display IBANs with spaces, we want to save them without
                        value = value.replace(" ", "")

            value_map[current] = value

        member: Optional[Member] = self.window[self.USEREDIT_TABGROUP].metadata.get(
            "user", None
        )

        if member is None:
            # Create a new member
            member = Member(**value_map)
            self.session.add(member)
        else:
            for current in value_map.keys():
                setattr(member, current, value_map[current])

        # Handle fee overrides
        self.session.execute(
            delete(FeeOverride).where(FeeOverride.member_id == member.id)
        )
        if self.window[self.USEREDIT_FEEOVERWRITE_CHECK].get():
            self.session.add(
                FeeOverride(
                    member_id=member.id,
                    amount=Decimal(
                        self.window[self.USEREDIT_MONTHLYFEE_INPUT].get().strip()
                    ),
                )
            )

        # Handle one-time fees
        self.session.execute(
            delete(OneTimeFee).where(OneTimeFee.member_id == member.id)
        )
        for i in range(MAX_ONETIME_FEES):
            reason = self.window["-onetimefee_reason_{}-".format(i)].get()
            amount = self.window["-onetimefee_amount_{}-".format(i)].get()

            if reason.strip() == "" or amount.strip() == "":
                continue

            amount = Decimal(amount)

            self.session.add(
                OneTimeFee(member_id=member.id, reason=reason, amount=amount)
            )

        # Handle relatives
        set_relatives(
            session=self.session,
            member=member,
            relatives=self.window[self.USEREDIT_RELATIVES_LISTBOX].get_list_values(),  # type: ignore
        )

        # Handle sessions
        sessions = self.session.scalars(select(Session)).all()
        participating_sessions = []
        trained_sessions = []
        for i in range(len(sessions)):
            if not self.window["-user_session_name_{}-".format(i)].visible:
                # As soon as we start seeing the first invisible session row, we have reached
                # the end of existing sessions
                break

            session_id: int = self.window["-user_session_name_{}-".format(i)].metadata[
                "session_id"
            ]
            takes_part = self.window["-user_session_participant_{}-".format(i)].get()
            trains = self.window["-user_session_trainer_{}-".format(i)].get()

            if takes_part:
                participating_sessions.append(session_id)
            if trains:
                trained_sessions.append(session_id)

        participating_sessions = [x for x in sessions if x.id in participating_sessions]
        trained_sessions = [x for x in sessions if x.id in trained_sessions]
        member.participating_sessions = participating_sessions
        member.trained_sessions = trained_sessions

        self.window[self.USEREDITOR_COLUMN].update(visible=False)
        self.open_management()

    def on_useredit_delete_pressed(self, values: Dict[Any, Any]):
        if "user" not in self.window[self.USEREDIT_TABGROUP].metadata:
            # This should not have happened -> treat it as a cancel event
            sg.popup_ok(_("No active user set - this should not have been possible"))
        else:
            user = self.window[self.USEREDIT_TABGROUP].metadata["user"]
            assert type(user) == Member
            assert self.session is not None

            result = sg.popup_yes_no(
                _('Are you sure you want to delete "{}"?').format(user)
            )
            # TODO: handle translation
            if not result == "Yes":
                return

            self.session.delete(user)

        self.window[self.USEREDITOR_COLUMN].update(visible=False)
        self.open_management()

    def on_useredit_relatives_tab_activated(self, values: Dict[Any, Any]):
        assert self.session is not None

        potential_relatives: List[Member] = self.window[
            self.USEREDIT_POTENTIALRELATIVES_LISTBOX
        ].get_list_values()  # type: ignore
        potential_relatives += self.window[
            self.USEREDIT_LIKELYRELATIVES_LISTBOX
        ].get_list_values()  # type: ignore
        likely_relatives: List[Member] = []

        current_city = self.window[self.USEREDIT_CITY_INPUT].get()
        current_street = self.window[self.USEREDIT_STREET_INPUT].get()
        current_streetnum = self.window[self.USEREDIT_STREETNUM_INPUT].get()
        current_iban = self.window[self.USEREDIT_IBAN_INPUT].get()

        for current_member in potential_relatives:
            if current_member.iban == current_iban or (
                current_member.city == current_city
                and current_member.street == current_street
                and current_member.street_number == current_streetnum
            ):
                # We consider people to likely be related if their fee is paid from the
                # same account or their address is the same
                likely_relatives.append(current_member)

                # Also add current_member's relatives as likely relatives
                for relative in get_relatives(self.session, current_member):
                    if relative in potential_relatives:
                        likely_relatives.append(relative)

        # Remove duplicates
        likely_relatives = list(set(likely_relatives))

        self.window[self.USEREDIT_LIKELYRELATIVES_LISTBOX].update(
            values=likely_relatives
        )
        self.window[self.USEREDIT_POTENTIALRELATIVES_LISTBOX].update(
            values=[x for x in potential_relatives if not x in likely_relatives]
        )

    def on_useredit_relatives_list_activated(self, values: Dict[Any, Any]):
        selection = self.window[self.USEREDIT_RELATIVES_LISTBOX].get()
        assert len(selection) in [0, 1]

        if len(selection) == 0:
            return

        selected_relative: Member = selection[0]  # type: ignore

        # Remove that entry from the list of relatives and clear selection
        relatives = self.window[self.USEREDIT_RELATIVES_LISTBOX].get_list_values()  # type: ignore
        relatives.remove(selected_relative)
        self.window[self.USEREDIT_RELATIVES_LISTBOX].update(values=relatives)
        self.window[self.USEREDIT_RELATIVES_LISTBOX].set_value([])  # type: ignore

        # Add it to the likely relatives instead
        likely_relatives = self.window[self.USEREDIT_LIKELYRELATIVES_LISTBOX].get_list_values()  # type: ignore
        likely_relatives.append(selected_relative)
        self.window[self.USEREDIT_LIKELYRELATIVES_LISTBOX].update(likely_relatives)

    def handle_add_relative(self, list_key: str):
        selection = self.window[list_key].get()
        assert len(selection) in [0, 1]

        if len(selection) == 0:
            return

        selected_member: Member = selection[0]  # type: ignore

        # Add it as a relative
        relatives = self.window[self.USEREDIT_RELATIVES_LISTBOX].get_list_values()  # type: ignore
        relatives.append(selected_member)
        self.window[self.USEREDIT_RELATIVES_LISTBOX].update(values=relatives)

        # Remove it from the original list and clear selection
        original = self.window[list_key].get_list_values()  # type: ignore
        original.remove(selected_member)
        self.window[list_key].update(values=original)
        self.window[list_key].set_value([])  # type: ignore

    def on_useredit_likelyrelatives_list_activated(self, values: Dict[Any, Any]):
        self.handle_add_relative(self.USEREDIT_LIKELYRELATIVES_LISTBOX)

    def on_useredit_potentialrelatives_list_activated(self, values: Dict[Any, Any]):
        self.handle_add_relative(self.USEREDIT_POTENTIALRELATIVES_LISTBOX)

    def create_sessioneditor(self):
        editor: Layout = [
            [
                sg.Column(
                    layout=[
                        [sg.Text(text=_("Name:"))],
                        [sg.Text(text=_("Membership fee:"))],
                    ]
                ),
                sg.Column(
                    layout=[
                        [sg.Input(key=self.SESSIONEDIT_NAME_INPUT, enable_events=True)],
                        [sg.Input(key=self.SESSIONEDIT_FEE_INPUT, enable_events=True)],
                    ]
                ),
            ],
            [sg.VPush()],
            [
                sg.Push(),
                sg.Button(button_text=_("Cancel"), key=self.SESSIONEDIT_CANCEL_BUTTON),
                sg.Button(button_text=_("Save"), key=self.SESSIONEDIT_SAVE_BUTTON),
                sg.Button(button_text=_("Delete"), key=self.SESSIONEDIT_DELETE_BUTTON),
            ],
        ]

        self.connect(self.SESSIONEDIT_NAME_INPUT, self.on_sessionedit_name_changed)
        self.connect(self.SESSIONEDIT_FEE_INPUT, self.on_sessionedit_fee_changed)
        self.connect(self.SESSIONEDIT_CANCEL_BUTTON, self.on_sessionedit_cancel_pressed)
        self.connect(self.SESSIONEDIT_SAVE_BUTTON, self.on_sessionedit_save_pressed)
        self.connect(self.SESSIONEDIT_DELETE_BUTTON, self.on_sessionedit_delete_pressed)

        self.layout[0].append(
            sg.Column(
                layout=editor,
                visible=False,
                key=self.SESSIONEDIT_COLUMN,
                expand_x=True,
                expand_y=True,
                metadata={},
            )
        )

    def open_sessioneditor(self, session: Optional[Session] = None):
        # Clear fields
        for field in [self.SESSIONEDIT_NAME_INPUT, self.SESSIONEDIT_FEE_INPUT]:
            self.window[field].update(value="")

        self.window[self.SESSIONEDIT_COLUMN].metadata["session"] = None

        if not session is None:
            self.window[self.SESSIONEDIT_NAME_INPUT].update(value=session.name)
            self.window[self.SESSIONEDIT_FEE_INPUT].update(
                value="{:.2f}".format(session.membership_fee)
            )

            self.window[self.SESSIONEDIT_COLUMN].metadata["session"] = session

        self.window[self.SESSIONEDIT_DELETE_BUTTON].update(disabled=session is None)

        self.window[self.SESSIONEDIT_COLUMN].update(visible=True)

    def on_sessionedit_name_changed(self, values: Dict[Any, Any]):
        validate_non_empty(self.window[self.SESSIONEDIT_NAME_INPUT], strip=False)

    def on_sessionedit_fee_changed(self, values: Dict[Any, Any]):
        validate_amount(self.window[self.SESSIONEDIT_FEE_INPUT])

    def on_sessionedit_cancel_pressed(self, values: Dict[Any, Any]):
        self.window[self.SESSIONEDIT_COLUMN].update(visible=False)
        self.open_management()

    def validate_sessionedit_contents(self):
        # Check presence of mandatory data
        if self.window[self.SESSIONEDIT_NAME_INPUT].get().strip() == "":
            return _("Missing session name")
        elif self.window[self.SESSIONEDIT_FEE_INPUT].get().strip() == "":
            return _("Missing session fee")

    def on_sessionedit_save_pressed(self, values: Dict[Any, Any]):
        assert self.session is not None

        error_msg = self.validate_sessionedit_contents()
        if not error_msg is None:
            sg.popup_ok(
                _("Invalid session data: {}").format(error_msg), title=_("Invalid data")
            )
            return

        field_map: Dict[str, Any] = {
            "name": self.SESSIONEDIT_NAME_INPUT,
            "membership_fee": self.SESSIONEDIT_FEE_INPUT,
        }

        validated_fields = list(field_map.values())
        for current in validated_fields:
            if type(self.window[current].metadata) == dict and not self.window[
                current
            ].metadata.get("valid", True):
                # This field has been considered invalid
                sg.popup_ok(_("There are fields with invalid data").format(current))
                return

        for current in field_map.keys():
            if current.endswith("_fee"):
                field_map[current] = Decimal(self.window[field_map[current]].get())
            else:
                field_map[current] = self.window[field_map[current]].get().strip()

        session: Optional[Session] = self.window[self.SESSIONEDIT_COLUMN].metadata.get(
            "session", None
        )

        if session is None:
            # Create a new session
            session = Session(**field_map)
            self.session.add(session)
        else:
            for current in field_map.keys():
                setattr(session, current, field_map[current])

        self.window[self.SESSIONEDIT_COLUMN].update(visible=False)
        self.open_management()

    def on_sessionedit_delete_pressed(self, values: Dict[Any, Any]):
        if "session" not in self.window[self.SESSIONEDIT_COLUMN].metadata:
            # This should not have happened -> treat it as a cancel event
            sg.popup_ok(_("No active session set - this should not have been possible"))
        else:
            session = self.window[self.SESSIONEDIT_COLUMN].metadata["session"]
            assert type(session) == Session
            assert self.session is not None

            result = sg.popup_yes_no(
                _('Are you sure you want to delete "{}"?').format(session)
            )
            # TODO: handle translation
            if not result == "Yes":
                return

            self.session.delete(session)

        self.window[self.SESSIONEDIT_COLUMN].update(visible=False)
        self.open_management()

    def show_and_execute(self):
        self.window: sg.Window = sg.Window(
            _("Memmer"),
            self.layout,
            resizable=True,
            finalize=True,
        )

        self.open_connector()

        while True:
            event, values = self.window.read()  # type: ignore

            if event in [sg.WIN_CLOSED]:
                self.prompted_commit()
                break

            if event in self.event_processors:
                for current in self.event_processors[event]:
                    current(values)

            selected_element = self.window.Find(event, silent_on_error=True)
            if selected_element is not None and type(selected_element) is sg.TabGroup:
                selected_tab: str = selected_element.get()  # type: ignore

                if selected_tab in self.event_processors:
                    for current in self.event_processors[selected_tab]:
                        current(values)

            print("Event: ", event)

        self.window.close()

        if not self.ssh_tunnel is None:
            self.ssh_tunnel.stop()

        if not self.config is None:
            # Write config to disk
            try:
                global config_path
                json.dump(self.config, open(config_path, "w"))
            except:
                print("Failed to persist config")
