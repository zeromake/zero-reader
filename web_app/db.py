import os
import asyncio

DRIVER_NAME = (
    "sqlite",
    "mysql",
    "postgresql"
)

class DateBase:
    """
    各种数据库切换
    """
    def __init__(self, database, **args):
        """
        初始化
        """
        from sqlalchemy import engine
        self._args = args
        self._url = engine.url.make_url(database)
        self._loop = None
        self._tables = None
        self._driver = None
        self._load_driver()
        self._models = {}
        self.load_table()

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
        import web_app.models as model
        from .models import __all__ as models
        self._tables = []
        for table in models:
            if hasattr(model, table):
                self._tables.append(getattr(model, table))

    async def create_engine(self, loop):
        """
        创建engine
        """
        if self._driver == "sqlite":
            from aiosqlite3.sa import create_engine
            # init = os.path.exists(self._url.database)
            return await create_engine(
                self._url.database,
                loop=loop,
                # echo=True,
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
                loop=loop
                # **self._args
            )
        elif self._driver == "postgresql":
            from aiopg.sa import create_engine
            return await create_engine(
                user=self._url.username,
                database=self._url.database,
                host=self._url.host,
                port=self._url.port,
                password=self._url.password,
                loop=loop,
                **self._args
            )

    async def create_table(self, engine):
        """
        创建表
        """
        from sqlalchemy.sql.ddl import CreateTable
        async with engine.acquire() as conn:
            async with conn.begin() as transaction:
                try:
                    if await self.exists_table(conn, self._tables[0].name):
                        await self.drop_table(conn)
                    for table in self._tables:
                        await conn.execute(CreateTable(table))
                except Exception:
                    await transaction.close()

    async def drop_table(self, conn):
        """
        删除表
        """
        from sqlalchemy.sql.ddl import DropTable
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
            sql = "SELECT TABLE_NAME FROM information_schema.TABLES "\
            "WHERE TABLE_NAME ='%s' AND TABLE_SCHEMA = '%s'" % (name, self._url.database)
        elif self._driver == "postgresql":
            sql = "SELECT relname FROM pg_class WHERE relname = '%s'" % name
        result = await conn.execute(sql)
        first = await result.first()
        return first != None

    async def get_last_row_id(self, conn, cursor):
        """
        获取最后的id
        """
        sql = None
        if self._driver == "sqlite":
            sql = "SELECT last_insert_rowid() as id"
        elif self._driver == "mysql":
            sql = "SELECT LAST_INSERT_ID() as id"
        elif self._driver == "postgresql":
            result = await cursor.first()
            if not result is None:
                return result[0]
        if sql:
            cursor = await conn.execute(sql)
            return (await cursor.first()).id

    def generate_model_class(self, model):
        """
        生成class
        """
        from .api import ApiView
        class TempClass(ApiView):
            """
            自动生成
            """
            __model__ = model
        return TempClass

    def model_add_view(self, router, open_api):
        """
        挂载视图
        """
        for model in self._tables:
            table_name = model.name
            if table_name not in self._models:
                view = self.generate_model_class(model).add_route(router, open_api)
                self._models[table_name] = view.self

    def get_model(self, name):
        """
        获取model操作对象
        """
        return self._models[name] if name in self._models else None
