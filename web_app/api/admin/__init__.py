"""
管理员才可访问的api
"""

from sanic import Blueprint

AdminApi = Blueprint("admin_api", url_prefix='/api/admin')
