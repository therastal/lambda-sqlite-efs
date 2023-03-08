import logging
import os
import sqlite3
import threading
from queue import Queue, Empty
from typing import Any

from .kvstore import sqlite


def worker(queue: Queue, con: sqlite3.Connection):
    thread = threading.current_thread().getName()
    while True:
        try:
            item: Any = queue.get(timeout=10)
            logging.info(
                "Attempting sqlite replace into",
                extra={"thread": thread, "item": item},
            )
            sqlite.put(*item, con=con)
            queue.task_done()
        except Empty:
            break
        except (sqlite.sqlite3.DatabaseError, sqlite.sqlite3.OperationalError) as e:
            logging.error(
                "Error in writing to the database",
                extra={"exception": e, "thread": thread},
            )


def load_handler(event: dict, _=None):
    shards: dict[str, tuple[Queue, sqlite3.Connection]] = {}

    for item in event.get("items", []):
        fieldname = item[0]
        if fieldname not in shards:
            queue = Queue()
            db = sqlite.connection(fieldname, sqlite.READ_WRITE_CREATE_ACCESS)

            thread = threading.Thread(target=worker, args=(queue, db))
            thread.start()

            shards[fieldname] = (queue, db)

        shards[fieldname][0].put(item)

    for fieldname, (queue, db) in shards.items():
        queue.join()
        db.commit()
        db.close()


def query_handler(event: dict, _=None):
    fieldname = event.get("fieldname", "__typename")
    db = sqlite3.connect(f"{sqlite.DEFAULT_PATH}/{fieldname}")

    sql = event.get("sql", "select * from items")

    parameters = event.get("parameters", [])
    if parameters:
        results = db.execute(sql, parameters).fetchall()
    else:
        results = db.execute(sql).fetchall()

    return results


def clear_handler(event: dict, _=None):
    print(os.listdir(sqlite.DEFAULT_PATH))

    for item in os.listdir(sqlite.DEFAULT_PATH):
        os.remove(f"{sqlite.DEFAULT_PATH}/{item}")

    print(os.listdir(sqlite.DEFAULT_PATH))
