# Memmer

`Memmer` (**mem**bership-**m**anag**er**) is a Python-based framework for membership management primarily intended for use in (small) clubs.


## Translation

<a href="https://hosted.weblate.org/engage/memmer/">
    <img src="https://hosted.weblate.org/widget/memmer/glossary/svg-badge.svg" alt="Translation status" />
</a>

Memmer uses [Weblate](https://weblate.org/) for translations. Get involved [here](https://hosted.weblate.org/engage/memmer/).


## Setup

Note: Memmer should work with any backend that [SQLAlchemy](https://www.sqlalchemy.org/) supports. However, it is strongly recommended to use a
database that supports foreign key constraints (and enables them by default!). For this reason SQLite can't be recommended for anything other than a
quick example.

### PostgreSQL

Precondition: Having a full PostgreSQL installation available. The following instructions assume a Linux host.

1. Connect to your PostgreSQL database via
```bash
sudo -u postgres psql
```
2. Create the user with which you intend to access the database and assign a password for them
```psql
CREATE USER "JamesBond" WITH PASSWORD ENCRYPTED "Shaken, not stirred";
```
3. Create the database that you intend to use (the name is arbitrary)
```psql
CREATE DATABASE "memmer_test" ENCODING "UTF-8";
```
4. Exit `psql` by entering `\q`
5. Edit the [create_database.py](bin/create_database.py) script and edit set the parameters for the connection URL to
```python
connection_url = sqlalchemy.engine.URL.create(
    drivername="postgresql",
    username="JamesBond",
    password="Shaken, not stirred",
    host="localhost",
    database="memmer_test"
)
```
6. Execute the script via `python3 bin/create_database.py` in order to have all necessary tables created for you

Now you are ready to connect to your database via the GUI. If the database lives on a remote host, it is recommended to use an SSH tunnel as that
doesn't require to open up the database to the internet itself. Instead, the client will authenticate via SSH (which is most conveniently achieved by
means of a certificate that is registered on the host) and then connect to the database from the remote host itself.

Note: If you are using the SSH tunnel authentication _without_ a certificate-based SSH authentication, then you will need enter _two different_
passwords into the GUI:
1. The password for authenticating the _database-intern_ user 
2. The password for authenticating the _remote host_ user via SSH

