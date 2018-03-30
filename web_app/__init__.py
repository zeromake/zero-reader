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
from .utils import root_resolve, decode_token, get_offset_timestamp
from .form import Form
import psutil

app = Sanic(__name__)
app.db = DateBase(CONFIG['DB'])
app.form = Form(root_resolve("../form"))
app.process = psutil.Process()


# @app.middleware("request")
# async def admin_request(request):
#     """
#     校验token
#     """
#     is_admin = request.path.startswith("/api/admin")
#     if is_admin or request.path.startswith("/api/public"):
#         authorization = request.headers.get("authorization")
#         if authorization is None:
#             return response.json({
#                 "status": 401,
#                 "message": "token没有传递!"
#             }, status=401)
#         res = None
#         try:
#             payload = decode_token(authorization)
#             timestamp_now = get_offset_timestamp()
#             if payload.get("refresh", False):
#                 res = {
#                     "status": 401,
#                     "message": "refresh_token无法用于认证!"
#                 }
#             elif timestamp_now >= payload["exp"]:
#                 res = {
#                     "status": 401,
#                     "message": "token已过期请重新登录!"
#                 }
#             elif not payload["admin"] and is_admin:
#                 res = {
#                     "status": 401,
#                     "message": "只有管理员才能访问该接口!"
#                 }
#         except Exception as e:
#             print(e)
#             res = {
#                 "status": 500,
#                 "message": "无法解析token!"
#             }
#         if res:
#             return response.json(res, status=res['status'])

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
    api_doc = ""
    try:
        with open(root_resolve("./openapi.md"), encoding="utf8") as fd:
            api_doc = fd.read()
    except Exception as e:
        api_doc = "api doc"
    OPEN_API = ApiSpec(
        "zero-reader api",
        api_doc,
        "0.1.0"
    )
    OPEN_API.add_schema("optParam", {
        "type": "string",
        "description": "运算符",
        "required": True,
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
            "$nin",
            "$bind"
        ]
    })
    OPEN_API.add_schema("anyParam", {
        "oneOf": [
            {
                "required": True,
                "type": "integer"
            },
            {
                "required": True,
                "type": "float"
            },
            {
                "required": True,
                "type": "string"
            }
        ]
    })
    OPEN_API.add_schema("whereParam", {
        "oneOf": [
            {
                "$ref": "#/components/schemas/anyParam"
            },
            {
                "type": "object",
                "properties": {
                    "val": {
                        "description": "数值",
                        "required": True,
                        "oneOf":[
                            {
                                "$ref": "#/components/schemas/anyParam"
                            },
                            {
                                "type": "object",
                                "description": "$bind对应的占位key设置",
                                "properties": {
                                    "val": {
                                        "description": "占位key",
                                        "type": "string"
                                    },
                                    "opt": {
                                        "$ref": "#/components/schemas/optParam"
                                    }
                                }
                            },
                            {
                                "type": "array",
                                "items": {
                                    "oneOf": [
                                        {"$ref": "#/components/schemas/anyParam"}
                                    ]
                                }
                            }
                        ]
                    },
                    "opt": {
                        "$ref": "#/components/schemas/optParam"
                    }
                }
            }
        ]
    })
    OPEN_API.add_schema("whereData", {
        "type": "object",
        "description": "",
        "properties": {
            "$or": {
                "type": "object",
                "description": "sql 的 OR",
                "additionalProperties": {
                    "$ref": "#/components/schemas/whereParam"
                }
            },
            "$and": {
                "type": "object",
                "description": "sql 的 AND",
                "additionalProperties": {
                    "$ref": "#/components/schemas/whereParam"
                }
            }
        },
        "additionalProperties": {
            "$ref": "#/components/schemas/whereParam"
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
    OPEN_API.add_response("baseResponse", {
        "description": "通用响应",
        "content": {
            "application/json": {
                "schema": {
                   "$ref": "#/components/schemas/baseResponse"
                }
            }
        }
    })
    OPEN_API.add_security_schemes("TokenAuth", {
        "type": "apiKey",
        "in": "header",
        "name": "authorization"
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
    @app.route("/ui.json", methods=["GET"])
    def openapi(request):
        """
        api文档
        """
        return response.json(OPEN_API.to_dict())
    app.static("/ui/", root_resolve("./assets/ui"), name="ui")

from . import router
