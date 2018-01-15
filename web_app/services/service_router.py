from sanic import response
from web_app import app
from .user_service import UserService

user_view = UserService.as_view()
app.__model__['/user'] = user_view.self
app.add_route(user_view, '/user')

@app.route("/register", methods=['POST'])
async def register(request):
    """
    注册
    """
    form_data = request.json
    if not isinstance(form_data, dict):
        return response.json({'status': 400, 'message': "param not is {...}"})
    form_data.update({
        'status': 1,
        'permissions': 0,
        'admin': False
    })
    model_url = "/user"
    model = app.__model__.get(model_url)
    if not model:
        return response.json({'status': 500, 'message': "not find model: %s" % model_url})
    return response.json(await model.execute_dml(model.insert(form_data)))
