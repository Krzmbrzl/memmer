from ui_ConnectWidget import Ui_ConnectWidget

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

class ConnectWidget(QWidget, Ui_ConnectWidget):
    connected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        # Hide SSH group by default
        self.ssh_group.setVisible(False)

        self.__connect_signals()

    def __connect_signals(self):
        pass

