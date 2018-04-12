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
from sqlalchemy.sql.expression import bindparam
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
              properties: {}
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
    elif item.status < 0:
        res = {"status": 401, "message": "该用户已冻结!"}
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
async def register(request):
    """
    注册
    ---
    post:
      summary: 注册
      requestBody:
        description: 帐号信息
        required: true
        content:
          application/json:
            schema:
              type: object
              properties: {}
              required: []
      responses:
        200:
          description: 注册成功
          content:
            application/json:
              schema:
                  $ref: '#/components/schemas/baseResponse'
    """
    form_data = request.json
    res = app.form.verify("register", form_data)
    if res is not None:
        return response.json(res, status=res["status"])
    account = form_data["account"]
    role_name = form_data["role_name"]
    model = app.db.get_model("user")
    sql, *_ = model.select(where_data={"$or": {"account": account, "role_name": role_name}})
    # print(sql)
    item = await model.execute_one(sql)
    if item is not None:
        return response.json({"message": "该用户或角色已存在!", "status": 500}, status=500)
    insert_data = {
        "account": account,
        "password": hash_string(form_data["password"]),
        "role_name": role_name,
        "email": form_data["email"],
        "status": 1,
        "permissions": 0,
        "admin": 0,
        "create_time": get_offset_timestamp(),
    }
    sql = model.insert(insert_data)
    res = await model.execute_insert(sql, "注册成功!")
    del res['row_id']
    return response.json(res, status=res["status"])

async def verify_email(request):
    """
    验证邮箱
    """
    token = request.json["token"]
    payload = decode_token(token)
    user_id = payload["user_id"]
    exp = payload["exp"]
    sort = payload["sort"]
    if get_offset_timestamp() < exp:
        res = {
            "status": 400,
            "message": "token已过期!"
        }
    elif sort != 1:
        res = {
            "status": 400,
            "message": "非法token!"
        }
    elif user_id > 0:
        model = app.db.get_model("user")
        sql, *_ = model.select({
            "id": user_id
        })
        item = await model.execute_one(sql)
        if item.status == 0:
            up_sql = model.update_sql({
                "where": {"id", user_id},
                "values": {"status": 1}
            })
            res = await model.execute_dml(up_sql, "验证成功!")
        else:
            res = {
                "status": 400,
                "message": "该用户已冻结!" if item.status < 0 else "该用户已验证!"
            }
    else:
        res = {
            "status": 400,
            "message": "不存在该用户!"
        }
    return response.json(res, status=res["status"])

async def send_verify_email(request):
    """
    发送验证邮件
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

add_route(Api, login, "/login", ["POST"], OPEN_API, "login")
add_route(Api, register, "/register", ["POST"], OPEN_API, "register")
add_route(Api, forgotpwd, "/forgotpwd", ["POST"], OPEN_API)
add_route(Api, refresh_token, "/refresh_token", ['POST'], OPEN_API)
add_route(Api, verify_email, "/verify_email", ['POST'], OPEN_API)

app.blueprint(Api, url_prefix=Api.url_prefix)

from .admin import admin_router
