#!/usr/bin/env python3

# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

import csv
import datetime
import os
import re
import tempfile
import unittest
from decimal import Decimal

import sqlalchemy
import sqlalchemy.orm

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth

from memmer.orm import Base, Member, Gender, Session, FixedCost, Setting
from memmer import BasicFeeAdultsKey
from memmer.queries import (
    ColumnKind,
    ColumnSpec,
    ColumnTemplate,
    SelectionKind,
    format_address,
    select_members,
    render_member_list_csv,
    render_member_list_pdf,
    load_column_templates,
    save_column_templates,
)
from memmer.queries.member_list import _column_widths, _note_row_padding
from memmer.utils import active_members


_HEADER_STYLE = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=8)
_CELL_STYLE = ParagraphStyle("c", fontName="Helvetica", fontSize=8)
_AVAIL = A4[0] - 30 * mm
_MIN_EMPTY = 30 * mm


def _widths(columns, rows):
    return _column_widths(
        columns, rows, _AVAIL, _HEADER_STYLE, _CELL_STYLE, stringWidth, _MIN_EMPTY
    )


def _pdf_page_count(path) -> int:
    with open(path, "rb") as pdf_file:
        data = pdf_file.read()
    return len(re.findall(rb"/Type\s*/Page(?![s])", data))


AS_OF = datetime.date(2026, 1, 1)


def _member(**overrides) -> Member:
    defaults = dict(
        first_name="John",
        last_name="Doe",
        birthday=datetime.date(1990, 6, 15),
        gender=Gender.Male,
        street="Main Street",
        street_number="1",
        postal_code="70173",
        city="Stuttgart",
        entry_date=datetime.date(2010, 1, 1),
    )
    defaults.update(overrides)
    return Member(**defaults)


class TestMemberList(unittest.TestCase):
    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)

        with self.Session() as session:
            session.add_all(
                [
                    _member(
                        first_name="Bob", last_name="Smith", city="Berlin",
                        birthday=datetime.date(2000, 3, 1),
                    ),
                    _member(
                        first_name="Alice", last_name="Smith", city="Aachen",
                        birthday=datetime.date(1985, 12, 24),
                    ),
                    _member(
                        first_name="Carol", last_name="Adams", city="Cologne",
                        birthday=datetime.date(1995, 7, 7),
                    ),
                ]
            )
            session.add(FixedCost(name=BasicFeeAdultsKey, cost=Decimal(5)))
            session.commit()

    def _members(self, session):
        return list(
            session.scalars(sqlalchemy.select(Member).order_by(Member.id.asc())).all()
        )

    def test_sorting_by_columns_with_tie_breaks(self):
        columns = [
            ColumnSpec(ColumnKind.LAST_NAME),
            ColumnSpec(ColumnKind.FIRST_NAME),
        ]
        with self.Session() as session:
            rows = _ordered_display(session, self._members(session), columns)

        # Sorted by last name, then first name.
        self.assertEqual(
            rows,
            [["Adams", "Carol"], ["Smith", "Alice"], ["Smith", "Bob"]],
        )

    def test_cell_values(self):
        columns = [
            ColumnSpec(ColumnKind.FIRST_NAME),
            ColumnSpec(ColumnKind.ADDRESS),
            ColumnSpec(ColumnKind.AGE),
            ColumnSpec(ColumnKind.BIRTHDAY),
            ColumnSpec(ColumnKind.MONTHLY_FEE),
        ]
        with self.Session() as session:
            members = self._members(session)
            alice = next(m for m in members if m.first_name == "Alice")
            rows = _ordered_display(session, [alice], columns)

        self.assertEqual(
            rows,
            [
                [
                    "Alice",
                    "Main Street 1 70173 Aachen",
                    "40",
                    "1985-12-24",
                    "5€",
                ]
            ],
        )

    def test_repeated_empty_columns(self):
        columns = [
            ColumnSpec(ColumnKind.LAST_NAME),
            ColumnSpec(ColumnKind.EMPTY, header_label="Signature"),
            ColumnSpec(ColumnKind.EMPTY, header_label="Paid"),
        ]
        with self.Session() as session:
            members = self._members(session)
            path = os.path.join(self.tmp(), "list.csv")
            render_member_list_csv(
                session, members, columns, path, as_of_date=AS_OF
            )
            with open(path, newline="", encoding="utf-8") as f:
                data = list(csv.reader(f))

        self.assertEqual(data[0], ["Last name", "Signature", "Paid"])
        # Every data row has the two trailing empty cells.
        for row in data[1:]:
            self.assertEqual(row[1:], ["", ""])

    def test_csv_row_count_and_order(self):
        columns = [ColumnSpec(ColumnKind.ROW_NUMBER), ColumnSpec(ColumnKind.LAST_NAME)]
        with self.Session() as session:
            members = self._members(session)
            path = os.path.join(self.tmp(), "list.csv")
            render_member_list_csv(session, members, columns, path, as_of_date=AS_OF)
            with open(path, newline="", encoding="utf-8") as f:
                data = list(csv.reader(f))

        self.assertEqual(len(data), 1 + 3)  # header + 3 members
        self.assertEqual([row[0] for row in data[1:]], ["1", "2", "3"])
        self.assertEqual([row[1] for row in data[1:]], ["Adams", "Smith", "Smith"])

    def test_pdf_is_written(self):
        columns = [
            ColumnSpec(ColumnKind.LAST_NAME),
            ColumnSpec(ColumnKind.CHECKBOX, header_label="Here"),
        ]
        with self.Session() as session:
            members = self._members(session)
            path = os.path.join(self.tmp(), "list.pdf")
            result = render_member_list_pdf(
                session, members, columns, path, as_of_date=AS_OF, title="Members"
            )

        self.assertEqual(result.member_count, 3)
        self.assertTrue(os.path.getsize(path) > 0)
        with open(path, "rb") as f:
            self.assertTrue(f.read(5).startswith(b"%PDF"))

    def test_template_round_trip(self):
        templates = [
            ColumnTemplate(
                name="Attendance",
                columns=[
                    ColumnSpec(ColumnKind.LAST_NAME, header_label="Nachname"),
                    ColumnSpec(ColumnKind.EMPTY, header_label=""),
                ],
            )
        ]
        with self.Session() as session:
            save_column_templates(session, templates)
            session.commit()

        with self.Session() as session:
            loaded = load_column_templates(session)

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].name, "Attendance")
        self.assertEqual(loaded[0].columns[0].kind, ColumnKind.LAST_NAME)
        self.assertEqual(loaded[0].columns[0].header_label, "Nachname")
        self.assertEqual(loaded[0].columns[1].kind, ColumnKind.EMPTY)

    def test_widths_empty_columns_absorb_slack(self):
        columns = [
            ColumnSpec(ColumnKind.LAST_NAME, "Last name"),
            ColumnSpec(ColumnKind.ADDRESS, "Address"),
            ColumnSpec(ColumnKind.EMPTY, "Signature"),
            ColumnSpec(ColumnKind.EMPTY, "Notes"),
        ]
        rows = [
            ["Smith", "Short St 1 70173 City", "", ""],
            ["Doe", "A considerably longer street address 99 12345 Town", "", ""],
        ]
        widths = _widths(columns, rows)

        # Sized to content: the address column is wider than the last-name one.
        self.assertGreater(widths[1], widths[0])
        # Empty columns never fall below the minimum and share the slack equally.
        self.assertGreaterEqual(widths[2], _MIN_EMPTY - 0.01)
        self.assertGreaterEqual(widths[3], _MIN_EMPTY - 0.01)
        self.assertAlmostEqual(widths[2], widths[3], places=2)
        # The table spans the full page.
        self.assertAlmostEqual(sum(widths), _AVAIL, places=1)

    def test_widths_overflow_scale_to_max_widths(self):
        columns = [
            ColumnSpec(ColumnKind.IBAN, "IBAN"),
            ColumnSpec(ColumnKind.EMAIL, "Email"),
            ColumnSpec(ColumnKind.ADDRESS, "Address"),
        ]
        rows = [
            [
                "DE" + "1" * 60,
                "someone.with.a.very.long.email.address@example-domain.org",
                "A very long street address 12345 Some Very Long City Name Indeed",
            ]
        ]
        widths = _widths(columns, rows)

        self.assertAlmostEqual(sum(widths), _AVAIL, places=1)
        # Widths stay in proportion to each column's longest content.
        natural = [stringWidth(v, "Helvetica", 8) for v in rows[0]]
        for i in range(len(columns)):
            self.assertAlmostEqual(
                widths[i] / sum(widths), natural[i] / sum(natural), places=2
            )

    def test_last_page_blank_fill_stays_on_one_page(self):
        columns = [
            ColumnSpec(ColumnKind.ROW_NUMBER, "No."),
            ColumnSpec(ColumnKind.LAST_NAME, "Last name"),
            ColumnSpec(ColumnKind.EMPTY, "Notes"),
        ]
        with self.Session() as session:
            members = self._members(session)
            path = os.path.join(self.tmp(), "fill.pdf")
            render_member_list_pdf(
                session, members, columns, path, as_of_date=AS_OF, title="X"
            )
        # A short list plus its page-filling blank rows must not spill onto a
        # second, near-empty page.
        self.assertEqual(_pdf_page_count(path), 1)

    def test_club_name_only_on_first_page(self):
        from io import BytesIO
        from memmer.queries.member_list import _numbered_canvas_factory

        calls = []
        maker = _numbered_canvas_factory(
            595.0, 842.0, 42.0, club_name="My Club", club_font="Helvetica-Bold"
        )

        class Spy(maker):
            def drawRightString(self, x, y, text, *args, **kwargs):
                calls.append((round(y), text))
                return super().drawRightString(x, y, text, *args, **kwargs)

        spy = Spy(BytesIO())
        spy.showPage()  # page 1
        spy.showPage()  # page 2
        spy.save()

        club = [(y, text) for y, text in calls if text == "My Club"]
        self.assertEqual(len(club), 1)  # first page only
        self.assertGreater(club[0][0], 700)  # near the top of the page
        page_numbers = [text for _, text in calls if "/" in text]
        self.assertEqual(page_numbers, ["1 / 2", "2 / 2"])  # footer on every page

    def test_pdf_embeds_unicode_font(self):
        columns = [ColumnSpec(ColumnKind.LAST_NAME, "Last name")]
        with self.Session() as session:
            member = self._members(session)[0]
            member.last_name = "Salićo"  # outside WinAnsi -> needs a Unicode font
            path = os.path.join(self.tmp(), "unicode.pdf")
            render_member_list_pdf(
                session, [member], columns, path, as_of_date=AS_OF
            )
        with open(path, "rb") as pdf_file:
            data = pdf_file.read()
        # The Unicode font is embedded rather than falling back to Helvetica.
        self.assertIn(b"DejaVuSans", data)

    def test_note_row_padding_at_least_doubles_height(self):
        leading, base = 10.0, 2.0
        pad = _note_row_padding(leading, base)
        single_line = leading + 2 * base
        self.assertGreaterEqual(leading + 2 * pad, 2 * single_line)

    def test_notes_column_makes_rows_taller(self):
        plain = [
            ColumnSpec(ColumnKind.LAST_NAME, "Last name"),
            ColumnSpec(ColumnKind.FIRST_NAME, "First name"),
        ]
        with_notes = [
            ColumnSpec(ColumnKind.LAST_NAME, "Last name"),
            ColumnSpec(ColumnKind.EMPTY, "Notes"),
        ]
        with self.Session() as session:
            # Enough members that the taller note rows force an extra page.
            for i in range(30):
                session.add(
                    _member(first_name=f"F{i}", last_name=f"L{i:02d}", city="C")
                )
            session.commit()
            members = list(
                session.scalars(sqlalchemy.select(Member)).all()
            )
            plain_path = os.path.join(self.tmp(), "plain.pdf")
            notes_path = os.path.join(self.tmp(), "notes.pdf")
            render_member_list_pdf(session, members, plain, plain_path, as_of_date=AS_OF)
            render_member_list_pdf(
                session, members, with_notes, notes_path, as_of_date=AS_OF
            )

        # Taller note rows mean fewer rows per page, hence more pages.
        self.assertGreater(_pdf_page_count(notes_path), _pdf_page_count(plain_path))

    def test_select_members_modes_and_activity(self):
        def mk(first, age=30, entry=2010, exit_date=None, sessions=(), trained=()):
            member = _member(
                first_name=first,
                birthday=datetime.date(AS_OF.year - age, 1, 1),
                entry_date=datetime.date(entry, 1, 1),
                exit_date=exit_date,
            )
            member.participating_sessions = list(sessions)
            member.trained_sessions = list(trained)
            return member

        latein = Session(name="Latein")
        latein.id = 1
        hiphop = Session(name="Hip Hop")
        hiphop.id = 2

        adult = mk("Adult", age=40, sessions=[latein])
        minor = mk("Minor", age=10, sessions=[latein])
        trainer = mk("Trainer", age=50, trained=[hiphop])
        exited = mk("Exited", age=40, exit_date=datetime.date(2020, 1, 1), sessions=[latein])
        future = mk("Future", age=40, entry=2099)
        members = [adult, minor, trainer, exited, future]

        def names(result):
            return sorted(m.first_name for m in result)

        # The active universe excludes exited and not-yet-joined members.
        self.assertEqual(names(active_members(members, AS_OF)), ["Adult", "Minor", "Trainer"])
        self.assertEqual(
            names(select_members(members, SelectionKind.ALL_ACTIVE, AS_OF)),
            ["Adult", "Minor", "Trainer"],
        )
        self.assertEqual(
            names(select_members(members, SelectionKind.MINORS, AS_OF)), ["Minor"]
        )
        self.assertEqual(
            names(select_members(members, SelectionKind.ADULTS, AS_OF)),
            ["Adult", "Trainer"],
        )
        self.assertEqual(
            names(select_members(members, SelectionKind.ALL_TRAINERS, AS_OF)),
            ["Trainer"],
        )
        self.assertEqual(
            names(
                select_members(
                    members, SelectionKind.PARTICIPANTS, AS_OF, session_id=1
                )
            ),
            ["Adult", "Minor"],  # the exited participant is excluded
        )
        self.assertEqual(select_members(members, SelectionKind.MANUAL, AS_OF), [])

    def test_format_address(self):
        with self.Session() as session:
            member = self._members(session)[0]
            self.assertEqual(
                format_address(member),
                "{} {} {} {}".format(
                    member.street,
                    member.street_number,
                    member.postal_code,
                    member.city,
                ),
            )

    def tmp(self) -> str:
        if not hasattr(self, "_tmp"):
            self._tmp = tempfile.mkdtemp()
        return self._tmp


def _ordered_display(session, members, columns):
    """Writes a CSV and reads the data rows back, so tests assert on the exact
    ordering and cell text the writers produce."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "list.csv")
        render_member_list_csv(session, members, columns, path, as_of_date=AS_OF)
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
    return rows[1:]


if __name__ == "__main__":
    unittest.main()
