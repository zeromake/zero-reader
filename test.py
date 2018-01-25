from web_app.models import User
import sqlalchemy as sa


for c in User.columns:
    if isinstance(c.type, sa.String):
        print(c.type, c.type.length, c.type.__class__)
    else:
        print(c.type, c.type.__class__)