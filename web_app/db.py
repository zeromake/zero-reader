import os
import asyncio

from .utils import import_string

DRIVER_NAME = (
    "sqlite",
    "mysql",
    "postgresql"
)

class DateBase:
    """
    各种数据库切换
    """
    def __init__(self, database, loop=None, **args):
        """
        初始化
        """
        from sqlalchemy import engine
        self._args = args
        self._url = engine.url.make_url(database)
        self._loop = loop or asyncio.get_event_loop()
        self._tables = None
        self._driver = None
        self._load_driver()

    def _load_driver(self):
        """
        加载driver
        """
        for name in DRIVER_NAME:
            if self._url.drivername.startswith(name):
                self._driver = name
                return
        raise TypeError("url not support: %s" % self._url)

    def load_table(self):
        """
        加载表模块
        """
        if self._tables:
            return
        from .models import __all__ as models
        self._tables = []
        for table in models:
            import_name = "web_app.models.%s" % table
            self._tables.append(import_string(import_name))

    async def create_engine(self):
        """
        创建engine
        """
        if self._driver == "sqlite":
            from aiosqlite3.sa import create_engine
            # init = os.path.exists(self._url.database)
            return await create_engine(
                self._url.database,
                loop=self._loop,
                **self._args
            )
        elif self._driver == "mysql":
            from aiomysql.sa import create_engine
            return await create_engine(
                user=self._url.username,
                db=self._url.database,
                host=self._url.host,
                password=self._url.password,
                port=self._url.port,
                loop=self._loop,
                **self._args
            )
        elif self._driver == "postgresql":
            from aiopg.sa import create_engine
            return await create_engine(
                user=self._url.username,
                db=self._url.database,
                host=self._url.host,
                port=self._url.port,
                password=self._url.password,
                loop=self._loop,
                **self._args
            )

    async def create_table(self, engine):
        """
        创建表
        """
        from sqlalchemy.sql.ddl import CreateTable
        self.load_table()
        print("create_table")
        async with engine.acquire() as conn:
            if await self.exists_table(conn, self._tables[0].name):
                await self.drop_table(conn)
            for table in self._tables:
                await conn.execute(CreateTable(table))

    async def drop_table(self, conn):
        """
        删除表
        """
        from sqlalchemy.sql.ddl import DropTable
        self.load_table()
        print("drop_table")
        # async with engine.acquire() as conn:
        for table in self._tables:
            await conn.execute(DropTable(table))

    async def exists_table(self, conn, name):
        """
        判断表是否存在
        """
        sql = None
        if self._driver == "sqlite":
            sql = "SELECT name FROM sqlite_master where type='table' and name='%s'" % name
        elif self._driver == "mysql":
            sql = "SELECT table_name FROM information_schema.TABLES WHERE table_name ='%s'" % name
        elif self._driver == "postgresql":
            sql = "SELECT name FROM pg_class WHERE relname = '%s'" % name
        result = await conn.execute(sql)
        first = await result.first()
        return first != None
