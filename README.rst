===================
flake8-tidy-imports
===================

.. image:: https://img.shields.io/github/workflow/status/adamchainz/flake8-tidy-imports/CI/main?style=for-the-badge
   :target: https://github.com/adamchainz/flake8-tidy-imports/actions?workflow=CI

.. image:: https://img.shields.io/pypi/v/flake8-tidy-imports.svg?style=for-the-badge
   :target: https://pypi.org/project/flake8-tidy-imports/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
   :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=for-the-badge
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

A `flake8 <https://flake8.readthedocs.io/en/latest/index.html>`_ plugin that helps you write tidier imports.

Requirements
============

Python 3.6 to 3.10 supported.

Installation
============

First, install with ``pip``:

.. code-block:: sh

     python -m pip install flake8-tidy-imports

Second, check that ``flake8`` lists the plugin in its version line:

.. code-block:: sh

    $ flake8 --version
    3.7.9 (flake8-tidy-imports: 3.1.0, mccabe: 0.6.1, pycodestyle: 2.5.0, pyflakes: 2.1.1) CPython 3.8.0 on Darwin

Third, add the ``I25`` prefix to your `select list <https://flake8.pycqa.org/en/latest/user/options.html#cmdoption-flake8-select>`__.
For example, if you have your configuration in ``setup.cfg``:

.. code-block:: ini

    [flake8]
    select = E,F,W,I25

----

**Linting a Django project?**
Check out my book `Speed Up Your Django Tests <https://gumroad.com/l/suydt>`__ which covers loads of best practices so you can write faster, more accurate tests.

----

Options
=======

``banned-modules``
------------------

Config for rule I251 (below).
Should contain a map where each line is a banned import string, followed by '=', then the message to use when encountering that import.

There is also a special directive to ban a preselected list of removed/moved modules between Python 2 and Python 3, recommending replacements from `six
<https://pythonhosted.org/six/>`_ where possible.
It can be turned on by adding ``{python2to3}`` to the list of ``banned-modules``.

For example in ``setup.cfg``:

.. code-block:: ini

    [flake8]
    banned-modules = mock = Use unittest.mock.
                     {python2to3}

Note that despite the name, you can ban imported objects too, since the syntax is the same.
For example:

.. code-block:: ini

    [flake8]
    banned-modules = decimal.Decimal = Use ints and floats only.

``ban-relative-imports``
------------------------

Controls rule I252 (below). Accepts two values:

* ``parents`` - bans imports from parent modules (and grandparents, etc.), i.e. with more than one ``.``.
* ``true`` - bans all relative imports.

For example:

.. code-block:: ini

    [flake8]
    ban-relative-imports = parents

(If you want to ban absolute imports, you can put your project's modules in ``banned-modules``.)

Rules
=====

**Note:** Before version 4.0.0, the rule codes were numbered 50 lower, e.g. I250 was I200.
They were changed in `Issue #106 <https://github.com/adamchainz/flake8-tidy-imports/issues/106>`__ due to conflict with ``flake8-import-order``.

I250: Unnecessary import alias
------------------------------

Complains about unnecessary import aliasing of three forms:

* ``import foo as foo`` -> ``import foo``
* ``import foo.bar as bar`` -> ``from foo import bar``
* ``from foo import bar as bar`` -> ``from foo import bar``

The message includes the suggested rewrite (which may not *always* be correct), for example:

.. code-block:: sh

    $ flake8 file.py
    file.py:1:1: I250 Unnecessary import alias - rewrite as 'from foo import bar'.

Such aliases can be automatically fixed by ``isort`` if you activate its `remove_redundant_aliases option <https://pycqa.github.io/isort/docs/configuration/options/#remove-redundant-aliases>`__.

I251: Banned import ``<import>`` used.
--------------------------------------

Complains about use of banned imports.
By default there are no imports banned - you should configure them with ``banned-modules`` as described above in 'Options'.

The message includes a user-defined part that comes from the configuration.
For example:

.. code-block:: sh

    $ flake8 file.py
    file.py:1:1: I251 Banned import 'mock' used - use unittest.mock instead.

I252: Relative imports <from parent modules> are banned.
--------------------------------------------------------

Complains about use of relative imports:

* ``from . import foo`` (sibling import)
* ``from .bar import foo`` (sibling import)
* ``from .. import foo`` (parent import)

Controlled by the ``ban-relative-imports`` configuration option.

Absolute imports, or relative imports from siblings, are recommended by `PEP8 <https://www.python.org/dev/peps/pep-0008/>`__:

    Absolute imports are recommended, as they are usually more readable and tend to be better behaved...

    .. code-block:: python

        import mypkg.sibling
        from mypkg import sibling
        from mypkg.sibling import example

    However, explicit relative imports are an acceptable alternative to absolute imports...

    .. code-block:: python

        from . import sibling
        from .sibling import example

See also
--------

For more advanced control of imports in your project, try `import-linter <https://pypi.org/project/import-linter/>`__.
