from web_app import app
from . import Api
# from .admin import AdminApi

app.blueprint(Api, url_prefix='/api')
# app.blueprint(AdminApi, url_prefix='/api/admin')

from .admin import admin_router
