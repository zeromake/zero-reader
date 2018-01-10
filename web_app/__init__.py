#!/bin/env python
# coding: utf-8

"""
web服务
"""
import os
import sys
from sanic import Sanic
# from sanic_graphql import GraphQLView
from .config import CONFIG
from .db import DateBase

app = Sanic(__name__)

@app.listener('before_server_start')
async def init_graphql(app, loop):
    # from .schema import Schema
    init = os.path.exists(CONFIG['FILE'])
    data_base = DateBase(CONFIG['DB'], loop)
    app.engine = await data_base.create_engine()
    if not init:
        await data_base.create_table(app.engine)
        with open(CONFIG['FILE'], 'w') as FILE:
            FILE.write("0")
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
