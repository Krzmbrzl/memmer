# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from .compiled_ui_files.ui_MemberListWidget import Ui_MemberListWidget

from typing import List, Optional

import datetime
import os
import time

from PySide6.QtCore import Signal, Slot, Qt, QDate, QModelIndex, QPersistentModelIndex
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHeaderView,
    QInputDialog,
    QListWidgetItem,
    QMessageBox,
)
from PySide6.QtCore import QUrl

from memmer.gui import (
    MemmerWidget,
    MemberModel,
    GenericSortFilterProxyModel,
    FormValidator,
    Issue,
    error,
)
from memmer.orm import Member, Setting

from sqlalchemy import select
from memmer.queries import (
    ColumnKind,
    ColumnSpec,
    ColumnTemplate,
    MemberListResult,
    SelectionKind,
    REPEATABLE_KINDS,
    select_members,
    render_member_list_pdf,
    render_member_list_csv,
    load_column_templates,
    save_column_templates,
)
from memmer.utils import active_members


# Data columns offered in the "available" list, in the order they appear there.
# EMPTY and CHECKBOX are added through dedicated buttons (they are repeatable)
# and so never live in the available list.
_AVAILABLE_COLUMN_ORDER = [
    ColumnKind.ROW_NUMBER,
    ColumnKind.FIRST_NAME,
    ColumnKind.LAST_NAME,
    ColumnKind.BIRTHDAY,
    ColumnKind.AGE,
    ColumnKind.ADDRESS,
    ColumnKind.EMAIL,
    ColumnKind.PHONE,
    ColumnKind.IBAN,
    ColumnKind.MONTHLY_FEE,
    ColumnKind.GENDER,
    ColumnKind.ENTRY_DATE,
    ColumnKind.EXIT_DATE,
    ColumnKind.MEMBERSHIP_DURATION,
    ColumnKind.SESSIONS,
]


def _member_model(table) -> MemberModel:
    model = table.model()
    if isinstance(model, GenericSortFilterProxyModel):
        model = model.sourceModel()
    assert isinstance(model, MemberModel)
    return model


def _member_at(table, idx: QModelIndex | QPersistentModelIndex) -> Optional[Member]:
    model = table.model()
    if isinstance(model, GenericSortFilterProxyModel):
        idx = model.mapToSource(idx)
    return _member_model(table).member_for(idx)


def _member_sort_orders():
    return [
        (MemberModel.Column.LastName, Qt.SortOrder.AscendingOrder),
        (MemberModel.Column.FirstName, Qt.SortOrder.AscendingOrder),
        (MemberModel.Column.City, Qt.SortOrder.AscendingOrder),
    ]


class MemberListWidget(MemmerWidget, Ui_MemberListWidget):
    main_menu_requested = Signal()
    # Emitted while a list is being generated so the main window can block
    # editing, mirroring the tally page.
    busy_changed = Signal(bool)
    # Emitted from the DB thread as rows are assembled: (processed, total).
    progress_updated = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.__templates: List[ColumnTemplate] = []
        self.__built = False

        self.__labels = {}

        self.__connect_signals()

        self.__init_static_inputs()

        self.__setup_validation()

    # --- setup -----------------------------------------------------------

    def __connect_signals(self):
        self.back_button.clicked.connect(self.main_menu_requested.emit)
        self.create_button.clicked.connect(self.__create)

        self.selection_combo.currentIndexChanged.connect(self.__apply_selection)
        self.as_of_input.dateChanged.connect(self.__apply_selection)

        self.add_column_button.clicked.connect(self.__add_selected_columns)
        self.remove_column_button.clicked.connect(self.__remove_selected_columns)
        self.add_empty_button.clicked.connect(
            lambda: self.__append_column(ColumnKind.EMPTY)
        )
        self.add_checkbox_button.clicked.connect(
            lambda: self.__append_column(ColumnKind.CHECKBOX)
        )
        self.up_button.clicked.connect(lambda: self.__move_chosen(-1))
        self.down_button.clicked.connect(lambda: self.__move_chosen(1))

        self.template_combo.currentIndexChanged.connect(self.__template_selected)
        self.save_template_button.clicked.connect(self.__save_template_as)
        self.update_template_button.clicked.connect(self.__update_template)
        self.delete_template_button.clicked.connect(self.__delete_template)

        self.format_combo.currentIndexChanged.connect(self.__format_changed)

        self.progress_updated.connect(self.__on_progress)

    def __init_static_inputs(self):
        self.__labels = {
            ColumnKind.ROW_NUMBER: self.tr("No."),
            ColumnKind.FIRST_NAME: self.tr("First name"),
            ColumnKind.LAST_NAME: self.tr("Last name"),
            ColumnKind.BIRTHDAY: self.tr("Date of birth"),
            ColumnKind.AGE: self.tr("Age"),
            ColumnKind.ADDRESS: self.tr("Address"),
            ColumnKind.EMAIL: self.tr("Email"),
            ColumnKind.PHONE: self.tr("Phone"),
            ColumnKind.IBAN: self.tr("IBAN"),
            ColumnKind.MONTHLY_FEE: self.tr("Monthly fee"),
            ColumnKind.GENDER: self.tr("Gender"),
            ColumnKind.ENTRY_DATE: self.tr("Entry date"),
            ColumnKind.EXIT_DATE: self.tr("Exit date"),
            ColumnKind.MEMBERSHIP_DURATION: self.tr("Membership (years)"),
            ColumnKind.SESSIONS: self.tr("Sessions"),
            # Default (editable) headers for the data-less columns.
            ColumnKind.EMPTY: self.tr("Notes"),
            ColumnKind.CHECKBOX: self.tr("Done"),
        }

        self.format_combo.addItem(self.tr("PDF"), "pdf")
        self.format_combo.addItem(self.tr("CSV"), "csv")

        self.orientation_combo.addItem(self.tr("Portrait"), "portrait")
        self.orientation_combo.addItem(self.tr("Landscape"), "landscape")

        self.chosen_columns.setDragDropMode(
            QAbstractItemView.DragDropMode.InternalMove
        )
        self.chosen_columns.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.out_file_input.accept_mode = QFileDialog.AcceptMode.AcceptSave
        self.out_file_input.file_mode = QFileDialog.FileMode.AnyFile

    def __setup_validation(self):
        self.validator = FormValidator(self, self.create_button)

        self.validator.add_check(
            self.__check_columns,
            [self.chosen_columns],
            triggers=[
                self.chosen_columns.model().rowsInserted,
                self.chosen_columns.model().rowsRemoved,
            ],
        )
        self.validator.add_check(self.__check_members, [self.included_table])
        self.validator.add_check(self.__check_out_file, [self.out_file_input])

    # --- lifecycle -------------------------------------------------------

    def opened(self, first_time: bool):
        if not first_time:
            return

        today = datetime.date.today()
        self.as_of_input.setDate(QDate(today.year, today.month, today.day))

        self.__populate_selection_modes()
        self.__refresh_available_columns()
        self.__apply_selection()
        self.__format_changed()

        member_list_dir = self.config().member_list_dir
        if member_list_dir is not None:
            self.out_file_input.dir_path = _as_path(member_list_dir)

        self.__load_templates()

        self.__built = True

    # --- member selection -----------------------------------------------

    def __populate_selection_modes(self):
        self.selection_combo.blockSignals(True)
        self.selection_combo.clear()

        self.selection_combo.addItem(
            self.tr("All active members"), (SelectionKind.ALL_ACTIVE, None)
        )
        self.selection_combo.addItem(
            self.tr("All trainers"), (SelectionKind.ALL_TRAINERS, None)
        )
        self.selection_combo.addItem(
            self.tr("Minors only"), (SelectionKind.MINORS, None)
        )
        self.selection_combo.addItem(
            self.tr("Adults only"), (SelectionKind.ADULTS, None)
        )

        for session in sorted(self.sessions(), key=lambda s: s.name.casefold()):
            self.selection_combo.addItem(
                self.tr("Participants: {name}").format(name=session.name),
                (SelectionKind.PARTICIPANTS, session.id),
            )

        self.selection_combo.addItem(
            self.tr("Manual selection (start empty)"), (SelectionKind.MANUAL, None)
        )

        self.selection_combo.blockSignals(False)

    def __apply_selection(self, *_):
        data = self.selection_combo.currentData()
        if data is None:
            return

        kind, session_id = data
        as_of = self.as_of_input.date().toPython()
        # Exited (and not-yet-joined) members are never part of a list, so the
        # whole selectable universe is restricted to members active at the
        # reference date - they can't even be added by hand.
        selectable = active_members(self.members(), as_of)
        included = select_members(
            self.members(), kind, as_of, session_id=session_id
        )

        included_model = MemberModel(
            members=selectable, active=included, parent=self.included_table
        )
        self.included_table.setModel(included_model)
        self.__configure_member_table(self.included_table)

        available_proxy = GenericSortFilterProxyModel(
            sort_orders=_member_sort_orders(), parent=self.available_table
        )
        available_proxy.setSourceModel(
            MemberModel(
                members=selectable, inactive=included, parent=self.available_table
            )
        )
        self.available_table.setModel(available_proxy)
        self.available_filter.attach(available_proxy)
        self.__configure_member_table(self.available_table)

        included_model.rowsInserted.connect(self.__member_counts_changed)
        included_model.rowsRemoved.connect(self.__member_counts_changed)
        self.included_table.activated.connect(self.__included_activated)
        self.available_table.activated.connect(self.__available_activated)

        self.__member_counts_changed()
        if self.__built:
            self.validator.revalidate()

    def __configure_member_table(self, table):
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(
            MemberModel.Column.Age, QHeaderView.ResizeMode.ResizeToContents
        )

    def __member_counts_changed(self, *_):
        self.included_group.setTitle(
            self.tr("Included ({count})").format(
                count=_member_model(self.included_table).rowCount()
            )
        )
        self.available_group.setTitle(
            self.tr("Available ({count})").format(
                count=_member_model(self.available_table).rowCount()
            )
        )

    def __included_activated(self, idx):
        member = _member_at(self.included_table, idx)
        if member:
            _member_model(self.included_table).make_inactive(member)
            _member_model(self.available_table).make_active(member)

    def __available_activated(self, idx):
        member = _member_at(self.available_table, idx)
        if member:
            _member_model(self.available_table).make_inactive(member)
            _member_model(self.included_table).make_active(member)

    # --- column picker ---------------------------------------------------

    def __refresh_available_columns(self):
        present = {
            ColumnKind(self.chosen_columns.item(i).data(Qt.ItemDataRole.UserRole))
            for i in range(self.chosen_columns.count())
        }
        self.available_columns.clear()
        for kind in _AVAILABLE_COLUMN_ORDER:
            if kind in present:
                continue
            item = QListWidgetItem(self.__labels[kind])
            item.setData(Qt.ItemDataRole.UserRole, kind.value)
            self.available_columns.addItem(item)

    def __append_column(self, kind: ColumnKind):
        item = QListWidgetItem(self.__labels[kind])
        item.setData(Qt.ItemDataRole.UserRole, kind.value)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.chosen_columns.addItem(item)
        if kind not in REPEATABLE_KINDS:
            self.__refresh_available_columns()

    def __add_selected_columns(self):
        for item in self.available_columns.selectedItems():
            self.__append_column(ColumnKind(item.data(Qt.ItemDataRole.UserRole)))

    def __remove_selected_columns(self):
        for item in self.chosen_columns.selectedItems():
            self.chosen_columns.takeItem(self.chosen_columns.row(item))
        self.__refresh_available_columns()

    def __move_chosen(self, offset: int):
        row = self.chosen_columns.currentRow()
        if row < 0:
            return
        target = row + offset
        if target < 0 or target >= self.chosen_columns.count():
            return
        item = self.chosen_columns.takeItem(row)
        self.chosen_columns.insertItem(target, item)
        self.chosen_columns.setCurrentRow(target)

    def __chosen_specs(self) -> List[ColumnSpec]:
        specs = []
        for i in range(self.chosen_columns.count()):
            item = self.chosen_columns.item(i)
            kind = ColumnKind(item.data(Qt.ItemDataRole.UserRole))
            specs.append(ColumnSpec(kind=kind, header_label=item.text()))
        return specs

    def __set_chosen(self, specs: List[ColumnSpec]):
        self.chosen_columns.clear()
        for spec in specs:
            item = QListWidgetItem(
                spec.header_label
                if spec.header_label is not None
                else self.__labels[spec.kind]
            )
            item.setData(Qt.ItemDataRole.UserRole, spec.kind.value)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.chosen_columns.addItem(item)
        self.__refresh_available_columns()

    # --- templates -------------------------------------------------------

    def __load_templates(self):
        try:
            self.__templates = self.db().run_sync(load_column_templates)
        except Exception as exc:  # noqa: BLE001 - surfaced to the user
            self.__templates = []
            self.status_changed.emit(self.tr("Could not load templates"))
            QMessageBox.warning(
                self,
                self.tr("Templates"),
                self.tr("The column templates could not be loaded. Reason given:\n{error}").format(
                    error=exc
                ),
            )
        self.__reload_template_combo()

    def __reload_template_combo(self, select_name: Optional[str] = None):
        self.template_combo.blockSignals(True)
        self.template_combo.clear()
        self.template_combo.addItem(self.tr("(No template)"), None)
        for template in self.__templates:
            self.template_combo.addItem(template.name, template.name)
        if select_name is not None:
            idx = self.template_combo.findData(select_name)
            if idx >= 0:
                self.template_combo.setCurrentIndex(idx)
        self.template_combo.blockSignals(False)

    def __template_selected(self, *_):
        name = self.template_combo.currentData()
        if name is None:
            return
        template = next((t for t in self.__templates if t.name == name), None)
        if template is not None:
            self.__set_chosen(template.columns)

    def __save_template_as(self):
        name, ok = QInputDialog.getText(
            self, self.tr("Save template"), self.tr("Template name")
        )
        name = name.strip()
        if not ok or not name:
            return
        if not self.__chosen_specs():
            QMessageBox.warning(
                self,
                self.tr("Save template"),
                self.tr("Add at least one column before saving a template."),
            )
            return

        templates = [t for t in self.__templates if t.name != name]
        templates.append(ColumnTemplate(name=name, columns=self.__chosen_specs()))
        self.__persist_templates(
            templates, self.tr("Template '{name}' saved").format(name=name), name
        )

    def __update_template(self):
        name = self.template_combo.currentData()
        if name is None:
            QMessageBox.information(
                self,
                self.tr("Update template"),
                self.tr("Select a template to update first."),
            )
            return
        templates = [
            ColumnTemplate(name=name, columns=self.__chosen_specs())
            if t.name == name
            else t
            for t in self.__templates
        ]
        self.__persist_templates(
            templates, self.tr("Template '{name}' updated").format(name=name), name
        )

    def __delete_template(self):
        name = self.template_combo.currentData()
        if name is None:
            QMessageBox.information(
                self,
                self.tr("Delete template"),
                self.tr("Select a template to delete first."),
            )
            return

        answer = QMessageBox.question(
            self,
            self.tr("Delete template"),
            self.tr("Delete the template '{name}'?").format(name=name),
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        templates = [t for t in self.__templates if t.name != name]
        self.__persist_templates(
            templates, self.tr("Template '{name}' deleted").format(name=name), None
        )

    def __persist_templates(
        self,
        templates: List[ColumnTemplate],
        success_status: str,
        select_name: Optional[str],
    ):
        def task(session):
            assert session is not None
            # Staged like any other edit; it is persisted when the user commits
            # through the main menu, so nothing is committed here.
            save_column_templates(session, templates)

        def on_success(_):
            self.__templates = templates
            self.__reload_template_combo(select_name)
            self.status_changed.emit(success_status)

        def on_error(err):
            self.status_changed.emit(self.tr("Saving the template failed"))
            QMessageBox.critical(
                self,
                self.tr("Templates"),
                self.tr("The template could not be saved. Reason given:\n{error}").format(
                    error=err
                ),
            )

        self.db().submit(task, on_success=on_success, on_error=on_error)

    # --- generation ------------------------------------------------------

    def __format_changed(self, *_):
        is_pdf = self.format_combo.currentData() == "pdf"
        self.pdf_options_group.setEnabled(is_pdf)

    def __check_columns(self) -> Optional[Issue]:
        if self.chosen_columns.count() == 0:
            return error(self.tr("Add at least one column"))
        return None

    def __check_members(self) -> Optional[Issue]:
        if _member_model(self.included_table).rowCount() == 0:
            return error(self.tr("Select at least one member"))
        return None

    def __check_out_file(self) -> Optional[Issue]:
        path = self.out_file_input.path.strip()
        if len(path) == 0:
            return error(self.tr("Please choose where to save the list"))
        directory = os.path.dirname(path) or "."
        if not os.path.isdir(directory):
            return error(self.tr("The target directory doesn't exist"))
        if not os.access(directory, os.W_OK):
            return error(self.tr("You don't have permission to write there"))
        return None

    def __create(self):
        if not self.validator.validate():
            return

        specs = self.__chosen_specs()
        member_ids = [m.id for m in _member_model(self.included_table).get_members()]
        fmt = self.format_combo.currentData()
        as_of = self.as_of_input.date().toPython()
        out_path = self.out_file_input.path.strip()
        title = self.title_input.text().strip() or None
        landscape = self.orientation_combo.currentData() == "landscape"
        zebra = self.zebra_check.isChecked()

        self.config().member_list_dir = os.path.dirname(out_path) or "."

        self.__run(fmt, member_ids, specs, out_path, as_of, title, landscape, zebra)

    def __set_busy(self, busy: bool):
        self.create_button.setEnabled(not busy)
        self.back_button.setEnabled(not busy)
        self.busy_changed.emit(busy)

    def __start_progress(self):
        self.__progress_start = time.monotonic()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(True)
        self.progress_label.setText(self.tr("Preparing…"))
        self.progress_label.setVisible(True)

    def __stop_progress(self):
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)

    @Slot(int, int)
    def __on_progress(self, current: int, total: int):
        if self.progress_bar.maximum() != total:
            self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

        elapsed = time.monotonic() - self.__progress_start
        if current > 0 and elapsed > 0:
            rate = current / elapsed
            remaining = int((total - current) / rate) if rate > 0 else 0
            self.progress_label.setText(
                self.tr(
                    "{current} / {total} members · ~{seconds}s left ({rate}/s)"
                ).format(
                    current=current,
                    total=total,
                    seconds=remaining,
                    rate="{:.0f}".format(rate),
                )
            )
        else:
            self.progress_label.setText(
                self.tr("{current} / {total} members").format(
                    current=current, total=total
                )
            )

    def __run(
        self,
        fmt: str,
        member_ids: List[int],
        specs: List[ColumnSpec],
        out_path: str,
        as_of: datetime.date,
        title: Optional[str],
        landscape: bool,
        zebra: bool,
    ):
        self.__set_busy(True)
        self.__start_progress()
        self.status_changed.emit(self.tr("Creating list…"))

        last_emit = [0.0]

        def report_progress(current: int, total: int):
            now = time.monotonic()
            if current == total or now - last_emit[0] >= 0.1:
                last_emit[0] = now
                self.progress_updated.emit(current, total)

        def task(session):
            assert session is not None
            members = [session.get(Member, mid) for mid in member_ids]
            members = [m for m in members if m is not None]
            if fmt == "pdf":
                club_name = session.scalars(
                    select(Setting.value).where(Setting.name == Setting.CLUB_NAME)
                ).one_or_none()
                return render_member_list_pdf(
                    session,
                    members,
                    specs,
                    out_path,
                    as_of_date=as_of,
                    title=title,
                    club_name=club_name,
                    landscape=landscape,
                    zebra=zebra,
                    progress_callback=report_progress,
                )
            return render_member_list_csv(
                session,
                members,
                specs,
                out_path,
                as_of_date=as_of,
                progress_callback=report_progress,
            )

        def on_success(result: MemberListResult):
            self.__stop_progress()
            self.__set_busy(False)
            self.status_changed.emit(self.tr("List created"))
            self.__show_result(result)

        def on_error(err):
            self.__stop_progress()
            self.__set_busy(False)
            self.status_changed.emit(self.tr("Creating the list failed"))
            QMessageBox.critical(
                self,
                self.tr("Creating the list failed"),
                self.tr("The list could not be created. Reason given:\n{error}").format(
                    error=err
                ),
            )

        self.db().submit(task, on_success=on_success, on_error=on_error)

    def __show_result(self, result: MemberListResult):
        box = QMessageBox(self)
        box.setWindowTitle(self.tr("List created"))
        box.setIcon(QMessageBox.Icon.Information)
        box.setText(
            self.tr("The list with {count} members was saved to:\n{path}").format(
                count=result.member_count, path=result.output_path
            )
        )
        open_button = box.addButton(self.tr("Open file"), QMessageBox.ButtonRole.ActionRole)
        box.addButton(QMessageBox.StandardButton.Close)
        box.exec()
        if box.clickedButton() is open_button:
            QDesktopServices.openUrl(QUrl.fromLocalFile(result.output_path))


def _as_path(value: str):
    from pathlib import Path

    return Path(value)
