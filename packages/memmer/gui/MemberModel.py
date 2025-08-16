from typing import List, Any
from enum import IntEnum

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt

from memmer.orm import Member
from memmer.utils import nominal_year_diff

from datetime import datetime


class MemberModel(QAbstractTableModel):
    class Column(IntEnum):
        LastName = 0
        FirstName = 1
        City = 2
        Age = 3

    def __init__(self, members: List[Member] = [], parent=None):
        super().__init__(parent)

        self.members = members

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        return len(self.members)

    def columnCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        # Last name, first name, city, age
        return len(MemberModel.Column)

    def data(
        self,
        idx: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not idx.isValid():
            return None

        row = idx.row()
        col = idx.column()

        if row >= len(self.members):
            return None

        member: Member = self.members[row]

        if role == Qt.ItemDataRole.DisplayRole:
            if col == MemberModel.Column.LastName:
                return member.last_name
            elif col == MemberModel.Column.FirstName:
                return member.first_name
            elif col == MemberModel.Column.City:
                return member.city
            elif col == MemberModel.Column.Age:
                return nominal_year_diff(member.birthday, datetime.now().date())

        return None

    def headerData(
        self,
        col: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if orientation != Qt.Orientation.Horizontal:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            if col == MemberModel.Column.LastName:
                return self.tr("Last name")
            elif col == MemberModel.Column.FirstName:
                return self.tr("First name")
            elif col == MemberModel.Column.City:
                return self.tr("City")
            elif col == MemberModel.Column.Age:
                return self.tr("Age")

        return None
