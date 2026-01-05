# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_MainWindow import Ui_MainWindow

from typing import Optional, Set

from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import QThreadPool, Signal

from sqlalchemy import orm

from sshtunnel import SSHTunnelForwarder

from memmer.orm import Member, Session
from memmer.utils import (
    load_config,
    save_config,
    has_uncommitted_changes,
    MemmerConfig,
    ConnectionParameter,
    DataManager,
)
from memmer.gui import MemmerWidget, MemberDialog, SessionDialog


class MainWindow(QMainWindow, Ui_MainWindow):
    session_about_to_be_deleted = Signal(Session)
    session_deleted = Signal(Session)
    session_created = Signal(Session)
    session_changed = Signal(Session)
    member_deleted = Signal(Member)
    member_about_to_be_deleted = Signal(Member)
    member_created = Signal(Member)
    member_changed = Signal(Member)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.ssh_tunnel: Optional[SSHTunnelForwarder] = None
        self.session: Optional[orm.Session] = None
        self.config: MemmerConfig = load_config()
        self.thread_pool = QThreadPool(self)
        self.data_manager = None
        self.__opened_widgets: Set[MemmerWidget] = set()

        self.__connect_signals()

        self.__init_state()

    def __connect_signals(self):
        self.statusbar.messageChanged.connect(self.__status_update)

        self.connect_page.connected.connect(self.__connection_established)
        self.connect_page.status_changed.connect(self.__status_update)

        self.main_menu.disconnect_requested.connect(self.__disconnect)
        self.main_menu.status_changed.connect(self.__status_update)
        self.main_menu.overview_page_requested.connect(
            lambda: self.__switch_to(self.overview_page)
        )
        self.main_menu.tally_page_requested.connect(
            lambda: self.__switch_to(self.tally_page)
        )

        self.tally_page.main_menu_requested.connect(
            lambda: self.__switch_to(self.main_menu)
        )

        self.overview_page.main_menu_requested.connect(
            lambda: self.__switch_to(self.main_menu)
        )

        self.new_member_action.triggered.connect(
            lambda: MemberDialog(parent=self).show()
        )
        self.new_session_action.triggered.connect(
            lambda: SessionDialog(parent=self).show()
        )

        self.session_deleted.connect(
            lambda session: self.__status_update(
                self.tr("Session '{name}' deleted").format(name=session.name)
            )
        )
        self.session_created.connect(
            lambda session: self.__status_update(
                self.tr("Session '{name}' created").format(name=session.name)
            )
        )

        self.member_deleted.connect(
            lambda member: self.__status_update(
                self.tr("Member '{first_name} {last_name}' deleted").format(
                    first_name=member.first_name, last_name=member.last_name
                )
            )
        )
        self.member_created.connect(
            lambda member: self.__status_update(
                self.tr("Member '{first_name} {last_name}' created").format(
                    first_name=member.first_name, last_name=member.last_name
                )
            )
        )

    def __init_state(self):
        self.setWindowTitle("Memmer")

        self.__status_update(status=None)

        if self.config.db_backend is not None and self.config.db_name is not None:
            # Only set connection parameter if the config contains the required fields
            # If not, we assume that we start fully with defaults
            self.connect_page.connection_parameter = ConnectionParameter.from_config(
                self.config
            )

        self.__switch_to(self.connect_page)

    def __switch_to(self, widget):
        old = self.page_stack.currentWidget()

        if isinstance(old, MemmerWidget):
            old.closed()

        if isinstance(widget, MemmerWidget):
            widget.opened(widget not in self.__opened_widgets)
            self.__opened_widgets.add(widget)

        self.page_stack.setCurrentWidget(widget)

    def __status_update(self, status: Optional[str]):
        if status:
            self.statusbar.showMessage(status, timeout=5000)
        else:
            self.statusbar.showMessage(self.tr("Ready"))

    def __connection_established(
        self, session: orm.Session, tunnel: Optional[SSHTunnelForwarder]
    ):
        if self.session:
            self.session.rollback()
            self.session.close()

        if self.ssh_tunnel:
            self.ssh_tunnel.stop()

        self.session = session
        self.ssh_tunnel = tunnel

        self.data_manager = DataManager(session=self.session)

        ConnectionParameter.to_config(
            self.connect_page.connection_parameter, self.config
        )

        self.__switch_to(self.main_menu)

        self.__status_update(status=self.tr("Connected"))

        self.menu_new.setEnabled(True)

    def __disconnect(self):
        if self.session:
            if has_uncommitted_changes(self.session):
                # There are uncommitted changes
                answer = QMessageBox.question(
                    self,
                    self.tr("Uncommitted changes"),
                    self.tr("Do you want to persist your modifications?"),
                    buttons=QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No,
                )

                if answer == QMessageBox.StandardButton.Yes:
                    self.__status_update(self.tr("Committing changes…"))

                    self.session.commit()

                    self.__status_update(self.tr("Changes committed"))
                else:
                    self.session.rollback()

            self.session.close()
            self.session = None

        if self.ssh_tunnel:
            self.ssh_tunnel.stop()
            self.ssh_tunnel = None

        save_config(self.config)

        self.__switch_to(self.connect_page)

        self.__status_update(status=self.tr("Disconnected"))

        self.menu_new.setEnabled(False)

    def closeEvent(self, event):
        self.__disconnect()

        super().closeEvent(event)
