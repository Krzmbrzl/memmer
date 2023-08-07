# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

import datetime

from sqlalchemy.orm import Session
from sqlalchemy import delete

from memmer.orm import Participation


def clear_outdated_entries(session: Session) -> None:
    """Remove all outdated entries in the database"""
    today = datetime.datetime.now().date()

    session.execute(delete(Participation).where(Participation.until < today))
