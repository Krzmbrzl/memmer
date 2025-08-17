from typing import List, Tuple

from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, QPersistentModelIndex, Qt


class GenericSortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, sort_orders: List[Tuple[int, Qt.SortOrder]], parent):
        super().__init__(parent)
        self.sort_orders = sort_orders

    def filterAcceptsRow(
        self, source_row: int, source_idx: QModelIndex | QPersistentModelIndex
    ) -> bool:
        return True

    def lessThan(
        self,
        lhs: QModelIndex | QPersistentModelIndex,
        rhs: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        lhs_data = lhs.data()
        rhs_data = rhs.data()

        if lhs_data < rhs_data:
            return True
        if rhs_data < lhs_data:
            return False

        # The underlying data is equal for the selected columns -> sort by remaining columns
        for col, order in self.sort_orders:
            lhs_idx = self.sourceModel().index(lhs.row(), col)
            rhs_idx = self.sourceModel().index(rhs.row(), col)

            lhs_data = lhs_idx.data()
            rhs_data = rhs_idx.data()

            if order == Qt.SortOrder.DescendingOrder:
                # Switch lhs and rhs
                rhs_data, lhs_data = lhs_data, rhs_data

            if lhs_data < rhs_data:
                return True
            elif rhs_data < lhs_data:
                return False

        # Indices considered equivalent
        return False
