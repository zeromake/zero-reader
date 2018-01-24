"""
登录后可以操作的公开api
"""

from sanic import Blueprint
PublicApi = Blueprint("public_api", url_prefix='/api/public')
