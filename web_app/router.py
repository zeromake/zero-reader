"""
一些静态文件和自动加载路由
"""
import os
from sanic import response
from sanic.exceptions import NotFound

from . import app
from .utils import root_resolve

app.static("/", root_resolve("../dist/index.html"), name="index")
app.static("/assets/", root_resolve("../dist/assets"), name="static")
app.static("/librarys/", root_resolve("../library"), name="librarys")

@app.exception(NotFound)
async def fall_back(request, exception):
    """
    全部重定向到index.html
    """
    return await response.file(root_resolve("../dist/index.html"))

# @app.route("/librarys/<file_uri:/?.+>", methods=["GET", "OPTIONS"])
# async def library(request, file_uri):
#     print(file_uri)
#     file_path = os.path.join(root_resolve("../library"), file_uri)
#     return await response.file(file_path)

from web_app.api import api_router
