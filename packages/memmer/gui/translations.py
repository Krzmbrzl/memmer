# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

"""Installs the GUI's QTranslator(s) for the chosen (or system) language.

This governs the *GUI* language only. Member-facing output (e.g. the fee
summary written into a tally) is translated separately by
``memmer.member_text.MemberTranslator`` in the language stored in the
database, so the GUI language and the member-facing language are fully
independent."""

import os

from typing import List, Optional

from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator
from PySide6.QtCore import QCoreApplication

_LOCALES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "locales")

# Keep references to the installed translators: QApplication only holds weak
# ones, so a translator that goes out of scope would silently stop translating.
_installed: List[QTranslator] = []


def install_translators(
    app: QCoreApplication, locale: Optional[QLocale] = None
) -> QLocale:
    """Install the GUI translators on ``app`` and return the chosen locale.

    The locale defaults to the ``MEMMER_GUI_LANGUAGE`` environment variable (a
    locale code such as ``de`` or ``nb_NO``) if set, otherwise to the system
    locale. Call this *before* building any widgets, since Qt applies the
    installed translators when the widgets are created.

    English is the source language and has no ``.qm``; for it (and any language
    without a compiled translation) the untranslated source strings are used."""
    if locale is None:
        env_language = os.environ.get("MEMMER_GUI_LANGUAGE")
        locale = QLocale(env_language) if env_language else QLocale.system()

    # Qt's own strings (the standard dialog buttons, etc.) live in qtbase_*.qm,
    # shipped with Qt; load them so built-in widgets match the GUI language.
    qt_translator = QTranslator(app)
    if qt_translator.load(
        locale,
        "qtbase",
        "_",
        QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath),
    ):
        app.installTranslator(qt_translator)
        _installed.append(qt_translator)

    # Memmer's own GUI strings. QTranslator.load walks the locale's fallback
    # chain, so e.g. a "de_DE" locale still finds memmer_de.qm.
    app_translator = QTranslator(app)
    if app_translator.load(locale, "memmer", "_", _LOCALES_DIR):
        app.installTranslator(app_translator)
        _installed.append(app_translator)

    return locale
