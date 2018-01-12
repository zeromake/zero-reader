"""
将model转换为resetful api模式
by zeromake 2018.01.12
"""
from web_app.utils import make_columns, handle_param, handle_param_primary
from sanic import response

class ApiView:
    __model__ = None
    decorators = []

    def __init__(self, *args, **kwargs):
        """
        初始化columns
        """
        if self.__model__ is None:
            raise TypeError("self.__model__ is None")
        else:
            self._columns = make_columns(self.__model__)

    async def dispatch_request(self, app, request, *args, **kwargs):
        method = request.method.lower()
        handler = getattr(self, method, None)
        return await handler(request, app, *args, **kwargs)

    @classmethod
    def as_view(cls, *class_args, **class_kwargs):
        """Return view function for use with the routing system, that
        dispatches request to appropriate handler method.
        """
        from web_app import app
        async def view(*args, **kwargs):
            self = view.view_class(*class_args, **class_kwargs)
            return await self.dispatch_request(app, *args, **kwargs)

        if cls.decorators:
            view.__module__ = cls.__module__
            for decorator in cls.decorators:
                view = decorator(view)

        view.view_class = cls
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.__name__ = cls.__name__
        return view

    async def post(self, request, app, *args, **kwargs):
        """
        form_data = request.json
        添加model
        """
        form_data = request.json
        is_use = False
        insert_data = None
        engine = app.engine
        if isinstance(form_data, list):
            insert_data = []
            for row in form_data:
                values, use = handle_param(self._columns, row)
                if use:
                    insert_data.append(values)
                is_use = is_use or use
        else:
            insert_data, is_use = handle_param(self._columns, form_data)
        if is_use:
            insert = self.__model__.insert().values(insert_data)
            try:
                async with engine.acquire() as conn:
                    await conn.execute(insert)
                    await conn.commit()
                return response.json({'status': 200, 'message': "insert ok"})
            except Exception as e:
                return response.json({'status': 500, 'message': str(e)})
        else:
            return response.json({'status': 400, 'message': "json not param"})
    
    async def delete(self, request, app, *args, **kwargs):
        """
        删除
        """
        form_data = request.json
        data, is_use = handle_param_primary(self._columns, form_data)
        if is_use:
            sql_obj = self.__model__.delete().where(*data)

