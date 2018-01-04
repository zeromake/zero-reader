#!/bin/env python
# coding: utf-8

"""
epub2json
"""
import re
import os
import zipfile
import posixpath
import tempfile
import asyncio
import shutil
from lxml import etree, html
from .utils import (
    file_sha256,
    file_open,
    read_tree_meta_opf,
    NAMESPACES,
    requests_douban_meta,
    save_json,
    copy_zip_file,
    zip_join,
    HTTP_NAME,
    FONT_RE,
    FACE_RE_START,
    FACE_RE_END,
    logger,
    get_file_path_dir,
    get_file_path_name,
    tar_open,
    add_zipfile_to_tar,
    add_json_to_tar,
    save_xml_path,
    add_xml_tree_to_tar,
    save_xml_tree_path,
    open_temp_file
)

NAV_POINT = '{%s}navPoint' % NAMESPACES['DAISY']
NAV_LABEL = '{%s}navLabel' % NAMESPACES['DAISY']
NAV_CONTENT = '{%s}content' % NAMESPACES['DAISY']

class Epub2Json(object):
    """
    转换为json
    """
    meta_info_path = 'META-INF/container.xml'
    def __init__(self, options, loop=None):
        """
        初始化配置
        """
        # loop
        self._loop = loop or asyncio.get_event_loop()

        self.options = options
        # epub 文件
        self.file_name = options['file']
        # 是否压缩
        self.compress = options['compress']
        # 该文件的sha256值
        self.sha = file_sha256(self.file_name)
        # 输出文件夹
        self.dist = os.path.join(options['dist'], self.sha)
        # meta文件
        self.meta_path = 'meta.json'
        # container文件
        self.container_file = 'container.json'
        # toc文件
        self.toc_file = 'toc.json'
        # 图片文件夹
        self.image_dir = 'img'
        # 内容页文件夹
        self.page_dir = 'page'
        # css文件夹
        self.css_dir = 'css'
        # css文件深度
        self.css_deep = self.css_dir.count('/') + 1
        # 内容页文件名前缀
        self.page_join = 'page-'

        # 字体文件夹
        self.font_dir = 'font'

        # 内容页分割大小
        self.split_size = 1000 * 1024
        # opf文件路径
        self.opf_file = None
        # opf文件夹
        self.opf_dir = None
        # 所有的文件清单
        self.manifest_map = None
        self.manifests = None
        # 原内容清单
        self.tcontainer = []
        # 新内容清单
        self.container = []
        # 目录文件路径
        self.toc_zip_path = None
        #
        self.toc_dir_path = None
        # page嵌入css原路径
        self.css_set = set()
        # 新css清单
        self.css_list = []
        self.toc_link = {}
        self.page_map = {}
        self.container_count = 1
        self.guide = []
        self.temp_dir = tempfile.mkdtemp()
        self.container_page_dict = None
        self.file_set = set()
        if self.compress:
            self.tar_file = tar_open(self.dist + '.zip', 'w')
        
        self.meta_data = None

    async def run(self):
        """
        创建zip文件对象
        """
        if not self.compress:
            self.mkdirs()
        try:
            with zipfile.ZipFile(
                self.file_name,
                'r',
                compression=zipfile.ZIP_DEFLATED,
                allowZip64=True
            ) as epub_file:
                await self.load_meta_info(epub_file)
                await self.load_opf(epub_file)
                await self.save_container()
                await self.save_toc(epub_file)
        except zipfile.BadZipfile:
            raise Exception(0, 'Bad Zip file')
        except zipfile.LargeZipFile:
            raise Exception(1, 'Large Zip file')
        finally:
            if self.compress and self.tar_file:
                self.tar_file.close()
                self.tar_file = None

    def save_zip_file(self, zip_file, zip_path, output_path):
        """
        保存zip中的文件到tar或文件系统
        """
        if zip_path in self.file_set:
            if not isinstance(zip_path, str):
                raise TypeError("%s -> %s" % (zip_path, output_path))
            logger.warn("has file: %s", zip_path)
            return
        else:
            self.file_set.add(zip_path)
        if self.compress:
            return add_zipfile_to_tar(self.tar_file, zip_file, zip_path, output_path)
        else:
            output_path = os.path.join(self.dist, output_path)
            return copy_zip_file(zip_file, zip_path, output_path)

    def save_tar_json(self, output_path, data):
        """
        保存json
        """
        if self.compress:
            add_json_to_tar(self.tar_file, data, output_path)
        else:
            output_path = os.path.join(self.dist, output_path)
            save_json(output_path, data)

    def save_tar_xml(self, tree, output_path):
        """
        保存xml到tar
        """
        if self.compress:
            res = add_xml_tree_to_tar(self.tar_file, tree, output_path)
        else:
            output_path = os.path.join(self.dist, output_path)
            res = save_xml_tree_path(tree, output_path)
        return res

    def save_temp_xml(self, xml, output_path):
        """
        保存文件到临时文件夹
        """
        name = os.path.join(self.temp_dir, output_path)
        return save_xml_path(xml, name)

    def open_temp_file(self, output_path, *args, **k):
        """
        打开临时或dist路径下的文件
        """
        if self.compress:
            return open_temp_file(self.tar_file, output_path, *args, **k)
        else:
            output_path = os.path.join(self.dist, output_path)
            return file_open(output_path, *args, **k)

    def mkdirs(self):
        """
        创建文件夹
        """
        dirs = [
            self.dist,
            os.path.join(self.dist, self.image_dir),
            os.path.join(self.dist, self.page_dir),
            os.path.join(self.dist, self.font_dir),
            os.path.join(self.dist, self.css_dir)
        ]
        for row in dirs:
            if not os.path.exists(row):
                os.makedirs(row)

    async def load_meta_info(self, epub_file):
        """
        读取根文件
        """
        with epub_file.open(self.meta_info_path) as container:
            tree = etree.parse(container)
            for root_file in tree.findall(
                    '//xmlns:rootfile[@media-type]',
                    namespaces={'xmlns': NAMESPACES['CONTAINERNS']}
            ):
                if root_file.get('media-type') == "application/oebps-package+xml":
                    self.opf_file = root_file.get('full-path')
                    self.opf_dir = posixpath.dirname(self.opf_file)

    async def load_opf(self, epub_file):
        """
        读取opf文件
        """
        with epub_file.open(self.opf_file) as opf_file:
            tree = etree.parse(opf_file)
            meta = read_tree_meta_opf(tree)
            # manifest
            self.load_items(tree)
            # container(spine)
            self.load_container(tree)
            # split
            self.split_container(epub_file)
            # load_guide
            self.load_guide(tree, epub_file)
            # print(self.toc_link)
            # print(self.page_map)
            self.handle_page(epub_file)
        # meta
        if 'identifier' in meta and (
                'douban' in meta['identifier'] or
                'isbn' in meta['identifier']
        ):
            douban_meta = requests_douban_meta(meta)
        else:
            douban_meta = meta
        if 'cover' in meta and meta['cover'] in self.manifest_map:
            cover_name = self.manifest_map[meta['cover']]
            cover_path = zip_join(self.opf_dir, cover_name)
            cover_name = get_file_path_name(cover_name)
            # if '/' in cover_name:
            #     cover_name = cover_name[cover_name.rindex('/') + 1:]
            cover_name = cover_name.lower()
            self.save_zip_file(epub_file, cover_path, os.path.join(self.image_dir, cover_name))
            # epub_file.extract(cover_path, os.path.join(self.dist, self.image_dir))
            douban_meta['cover'] = os.path.join(self.image_dir, cover_name).replace('\\', '/')
        if len(self.css_list) > 0:
            douban_meta['page_style'] = self.css_list
        douban_meta['type'] = 'epub'
        douban_meta['container'] = self.container_file
        douban_meta['toc'] = self.toc_file
        douban_meta['sha'] = self.sha
        douban_meta['file_name'] = get_file_path_name(self.file_name)
        self.save_tar_json(self.meta_path, douban_meta)
        self.meta_data = douban_meta

    async def save_container(self):
        """
        保存内容清单
        """
        # print(str1)
        # page_re = re.compile()
        container_data = []
        for container_name, container_num in self.container:
            data = {
                'data-page-url': zip_join(self.page_dir, container_name),
                'index': container_num
            }
            if container_num in self.toc_link:
                link_ids = list(self.toc_link[container_num])
                data['ids'] = link_ids
            container_data.append(data)
        self.save_tar_json(self.container_file, container_data)

    def load_items(self, tree):
        """
        把所有items处理为字典
        """
        tree = tree.find('{%s}%s' % (NAMESPACES['OPF'], 'manifest'))
        self.manifest_map = {}
        self.manifests = []
        for item in tree.iterchildren():
            attrib = item.attrib
            self.manifests.append(attrib)
            self.manifest_map[attrib['id']] = attrib['href']

    def load_container(self, tree):
        """
        处理内容页
        """
        tree = tree.find('{%s}%s' % (NAMESPACES['OPF'], 'spine'))
        toc_id = tree.get('toc')
        if toc_id in self.manifest_map:
            self.toc_zip_path = zip_join(self.opf_dir, self.manifest_map[toc_id])
            self.toc_dir_path = get_file_path_dir(self.toc_zip_path)
        for cont in tree.iterchildren():
            cout_id = cont.get('idref')
            if cout_id in self.manifest_map:
                page_name = self.manifest_map[cout_id]
                # page_zip_path = zip_join(self.opf_dir, page_name)
                self.tcontainer.append(page_name)

    def load_guide(self, tree, epub_file):
        """
        处理guide中
        """
        tree = tree.find('{%s}%s' % (NAMESPACES['OPF'], 'guide'))
        for item in tree.iterchildren():
            href = item.get('href')
            href_arr = href.split('#')
            href_name = href_arr[0]
            # href_id = href_arr[1] if len(href_arr) > 1 else None
            if href_name not in self.tcontainer:
                href_path = zip_join(self.opf_dir, href_name)
                href_dir = get_file_path_dir(href_path)
                try:
                    self.copy_html(epub_file, href_path, href_dir, self.container_count)
                    self.page_map[href_path] = self.container_count
                    self.container_count += 1
                except KeyError:
                    logger.warn("guide -> %s not in epub", href_path)

    def split_container(self, epub_file):
        """
        切割内容
        """
        self.container_count = 1
        for container in self.tcontainer:
            zip_path = zip_join(self.opf_dir, container)
            logger.debug('copy container: ' + zip_path)
            container_dir = None
            if '/' in zip_path:
                container_dir = get_file_path_dir(zip_path)
                # container_dir = zip_path[:zip_path.rindex('/')]
            info = epub_file.getinfo(zip_path)
            if info.file_size > self.split_size:
                split_count = int(info.file_size / self.split_size)
                if info.file_size % self.split_size:
                    split_count += 1
                if split_count > 0:
                # with epub_file.open(zip_path) as html_file:
                    self.page_map[zip_path] = range(
                        self.container_count,
                        self.container_count + split_count
                    )
                    self.split_html(
                        epub_file,
                        zip_path,
                        container_dir,
                        split_count,
                        self.container_count
                    )
                    self.container_count += split_count - 1
                else:
                    self.page_map[zip_path] = self.container_count
                    self.copy_html(epub_file, zip_path, container_dir, self.container_count)
            else:
                # with epub_file.open(zip_path) as html_file:
                self.page_map[zip_path] = self.container_count
                self.copy_html(epub_file, zip_path, container_dir, self.container_count)
            self.container_count += 1

    def copy_html(
            self,
            epub_file,
            zip_path,
            container_dir,
            container_count
    ):
        """
        不分割拷贝
        """
        with epub_file.open(zip_path) as html_file:
            tree = html.parse(html_file)
            self.find_head_css(epub_file, tree, container_dir)
            body = tree.find('//body')
            page_xml = html.Element('div')
            for child in body.iterchildren():
                page_xml.append(child)
            self.save_html(page_xml, container_count)

    def split_html(
            self,
            epub_file,
            zip_path,
            container_dir,
            split_count,
            container_count
    ):
        """
        切割html
        """
        with epub_file.open(zip_path) as html_file:
            tree = html.parse(html_file)
            self.find_head_css(epub_file, tree, container_dir)
            body = tree.find('//body')
            children = body.getchildren()
            children_len = len(children)
            if children_len < split_count:
                self.copy_html(epub_file, zip_path, container_dir, container_count)
                self.container_count -= split_count - 1
                return
            split_num = int(children_len / split_count)
            page_count = 0
            page_xml = None
            for index, child in enumerate(children):
                if index % split_num == 0 and page_count < split_count - 1:
                    if page_xml is not None:
                        self.save_html(page_xml, container_count + page_count)
                        page_count += 1
                    page_xml = html.Element('div')
                page_xml.append(child)
            if page_xml is not None:
                self.save_html(page_xml, container_count + page_count)

    def save_html(self, xml, container_count):
        """
        保存并处理
        """
        page_name = '%s%d.html' % (self.page_join, container_count)
        logger.debug('save container: ' + page_name)
        links = xml.xpath('//@id')
        self.container.append((page_name, container_count))
        link_set = set()
        for link in links:
            link_set.add(link)
        # if len(link_set) > 0:
        if len(link_set) > 0:
            self.toc_link[container_count] = link_set
        return self.save_temp_xml(xml, page_name)
        # return etree.ElementTree(xml).write(
        #     os.path.join(self.dist, self.page_dir, page_name),
        #     pretty_print=True,
        #     encoding='utf-8',
        #     method='html'
        # )


    def find_head_css(
            self,
            epub_file,
            tree,
            container_dir
    ):
        """
        处理内容页head上的css
        """
        links = tree.findall('//link[@href]')
        for link in links:
            css_name = link.get('href')
            if container_dir:
                css_zip_path = zip_join(container_dir, css_name)
            else:
                css_zip_path = css_name
            if css_zip_path not in self.css_set:
                self.css_set.add(css_zip_path)
                css_name = get_file_path_name(css_name).lower()
                css_out_name = zip_join(self.css_dir, css_name)
                self.filter_font_by_css(epub_file, css_zip_path, css_out_name)
                logger.debug('save css: ' + css_zip_path + ' -> ' + css_out_name)
                # copy_zip_file(epub_file, css_zip_path, os.path.join(self.dist, css_out_name))
                self.css_list.append(css_out_name)

    def filter_font_by_css(self, epub_file, css_zip_path, css_out_path):
        """
        过滤字体
        """
        css_dir = get_file_path_dir(css_zip_path)
        self.flag = False
        def replace_copy_font(match):
            """
            替换css中的字体路径，并拷贝到指定目录
            """
            font_url = match.group(1)
            font_path = zip_join(css_dir, font_url)
            font_name = get_file_path_name(font_url)
            out_name = zip_join(self.font_dir, font_name)
            if self.save_zip_file(epub_file, font_path, out_name):
                out_url = ('../' * self.css_deep) + out_name
                logger.debug('save font: ' + font_path + ' -> ' + out_name)
                replace_str = 'url(%s)' % out_url
                if match.group(0).endswith(","):
                    replace_str += ','
                self.flag = True
            else:
                raw_str = match.group(0)
                if not raw_str.startswith("src:"):
                        self.flag = True
                # if not font_url.startswith("res:///") and not font_url.startswith("/"):
                #     out_url = ('../' * self.css_deep) + out_name
                #     replace_str = 'url(%s)' % out_url
                #     raw_str = match.group(0)
                #     if raw_str.endswith(","):
                #         replace_str += ','
                #     if raw_str.startswith("src:"):
                #         replace_str = "src: " + replace_str
                #     else:
                #         self.flag = True
                        
                # else:
                replace_str = ""
            return replace_str

        with epub_file.open(css_zip_path, 'r') as from_file:
            line = from_file.readline().decode('utf8')
            with self.open_temp_file(css_out_path, 'w', encoding='utf8') as out_fd:
                face_arr = []
                face_start = False
                while line:
                    if FACE_RE_START.match(line):
                        face_start = True
                    if face_start and FACE_RE_END.match(line):
                        face_start = False
                        if self.flag:
                            for temp in face_arr:
                                out_fd.write(temp)
                            out_fd.write(line)
                        self.flag = False
                        face_arr = []
                    elif face_start:
                        line = FONT_RE.sub(replace_copy_font, line)
                        face_arr.append(line)
                    else:
                        out_fd.write(line)
                    line = from_file.readline().decode('utf8')

    def handle_page(self, epub_file):
        """
        处理page中的锚点
        """
        # return
        for page_name, index in self.container:
            old_page_name = self.get_old_page_name(index)
            old_page_dir = get_file_path_dir(old_page_name)
            now_page_path = os.path.join(self.temp_dir, page_name)
            new_page_path = os.path.join(self.page_dir, page_name)
            with file_open(
                now_page_path,
                'r',
                encoding='utf8'
            ) as page_file:
                tree = html.parse(page_file)
                links = tree.findall('//a[@href]')
                for link in links:
                    href = link.get('href')
                    http_head = HTTP_NAME.findall(href)
                    if len(http_head) > 0:
                        continue
                    link_page_name = zip_join(old_page_dir, href)
                    now_page, link_id, query_str = self.handle_href(link_page_name)
                    if now_page is not None:
                        new_href = '%s%d.html' % (self.page_join, now_page)
                        if link_id:
                            new_href += '#' + link_id
                        if query_str:
                            new_href += '?' + query_str
                        link.set('href', new_href)
                images = tree.findall(
                    '//img[@src]'
                )
                for img in images:
                    img_src = img.get('src')
                    img_zip_path = zip_join(old_page_dir, img_src)
                    if '/' in img_src:
                        img_out_name = zip_join(
                            self.image_dir,
                            get_file_path_name(img_src)
                        )
                    else:
                        img_out_name = zip_join(self.image_dir, img_src)
                    self.save_zip_file(
                        epub_file,
                        img_zip_path,
                        img_out_name
                    )
                    old_class = img.get('class')
                    tmp = 'lozad'
                    if old_class:
                        tmp += " " + old_class
                    img.set('class', tmp)
                    del img.attrib['src']
                    img.set('data-src', img_out_name)
                images = tree.findall(
                    "//image"
                )
                img_len = len(images)
                if img_len > 0:
                    for img in images:
                        name_spaces = 'xlink:href'
                        img_src = img.get(name_spaces)
                        img_zip_path = zip_join(old_page_dir, img_src)
                        if '/' in img_src:
                            img_out_name = zip_join(self.image_dir, get_file_path_name(img_src))
                        else:
                            img_out_name = zip_join(self.image_dir, img_src)
                        self.save_zip_file(epub_file, img_zip_path, os.path.join(img_out_name))
                        old_class = img.get('class')
                        tmp = 'lozad'
                        if old_class:
                            tmp += " " + old_class
                        img.set('class', tmp)
                        del img.attrib[name_spaces]
                        img.set('data-src', img_out_name)
                with file_open(os.path.join(self.dist, new_page_path), 'wb') as xml_file:
                    root_tree = tree.find("//div")
                    for child in root_tree.iterchildren():
                        string_ = html.tostring(
                            child,
                            pretty_print=True,
                            method="html",
                            encoding='utf-8'
                        )
                        xml_file.write(
                            string_
                        )
        shutil.rmtree(self.temp_dir)

    def get_old_page_name(self, count):
        """
        根据count数取到原有name
        """
        for old_page_name, new_page in self.page_map.items():
            if isinstance(new_page, int):
                if count == new_page:
                    return old_page_name
            elif count in new_page:
                return old_page_name
        return None

    async def save_toc(self, epub_file):
        """
        处理并保存toc
        """
        if not self.toc_zip_path:
            return
        self.container_page_dict = { container_name : page for container_name, page in self.container}
        with epub_file.open(self.toc_zip_path, 'r') as toc_file:
            tree = etree.parse(toc_file)
            nav_map = tree.find('//xmlns:navMap', namespaces={'xmlns': NAMESPACES['DAISY']})
            tocs_info = []
            for point in nav_map.iterchildren():
                if point.tag == NAV_POINT:
                    toc_info = self.handle_toc_item(point)
                    tocs_info.append(toc_info)
            self.save_tar_json(self.toc_file, tocs_info)

    def handle_toc_item(self, nav_point, level=1):
        """
        递归处理toc
        """
        toc_info = {'level': level}
        toc_info['id'] = nav_point.get('id')
        toc_info['play_order'] = nav_point.get('playOrder')
        for item in nav_point.iterchildren():
            if item.tag == NAV_LABEL:
                text = item.getchildren()
                toc_info['text'] = text[0].text
            elif item.tag == NAV_POINT:
                if 'children' not in toc_info:
                    toc_info['children'] = []
                toc_info['children'].append(self.handle_toc_item(item, level + 1))
            elif item.tag == NAV_CONTENT:
                href_name = item.get('src')
                page, hash_str, query_str = self.handle_href(zip_join(self.toc_dir_path, href_name))
                if page is not None:
                    toc_info['page'] = page
                    new_href = '%s/%s%d.html' % (self.page_dir, self.page_join, page)
                    toc_info['index'] = page - 1
                    toc_info['page_url'] = new_href
                else:
                    toc_info['src'] = href_name
                if hash_str:
                    toc_info['hash'] = hash_str
                if query_str:
                    toc_info['query'] = query_str
        return toc_info

    def handle_href(self, href_name):
        """
        处理href到新的定位
        """
        hash_str = None
        query_str = None
        page = None
        if '#' in href_name:
            href_arr = href_name.split('#')
            if len(href_arr) > 1:
                hash_str = href_arr[1]
            href_name = href_arr[0]
        if hash_str and '?' in hash_str:
            query_arr = hash_str.split('?')
            if len(query_arr) > 1:
                query_str = hash_str[1]
            hash_str = hash_str[0]
        if href_name in self.page_map:
            now_page = self.page_map[href_name]
            if isinstance(now_page, int):
                page = now_page
            else:
                for page_num in now_page:
                    if not hash_str:
                        page = page_num
                        break
                    if page_num in self.toc_link and hash_str in self.toc_link[page_num]:
                        page = page_num
                        break
                if not page:
                    page = now_page[0]
        return page, hash_str, query_str



if __name__ == '__main__':
    pass
