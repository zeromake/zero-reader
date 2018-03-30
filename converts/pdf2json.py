#!/bin/env python
# coding: utf-8

"""
pdf to json
"""

import re
import os
import json
import shutil
import tempfile
import zipfile
import platform
import subprocess

import asyncio
# from lxml import etree, html
from .utils import (
    PNGBIN,
    deep_tree,
    read_meta_pdf,
    read_meta_opf,
    requests_douban_meta,
    file_open,
    read_json,
    save_json,
    file_sha256,
    zip_join,
    PDF_EXEC,
    logger,
    get_file_path_name
)


class Pdf2Json(object):
    """
    转换
    """
    def __init__(self, options, loop=None):
        """
        初始化
        """

        self.sysstr = platform.system()
        self.pngbin = PNGBIN.get(self.sysstr)
        self._loop = loop or asyncio.get_event_loop()
        self.is_png_compress = options['png'] == 1
        self.pdf_name = options['file']
        self.sha = file_sha256(self.pdf_name)
        self.abs_url = '/library/' + self.sha + '/'
        self.dist = os.path.join(options['dist'], self.sha)
        self.out = os.path.join(options['out'], self.sha)
        self.css = options['css']
        self.join = options['join']
        self.page = os.path.join(self.join, options['page'])
        self.img_dir = 'img'
        self.share = options['share']
        self.toc = options['toc']
        self.meta = options['meta']
        self.content_class = 'html_content'

        self.meta_file = 'meta.json'
        self.pages = None
        self.tocs = None
        self.containers = None
        self.font_join = 'font'
        self.zoom = 'zoom.json'
        self.page_css = []
        self.meta_data = None
        self.links_zoom = {}
        self.links_css = {}
        self.del_css = set()

    async def run(self):
        """
        执行处理
        """
        if os.path.exists(self.dist):
            print('book sha256: %s is exist' % self.dist)
            return
        await self.mkdir()
        await self.exec_pdf()
        await self.container_to_json(
            os.path.join(self.out, 'index.html'),
            os.path.join(self.dist, 'container.json'),
            self.copy_page
        )
        await self.toc_to_json(
            os.path.join(self.out, self.toc),
            os.path.join(self.dist, 'toc.json')
        )
        await self.css_copy()
        await self.read_meta()
        # self.deldir()

    async def read_meta(self):
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
        meta['type'] = 'pdf'
        meta['page_style'] = self.page_css
        meta['container'] = 'container.json'
        if os.path.exists(os.path.join(self.dist, 'toc.json')):
            meta['toc'] = 'toc.json'
        meta['zoom'] = 'zoom.json'
        meta['file_name'] = get_file_path_name(self.pdf_name)
        cover_url = zip_join(self.img_dir, 'bg1.png')
        if os.path.exists(os.path.join(self.dist, cover_url)):
            meta['cover'] = cover_url
        save_json(os.path.join(self.dist, self.meta_file), meta)
        # db_name = os.path.join('library', 'db.json')
        # db_data = []
        # if os.path.exists(db_name):
        #     db_data = read_json(db_name)
        #     # with open(db_name, 'r', encoding='utf8') as fd:
        #     #     db_data = json.load(fd)
        # sha_set = set([row['sha']for row in db_data])
        # if self.sha not in sha_set:
        #     db_data.append(meta)
        # save_json(db_name, db_data)
        self.meta_data = meta
        # with open(db_name, 'w', encoding='utf8') as fd:
        #     json.dump(db_data, fd, ensure_ascii=False, indent="  ")

    async def mkdir(self):
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

    async def exec_pdf(self):
        """
        转换
        """
        lock_name = os.path.join(self.out, 'exec.lock')
        if os.path.exists(lock_name):
            with file_open(lock_name, 'r', encoding='utf8') as file_:
                if file_.read(1) == '0':
                    logger.info('MISS exec_pdf')
                    return

        pdf2html_dict = {
            "Windows": ('bin/pdf2htmlEX-win32.zip', 'bin/pdf2htmlEX.exe'),
            "Linux": ('bin/pdf2htmlEX-linux-x64.zip', 'bin/pdf2htmlEX.sh'),
            "Darwin": (None, "pdf2htmlex")
        }
        pdf2html = pdf2html_dict.get(self.sysstr)
        if pdf2html:
            if pdf2html[0]:
                if not os.path.exists(pdf2html[1]):
                    self.extract_zip(pdf2html[0])
        else:
            raise NameError("bin not on")
        if self.sysstr == 'Linux':
            subprocess.call(["chmod", "+x", pdf2html[1]])
            subprocess.call(["chmod", "+x", 'bin/pdf2htmlEX'])
        temp_name = tempfile.mktemp()
        shutil.copyfile(self.pdf_name, temp_name)
        try:
            exec_str = " ".join([
                pdf2html[1],
                '--font-format', 'woff',
                '--bg-format', 'png',
                '--optimize-text', '1',
                '--space-as-offset', '0',
                '--embed-css', '0',
                '--embed-font', '0',
                '--embed-image', '0',
                '--embed-javascript', '0',
                '--embed-outline', '0',
                '--outline-filename', self.toc,
                '--split-page', '1',
                '--css-filename', self.css,
                '--page-filename', self.page,
                '--data-dir', self.share,
                '--dest-dir', self.out,
                temp_name,
                'index.html'
            ])
            popen_obj = subprocess.Popen(
                exec_str,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True
            )
            flag = False
            read_num = 1
            offset = 0
            offset_start = False
            old_line = b''
            add_set = {int('9' * i) for i in range(1, 5)}
            state = 1
            # while True:
            #     line = popen_obj.stdout.readline()
            #     print(line)
            #     if not line:
            #         break
            while True:
                line = popen_obj.stdout.read(read_num)
                if not line:
                    state = popen_obj.wait()
                    break
                if not flag and line == b'W':
                    if offset_start:
                        flag = True
                        read_num = offset
                        offset_start = False
                        match = PDF_EXEC.match(old_line.decode('utf8'))
                        task_progress = match.group(1)
                        task_count = int(match.group(2))
                        logger.debug('progress: %s/%d' % (task_progress, task_count))
                        line = line + popen_obj.stdout.read(read_num -1)
                    else:
                        offset_start = True

                if offset_start:
                    offset += 1
                    old_line += line
                if flag:
                    line_str = line.decode('utf8')
                    match = PDF_EXEC.match(line_str)
                    if match:
                        task_progress = int(match.group(1))
                        if task_progress in add_set:
                            read_num += 1
                        logger.debug('progress: %d/%d' % (task_progress, task_count))
                    else:
                        flag = False
                        read_num = 1
                        offset = 0
                        offset_start = False
                        old_line = b''
        finally:
            os.remove(temp_name)
        with file_open(os.path.join(self.out, 'exec.lock'), 'w') as file_:
            file_.write(str(state))

    def extract_zip(self, zip_name):
        """
        解压bin下的zip
        """
        with zipfile.ZipFile(zip_name, 'r') as file_:
            for file_name in file_.namelist():
                file_.extract(file_name, "bin/")

    async def toc_to_json(self, toc_html_name, toc_json_name, is_try=False):
        """
        把html的toc转为json
        """
        from lxml import etree
        if os.path.getsize(toc_html_name) < 1:
            logger.debug('MISS empty TOC')
            return
        handle = {
            'data-dest-detail': lambda x: tuple(json.loads(x)),
            'href': lambda x: x[1:]
        }
        with file_open(toc_html_name, 'r', encoding='utf8', errors="ignore") as file_:
            tree = etree.parse(file_)
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
                            index, page_no, page_url = self.pages.get(toc_item['href'])
                            toc_item['page'] = page_no
                            toc_item['page_url'] = page_url
                            toc_item['index'] = index
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

    async def container_to_json(self, container_name, json_name, callback=None):
        """
        转换内容页
        """
        from lxml import etree
        page_id_to_index = {}
        containers = []
        # out_bg_css = os.path.join(self.dist, 'bg.css')
        # self.page_css.append('bg.css')
        # background = []
        # background.append("div.background_img_class{")
        # background.append("  background-size: 100%;")
        # background.append("}")
        with file_open(container_name, encoding='utf8', errors="ignore") as file_:
            tree = etree.parse(file_)
            container_root = tree.xpath(u'//div[@id="page-container"]')[0]
            last_class = None
            index = 0
            # page_id_map = {}
            for row in container_root.iterchildren():
                item = {key: val for key, val in row.items()
                        if not (
                            key == 'class' and
                            val == last_class
                        )}
                data_page_no = item['data-page-no']
                try:
                    page_no = int('0x' + data_page_no, 16)
                except Exception:
                    page_no = data_page_no
                page_id_to_index[item['id']] = (index, page_no, item['data-page-url'])

                item['index'] = index
                containers.append(item)
                last_class = row.get('class')
                index += 1
            self.pages = page_id_to_index
            for container in containers:
                if callback:
                    await callback(container)
        if json_name:
            save_json(json_name, containers)
        # with file_open(out_bg_css, 'w', encoding='utf8') as file_:
        #     file_.write("\n".join(background))
        self.containers = containers

    async def copy_page(self, page):
        """
        拷贝page的html，并做好预处理
        """
        from lxml import etree
        page_name = page['data-page-url']
        out_dir = self.dist
        input_dir = self.out
        join_dir = 'img'
        input_name = os.path.join(input_dir, page_name)
        out_name = os.path.join(out_dir, page_name)
        class_pat = re.compile(r'pages/page-(\d+)\.html')
        class_name_join = class_pat.match(page_name).group(1)
        with file_open(input_name, 'r', encoding='utf8', errors="ignore") as file_:
            tree = etree.parse(file_)
            root = tree.getroot()
            old_class = root.get('class')
            tmp = self.content_class
            if old_class:
                tmp += " " + old_class
            root.set('class', tmp)
            # for span_class in self.del_css:
            #     for span in tree.xpath('//span[@class=\'_ %s\']' % span_class):
            #         parent_span = span.getparent()
            #         parent_span.remove(span)
            for img in tree.xpath('//img'):
                # parent = img.getparent()
                # div = lxml.etree.Element('div')
                val = img.get('src')
                input_path = os.path.join(input_dir, val)
                # logger.debug("pngquant : %s", input_path)
                if self.is_png_compress and self.pngbin:
                    process = await asyncio.create_subprocess_exec(
                        self.pngbin,
                        input_path,
                        '-o', os.path.join(out_dir, join_dir, val),
                        loop=self._loop
                    )
                    await process.wait()
                else:
                    shutil.copyfile(
                        os.path.join(input_dir, val),
                        os.path.join(out_dir, join_dir, val)
                    )
                old_class = img.get('class')
                tmp = 'lozad'
                if old_class:
                    tmp += " " + old_class
                img.set('class', tmp)
                del img.attrib['src']
                img.set('data-src', zip_join(join_dir, val))
            px_and_pat = re.compile(r'([\w-]+): *(-?\d+(?:\.\d+)?)(px|pt)')
            field = ('attribute', 'size', 'unit')
            class_index = 1
            for link in tree.xpath('//div[@style]'):
                style = link.get("style")
                parent_link = link.getparent()
                # del link.attrib['style']
                old_class = link.get("class")
                parent_link.remove(link)
                style_arr = style.split(";")
                class_name = 'link_%s_%s'% (class_name_join, class_index)
                new_class = class_name
                if old_class:
                    new_class += " %s" % old_class
                old_class = parent_link.set("class", new_class)
                class_name = "." + class_name
                href = parent_link.get('href')
                if href.startswith("#"):
                    page_id = href[1:]
                    page_data = self.pages.get(page_id)
                    if page_data:
                        parent_link.set(
                            'data-href',
                            json.dumps({
                                'index': page_data[0],
                                'page': page_data[1]
                            })
                        )
                        parent_link.set('href', '?page=%s' % page_data[0])
                else:
                    parent_link.set("target", "_blank")
                class_index += 1
                for style_item in style_arr:
                    match = px_and_pat.match(style_item)
                    if match:
                        item = {
                            key: val
                            for key, val in
                            zip(field, match.groups())
                        }
                        item['size'] = float(item['size'])
                        if class_name not in self.links_zoom:
                            self.links_zoom[class_name] = []
                        self.links_zoom[class_name].append(item)
                    elif style_item != "":
                        if class_name not in self.links_css:
                            self.links_css[class_name] = []
                        self.links_css[class_name].append(style_item)
                # img_sha = file_sha256(os.path.join(input_dir, val))
                # background.append("div.img_" + img_sha + "{")
                # background.append(
                #     "  background-image: url('./" +
                #     join_dir +
                #     '/' +
                #     val +
                #     "');"
                # )
                # background.append("}")
                # val = img.get('alt')
                # if val != '':
                #     div.set('title', val)
                # val = img.get('class')
                # val += ' img_' + img_sha + ' background_img_class'
                # div.set('class', val)
                # parent.replace(img, div)
            tree.write(
                out_name,
                pretty_print=True,
                encoding='utf-8',
                method='html'
            )

    async def css_copy(self):
        """
        css 拷贝
        """
        css_name = os.path.join(self.out, self.css)
        out_name = os.path.join(self.dist, self.css)
        self.page_css.append(self.css)
        font_pat = re.compile(r'url\((\w+\.woff)\)')
        px_and_pat = re.compile(r'(.*){([\w-]+):(-?\d+(?:\.\d+)?)(px|pt);}')
        # filter_pat = re.compile(r'^\._[\d\w]+$')
        zoom_arr = self.links_zoom
        field = ('select', 'attribute', 'size', 'unit')
        zoom = {
            'width': 0,
            'height': 0
        }
        with file_open(css_name, 'r', encoding='utf-8', errors="ignore") as file_:
            with file_open(out_name, 'w', encoding='utf-8', errors="ignore") as out_fd:
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
                            if item['select'] == '.w0':
                                zoom['width'] = item['size']
                            elif item['select'] == '.h0':
                                zoom['height'] = item['size']
                            item['media_print'] = media_print
                            select = item['select']
                            # if select.startswith("._") and item['attribute'] == "margin-left":
                            #     self.del_css.add(select[1:])
                            # else:
                            del item['select']
                            if select not in zoom_arr:
                                zoom_arr[select] = []
                            # if not filter_pat.match(item['select']) or not (item['attribute'] == 'width'):
                            zoom_arr[select].append(item)
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
                for css_select, values in self.links_css.items():
                    out_fd.write('%s{\n' % css_select)
                    out_fd.write(";\n".join(values))
                    out_fd.write('\n}\n')
                # out_fd.write('.link_base{\ndisplay:block;background-color:rgba(255,255,255,0.000001);\nposition:absolute;\nborder-style:none;\n}')
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


if __name__ == '__main__':
    pass
    # option = add_args()
    # pdf_obj = Pdf2Json(option)
    # pdf_obj.run()
