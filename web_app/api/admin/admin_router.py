from web_app import app, OPEN_API
from . import AdminApi
from web_app.utils import decode_token, get_offset_timestamp
from sanic import response
# from .user_service import UserService
# from .library_service import LibraryService

app.db.model_add_view(AdminApi, OPEN_API)
# UserService.add_route(AdminApi, OPEN_API)
# LibraryService.add_route(AdminApi, OPEN_API)
app.blueprint(AdminApi)
# AdminApi.add_route(UserService.as_view(), "/user")
# AdminApi.add_route(UserService.as_view(), "/user/<primary_key:int>")

