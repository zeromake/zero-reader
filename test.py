from web_app.models import User


from sqlalchemy import func, sql as sa_sql

print(sa_sql.select([func.count(User.c.id).label("count")]))