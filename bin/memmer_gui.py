#!/usr/bin/env python3

# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "packages"))

from memmer.gui import MemmerGUI


def main():
    gui = MemmerGUI()

    gui.show_and_execute()


if __name__ == "__main__":
    main()
