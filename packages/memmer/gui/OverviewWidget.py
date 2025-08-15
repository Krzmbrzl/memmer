from .compiled_ui_files.ui_OverviewWidget import Ui_OverviewWidget

from memmer.gui import MemmerWidget


class OverviewWidget(MemmerWidget, Ui_OverviewWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
