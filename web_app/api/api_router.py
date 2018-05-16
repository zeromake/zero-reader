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

def verify_token(payload: dict, sort: int) -> str:
    """
    校验payload
    """
    user_id = payload["user_id"]
    exp = payload["exp"]
    sort_ = payload["sort"]
    if get_offset_timestamp() < exp:
        res = "token已过期!"
    elif user_id <= 0:
        res = "不存在该用户!"
    elif sort_ != sort:
        res = "非法token类型!"
    else:
        res = None
    return res

async def verify_email(request):
    """
    验证邮箱
    ---
    post:
      summary: 验证邮箱
      requestBody:
        description: 帐号信息
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                token:
                  type: string
                  description: token
              required: [token]
      responses:
        200:
          description: 验证成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/baseResponse'
        default:
          $ref: '#/components/responses/baseResponse'
    """
    token = request.json["token"]
    payload = decode_token(token)
    user_id = payload["user_id"]
    # sort = payload["sort"]
    message = verify_token(payload, 1)
    if message:
        res = {
            "status": 400,
            "message": message
        }
    else:
        model = app.db.get_model("user")
        sql, *_ = model.select({
            "id": user_id
        })
        item = await model.execute_one(sql)
        if item is not None:
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

async def reset_passwd(request):
    """
    重置密码
    ---
    post:
      summary: 重置密码
      requestBody:
        description: 帐号信息
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                token:
                  type: string
                  description: token
                password:
                  type: string
                  description: 新密码
              required: [token, password]
      responses:
        200:
          description: 重置成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/baseResponse'
        default:
          $ref: '#/components/responses/baseResponse'
    """
    token: str = request.json["token"]
    password: str = request.json["password"]
    payload: dict = decode_token(token)
    user_id: int = payload["user_id"]
    message: str = verify_token(payload, 2)
    if message:
        res = {
            "status": 400,
            "message": message
        }
    else:
        model = app.db.get_model("user")
        sql = model.update_sql({
            "where": {"id": user_id},
            "values": {"password", hash_string(password)}
        })
        res = await model.execute_dml(sql, "重置密码成功!")
    return response.json(res, status=res["status"])


async def forgotpwd(request):
    """
    忘记密码
    ---
    post:
      summary: 忘记密码
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
          description: 发送重置邮件成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/baseResponse'
        default:
          $ref: '#/components/responses/baseResponse'
    """
    form_data = request.json
    res = app.form.verify("forgotpwd", form_data)
    if res:
        return response.json(res, res['status'])
    # account = res["account"]
    model = app.db.get_model("user")
    sql, *_ = model.select(where_data=form_data)
    item = await model.execute_one(sql)
    if item is None:
        res = {
            "message": "未找到该用户！",
            "status": 400,
        }
    else:
        status = app.email.send_email(
            item.email,
            "分-段-富贵花！",
            "He-llo",
        )
        res = {
            "message": "已发送重置密码邮件！",
            "status": 200,
        } if status else {
            "message": "邮件发送失败",
            "status": 500,
        }
    return response.json(res, res['status'])


# @Api.route("/refresh_token", methods=['POST', 'GET'])
async def refresh_token(request):
    """
    刷新token
    ---
    post:
      summary: 刷新token
      requestBody:
        description: 帐号信息
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                Authorization:
                  type: string
                  description: refresh token
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
    authorization = request.json.get("Authorization", "")
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
add_route(Api, forgotpwd, "/forgotpwd", ["POST"], OPEN_API, 'forgotpwd')
add_route(Api, refresh_token, "/refresh_token", ['POST'], OPEN_API)
add_route(Api, verify_email, "/verify_email", ['POST'], OPEN_API)
add_route(Api, reset_passwd, "/reset_passwd", ['POST'], OPEN_API)
add_route(Api, send_verify_email, "/send_verify_mail", ["POST"], OPEN_API)

app.blueprint(Api, url_prefix=Api.url_prefix)

from .admin import admin_router
