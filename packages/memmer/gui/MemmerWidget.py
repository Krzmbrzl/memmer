from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

from sqlalchemy.orm import Session


class MemmerWidget(QWidget):
    status_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def parent_mainwindow(self) -> "MainWindow":
        from memmer.gui import MainWindow

        parent = self.parent()
        while parent is not None and type(parent) is not MainWindow:
            parent = parent.parent()

        assert parent is not None

        return parent

    def session(self) -> Session:
        parent = self.parent_mainwindow()

        assert parent.session is not None

        return parent.session
