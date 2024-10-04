from ui_MainWindow import Ui_MainWindow

from PySide6.QtWidgets import QMainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.statusbar.showMessage(self.tr("Ready"))

        self.setWindowTitle("Memmer")


