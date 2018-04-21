"""
将model转换为resetful api模式
by zeromake 2018.01.12
"""
import xmltodict
import yaml
from web_app.utils import (
    make_columns,
    handle_param,
    handle_param_primary,
    handle_keys,
    generate_openapi_by_table,
    generate_openapi_by_column
)
from sanic.views import HTTPMethodView
from sanic import response, Blueprint
from web_app import app
try:
    import ujson as json
except ImportError:
    import json
from sqlalchemy import func, sql as sa_sql, desc, and_
from sqlalchemy.sql.expression import bindparam

__all__ = [
    "ApiView",
    "Api"
]

def json_dumps(res, **kwargs):
    """
    json格式化
    """
    return json.dumps(res, **kwargs)

def xml_dumps(res, root="root", **kwargs):
    """
    xml格式化
    """
    return xmltodict.unparse({root: res}, **kwargs)

def yaml_dumps(res, **kwargs):
    """
    yaml格式化
    """
    return yaml.dump(res, **kwargs)

def model_row_to_dict(row):
    """
    把model查询出的row转换为dict
    """
    return {key: val for key, val in row.items()}

HANDLE_RESPONSE = {
    "application/json": json_dumps,
    "application/xml": xml_dumps,
    "text/yaml": yaml_dumps,
}

class ApiView(HTTPMethodView):
    """
    自动化model转换api
    """
    __model__ = None
    methods = None

    def __init__(self, *args, **kwargs):
        """
        初始化columns
        """
        if self.__model__ is None:
            raise TypeError("self.__model__ is None")
        else:
            self._columns = make_columns(self.__model__)
            self._columns_name = {str(column.name): column for column in self._columns}
            self._key = None
            for column in self.__model__.columns:
                if column.primary_key:
                    self._key = column
                    break

    async def dispatch_request(self, request, *args, **kwargs):
        method = request.method.lower()
        raw_type = request.headers.get("accept", "application/json")
        if raw_type not in HANDLE_RESPONSE:
            raw_type = "application/json"
        handler = None
        if self.methods is None:
            handler = getattr(self, method, None)
        else:
            if method in self.methods:
                handler = getattr(self, method, None)
        if handler is None:
            res = {"status": 405, "message": "not support method"}
        else:
            res = await handler(request, *args, **kwargs)
        # 自动根据Content-Type请求头格式化响应
        return response.text(
            HANDLE_RESPONSE[raw_type](res),
            headers={'Content-Type': raw_type},
            status=res['status']
        )

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

    @classmethod
    def add_route(cls, app_, OPEN_API=None, *class_args, **class_kwargs):
        """
        添加路由
        """
        view = cls.as_view(*class_args, **class_kwargs)
        self = view.self
        table_name = str(self.__model__.name)
        url = "/" + table_name
        if OPEN_API:
            OPEN_API.add_schema(table_name, generate_openapi_by_table(self.__model__))
            base_url = app_.url_prefix + url
            table_doc = self.__model__.__doc__
            doc = table_doc + self.get.__doc__
            OPEN_API.add_tag(table_name, table_doc)
            primary_key = {
                "in": "path",
                "name": "primary_key",
                "description": "主键",
                "required": True,
                "schema": {
                    "type": generate_openapi_by_column(self._key)["type"]
                }
            }
            default_responses = {
                "200": {
                    "description": "OK",
                    "content": {
                        "application/json": {
                            "schema": {
                                "allOf": [
                                    {
                                        "$ref": "#/components/schemas/baseResponse"
                                    },
                                    {
                                        "type": "object",
                                        "properties": {
                                            "count": {
                                                "type": "integer",
                                                "description": "执行sql条数"
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                    }
                },
                "400": {
                    "description": "Parameters Error!",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/baseResponse"
                            }
                        },
                    }
                },
                "500": {
                    "description": "Error!",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/baseResponse"
                            }
                        },
                    }
                }
            }
            OPEN_API.add_path(
                base_url+"/{primary_key}",
                {
                    "get": {
                        "parameters": [primary_key, {"$ref": "#/components/parameters/keys"}],
                        "summary": doc + "单条",
                        "tags": [table_name],
                        "security":[
                            {"TokenAuth": []}
                        ],
                        "responses": {
                            "200": {
                                "description": "OK",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "allOf": [
                                                {
                                                    "$ref": "#/components/schemas/baseResponse"
                                                },
                                                {
                                                    "type": "object",
                                                    "properties": {
                                                        "data": {
                                                            "oneOf": [
                                                                {"$ref": '#/components/schemas/%s' % table_name},
                                                                {"type": "null"}
                                                            ]
                                                        }
                                                    }
                                                }
                                            ]
                                            
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "delete": {
                        "parameters": [primary_key],
                        "tags": [table_name],
                        "summary": table_doc + self.delete.__doc__,
                        "security":[
                            {"TokenAuth": []}
                        ],
                        "responses": default_responses
                    }
                }
            )
            schema = {
                "allOf": [
                    {
                        "$ref": "#/components/schemas/baseResponse"
                    },
                    {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {
                                    "$ref": '#/components/schemas/%s' % table_name
                                }
                            },
                            "count": {
                                "type": "integer",
                                "description": "总条数"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "取出多少条"
                            },
                            "skip": {
                                "type": "integer",
                                "description": "略过多少条"
                            }
                        }
                    }
                ]
                
            }
            response = {
                "schema": schema
            }
            OPEN_API.add_path(
                base_url, 
                {
                    "get": {
                        "parameters": [
                            {"$ref": "#/components/parameters/where"},
                            {"$ref": "#/components/parameters/order"},
                            {"$ref": "#/components/parameters/keys"},
                            {"$ref": "#/components/parameters/limit"},
                            {"$ref": "#/components/parameters/skip"}
                        ],
                        "summary": doc + "多条",
                        "tags": [table_name],
                        "security":[
                            {"TokenAuth": []}
                        ],
                        "responses": {
                            "200": {
                                "description": "OK",
                                "content": {
                                    "application/json": response,
                                    "application/xml": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "root": schema
                                            }
                                        }
                                    },
                                    "text/yaml": response
                                }
                            }
                        }
                    },
                    "post": {
                        "requestBody": {
                            "description": table_doc,
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "oneOf": [
                                            {
                                                "type": "object",
                                                "$ref": '#/components/schemas/%s' % table_name
                                            },
                                            {
                                                "type": "array",
                                                "items": {
                                                    "$ref": '#/components/schemas/%s' % table_name
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        },
                        "tags": [table_name],
                        "summary": table_doc + self.post.__doc__,
                        "security":[
                            {"TokenAuth": []}
                        ],
                        "responses": default_responses
                    },
                    "put": {
                        "tags": [table_name],
                        "summary": table_doc + self.put.__doc__,
                        "security":[
                            {"TokenAuth": []}
                        ],
                        "responses": default_responses,
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "where": {
                                                "$ref": "#/components/schemas/whereData"
                                            },
                                            "values": {
                                                "type": "object",
                                                "additionalProperties": {
                                                    "oneOf": [
                                                        {
                                                            "type": "any",
                                                            "description": "要更新的值"
                                                        },
                                                        {
                                                            "type": "object",
                                                            "description": "设置占位符",
                                                            "properties": {
                                                                "val": {
                                                                    "type": "string",
                                                                    "description": "占位符名用于data的key"
                                                                }
                                                            }
                                                        }
                                                    ]
                                                }
                                            },
                                            "data": {
                                                "oneOf": [
                                                    {
                                                        "type": "object",
                                                        "required": False,
                                                        "description": "对应 values, where 中的占位数据"
                                                    },
                                                    {
                                                        "type": "array",
                                                        "required": False,
                                                        "description": "批量操作",
                                                        "items": {
                                                            "type": "object",
                                                            "description": "对应 values, where 中的占位数据"
                                                        }
                                                    }
                                                ]
                                                
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            )
        app_.add_route(view, url)
        app_.add_route(view, url + "/<primary_key:int>")
        return view

    async def execute_dml(self, sql, message="execute ok", data=None):
        """
        执行DML语句
        """
        # print("execute_dml sql: ", str(sql))
        engine = app.engine
        try:
            async with engine.acquire() as conn:
                async with conn.begin() as begin:
                    count = 0
                    if isinstance(sql, list):
                        for sql_ in sql:
                            async with conn.execute(sql_) as cursor:
                                count += cursor.rowcount
                    else:
                        async with conn.execute(sql, data) as cursor:
                            count = cursor.rowcount
                    return {'status': 200, 'message': message, 'count': count}
        except Exception as e:
            return {'status': 500, 'message': str(e)}

    
    async def execute_insert(self, sql, message="execute ok", form_data=None):
        """
        执行单次插入语句
        """
        engine = app.engine
        db_ = app.db
        try:
            async with engine.acquire() as conn:
                async with conn.begin():
                    count = 0
                    row_id = 0
                    async with conn.execute(sql) as cursor:
                        count = cursor.rowcount
                        row_id = await db_.get_last_row_id(conn, cursor)
                    if form_data:
                        form_data["row_id"] = row_id
                        return {'status': 200, 'message': message, 'count': count, "data": form_data}
                    return {'status': 200, 'message': message, 'count': count, "row_id": row_id}
        except Exception as e:
            return {'status': 500, 'message': str(e)}

    async def execute_one(self, sql):
        """
        执行sql取出一条记录
        """
        engine = app.engine
        async with engine.acquire() as conn:
            async with conn.execute(sql) as cursor:
                return await cursor.first()

    async def post(self, request, *args, **kwargs):
        """
        添加
        """
        form_data = request.json
        sql = self.insert(form_data)
        if sql is None:
            return {'status': 400, 'message': 'param is error'}
        if isinstance(form_data, list):
            return await self.execute_dml(sql, "insert ok")
        return await self.execute_insert(sql, "insert ok", form_data)

    def insert(self, form_data):
        """
        抽取插入语句生成
        """
        if not form_data:
            return
        return self.__model__.insert().values(form_data)

    async def delete(self, request, *args, **kwargs):
        """
        删除
        """
        form_data = request.json
        if 'primary_key' in kwargs:
            if form_data is None:
                form_data = {}
            if not self._key is None:
                form_data[self._key.name] = kwargs['primary_key']
        sql = self.delete_sql(form_data)
        if sql is None:
            return {'status': 400, 'message': 'param is error'}
        return await self.execute_dml(sql, "delete ok")

    def delete_sql(self, form_data):
        """
        生成删除语句
        """
        if not form_data:
            return
        data = handle_param_primary(self._columns_name, form_data)
        sql = None
        if not data is None:
            sql = self.__model__.delete().where(data)
        return sql

    async def put(self, request, *args, **kwargs):
        """
        全量更新
        """
        form_data = request.json
        data = None
        if 'primary_key' in kwargs:
            sql = self.__model__.update().where(self._key==kwargs['primary_key']).values(form_data)
        else:
            sql = self.update_sql(form_data)
            data = form_data.get("data")
        if sql is None:
            return {'status': 400, 'message': 'param is error'}
        return await self.execute_dml(sql, "update ok", data)

    async def patch(self, request, *args, **kwargs):
        """
        部分更新
        """
        return await self.put(request, *args, **kwargs)

    def update_sql(self, form_data):
        """
        生成更新语句
        """
        if not form_data:
            return
        sql = None
        if isinstance(form_data, list):
            # 生成批量更新语句
            sql = []
            for row in form_data:
                row_sql = self.update_sql(row)
                if not row_sql is None:
                    sql.append(row_sql)
            if len(sql) == 0:
                sql = None
        else:
            where = handle_param_primary(self._columns_name, form_data.get("where", {}))
            values = form_data.get("values")
            if not where is None and values and isinstance(values, dict):
                for key, val in values.items():
                    if isinstance(val, dict):
                        values[key] = bindparam(val.get("val", key))
                sql = self.__model__.update().where(where).values(values)
        return sql

    def select(self, args={}, where_data={}, kwargs={}):
        """
        生成查询语句
        """
        use_primary = False
        if 'primary_key' in kwargs:
            if not self._key is None:
                use_primary = True
                where_data[self._key.name] = kwargs['primary_key']
        if "limit" in args:
            limit = [int(args.get("skip", 0)), int(args["limit"])]
        else:
            limit = None
        where = handle_param_primary(self._columns_name, where_data)
        limit_sql = None
        count_sql = None
        sql = self.__model__.select()
        if "keys" in args:
            keys = handle_keys(self._columns_name, args['keys'])
            if keys:
                sql = sa_sql.select(keys)
        if not where is None:
            sql = sql.where(where)
        if limit:
            count_sql = sa_sql.select([func.count(self._columns[0]).label("count")])
            if not where is None:
                count_sql = count_sql.where(where)
            limit_sql = sql.offset(limit[0]).limit(limit[1])
        if "order" in args:
            orders = args['order'].split(",")
            order_by = None
            for order in orders:
                is_desc = False
                if order[0] == "-":
                    order = order[1:]
                    is_desc = True
                if order in self._columns_name:
                    if order_by is None:
                        order_by = []
                    column = self._columns_name[order]
                    if is_desc:
                        order_by.append(desc(column))
                    else:
                        order_by.append(column)
            if order_by:
                if limit_sql is None:
                    sql = sql.order_by(*order_by)
                else:
                    limit_sql = limit_sql.order_by(*order_by)
        if limit_sql is None:
            return sql, use_primary, None
        else:
            return limit_sql, count_sql, limit

    async def get(self, request, *args_, **kwargs):
        """
        查询
        """
        args = request.raw_args
        if "where" in args:
            try:
                where_data = json.loads(args["where"])
            except ValueError:
                where_data = {}
        else:
            where_data = {}
        engine = app.engine
        limit_sql, count_sql, limit = self.select(args, where_data, kwargs)
        use_primary = False
        sql = None
        if limit is None:
            sql = limit_sql
            limit_sql = None
            use_primary = count_sql
        try:
            async with engine.acquire() as conn:
                if limit_sql is None or use_primary:
                    async with conn.execute(sql) as cursor:
                        if use_primary:
                            row = await cursor.first()
                            data = row if row is None else model_row_to_dict(row)
                            return {'status': 200, 'message': "ok", 'data': data}
                        data = await cursor.fetchall()
                        data = [model_row_to_dict(row) for row in data]
                        return {'status': 200, 'message': "ok", 'data': data}
                else:
                    count = 0
                    async with conn.execute(count_sql) as cursor:
                        count = (await cursor.first()).count
                    async with conn.execute(limit_sql) as cursor:
                        data = await cursor.fetchall()
                        data = [model_row_to_dict(row) for row in data]
                        return {
                            'status': 200,
                            'message': "ok",
                            'data': data,
                            'count': count,
                            'skip': limit[0],
                            'limit': limit[1]
                        }
        except Exception as e:
            return {'status': 500, 'message': str(e)}
        return {'status': 400, 'message': 'param is error'}


Api = Blueprint("api", url_prefix='/api')
