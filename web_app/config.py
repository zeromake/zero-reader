#!/bin/env python
# coding: utf-8
import os
"""
配置
"""
CONFIG = {
    # 'DB': "mysql+pymysql://root:123456@127.0.0.1:3306/zero_reader",
    "DB": 'sqlite:///config/sqlite.db',
    "OPEN_API": True,
    # "DB": "postgresql+psycopg2://postgres:123456@127.0.0.1:5432/zero_reader",
    "FILE": "config/config.ini",
    "SECRET": "Be9ZszibMYVu",
    "HASH": "md5_crypt",
    "SMTP": {
        "HOST": "smtp.163.com",
        "PORT": 465,
        "ACCOUNT": "390720046@163.com",
        "PASSWORD": os.environ.get("SMTP_PWD"),
        "SSL": True
    }
}
