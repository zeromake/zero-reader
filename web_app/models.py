import sqlalchemy as sa

"""
models by zeromake on 2018-01-11
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
    "ReadHistory",
    "BookShelf",
    "UserConfig",
    "BookConfig",
    "BookNotes"
]
__version__ = "1.1.0"

# 用户表
User = sa.Table(
    'user',
    metadata,
    sa.Column(
        'id',
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        nullable=False,
        doc="主键"
    ),
    sa.Column(
        'account',
        sa.String(16),
        nullable=False,
        doc="帐号"
    ),
    sa.Column(
        'role_name',
        sa.String(16),
        nullable=False,
        doc="昵称"
    ),
    sa.Column(
        'email',
        sa.String(256),
        nullable=False,
        doc="邮箱"
    ),
    sa.Column(
        'password',
        sa.String(128),
        nullable=False,
        doc="密码"
    ),
    sa.Column(
        'status',
        sa.Integer,
        nullable=False,
        doc="用户状态"
    ),
    sa.Column(
        'permissions',
        sa.Integer,
        nullable=False,
        doc="用户权限"
    ),
    sa.Column(
        'admin',
        sa.Boolean,
        nullable=False,
        doc="是否为管理员"
    ),
    sa.Column(
        'create_time',
        sa.BigInteger,
        nullable=False,
        doc="创建时间"
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
        nullable=False,
        doc="权限名"
    ),
    sa.Column(
        'permission',
        sa.Text,
        nullable=False,
        doc="权限配置文本"
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
        'hash',
        sa.String(256),
        nullable=False,
        doc="书籍唯一编码通过文件hash获取,其它书籍通过uuid"
    ),
    sa.Column(
        'title',
        sa.String(128),
        nullable=False,
        doc="书籍标题"
    ),
    sa.Column(
        'file_name',
        sa.String(128),
        nullable=False,
        doc="文件名"
    ),
    sa.Column(
        'type',
        sa.String(8),
        nullable=False,
        doc="文件类型"
    ),
    sa.Column(
        'create_time',
        sa.BigInteger,
        nullable=False,
        doc="创建时间"
    ),
    sa.Column(
        'update_time',
        sa.BigInteger,
        nullable=False,
        doc="更新时间"
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
        nullable=False,
        doc="tag名"
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
        nullable=False,
        doc="标签"
    ),
    sa.Column(
        'library_id',
        sa.Integer,
        nullable=False,
        doc="书籍"
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
        sa.String(32),
        nullable=False,
        doc="名字"
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
        nullable=False,
        doc="书籍"
    ),
    sa.Column(
        'type_id',
        sa.Integer,
        nullable=False,
        doc="作者类型"
    ),
    sqlite_autoincrement=True
)

# 阅读记录
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
    sa.Column(
        'library_id',
        sa.Integer,
        nullable=False,
        doc="书籍"
    ),
    sa.Column(
        'page',
        sa.Integer,
        nullable=False,
        doc="页数"
    ),
    sa.Column(
        'offset',
        sa.Integer,
        nullable=False,
        doc="滚动高度或epub视图offset"
    ),
    sa.Column(
        'create_time',
        sa.BigInteger,
        nullable=False,
        doc="创建时间"
    ),
    sqlite_autoincrement=True
)
# 书架
BookShelf = sa.Table(
    'book_shelf',
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
        nullable=False,
        doc="书籍"
    ),
    sa.Column(
        'sort',
        sa.String(32),
        nullable=False,
        doc="分类"
    ),
    sa.Column(
        'create_time',
        sa.BigInteger,
        nullable=False,
        doc="创建时间"
    ),
    sqlite_autoincrement=True
)
# 用户偏好设置
UserConfig = sa.Table(
    'user_config',
    metadata,
    sa.Column(
        'id',
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        nullable=False
    ),
    sa.Column(
        'user_id',
        sa.Integer,
        nullable=False,
        doc="用户"
    ),
    # 配置
    sa.Column(
        'config',
        sa.Text,
        nullable=False,
        doc="配置文本"
    ),
    sqlite_autoincrement=True
)

BookConfig = sa.Table(
    'book_config',
    metadata,
    sa.Column(
        'id',
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        nullable=False
    ),
    sa.Column(
        'user_id',
        sa.Integer,
        nullable=False,
        doc="用户"
    ),
    sa.Column(
        'library_id',
        sa.Integer,
        nullable=False,
        doc="书籍"
    ),
    # 配置
    sa.Column(
        'config',
        sa.Text,
        nullable=False,
        doc="配置文本"
    ),
    sqlite_autoincrement=True
)

BookNotes = sa.Table(
    'book_notes',
    metadata,
    sa.Column(
        'id',
        sa.Integer,
        autoincrement=True,
        primary_key=True,
        nullable=False
    ),
    sa.Column(
        'user_id',
        sa.Integer,
        nullable=False,
        doc="用户"
    ),
    sa.Column(
        'library_id',
        sa.Integer,
        nullable=False,
        doc="书籍"
    ),
    sa.Column(
        'update_time',
        sa.BigInteger,
        nullable=False,
        doc="更新时间"
    ),
    sa.Column(
        'page',
        sa.Integer,
        nullable=False,
        doc="页数"
    ),
    sa.Column(
        'note',
        sa.Text,
        nullable=False,
        doc="笔记"
    ),
    sqlite_autoincrement=True
)
