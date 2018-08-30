#!/bin/env python
# coding: utf-8

"""
函数工具
"""
import os
import io
import re
import sys
import json
import base64
import codecs
import hashlib
import logging
import posixpath
import requests
import tempfile
import platform
import subprocess
import asyncio
from functools import partial
from lxml import html as lxml_html
from lxml.html import tostring as lxml_html_tostring
# from lxml.html import parse as html_parse, fromstring as html_fromstring

# from lxml import etree, html as lxmlHtml
from PyPDF2 import PdfFileReader
from PyPDF2.generic import IndirectObject, TextStringObject
import zipfile
# # from .compress.zstd_tar import ZstdTar
import tarfile

logging.basicConfig(
    level=logging.DEBUG
)
logger = logging.getLogger('converts')

IS_PY3 = sys.version_info[0] > 2
ENCODING = 'utf-8'

NAMESPACES = {
    'XML': 'http://www.w3.org/XML/1998/namespace',
    'EPUB': 'http://www.idpf.org/2007/ops',
    'DAISY': 'http://www.daisy.org/z3986/2005/ncx/',
    'OPF': 'http://www.idpf.org/2007/opf',
    'CONTAINERNS': 'urn:oasis:names:tc:opendocument:xmlns:container',
    'DC': "http://purl.org/dc/elements/1.1/",
    'XHTML': 'http://www.w3.org/1999/xhtml',
    'SVG': 'http://www.w3.org/2000/svg',
    'SVGLINK': 'http://www.w3.org/1999/xlink'
}

HTTP_NAME = re.compile(r'(^(?:[a-z]+\:)?(?:\/\/))')

FONT_RE = re.compile(
    r'(?:src: *)?url\(\'?"? *([a-zA-Z0-9\/\-_:\.]+\.(?:ttf|woff|woff2|svg|eot|otf)) *\'?"?\),? *'
)
FACE_RE_START = re.compile(
    r'^ *@font-face *{'
)
FACE_RE_END = re.compile(
    r'^.*}$'
)
TAG_RE = re.compile(
    r'^\s*(\w+(\s+\w+)*\s*($|,|(\{\s*$)))'
)

PDF_EXEC = re.compile(r'Working: *(\d+)\/(\d+)')

def file_open(*args, **k):
    """
    代理原open保证python2，python3通用
    """
    # if 'errors' not in k:
    #     k['errors'] = 'surrogateescape'
    if IS_PY3:
        return open(*args, **k)
    return codecs.open(*args, **k)


def save_json(json_name, json_data, indent='  '):
    """
    通用保存json: 不转为ascii，添加2个空格缩进
    """
    with file_open(json_name, 'w', encoding='utf8') as file_:
        if IS_PY3:
            json.dump(json_data, file_, ensure_ascii=False, indent=indent)
        else:
            json.dump(json_data, file_, ensure_ascii=False, indent=2)


def read_json(json_name):
    """
    通用读取json
    """
    with file_open(json_name, 'r', encoding='utf8') as file_:
        return json.load(file_)


def deep_tree(roots, level, callback):
    """
    递归处理xml
    """
    for row in roots.iterchildren():
        callback(row, level)


def convert(name):
    """
    驼峰转下滑线分割
    """
    str1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', str1).lower()


def read_meta_pdf(pdf_name):
    """
    读取pdf的meta信息
    """
    with open(pdf_name, 'rb') as file_:
        doc = PdfFileReader(file_)
        info = doc.documentInfo
        new_info = {}
        for key, tmp in info.items():
            key = convert(key[1:])
            if isinstance(tmp, IndirectObject):
                new_info[key] = tmp.getObject()
            elif isinstance(tmp, TextStringObject):
                new_info[key] = tmp.title()
            else:
                new_info[key] = str(tmp)
    new_info['meta_type'] = 'pdf'
    return new_info

def read_tree_meta_opf(tree):
    opf = NAMESPACES['OPF']
    dc_name = '{%s}' % NAMESPACES['DC']
    identifier = '{%s}scheme' % opf
    dc_len = len(dc_name)
    meta = {}
    root = tree.find('{%s}metadata' % opf)
    for val in root.iterchildren():
        tag = val.tag
        if tag == '{%s}meta' % opf:
            name = val.get('name')
            name_arr = name.split(':')
            name = name_arr[1] if len(name_arr) > 1 else name
            meta[name] = val.get('content')
        elif tag.startswith(dc_name):
            tag = tag[dc_len:]
            if tag in ('subject', 'identifier'):
                if tag == 'subject':
                    if tag not in meta:
                        meta[tag] = []
                    meta[tag].append(val.text)
                else:
                    if tag not in meta:
                        meta[tag] = {}
                    name_tag = val.get(identifier)
                    if name_tag:
                        meta[tag][str(name_tag).lower()] = val.text
            else:
                meta[tag] = val.text
    meta['meta_type'] = 'opf'
    return meta

def read_zip_meta_opf(opf_file):
    """
    直接读取文件对象的opf
    """
    from lxml import etree
    return read_tree_meta_opf(etree.parse(opf_file))

def read_meta_opf(opf_name):
    """
    读取opf文件中的meta
    """
    with file_open(opf_name, 'rb') as file_:
        meta = read_zip_meta_opf(file_)
    return meta

def requests_douban_meta(meta):
    """
    通过原meta查询到豆瓣的meta
    """
    # print(meta)
    if 'douban' in meta['identifier']:
        douban_id = meta['identifier']['douban']
        douban_url = 'https://api.douban.com/v2/book/%s' % douban_id
    else:
        douban_id = meta['identifier']['isbn']
        douban_url = 'https://api.douban.com/v2/book/isbn/%s' % douban_id
    res = requests.get(douban_url)
    douban_meta = res.json()
    # douban_meta['type'] = 'pdf'
    douban_meta['meta_type'] = 'douban'
    douban_meta['title'] = meta['title']
    return douban_meta


def file_sha256(file_name):
    """
    获取文件的sha256码
    """
    sha = hashlib.sha256()
    with file_open(file_name, 'rb') as file_:
        byte = file_.read(8096)
        while byte:
            sha.update(byte)
            byte = file_.read(8096)
    return sha.hexdigest(), base64.urlsafe_b64encode(sha.digest()).decode()

def get_hash_string(data):
    """
    获取文本hash
    """
    md5 = hashlib.md5()
    md5.update(data.encode())
    return base64.urlsafe_b64encode(md5.digest()).decode()

def html_parse(page_file):
    """
    解析html
    """
    return lxml_html.fromstring(page_file.read())

def html_create_element(*args, **k):
    return lxml_html.Element(*args, **k)

def parse_string(string):
    """
    处理zip open无法解析文本
    """
    from lxml import etree
    try:
        tree = etree.parse(io.BytesIO(string.encode('utf-8')))
    except:
        tree = etree.parse(io.BytesIO(string))

    return tree

def html_tostring(tree):
    """
    html to string
    """
    return lxml_html_tostring(
        tree,
        pretty_print=True,
        # method="html",
        encoding='utf-8',
    ).strip()

def copy_zip_file(zip_file, from_path, to_path):
    """
    拷贝zip中的文件
    """
    try:
        with zip_file.open(from_path, 'r') as from_file:
            with file_open(to_path, 'wb') as to_file:
                data = from_file.read(io.DEFAULT_BUFFER_SIZE)
                while data:
                    to_file.write(data)
                    data = from_file.read(io.DEFAULT_BUFFER_SIZE)
        return True
    except KeyError:
        logger.debug('miss: %s not in zip' % from_path)
        return False

def zip_join(*dirs):
    """
    去除..的zip用路径拼接
    """
    dist_dirs = []
    for dir_name in dirs:
        if '/' in dir_name:
            dir_arr = dir_name.split('/')
            for item in dir_arr:
                if item == '..':
                    if len(dist_dirs):
                        dist_dirs.pop()
                else:
                    dist_dirs.append(item)
        else:
            dist_dirs.append(dir_name)
    return posixpath.join(dist_dirs[0], *dist_dirs[1:])

def get_file_path_dir(file_name):
    """
    获取文件的目录
    """
    if os.path.sep in file_name:
        return file_name[:file_name.rindex(os.path.sep)]
    else:
        return ''

def get_file_path_name(file_name):
    """
    获取文件的名字
    """
    if os.path.sep in file_name:
        return file_name[file_name.rindex(os.path.sep) + 1:]
    else:
        return file_name

def add_path_to_tar(tar_file, input_path, output_path):
    """
    通过文件路径把文件添加到tar
    """
    with file_open(input_path, 'rb') as input_file:
        if hasattr(tar_file, 'write'):
            tar_file.write(input_path, output_path)
        else:
            info = tar_file.gettarinfo(input_path, output_path)
            tar_file.addfile(info, input_file)


def add_zipfile_to_tar(tar_file, zip_file, zip_path, output_path):
    """
    把zip文件放入tar中
    """
    status = False
    temp = tempfile.mktemp()
    if copy_zip_file(zip_file, zip_path, temp):
        status = True
        add_path_to_tar(tar_file, temp, output_path)
    os.remove(temp)
    return status

def add_json_to_tar(tar_file, json_data, output_path):
    """
    json对象添加到tar
    """
    temp = tempfile.mktemp(suffix='.json')
    save_json(temp, json_data)
    add_path_to_tar(tar_file, temp, output_path)
    os.remove(temp)

def save_xml_path(xml, output_path, method="html"):
    """
    保存xml
    """
    from lxml import etree
    return etree.ElementTree(xml).write(
        output_path,
        pretty_print=True,
        encoding='utf-8',
        method=method
    )

def save_xml_tree_path(tree, output_path):
    """
    保存tree
    """
    return tree.write(
        output_path,
        pretty_print=True,
        encoding='utf-8',
        method='html'
    )

def add_xml_tree_to_tar(tar_file, tree, output_path):
    """
    tree
    """
    temp = tempfile.mktemp(suffix='.xml')
    res = save_xml_tree_path(tree, temp)
    add_path_to_tar(tar_file, temp, output_path)
    os.remove(temp)
    return res

def tar_open(name, mode, file_type='zip'):
    """
    打开tar文件
    """
    if file_type == 'zip':
        return zipfile.ZipFile(name, mode)
    else:
        return tarfile.open(name, mode)

class TempTar():
    def __init__(self, tar_file, temp, output_path, *args, **k):
        self._tar_file = tar_file
        self._temp = temp
        self._output_path = output_path
        self._obj = file_open(self._temp, *args, **k)

    def __enter__(self):
        self._obj.__enter__()
        return self._obj

    def __exit__(self, arg1, arg2, arg3):
        self._obj.__exit__(arg1, arg2, arg3)
        self.close()

    def close(self):
        self._obj.close()
        add_path_to_tar(self._tar_file, self._temp, self._output_path)
        os.remove(self._temp)

def open_temp_file(tar_file, output_path, *args, **k):
    """
    打开一个临时文件，在退出上下文时会自动保存到tar中
    """
    temp = tempfile.mktemp()
    temp_file = TempTar(tar_file, temp, output_path, *args, **k)
    return temp_file

PNGBIN = {
    'Windows': 'bin\\pngquant.exe',
    'Linux': 'bin/pngquant'
}
