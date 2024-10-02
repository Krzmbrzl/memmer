#!/usr/bin/env python3

from ui_MainWindow import Ui_MainWindow

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader

import sys


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.statusbar.showMessage(self.tr("Ready"))

        self.setWindowTitle("Memmer")

        self.connect_button.clicked.connect(
            lambda: self.page_stack.setCurrentWidget(self.main_menu)
        )


def main():
    loader = QUiLoader()

    app = QApplication(sys.argv)

    # win = loader.load("MainWindow.ui")
    win = MainWindow()

    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
