#!/bin/env python
# coding: utf-8

"""
web服务
"""
import os
import sys
from sanic import Sanic
# from sanic_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor
from aiosqlite3.sa import create_engine
from .config import CONFIG

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

app = Sanic(__name__)

@app.listener('before_server_start')
async def init_graphql(app, loop):
    # from .schema import Schema
    init = os.path.exists(CONFIG['DB'])
    app.engine = await create_engine(CONFIG['DB'], loop=loop)
    if not init:
        from sqlalchemy.sql.ddl import CreateTable
        from .models import __all__ as models
        async with app.engine.acquire() as conn:
            for table in models:
                import_name = "web_app.models.%s" % table
                table_module = import_string(import_name)
                await conn.execute(CreateTable(table_module))
    # app.add_route(
    #     GraphQLView.as_view(
    #         schema=Schema,
    #         executor=AsyncioExecutor(loop=loop)
    #     ),
    #     '/graphql'
    # )

@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    if app.engine:
        app.engine.close()
        await app.engine.wait_closed()
        app.engine = None

@app.middleware('request')
async def cros(request):
    app.conn = await app.engine.acquire()

@app.middleware('response')
async def cors_res(request, response):
    if app.conn:
        await app.conn.close()
        app.conn = None
