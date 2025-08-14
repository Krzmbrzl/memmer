from .compiled_ui_files.ui_MainWindow import Ui_MainWindow

from typing import Optional

from PySide6.QtWidgets import QMainWindow, QMessageBox

from sqlalchemy.orm import Session

from sshtunnel import SSHTunnelForwarder

from memmer.utils import load_config, save_config, MemmerConfig, ConnectionParameter


def has_uncommitted_changes(session: Session):
    return (
        any(session.new)
        or any(session.deleted)
        or any([x for x in session.dirty if session.is_modified(x)])
        or session.info.get("flushed", False)
    )


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.ssh_tunnel: Optional[SSHTunnelForwarder] = None
        self.session: Optional[Session] = None
        self.config: MemmerConfig = load_config()

        self.__connect_signals()

        self.__init_state()

    def __connect_signals(self):
        self.statusbar.messageChanged.connect(self.__status_update)

        self.connect_page.connected.connect(self.__connection_established)

        self.connect_page.status_changed.connect(self.__status_update)

    def __init_state(self):
        self.setWindowTitle("Memmer")

        self.__status_update(status=None)

        self.connect_page.connection_parameter = ConnectionParameter.from_config(self.config)

    def __status_update(self, status: Optional[str]):
        if status:
            self.statusbar.showMessage(status, timeout=5000)
        else:
            self.statusbar.showMessage(self.tr("Ready"))

    def __connection_established(
        self, session: Session, tunnel: Optional[SSHTunnelForwarder]
    ):
        if self.session:
            self.session.rollback()
            self.session.close()

        if self.ssh_tunnel:
            self.ssh_tunnel.stop()

        self.session = session
        self.ssh_tunnel = tunnel

        ConnectionParameter.to_config(self.connect_page.connection_parameter, self.config)

        self.page_stack.setCurrentWidget(self.main_menu)

    def closeEvent(self, event):
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
                    self.session.commit()
                else:
                    self.session.rollback()

            self.session.close()

        if self.ssh_tunnel:
            self.ssh_tunnel.stop()

        save_config(self.config)

        super().closeEvent(event)
