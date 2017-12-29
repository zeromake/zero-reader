from sanic import Sanic
from sanic import response
import os

app = Sanic(__name__)

@app.listener('before_server_start')
async def init_ipfsapi(app, loop):
    import ipfsapi
    app.ipfsapi = ipfsapi.connect('127.0.0.1', 5001)

@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    if app.ipfsapi:
        app.ipfsapi = None

@app.route('/ipfs/<file:[A-z0-9/\.\?-]+>', methods=['GET'])
async def get_ipfs(request, file):
    local_path = os.path.join('cache', file)
    if not os.path.exists(local_path):
        file_path = local_path[:local_path.rfind('/')]
        app.ipfsapi.get(file, filepath=file_path)
    return await response.file(local_path, headers={'Access-Control-Allow-Origin': '*'})

if __name__ == '__main__':
    app.run()
