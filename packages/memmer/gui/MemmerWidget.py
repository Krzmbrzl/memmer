from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, QRunnable, Slot

from sqlalchemy.orm import Session

if TYPE_CHECKING:
    # This creates cyclic imports, so we only want to do this to bring in the
    # symbol for type-checking but not at runtime
    # See https://stackoverflow.com/a/39757388
    from memmer.gui import MainWindow


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

    def async_exec(self, runnable):
        parent = self.parent_mainwindow()

        if isinstance(runnable, QRunnable):
            parent.thread_pool.start(runnable)
        else:

            class RunnableWrapper(QRunnable):
                def __init__(self, runnable):
                    super().__init__()
                    self.runnable = runnable

                def run(self):
                    self.runnable()

            wrapper = RunnableWrapper(runnable)

            parent.thread_pool.start(wrapper)

    def config(self):
        config = self.parent_mainwindow().config

        assert config is not None

        return config

    @Slot(bool)
    def opened(self, first_time: bool):
        pass

    @Slot()
    def closed(self):
        pass
