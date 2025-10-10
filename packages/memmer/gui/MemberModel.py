# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import List, Any, Optional, Sequence, Callable
from enum import IntEnum
from copy import copy

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

    MemberIdRole = Qt.ItemDataRole.UserRole

    def __init__(
        self,
        members: List[Member] = [],
        active: Optional[Sequence[Member | int]] = None,
        inactive: Optional[Sequence[Member | int]] = None,
        active_predicate: Optional[Callable[[Member], bool]] = None,
        inactive_predicate: Optional[Callable[[Member], bool]] = None,
        parent=None,
    ):
        super().__init__(parent)

        self.members = members
        self.active: List[int] = []

        if active is None:
            self.active = list(range(0, len(self.members)))
        else:
            for current in active:
                if isinstance(current, Member):
                    self.active.append(self.members.index(current))
                else:
                    self.active.append(current)

        if inactive is not None:
            for current in inactive:
                if isinstance(current, Member):
                    self.active.remove(self.members.index(current))
                else:
                    self.active.remove(current)

        if active_predicate is not None:
            for i, current in enumerate(self.members):
                if active_predicate(current) and i not in self.active:
                    self.active.append(i)

        if inactive_predicate is not None:
            self.active = [
                x for x in self.active if not inactive_predicate(self.members[x])
            ]

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        return len(self.active)

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

        if row >= len(self.active):
            return None

        member: Member = self.members[self.active[row]]

        if role == Qt.ItemDataRole.DisplayRole:
            if col == MemberModel.Column.LastName:
                return member.last_name
            elif col == MemberModel.Column.FirstName:
                return member.first_name
            elif col == MemberModel.Column.City:
                return member.city
            elif col == MemberModel.Column.Age:
                return nominal_year_diff(member.birthday, datetime.now().date())
        elif role == MemberModel.MemberIdRole:
            return member.id

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

    def member_for(self, idx: QModelIndex | QPersistentModelIndex) -> Optional[Member]:
        if not idx.isValid():
            return None

        row = idx.row()

        if row >= len(self.active):
            return None

        return self.members[self.active[row]]

    def get_members(self) -> List[Member]:
        return [self.members[x] for x in self.active]

    def make_active(
        self, member: Optional[Member] = None, member_id: Optional[int] = None
    ):
        if member is not None and member_id is not None:
            raise RuntimeError("Can only specify member or member_id, but not both")
        if member is None and member_id is None:
            raise RuntimeError("Have to specify member or member_id")

        if member is not None:
            idx = self.members.index(member)
        else:
            assert member_id is not None
            idx = None
            for i, current in enumerate(self.members):
                if current.id == member_id:
                    idx = i
                    break

            if idx is None:
                return

        if idx in self.active:
            return

        self.beginInsertRows(QModelIndex(), len(self.active), len(self.active))

        self.active.append(idx)

        self.endInsertRows()

    def make_inactive(
        self, member: Optional[Member] = None, member_id: Optional[int] = None
    ):
        if member is not None and member_id is not None:
            raise RuntimeError("Can only specify member or member_id, but not both")
        if member is None and member_id is None:
            raise RuntimeError("Have to specify member or member_id")

        if member is not None:
            idx = self.members.index(member)
        else:
            assert member_id is not None
            idx = None
            for i, current in enumerate(self.members):
                if current.id == member_id:
                    idx = i
                    break

            if idx is None:
                return

        if idx not in self.active:
            return

        active_idx = self.active.index(idx)

        self.beginRemoveRows(QModelIndex(), active_idx, active_idx)

        del self.active[active_idx]

        self.endRemoveRows()
