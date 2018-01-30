"""
无需登录的api 如登录，注册，验证码，email验证，安装引导
"""
from web_app import app
from . import Api
from sanic import response
from ..utils import encode_token, verify_hash, hash_string
from datetime import datetime, timedelta
# from .admin import AdminApi

@Api.route("/login", methods=['POST'])
async def login(request):
    """
    登录
    """
    form_data = request.json
    account = form_data.get("account")
    password = form_data.get("password")
    model = app.db.get_model("user")
    sql, *_ = model.select(where_data={"account": account})
    item = await model.execute_one(sql)
    print("----", hash_string(password))
    if item is None:
        res = {"status": 400, "message": "未找到该用户!"}
    else:
        try:
            is_verify = verify_hash(password, item.password)
        except Exception:
            is_verify = False
        if is_verify:
            token = encode_token({
                "account": account,
                "admin": item.admin,
                'exp': datetime.utcnow() + timedelta(hours=1)
            })
            res = {"status": 200, "message": "Login ok!", "token": token}
        else:
            res = {"status": 400, "message": "密码错误!"}
    return response.json(res, status=res['status'])


app.blueprint(Api, url_prefix='/api')
# app.blueprint(AdminApi, url_prefix='/api/admin')

from .admin import admin_router
