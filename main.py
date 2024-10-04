#!/usr/bin/env python3

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtUiTools import QUiLoader

from MainWindow import MainWindow

import sys
import signal


def quit_app(*_):
    QApplication.quit()


def main():
    signal.signal(signal.SIGINT, quit_app)

    app = QApplication(sys.argv)

    # Required to ensure that the Python interpreter is called every now
    # and then in order to allow for signal handling (e.g. Ctrl+C)
    # to be done.
    # Taken from https://stackoverflow.com/a/4939113
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    # loader = QUiLoader()
    # win = loader.load("MainWindow.ui")
    win = MainWindow()

    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
