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

import PySimpleGUI as sg

import pgeocode

from schwifty import IBAN
from schwifty.exceptions import SchwiftyException

from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError

from memmer.gui import Layout
from memmer.orm import Member, Session, OneTimeFee, FeeOverride
from memmer.utils import nominal_year_diff

from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import create_engine, URL, select, delete, event

zip_code_locator = pgeocode.Nominatim(country="de")


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
    CONNECTOR_SSHUSER_INPUT: str = "-CONNECTOR_SSHUSER_INPUT_"
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
    USEREDITOR_COLUMN: str = "-USEREDITOR_COLUMN-"

    def __init__(self):
        self.layout: Layout = [[]]
        self.event_processors: Dict[str, List[Callable[[Dict[Any, Any]], Any]]] = {}
        self.ssh_tunnel: Optional[SSHTunnelForwarder] = None
        self.session: Optional[SQLSession] = None

        self.create_connector()
        self.create_overview()
        self.create_management()
        self.create_usereditor()

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
            [sg.Input(key=self.CONNECTOR_PASSWORD_INPUT)],
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
            [sg.Input(key=self.CONNECTOR_SSHPASSWORD_INPUT)],
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
                visible=True,
                key=self.CONNECTOR_COLUMN,
                expand_x=True,
                expand_y=True,
            )
        )

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
                        int(values[self.CONNECTOR_PORT_INPUT]),
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
        sg.popup_ok(_("Not yet implemented"))

    def create_management(self):
        user_management: Layout = [
            [sg.Button(_("Add member"), key=self.MANAGEMENT_ADDMEMBER_BUTTON)],
            [sg.HorizontalSeparator()],
            [sg.Text(_("Search:")), sg.Input(key=self.MANAGEMENT_MEMBERSEARCH_INPUT)],
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
            [sg.Text(_("Search:")), sg.Input(key=self.MANAGEMENT_SESSIONSEARCH_INPUT)],
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

        self.connect(self.MANAGEMENT_ADDMEMBER_BUTTON, self.on_addmember_button_pressed)

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

        members = self.session.scalars(select(Member)).all()

        self.window[self.MANAGEMENT_MEMBER_LISTBOX].update(
            values=[
                "{}, {}".format(current.first_name, current.last_name)
                for current in members
            ]
        )
        self.window[self.MANAGEMENT_MEMBER_LISTBOX].metadata = members

        sessions = self.session.scalars(select(Session)).all()

        self.window[self.MANAGEMENT_SESSION_LISTBOX].update(
            values=[current.name for current in sessions]
        )
        self.window[self.MANAGEMENT_SESSION_LISTBOX].metadata = sessions

    def on_addmember_button_pressed(self, values: Dict[Any, Any]):
        self.window[self.MANAGEMENT_COLUMN].update(visible=False)
        self.open_usereditor()

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

        sessions_tab: Layout = [[]]

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
                            ),
                        ]
                    ],
                    key=self.USEREDIT_TABGROUP,
                    expand_x=True,
                    expand_y=True,
                ),
            ],
            [
                sg.Push(),
                sg.Button(button_text=_("Cancel"), key=self.USEREDIT_CANCEL_BUTTON),
                sg.Button(button_text=_("Save"), key=self.USEREDIT_SAVE_BUTTON),
                sg.Button(button_text=_("Delete"), key=self.USEREDIT_DELETE_BUTTON),
            ],
        ]

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
        # Clear elements
        for current in [
            self.USEREDIT_FIRSTNAME_INPUT,
            self.USEREDIT_LASTNAME_INPUT,
            self.USEREDIT_BIRTHDAY_INPUT,
            self.USEREDIT_STREET_INPUT,
            self.USEREDIT_STREETNUM_INPUT,
            self.USEREDIT_CITY_INPUT,
            self.USEREDIT_PHONE_INPUT,
            self.USEREDIT_EMAIL_INPUT,
            self.USEREDIT_ENTRYDATE_INPUT,
            self.USEREDIT_EXITDATE_INPUT,
            self.USEREDIT_SEPAMANDATEDATE_INPUT,
            self.USEREDIT_IBAN_INPUT,
            self.USEREDIT_CREDITINSTITUTE_INPUT,
            self.USEREDIT_ACCOUNTOWNER_INPUT,
            *["-onetimefee_reason_{}-".format(i) for i in range(MAX_ONETIME_FEES)],
            *["-onetimefee_amount_{}-".format(i) for i in range(MAX_ONETIME_FEES)],
        ]:
            self.window[current].update(value="")
            set_validation_state(self.window[current], True)
            self.window[current].metadata = None

        self.window[self.USEREDIT_HONORABLEMEMBER_CHECKBOX].update(value=False)
        self.window[self.USEREDIT_FEEOVERWRITE_CHECK].update(value=False)

        self.window[self.USEREDITOR_GENERAL_TAB].select()  # type: ignore

        if user is not None:
            # TODO: Populate fields with user's data
            self.window[self.USEREDIT_TABGROUP].metadata = user
            self.window[self.USEREDIT_DELETE_BUTTON].update(disabled=False)
        else:
            # TODO: Setup admission fee
            self.window[self.USEREDIT_TABGROUP].metadata = None
            self.window[self.USEREDIT_DELETE_BUTTON].update(disabled=True)

        # TODO: Set calculated monthly fee for this member

        self.window[self.USEREDITOR_COLUMN].update(visible=True)

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
            if type(
                self.window[field_map[current]].metadata
            ) == dict and not self.window[field_map[current]].metadata.get(
                "valid", True
            ):
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

            value_map[current] = value

        member: Optional[Member] = self.window[self.USEREDIT_TABGROUP].metadata

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

        # TODO: Handle sessions

        self.window[self.USEREDITOR_COLUMN].update(visible=False)
        self.open_management()

    def on_useredit_delete_pressed(self, values: Dict[Any, Any]):
        if self.window[self.USEREDIT_TABGROUP].metadata is None:
            # This should not have happened -> treat it as a cancel event
            sg.popup_ok(_("No active user set - this should not have been possible"))
        else:
            result = sg.popup_yes_no(_("Are you sure you want to delete this user?"))
            # TODO: handle translation
            if not result == "Yes":
                return

            user = self.window[self.USEREDIT_TABGROUP].metadata
            assert type(user) == Member
            assert self.session is not None

            self.session.execute(delete(Member).where(Member.id == user.id))

        self.window[self.USEREDITOR_COLUMN].update(visible=False)
        self.open_management()

    def show_and_execute(self):
        self.window: sg.Window = sg.Window(
            _("Memmer"),
            self.layout,
            resizable=True,
            finalize=True,
        )

        while True:
            event, values = self.window.read()  # type: ignore

            if event in [sg.WIN_CLOSED]:
                self.prompted_commit()
                break

            if event in self.event_processors:
                for current in self.event_processors[event]:
                    current(values)

            print("Event: ", event)

        self.window.close()

        if not self.ssh_tunnel is None:
            self.ssh_tunnel.stop()
