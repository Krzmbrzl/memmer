# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Optional

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from memmer.gui import MemmerDialog
from memmer.queries import TallyResult


class TallyResultDialog(MemmerDialog):
    """Shown once a tally has been created but is not yet committed.

    It lets the user open the generated file for inspection and then decide
    whether to keep (commit) or discard (roll back) the changes. Because a
    discard also deletes the file, the dialog refuses to close without an
    explicit choice; :attr:`decision` is therefore always set afterwards."""

    def __init__(self, result: TallyResult, parent=None):
        super().__init__(parent=parent)

        self.__output_path = result.output_path
        self.decision: Optional[str] = None

        self.setWindowTitle(self.tr("Tally created"))
        self.setModal(True)
        # No close button: the user must pick keep or discard explicitly.
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        layout = QVBoxLayout(self)

        summary = QLabel(
            self.tr(
                "The tally has been created but not saved yet. Inspect it and "
                "choose whether to keep or discard it.\n\n"
                "Transactions: {count}\n"
                "Total amount: {amount} €\n"
                "File: {path}"
            ).format(
                count=result.transaction_count,
                amount="{:.2f}".format(result.total_amount),
                path=result.output_path,
            ),
            self,
        )
        summary.setWordWrap(True)
        summary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(summary)

        open_button = QPushButton(self.tr("Open file"), self)
        open_button.clicked.connect(self.__open_file)

        keep_button = QPushButton(self.tr("Keep"), self)
        keep_button.setDefault(True)
        keep_button.clicked.connect(lambda: self.__decide("keep"))

        discard_button = QPushButton(self.tr("Discard"), self)
        discard_button.clicked.connect(lambda: self.__decide("discard"))

        button_box = QDialogButtonBox(self)
        button_box.addButton(open_button, QDialogButtonBox.ButtonRole.ActionRole)
        button_box.addButton(discard_button, QDialogButtonBox.ButtonRole.DestructiveRole)
        button_box.addButton(keep_button, QDialogButtonBox.ButtonRole.AcceptRole)
        layout.addWidget(button_box)

    def __open_file(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.__output_path))

    def __decide(self, decision: str) -> None:
        self.decision = decision
        self.accept()

    def reject(self) -> None:
        # Ignore Escape / window-manager close: a choice is mandatory.
        pass
