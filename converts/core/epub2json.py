#!/bin/env python
# coding: utf-8

"""
epub2json
"""
import os
from zipfile import ZipFile
from lxml import etree
from .utils import file_sha256, file_open


class Epub2Json(object):
    """
    转换为json
    """
    def __init__(self, options):
        """
        初始化配置
        """
        self.options = options
        self.file_name = options['file']
        self.sha = file_sha256(self.file_name)
        self.dist = os.path.join(options['dist'], self.sha)

    def run(self):
        """
        创建zip文件对象
        """
        with ZipFile(self.file_name, 'r') as epub_file:
            with epub_file.open('OEBPS/toc.ncx') as mimetype:
                print(mimetype.read())
            # print(epub_file)

        
    

if __name__ == '__main__':
    pass
