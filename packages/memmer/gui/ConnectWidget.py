# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_ConnectWidget import Ui_ConnectWidget

from typing import Optional
import os

from PySide6.QtWidgets import QMessageBox, QLineEdit
from PySide6.QtCore import Signal, Qt

from memmer.utils import (
    DBBackend,
    ConnectType,
    ConnectionParameter,
    SSHTunnelParameter,
    connect,
)
from memmer.gui import MemmerWidget, FormValidator, Issue, error, warning

from sqlalchemy.orm import Session

from sshtunnel import SSHTunnelForwarder


def db_backend_idx_to_type(idx: int) -> DBBackend:
    if idx == 0:
        return DBBackend.SQLite
    elif idx == 1:
        return DBBackend.PostgreSQL
    elif idx == 2:
        return DBBackend.MySQL

    raise RuntimeError(f"Unknown DB backend index '{idx}'")


def db_backend_to_idx(backend: DBBackend) -> int:
    if backend == DBBackend.SQLite:
        return 0
    elif backend == DBBackend.PostgreSQL:
        return 1
    elif backend == DBBackend.MySQL:
        return 2

    raise RuntimeError(f"Unknown DB backend '{backend}'")


def connect_idx_to_type(idx: int) -> ConnectType:
    if idx == 0:
        return ConnectType.REGULAR
    elif idx == 1:
        return ConnectType.SSH_TUNNEL

    raise RuntimeError(f"Unknown connect type index '{idx}'")


def connect_type_to_index(connect_type: ConnectType) -> int:
    if connect_type == ConnectType.REGULAR:
        return 0
    elif connect_type == ConnectType.SSH_TUNNEL:
        return 1

    raise RuntimeError(f"Unknown connect type '{connect_type}'")


class ConnectWidget(MemmerWidget, Ui_ConnectWidget):
    connected = Signal(Session, SSHTunnelForwarder)

    @property
    def connection_parameter(self) -> ConnectionParameter:
        params = ConnectionParameter(
            db_backend_idx_to_type(self.db_backend_combo.currentIndex()),
            database=self.db_name_input.text().strip(),
        )

        if params.db_backend != DBBackend.SQLite:
            if self.db_host_input.text().strip():
                params.address = self.db_host_input.text().strip()
            if self.db_port_spinner.value() > 0:
                params.port = self.db_port_spinner.value()

        if self.db_user_input.text().strip():
            params.user = self.db_user_input.text().strip()

        if self.db_password_edit.text().strip():
            params.password = self.db_password_edit.text().strip()

        if (
            connect_idx_to_type(self.connection_type_combo.currentIndex())
            == ConnectType.SSH_TUNNEL
        ):
            params.ssh_tunnel = SSHTunnelParameter(
                address=self.ssh_host_input.text().strip(),
                user=self.ssh_user_input.text().strip(),
            )

            if self.ssh_port_spinner.value() > 0:
                params.ssh_tunnel.port = self.ssh_port_spinner.value()

            if self.db_port_spinner.value() > 0:
                params.ssh_tunnel.remote_port = self.db_port_spinner.value()

            if self.db_host_input.text().strip():
                params.ssh_tunnel.remote_address = self.db_host_input.text().strip()

            if self.ssh_authentication_combo.currentIndex() == 0:
                params.ssh_tunnel.password = self.ssh_password_input.text()
            elif self.ssh_authentication_combo.currentIndex() == 1:
                params.ssh_tunnel.key = self.ssh_key_input.path
            elif self.ssh_authentication_combo.currentIndex() == 2:
                params.ssh_tunnel.use_agent = True

        return params

    @connection_parameter.setter
    def connection_parameter(self, params: ConnectionParameter):
        self.connection_type_combo.setCurrentIndex(
            connect_type_to_index(
                ConnectType.SSH_TUNNEL if params.ssh_tunnel else ConnectType.REGULAR
            )
        )

        self.db_backend_combo.setCurrentIndex(db_backend_to_idx(params.db_backend))

        self.db_name_input.setText(params.database)

        if params.address:
            self.db_host_input.setText(params.address)
        else:
            self.db_host_input.clear()

        if params.port:
            self.db_port_spinner.setValue(params.port)
        else:
            self.db_port_spinner.setValue(0)

        if params.user:
            self.db_user_input.setText(params.user)
        else:
            self.db_user_input.clear()

        if params.password:
            self.db_password_edit.setText(params.password)
        else:
            self.db_password_edit.clear()

        if params.ssh_tunnel:
            self.ssh_host_input.setText(params.ssh_tunnel.address)

            self.ssh_user_input.setText(params.ssh_tunnel.user)

            self.ssh_port_spinner.setValue(params.ssh_tunnel.port)

            if params.ssh_tunnel.password:
                self.ssh_password_input.setText(params.ssh_tunnel.password)
                self.ssh_authentication_combo.setCurrentIndex(0)
            else:
                self.ssh_password_input.clear()

            if params.ssh_tunnel.key:
                self.ssh_key_input.path = params.ssh_tunnel.key
                self.ssh_authentication_combo.setCurrentIndex(1)
            else:
                self.ssh_key_input.clear()

            if params.ssh_tunnel.use_agent:
                self.ssh_authentication_combo.setCurrentIndex(2)

            if params.ssh_tunnel.remote_address:
                self.db_host_input.setText(params.ssh_tunnel.remote_address)

            if params.ssh_tunnel.remote_port:
                self.db_port_spinner.setValue(params.ssh_tunnel.remote_port)
        else:
            self.ssh_host_input.clear()
            self.ssh_user_input.clear()
            self.ssh_port_spinner.setValue(0)
            self.ssh_password_input.clear()
            self.ssh_key_input.clear()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.ssh_authentication_combo.setItemData(
            0, self.tr("Use a regular password"), Qt.ItemDataRole.ToolTipRole
        )
        self.ssh_authentication_combo.setItemData(
            1,
            self.tr("Use a provided SSH certificate/key"),
            Qt.ItemDataRole.ToolTipRole,
        )
        self.ssh_authentication_combo.setItemData(
            2,
            self.tr("Use an SSH-agent to obtain a certificate/key"),
            Qt.ItemDataRole.ToolTipRole,
        )

        self.__connect_signals()

        self.__init_state()

        self.__setup_validation()

    def __connect_signals(self):
        self.connection_type_combo.currentIndexChanged.connect(
            self.__connect_type_changed
        )

        self.db_backend_combo.currentIndexChanged.connect(self.__db_backend_changed)

        self.ssh_authentication_combo.currentIndexChanged.connect(
            self.__ssh_authentication_changed
        )

        self.connect_button.clicked.connect(self.__connect)

    def __init_state(self):
        self.__connect_type_changed(self.connection_type_combo.currentIndex())

        self.__db_backend_changed(self.db_backend_combo.currentIndex())

        self.__ssh_authentication_changed(self.ssh_authentication_combo.currentIndex())

        # Problems are reported when trying to connect
        self.connect_button.setEnabled(True)

    def __setup_validation(self):
        self.validator = FormValidator(self, self.connect_button)
        add = self.validator.add_check

        connect_type_changed = self.connection_type_combo.currentIndexChanged
        auth_changed = self.ssh_authentication_combo.currentIndexChanged

        add(
            self.__check_db_name,
            [self.db_name_input],
            triggers=[connect_type_changed, self.db_backend_combo.currentIndexChanged],
        )
        add(
            lambda: self.__check_ssh_required(
                self.ssh_host_input, self.tr("Please enter the SSH host")
            ),
            [self.ssh_host_input],
            triggers=[connect_type_changed],
        )
        add(
            lambda: self.__check_ssh_required(
                self.ssh_user_input, self.tr("Please enter the SSH user")
            ),
            [self.ssh_user_input],
            triggers=[connect_type_changed],
        )
        add(
            self.__check_ssh_password,
            [self.ssh_password_input],
            triggers=[connect_type_changed, auth_changed],
        )
        add(
            self.__check_ssh_key,
            [self.ssh_key_input],
            triggers=[connect_type_changed, auth_changed],
        )
        add(
            self.__check_ssh_agent,
            [self.ssh_authentication_combo],
            triggers=[connect_type_changed],
        )

    def __uses_ssh(self) -> bool:
        return (
            connect_idx_to_type(self.connection_type_combo.currentIndex())
            == ConnectType.SSH_TUNNEL
        )

    def __check_db_name(self) -> Optional[Issue]:
        name = self.db_name_input.text().strip()
        if len(name) == 0:
            return error(self.tr("Please enter the database"))

        backend = db_backend_idx_to_type(self.db_backend_combo.currentIndex())
        if (
            backend == DBBackend.SQLite
            and not self.__uses_ssh()
            and not os.path.isfile(os.path.expanduser(name))
        ):
            # SQLite would silently create a new, empty database
            return error(self.tr("There is no SQLite database at this path"))
        return None

    def __check_ssh_required(self, edit: QLineEdit, message: str) -> Optional[Issue]:
        if self.__uses_ssh() and len(edit.text().strip()) == 0:
            return error(message)
        return None

    def __check_ssh_password(self) -> Optional[Issue]:
        if (
            self.__uses_ssh()
            and self.ssh_authentication_combo.currentIndex() == 0
            and len(self.ssh_password_input.text()) == 0
        ):
            return error(self.tr("Please enter the SSH password"))
        return None

    def __check_ssh_key(self) -> Optional[Issue]:
        if not self.__uses_ssh() or self.ssh_authentication_combo.currentIndex() != 1:
            return None

        path = os.path.expanduser(self.ssh_key_input.path.strip())
        if len(path) == 0:
            return error(self.tr("Please choose the private key file"))
        if not os.path.isfile(path):
            return error(self.tr("This file doesn't exist"))
        if not os.access(path, os.R_OK):
            return error(self.tr("You don't have permission to read this file"))
        return None

    def __check_ssh_agent(self) -> Optional[Issue]:
        if (
            self.__uses_ssh()
            and self.ssh_authentication_combo.currentIndex() == 2
            and not os.environ.get("SSH_AUTH_SOCK")
        ):
            return warning(
                self.tr("No running SSH agent found (SSH_AUTH_SOCK is not set)")
            )
        return None

    def __connect_type_changed(self, type_idx: int):
        connect_type = connect_idx_to_type(idx=type_idx)

        self.ssh_group.setVisible(connect_type == ConnectType.SSH_TUNNEL)

    def __db_backend_changed(self, backend_idx: int):
        backend = db_backend_idx_to_type(idx=backend_idx)

        # Disable options that aren't applicable for SQLite
        self.db_host_label.setVisible(backend != DBBackend.SQLite)
        self.db_host_input.setVisible(backend != DBBackend.SQLite)
        self.db_port_label.setVisible(backend != DBBackend.SQLite)
        self.db_port_spinner.setVisible(backend != DBBackend.SQLite)

    def __ssh_authentication_changed(self, auth_idx):
        show_password = False
        show_cert = False

        if auth_idx == 0:
            # Password
            show_password = True
        elif auth_idx == 1:
            # Certificate
            show_cert = True
        elif auth_idx == 2:
            # SSH agent
            pass

        self.ssh_password_label.setVisible(show_password)
        self.ssh_password_input.setVisible(show_password)
        self.ssh_key_label.setVisible(show_cert)
        self.ssh_key_input.setVisible(show_cert)

    def __connect(self):
        if not self.validator.validate():
            return

        self.status_changed.emit(self.tr("Connecting…"))

        def perform_connection():
            try:
                session, ssh_tunnel = connect(
                    params=self.connection_parameter, enable_sql_echo=False
                )

                self.connected.emit(session, ssh_tunnel)
            except Exception as error:
                self.status_changed.emit(self.tr("Connection failed"))

                def show_error_msg(err=error):
                    QMessageBox.critical(
                        self,
                        self.tr("Connection failed"),
                        self.tr(
                            "Establishing the connection to the database has failed. Reason given:\n{error}"
                        ).format(error=err),
                        buttons=QMessageBox.StandardButton.Ok,
                    )

                self.run_in_gui_thread(show_error_msg)

        self.async_exec(perform_connection)
