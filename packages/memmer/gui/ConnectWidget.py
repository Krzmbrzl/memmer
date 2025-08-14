from .compiled_ui_files.ui_ConnectWidget import Ui_ConnectWidget

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

from memmer.utils import DBBackend, ConnectType

def backend_idx_to_type(idx: int) -> DBBackend:
    if idx == 0:
        return DBBackend.SQLite
    elif idx == 1:
        return DBBackend.PostgreSQL
    elif idx == 2:
        return DBBackend.MySQL

    raise RuntimeError(f"Unknown DB backend index '{idx}'")

def connect_idx_to_type(idx: int) -> ConnectType:
    if idx == 0:
        return ConnectType.REGULAR
    elif idx == 1:
        return ConnectType.SSH_TUNNEL

    raise RuntimeError(f"Unknown connect type index '{idx}'")

class ConnectWidget(QWidget, Ui_ConnectWidget):
    connected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.__connect_signals()

        self.__init_state()

    def __connect_signals(self):
        self.connection_type_combo.currentIndexChanged.connect(
            self.__connect_type_changed
        )

        self.db_backend_combo.currentIndexChanged.connect(self.__db_backend_changed)

        self.db_name_input.textChanged.connect(self.__db_name_changed)

    def __init_state(self):
        self.__connect_type_changed(self.connection_type_combo.currentIndex())

        self.__db_backend_changed(self.db_backend_combo.currentIndex())

        self.__db_name_changed(self.db_name_input.text())

    def __connect_type_changed(self, type_idx: int):
        connect_type = connect_idx_to_type(idx=type_idx)

        self.ssh_group.setVisible(connect_type == ConnectType.SSH_TUNNEL)

    def __db_backend_changed(self, backend_idx: int):
        backend = backend_idx_to_type(idx=backend_idx)

        # Disable options that aren't applicable for SQLite
        self.db_host_label.setVisible(backend != DBBackend.SQLite)
        self.db_host_input.setVisible(backend != DBBackend.SQLite)
        self.db_port_label.setVisible(backend != DBBackend.SQLite)
        self.db_port_spinner.setVisible(backend != DBBackend.SQLite)

    def __db_name_changed(self, name: str):
        self.connect_button.setEnabled(len(name.strip()) > 0)
