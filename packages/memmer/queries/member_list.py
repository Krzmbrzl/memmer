# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

"""Renders a list of members as a table, either as a styled PDF or as CSV.

The two writers share the same column model, the same per-column value
extraction and the same ordering, so a PDF and a CSV built from the same
selection always contain the same rows in the same order. Only the base fee is
computed through the database (via :func:`compute_monthly_fee`); everything else
is read straight off the detached member objects.

Like :mod:`fee_summary`, this module stays free of any Qt dependency: the GUI
supplies the (translated) column headers through :class:`ColumnSpec`."""

from typing import Any, Callable, List, Optional, Sequence, Tuple

from dataclasses import dataclass
from enum import Enum

import csv
import datetime
import json

from sqlalchemy import select
from sqlalchemy.orm import Session as SqlSession

from memmer.orm import Member, Setting
from memmer.utils import nominal_year_diff, is_active

from .fees import compute_monthly_fee
from .fee_summary import _money


class ColumnKind(Enum):
    """A selectable column of a member list.

    ``EMPTY`` (a blank cell left for hand-written notes once printed) and
    ``CHECKBOX`` (a blank box to tick) carry no member data and may appear more
    than once in a list; every other kind refers to a single member attribute."""

    ROW_NUMBER = "row_number"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    BIRTHDAY = "birthday"
    AGE = "age"
    ADDRESS = "address"
    EMAIL = "email"
    PHONE = "phone"
    IBAN = "iban"
    MONTHLY_FEE = "monthly_fee"
    GENDER = "gender"
    ENTRY_DATE = "entry_date"
    EXIT_DATE = "exit_date"
    MEMBERSHIP_DURATION = "membership_duration"
    SESSIONS = "sessions"
    EMPTY = "empty"
    CHECKBOX = "checkbox"


# English fall-back headers, used when a ColumnSpec carries no explicit label
# (e.g. from the CLI or tests). The GUI always passes translated labels.
DEFAULT_LABELS = {
    ColumnKind.ROW_NUMBER: "No.",
    ColumnKind.FIRST_NAME: "First name",
    ColumnKind.LAST_NAME: "Last name",
    ColumnKind.BIRTHDAY: "Date of birth",
    ColumnKind.AGE: "Age",
    ColumnKind.ADDRESS: "Address",
    ColumnKind.EMAIL: "Email",
    ColumnKind.PHONE: "Phone",
    ColumnKind.IBAN: "IBAN",
    ColumnKind.MONTHLY_FEE: "Monthly fee",
    ColumnKind.GENDER: "Gender",
    ColumnKind.ENTRY_DATE: "Entry date",
    ColumnKind.EXIT_DATE: "Exit date",
    ColumnKind.MEMBERSHIP_DURATION: "Membership (years)",
    ColumnKind.SESSIONS: "Sessions",
    ColumnKind.EMPTY: "",
    ColumnKind.CHECKBOX: "",
}

# Columns that carry no member data and may therefore be selected repeatedly.
REPEATABLE_KINDS = frozenset({ColumnKind.EMPTY, ColumnKind.CHECKBOX})

@dataclass
class ColumnSpec:
    """One column of a member list: its kind and the header to print for it."""

    kind: ColumnKind
    header_label: Optional[str] = None

    def header(self) -> str:
        if self.header_label is not None:
            return self.header_label
        return DEFAULT_LABELS.get(self.kind, "")


@dataclass
class ColumnTemplate:
    """A named, reusable column selection."""

    name: str
    columns: List[ColumnSpec]


@dataclass
class MemberListResult:
    output_path: str
    member_count: int


class SelectionKind(Enum):
    """A way of picking which members a list should contain."""

    ALL_ACTIVE = "all_active"
    ALL_TRAINERS = "all_trainers"
    MINORS = "minors"
    ADULTS = "adults"
    PARTICIPANTS = "participants"  # participants of the session given by session_id
    MANUAL = "manual"  # no automatic members; the caller picks them by hand


# Members younger than this (in whole years) count as minors.
MINOR_MAX_AGE = 18


def select_members(
    members: Sequence[Member],
    kind: SelectionKind,
    as_of_date: datetime.date,
    *,
    session_id: Optional[int] = None,
) -> List[Member]:
    """The members matching ``kind`` at ``as_of_date``.

    The result is always restricted to members active at ``as_of_date`` -
    exited and not-yet-joined members are never selectable. ``PARTICIPANTS``
    needs a ``session_id``; ``MANUAL`` yields no members."""
    if kind == SelectionKind.MANUAL:
        return []

    result = []
    for member in members:
        if not is_active(member, as_of_date):
            continue
        if _selection_matches(member, kind, as_of_date, session_id):
            result.append(member)
    return result


def _selection_matches(
    member: Member,
    kind: SelectionKind,
    as_of_date: datetime.date,
    session_id: Optional[int],
) -> bool:
    if kind == SelectionKind.ALL_ACTIVE:
        return True
    if kind == SelectionKind.ALL_TRAINERS:
        return len(member.trained_sessions) > 0
    if kind == SelectionKind.MINORS:
        return nominal_year_diff(member.birthday, as_of_date) < MINOR_MAX_AGE
    if kind == SelectionKind.ADULTS:
        return nominal_year_diff(member.birthday, as_of_date) >= MINOR_MAX_AGE
    if kind == SelectionKind.PARTICIPANTS:
        return any(s.id == session_id for s in member.participating_sessions)
    return False


def format_address(member: Member) -> str:
    """The single-line address as required for the list's address column."""
    return "{} {} {} {}".format(
        member.street, member.street_number, member.postal_code, member.city
    )


def _format_date(value: Optional[datetime.date]) -> str:
    return value.isoformat() if value is not None else ""


def _cell(
    session: Optional[SqlSession],
    member: Member,
    kind: ColumnKind,
    as_of_date: datetime.date,
) -> Tuple[str, Tuple[int, Any]]:
    """The (display text, sort key) of one member's cell for the given column.

    The sort key is a ``(group, value)`` pair comparable within one column: a
    present value is group 0, an absent one group 1 (so blanks sort last), and
    ``value`` is numeric for numeric columns and a case-folded string
    otherwise. Columns that carry no member data yield a constant key, so they
    never influence the ordering."""
    if kind == ColumnKind.FIRST_NAME:
        return member.first_name, (0, member.first_name.casefold())
    if kind == ColumnKind.LAST_NAME:
        return member.last_name, (0, member.last_name.casefold())
    if kind == ColumnKind.BIRTHDAY:
        return _format_date(member.birthday), (0, member.birthday.isoformat())
    if kind == ColumnKind.AGE:
        age = nominal_year_diff(member.birthday, as_of_date)
        return str(age), (0, age)
    if kind == ColumnKind.ADDRESS:
        address = format_address(member)
        return address, (0, address.casefold())
    if kind == ColumnKind.EMAIL:
        value = member.email_address or ""
        return value, (0 if value else 1, value.casefold())
    if kind == ColumnKind.PHONE:
        value = member.phone_number or ""
        return value, (0 if value else 1, value.casefold())
    if kind == ColumnKind.IBAN:
        value = member.iban or ""
        return value, (0 if value else 1, value.casefold())
    if kind == ColumnKind.MONTHLY_FEE:
        assert session is not None
        fee = compute_monthly_fee(session, member, target_date=as_of_date)
        return _money(fee), (0, fee)
    if kind == ColumnKind.GENDER:
        value = member.gender.name
        return value, (0, value.casefold())
    if kind == ColumnKind.ENTRY_DATE:
        return _format_date(member.entry_date), (0, member.entry_date.isoformat())
    if kind == ColumnKind.EXIT_DATE:
        present = member.exit_date is not None
        return (
            _format_date(member.exit_date),
            (0 if present else 1, member.exit_date.isoformat() if present else ""),
        )
    if kind == ColumnKind.MEMBERSHIP_DURATION:
        years = nominal_year_diff(member.entry_date, as_of_date)
        return str(years), (0, years)
    if kind == ColumnKind.SESSIONS:
        names = sorted(s.name for s in member.participating_sessions)
        joined = ", ".join(names)
        return joined, (0, joined.casefold())
    # EMPTY, CHECKBOX and ROW_NUMBER have no member data. ROW_NUMBER's display
    # is filled in after sorting; the others stay blank.
    return "", (0, "")


def _ordered_rows(
    session: Optional[SqlSession],
    members: Sequence[Member],
    columns: Sequence[ColumnSpec],
    as_of_date: datetime.date,
    progress_callback: Optional[Callable[[int, int], None]],
) -> List[List[str]]:
    """Computes every cell once, sorts by the columns in order, then assigns
    row numbers. The (possibly expensive) fee lookup happens here, so progress
    is reported over it."""
    total = len(members)
    computed: List[Tuple[List[str], Tuple[Tuple[int, Any], ...]]] = []
    for index, member in enumerate(members):
        cells = [_cell(session, member, spec.kind, as_of_date) for spec in columns]
        displays = [display for display, _ in cells]
        key = tuple(sort_key for _, sort_key in cells)
        computed.append((displays, key))
        if progress_callback is not None:
            progress_callback(index + 1, total)

    computed.sort(key=lambda entry: entry[1])

    rows: List[List[str]] = []
    for position, (displays, _key) in enumerate(computed, start=1):
        row = list(displays)
        for col_index, spec in enumerate(columns):
            if spec.kind == ColumnKind.ROW_NUMBER:
                row[col_index] = str(position)
        rows.append(row)
    return rows


def render_member_list_csv(
    session: Optional[SqlSession],
    members: Sequence[Member],
    columns: Sequence[ColumnSpec],
    output_path: str,
    *,
    as_of_date: datetime.date,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> MemberListResult:
    rows = _ordered_rows(session, members, columns, as_of_date, progress_callback)

    with open(output_path, "w", newline="", encoding="utf-8") as out_file:
        writer = csv.writer(out_file)
        writer.writerow([spec.header() for spec in columns])
        writer.writerows(rows)

    return MemberListResult(output_path=output_path, member_count=len(members))


_pdf_fonts: Optional[Tuple[str, str]] = None


def _ensure_pdf_fonts() -> Tuple[str, str]:
    """Registers a Unicode font for the PDF and returns its (regular, bold)
    names.

    The built-in Helvetica only covers WinAnsi, so characters outside it (e.g.
    the ``ć`` in "Salićo") render as blanks. DejaVu Sans ships with matplotlib,
    already a dependency, and has broad Unicode coverage. If it can't be loaded
    for any reason, Helvetica is used as a last resort."""
    global _pdf_fonts
    if _pdf_fonts is not None:
        return _pdf_fonts

    fonts = ("Helvetica", "Helvetica-Bold")
    try:
        from pathlib import Path

        import matplotlib
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        ttf_dir = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
        pdfmetrics.registerFont(TTFont("DejaVuSans", str(ttf_dir / "DejaVuSans.ttf")))
        pdfmetrics.registerFont(
            TTFont("DejaVuSans-Bold", str(ttf_dir / "DejaVuSans-Bold.ttf"))
        )
        pdfmetrics.registerFontFamily(
            "DejaVuSans", normal="DejaVuSans", bold="DejaVuSans-Bold"
        )
        fonts = ("DejaVuSans", "DejaVuSans-Bold")
    except Exception:
        pass

    _pdf_fonts = fonts
    return _pdf_fonts


def _numbered_canvas_factory(
    page_width: float,
    page_height: float,
    margin: float,
    club_name: Optional[str] = None,
    club_font: str = "Helvetica-Bold",
):
    """A reportlab canvas that stamps a language-neutral ``x / y`` page footer
    on every page and the club name in the top-right corner of the first page.

    Total page count is only known once the whole document is laid out, so the
    pages are buffered and the overlays drawn in a second pass on save."""
    from reportlab.pdfgen import canvas

    class _NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__saved_states: List[dict] = []

        def showPage(self):
            self.__saved_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self.__saved_states)
            for state in self.__saved_states:
                self.__dict__.update(state)
                self.setFont("Helvetica", 8)
                self.drawRightString(
                    page_width - margin,
                    margin / 2,
                    "{} / {}".format(self._pageNumber, total),
                )
                if club_name and self._pageNumber == 1:
                    self.setFont(club_font, 9)
                    self.drawRightString(
                        page_width - margin, page_height - margin + 2, club_name
                    )
                super().showPage()
            super().save()

    return _NumberedCanvas


def render_member_list_pdf(
    session: Optional[SqlSession],
    members: Sequence[Member],
    columns: Sequence[ColumnSpec],
    output_path: str,
    *,
    as_of_date: datetime.date,
    title: Optional[str] = None,
    club_name: Optional[str] = None,
    landscape: bool = False,
    zebra: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> MemberListResult:
    # Imported lazily so that importing this module (and, through it, the GUI)
    # never hard-requires reportlab unless a PDF is actually produced.
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape as _landscape
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.graphics.shapes import Drawing, Rect
    from reportlab.platypus import (
        BaseDocTemplate,
        PageTemplate,
        Frame,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
    )

    rows = _ordered_rows(session, members, columns, as_of_date, progress_callback)

    page_size = _landscape(A4) if landscape else A4
    margin = 15 * mm

    doc = BaseDocTemplate(
        output_path,
        pagesize=page_size,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
    )
    # A zero-padding frame makes doc.width/doc.height the exact usable area, so
    # the column-width and last-page-fill math below is not thrown off by the
    # default 6pt frame padding (which otherwise overflows the page).
    doc.addPageTemplates(
        [
            PageTemplate(
                id="member_list",
                frames=[
                    Frame(
                        doc.leftMargin,
                        doc.bottomMargin,
                        doc.width,
                        doc.height,
                        leftPadding=0,
                        rightPadding=0,
                        topPadding=0,
                        bottomPadding=0,
                    )
                ],
            )
        ]
    )

    regular_font, bold_font = _ensure_pdf_fonts()

    header_style = ParagraphStyle(
        "MemberListHeader",
        fontName=bold_font,
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )
    cell_style = ParagraphStyle(
        "MemberListCell", fontName=regular_font, fontSize=8, leading=10
    )

    def checkbox() -> Drawing:
        size = 9
        drawing = Drawing(size, size)
        drawing.add(
            Rect(0, 0, size, size, strokeColor=colors.black, fillColor=None, strokeWidth=0.75)
        )
        return drawing

    col_widths = _column_widths(
        columns, rows, doc.width, header_style, cell_style, stringWidth, min_empty=30 * mm
    )

    base_padding = 2
    style = TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#33475b")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), base_padding),
            ("BOTTOMPADDING", (0, 0), (-1, -1), base_padding),
        ]
    )
    # With a notes column every body row carries a cell meant for hand-writing,
    # so make those rows at least twice a single line tall (the header stays
    # compact). Extra padding rather than a fixed height, so wrapped content is
    # never clipped.
    if any(spec.kind == ColumnKind.EMPTY for spec in columns):
        note_pad = _note_row_padding(cell_style.leading, base_padding)
        style.add("TOPPADDING", (0, 1), (-1, -1), note_pad)
        style.add("BOTTOMPADDING", (0, 1), (-1, -1), note_pad)
    if zebra:
        style.add(
            "ROWBACKGROUNDS",
            (0, 1),
            (-1, -1),
            [colors.white, colors.HexColor("#eef2f6")],
        )
    for col_index, spec in enumerate(columns):
        if spec.kind in (
            ColumnKind.ROW_NUMBER,
            ColumnKind.AGE,
            ColumnKind.CHECKBOX,
            ColumnKind.MEMBERSHIP_DURATION,
        ):
            style.add("ALIGN", (col_index, 0), (col_index, -1), "CENTER")
        elif spec.kind == ColumnKind.MONTHLY_FEE:
            style.add("ALIGN", (col_index, 0), (col_index, -1), "RIGHT")

    # Fresh flowables per call: a reportlab flowable keeps layout state once
    # wrapped, so the table built for measuring must not be reused for output.
    def header_cells() -> List[Any]:
        return [Paragraph(spec.header(), header_style) for spec in columns]

    def data_cells(row: List[str]) -> List[Any]:
        return [
            checkbox() if spec.kind == ColumnKind.CHECKBOX else Paragraph(value, cell_style)
            for spec, value in zip(columns, row)
        ]

    def blank_cells() -> List[Any]:
        # Empty cells to hand-write new members into; checkbox columns keep
        # their box so an added member can still be ticked.
        return [checkbox() if spec.kind == ColumnKind.CHECKBOX else "" for spec in columns]

    def build_table(blank_rows: int) -> Table:
        data: List[List[Any]] = [header_cells()]
        data.extend(data_cells(row) for row in rows)
        data.extend(blank_cells() for _ in range(blank_rows))
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(style)
        return table

    leading: List[Any] = []
    if title:
        leading.append(
            Paragraph(
                title,
                ParagraphStyle(
                    "MemberListTitle",
                    fontName=bold_font,
                    fontSize=15,
                    leading=18,
                ),
            )
        )
    leading.append(
        Paragraph(
            datetime.date.today().isoformat(),
            ParagraphStyle(
                "MemberListSubtitle", fontName=regular_font, fontSize=8, textColor=colors.grey
            ),
        )
    )
    leading.append(Spacer(1, 6))

    blank_rows = _blank_rows_for_last_page(
        build_table, leading, doc.width, doc.height
    )

    doc.build(
        leading + [build_table(blank_rows)],
        canvasmaker=_numbered_canvas_factory(
            page_size[0], page_size[1], margin, club_name, bold_font
        ),
    )

    return MemberListResult(output_path=output_path, member_count=len(members))


def _note_row_padding(leading: float, base_padding: float) -> float:
    """Per-side top/bottom cell padding that makes a single-line body row at
    least twice its normal height, giving note columns room to write in.

    A normal single line is ``leading + 2 * base_padding`` tall; doubling it
    means adding that same amount of padding, split evenly between top and
    bottom."""
    single_line = leading + 2 * base_padding
    return base_padding + single_line / 2


def _column_widths(
    columns, rows, available, header_style, cell_style, string_width, min_empty
):
    """Column widths that fit each column's longest content on one line.

    Data columns take the width of their widest cell (or header) so their text
    isn't broken; empty (notes) columns are never narrower than ``min_empty``
    and share whatever horizontal space is left. When the natural widths don't
    all fit, empty columns stay at their minimum and the data columns shrink
    proportionally (wrapping as needed)."""
    padding = 6.0  # left + right cell padding
    box = 9.0  # checkbox drawing width

    flex = [i for i, spec in enumerate(columns) if spec.kind == ColumnKind.EMPTY]

    natural = []
    for i, spec in enumerate(columns):
        header_w = string_width(
            spec.header(), header_style.fontName, header_style.fontSize
        )
        if spec.kind == ColumnKind.EMPTY:
            natural.append(max(min_empty, header_w + padding))
        elif spec.kind == ColumnKind.CHECKBOX:
            natural.append(max(header_w, box) + padding)
        else:
            content_w = max(
                (
                    string_width(row[i], cell_style.fontName, cell_style.fontSize)
                    for row in rows
                ),
                default=0.0,
            )
            natural.append(max(header_w, content_w) + padding)

    widths = list(natural)
    total = sum(natural)

    if total <= available:
        leftover = available - total
        if flex:
            # Empty columns soak up the remaining width equally.
            share = leftover / len(flex)
            for i in flex:
                widths[i] += share
        else:
            # No notes column to absorb slack: widen everything to span the
            # page (only ever grows a column, so nothing wraps).
            scale = available / total if total > 0 else 1.0
            widths = [w * scale for w in widths]
        return widths

    # Natural widths overflow the page: content must break somewhere, so pin
    # empties at their minimum and give the data columns a share of the rest in
    # proportion to their max-content widths (a wider column keeps a wider
    # share). ``widths[i]`` still holds the natural width here, so scaling it
    # keeps those relative proportions.
    empty_total = sum(natural[i] for i in flex)
    data_total = total - empty_total
    remaining = available - empty_total
    if remaining <= 0 or data_total <= 0:
        return [available / len(columns)] * len(columns)
    scale = remaining / data_total
    for i in range(len(columns)):
        if i not in flex:
            widths[i] *= scale
    return widths


def _blank_rows_for_last_page(build_table, leading, avail_width, page_height) -> int:
    """How many empty rows fill the remainder of the last page.

    The table is paginated by repeatedly splitting it against the height left on
    each page (less on the first, which also carries the title block). The gap
    between the last page's content and its bottom is then divided by one empty
    row's height."""
    leading_height = sum(f.wrap(avail_width, page_height)[1] for f in leading)
    first_height = page_height - leading_height
    rest_height = page_height

    # One body row's height, from the difference one extra blank row makes.
    height_no_blanks = build_table(0).wrap(avail_width, page_height)[1]
    height_one_blank = build_table(1).wrap(avail_width, page_height)[1]
    row_height = max(1.0, height_one_blank - height_no_blanks)

    pages = _split_into_pages(
        build_table(0), avail_width, first_height, rest_height
    )
    if not pages:
        return 0

    last = pages[-1]
    last_avail = first_height if len(pages) == 1 else rest_height
    free = last_avail - last.wrap(avail_width, last_avail)[1]
    # A small margin keeps rounding from pushing a blank row onto a new page.
    return max(0, int((free - 1.0) // row_height))


def _split_into_pages(table, avail_width, first_height, rest_height):
    pages = []
    avail = first_height
    remaining = table
    # Bounded so a degenerate split (a row taller than the page) can't loop.
    for _ in range(100000):
        if remaining is None:
            break
        remaining.wrap(avail_width, avail)
        parts = remaining.split(avail_width, avail)
        if len(parts) <= 1:
            pages.append(parts[0] if parts else remaining)
            remaining = None
        else:
            pages.append(parts[0])
            remaining = parts[1]
        avail = rest_height
    return pages


def load_column_templates(session: SqlSession) -> List[ColumnTemplate]:
    """Reads the shared column-selection templates from the settings table."""
    value = session.scalars(
        select(Setting.value).where(Setting.name == Setting.MEMBER_LIST_TEMPLATES)
    ).one_or_none()
    if not value:
        return []

    templates: List[ColumnTemplate] = []
    for entry in json.loads(value):
        columns = [
            ColumnSpec(
                kind=ColumnKind(column["kind"]),
                header_label=column.get("header_label"),
            )
            for column in entry["columns"]
        ]
        templates.append(ColumnTemplate(name=entry["name"], columns=columns))
    return templates


def save_column_templates(
    session: SqlSession, templates: Sequence[ColumnTemplate]
) -> None:
    """Writes the shared column-selection templates to the settings table.

    This does not commit; the change is staged in the session and persisted by
    the caller's usual commit flow, like any other edit."""
    payload = json.dumps(
        [
            {
                "name": template.name,
                "columns": [
                    {"kind": column.kind.value, "header_label": column.header_label}
                    for column in template.columns
                ],
            }
            for template in templates
        ]
    )

    setting = session.get(Setting, Setting.MEMBER_LIST_TEMPLATES)
    if setting is None:
        session.add(Setting(name=Setting.MEMBER_LIST_TEMPLATES, value=payload))
    else:
        setting.value = payload
