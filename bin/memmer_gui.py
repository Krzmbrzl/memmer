#!/usr/bin/env python3

# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from memmer.gui import MemmerGUI


def main():
    gui = MemmerGUI()

    gui.show_and_execute()


if __name__ == "__main__":
    main()
