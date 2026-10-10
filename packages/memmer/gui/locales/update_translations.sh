#!/bin/bash
# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

# Extracts the GUI's translatable strings (the self.tr() calls in the Python
# sources and the strings in the Qt Designer .ui files) and merges them into
# the per-language memmer_*.ts sources loaded by the GUI's QTranslator. Run
# this after changing any GUI string, then compile_translations.sh to produce
# the .qm files. The member-facing texts are maintained separately (see
# ../../locales).

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
GUI_DIR=$( dirname -- "$SCRIPT_DIR" )

# Languages the GUI is translated into. English is the source language and
# needs no .ts file. Add a code here to start a new translation.
LANGUAGES=(de nb_NO ta)

# The compiled UI files are generated from the .ui files and would duplicate
# their strings, so only the hand-written sources and the .ui files are scanned.
SOURCES=( "$GUI_DIR"/*.py "$GUI_DIR"/ui_files/*.ui )

for lang in "${LANGUAGES[@]}"; do
	pyside6-lupdate \
		-no-obsolete \
		-locations relative \
		"${SOURCES[@]}" \
		-ts "$SCRIPT_DIR/memmer_$lang.ts"
done
