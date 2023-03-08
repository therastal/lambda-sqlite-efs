import os
import sqlite3
from typing import Optional

DEFAULT_PATH = os.getenv("MOUNT_PATH", "datastore/default")
DEFAULT_TABLE = "items"

READ_ONLY_ACCESS = "ro"
READ_WRITE_CREATE_ACCESS = "rwc"


def adapt_list(L: list) -> str:
    return str(L)


sqlite3.register_adapter(list, adapt_list)


def get(
    fieldname: str, uid: int, tablename: str = DEFAULT_TABLE, path: str = DEFAULT_PATH
):
    db = connection(fieldname, READ_ONLY_ACCESS, tablename, path)
    data = db.execute(f"select value from {tablename} where uid = ?", [uid]).fetchone()
    db.close()
    return data["value"]


def put(
    fieldname: str,
    uid: int,
    value,
    tablename: str = DEFAULT_TABLE,
    path: str = DEFAULT_PATH,
    con: Optional[sqlite3.Connection] = None,
):
    db = con or connection(fieldname, READ_WRITE_CREATE_ACCESS, tablename, path)

    db.execute(f"replace into {tablename}(uid, value) values(?, ?)", [uid, value])

    if con is None:
        db.commit()
        db.close()


def delete(
    fieldname: str,
    uid: int,
    tablename: str = DEFAULT_TABLE,
    path: str = DEFAULT_PATH,
    con: Optional[sqlite3.Connection] = None,
):
    db = con or connection(fieldname, READ_WRITE_CREATE_ACCESS, tablename, path)

    db.execute(f"delete from {tablename} where uid = ?", [uid])

    if con is None:
        db.commit()
        db.close()


def connection(
    fieldname: str,
    access: str = READ_ONLY_ACCESS,
    tablename: str = DEFAULT_TABLE,
    path: str = DEFAULT_PATH,
) -> sqlite3.Connection:
    file = f"{path}/{fieldname}.sqlite"

    # Hacky solution to ensure the shard for this fieldname exists
    db_prep = sqlite3.connect(file)
    db_prep.execute(
        f"create table if not exists {tablename}(uid integer primary key, value)"
    )
    db_prep.commit()
    db_prep.close()

    uri = f"file:{file}?mode={access}"
    db = sqlite3.connect(uri, uri=True)
    db.row_factory = sqlite3.Row
    return db
