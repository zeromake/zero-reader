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
    zip_join
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
        self.file_name = options['file']
        self.sha = file_sha256(self.file_name)
        self.dist = os.path.join(options['dist'], self.sha)
        self.meta_dist_path = os.path.join(self.dist, 'meta.json')
        self.image_dir = 'img'
        self.page_dir = 'page'
        self.css_dir = 'css'
        self.page_join = 'page-'

        self.split_size = 100 * 1024
        self.opf_file = None
        self.opf_dir = None
        self.manifest_map = None
        self.manifests = None
        self.tcontainer = []
        self.container = []
        self.toc_zip_path = None
        self.css_set = set()
        self.toc_link = {}

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
        # print(self.toc_link)
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

    def split_container(self, epub_file):
        """
        切割内容
        """

        container_count = 1
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
                self.split_html(epub_file, zip_path, container_dir, split_count, container_count)
                container_count += split_count
            else:
                # with epub_file.open(zip_path) as html_file:
                self.copy_html(epub_file, zip_path, container_dir, container_count)
            container_count += 1

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
            page_name = '%s%d.html' % (self.page_join, container_count)
            self.save_html(page_xml, page_name)

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
                return self.copy_html(epub_file, html_file, container_dir, container_count)
            split_num = int(children_len / split_count)
            page_count = 0
            page_xml = None
            nsmap = body.nsmap
            for index, child in enumerate(children):
                if index % split_num == 0 and page_count < split_count - 1:
                    if page_xml is not None:
                        page_name = '%s%d.html' % (self.page_join, container_count + page_count)
                        self.save_html(page_xml, page_name)
                        page_count += 1
                    page_xml = etree.Element('div', nsmap=nsmap)
                page_xml.append(child)
            if page_xml is not None:
                page_name = '%s%d.html' % (self.page_join, container_count + page_count)
                self.save_html(page_xml, page_name)

    def save_html(self, xml, page_name):
        """
        保存并处理
        """
        links = xml.xpath('//@id', namespaces={'xmlns': NAMESPACES['XHTML']})
        page_path = zip_join(self.page_dir, page_name)
        link_set = set()
        for link in links:
            link_set.add(link)
        if len(link_set) > 0:
            self.toc_link[page_path] = link_set
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
            if css_name not in self.css_set:
                self.css_set.add(css_name)
                if container_dir:
                    css_zip_path = zip_join(container_dir, css_name)
                else:
                    css_zip_path = css_name
                if '/' in css_name:
                    css_name = css_name[css_name.rindex('/') + 1: ].lower()
                copy_zip_file(epub_file, css_zip_path, os.path.join(self.dist, self.css_dir, css_name))

if __name__ == '__main__':
    pass
