import os
import sys
from sqlalchemy import or_

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
    opt = data.get('opt', '==')
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

def handle_param_primary(columns, form_data):
    """
    处理带主键的参数
    """
    data = []
    column_name = {column.name: column for column in columns}
    for key, val in form_data:
        if key in column_name:
            column = column_name[key]
            if isinstance(val, list):
                if len(val) > 0:
                    if isinstance(val[0], dict):
                        for row in val:
                            param = handle_param(column, row)
                            if not param is None:
                                data.append(param)
                    else:
                        data.append(column.in_(val))
            elif isinstance(val, dict):
                param = handle_param(column, val)
                if not param is None:
                    data.append(param)
            else:
                data.append(column==val)
        elif key == "$or" and isinstance(val, dict):
            params = []
            for column_key, row in val.items():
                if column_key in column_name:
                    column = column_name[column_key]
                    params.append(handle_param(column, row))
            params_len = len(params)
            if params_len == 1:
                data.append(params[0])
            elif params_len > 1:
                data.append(or_(*params))
    is_use = len(data) > 0
    return data, is_use
