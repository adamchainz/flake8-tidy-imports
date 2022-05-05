from __future__ import annotations

import re
import sys
from textwrap import dedent
from unittest.mock import Mock

import pytest

if sys.version_info >= (3, 8):
    from importlib.metadata import version
else:
    from importlib_metadata import version

from src.flake8_tidy_imports import ImportChecker

default_setup_cfg = """\
[flake8]
select = I2
"""


@pytest.fixture
def flake8_path(flake8_path):
    (flake8_path / "setup.cfg").write_text(default_setup_cfg)
    yield flake8_path


def test_version(flake8_path):
    result = flake8_path.run_flake8(["--version"])
    version_regex = r"flake8-tidy-imports:( )*" + version("flake8-tidy-imports")
    unwrapped = "".join(result.out_lines)
    assert re.search(version_regex, unwrapped)


# I250


def test_I250_pass_1(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import foo

            foo
            """
        )
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == []


def test_I250_pass_2(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import foo as foo2

            foo2
            """
        )
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == []


def test_I250_pass_3(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import os.path as path2

            path2
            """
        )
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == []


def test_I250_fail_1(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import foo.bar as bar

            bar
            """
        )
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == [
        (
            "./example.py:1:1: I250 Unnecessary import alias - rewrite as "
            + "'from foo import bar'."
        )
    ]


def test_I250_fail_2(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import foo as foo

            foo
            """
        )
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == [
        "./example.py:1:1: I250 Unnecessary import alias - rewrite as 'import foo'."
    ]


def test_I250_fail_3(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import foo as foo, bar as bar

            foo
            bar
            """
        )
    )
    result = flake8_path.run_flake8()
    assert set(result.out_lines) == {
        "./example.py:1:1: I250 Unnecessary import alias - rewrite as 'import foo'.",
        "./example.py:1:1: I250 Unnecessary import alias - rewrite as 'import bar'.",
    }


def test_I250_from_success_1(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from foo import bar as bar2

            bar2
            """
        )
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == []


def test_I250_from_fail_1(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from foo import bar as bar

            bar
            """
        )
    )
    result = flake8_path.run_flake8()

    assert result.out_lines == [
        (
            "./example.py:1:1: I250 Unnecessary import alias - rewrite as "
            + "'from foo import bar'."
        )
    ]


def test_I250_from_fail_2(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from foo import bar as bar, baz as baz

            bar
            baz
            """
        )
    )
    result = flake8_path.run_flake8()
    assert set(result.out_lines) == {
        (
            "./example.py:1:1: I250 Unnecessary import alias - rewrite as "
            + "'from foo import bar'."
        ),
        (
            "./example.py:1:1: I250 Unnecessary import alias - rewrite as "
            + "'from foo import baz'."
        ),
    }


# I251


def test_I251_import_mock(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import mock

            mock
            """
        )
    )
    result = flake8_path.run_flake8(
        extra_args=["--banned-modules", "mock = use unittest.mock instead"]
    )
    assert result.out_lines == [
        "./example.py:1:1: I251 Banned import 'mock' used - use unittest.mock instead."
    ]


def test_I251_import_mock_config(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import mock

            mock
            """
        )
    )
    (flake8_path / "setup.cfg").write_text(
        default_setup_cfg + "banned-modules = mock = use unittest.mock instead"
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == [
        "./example.py:1:1: I251 Banned import 'mock' used - use unittest.mock instead."
    ]


def test_I251_most_specific_imports(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import foo
            import foo.bar
            from foo import bar

            [foo, foo.bar, bar]
            """
        )
    )
    (flake8_path / "setup.cfg").write_text(
        default_setup_cfg
        + dedent(
            """\
            banned-modules = foo = use foo_prime instead
                             foo.bar = use foo_prime.bar_rename instead
            """
        )
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == [
        "./example.py:1:1: I251 Banned import 'foo' used - use foo_prime instead.",
        (
            "./example.py:2:1: I251 Banned import 'foo.bar' used - use "
            + "foo_prime.bar_rename instead."
        ),
        (
            "./example.py:3:1: I251 Banned import 'foo.bar' used - use "
            + "foo_prime.bar_rename instead."
        ),
    ]


def test_I251_relative_import(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from . import foo

            foo
            """
        )
    )
    (flake8_path / "setup.cfg").write_text(
        default_setup_cfg + "banned-modules = bar = use bar_prime instead"
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == []


def test_I251_relative_import_2(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from .. import bar

            bar
            """
        )
    )
    (flake8_path / "setup.cfg").write_text(
        default_setup_cfg + "banned-modules = bar = use bar_prime instead"
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == []


def test_I251_import_mock_and_others(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import ast, mock


            ast + mock
            """
        )
    )
    result = flake8_path.run_flake8(
        extra_args=["--banned-modules", "mock = use unittest.mock instead"]
    )
    assert set(result.out_lines) == {
        "./example.py:1:1: I251 Banned import 'mock' used - use unittest.mock instead.",
    }


def test_I251_import_mock_and_others_all_banned(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import ast, mock


            ast + mock
            """
        )
    )
    result = flake8_path.run_flake8(
        extra_args=["--banned-modules", "mock = foo\nast = bar"]
    )
    assert set(result.out_lines) == {
        "./example.py:1:1: I251 Banned import 'mock' used - foo.",
        "./example.py:1:1: I251 Banned import 'ast' used - bar.",
    }


def test_I251_from_mock_import(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from mock import Mock

            Mock
            """
        )
    )
    result = flake8_path.run_flake8(
        extra_args=["--banned-modules", "mock = use unittest.mock instead"]
    )
    assert result.out_lines == [
        "./example.py:1:1: I251 Banned import 'mock' used - use unittest.mock instead."
    ]


def test_I251_from_unittest_import_mock(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from unittest import mock

            mock
            """
        )
    )
    result = flake8_path.run_flake8(
        extra_args=["--banned-modules", "unittest.mock = actually use mock"]
    )
    assert result.out_lines == [
        "./example.py:1:1: I251 Banned import 'unittest.mock' used - actually use mock."
    ]


def test_I251_from_unittest_import_mock_as(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from unittest import mock as mack

            mack
            """
        )
    )
    result = flake8_path.run_flake8(
        extra_args=["--banned-modules", "unittest.mock = actually use mock"]
    )
    assert result.out_lines == [
        "./example.py:1:1: I251 Banned import 'unittest.mock' used - actually use mock."
    ]


def test_I251_from_unittest_import_wildcard(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from foo.bar import Bar

            Bar
            """
        )
    )
    result = flake8_path.run_flake8(
        extra_args=["--banned-modules", "foo.* = foo is banned"]
    )
    assert result.out_lines == [
        "./example.py:1:1: I251 Banned import 'foo.bar.Bar' used - foo is banned."
    ]


def test_I251_import_import_wildcard(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import mock

            mock
            """
        )
    )
    result = flake8_path.run_flake8(
        extra_args=["--banned-modules", "mock.* = use unittest.mock instead"]
    )
    assert result.out_lines == [
        "./example.py:1:1: I251 Banned import 'mock' used - use unittest.mock instead."
    ]


def test_I251_from_unittest_import_wildcard_specific(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import foo
            import foo.bar
            from foo import bar

            [foo, foo.bar, bar]
            """
        )
    )
    (flake8_path / "setup.cfg").write_text(
        default_setup_cfg
        + dedent(
            """\
            banned-modules = foo.* = use foo_prime instead
                             foo.bar = use foo_prime.bar_rename instead
            """
        )
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == [
        "./example.py:1:1: I251 Banned import 'foo' used - use foo_prime instead.",
        (
            "./example.py:2:1: I251 Banned import 'foo.bar' used - use "
            + "foo_prime.bar_rename instead."
        ),
        (
            "./example.py:3:1: I251 Banned import 'foo.bar' used - use "
            + "foo_prime.bar_rename instead."
        ),
    ]


def test_I251_from_unittest_import_wildcard_no_match(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from foo.bar import Bar

            Bar
            """
        )
    )
    result = flake8_path.run_flake8(
        extra_args=["--banned-modules", "foo.baz.* = foo.baz is banned"]
    )
    assert result.out_lines == []


def test_I251_from_unittest_import_wildcard_multiple_matches(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import foo.baz
            import foo.bar.bat

            [foo.baz, foo.bar.bat]
            """
        )
    )
    (flake8_path / "setup.cfg").write_text(
        default_setup_cfg
        + dedent(
            """\
            banned-modules = foo.* = general
                             foo.bar.* = specific
            """
        )
    )
    result = flake8_path.run_flake8()
    # foo.* matches both, but we prefer the longer matching pattern
    assert result.out_lines == [
        "./example.py:1:1: I251 Banned import 'foo.baz' used - general.",
        "./example.py:2:1: I251 Banned import 'foo.bar.bat' used - specific.",
    ]


@pytest.mark.parametrize(
    "module, expected_message",
    (
        ("foo", "concrete"),
        ("foo.bar", "structured specific"),
        ("foo.bar.bat", "structured specific"),
        ("foo.bat", "structured general"),
        ("foo.baz", "unstructured first"),
        ("foo.bar.bat.baz", "unstructured first"),
        ("foo.quux.baz", "unstructured first"),
    ),
)
def test_I251_wildcard_precedence(flake8_path, module, expected_message):
    """
    Check that if there are multiple possible rules matching, they are matched
    in the expected order.
    """
    (flake8_path / "example.py").write_text(
        dedent(
            f"""\
            import {module}
            [{module}]
            """
        )
    )
    (flake8_path / "setup.cfg").write_text(
        default_setup_cfg
        + dedent(
            """\
            banned-modules = foo = concrete
                             foo.* = structured general
                             foo.bar.* = structured specific
                             foo.*.baz = unstructured first
                             foo.*.quux.baz = unstructured second
            """
        )
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == [
        f"./example.py:1:1: I251 Banned import '{module}' used - {expected_message}.",
    ]


@pytest.mark.parametrize(
    "banned_module, imported_module, expected",
    (
        # Concrete matches
        ("foo", "foo", True),
        ("foo", "foo.bar", False),
        # Structured matches
        ("foo.bar.*", "foo.bar", True),
        ("foo.bar.*", "foo.bar.baz", True),
        ("foo.bar.*", "foo.bar.baz.quux", True),
        ("foo.*", "foobar", False),
        ("foo.*", "f", False),
        ("foo.bar.*", "foo.bark.baz", False),
        # Unstructured matches
        ("site.*.migrations", "site.migrations", True),
        ("site.*.migrations", "site.app.migrations", True),
        ("site.*.migrations", "site.app.production.migrations", True),
        ("site.*.migrations", "site.app", False),
        ("site.*.migrations", "site.migrations.foo", False),
        ("site.*.migrations.*", "site.migrations.foo", True),
        ("site.*.migrations.*", "site.app.migrations.foo", True),
        ("site.*.migrations.*", "site.app.production.migrations.foo", True),
        ("site.*.migrations.*", "site.app", False),
        ("foo.*.bar.*.baz", "foo.bar.baz", True),
        ("foo.*.bar.*.baz", "foo.quux.bar.baz", True),
        ("foo.*.bar.*.baz", "foo.quux.bar.qiix.baz", True),
        ("foo.*.bar.*.baz", "foo.baz.bar", False),
        ("*", "foo", True),
        ("*.foo", "foo", False),
        ("*.foo", "bar.foo", True),
        ("*.foo", "bar.bazfoo", False),
    ),
)
def test_I251_is_module_banned(banned_module, imported_module, expected):
    # Set up a simple banned-modules string
    banned_modules_str = f"{banned_module} = ERROR: {banned_module}"

    # Set up an ImportChecker and pass the options in
    checker = ImportChecker(Mock())
    options = Mock()
    options.banned_modules = banned_modules_str
    options.ban_relative_imports = False

    # Make sure we get the expected result on the module we're trying to import
    checker.parse_options(options)
    is_banned, _ = checker._is_module_banned(imported_module)
    assert is_banned is expected


def test_I251_python2to3_import_md5(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            import md5

            md5
            """
        )
    )
    result = flake8_path.run_flake8(extra_args=["--banned-modules", "{python2to3}"])
    assert result.out_lines == [
        "./example.py:1:1: I251 Banned import 'md5' used - removed in Python "
        + "3, use hashlib.md5() instead."
    ]


# I252


def test_I252_not_activated(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from . import foo

            foo
            """
        )
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == []


def test_I252_relative_import(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from . import foo

            foo
            """
        )
    )
    (flake8_path / "setup.cfg").write_text(
        default_setup_cfg + "ban-relative-imports = true"
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == ["./example.py:1:1: I252 Relative imports are banned."]


def test_I252_relative_import_2(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from .. import bar

            bar
            """
        )
    )
    (flake8_path / "setup.cfg").write_text(
        default_setup_cfg + "ban-relative-imports = true"
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == ["./example.py:1:1: I252 Relative imports are banned."]


def test_I252_relative_import_3(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from .foo import bar

            bar
            """
        )
    )
    (flake8_path / "setup.cfg").write_text(
        default_setup_cfg + "ban-relative-imports = true"
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == ["./example.py:1:1: I252 Relative imports are banned."]


def test_I252_relative_import_commandline(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from . import foo

            foo
            """
        )
    )
    result = flake8_path.run_flake8(["--ban-relative-imports"])
    assert result.out_lines == ["./example.py:1:1: I252 Relative imports are banned."]


def test_I252_relative_import_parents1(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from . import foo

            foo
            """
        )
    )
    (flake8_path / "setup.cfg").write_text(
        default_setup_cfg + "ban-relative-imports = parents"
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == []


def test_I252_relative_import_parents2(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from .foo import bar

            bar
            """
        )
    )
    (flake8_path / "setup.cfg").write_text(
        default_setup_cfg + "ban-relative-imports = parents"
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == []


def test_I252_relative_import_parents3(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from .. import foo

            foo
            """
        )
    )
    (flake8_path / "setup.cfg").write_text(
        default_setup_cfg + "ban-relative-imports = parents"
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == [
        "./example.py:1:1: I252 Relative imports from parent modules are banned."
    ]


def test_I252_relative_import_parents4(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from ...foo import bar

            bar
            """
        )
    )
    (flake8_path / "setup.cfg").write_text(
        default_setup_cfg + "ban-relative-imports = parents"
    )
    result = flake8_path.run_flake8()
    assert result.out_lines == [
        "./example.py:1:1: I252 Relative imports from parent modules are banned."
    ]


def test_I252_relative_import_parents_commandline(flake8_path):
    (flake8_path / "example.py").write_text(
        dedent(
            """\
            from ... import bar

            bar
            """
        )
    )
    result = flake8_path.run_flake8(["--ban-relative-imports=parents"])
    assert result.out_lines == [
        "./example.py:1:1: I252 Relative imports from parent modules are banned."
    ]
