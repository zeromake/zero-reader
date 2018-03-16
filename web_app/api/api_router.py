"""
无需登录的api 如登录，注册，验证码，email验证，安装引导
"""
from web_app import app, OPEN_API
from . import Api
from sanic import response
from ..utils import (
    encode_token,
    decode_token,
    verify_hash,
    hash_string,
    get_offset_timestamp,
    add_route
)
from datetime import datetime, timedelta, timezone
# from .admin import AdminApi

# @Api.route("/login", methods=['POST'])
async def login(request):
    """
    登录
    ---
    post:
      summary: 登录
      requestBody:
        description: 帐号密码
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                account:
                  type: string
                  description: 帐号
                password:
                  type: string
                  description: 密码
      responses:
        200:
          description: 登录成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/baseResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        description: token数据
                        properties:
                          token:
                            type: string
                            description: 认证token
                          refresh_token:
                            type: string
                            description: 刷新token
                          exp:
                            type: integer
                            description: token过期时间
                          refresh_exp:
                            type: integer
                            description: token过期时间
        default:
          $ref: '#/components/responses/baseResponse'
    """
    form_data = request.json
    res = app.form.verify("login", form_data)
    if res:
        return response.json(res, status=res['status'])
    account = form_data.get("account")
    password = form_data.get("password")
    model = app.db.get_model("user")
    sql, *_ = model.select(where_data={"account": account})
    item = await model.execute_one(sql)
    # print("----", hash_string(password))
    if item is None:
        res = {"status": 400, "message": "未找到该用户!"}
    elif item.status == 0:
        res = {"status": 401, "message": "该用户未验证!"}
    else:
        try:
            is_verify = verify_hash(password, item.password)
        except Exception:
            is_verify = False
        if is_verify:
            exp = get_offset_timestamp(minutes=30)
            token = encode_token({
                "account": account,
                "admin": item.admin,
                "refresh": False,
                "exp": exp
            })
            refresh_exp = get_offset_timestamp(days=1)
            refresh_token = encode_token({
                "account": account,
                "refresh": True,
                "exp": refresh_exp
            })
            res = {
                "status": 200,
                "message": "Login ok!",
                "data": {
                    "token": token,
                    "refresh_token": refresh_token,
                    "exp": exp,
                    "refresh_exp": refresh_exp
                }
            }
        else:
            res = {"status": 400, "message": "密码错误!"}
    return response.json(res, status=res['status'])

# @Api.route("/sign_up", methods=['POST'])
async def sign_up(request):
    """
    注册
    """

async def forgotpwd(request):
    """
    忘记密码
    """

# @Api.route("/refresh_token", methods=['POST', 'GET'])
async def refresh_token(request):
    """
    刷新token
    ---
    post:
      summary: 刷新token
      security:
        - TokenAuth: []
      responses:
        200:
          description: 续期成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/baseResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        description: token数据
                        properties:
                          token:
                            type: string
                            description: 认证token
                          exp:
                            type: integer
                            description: token过期时间
        default:
          $ref: '#/components/responses/baseResponse'
    """
    authorization = request.headers.get("authorization", "")
    try:
        payload = decode_token(authorization)
        timestamp_now = get_offset_timestamp()
        if timestamp_now >= payload["exp"]:
            res = {
                "status": 401,
                "message": "token已过期请重新登录!"
            }
        else:
            account = payload["account"]
            model = app.db.get_model("user")
            sql, *_ = model.select(where_data={"account": account})
            item = await model.execute_one(sql)
            if item is None:
                res = {
                    "status": 500,
                    "message": "该用户不存在!"
                }
            else:
                exp = get_offset_timestamp(minutes=30)
                token = encode_token({
                    "account": account,
                    "admin": item.admin,
                    "refresh": False,
                    "exp": exp
                })
                res = {
                    "status": 200,
                    "message": "token续期成功!",
                    "data": {
                        "exp": exp,
                        "token": token
                    }
                }
    except Exception:
        res = {
            "status": 401,
            "message": "token无法解析"
        }
    return response.json(res, status=res['status'])

add_route(Api, login, "/login", ["POST"], OPEN_API)
add_route(Api, sign_up, "/sign_up", ["POST"], OPEN_API)
add_route(Api, forgotpwd, "/forgotpwd", ["POST"], OPEN_API)
add_route(Api, refresh_token, "/refresh_token", ['POST'], OPEN_API)

app.blueprint(Api, url_prefix=Api.url_prefix)
# app.blueprint(AdminApi, url_prefix='/api/admin')

from .admin import admin_router
