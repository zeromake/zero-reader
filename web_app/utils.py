import os
import sys
import sqlalchemy as sa
from sqlalchemy import or_, and_
from sqlalchemy.sql.expression import bindparam
import jwt
from sanic import response
from web_app.config import CONFIG
from . import crypt_zero as passlib_hash
from datetime import datetime, timedelta, timezone
from jinja2 import Environment, PackageLoader, select_autoescape
from io import StringIO
import yaml

custom_app_context = getattr(passlib_hash, CONFIG.get('HASH', "md5_crypt"))

jinja2_env = Environment(
    loader=PackageLoader('web_app', '../dist'),
    autoescape=select_autoescape(['html'])
)
__all__ = [
    "ROOT_PATH",
    "root_resolve",
    "make_columns",
    "handle_param",
    "handle_param_desc",
    "handle_param_primary",
    "handle_keys",
    "generate_openapi_by_column",
    "generate_openapi_by_table",
    "encode_token",
    "decode_token",
    "hash_string",
    "verify_hash"
]

OPEN_METHOD = {
    "get:",
    "post:",
    "delete:",
    "put:"
}

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

def root_resolve(*path: str):
    """
    获取绝对路径(以${project_dir}/web_app/起始)
    """
    return os.path.join(ROOT_PATH, *path)

def make_columns(table):
    """
    取出table中的columns
    """
    return [column for column in table.columns]

def handle_param(column, data):
    """
    处理where条件
    """
    opt = data.get('opt', '$te')
    if 'val' in data:
        value = data['val']
        if opt == '$ne': # 不等于
            return column != value
        if opt == '$te': # 等于
            return column == value
        elif opt == '$lt': # 小于
            return column < value
        elif opt == '$lte': # 小于等于
            return column <= value
        elif opt == '$gt': # 大于
            return column > value
        elif opt == '$gte': # 大于等于
            return column >= value
        elif opt == '$like': # like
            return column.like(value)
        elif opt == '$in':
            return column.in_(value)
        elif opt == '$nin':
            return ~column.in_(value)
        elif opt == '$bind':
            # 占位符
            if isinstance(value, str):
                return column == bindparam(value)
            else:
                opt = value["opt"]
                if opt == '$bind':
                    return None
                if opt == "$in" or opt == "$nin":
                    value["val"] = bindparam(value["val"], expanding=True)
                else:
                    value["val"] = bindparam(value["val"])
                return handle_param(column, value)
        elif opt == '$raw':
            return value

def handle_param_desc(column, data):
    """
    处理参数类型
    """
    params = []
    if isinstance(data, list):
        if len(data) > 0:
            if isinstance(data[0], dict):
                for row in data:
                    param = handle_param(column, row)
                    if not param is None:
                        params.append(param)
            else:
                data.append(column.in_(data))
    elif isinstance(data, dict):
        param = handle_param(column, data)
        if not param is None:
            params.append(param)
    else:
        params.append(column==data)
    params_len = len(params)
    if params_len == 0:
        return
    elif params_len == 1:
        return params[0]
    elif params_len > 1:
        return params

def handle_param_primary(column_name, form_data, is_or=False):
    """
    处理带主键的参数
    """
    data = []
    for key, val in form_data.items():
        if key in column_name:
            column = column_name[key]
            params = handle_param_desc(column, val)
            if not params is None:
                if isinstance(params, list):
                    data.append(and_(params))
                else:
                    data.append(params)
        elif key == "$or" and isinstance(val, dict):
            params = handle_param_primary(column_name, val, True)
            if not params is None:
                data.append(params)
        elif key == "$and" and isinstance(val, dict):
            params = handle_param_primary(column_name, val, False)
            if not params is None:
                data.append(params)
    data_len = len(data)
    if data_len == 1:
        return data[0]
    elif data_len > 1:
        return or_(*data) if is_or else and_(*data)

def handle_keys(column_name, keys_string):
    """
    处理
    """
    key_set = set()
    keys = keys_string.split(",")
    is_block = False
    for key in keys:
        if key != "" and key[0] == "-":
            is_block = True
            key = key[1:]
        if key in column_name:
            key_set.add(key)
    if is_block:
        key_arr = [column for key, column in column_name.items() if key not in key_set]
    else:
        key_arr = [column_name[key] for key in key_set]
    if len(key_arr) > 0:
        return key_arr


def generate_openapi_by_column(column):
    """
    处理column生成openapi propertie对象
    """
    propertie = {
        "description": column.doc
    }

    column_type = column.type
    type_string = None
    if isinstance(column_type, sa.BigInteger):
        propertie['format'] = "int64"
        type_string = "integer"
    elif isinstance(column_type, sa.Integer):
        propertie['format'] = "int32"
        type_string = "integer"
    elif isinstance(column_type, sa.Float):
        propertie['format'] = "float"
        type_string = "number"
    elif isinstance(column_type, sa.Boolean):
        type_string = "boolean"
    elif isinstance(column_type, sa.Date):
        type_string = "string"
        propertie['format'] = "float"
    elif isinstance(column_type, sa.Time):
        propertie['format'] = "time"
        type_string = "string"
    elif isinstance(column_type, (sa.DateTime, sa.TIMESTAMP)):
        propertie['format'] = "data-time"
        type_string = "string"
    elif isinstance(column_type, sa.Text):
        type_string = "string"
    elif isinstance(column_type, sa.String):
        propertie['maxLength'] = column_type.length
        type_string = "string"
    propertie['type'] = type_string
    return propertie

def generate_openapi_by_table(table, blacklist=None, whitelist=None):
    """
    把model转为openapi的schema
    """
    schema = {
        "type": "object",
        "properties": {},
        "description": table.__doc__,
        "required": []
    }
    filterlist = blacklist or whitelist
    is_black = blacklist is not None
    for column in table.columns:
        column_name = str(column.name)
        flag = True
        if filterlist:
            if column_name in filterlist:
                if is_black:
                    flag = False
            elif not is_black:
                flag = False
        if flag:
            if not column.nullable and not column.primary_key:
                schema['required'].append(column_name)
            schema['properties'][column_name] = generate_openapi_by_column(column)
    return schema

def encode_token(payload: dict, algorithm: str='HS256', **kwargs: dict)-> str:
    """
    生成token
    """
    return jwt.encode(payload, CONFIG['SECRET'], algorithm=algorithm, **kwargs).decode()

def decode_token(jwt_payload: str, algorithm: str='HS256', **kwargs: dict)-> dict:
    """
    读取payload
    """
    return jwt.decode(jwt_payload.encode(), CONFIG['SECRET'], algorithm=algorithm, **kwargs)

def hash_string(string: str)-> str:
    """
    hash密码
    """
    return custom_app_context.hash(string)

def verify_hash(string: str, hash_str: str):
    """
    校验hash与当前的密码
    """
    return custom_app_context.verify(string, hash_str)

def to_timestamp(obj: datetime):
    """
    毫秒值
    """
    return int(obj.timestamp() * 1000)

def get_offset_timestamp(**kwargs):
    """
    获取偏移时间戳
    """
    return to_timestamp(datetime.now(timezone.utc) + timedelta(**kwargs))

def template(name: str, headers: dict=None, **kwargs: dict):
    """
    jinja2_env
    """
    template_obj = jinja2_env.get_template(name)
    return response.html(template_obj.render(kwargs), headers=headers)

def generate_openapi_by_def(handler):
    """
    生成
    """
    doc = StringIO(handler.__doc__)
    line = doc.readline()
    gen = []
    space = 0
    flag = False
    while line:
        if line.endswith("---\n"):
            space = len(line) - 4
            flag = True
            line = doc.readline()
        if flag:
            if space > 0 and len(line) > space:
                line = line[space:]
            gen.append(line)
        line = doc.readline()
    if len(gen) > 0:
        text = "".join(gen)
        return yaml.load(text)
    return None

def extend_dict(target, *args):
    for arg in args:
        if isinstance(arg, dict):
            for key, val in arg.items():
                target[key] = val
    return target

def get_deep_obj(target, key_name, split="."):
    """
    获取深层对象
    """
    temp = target
    key_arr = key_name.split(split)
    for key in key_arr:
        if isinstance(temp, dict) and key in temp:
            temp = temp[key]
        else:
            temp = None
            break
    return temp
        

def add_route(context, handler, url, methods=None, openApi=None, form_name=None):
    """
    添加路由
    """
    if openApi:
        doc = generate_openapi_by_def(handler)
        url_prefix = context.url_prefix
        if doc:
            if form_name:
                from web_app import app
                schema = app.form.generate_schema(form_name)
                for method in OPEN_METHOD:
                    method = method[:-1]
                    key = ".".join([method, "requestBody", "content"])
                    temp = get_deep_obj(doc, key)
                    if temp:
                        for _, content in temp.items():
                            if "schema" in content:
                                schemas = content["schema"]
                                extend_dict(schemas["properties"], schema["properties"])
                                if "required" in schemas:
                                    schemas["required"].extend(schema["required"])
            openApi.add_path(url_prefix + url, doc)
    context.add_route(handler, url, methods)
