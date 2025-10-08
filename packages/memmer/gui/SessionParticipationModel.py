# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import List, Any, Optional

from memmer.gui import SessionModel
from memmer.orm import Session, Member

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt


class SessionParticipationModel(SessionModel):
    def __init__(
        self, member: Optional[Member], sessions: List[Session] = [], parent=None
    ):
        super().__init__(sessions=sessions, parent=parent)

        self.member = member
        self.participations = [False] * len(sessions)

        if self.member:
            for current in self.member.participating_sessions:
                idx = self.sessions.index(current)
                self.participations[idx] = True

    def flags(self, idx: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        base_flags = super().flags(idx)

        if idx.isValid() and idx.column() == SessionModel.Column.Name:
            base_flags |= Qt.ItemFlag.ItemIsUserCheckable

        return base_flags

    def data(
        self,
        idx: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if role != Qt.ItemDataRole.CheckStateRole:
            return super().data(idx=idx, role=role)

        if not idx.isValid():
            return None

        row = idx.row()
        col = idx.column()

        if col != SessionModel.Column.Name:
            return None

        if row >= len(self.participations):
            return None

        return (
            Qt.CheckState.Checked
            if self.participations[row]
            else Qt.CheckState.Unchecked
        )

    def setData(
        self,
        idx: QModelIndex | QPersistentModelIndex,
        value: Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if role != Qt.ItemDataRole.CheckStateRole:
            return super().setData(idx, value, role)

        if not idx.isValid():
            return False

        row = idx.row()
        col = idx.column()

        if col != SessionModel.Column.Name:
            return False

        if row >= len(self.participations):
            return False

        self.participations[row] = (
            True if value == Qt.CheckState.Checked.value else False
        )

        return True

    def get_participated_sessions(self) -> List[Session]:
        participated_sessions: List[Session] = []

        for i, participating in enumerate(self.participations):
            if participating:
                participated_sessions.append(self.sessions[i])

        return participated_sessions
