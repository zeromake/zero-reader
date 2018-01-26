#!/bin/env python
# coding: utf-8

"""
web服务
"""
import os
import sys
import asyncio
from sanic import Sanic, response
# from sanic_graphql import GraphQLView
from .config import CONFIG
from .db import DateBase
from .apispec import ApiSpec

app = Sanic(__name__)
app.__model__ = {}

@app.listener('before_server_start')
async def before_server_start(app, loop):
    init = os.path.exists(CONFIG['FILE'])
    data_base = DateBase(CONFIG['DB'], loop)
    app.db = data_base
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



OPEN_API = ApiSpec(
    "zero-reader api",
    "api doc",
    "0.1.0"
)
OPEN_API.add_parameters("where", {
    "in": "query",
    "name": "where",
    "content": {
        "application/json":
        {
            "schema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                    }
                }
            }
        }
    }

})
OPEN_API.add_schema("baseResponse", {
    "type": "object",
    "properties": {
        "status": {
            "description": "状态码",
            "type": "integer"
        },
        "message": {
            "description": "消息",
            "type": "string"
        }
    }
})

@app.route("/ui.json", methods=["GET"])
def openapi(request):
    """
    api文档
    """
    return response.json(OPEN_API.to_dict())

from . import router
