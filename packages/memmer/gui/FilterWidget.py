# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_FilterWidget import Ui_FilterWidget
from .GenericSortFilterProxyModel import GenericSortFilterProxyModel

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal


class FilterWidget(QWidget, Ui_FilterWidget):
    filter_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        # Filter live as the user types; the button re-applies the current text
        self.lineEdit.textChanged.connect(self.filter_changed)
        self.pushButton_3.clicked.connect(
            lambda: self.filter_changed.emit(self.lineEdit.text())
        )

    def attach(self, proxy: GenericSortFilterProxyModel) -> None:
        """Lets this widget drive the given proxy's row filter"""
        self.filter_changed.connect(proxy.set_filter_string)
        proxy.set_filter_string(self.lineEdit.text())
