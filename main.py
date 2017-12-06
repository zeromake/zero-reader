#!/bin/env python
# coding: utf-8

"""
命令行
"""
import os
import argparse

from converts.pdf2json import Pdf2Json
from converts.epub2json import Epub2Json
from converts.utils import logger

def add_args():
    """
    处理命令行参数
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        '--compress',
        type=int,
        help='book out dir is tar.zstd',
        default=1
    )
    parser.add_argument(
        '-f',
        '--file',
        type=str,
        help='book file'
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
    file_name = options['file']
    options['css'] = 'style.css'
    options['compress'] = bool(options['compress'])

    if not os.path.exists(options['dist']):
        os.makedirs(options['dist'])

    if file_name.endswith('.epub'):
        epub_converts = Epub2Json(options)
        epub_converts.run()
        # print('dont converts epub')
    elif file_name.endswith('.pdf'):
        pdf_converts = Pdf2Json(options)
        pdf_converts.run()
    else:
        logger.error('only support book on epub, pdf!')
