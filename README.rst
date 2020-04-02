===================
flake8-tidy-imports
===================

.. image:: https://img.shields.io/pypi/v/flake8-tidy-imports.svg
        :target: https://pypi.python.org/pypi/flake8-tidy-imports

.. image:: https://github.com/adamchainz/flake8-tidy-imports/workflows/CI/badge.svg?branch=master
        :target: https://github.com/adamchainz/flake8-tidy-imports/actions?workflow=CI

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/python/black

A `flake8 <https://flake8.readthedocs.io/en/latest/index.html>`_ plugin that
helps you write tidier imports.

Installation
------------

Install from ``pip`` with:

.. code-block:: sh

     python -m pip install flake8-tidy-imports

Python 3.5 to 3.8 supported.

When installed it will automatically be run as part of ``flake8``; you can
check it is being picked up with:

.. code-block:: sh

    $ flake8 --version
    3.7.9 (flake8-tidy-imports: 3.1.0, mccabe: 0.6.1, pycodestyle: 2.5.0, pyflakes: 2.1.1) CPython 3.8.0 on Darwin

Options
-------

``banned-modules``
~~~~~~~~~~~~~~~~~~

Config for rule I251 (see below). A map where each line is a banned import
string, followed by '=', then the message to use when encountering that banned
import. Note that despite the name, you can ban imported objects too, since the
syntax is the same, such as ``decimal.Decimal``.

There is also a special directive to ban a preselected list of removed/moved
modules between Python 2 and Python 3, recommending replacements, from `six
<https://pythonhosted.org/six/>`_ where possible. It can be turned on by adding
``{python2to3}`` to the list of ``banned-modules``.

Whilst the option can be passed on the commandline, it's much easier to
configure it in your config file, such as ``setup.cfg``, for example:

.. code-block:: ini

    [flake8]
    banned-modules = mock = use unittest.mock!
                     urlparse = use six.moves.urllib.parse!
                     {python2to3}

``ban-relative-imports``
~~~~~~~~~~~~~~~~~~~~~~~~

Enables rule I252, which bans relative imports. See below.

.. code-block:: ini

    [flake8]
    ban-relative-imports = true


Rules
-----

**N.B.** Before version 4.0.0, the rule codes were numbered 50 less, e.g. I250
was I200. They were changed in `Issue #106
<https://github.com/adamchainz/flake8-tidy-imports/issues/106>`__ due to
conflict with ``flake8-import-order``.

I250: Unnecessary import alias
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complains about unnecessary import aliasing of three forms:

* ``import foo as foo`` -> ``import foo``
* ``import foo.bar as bar`` -> ``from foo import bar``
* ``from foo import bar as bar`` -> ``from foo import bar``

The message includes the suggested rewrite (which may not be correct at
current), for example:

.. code-block:: sh

    $ flake8 file.py
    file.py:1:1: I250 Unnecessary import alias - rewrite as 'from foo import bar'.

I251: Banned import 'foo' used
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complains about importing of banned imports. This might be useful when
refactoring code, for example when moving from Python 2 to 3. By default there
are no imports banned - you should configure them with ``banned-modules`` as
described above in 'Options'.

The message includes a user-defined part that comes from the configuration. For
example:

.. code-block:: sh

    $ flake8 file.py
    file.py:1:1: I251 Banned import 'mock' used - use unittest.mock instead.

I252: Relative imports are banned.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complains about use of relative imports:

* ``from . import foo``
* ``from .bar import foo``

Needs enabling with ``ban-relative-imports`` configuration option.

See also
--------

For more advanced control of imports in your project, try
`import-linter <https://pypi.org/project/import-linter/>`__.
