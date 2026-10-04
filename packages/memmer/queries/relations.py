# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import exists
from sqlalchemy import or_
from sqlalchemy import select, delete

from memmer.orm import Member, Relation


def are_related(session: Session, first: Member, second: Member) -> bool:
    """Checks whether the given two members are related"""
    result = session.query(
        exists(Relation).where(
            or_(
                (Relation.first_id == first.id) & (Relation.second_id == second.id),
                (Relation.second_id == first.id) & (Relation.first_id == second.id),
            )
        )
    ).scalar()

    return result


def get_relatives(session: Session, member: Member) -> List[Member]:
    """Gets a list of members that are related to the given one"""
    relations = session.scalars(
        select(Relation).where(
            or_(Relation.first_id == member.id, Relation.second_id == member.id)
        )
    ).all()

    # Collect the id of the "other" member in each relation, deduplicated but
    # keeping the order in which the relations were returned. Comparing by id
    # (not identity): `member` may be a detached instance from a different
    # session than the ones queried here.
    related_ids: List[int] = []
    for currentRelation in relations:
        for other_id in (currentRelation.first_id, currentRelation.second_id):
            if other_id != member.id and other_id not in related_ids:
                related_ids.append(other_id)

    # Resolve all of them in a single query instead of two SELECTs per relation.
    by_id = {
        m.id: m
        for m in session.scalars(
            select(Member).where(Member.id.in_(related_ids))
        ).all()
    }
    relatedMembers: List[Member] = [by_id[i] for i in related_ids if i in by_id]

    # Also consider dummy relatives added directly to Member instances
    if hasattr(member, "relatives"):
        for current in member.relatives:  # type: ignore
            if current not in relatedMembers:
                relatedMembers.append(current)

    return relatedMembers


def make_relation(session: Session, first: Member, second: Member) -> None:
    """Ensures that the given two members are stored as being related to each other.
    Note: relationship is a transitive property."""
    if not are_related(session, first, second):
        first_relatives = get_relatives(session=session, member=first)
        second_relatives = get_relatives(session=session, member=second)

        # Handle transitiveness of relationships
        for current in first_relatives:
            session.add(Relation(first_id=current.id, second_id=second.id))

        for current in second_relatives:
            session.add(Relation(first_id=current.id, second_id=first.id))

        # Actually make first and second relatives
        session.add(Relation(first_id=first.id, second_id=second.id))


def drop_relation(session: Session, first: Member, second: Member) -> None:
    """Removes the relationship between the two members"""
    relation = session.scalars(
        select(Relation).where(
            or_(
                (Relation.first_id == first.id) & (Relation.second_id == second.id),
                (Relation.second_id == first.id) & (Relation.first_id == second.id),
            )
        )
    ).first()

    if not relation is None:
        session.delete(relation)


def clear_relations(session: Session, member: Member):
    """Clears all of the given member's relationships"""
    session.execute(
        delete(Relation).where(
            or_(Relation.first_id == member.id, Relation.second_id == member.id)
        )
    )


def set_relatives(session: Session, member: Member, relatives: List[Member]):
    """Sets the given member's relatives"""
    clear_relations(session, member)

    for current in relatives:
        make_relation(session, member, current)
