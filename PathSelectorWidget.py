from ui_PathSelectorWidget import Ui_PathSelectorWidget

from PySide6.QtWidgets import QWidget, QFileDialog, QDialog
from PySide6.QtCore import Signal, Slot

from pathlib import Path


class PathSelectorWidget(QWidget, Ui_PathSelectorWidget):
    pathChanged = Signal(str)

    def __init__(
        self,
        parent=None,
        file_mode: QFileDialog.FileMode = QFileDialog.FileMode.AnyFile,
        dir_path: Path = Path.home(),
        accept_mode: QFileDialog.AcceptMode = QFileDialog.AcceptMode.AcceptOpen,
        placeholder: str = "/path/to/resource",
    ):
        super().__init__(parent=parent)

        self.setupUi(self)

        self.browse_button.released.connect(self.__on_browse)
        self.file_mode = file_mode
        self.dir_path = dir_path
        self.accept_mode = accept_mode

        self.path_input.setPlaceholderText(placeholder)

        self.__wire_signals()

    def __wire_signals(self) -> None:
        self.path_input.textChanged.connect(lambda path: self.pathChanged.emit(path))

    def __on_browse(self) -> None:
        file_chooser = QFileDialog(self)

        file_chooser.setFileMode(self.file_mode)
        file_chooser.setDirectory(self.dir_path.absolute().as_posix())
        file_chooser.setAcceptMode(self.accept_mode)

        file_chooser.setModal(True)

        if file_chooser.exec() == QDialog.DialogCode.Accepted:
            assert len(file_chooser.selectedFiles()) == 1
            self.setPath(file_chooser.selectedFiles()[0])

    def path(self) -> str:
        return self.path_input.text()

    @Slot(str)
    def setPath(self, path: str) -> None:
        self.path_input.setText(path)
