#!/bin/env python
# coding: utf-8

import re
import os
import sys
import json
import shutil
import hashlib
import zipfile
import argparse
import platform
import subprocess
import requests
from lxml import etree

from PyPDF2 import PdfFileReader
from PyPDF2.generic import IndirectObject, TextStringObject



def deep_tree(roots, level, callback):
    for row in roots.iterchildren():
        callback(row, level)

class Pdf2Json(object):
    def __init__(self, options):
        """
        初始化
        """
        self.pdf_name = options.file
        self.sha = self.file_sha256(self.pdf_name)
        self.abs_url = '/library/' + self.sha + '/'
        self.dist = os.path.join(options.dist, self.sha)
        self.out = os.path.join(options.out, self.sha)
        self.css = options.css
        self.join = options.join
        self.page = os.path.join(self.join, options.page)
        self.img_dir = 'img'
        self.share = options.share
        self.toc = options.toc
        self.meta = options.meta

        self.pages = None
        self.tocs = None
        self.containers = None
        self.font_join = 'font'
        self.zoom = 'zoom.json'
    
    def file_sha256(self, file_name):
        sha = hashlib.sha256()
        with open(file_name, 'rb') as fd:
            byte = fd.read(8096)
            while byte:
                sha.update(byte)
                byte = fd.read(8096)
        return sha.hexdigest()

    
    def run(self):
        """
        执行处理
        """
        if os.path.exists(self.dist):
            print('book sha256: %s is exist' % self.dist)
            return
        self.mkdir()
        self.read_meta()
        self.exec_pdf()
        self.container_to_json(
            os.path.join(self.out, 'index.html'),
            os.path.join(self.dist, 'container.json'),
            self.copy_page
        )
        self.toc_to_json(
            os.path.join(self.out, self.toc),
            os.path.join(self.dist, 'toc.json')
        )
        self.css_copy()
        # self.deldir()

    def read_meta(self):
        opf_name = self.pdf_name[:self.pdf_name.rfind('.')] + '.opf'
        if self.meta != '' and os.path.exists(self.meta):
            meta = read_meta_opf(self.meta)
        elif os.path.exists(opf_name):
            meta = read_meta_opf(opf_name)
        else:
            meta = read_meta_pdf(self.pdf_name)
        if 'identifier' in meta and 'DOUBAN' in meta['identifier']:
            meta = requests_douban_meta(meta)
        meta['sha'] = self.sha
        if 'title' not in meta:
            meta['title'] = self.pdf_name[self.pdf_name.rfind('/') + 1:self.pdf_name.rfind('.')]
        with open(os.path.join(self.dist, 'meta.json'), 'w', encoding='utf8') as fd:
            json.dump(meta, fd, ensure_ascii=False, indent="  ")
        db_name = os.path.join('library', 'db.json')
        db_data = []
        if os.path.exists(db_name):
            with open(db_name, 'r', encoding='utf8') as fd:
                db_data = json.load(fd)
        sha_set = set([row['sha']for row in db_data])
        if self.sha not in sha_set:
            db_data.append(meta)
        with open(db_name, 'w', encoding='utf8') as fd:
            json.dump(db_data, fd, ensure_ascii=False, indent="  ")

        


    def mkdir(self):
        dirs = [
            self.out,
            self.dist,
            os.path.join(self.out, self.join),
            os.path.join(self.dist, self.join),
            os.path.join(self.dist, self.font_join),
            os.path.join(self.dist, self.img_dir)
        ]
        for row in dirs:
            if not os.path.exists(row):
                os.makedirs(row)
    def deldir(self):
        shutil.rmtree(self.out)
    
    def exec_pdf(self):
        """
        转换
        """
        lock_name = os.path.join(self.out, 'exec.lock')
        if os.path.exists(lock_name):
            with open(lock_name, 'r', encoding='utf8') as fd:
                if fd.read(1) == '0':
                    print('MISS exec_pdf')
                    return

        pdf2html_dict = {
            "Windows": ('bin/pdf2htmlEX-win32.zip', 'bin/pdf2htmlEX.exe'),
            "Linux": ('bin/pdf2htmlEX-linux-x64.zip', 'bin/pdf2htmlEX.sh')
        }
        sysstr = platform.system()
        pdf2html = pdf2html_dict.get(sysstr)
        if pdf2html:
            if not os.path.exists(pdf2html[1]):
                self.extract_zip(pdf2html[0])
        else:
            raise NameError("bin not on")
        if sysstr == 'Linux':
            subprocess.call(["chmod", "+x", pdf2html[1]])
            subprocess.call(["chmod", "+x", 'bin/pdf2htmlEX'])
        state = subprocess.call([
            pdf2html[1],
            '--embed-css','0',
            '--embed-font','0',
            '--embed-image','0',
            '--embed-javascript', '0',
            '--embed-outline', '0',
            '--outline-filename', '%s' % self.toc,
            '--split-page', '1',
            '--css-filename', '%s' % self.css,
            '--page-filename', '%s' % self.page,
            '--space-as-offset', '1',
            '--data-dir', '%s' % self.share,
            '--dest-dir', '%s' % self.out,
            self.pdf_name,
            'index.html'
        ])
        with open(os.path.join(self.out, 'exec.lock'), 'w') as fd:
            fd.write(str(state))

    def extract_zip(self, zip_name):
        with zipfile.ZipFile(zip_name,'r') as f:
            for file in f.namelist():
                f.extract(file,"bin/")

    def toc_to_json(self, toc_html_name, toc_json_name):
        """
        把html的toc转为json
        """
        if os.path.getsize(toc_html_name) < 1:
            print('MISS empty TOC')
            return
        handle = {
            'data-dest-detail': lambda x: tuple(json.loads(x)),
            'href': lambda x: x[1:]
        }
        with open(toc_html_name, 'r', encoding='utf8') as fd:
            try:
                tree = etree.parse(fd)
            except etree.XMLSyntaxError as e:
                fd.seek(0)
                self.toc_del_zero(toc_html_name)
                return self.toc_to_json(toc_html_name, toc_json_name)
            toc = []
            def callback_toc(item, level):
                for row in item.iterchildren():
                    if row.tag == 'a':
                        toc_item = {}
                        for key, val in row.items():
                            han = handle.get(key)
                            if han:
                                val = han(val)
                            toc_item[key] = val
                        toc_item['text'] = row.text.strip()
                        toc_item['level'] = level
                        if self.pages:
                            toc_item['page'] = self.pages.get(toc_item['href'])
                        if level == 0:
                            toc.append(toc_item)
                        else:
                            parent = toc[-1]
                            index = level -1
                            while index:
                                index -= 1
                                parent = parent['children'][-1]
                            if 'children' not in parent:
                                parent['children'] = []
                            parent['children'].append(toc_item)
                    elif row.tag == 'ul':
                        deep_tree(row, level + 1, callback_toc)
                        
            root = tree.getroot()
            deep_tree(root, 0, callback_toc)
        if toc_json_name:
            with open(toc_json_name, 'w', encoding='utf8') as fd:
                json.dump(toc, fd, ensure_ascii=False, indent="  ")
        self.tocs = toc
    
    def toc_del_zero(self, toc_html_name):
        with open(toc_html_name, 'rb') as fd:
            data = fd.read()
        buffer = bytearray()
        for char in data:
            if char != 0x00:
                buffer.append(char)
        with open(toc_html_name, 'wb') as fd:
            fd.write(buffer)
            # with open(toc_html_name, 'wb') as out_fd:
            #     char = fd.read(1)
            #     while char != None
            #         if char != 0x00
            #             out_fd.write(char)
            #         char = fd.read(1)
        # return subprocess.call(['sed', r"'s/\x00//g'", toc_html_name])
    
    def container_to_json(self, container_name, json_name, callback=None):
        """
        转换内容页
        """
        page_id_to_index = {}
        containers = []
        out_bg_css = os.path.join(self.dist, 'bg.css')
        background = []
        background.append("div.background_img_class{")
        background.append("  background-size: 100%;")
        background.append("}")
        with open(container_name, encoding='utf8') as fd:
            tree = etree.parse(fd)
            container_root = tree.xpath(u'//div[@id="page-container"]')[0]
            last_class = None
            index = 0
            for row in container_root.iterchildren():
                item = {key: val for key, val in row.items() if key != 'data-page-no' and not (key == 'class' and val == last_class)}
                page_id_to_index[item['id']] = index
                item['index'] = index
                containers.append(item)
                if callback:
                    callback(item, background)
                last_class = row.get('class')
                index += 1
        if json_name:
            with open(json_name, 'w', encoding='utf8') as fd:
                json.dump(containers, fd, ensure_ascii=False, indent="  ")
        with open(out_bg_css, 'w', encoding='utf8') as fd:
            fd.write("\n".join(background))
        self.containers = containers
        self.pages = page_id_to_index

    def copy_page(self, page, background):
        """
        拷贝page的html，并做好预处理
        """
        page_name = page['data-page-url']
        out_dir = self.dist
        input_dir = self.out
        join_dir = 'img'
        input_name = os.path.join(input_dir, page_name)
        out_name = os.path.join(out_dir, page_name)
        with open(input_name, 'r', encoding='utf8') as fd:
            tree = etree.parse(fd)
            for img in tree.xpath('//img'):
                parent = img.getparent()
                div = etree.Element('div')
                val = img.get('src')
                shutil.copyfile(os.path.join(input_dir, val), os.path.join(out_dir, join_dir, val))
                img_sha = self.file_sha256(os.path.join(input_dir, val))
                background.append("div.img_" + img_sha + "{")
                background.append("  background-image: url('./" + join_dir + '/' + val + "');")
                background.append("}")
                val = img.get('alt')
                if val != '':
                    div.set('title', val)
                val = img.get('class')
                val += ' img_' + img_sha + ' background_img_class'
                div.set('class', val)
                parent.replace(img, div)
            tree.write(out_name, pretty_print=True, encoding='utf-8', method='html')
        
    def css_copy(self):
        css_name = os.path.join(self.out, self.css)
        out_name = os.path.join(self.dist, self.css)
        font_pat = re.compile(r'url\((\w+\.woff)\)')
        px_and_pat = re.compile(r'(.*){([\w-]+):(-?\d+(?:\.\d+)?)(px|pt);}')
        zoom = []
        field = ('select', 'attribute', 'size', 'unit')

        with open(css_name, 'r', encoding='utf-8') as fd:
            with open(out_name, 'w', encoding='utf-8') as out_fd:
                line = fd.readline()
                media_print = False
                while line:
                    match = px_and_pat.match(line)
                    if match:
                        item = {key: val for key, val in zip(field, match.groups())}
                        item['size'] = float(item['size'])
                        item['media_print'] = media_print
                        zoom.append(item)
                    elif line.startswith('@font-face{font-family'):
                        line = font_pat.sub(self.font_copy, line)
                    elif line == '@media print{\n':
                        media_print = True
                    elif line == '}\n' and media_print:
                        media_print = False
                    out_fd.write(line)
                    line = fd.readline()
        with open(os.path.join(self.dist, self.zoom), 'w', encoding='utf8') as fd:
            json.dump(zoom, fd, ensure_ascii=False, indent="  ")
    def font_copy(self, group):
        """
        拷贝字体
        """
        out_dir = self.dist
        input_dir = self.out
        font_name = group.group(1)
        out_name = os.path.join(out_dir, self.font_join, font_name)
        input_name = os.path.join(input_dir, font_name)
        shutil.copyfile(input_name, out_name)
        return 'url(%s)' % ('./' + self.font_join + '/' + font_name)
def add_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, help='pdf file')
    parser.add_argument('-o', '--out', type=str, help='out file dir', default="out")
    parser.add_argument('-d', '--dist', type=str, help='dist file dir', default="library")
    parser.add_argument('-c', '--css', type=str, help='css file name', default="style.css")
    parser.add_argument('-p', '--page', type=str, help='page file name', default="page-.html")
    parser.add_argument('-j', '--join', type=str, help='json file dir', default="pages")
    parser.add_argument('-s', '--share', type=str, help='pdf2htmlEX share dir', default="bin/data")
    parser.add_argument('-t', '--toc', type=str, help='toc filename', default="toc.html")
    parser.add_argument('-m', '--meta', type=str, help='meta filename', default="")
    return parser.parse_args()

def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def read_meta_pdf(pdf_name):
    with open(pdf_name, 'rb') as fd:
        doc = PdfFileReader(fd)
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

NAMESPACES = {'OPF': 'http://www.idpf.org/2007/opf',
              'DC': "http://purl.org/dc/elements/1.1/"}

def read_meta_opf(opf_name):
    opf = NAMESPACES['OPF']
    dc = '{%s}' % NAMESPACES['DC']
    identifier = '{%s}scheme' % opf
    dc_len = len(dc)
    meta = {}
    with open(opf_name, 'rb') as fd:
        root = etree.parse(fd).find('{%s}metadata' % opf)
        for val in root.iterchildren():
            tag = val.tag
            if tag == '{%s}meta' % opf:
                name = val.get('name')
                name_arr = name.split(':')
                name = name_arr[1] if len(name_arr) > 1 else name
                meta[name] = val.get('content')
            elif tag.startswith(dc):
                tag = tag[dc_len:]
                if tag in ('subject', 'identifier'):
                    if tag == 'subject':
                        if tag not in meta:
                            meta[tag] = []
                        meta[tag].append(val.text)
                    else:
                        if tag not in meta:
                            meta[tag] = {}
                        meta[tag][val.get(identifier)] = val.text
                else:
                    meta[tag] = val.text
    return meta

def requests_douban_meta(meta):
    """
    通过原meta查询到豆瓣的meta
    """
    douban_id = meta['identifier']['DOUBAN']
    douban_url = 'https://api.douban.com/v2/book/%s' % douban_id
    r = requests.get(douban_url)
    douban_meta = r.json()
    douban_meta['type'] = 'pdf'
    douban_meta['title'] = meta['title']
    return douban_meta

if __name__ == '__main__':
    args = add_args()
    pdf = Pdf2Json(args)
    pdf.run()
    # pdf.toc_del_zero('out/tmp/toc.html')