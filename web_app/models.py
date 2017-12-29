import sqlalchemy as sa

"""
models by zeromake on 2017-12-29
"""

metadata = sa.MetaData()

__all__ = [
    "User",
    "Permissions",
    "Library",
    "Tags",
    "LibraryBindTag",
    "Authors",
    "LibraryBindAuthor",
    "ReadHistory"
]

# 用户表
User = sa.Table(
    'user',
    metadata,
    sa.Column(
        'id',
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        nullable=False
    ),
    sa.Column(
        'account',
        sa.String(16),
        nullable=False
    ),
    sa.Column(
        'role_name',
        sa.String(16),
        nullable=False
    ),
    sa.Column(
        'password',
        sa.String(32),
        nullable=False
    ),
    sa.Column(
        'status',
        sa.Integer,
        nullable=False
    ),
    sa.Column(
        'permissions',
        sa.Integer,
        nullable=False
    ),
    sa.Column(
        'admin',
        sa.Boolean,
        nullable=False
    ),
    sqlite_autoincrement=True
)

# 权限表
Permissions = sa.Table(
    'permissions',
    metadata,
    sa.Column(
        'id',
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        nullable=False
    ),
    sa.Column(
        'name',
        sa.String(16),
        nullable=False
    ),
    sa.Column(
        'permission',
        sa.Text,
        nullable=False
    ),
    sqlite_autoincrement=True
)

# 书库表
Library = sa.Table(
    'library',
    metadata,
    sa.Column(
        'id',
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        nullable=False
    ),
    sa.Column(
        'sha256',
        sa.String(256),
        nullable=False
    ),
    sa.Column(
        'title',
        sa.String(128),
        nullable=False
    ),
    sa.Column(
        'file_name',
        sa.String(128),
        nullable=False
    ),
    sa.Column(
        'type',
        sa.String(8),
        nullable=False
    ),
    sqlite_autoincrement=True
)

# 书籍标签表
Tags = sa.Table(
    'tags',
    metadata,
    sa.Column(
        'id',
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        nullable=False
    ),
    sa.Column(
        'name',
        sa.String(16),
        nullable=False
    )
)

# 书籍标签关联表
LibraryBindTag = sa.Table(
    'library_bind_tag',
    metadata,
    sa.Column(
        'id',
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        nullable=False
    ),
    sa.Column(
        'tag_id',
        sa.Integer,
        nullable=False
    ),
    sa.Column(
        'library_id',
        sa.Integer,
        nullable=False
    ),
    sqlite_autoincrement=True
)

# 作者或翻译者
Authors = sa.Table(
    'authors',
    metadata,
    sa.Column(
        'id',
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        nullable=False
    ),
    sa.Column(
        'name',
        sa.String(16),
        nullable=False
    ),
    sqlite_autoincrement=True
)

# 作者或翻译者关联
LibraryBindAuthor = sa.Table(
    'library_bind_author',
    metadata,
    sa.Column(
        'id',
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        nullable=False
    ),
    sa.Column(
        'library_id',
        sa.Integer,
        nullable=False
    ),
    sa.Column(
        'type_id',
        sa.Integer,
        nullable=False
    ),
    sqlite_autoincrement=True
)

ReadHistory = sa.Table(
    'read_history',
    metadata,
    sa.Column(
        'id',
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        nullable=False
    ),
    sqlite_autoincrement=True
)
