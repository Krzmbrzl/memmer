from ui_FilterWidget import Ui_FilterWidget

from PySide6.QtWidgets import QWidget


class FilterWidget(QWidget, Ui_FilterWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
