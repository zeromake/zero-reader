#!/bin/env python
# coding: utf-8

"""
web服务
"""
import os
import sys
import asyncio
from sanic import Sanic
# from sanic_graphql import GraphQLView
from .config import CONFIG
from .db import DateBase

app = Sanic(__name__)
app.__model__ = {}

@app.listener('before_server_start')
async def before_server_start(app, loop):
    init = os.path.exists(CONFIG['FILE'])
    data_base = DateBase(CONFIG['DB'], loop)
    app.engine = await data_base.create_engine()
    if not init:
        await data_base.create_table(app.engine)
        with open(CONFIG['FILE'], 'w') as FILE:
            FILE.write("0")

@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    if app.engine:
        app.engine.close()
        await app.engine.wait_closed()
        app.engine = None

from . import router
