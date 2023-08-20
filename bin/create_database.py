#!/usr/bin/env python3

from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from memmer.orm import Base, FixedCost
from memmer import AdmissionFeeKey, BasicFeeAdultsKey, BasicFeeYouthsKey


def main():
    engine = create_engine("sqlite:///sampleDB.sqlite", echo=True)

    Base.metadata.create_all(engine)

    with Session(bind=engine) as session:
        session.add_all(
            [
                FixedCost(name=AdmissionFeeKey, cost=Decimal("15")),
                FixedCost(name=BasicFeeAdultsKey, cost=Decimal("5")),
                FixedCost(name=BasicFeeYouthsKey, cost=Decimal("4")),
            ]
        )

        session.commit()


if __name__ == "__main__":
    main()
