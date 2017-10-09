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
from lxml import etree



def deep_tree(roots, level, callback):
    for row in roots.iterchildren():
        callback(row, level)

class Pdf2Json(object):
    def __init__(self, options):
        """
        初始化
        """
        self.pdf_name = options.file
        self.dist = os.path.join(options.dist, self.file_sha256(self.pdf_name))
        self.out = options.out
        self.css = options.css
        self.join = options.join
        self.page = os.path.join(self.join, options.page)
        self.img_dir = 'img'
        self.share = options.share
        self.toc = options.toc

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
        self.deldir()
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
        return subprocess.call([
            pdf2html[1],
            '--embed-css 0',
            '--embed-font 0',
            '--embed-image 0',
            '--embed-javascript 0',
            '--embed-outline 0',
            '--outline-filename %s' % self.toc,
            '--split-pages 1',
            '--css-filename %s' % self.css,
            '--page-filename %s' % self.page,
            '--space-as-offset 1',
            '--data-dir %s' % self.share,
            '--dest-dir %s' % self.out,
            self.pdf_name,
            'index.html'
        ])

    def extract_zip(self, zip_name):
        with zipfile.ZipFile(zip_name,'r') as f:
            for file in f.namelist():
                f.extract(file,"bin/")

    def toc_to_json(self, toc_html_name, toc_json_name):
        """
        把html的toc转为json
        """
        handle = {
            'data-dest-detail': lambda x: tuple(json.loads(x)),
            'href': lambda x: x[1:]
        }
        with open(toc_html_name, 'r') as fd:
            tree = etree.parse(fd)
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
            with open(toc_json_name, 'w') as fd:
                json.dump(toc, fd, ensure_ascii=False, indent="  ")
        self.tocs = toc
    
    def container_to_json(self, container_name, json_name, callback=None):
        """
        转换内容页
        """
        xmlns = 'http://www.w3.org/1999/xhtml'
        namespaces = {'ns': xmlns}
        page_id_to_index = {}
        containers = []
        with open(container_name) as fd:
            tree = etree.parse(fd)
            container_root = tree.xpath(u'//ns:div[@id="page-container"]', namespaces = namespaces)[0]
            last_class = None
            index = 0
            for row in container_root.iterchildren():
                item = {key: val for key, val in row.items() if key != 'data-page-no' and not (key == 'class' and val == last_class)}
                page_id_to_index[item['id']] = index
                item['index'] = index
                containers.append(item)
                if callback:
                    callback(item)
                last_class = row.get('class')
                index += 1
        if json_name:
            with open(json_name, 'w') as fd:
                json.dump(containers, fd, ensure_ascii=False, indent="  ")
        self.containers = containers
        self.pages = page_id_to_index

    def copy_page(self, page):
        """
        拷贝page的html，并做好预处理
        """
        page_name = page['data-page-url']
        out_dir = self.dist
        input_dir = self.out
        join_dir = 'img'
        input_name = os.path.join(input_dir, page_name)
        out_name = os.path.join(out_dir, page_name)
        with open(input_name, 'r') as fd:
            tree = etree.parse(fd)
            for img in tree.xpath('//img'):
                parent = img.getparent()
                div = etree.Element('div')
                for key, val in img.items():
                    if key == 'src':
                        shutil.copyfile(os.path.join(input_dir, val), os.path.join(out_dir, join_dir, val))
                        style = "background-image: url('" + join_dir + '/' + val + "'); background-size: 100%;"
                        div.set('style', style)
                    elif key == 'alt':
                        if val != '':
                            div.set('title', val)
                    else:
                        if  key == 'class':
                            val += ' global_background_div'
                        div.set(key, val)
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
                        font = font_pat.sub(self.font_copy, line)
                        out_fd.write(font)
                    elif line == '@media print{\n':
                        media_print = True
                    elif line == '}\n' and media_print:
                        media_print = False
                    out_fd.write(line)
                    line = fd.readline()
        with open(os.path.join(self.dist, self.zoom), 'w') as fd:
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
        return 'url(%s)' % (self.font_join + '/' + font_name)

def main(options):
    if len(options) < 1:
        print("argv miss pdf name")
        return
    pdf_name = options[0]
    return subprocess.call([
        'pdf2html',
        '--embed-css 0',
        '--embed-font 0',
        '--embed-image 0',
        '--embed-javascript 0',
        '--embed-outline 0',
        '--outline-filename toc.html',
        '--split-pages 1',
        '--css-filename style.css',
        '--page-filename pages/page-.html',
        '--space-as-offset 1',
        '--data-dir /home/zero/project/pdf2html/share',
        '--dest-dir ./out',
        pdf_name,
        'index.html'
    ])

def add_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, help='pdf file')
    parser.add_argument('-o', '--out', type=str, help='out file dir', default="out/tmp")
    parser.add_argument('-d', '--dist', type=str, help='dist file dir', default="library")
    parser.add_argument('-c', '--css', type=str, help='css file name', default="style.css")
    parser.add_argument('-p', '--page', type=str, help='page file name', default="page-.html")
    parser.add_argument('-j', '--join', type=str, help='json file dir', default="pages")
    parser.add_argument('-s', '--share', type=str, help='pdf2htmlEX share dir', default="bin/data")
    parser.add_argument('-t', '--toc', type=str, help='toc filename', default="toc.html")
    return parser.parse_args()


if __name__ == '__main__':
    args = add_args()
    pdf = Pdf2Json(args)
    pdf.run()