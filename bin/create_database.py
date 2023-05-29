#!/usr/bin/env python3

from sqlalchemy import create_engine

from memmer.orm import Base


def main():
    engine = create_engine("sqlite:///sampleDB.sqlite", echo=True)

    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
