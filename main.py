#!/bin/env python
# coding: utf-8

"""
命令行
"""

from converts.pdf2json import Pdf2Json
from converts.epub2json import Epub2Json
import argparse

def add_args():
    """
    处理命令行参数
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e',
        '--epub',
        type=bool,
        help='is epub file',
        default=False
    )
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
    args = add_args()
    options = args.__dict__
    if options['epub']:
        epub_converts = Epub2Json(options)
        epub_converts.run()
        # print('dont converts epub')
    else:
        pdf_converts = Pdf2Json(options)
        pdf_converts.run()
