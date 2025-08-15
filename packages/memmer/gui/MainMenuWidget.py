from .compiled_ui_files.ui_MainMenuWidget import Ui_MainMenuWidget

from PySide6.QtCore import Signal

from memmer.gui import MemmerWidget


class MainMenuWidget(MemmerWidget, Ui_MainMenuWidget):
    disconnect_requested = Signal()
    overview_page_requested = Signal()
    tally_page_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.__connect_signals()

        self.__init_state()

    def __connect_signals(self):
        self.disconnect_button.clicked.connect(self.disconnect_requested.emit)

        self.commit_button.clicked.connect(self.__commit_changes)

        self.overview_button.clicked.connect(self.overview_page_requested.emit)

        self.tally_button.clicked.connect(self.tally_page_requested.emit)

    def __init_state(self):
        pass

    def __commit_changes(self):
        self.session().commit()

        self.status_changed.emit(self.tr("Changes committed"))
