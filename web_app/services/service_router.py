from web_app import app
from .user_service import UserService

app.add_route(UserService.as_view(), '/user')
