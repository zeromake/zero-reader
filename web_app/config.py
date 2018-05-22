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
    "URL": "http://127.0.0.1:8090",
    # "SMTP": {
    #     "HOST": "smtp-mail.outlook.com",
    #     "PORT": 25,
    #     "ACCOUNT": "fly-zero@hotmail.com",
    #     "PASSWORD": os.environ.get("SMTP_PWD"),
    #     "SSL": 2,
    # },
    "SMTP": {
        "HOST": "smtp.163.com",
        "PORT": 465,
        "ACCOUNT": "390720046@163.com",
        "PASSWORD": os.environ.get("SMTP_PWD"),
        "SSL": 1
    },
}
