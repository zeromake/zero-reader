import web_app.models as model
from web_app.models import __all__ as model_name
import sqlalchemy as sa

def print_model(m):
    print("name: ", m.name)
    for c in m.columns:
        if isinstance(c.type, sa.String):
            print(c.type, c.type.length, c.type.__class__)
        else:
            print(c.type, c.type.__class__)

for m in model_name:
    if hasattr(model, m):
        print_model(getattr(model, m))