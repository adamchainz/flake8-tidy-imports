# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import shutil
import sys
from pathlib import Path
from tempfile import mkdtemp
from textwrap import dedent

from flake8.main import main as flake8_main

from .utils import captured_stdout

MODULE_DIR = Path(__file__).parent.resolve()
TMP_DIR = None


def setup_module(module):
    global TMP_DIR
    TMP_DIR = Path(mkdtemp())


def teardown_module(module):
    shutil.rmtree(str(TMP_DIR))


def run_flake8(file_contents, extra_args=None):
    with open(str(TMP_DIR / "example.py"), 'w') as tempf:
        tempf.write(dedent(file_contents).strip() + '\n')

    orig_dir = os.getcwd()
    os.chdir(str(TMP_DIR))
    orig_args = sys.argv
    try:
        # Can't pass args to flake8 but can set to sys.argv
        sys.argv = [
            'flake8',
            '--jobs', '1',
            '--exit-zero',
            'example.py',
        ]
        if extra_args:
            sys.argv.extend(extra_args)

        # Run it
        with captured_stdout() as stdout:
            flake8_main()
        out = stdout.getvalue().strip()
        lines = out.split('\n')
        if lines[-1] == '':
            lines = lines[:-1]
        return lines
    finally:
        sys.argv = orig_args
        os.chdir(orig_dir)


# I200


def test_I200_pass_1():
    errors = run_flake8("""
        import foo

        foo
    """)
    assert errors == []


def test_I200_pass_2():
    errors = run_flake8("""
        import foo as foo2

        foo2
    """)
    assert errors == []


def test_I200_pass_3():
    errors = run_flake8("""
        import os.path as path2

        path2
    """)
    assert errors == []


def test_I200_fail_1():
    errors = run_flake8("""
        import foo.bar as bar

        bar
    """)
    assert errors == [
        "example.py:1:1: I200 Unnecessary import alias - rewrite as 'from foo import bar'.",
    ]


def test_I200_fail_2():
    errors = run_flake8("""
        import foo as foo

        foo
    """)
    assert errors == [
        "example.py:1:1: I200 Unnecessary import alias - rewrite as 'import foo'.",
    ]


def test_I200_fail_3():
    errors = run_flake8("""
        import foo as foo, bar as bar

        foo
        bar
    """)
    assert set(errors) == {
        "example.py:1:1: I200 Unnecessary import alias - rewrite as 'import foo'.",
        "example.py:1:1: I200 Unnecessary import alias - rewrite as 'import bar'.",
        "example.py:1:18: E401 multiple imports on one line",
    }


def test_I200_from_success_1():
    errors = run_flake8("""
        from foo import bar as bar2

        bar2
    """)
    assert errors == []


def test_I200_from_fail_1():
    errors = run_flake8("""
        from foo import bar as bar

        bar
    """)

    assert errors == [
        "example.py:1:1: I200 Unnecessary import alias - rewrite as 'from foo import bar'.",
    ]


def test_I200_from_fail_2():
    errors = run_flake8("""
        from foo import bar as bar, baz as baz

        bar
        baz
    """)
    assert set(errors) == {
        "example.py:1:1: I200 Unnecessary import alias - rewrite as 'from foo import bar'.",
        "example.py:1:1: I200 Unnecessary import alias - rewrite as 'from foo import baz'.",
    }


# I201


def test_I201_import_mock():
    errors = run_flake8(
        """
        import mock

        mock
        """,
        ['--banned-modules', 'mock = Use unittest.mock instead']
    )
    assert errors == [
        "example.py:1:1: I201 Banned module 'mock' imported - Use unittest.mock instead."
    ]


def test_I201_import_mock_and_others():
    errors = run_flake8(
        """
        import ast, mock


        ast + mock
        """,
        ['--banned-modules', 'mock = Use unittest.mock instead']
    )
    assert set(errors) == {
        'example.py:1:11: E401 multiple imports on one line',
        "example.py:1:1: I201 Banned module 'mock' imported - Use unittest.mock instead."
    }


def test_I201_import_mock_and_others_all_banned():
    errors = run_flake8(
        """
        import ast, mock


        ast + mock
        """,
        ['--banned-modules', 'mock = foo\nast = bar']
    )
    assert set(errors) == {
        'example.py:1:11: E401 multiple imports on one line',
        "example.py:1:1: I201 Banned module 'mock' imported - foo.",
        "example.py:1:1: I201 Banned module 'ast' imported - bar.",
    }


def test_I201_from_mock_import():
    errors = run_flake8(
        """
        from mock import Mock

        Mock
        """,
        ['--banned-modules', 'mock = Use unittest.mock instead']
    )
    assert errors == [
        "example.py:1:1: I201 Banned module 'mock' imported - Use unittest.mock instead."
    ]


def test_I201_from_unittest_import_mock():
    errors = run_flake8(
        """
        from unittest import mock

        mock
        """,
        ['--banned-modules', 'unittest.mock = Actually use mock']
    )
    assert errors == [
        "example.py:1:1: I201 Banned module 'unittest.mock' imported - Actually use mock."
    ]


def test_I201_from_unittest_import_mock_as():
    errors = run_flake8(
        """
        from unittest import mock as mack

        mack
        """,
        ['--banned-modules', 'unittest.mock = Actually use mock']
    )
    assert errors == [
        "example.py:1:1: I201 Banned module 'unittest.mock' imported - Actually use mock."
    ]
