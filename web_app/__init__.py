#!/bin/env python
# coding: utf-8

"""
web服务
"""

from sanic import Sanic
from sanic_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor
from aiosqlite3.sa import create_engine
from .config import CONFIG


app = Sanic(__name__)

@app.listener('before_server_start')
async def init_graphql(app, loop):
    from .schema import Schema
    app.engine = await create_engine(CONFIG['DB'], loop=loop)
    app.add_route(
        GraphQLView.as_view(
            schema=Schema,
            executor=AsyncioExecutor(loop=loop)
        ),
        '/graphql'
    )

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
