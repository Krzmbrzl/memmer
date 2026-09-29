# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Callable, Optional, List, Tuple, Dict
from dataclasses import dataclass, field
from enum import Enum, auto

from PySide6.QtCore import QObject, QEvent, Qt, SignalInstance
import shiboken6
from PySide6.QtGui import QColor, QPainter, QPen, QIcon
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLayout,
    QBoxLayout,
    QFormLayout,
    QTabWidget,
    QStackedWidget,
    QScrollArea,
    QAbstractButton,
    QLineEdit,
    QAbstractSpinBox,
    QDateEdit,
    QDoubleSpinBox,
    QSpinBox,
    QComboBox,
    QCheckBox,
    QStyle,
)


class Severity(Enum):
    Error = auto()
    # Warnings are displayed but don't block saving
    Warning = auto()


@dataclass
class Issue:
    severity: Severity
    message: str


def error(message: str) -> Issue:
    return Issue(Severity.Error, message)


def warning(message: str) -> Issue:
    return Issue(Severity.Warning, message)


_colors = {
    Severity.Error: QColor("#d32f2f"),
    Severity.Warning: QColor("#c77700"),
}


class _Outline(QWidget):
    """Frame painted around a widget, independent of the active style"""

    def __init__(self, target: QWidget):
        super().__init__(target.parentWidget())

        self.target = target
        self.color: Optional[QColor] = None

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.hide()

        target.installEventFilter(self)

    def set_color(self, color: Optional[QColor]):
        self.color = color
        self.__sync()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() in (
            QEvent.Type.Move,
            QEvent.Type.Resize,
            QEvent.Type.Show,
            QEvent.Type.Hide,
        ):
            self.__sync()

        return False

    def __sync(self):
        if self.color is None or not self.target.isVisible():
            self.hide()
            return

        self.setGeometry(self.target.geometry().adjusted(-2, -2, 2, 2))
        self.show()
        self.raise_()
        self.update()

    def paintEvent(self, event):
        if self.color is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self.color, 2))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 3, 3)


@dataclass
class _Check:
    fn: Callable[[], Optional[Issue]]
    widgets: List[QWidget]
    outlines: List[_Outline]
    message_label: QLabel
    message_row: Optional[Tuple[QFormLayout, QWidget]]
    revealed: bool = False
    issue: Optional[Issue] = None
    tooltips: Dict[int, str] = field(default_factory=dict)


def _layout_contains(layout: QLayout, widget: QWidget) -> bool:
    if layout.indexOf(widget) >= 0:
        return True

    for i in range(layout.count()):
        item = layout.itemAt(i)
        child = item.layout() if item is not None else None
        if child is not None and _layout_contains(child, widget):
            return True

    return False


def _is_vertical(layout: QLayout) -> bool:
    return isinstance(layout, QBoxLayout) and layout.direction() in (
        QBoxLayout.Direction.TopToBottom,
        QBoxLayout.Direction.BottomToTop,
    )


def _vertical_slot(
    layout: QLayout, widget: QWidget
) -> Optional[Tuple[QBoxLayout, int]]:
    """Finds the innermost vertical box layout and the index of its item holding widget"""
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item is None:
            continue

        child = item.layout()
        if child is not None:
            inner = _vertical_slot(child, widget)
            if inner is not None:
                return inner
            holds_widget = _layout_contains(child, widget)
        else:
            holds_widget = item.widget() is widget

        if holds_widget and _is_vertical(layout):
            assert isinstance(layout, QBoxLayout)
            return (layout, i)

    return None


def _ancestors(widget: QWidget):
    current: Optional[QWidget] = widget
    while current is not None:
        yield current
        current = current.parentWidget()


def _default_reveal_signals(widget: QWidget) -> List[SignalInstance]:
    if isinstance(widget, QLineEdit):
        return [widget.editingFinished]
    if isinstance(widget, QDateEdit):
        return [widget.dateChanged]
    if isinstance(widget, (QDoubleSpinBox, QSpinBox)):
        return [widget.valueChanged]
    if isinstance(widget, QAbstractSpinBox):
        return [widget.editingFinished]
    if isinstance(widget, QComboBox):
        return [widget.currentIndexChanged]
    if isinstance(widget, QCheckBox):
        return [widget.toggled]
    if hasattr(widget, "pathChanged"):
        return [getattr(widget, "pathChanged")]

    return []


def _default_change_signals(widget: QWidget) -> List[SignalInstance]:
    if isinstance(widget, QLineEdit):
        return [widget.textChanged]

    return []


class FormValidator(QObject):
    """Runs input checks and displays their results next to the respective widgets

    Problems are only shown once the user has finished editing the respective input
    (or tried to save), so that a fresh form isn't covered in errors.
    """

    def __init__(self, owner: QWidget, action_button: QAbstractButton):
        super().__init__(owner)

        self.owner = owner
        self.action_button = action_button
        self.checks: List[_Check] = []
        self.save_attempted = False
        self.tab_tooltips: Dict[Tuple[int, int], str] = {}

        self.summary_label = QLabel(owner)
        self.summary_label.setStyleSheet(
            f"color: {_colors[Severity.Error].name()}; font-weight: bold;"
        )
        self.summary_label.hide()

        for box in owner.findChildren(QBoxLayout):
            if box.indexOf(action_button) >= 0:
                box.insertWidget(0, self.summary_label, 1)
                break

    def add_check(
        self,
        check: Callable[[], Optional[Issue]],
        widgets: List[QWidget],
        triggers: Optional[List[SignalInstance]] = None,
        reveal_on: Optional[List[SignalInstance]] = None,
    ):
        """Registers a check

        check: returns the problem with the current input (if any)
        widgets: the widgets to highlight on failure. The first one is used to place the
          message and to jump to when saving fails.
        triggers: signals (besides reveal_on) after which to re-run the check, e.g.
          changes of other inputs the check depends on. Changes of the widgets'
          text are always included.
        reveal_on: signals indicating that the user is done editing the input. Defaults
          to a sensible signal of each widget.
        """
        assert len(widgets) > 0

        label = QLabel(self.owner)
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.PlainText)
        label.hide()

        entry = _Check(
            fn=check,
            widgets=widgets,
            outlines=[_Outline(w) for w in widgets],
            message_label=label,
            message_row=self.__place_message_label(widgets[0], label),
        )
        self.checks.append(entry)

        if reveal_on is None:
            reveal_on = [s for w in widgets for s in _default_reveal_signals(w)]

        for signal in reveal_on:
            signal.connect(lambda *_, entry=entry: self.__reveal(entry))
        triggers = (triggers or []) + [
            s for w in widgets for s in _default_change_signals(w)
        ]
        for signal in triggers:
            signal.connect(lambda *_, entry=entry: self.__run(entry))

    def revalidate(self):
        for entry in self.checks:
            self.__run(entry, update_summary=False)

        self.__update_summary()

    def reveal_all(self):
        for entry in self.checks:
            entry.revealed = True

        self.revalidate()

    def validate(self) -> bool:
        """Shows all problems and returns whether there are no errors

        On failure, the first erroneous input receives focus.
        """
        self.save_attempted = True
        self.reveal_all()

        failed = [x for x in self.checks if self.__is_error(x)]
        if len(failed) == 0:
            return True

        self.__focus(failed[0].widgets[0])

        return False

    def __is_error(self, entry: _Check) -> bool:
        return entry.issue is not None and entry.issue.severity == Severity.Error

    def __reveal(self, entry: _Check):
        entry.revealed = True
        self.__run(entry)

    def __run(self, entry: _Check, update_summary: bool = True):
        if not shiboken6.isValid(self.owner):
            # Signals emitted while the form is being destroyed
            return

        entry.issue = entry.fn()

        shown = entry.issue if entry.revealed else None

        for widget, outline in zip(entry.widgets, entry.outlines):
            outline.set_color(_colors[shown.severity] if shown else None)

            widget.setProperty(
                "validation",
                "" if shown is None else shown.severity.name.lower(),
            )

            if shown is not None:
                entry.tooltips.setdefault(id(widget), widget.toolTip())
                widget.setToolTip(shown.message)
            elif id(widget) in entry.tooltips:
                widget.setToolTip(entry.tooltips.pop(id(widget)))

        label = entry.message_label
        if shown is not None:
            prefix = "⚠ " if shown.severity == Severity.Error else "ⓘ "
            label.setText(prefix + shown.message)
            label.setStyleSheet(f"color: {_colors[shown.severity].name()};")

        if entry.message_row is not None:
            form, _ = entry.message_row
            form.setRowVisible(label, shown is not None)
        else:
            label.setVisible(shown is not None)

        if update_summary:
            self.__update_summary()

    def __update_summary(self):
        errors = [x for x in self.checks if x.revealed and self.__is_error(x)]

        self.__update_tabs(errors)

        if not self.save_attempted or len(errors) == 0:
            self.summary_label.hide()
            return

        if len(errors) == 1:
            text = self.tr("1 input needs fixing")
        else:
            text = self.tr("{count} inputs need fixing").format(count=len(errors))

        self.summary_label.setText("⚠ " + text)
        self.summary_label.show()

    def __update_tabs(self, errors: List[_Check]):
        erroneous_tabs = set()
        for entry in errors:
            for tabs, idx in self.__enclosing_tabs(entry.widgets[0]):
                erroneous_tabs.add((id(tabs), idx))

        icon = self.owner.style().standardIcon(
            QStyle.StandardPixmap.SP_MessageBoxWarning
        )

        for tabs in self.owner.findChildren(QTabWidget):
            for idx in range(tabs.count()):
                key = (id(tabs), idx)
                if key in erroneous_tabs:
                    self.tab_tooltips.setdefault(key, tabs.tabToolTip(idx))
                    tabs.setTabIcon(idx, icon)
                    tabs.setTabToolTip(idx, self.tr("Contains invalid input"))
                elif key in self.tab_tooltips:
                    tabs.setTabIcon(idx, QIcon())
                    tabs.setTabToolTip(idx, self.tab_tooltips.pop(key))

    def __enclosing_tabs(self, widget: QWidget) -> List[Tuple[QTabWidget, int]]:
        result = []
        for ancestor in _ancestors(widget):
            stack = ancestor.parentWidget()
            if isinstance(stack, QStackedWidget) and isinstance(
                stack.parentWidget(), QTabWidget
            ):
                tabs = stack.parentWidget()
                assert isinstance(tabs, QTabWidget)
                result.append((tabs, tabs.indexOf(ancestor)))

        return result

    def __focus(self, widget: QWidget):
        # Outermost tab first so that nested pages become visible
        for tabs, idx in reversed(self.__enclosing_tabs(widget)):
            tabs.setCurrentIndex(idx)

        for ancestor in _ancestors(widget):
            if isinstance(ancestor, QScrollArea):
                ancestor.ensureWidgetVisible(widget)
                break

        widget.setFocus(Qt.FocusReason.OtherFocusReason)

    def __place_message_label(
        self, anchor: QWidget, label: QLabel
    ) -> Optional[Tuple[QFormLayout, QWidget]]:
        """Puts the label below the anchor. Form layouts get a dedicated row."""
        forms = self.owner.findChildren(QFormLayout)

        for ancestor in _ancestors(anchor):
            parent = ancestor.parentWidget()
            if ancestor is self.owner or parent is None:
                break

            for form in forms:
                for row in range(form.rowCount()):
                    item = form.itemAt(row, QFormLayout.ItemRole.FieldRole)
                    if item is None:
                        continue
                    sub_layout = item.layout()
                    if item.widget() is ancestor or (
                        sub_layout is not None
                        and _layout_contains(sub_layout, ancestor)
                    ):
                        form.insertRow(row + 1, "", label)
                        form.setRowVisible(label, False)
                        return (form, label)

            top_layout = parent.layout()
            slot = _vertical_slot(top_layout, ancestor) if top_layout else None
            if slot is not None:
                box, idx = slot
                box.insertWidget(idx + 1, label)
                return None

        return None
