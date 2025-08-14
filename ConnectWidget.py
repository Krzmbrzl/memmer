from .compiled_ui_files.ui_ConnectWidget import Ui_ConnectWidget

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal


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
        assert type_idx in [0, 1]

        is_ssh = type_idx == 1

        self.ssh_group.setVisible(is_ssh)

    def __db_backend_changed(self, backend_idx: int):
        assert backend_idx in [0, 1, 2]

        is_sqlite = backend_idx == 0

        self.db_host_label.setVisible(not is_sqlite)
        self.db_host_input.setVisible(not is_sqlite)
        self.db_port_label.setVisible(not is_sqlite)
        self.db_port_spinner.setVisible(not is_sqlite)

    def __db_name_changed(self, name: str):
        self.connect_button.setEnabled(len(name.strip()) > 0)
