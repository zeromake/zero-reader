"""
将model转换为resetful api模式
by zeromake 2018.01.12
"""
import aiosqlite3
from web_app.utils import make_columns, handle_param, handle_param_primary
from sanic.views import HTTPMethodView
from sanic import response
from web_app import app

class ApiView(HTTPMethodView):
    __model__ = None
    __models__ = []

    def __init__(self, *args, **kwargs):
        """
        初始化columns
        """
        if self.__model__ is None:
            raise TypeError("self.__model__ is None")
        else:
            self._columns = make_columns(self.__model__)

    async def dispatch_request(self, request, *args, **kwargs):
        method = request.method.lower()
        handler = getattr(self, method, None)
        return await handler(request, *args, **kwargs)

    @classmethod
    def as_view(cls, *class_args, **class_kwargs):
        """Return view function for use with the routing system, that
        dispatches request to appropriate handler method.
        """
        self = cls(*class_args, **class_kwargs)
        async def view(*args, **kwargs):
            return await self.dispatch_request(*args, **kwargs)

        if cls.decorators:
            view.__module__ = cls.__module__
            for decorator in cls.decorators:
                view = decorator(view)

        view.view_class = cls
        view.self = self
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.__name__ = cls.__name__
        return view

    async def execute_dml(self, sql, message="execute ok"):
        """
        执行DML语句
        """
        # print("execute_dml sql: ", str(sql))
        engine = app.engine
        try:
            async with engine.acquire() as conn:
                async with conn.begin():
                    count = 0
                    if isinstance(sql, list):
                        for sql_ in sql:
                            async with conn.execute(sql_) as cursor:
                                count += cursor.rowcount
                    else:
                        async with conn.execute(sql) as cursor:
                            count = cursor.rowcount
                    return {'status': 200, 'message': message, 'count': count}
        except Exception as e:
            return {'status': 500, 'message': str(e)}

    async def post(self, request, *args, **kwargs):
        """
        form_data = request.json
        添加model
        """
        form_data = request.json
        sql = self.insert(form_data)
        return response.json(await self.execute_dml(sql, "insert ok"))

    def insert(self, form_data):
        """
        抽取插入语句生成
        """
        return self.__model__.insert().values(form_data)

    async def delete(self, request, *args, **kwargs):
        """
        删除
        """
        form_data = request.json
        sql = self.delete_sql(form_data)
        if sql is None:
            return response.json({'status': 400, 'message': 'param is error'})
        return response.json(await self.execute_dml(sql, "delete ok"))

    def delete_sql(self, form_data):
        """
        生成删除语句
        """
        data, is_use = handle_param_primary(self._columns, form_data)
        sql = None
        if is_use:
            sql = self.__model__.delete().where(*data)
        return sql

    async def put(self, request, *args, **kwargs):
        """
        全量更新(支持部分更新)
        """
        form_data = request.json
        sql = self.update_sql(form_data)
        if sql is None:
            return response.json({'status': 400, 'message': 'param is error'})
        return response.json(await self.execute_dml(sql, "update ok"))

    async def patch(self, request, *args, **kwargs):
        """
        部分更新
        """
        return self.put(request, *args, **kwargs)

    def update_sql(self, form_data):
        """
        生成更新语句
        """
        sql = None
        if isinstance(form_data, list):
            # 生成批量更新语句
            sql = []
            for row in form_data:
                where, is_use = handle_param_primary(self._columns, row.get("where", {}))
                data = row.get("data")
                if is_use and data and isinstance(data, dict):
                    sql.append(self.__model__.update().where(*where).values(data))
            if len(sql) == 0:
                sql = None
        else:
            where, is_use = handle_param_primary(self._columns, form_data.get("where", {}))
            data = form_data.get("data")
            if is_use and data and isinstance(data, dict):
                sql = self.__model__.update().where(*where).values(data)
        return sql
