from web_app import app, OPEN_API
from . import AdminApi
from .user_service import UserService

UserService.add_route(AdminApi, "/user", OPEN_API)
app.blueprint(AdminApi, url_prefix=AdminApi.url_prefix)
# AdminApi.add_route(UserService.as_view(), "/user")
# AdminApi.add_route(UserService.as_view(), "/user/<primary_key:int>")

