#!/bin/bash
# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

# Compiles the GUI translation sources (memmer_*.ts, kept up to date by
# update_translations.sh and the translators) into the .qm files that the
# GUI's QTranslator loads at startup.

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

for current in "$SCRIPT_DIR/"memmer_*.ts; do
	pyside6-lrelease "$current" -qm "${current%.ts}.qm"
done
