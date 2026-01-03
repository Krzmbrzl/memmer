# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from sqlalchemy.orm import Session
from sqlalchemy import event

uncommitted_changes_key = "memmer_has_uncommitted_changes"


def on_commit(session: Session, *_):
    session.info[uncommitted_changes_key] = False


def on_flush(session: Session, *_):
    session.info[uncommitted_changes_key] = True


def register_session_for_uncommitted_state_tracking(session: Session):
    event.listen(session, "after_commit", on_commit)
    event.listen(session, "after_rollback", on_commit)
    event.listen(session, "after_begin", on_commit)

    event.listen(session, "after_flush_postexec", on_flush)

    # Initialize the info field by calling the hook manually
    on_commit(session)


def has_uncommitted_changes(session: Session) -> bool:
    assert (
        uncommitted_changes_key in session.info
    ), "Called on session that wasn't registered for tracking"

    return (
        # Whether any changes have already been flushed to the DB since the last commit
        session.info[uncommitted_changes_key]
        # Whether there are any pending changes that the DB doesn't yet know about
        # (they haven't been flushed)
        or any(session.new)
        or any(session.deleted)
        or any([x for x in session.dirty if session.is_modified(x)])
    )
