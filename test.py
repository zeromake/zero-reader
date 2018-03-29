from sqlalchemy import sql as sa_sql
from sqlalchemy.sql.expression import bindparam
from web_app.models import User

where = User.c.id==bindparam("_id")
sql = sa_sql.update(User, whereclause=where,
values={ "account": bindparam("_account") }
)

print(sql)

