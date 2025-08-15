from .compiled_ui_files.ui_MainMenuWidget import Ui_MainMenuWidget

from PySide6.QtCore import Signal

from memmer.gui import MemmerWidget


class MainMenuWidget(MemmerWidget, Ui_MainMenuWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
