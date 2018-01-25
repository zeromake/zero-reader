from web_app import app
from . import AdminApi
from .user_service import UserService

UserService.add_route(AdminApi, "/user")
app.blueprint(AdminApi, url_prefix=AdminApi.url_prefix)
# AdminApi.add_route(UserService.as_view(), "/user")
# AdminApi.add_route(UserService.as_view(), "/user/<primary_key:int>")

