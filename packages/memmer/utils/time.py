# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

import datetime


def nominal_year_diff(first: datetime.date, second: datetime.date) -> int:
    """Computes how many years lie between the first and second date (nominally)"""
    years = second.year - first.year

    if second.month < first.month:
        years -= 1
    elif second.month == first.month and second.day < first.day:
        years -= 1

    return years
