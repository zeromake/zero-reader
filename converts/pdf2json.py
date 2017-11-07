#!/bin/env python
# coding: utf-8

"""
pdf to json
"""

import re
import os
import json
import shutil
import zipfile
import argparse
import platform
import subprocess
from lxml import etree
from utils import deep_tree, read_meta_pdf, read_meta_opf,\
     requests_douban_meta, file_open, read_json, save_json, file_sha256


class Pdf2Json(object):
    """
    转换
    """
    def __init__(self, options):
        """
        初始化
        """
        self.pdf_name = options.file
        self.sha = file_sha256(self.pdf_name)
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
        """
        分发读取
        """
        opf_name = self.pdf_name[:self.pdf_name.rfind('.')] + '.opf'
        if self.meta != '' and os.path.exists(self.meta):
            meta = read_meta_opf(self.meta)
        elif os.path.exists(opf_name):
            meta = read_meta_opf(opf_name)
        else:
            meta = read_meta_pdf(self.pdf_name)
        if 'identifier' in meta and \
                (('douban' in meta['identifier'])
                    or ('isbn' in meta['identifier'])):
            meta = requests_douban_meta(meta)
        meta['sha'] = self.sha
        if 'title' not in meta:
            meta['title'] = self.pdf_name[
                self.pdf_name.rfind('/') + 1: self.pdf_name.rfind('.')
            ]
        save_json(os.path.join(self.dist, 'meta.json'), meta)
        db_name = os.path.join('library', 'db.json')
        db_data = []
        if os.path.exists(db_name):
            db_data = read_json(db_name)
            # with open(db_name, 'r', encoding='utf8') as fd:
            #     db_data = json.load(fd)
        sha_set = set([row['sha']for row in db_data])
        if self.sha not in sha_set:
            db_data.append(meta)
        save_json(db_name, db_data)
        # with open(db_name, 'w', encoding='utf8') as fd:
        #     json.dump(db_data, fd, ensure_ascii=False, indent="  ")

    def mkdir(self):
        """
        创建文件夹
        """
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
        """
        删除
        """
        shutil.rmtree(self.out)

    def exec_pdf(self):
        """
        转换
        """
        lock_name = os.path.join(self.out, 'exec.lock')
        if os.path.exists(lock_name):
            with file_open(lock_name, 'r', encoding='utf8') as file_:
                if file_.read(1) == '0':
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
            '--embed-css', '0',
            '--embed-font', '0',
            '--embed-image', '0',
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
        with file_open(os.path.join(self.out, 'exec.lock'), 'w') as file_:
            file_.write(str(state))

    def extract_zip(self, zip_name):
        """
        解压bin下的zip
        """
        with zipfile.ZipFile(zip_name, 'r') as file_:
            for file_name in file_.namelist():
                file_.extract(file_name, "bin/")

    def toc_to_json(self, toc_html_name, toc_json_name, is_try=False):
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
        with file_open(toc_html_name, 'r', encoding='utf8') as file_:
            try:
                tree = etree.parse(file_)
            except etree.XMLSyntaxError as error:
                if is_try:
                    raise error
                file_.seek(0)
                self.toc_del_zero(toc_html_name)
                return self.toc_to_json(toc_html_name, toc_json_name, True)
            toc = []

            def callback_toc(item, level):
                """
                递归中的回调
                """
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
                            index = level - 1
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
            save_json(toc_json_name, toc)
        self.tocs = toc

    def toc_del_zero(self, toc_html_name):
        """
        删除0x00
        """
        with file_open(toc_html_name, 'rb') as file_:
            data = file_.read()
        buffer = bytearray()
        for char in data:
            if char != 0x00:
                buffer.append(char)
        with file_open(toc_html_name, 'wb') as file_:
            file_.write(buffer)

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
        with file_open(container_name, encoding='utf8') as file_:
            tree = etree.parse(file_)
            container_root = tree.xpath(u'//div[@id="page-container"]')[0]
            last_class = None
            index = 0
            for row in container_root.iterchildren():
                item = {key: val for key, val in row.items()
                        if key != 'data-page-no' and not (
                            key == 'class' and
                            val == last_class
                        )}
                page_id_to_index[item['id']] = index
                item['index'] = index
                containers.append(item)
                if callback:
                    callback(item, background)
                last_class = row.get('class')
                index += 1
        if json_name:
            save_json(json_name, containers)
        with file_open(out_bg_css, 'w', encoding='utf8') as file_:
            file_.write("\n".join(background))
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
        with file_open(input_name, 'r', encoding='utf8') as file_:
            tree = etree.parse(file_)
            for img in tree.xpath('//img'):
                parent = img.getparent()
                div = etree.Element('div')
                val = img.get('src')
                shutil.copyfile(
                    os.path.join(input_dir, val),
                    os.path.join(out_dir, join_dir, val)
                )
                img_sha = file_sha256(os.path.join(input_dir, val))
                background.append("div.img_" + img_sha + "{")
                background.append(
                    "  background-image: url('./" +
                    join_dir +
                    '/' +
                    val +
                    "');"
                )
                background.append("}")
                val = img.get('alt')
                if val != '':
                    div.set('title', val)
                val = img.get('class')
                val += ' img_' + img_sha + ' background_img_class'
                div.set('class', val)
                parent.replace(img, div)
            tree.write(
                out_name,
                pretty_print=True,
                encoding='utf-8',
                method='html'
            )

    def css_copy(self):
        """
        css 拷贝
        """
        css_name = os.path.join(self.out, self.css)
        out_name = os.path.join(self.dist, self.css)
        font_pat = re.compile(r'url\((\w+\.woff)\)')
        px_and_pat = re.compile(r'(.*){([\w-]+):(-?\d+(?:\.\d+)?)(px|pt);}')
        zoom_arr = []
        field = ('select', 'attribute', 'size', 'unit')
        zoom = {
            'width': 0,
            'height': 0
        }
        with file_open(css_name, 'r', encoding='utf-8') as file_:
            with file_open(out_name, 'w', encoding='utf-8') as out_fd:
                line = file_.readline()
                media_print = False
                while line:
                    match = px_and_pat.match(line)
                    if match:
                        if not media_print:
                            item = {
                                key: val
                                for key, val in
                                zip(field, match.groups())
                            }
                            item['size'] = float(item['size'])
                            if item['select'].startswith('.w'):
                                zoom['width'] = max(
                                    (
                                        item['size'],
                                        zoom['width']
                                    )
                                )
                            elif item['select'].startswith('.h'):
                                zoom['height'] = max(
                                    (
                                        item['size'],
                                        zoom['height']
                                    )
                                )
                            item['media_print'] = media_print
                            zoom_arr.append(item)
                    elif line.startswith('@font-face{font-family'):
                        line = font_pat.sub(self.font_copy, line)
                        out_fd.write(line)
                    elif line == '@media print{\n':
                        media_print = True
                    elif line == '}\n' and media_print:
                        media_print = False
                    else:
                        out_fd.write(line)
                    line = file_.readline()
        zoom['css'] = zoom_arr
        save_json(os.path.join(self.dist, self.zoom), zoom)

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
    parser.add_argument(
        '-f',
        '--file',
        type=str,
        help='pdf file'
    )
    parser.add_argument(
        '-o',
        '--out',
        type=str,
        help='out file dir',
        default="out"
    )
    parser.add_argument(
        '-d',
        '--dist',
        type=str,
        help='dist file dir',
        default="library"
    )
    parser.add_argument(
        '-c',
        '--css',
        type=str,
        help='css file name',
        default="style.css"
    )
    parser.add_argument(
        '-p',
        '--page',
        type=str,
        help='page file name',
        default="page-.html"
    )
    parser.add_argument(
        '-j',
        '--join',
        type=str,
        help='json file dir',
        default="pages"
    )
    parser.add_argument(
        '-s',
        '--share',
        type=str,
        help='pdf2htmlEX share dir',
        default="bin/data"
    )
    parser.add_argument(
        '-t',
        '--toc',
        type=str,
        help='toc filename',
        default="toc.html"
    )
    parser.add_argument(
        '-m',
        '--meta',
        type=str,
        help='meta filename',
        default=""
    )
    return parser.parse_args()


if __name__ == '__main__':
    option = add_args()
    pdf_obj = Pdf2Json(option)
    pdf_obj.run()
