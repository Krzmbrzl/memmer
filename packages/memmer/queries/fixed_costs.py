# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import select

from memmer.orm import FixedCost

def get_fixed_cost(session:Session, key: str) -> Decimal:
    """Gets the fixed cost associated with the given key"""
    fixed_cost = session.scalars(select(FixedCost).where(FixedCost.name == key)).first()

    if fixed_cost is None:
        raise RuntimeError("No fixed cost known with key '{}'".format(key))

    return fixed_cost.cost

