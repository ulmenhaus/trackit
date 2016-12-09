"""
Module to invoke trackit API as flask APP
"""

import logging
import os
import time

import rethinkdb as r

from api.api import API

DB_HOST = os.environ.get("DB_HOST", 'db')
DB_PORT = int(os.environ.get("DB_PORT", 28015))
DB_NAME = os.environ.get("DB_NAME", "trackit")

LOGGER = logging.getLogger(__name__)


def _wait_for_db():
    """
    Initialize rethinkdb connection with backoff
    """
    # TODO(rabrams) generic retry functional would be nice
    for sleepsecs in [1, 2, 4, 10]:
        try:
            return r.connect(DB_HOST, DB_PORT).repl()
        except Exception:
            LOGGER.exception("Could not connect to db")
            time.sleep(sleepsecs)
    raise Exception("Retry cap reached for connecting to db")


def _init_db():
    """
    Initialize rethinkdb schema
    """
    # TODO(rabrams) consider looking into schema migration tools
    if not r.db_list().contains(DB_NAME).run():
        r.db_create(DB_NAME).run()

    if not r.db(DB_NAME).table_list().contains("schemata").run():
        r.db(DB_NAME).table_create("schemata", primary_key="name").run()

    if not r.db(DB_NAME).table_list().contains("data").run():
        r.db(DB_NAME).table_create("data", primary_key="key").run()


_wait_for_db()
_init_db()
app = API(r, DB_NAME).app  # pylint: disable=invalid-name
