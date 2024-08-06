# This file is part of memmer. Use of this source code is
# governed by a BSD-style license that can be found in the
# LICENSE file at the root of the source tree or at
# <https://github.com/Krzmbrzl/memmer/blob/main/LICENSE>.

from typing import Optional, Tuple

from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import URL, create_engine, event

from sshtunnel import SSHTunnelForwarder

from .config import MemmerConfig, DBBackend, ConnectType


@dataclass
class SSHTunnelParameter:
    address: str
    user: str
    port: int = 22
    password: Optional[str] = None
    key: Optional[str] = None
    remote_address: str = "127.0.0.1"
    remote_port: int = 80

    @staticmethod
    def from_config(config: MemmerConfig) -> "SSHTunnelParameter":
        if config.db_host is None or config.ssh_user is None:
            raise RuntimeError(
                "Mandatory arguments for SSHTunnelParameter not present!"
            )

        params = SSHTunnelParameter(address=config.db_host, user=config.ssh_user)

        if config.ssh_port is not None:
            params.port = config.ssh_port
        if config.ssh_key is not None:
            params.key = config.ssh_key
        if config.db_port is not None:
            params.remote_port = config.db_port
        # No way to set the remote address for now

        return params


@dataclass
class ConnectionParameter:
    db_backend: DBBackend
    database: str
    address: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None

    ssh_tunnel: Optional[SSHTunnelParameter] = None

    @staticmethod
    def from_config(config: MemmerConfig) -> "ConnectionParameter":
        if config.db_backend is None or config.db_name is None:
            raise RuntimeError(
                "Mandatory arguments for ConnectionParameter not present!"
            )

        params = ConnectionParameter(
            db_backend=config.db_backend, database=config.db_name
        )

        if config.db_host is not None:
            params.address = config.db_host
        if config.db_port is not None:
            params.port = config.db_port
        if config.db_user is not None:
            params.user = config.db_user

        if config.connect_type == ConnectType.SSH_TUNNEL:
            params.ssh_tunnel = SSHTunnelParameter.from_config(config)

        if params.db_backend == DBBackend.SQLite:
            params.address = None
            params.user = None
            params.port = None

        return params


def establish_ssh_tunnel(params: SSHTunnelParameter) -> SSHTunnelForwarder:
    tunnel = SSHTunnelForwarder(
        ssh_address_or_host=params.address,
        ssh_port=params.port,
        ssh_username=params.user,
        ssh_password=params.password,
        ssh_pkey=params.key,
        remote_bind_address=(params.remote_address, params.remote_port),
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
    address = params.address
    port = params.port

    if params.ssh_tunnel is not None:
        tunnel = establish_ssh_tunnel(params.ssh_tunnel)
        address = tunnel.local_bind_host
        port = tunnel.local_bind_port

    is_sqlite: bool = params.db_backend == DBBackend.SQLite

    connection_url = URL.create(
        drivername=params.db_backend.name.lower(),
        username=params.user if not is_sqlite else None,
        password=params.password if not is_sqlite else None,
        port=port if not is_sqlite else None,
        host=address if not is_sqlite else None,
        database=params.database,
    )

    engine = create_engine(url=connection_url, echo=enable_sql_echo)

    if is_sqlite:
        # SQLite doesn't enable FK support by default (for backwards compatibility reasons)
        event.listen(engine, "connect", enable_foreign_key_constraint_support)

    return (Session(bind=engine), tunnel)
