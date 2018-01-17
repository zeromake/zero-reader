from web_app import app
from . import AdminApi
from .user_service import UserService

UserService.add_route(AdminApi, "/user")
# AdminApi.add_route(UserService.as_view(), "/user")
# AdminApi.add_route(UserService.as_view(), "/user/<primary_key:int>")

app.blueprint(AdminApi, url_prefix='/api/admin')
