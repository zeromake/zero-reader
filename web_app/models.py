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
    sqlite_autoincrement=True,
)
User.__doc__ = "用户"

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
Permissions.__doc__ = "权限"

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
        'status',
        sa.Integer,
        nullable=False,
        doc="书籍状态"
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
Library.__doc__ = "书库"

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
Tags.__doc__ = "标签"

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
LibraryBindTag.__doc__ = "标签关联"

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
Authors.__doc__ = "作者|翻译者"

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
LibraryBindAuthor.__doc__ = "作者关联"

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
ReadHistory.__doc__ = "阅读记录"
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
        'update_time',
        sa.BigInteger,
        nullable=False,
        doc="更新时间"
    ),
    sqlite_autoincrement=True
)
BookShelf.__doc__ = "书架"
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
UserConfig.__doc__ = "用户设置"

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
BookConfig.__doc__ = "书籍设置"

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
BookNotes.__doc__ = "笔记"
