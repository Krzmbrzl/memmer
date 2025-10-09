# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import List, Any, Optional
from enum import IntEnum

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt

from memmer.orm import Session


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
                # TODO: This seems to take a non-trivial amount of time
                # -> prefetch linked members?
                return len(session.members)
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
