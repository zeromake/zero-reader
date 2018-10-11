"""
一些静态文件和自动加载路由
"""
import json
import os
import asyncio
from sanic import response
from mimetypes import guess_type
from sanic.exceptions import NotFound

from . import app
from .utils import root_resolve, template
from .zero_copy import zero_copy_stream

# app.static("/", root_resolve("../dist/index.html"), name="index")
app.static("/assets/", root_resolve("../dist/assets"), name="static")
# app.static("/api/librarys/", root_resolve("../librarys"), name="librarys")
app.config.project = "<script type=\"text/javascript\" src=\"/config.js\"></script>"

app.config.projectConfig = json.dumps({
    "sign_up": True,
    "sign_up_code": True,
})

CSP = "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline';"
# app.config.url = "http://reader.zeromake.com"
# app.config.project = "null"

def safe_file_path(file_uri: str):
    if '..' not in file_uri:
        return file_uri
    new_path = []
    path_arr = os.path.split(file_uri)
    path_len = 0
    for path in path_arr:
        if path == '..':
            if path_len > 0:
                new_path.pop()
                path_len -= 1
        else:
            new_path.append(path)
            path_len += 1
    return os.path.join(*new_path)

@app.route("/api/librarys/<file_uri:\/?.+>")
async def librarys(request, file_uri):
    file_name = root_resolve("..", "librarys", safe_file_path(file_uri))
    # print(file_name)
    # if file_uri.endswith(".png"):
    #     await asyncio.sleep(2)
    return await zero_copy_stream(file_name, chunked=False)

@app.route("/")
def index(request):
    return template("index.html", headers={
        # "Content-Security-Policy": CSP
    }, config=app.config.project)

@app.route("/config.js")
def config(request):
    return response.text(
        "window.projectConfig=" + app.config.projectConfig,
        headers= {
            'Content-Type': 'text/javascript'
        }
    )

@app.route("/config")
def index_(request):
    return response.text(
        app.config.projectConfig,
        headers= {
            'Content-Type': 'application/json'
        }
    )

@app.exception(NotFound)
def fall_back(request, exception):
    """
    全部重定向到index.html
    """
    return template("index.html", headers={
        # "Content-Security-Policy": CSP
    }, config=app.config.project)

# @app.route("/librarys/<file_uri:/?.+>", methods=["GET", "OPTIONS"])
# async def library(request, file_uri):
#     print(file_uri)
#     file_path = os.path.join(root_resolve("../library"), file_uri)
#     return await response.file(file_path)

from web_app.api import api_router
