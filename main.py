#!/bin/env python
# coding: utf-8

"""
命令行
"""
import os
import argparse
import asyncio
import logging

def add_args():
    """
    处理命令行参数
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-w',
        '--web',
        type=int,
        help='run web',
        default=0
    )
    parser.add_argument(
        '-p',
        '--png',
        type=int,
        help='png is compress',
        default=0
    )
    parser.add_argument(
        '-c',
        '--compress',
        type=int,
        help='book out dir is tar.zstd',
        default=0
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
        default="librarys"
    )
    parser.add_argument(
        '-m',
        '--meta',
        type=str,
        help='meta filename',
        default=""
    )
    return parser.parse_args()

def main():
    """
    主函数
    """
    logging.basicConfig(level=logging.ERROR)
    args = add_args()
    raw_options = args.__dict__
    options = {
        'toc': "toc.html",
        'share': "bin/data",
        'join': "pages",
        'page': "page-.html"
    }
    for key, value in raw_options.items():
        if isinstance(value, str):
            value = value.encode("utf-8", 'surrogateescape').decode('utf-8')
        options[key] = value
    file_name = options['file']
    options['css'] = 'style.css'
    options['compress'] = bool(options['compress'])
    if file_name is None:
        options['web'] = 1
    loop = asyncio.get_event_loop()
    if options['web'] == 1:
        from web_app import app
        app.run(host="0.0.0.0", workers=1, access_log=False, debug=False)
    else:
        from converts.utils import logger
        from converts.epub2json import Epub2Json
        from converts.pdf2json import Pdf2Json

        if not os.path.exists(options['dist']):
            os.makedirs(options['dist'])
        convert = None
        if file_name.endswith('.epub'):
            convert = Epub2Json
        elif file_name.endswith('.pdf'):
            convert = Pdf2Json
        if convert is None:
            logger.error('only support book on epub, pdf!')
        else:
            converts = convert(options, loop)
            loop.run_until_complete(converts.run())
            logger.debug("meta: %s", converts.meta_data)

if __name__ == '__main__':
    main()
