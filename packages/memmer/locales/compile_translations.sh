#!/bin/bash
# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

# Compiles the hand-maintained member-facing translation sources (member_*.ts)
# into the .qm files loaded by memmer.member_text.MemberTranslator. The .ts
# files are edited by hand (the labels are few), so only lrelease is run here.

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

for current in "$SCRIPT_DIR/"member_*.ts; do
	pyside6-lrelease "$current" -qm "${current%.ts}.qm"
done
