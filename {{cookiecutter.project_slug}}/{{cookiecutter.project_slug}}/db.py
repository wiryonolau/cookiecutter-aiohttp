import asyncio
import sqlite3
import aiosqlite
import traceback
import sys
import os
import datetime
from {{ cookiecutter.project_slug }}.util import get_logger, dt2str

class Database:
    def __init__(self, data_path: str):
        self._logger = get_logger(self.__class__.__name__)
        self._data_path = data_path
        self._db_path = os.path.join(self._data_path, "{{ cookiecutter.project_slug }}.sqlite3")

    def init(self):
        try:
            with sqlite3.connect(self._db_path) as db:
                # db.execute('''CREATE TABLE...''')
                pass
        except:
            self._logger.debug(traceback.print_exc())


    async def insert(self, table_name, table_value):
        insert = "INSERT INTO {}({}) VALUES({})"
        insert = insert.format(
            table_name,
            ",".join(table_value.keys()),
            ",".join(list('?' * len(table_value))))

        for k, v in table_value.items():
            if isinstance(v, datetime.datetime):
                table_value[k] = dt2str(v)

        return await self.execute(insert, table_value)

    async def execute(self, stmt, params=None):
        result = []
        try:
            if params is not None:
                params = tuple(params.values())

            async with aiosqlite.connect(self._db_path) as db:
                db.row_factory = sqlite3.Row
                async with db.execute(stmt, params) as cursor:
                    rows = await cursor.fetchall()
                    result = [dict(r) for r in rows]
                await db.commit()
        except:
            self._logger.debug(traceback.print_exc())
        return result
