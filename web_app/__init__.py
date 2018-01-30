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
from .utils import root_resolve

app = Sanic(__name__)
app.db = DateBase(CONFIG['DB'])

@app.listener('before_server_start')
async def before_server_start(app, loop):
    init = os.path.exists(CONFIG['FILE'])
    app.engine = await app.db.create_engine(loop)
    if not init:
        await app.db.create_table(app.engine)
        with open(CONFIG['FILE'], 'w') as FILE:
            FILE.write("0")

@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    if app.engine:
        app.engine.close()
        await app.engine.wait_closed()
        app.engine = None

OPEN_API = None
if CONFIG['OPEN_API']:
    OPEN_API = ApiSpec(
        "zero-reader api",
        "api doc",
        "0.1.0"
    )
    OPEN_API.add_schema("whereParam", {
        "type": "object",
        "properties": {
            "val": {
                "description": "数值",
                "oneOf":[
                    {
                        "type": "integer"
                    },
                    {
                        "type": "float"
                    },
                    {
                        "type": "string"
                    },
                    {
                        "type": "array",
                        "items": {
                            "oneOf": [
                                {"type": "integer"},
                                {"type": "float"},
                                {"type": "string"}
                            ]
                        }
                    }
                ]
            },
            "opt": {
                "type": "string",
                "description": "运算符",
                "enum": [
                    "$raw",
                    "$ne",
                    "$te",
                    "$lt",
                    "$lte",
                    "$gt",
                    "$gte",
                    "$like",
                    "$in",
                    "$nin"
                ]
            }
        }
    })
    OPEN_API.add_parameters("order", {
        "in": "query",
        "name": "order",
        "description": "排序字段,带 `-` 为倒序",
        "schema": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "style": "form",
        "explode": False
    })
    OPEN_API.add_parameters("keys", {
        "in": "query",
        "name": "keys",
        "description": "过滤字段,带 `-` 为黑名单",
        "schema": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "style": "form",
        "explode": False
    })
    OPEN_API.add_parameters("limit", {
        "in": "query",
        "name": "limit",
        "description": "取出多少条",
        "schema": {
            "type": "integer",
            "default": 50
        }
    })
    OPEN_API.add_parameters("skip", {
        "in": "query",
        "name": "skip",
        "description": "略过多少条",
        "schema": {
            "type": "integer",
            "default": 0
        }
    })
    OPEN_API.add_parameters("where", {
        "in": "query",
        "name": "where",
        "description": "过滤条件",
        "content": {
            "application/json":
            {
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "$ref": "#/components/schemas/whereParam",
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
    app.static("/ui/", root_resolve("./assets/ui"), name="ui")

from . import router
