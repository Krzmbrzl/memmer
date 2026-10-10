# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_MainWindow import Ui_MainWindow

from typing import Callable, Optional, Set

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import Signal

from memmer.orm import Member, Session
from memmer.utils import (
    load_config,
    save_config,
    has_uncommitted_changes,
    MemmerConfig,
    ConnectionParameter,
    DataManager,
)
from memmer.gui import MemmerWidget, MemberDialog, SessionDialog, DatabaseController


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

        self.config: MemmerConfig = load_config()
        # Owns the DB session on a dedicated thread; all DB access is serialized
        # through it.
        self.db_controller = DatabaseController(self)
        self.data_manager = None
        self.__connected = False
        self.__shutting_down = False
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
        self.main_menu.member_list_page_requested.connect(
            lambda: self.__switch_to(self.member_list_page)
        )

        self.tally_page.main_menu_requested.connect(
            lambda: self.__switch_to(self.main_menu)
        )
        self.tally_page.status_changed.connect(self.__status_update)
        # Block starting edits while a tally is being created.
        self.tally_page.busy_changed.connect(
            lambda busy: self.menu_new.setEnabled(not busy)
        )

        self.member_list_page.main_menu_requested.connect(
            lambda: self.__switch_to(self.main_menu)
        )
        self.member_list_page.status_changed.connect(self.__status_update)
        # Block starting edits while a list is being generated.
        self.member_list_page.busy_changed.connect(
            lambda busy: self.menu_new.setEnabled(not busy)
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

    def __connection_established(self):
        # The session was created and is owned by the controller's DB thread.
        self.__connected = True
        self.data_manager = DataManager(controller=self.db_controller)

        ConnectionParameter.to_config(
            self.connect_page.connection_parameter, self.config
        )

        self.__switch_to(self.main_menu)

        self.__status_update(status=self.tr("Connected"))

        self.menu_new.setEnabled(True)

    def __disconnect(self, on_done: Optional[Callable[[], None]] = None):
        if not self.__connected:
            self.__finish_disconnect()
            if on_done is not None:
                on_done()
            return

        def check(session):
            return session is not None and has_uncommitted_changes(session)

        def decide(has_changes: bool):
            commit = False
            if has_changes:
                answer = QMessageBox.question(
                    self,
                    self.tr("Uncommitted changes"),
                    self.tr("Do you want to persist your modifications?"),
                    buttons=QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No,
                )
                commit = answer == QMessageBox.StandardButton.Yes

            if commit:
                self.__status_update(self.tr("Committing changes…"))

            def finished(_):
                self.__finish_disconnect(committed=commit)
                if on_done is not None:
                    on_done()

            # teardown commits or rolls back, then closes the session and the
            # tunnel, all on the DB thread.
            self.db_controller.teardown(
                commit,
                on_success=finished,
                on_error=self.__disconnect_failed,
            )

        self.db_controller.submit(
            check, on_success=decide, on_error=self.__disconnect_failed
        )

    def __disconnect_failed(self, error: Exception):
        # Allow another close attempt if the shutdown-triggered disconnect failed.
        self.__shutting_down = False
        self.__status_update(self.tr("Disconnecting failed"))
        QMessageBox.critical(
            self,
            self.tr("Disconnecting failed"),
            self.tr("The database operation failed. Reason given:\n{error}").format(
                error=error
            ),
        )

    def __finish_disconnect(self, committed: bool = False):
        self.__connected = False
        self.data_manager = None

        if committed:
            self.__status_update(self.tr("Changes committed"))

        save_config(self.config)

        self.__switch_to(self.connect_page)

        self.__status_update(status=self.tr("Disconnected"))

        self.menu_new.setEnabled(False)

    def closeEvent(self, event):
        # Disconnecting (and the optional commit) runs asynchronously on the DB
        # thread and may show a modal dialog. Closing the window right away would
        # drop that pending work and, because the modal dialog re-enters the
        # event loop, leave "quit on last window closed" unable to fire — so the
        # process would keep running with no window. Keep the window open until
        # the shutdown finished, then quit explicitly.
        if self.__shutting_down:
            super().closeEvent(event)
            return

        self.__shutting_down = True
        event.ignore()
        self.__disconnect(on_done=self.__quit)

    def __quit(self):
        self.db_controller.shutdown()
        QApplication.quit()
