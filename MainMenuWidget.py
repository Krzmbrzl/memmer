from ui_MainMenuWidget import Ui_MainMenuWidget

from PySide6.QtWidgets import QWidget


class MainMenuWidget(QWidget, Ui_MainMenuWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setupUi(self)
