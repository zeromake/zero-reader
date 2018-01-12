from web_app.models import User
from . import ApiView

class UserService(ApiView):
    """
    用户
    """
    __model__ = User
