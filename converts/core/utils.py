#!/bin/env python
# coding: utf-8

"""
函数工具
"""
import io
import re
import sys
import json
import codecs
import hashlib
import requests
import posixpath

from lxml import etree
from PyPDF2 import PdfFileReader
from PyPDF2.generic import IndirectObject, TextStringObject

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

IS_PY3 = sys.version_info[0] > 2
ENCODING = 'utf-8'

NAMESPACES = {
    'XML': 'http://www.w3.org/XML/1998/namespace',
    'EPUB': 'http://www.idpf.org/2007/ops',
    'DAISY': 'http://www.daisy.org/z3986/2005/ncx/',
    'OPF': 'http://www.idpf.org/2007/opf',
    'CONTAINERNS': 'urn:oasis:names:tc:opendocument:xmlns:container',
    'DC': "http://purl.org/dc/elements/1.1/",
    'XHTML': 'http://www.w3.org/1999/xhtml'
}

HTTP_NAME = re.compile(r'(^(?:[a-z]+\:)?(?:\/\/))')

def file_open(*args, **k):
    """
    代理原open保证python2，python3通用
    """
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
    if 'douban' in meta['identifier']:
        douban_id = meta['identifier']['douban']
        douban_url = 'https://api.douban.com/v2/book/%s' % douban_id
    else:
        douban_id = meta['identifier']['isbn']
        douban_url = 'https://api.douban.com/v2/book/isbn/%s' % douban_id
    res = requests.get(douban_url)
    douban_meta = res.json()
    douban_meta['type'] = 'pdf'
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
    return sha.hexdigest()

def parse_string(string):
    """
    处理zip open无法解析文本
    """
    try:
        tree = etree.parse(io.BytesIO(string.encode('utf-8')))
    except:
        tree = etree.parse(io.BytesIO(string))

    return tree

def copy_zip_file(zip_file, from_path, to_path):
    """
    拷贝zip中的文件
    """
    with zip_file.open(from_path, 'r') as from_file:
        with file_open(to_path, 'wb') as to_file:
            data = from_file.read(4096)
            while data:
                to_file.write(bytes(data))
                data = from_file.read(4096)

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
                    dist_dirs.pop()
                else:
                    dist_dirs.append(item)
        else:
            dist_dirs.append(dir_name)
    
    return posixpath.join(dist_dirs[0], *dist_dirs[1:])
