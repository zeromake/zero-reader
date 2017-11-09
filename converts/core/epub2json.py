#!/bin/env python
# coding: utf-8

"""
epub2json
"""
import os
import zipfile
import posixpath
from lxml import etree
from .utils import (
    file_sha256,
    file_open,
    read_tree_meta_opf,
    NAMESPACES,
    requests_douban_meta,
    save_json,
    copy_zip_file,
    zip_join,
    HTTP_NAME
)


class Epub2Json(object):
    """
    转换为json
    """
    meta_info_path = 'META-INF/container.xml'
    def __init__(self, options):
        """
        初始化配置
        """
        self.options = options
        # epub 文件
        self.file_name = options['file']
        # 该文件的sha256值
        self.sha = file_sha256(self.file_name)
        # 输出文件夹
        self.dist = os.path.join(options['dist'], self.sha)
        # meta文件
        self.meta_dist_path = os.path.join(self.dist, 'meta.json')
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
        # 内容页文件名前缀
        self.page_join = 'page-'

        # 内容页分割大小
        self.split_size = 100 * 1024
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
        # page嵌入css原路径
        self.css_set = set()
        # 新css清单
        self.css_list = []
        self.toc_link = {}
        self.page_map = {}
        self.container_count = 1
        self.guide = []

    def run(self):
        """
        创建zip文件对象
        """
        self.mkdirs()
        try:
            with zipfile.ZipFile(
                self.file_name,
                'r',
                compression=zipfile.ZIP_DEFLATED,
                allowZip64=True
            ) as epub_file:
                self.load_meta_info(epub_file)
                self.load_opf(epub_file)
                # self.load_meta(epub_file)
        except zipfile.BadZipfile:
            raise Exception(0, 'Bad Zip file')
        except zipfile.LargeZipFile:
            raise Exception(1, 'Large Zip file')

    def mkdirs(self):
        """
        创建文件夹
        """
        dirs = [
            self.dist,
            os.path.join(self.dist, self.image_dir),
            os.path.join(self.dist, self.page_dir),
            os.path.join(self.dist, self.css_dir)
        ]
        for row in dirs:
            if not os.path.exists(row):
                os.makedirs(row)

    def load_meta_info(self, epub_file):
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
    
    def load_opf(self, epub_file):
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
        douban_meta = requests_douban_meta(meta)
        if 'cover' in meta and meta['cover'] in self.manifest_map:
            cover_name = self.manifest_map[meta['cover']]
            cover_path = zip_join(self.opf_dir, cover_name)
            if '/' in cover_name:
                cover_name = cover_name[cover_name.rindex('/') + 1:]
            cover_name = cover_name.lower()
            copy_zip_file(epub_file, cover_path, os.path.join(self.dist, self.image_dir, cover_name))
            # epub_file.extract(cover_path, os.path.join(self.dist, self.image_dir))
            douban_meta['cover'] = os.path.join(self.image_dir, cover_name).replace('\\', '/')
        if len(self.css_list) > 0:
            douban_meta['page_style'] = self.css_list
        douban_meta['type'] = 'epub'
        douban_meta['container'] = self.container_file
        douban_meta['toc'] = self.toc_file
        save_json(self.meta_dist_path, douban_meta)

    
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
            href_id = href_arr[1] if len(href_arr) > 1 else None
            if href_name not in self.tcontainer:
                href_path = zip_join(self.opf_dir, href_name)
                href_dir = self.get_zip_file_dir(href_path)
                try:
                    self.copy_html(epub_file, href_path, href_dir, self.container_count)
                    self.page_map[href_path] = self.container_count
                    self.container_count += 1
                except KeyError:
                    print('miss: %s not in zip' % href_path)

    def split_container(self, epub_file):
        """
        切割内容
        """
        self.container_count = 1
        for container in self.tcontainer:
            zip_path = zip_join(self.opf_dir, container)
            container_dir = None
            if '/' in zip_path:
                container_dir = zip_path[:zip_path.rindex('/')]
            info = epub_file.getinfo(zip_path)
            if info.file_size > self.split_size:
                split_count = int(info.file_size / self.split_size)
                if info.file_size % self.split_size:
                    split_count += 1
                # with epub_file.open(zip_path) as html_file:
                self.page_map[zip_path] = set(range(
                    self.container_count,
                    self.container_count + split_count
                ))
                self.split_html(
                    epub_file,
                    zip_path,
                    container_dir,
                    split_count,
                    self.container_count
                )
                self.container_count += split_count - 1
            else:
                # with epub_file.open(zip_path) as html_file:
                self.page_map[zip_path] = self.container_count
                self.copy_html(epub_file, zip_path, container_dir, self.container_count)
            self.container_count += 1

    def copy_html(self, epub_file, zip_path, container_dir, container_count):
        """
        不分割拷贝
        """
        with epub_file.open(zip_path) as html_file:
            tree = etree.parse(html_file)
            self.find_head_css(epub_file, tree, container_dir)
            body = tree.find('//xmlns:body', namespaces={'xmlns': NAMESPACES['XHTML']})
            nsmap = body.nsmap
            page_xml = etree.Element('div', nsmap=nsmap)
            for child in body.iterchildren():
                page_xml.append(child)
            self.save_html(page_xml, container_count)

    def split_html(self, epub_file, zip_path, container_dir, split_count, container_count):
        """
        切割html
        """
        with epub_file.open(zip_path) as html_file:
            tree = etree.parse(html_file)
            self.find_head_css(epub_file, tree, container_dir)
            body = tree.find('//xmlns:body', namespaces={'xmlns': NAMESPACES['XHTML']})
            children = body.getchildren()
            children_len = len(children)
            if children_len < split_count:
                self.copy_html(epub_file, html_file, container_dir, container_count)
                self.container_count -= split_count - 1
            split_num = int(children_len / split_count)
            page_count = 0
            page_xml = None
            nsmap = body.nsmap
            for index, child in enumerate(children):
                if index % split_num == 0 and page_count < split_count - 1:
                    if page_xml is not None:
                        self.save_html(page_xml, container_count + page_count)
                        page_count += 1
                    page_xml = etree.Element('div', nsmap=nsmap)
                page_xml.append(child)
            if page_xml is not None:
                self.save_html(page_xml, container_count + page_count)

    def save_html(self, xml, container_count):
        """
        保存并处理
        """
        page_name = '%s%d.html' % (self.page_join, container_count)
        links = xml.xpath('//@id', namespaces={'xmlns': NAMESPACES['XHTML']})
        page_path = zip_join(self.page_dir, page_name)
        self.container.append((page_path, container_count))
        link_set = set()
        for link in links:
            link_set.add(link)
        # if len(link_set) > 0:
        self.toc_link[container_count] = link_set
        return etree.ElementTree(xml).write(
            os.path.join(self.dist, self.page_dir, page_name),
            pretty_print=True,
            encoding='utf-8',
            method='html'
        )


    def find_head_css(self, epub_file, tree, container_dir):
        """
        处理内容页head上的css
        """
        links = tree.findall('//xmlns:link[@href]', namespaces={'xmlns': NAMESPACES['XHTML']})
        for link in links:
            css_name = link.get('href')
            if container_dir:
                css_zip_path = zip_join(container_dir, css_name)
            else:
                css_zip_path = css_name
            if css_zip_path not in self.css_set:
                self.css_set.add(css_zip_path)
                if '/' in css_name:
                    css_name = css_name[css_name.rindex('/') + 1: ].lower()
                css_out_name = zip_join(self.css_dir, css_name)
                copy_zip_file(epub_file, css_zip_path, os.path.join(self.dist, css_out_name))
                self.css_list.append(css_out_name)

    def handle_page(self, epub_file):
        """
        处理page中的锚点
        """
        # print(self.container)
        for page_name, index in self.container:
            old_page_name = self.get_old_page_name(index)
            old_page_dir = self.get_zip_file_dir(old_page_name)
            now_page_path = os.path.join(self.dist, page_name)
            print(now_page_path)
            with file_open(
                now_page_path,
                'r',
                encoding='utf8'
            ) as page_file:
                tree = etree.parse(page_file)
                links = tree.findall('//xmlns:a[@href]', namespaces={'xmlns': NAMESPACES['XHTML']})
                for link in links:
                    href = link.get('href')
                    http_head = HTTP_NAME.findall(href)
                    if len(http_head) > 0:
                        continue
                    link_arr = href.split('#')
                    # print(link_arr)
                    link_page = link_arr[0]
                    link_id = link_arr[1] if len(link_page) > 1 else None
                    # link_args = None
                    if link_id and '?' in link_id:
                        tmp = link_id.split('?')
                        link_id = tmp[0]
                        # link_args = tmp[1]
                    link_page_name = zip_join(old_page_dir, link_page)
                    if link_page_name in self.page_map:
                        now_page = self.page_map[link_page_name]
                        if isinstance(now_page, int):
                            new_href = '%s%d.html#%s' % (
                                self.page_join,
                                now_page,
                                link_id if link_id else ''
                            )
                            link.set('href', new_href)
                        else:
                            for page_num in now_page:
                                if not link_id or (
                                    page_num in self.toc_link and
                                    link_id in self.toc_link[page_num]
                                ):
                                    new_href = '%s%d.html#%s' % (
                                        self.page_join,
                                        page_num,
                                        link_id if link_id else ''
                                    )
                                    link.set('href', new_href)
                images = tree.findall(
                    '//xmlns:img[@src]',
                    namespaces={
                        'xmlns': NAMESPACES['XHTML']
                    }
                )
                for img in images:
                    img_src = img.get('src')
                    img_zip_path = zip_join(old_page_dir, img_src)
                    if '/' in img_src:
                        img_out_name = zip_join(
                            self.image_dir,
                            img_src[img_src.rindex('/') + 1:]
                        )
                    else:
                        img_out_name = zip_join(self.image_dir, img_src)
                    copy_zip_file(
                        epub_file,
                        img_zip_path,
                        os.path.join(self.dist, img_out_name)
                    )
                    del img.attrib['src']
                    # print(dir(img))
                    img.set('data-src', img_out_name)
                images = tree.findall(
                    '//xmlns:image[@xlink:href]',
                    namespaces={
                        'xmlns': NAMESPACES['SVG'],
                        'xlink': NAMESPACES['SVGLINK']
                    }
                )
                img_len = len(images)
                if img_len > 0:
                    for img in images:
                        name_spaces = '{%s}href' % NAMESPACES['SVGLINK']
                        img_src = img.get(name_spaces)
                        # print(img_src, name_spaces)
                        img_zip_path = zip_join(old_page_dir, img_src)
                        if '/' in img_src:
                            img_out_name = zip_join(self.image_dir, img_src[img_src.rindex('/') + 1:])
                        else:
                            img_out_name = zip_join(self.image_dir, img_src)
                        copy_zip_file(epub_file, img_zip_path, os.path.join(self.dist, img_out_name))
                        del img.attrib[name_spaces]
                        # print(dir(img))
                        img.set('data-src', img_out_name)
                tree.write(
                    now_page_path,
                    pretty_print=True,
                    encoding='utf-8',
                    method='html'
                )
                    # print(href, link.get('href'))
                    # print(link_page_name)
                    
                    


    def get_zip_file_dir(self, file_name):
        """
        获取文件的目录
        """
        if '/' in file_name:
            return file_name[:file_name.rindex('/')]
        else:
            return ''
    
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

if __name__ == '__main__':
    pass
