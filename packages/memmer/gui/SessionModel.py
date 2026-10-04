# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import List, Any, Optional
from enum import IntEnum

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt

from memmer.orm import Session
from memmer.utils import is_active


class SessionModel(QAbstractTableModel):
    class Column(IntEnum):
        Name = 0
        Participants = 1

    SessionIdRole: int = Qt.ItemDataRole.UserRole

    def __init__(self, sessions: List[Session] = [], parent=None):
        super().__init__(parent)

        self.sessions = sessions

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        return len(self.sessions)

    def columnCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        # Last name, first name, city, age
        return len(SessionModel.Column)

    def data(
        self,
        idx: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not idx.isValid():
            return None

        row = idx.row()
        col = idx.column()

        if row >= len(self.sessions):
            return None

        session: Session = self.sessions[row]

        if role == Qt.ItemDataRole.DisplayRole:
            if col == SessionModel.Column.Name:
                return session.name
            elif col == SessionModel.Column.Participants:
                return sum((1 for x in session.members if is_active(x)))
        elif role == SessionModel.SessionIdRole:
            return session.id

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
            if col == SessionModel.Column.Name:
                return self.tr("Name")
            elif col == SessionModel.Column.Participants:
                return self.tr("Participants")

        return None

    def session_for(
        self, idx: QModelIndex | QPersistentModelIndex
    ) -> Optional[Session]:
        if not idx.isValid():
            return None

        row = idx.row()

        if row >= len(self.sessions):
            return None

        return self.sessions[row]

    def row_for(self, session: Session) -> Optional[int]:
        """The row showing ``session``, or None if it isn't shown"""
        for row, current in enumerate(self.sessions):
            if current.id == session.id:
                return row
        return None

    def session_updated(self, session: Session) -> None:
        """Repaints the row of a session whose data changed in place"""
        row = self.row_for(session)
        if row is None:
            return
        self.dataChanged.emit(
            self.index(row, 0), self.index(row, self.columnCount() - 1)
        )

    def refresh_participant_counts(self) -> None:
        """Repaints the participant column, e.g. after a member changed"""
        if len(self.sessions) == 0:
            return
        self.dataChanged.emit(
            self.index(0, SessionModel.Column.Participants),
            self.index(len(self.sessions) - 1, SessionModel.Column.Participants),
        )

    def reload(self) -> None:
        """Resets the rows from the (already updated) backing list.

        Used after a session was added to or removed from the shared list."""
        self.beginResetModel()
        self.endResetModel()
