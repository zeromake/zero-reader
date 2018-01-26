import os
import sys
import sqlalchemy as sa
from sqlalchemy import or_, and_

__all__ = ["import_string", "ROOT_PATH"]

def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).
    If `silent` is True the return value will be `None` if the import fails.
    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    # force the import name to automatically convert to strings
    # __import__ is not able to handle unicode strings in the fromlist
    # if the module is a package
    import_name = str(import_name).replace(':', '.')
    try:
        try:
            __import__(import_name)
        except ImportError:
            if '.' not in import_name:
                raise
        else:
            return sys.modules[import_name]

        module_name, obj_name = import_name.rsplit('.', 1)
        try:
            module = __import__(module_name, None, None, [obj_name])
        except ImportError:
            # support importing modules not yet set up by the parent module
            # (or package for that matter)
            module = import_string(module_name)

        try:
            return getattr(module, obj_name)
        except AttributeError as e:
            raise ImportError(e)

    except ImportError as e:
        if not silent:
            raise e
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

def root_resolve(path):
    """
    获取绝对路径(以${project_dir}/web_app/起始)
    """
    return os.path.join(ROOT_PATH, path)

def make_columns(table):
    """
    取出table中的columns
    """
    return [column for column in table.columns]

def handle_param(column, data):
    """
    处理where条件
    """
    opt = data.get('opt', '$lt')
    if 'val' in data:
        value = data['val']
        if opt == '$ne': # 不等于
            return column != value
        if opt == '$lt': # 等于
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
            like_str = value if value.startswith("%") else "%%%s%%" % value
            return column.like(like_str)
        elif opt == '$in':
            return column.in_(value)
        elif opt == '$nin':
            return ~column.in_(value)
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
    elif isinstance(column_type, sa.String):
        propertie['maxLength'] = column_type.length
        type_string = "string"
    elif isinstance(column_type, sa.Text):
        type_string = "string"
    propertie['type'] = type_string
    return propertie

def generate_openapi_by_table(table):
    """
    把model转为openapi的schema
    """
    schema = {
        "type": "object",
        "properties": {},
        "required": []
    }
    for column in table.columns:
        column_name = str(column.name)
        if not column.nullable and not column.primary_key:
            schema['required'].append(column_name)
        schema['properties'][column_name] = generate_openapi_by_column(column)
    return schema

