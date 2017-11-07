#!/bin/env python
# coding: utf-8
import argparse


class Epub2Json(object):
    def __init__(self, options):
        pass


def add_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f',
        '--file',
        type=str,
        help='pdf file'
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
    return parser.parse_args()


if __name__ == '__main__':
    args = add_args()
    epub = Epub2Json(args)
    epub.run()
