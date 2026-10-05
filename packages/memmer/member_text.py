# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

"""Translation of member-facing generated text (e.g. the fee summary written
into a tally), in a language chosen independently of the GUI language.

The GUI translates its own strings through the installed ``QTranslator``,
which serves a single language. Member-facing output must be able to use a
different language, so this module keeps a *dedicated* ``QTranslator`` per
requested language and queries it directly, leaving the GUI's translation
untouched."""

import os

from PySide6.QtCore import QTranslator

# Translation context shared with the hand-maintained locales/member_*.ts files.
CONTEXT = "MemberText"

_LOCALES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "locales")


class MemberTranslator:
    """Translates member-facing labels into a single configured language.

    Instances are cheap and self-contained; create and use one on whichever
    thread produces the text. English is treated as the source language, so no
    ``.qm`` is needed for it and any label without a translation falls back to
    its (English) source."""

    def __init__(self, language: str):
        self.language = language
        self.__translator = QTranslator()
        self.__loaded = False

        # English is the source language; everything else needs a compiled .qm.
        if language and not language.startswith("en"):
            self.__loaded = self.__translator.load(
                os.path.join(_LOCALES_DIR, "member_{}.qm".format(language))
            )

    def translate(self, source: str) -> str:
        if self.__loaded:
            translated = self.__translator.translate(CONTEXT, source)
            if translated:
                return translated
        return source
