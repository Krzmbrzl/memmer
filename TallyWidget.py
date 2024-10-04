from ui_TallyWidget import Ui_TallyWidget

from PySide6.QtWidgets import QWidget


class TallyWidget(QWidget, Ui_TallyWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
