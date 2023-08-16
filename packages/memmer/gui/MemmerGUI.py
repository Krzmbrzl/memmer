# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Dict, Any, Optional

from gettext import gettext as _

import PySimpleGUI as sg

from memmer.gui import Layout
from memmer.orm import Member

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, URL


class MemmerGUI:
    CONNECTOR_DBBACKEND_COMBO: str = "-CONNCETOR_DBBACKEND_COMBO-"
    CONNECTOR_CONNECT_BUTTON: str = "-CONNECTOR_CONNECT_EVENT-"
    CONNECTOR_HOST_FIELD: str = "-CONNECTOR_HOST_INPUT-"
    CONNECTOR_USER_FIELD: str = "-CONNECTOR_USER_INPUT-"
    CONNECTOR_PORT_FIELD: str = "-CONNECTOR_PORT_INPUT-"
    CONNECTOR_DBNAME_FIELD: str = "-CONNECTOR_DBNAME_INPUT-"
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
    USEREDIT_ACCOUNTOWNER_INPUT: str = "-USEREDIT_ACCOUNTOWNER_INPUT-"
    USEREDIT_SEPAMANDATEDATE_INPUT: str = "-USEREDIT_SEPAMANDATEDATE_INPUT-"
    USEREDIT_MONTHLYFEE_INPUT: str = "-USEREDIT_MONTHLYFEE_INPUT-"
    USEREDIT_FEEOVERWRITE_CHECK: str = "-USEREDIT_FEEOVERWRITE_CHECK-"
    USEREDITOR_COLUMN: str = "-USEREDITOR_COLUMN-"

    def __init__(self):
        self.layout: Layout = [[]]
        self.create_connector()
        self.create_overview()
        self.create_management()
        self.create_usereditor()

    def create_connector(self):
        labels: Layout = [
            [sg.Text(_("Backend:"))],
            [sg.Text(_("User:"))],
            [sg.Text(_("Host:"))],
            [sg.Text(_("Port:"))],
            [sg.Text(_("Database:"))],
        ]

        inputs: Layout = [
            [
                sg.Combo(
                    values=["PostgreSQL", "MySQL", "SQLite"],
                    default_value="PostgreSQL",
                    enable_events=True,
                    readonly=True,
                    key=self.CONNECTOR_DBBACKEND_COMBO,
                )
            ],
            [sg.Input(key=self.CONNECTOR_USER_FIELD)],
            [sg.Input(key=self.CONNECTOR_HOST_FIELD)],
            [sg.Input(key=self.CONNECTOR_PORT_FIELD)],
            [sg.Input(key=self.CONNECTOR_DBNAME_FIELD)],
        ]

        connector_layout: Layout = [
            [sg.Column(layout=labels), sg.Column(layout=inputs)],
            [sg.Button(button_text=_("Connect"), key=self.CONNECTOR_CONNECT_BUTTON)],
        ]

        self.layout[0].append(
            sg.Column(
                layout=connector_layout,
                visible=True,
                key=self.CONNECTOR_COLUMN,
                expand_x=True,
                expand_y=True,
            )
        )

    def on_db_backend_changed(self, values: Dict[Any, Any]):
        selected_backend = values[self.CONNECTOR_DBBACKEND_COMBO]

        remote_options_disabled = selected_backend == "SQLite"

        self.window[self.CONNECTOR_HOST_FIELD].update(disabled=remote_options_disabled)
        self.window[self.CONNECTOR_PORT_FIELD].update(disabled=remote_options_disabled)
        self.window[self.CONNECTOR_USER_FIELD].update(disabled=remote_options_disabled)

    def on_connect_button_pressed(self, values: Dict[Any, Any]):
        if values[self.CONNECTOR_DBBACKEND_COMBO] == "SQLite":
            backend = "sqlite"

            if values[self.CONNECTOR_DBNAME_FIELD] == "":
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

        try:
            connect_url = URL.create(
                drivername=backend,
                username=values[self.CONNECTOR_USER_FIELD]
                if backend != "sqlite"
                else None,
                port=values[self.CONNECTOR_PORT_FIELD] if backend != "sqlite" else None,
                host=values[self.CONNECTOR_HOST_FIELD] if backend != "sqlite" else None,
                database=values[self.CONNECTOR_DBNAME_FIELD],
            )
            engine = create_engine(connect_url)

            self.Session = sessionmaker(bind=engine)

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

        # TODO: Create list of members and put them into the listbox
        self.window[self.MANAGEMENT_MEMBER_LISTBOX].update(
            values=["Test Arthuis", "Jemma Tellar"]
        )

        # TODO: Create list of sessions and put them to the listbox

        # TODO: Store full list of entries in metadata variable on listbox

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
                            sg.Input(key=self.USEREDIT_BIRTHDAY_INPUT),
                            sg.Text(text="(3 years)", key=self.USEREDIT_AGE_LABEL),
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
                        [sg.Input(key=self.USEREDIT_POSTALCODE_INPUT)],
                        [sg.Input(key=self.USEREDIT_CITY_INPUT)],
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
                        [sg.Input(key=self.USEREDIT_EMAIL_INPUT)],
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
                        [sg.Input(key=self.USEREDIT_ENTRYDATE_INPUT)],
                        [sg.Input(key=self.USEREDIT_EXITDATE_INPUT)],
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
                        [sg.Text(_("Account owner:"))],
                    ]
                ),
                sg.Column(
                    layout=[
                        [sg.Input(key=self.USEREDIT_SEPAMANDATEDATE_INPUT)],
                        [sg.Input(key=self.USEREDIT_IBAN_INPUT)],
                        [sg.Input(key=self.USEREDIT_BIC_INPUT)],
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
                    ]
                ),
                sg.Column(
                    layout=[
                        [
                            sg.Input(disabled=True, key=self.USEREDIT_MONTHLYFEE_INPUT),
                            sg.Checkbox(
                                text=_("Overwrite"),
                                default=False,
                                key=self.USEREDIT_FEEOVERWRITE_CHECK,
                            ),
                        ],
                        [sg.Button(button_text=_("Add"))],
                    ]
                ),
            ],
        ]

        payment_tab: Layout = [
            [sg.Frame(title=_("Bank details"), layout=bank_details, expand_x=True)],
            [sg.HorizontalSeparator()],
            [sg.Frame(title=_("Fees"), layout=fees, expand_x=True)],
        ]

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
                    ]
                ),
            ],
            [
                sg.Button(button_text=_("Cancel")),
                sg.Button(button_text=_("Save")),
                sg.Button(button_text=_("Delete")),
            ],
        ]

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
        if user is not None:
            # TODO: Populate fields with user's data
            pass
        else:
            # TODO: Clear all fields
            pass

        self.window[self.USEREDITOR_COLUMN].update(visible=True)

    def show_and_execute(self):
        self.window: sg.Window = sg.Window(
            _("Memmer"), self.layout, resizable=True, finalize=True
        )

        while True:
            event, values = self.window.read()  # type: ignore

            if event in [sg.WIN_CLOSED]:
                break

            if event == self.CONNECTOR_CONNECT_BUTTON:
                self.on_connect_button_pressed(values)
            elif event == self.CONNECTOR_DBBACKEND_COMBO:
                self.on_db_backend_changed(values)
            elif event == self.OVERVIEW_MANAGEMENT_BUTTON:
                self.on_management_button_pressed(values)
            elif event == self.OVERVIEW_TALLY_BUTTON:
                self.on_tally_button_pressed(values)
            elif event == self.MANAGEMENT_ADDMEMBER_BUTTON:
                self.on_addmember_button_pressed(values)

            print("Event: ", event)

        self.window.close()
