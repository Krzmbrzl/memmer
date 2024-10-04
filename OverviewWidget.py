from ui_OverviewWidget import Ui_OverviewWidget

from PySide6.QtWidgets import QWidget


class OverviewWidget(QWidget, Ui_OverviewWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
