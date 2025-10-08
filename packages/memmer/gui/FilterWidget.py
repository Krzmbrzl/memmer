# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_FilterWidget import Ui_FilterWidget

from PySide6.QtWidgets import QWidget


class FilterWidget(QWidget, Ui_FilterWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
