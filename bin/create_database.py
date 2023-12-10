#!/usr/bin/env python3

from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from memmer.orm import Base, FixedCost, Setting
from memmer import (
    AdmissionFeeKey,
    BasicFeeAdultsKey,
    BasicFeeYouthsKey,
    BasicFeeTrainersKey,
)


def main():
    engine = create_engine("sqlite:///sampleDB.sqlite", echo=True)

    Base.metadata.create_all(engine)

    with Session(bind=engine) as session:
        session.add_all(
            [
                FixedCost(name=AdmissionFeeKey, cost=Decimal("15")),
                FixedCost(name=BasicFeeAdultsKey, cost=Decimal("5")),
                FixedCost(name=BasicFeeYouthsKey, cost=Decimal("4")),
                FixedCost(name=BasicFeeTrainersKey, cost=Decimal("1")),
            ]
        )

        session.add_all(
            [
                Setting(
                    name=Setting.TALLY_E2E_ID_TEMPLATE, value="Member-ID: {mem_id:06d}"
                ),
                Setting(name=Setting.TALLY_PURPOSE, value="Membership fee"),
                Setting(name=Setting.TALLY_CREDITOR_NAME, value="Memmer Club"),
                Setting(
                    name=Setting.TALLY_CREDITOR_IBAN, value="DE02700100800030876808"
                ),
                Setting(name=Setting.TALLY_CREDITOR_BIC, value="PBNKDEFF"),
                Setting(name=Setting.TALLY_CREDITOR_ID, value="DE98ZZZ09999999999"),
            ]
        )

        session.commit()


if __name__ == "__main__":
    main()
