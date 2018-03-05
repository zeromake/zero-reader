"""
一些静态文件和自动加载路由
"""
import json
import os
from sanic import response
from sanic.exceptions import NotFound

from . import app
from .utils import root_resolve, template

# app.static("/", root_resolve("../dist/index.html"), name="index")
app.static("/assets/", root_resolve("../dist/assets"), name="static")
app.static("/librarys/", root_resolve("../librarys"), name="librarys")
# app.config.project = json.dumps({"sign_up": True, "sign_up_code": True})
app.config.project = "null"

@app.route("/")
def index(request):
    return template("index.html", config=app.config.project)

@app.route("/config")
async def index(request):
    return response.text(
        app.config.project,
        headers= {
            'Content-Type': 'application/json'
        }
    )

@app.exception(NotFound)
def fall_back(request, exception):
    """
    全部重定向到index.html
    """
    return template("index.html", config=app.config.project)

# @app.route("/librarys/<file_uri:/?.+>", methods=["GET", "OPTIONS"])
# async def library(request, file_uri):
#     print(file_uri)
#     file_path = os.path.join(root_resolve("../library"), file_uri)
#     return await response.file(file_path)

from web_app.api import api_router
