# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from pathlib import Path

import six
from flake8.main import main as flake8_main

MODULE_DIR = Path(__file__).parent.resolve()
DATA_DIR = MODULE_DIR / 'data'


def run_flake8(*args):
    try:
        orig_args = sys.argv
        sys.argv = ['flake8', '--jobs', '1'] + [six.text_type(a) for a in args]
        return flake8_main()
    finally:
        sys.argv = orig_args


def test_fail_a():
    run_flake8(DATA_DIR / 'fail_a.py')
