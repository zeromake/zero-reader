from sqlalchemy import sql as sa_sql
from sqlalchemy.sql.expression import bindparam
from web_app.models import User
from web_app.utils import handle_param_primary
from aiosqlite3.sa.engine import compiler_dialect

where = User.c.id.in_(bindparam("_id", expanding=True))
sql = sa_sql.update(User, whereclause=where,
values={ "account": bindparam("_account") }
)

print(sql.compile(dialect=compiler_dialect()))

