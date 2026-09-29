# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Optional, List, Any
from enum import IntEnum
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import (
    QAbstractTableModel,
    QAbstractItemModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    QTimer,
)
from PySide6.QtWidgets import (
    QStyledItemDelegate,
    QDoubleSpinBox,
    QWidget,
    QStyleOptionViewItem,
)

from memmer.orm import Member


@dataclass(unsafe_hash=True)
class Fee:
    reason: str
    amount: Decimal


class OneTimeFeeModel(QAbstractTableModel):
    class Column(IntEnum):
        Reason = 0
        Amount = 1

    def __init__(self, member: Optional[Member] = None, parent=None):
        super().__init__(parent)

        self.fees: List[Fee] = []

        if member:
            self.load_for(member)

    def load_for(self, member: Member):
        removed_rows = False
        if len(self.fees) > 0:
            self.beginRemoveRows(QModelIndex(), 0, len(self.fees) - 1)
            removed_rows = True

        self.fees.clear()

        if removed_rows:
            self.endRemoveRows()

        if len(member.one_time_fees) > 0:
            self.beginInsertRows(QModelIndex(), 0, len(member.one_time_fees) - 1)

            for fee in member.one_time_fees:
                self.fees.append(Fee(reason=fee.reason, amount=fee.amount))

            self.endInsertRows()

    def add_fee(self, reason: str, amount: Decimal):
        self.beginInsertRows(QModelIndex(), len(self.fees), len(self.fees))

        self.fees.append(Fee(reason=reason, amount=amount))

        self.endInsertRows()

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        return len(self.fees) + 1

    def columnCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        return len(OneTimeFeeModel.Column)

    def headerData(
        self,
        col: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if orientation != Qt.Orientation.Horizontal:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            if col == OneTimeFeeModel.Column.Reason:
                return self.tr("Reason")
            elif col == OneTimeFeeModel.Column.Amount:
                return self.tr("Amount")

        return None

    def data(
        self,
        idx: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not idx.isValid():
            return None

        row = idx.row()
        col = idx.column()

        if col >= len(OneTimeFeeModel.Column):
            return None

        if row > len(self.fees):
            return None

        if row == len(self.fees):
            # Special last row used as a placeholder to insert new data
            if role == Qt.ItemDataRole.DisplayRole:
                if col == OneTimeFeeModel.Column.Reason:
                    return self.tr("(Add new…)")
                elif col == OneTimeFeeModel.Column.Amount:
                    return ""
            elif role == Qt.ItemDataRole.FontRole:
                font = QFont()
                font.setItalic(True)
                return font
        else:
            fee = self.fees[row]
            missing_reason = (
                col == OneTimeFeeModel.Column.Reason and len(fee.reason.strip()) == 0
            )

            if missing_reason and role == Qt.ItemDataRole.BackgroundRole:
                return QColor(211, 47, 47, 60)
            elif missing_reason and role == Qt.ItemDataRole.ToolTipRole:
                return self.tr("Please enter a reason")
            elif role == Qt.ItemDataRole.DisplayRole:
                if col == OneTimeFeeModel.Column.Reason:
                    return fee.reason
                elif col == OneTimeFeeModel.Column.Amount:
                    return f"{fee.amount:.2f} €"
            elif role == Qt.ItemDataRole.EditRole:
                if col == OneTimeFeeModel.Column.Reason:
                    return fee.reason
                elif col == OneTimeFeeModel.Column.Amount:
                    return str(fee.amount)

        return None

    def flags(self, idx: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        base_flags = super().flags(idx)

        if idx.isValid():
            base_flags |= Qt.ItemFlag.ItemIsEditable

        return base_flags

    def setData(
        self,
        idx: QModelIndex | QPersistentModelIndex,
        value: Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if role != Qt.ItemDataRole.EditRole:
            return False

        if not idx.isValid():
            return False

        row = idx.row()
        col = idx.column()

        if col >= len(OneTimeFeeModel.Column):
            return False

        if row > len(self.fees):
            return False

        if col == OneTimeFeeModel.Column.Amount:
            value = value.replace("€", "")

        value = value.strip()

        try:
            if row == len(self.fees):
                # Append a new entry
                if col == OneTimeFeeModel.Column.Reason and len(value) > 0:
                    self.add_fee(reason=value, amount=Decimal(0))
                    return True
                elif col == OneTimeFeeModel.Column.Amount and Decimal(value) != 0:
                    # The reason has to be entered afterwards
                    self.add_fee(reason="", amount=Decimal(value))
                    return True
            else:
                if col == OneTimeFeeModel.Column.Reason:
                    if len(value) > 0:
                        self.fees[row].reason = value
                        self.dataChanged.emit(idx, idx)
                    else:
                        # Remove this row
                        def remove_row():
                            self.beginRemoveRows(QModelIndex(), row, row)

                            del self.fees[row]

                            self.endRemoveRows()

                        # Give the current editor time to close before we remove the row
                        # (in the next iteration of the event loop)
                        QTimer.singleShot(0, remove_row)

                    return True
                elif col == OneTimeFeeModel.Column.Amount:
                    self.fees[row].amount = Decimal(value)
                    self.dataChanged.emit(idx, idx)
                    return True
        except InvalidOperation:
            pass

        return False

    def get_fees(self) -> List[Fee]:
        return self.fees


class OneTimeFeeAmountDelegate(QStyledItemDelegate):
    """Edits amounts with a spin box so that only valid amounts can be entered"""

    def createEditor(
        self,
        parent: QWidget,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(2)
        # Negative amounts are credits
        editor.setRange(-9999.99, 9999.99)
        editor.setSuffix(" €")
        return editor

    def setEditorData(
        self, editor: QWidget, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        assert isinstance(editor, QDoubleSpinBox)
        value = index.data(Qt.ItemDataRole.EditRole)
        editor.setValue(float(value) if value else 0.0)

    def setModelData(
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        assert isinstance(editor, QDoubleSpinBox)
        editor.interpretText()
        model.setData(index, f"{editor.value():.2f}", Qt.ItemDataRole.EditRole)
