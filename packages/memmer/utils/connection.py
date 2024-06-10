# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Optional, Tuple

from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import URL, create_engine, event

from sshtunnel import SSHTunnelForwarder


@dataclass
class SSHTunnelParameter:
    address: str
    user: str
    port: int = 22
    password: Optional[str] = None
    key: Optional[str] = None
    remote_address: str = "127.0.0.1"


@dataclass
class ConnectionParameter:
    db_backend: str
    database: str
    address: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None

    ssh_tunnel: Optional[SSHTunnelParameter] = None


def establish_ssh_tunnel(params: SSHTunnelParameter) -> SSHTunnelForwarder:
    tunnel = SSHTunnelForwarder(
        ssh_address_or_host=params.address,
        ssh_port=params.port,
        ssh_username=params.user,
        ssh_password=params.password,
        ssh_pkey=params.key,
        remote_bind_address=params.remote_address,
    )

    tunnel.start()

    return tunnel


# From: https://stackoverflow.com/a/7831210
def enable_foreign_key_constraint_support(dbapi_con, con_record):
    dbapi_con.execute("pragma foreign_keys=on")


def connect(
    params: ConnectionParameter, enable_sql_echo: bool = False
) -> Tuple[Session, Optional[SSHTunnelForwarder]]:
    tunnel: Optional[SSHTunnelForwarder] = None
    if params.ssh_tunnel is not None:
        tunnel = establish_ssh_tunnel(params.ssh_tunnel)

    is_sqlite: bool = params.db_backend.lower() == "sqlite"

    connection_url = URL.create(
        drivername=params.db_backend.lower(),
        username=params.user if not is_sqlite else None,
        password=params.password if not is_sqlite else None,
        port=params.port if not is_sqlite else None,
        host=params.address if not is_sqlite else None,
        database=params.database,
    )

    engine = create_engine(url=connection_url, echo=enable_sql_echo)

    if is_sqlite:
        # SQLite doesn't enable FK support by default (for backwards compatibility reasons)
        event.listen(engine, "connect", enable_foreign_key_constraint_support)

    return (Session(bind=engine), tunnel)
