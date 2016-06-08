===================
Flake8 Tidy Imports
===================

.. image:: https://img.shields.io/pypi/v/flake8-tidy-imports.svg
        :target: https://pypi.python.org/pypi/flake8-tidy-imports

.. image:: https://img.shields.io/travis/adamchainz/flake8-tidy-imports.svg
        :target: https://travis-ci.org/adamchainz/flake8-tidy-imports

A `flake8 <https://flake8.readthedocs.io/en/latest/index.html>`_ plugin that
helps you write tidier imports.

* Free software: ISC license

Installation
------------

Install from ``pip`` with:

.. code-block:: sh

     pip install flake8-tidy-imports

It will then automatically be run as part of ``flake8``; you can check it has
been picked up with:

.. code-block:: sh

    $ flake8 --version
    2.4.1 (pep8: 1.7.0, pyflakes: 0.8.1, flake8-tidy-imports: 1.0.0, mccabe: 0.3.1) CPython 2.7.11 on Darwin


Rules
-----

Currently only one rule is implemented.

I200: Unnecessary import alias
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complains about unnecessary import aliasing of three forms:

* ``import foo as foo`` -> ``import foo``
* ``import foo.bar as bar`` -> ``from foo import bar``
* ``from foo import bar as bar`` -> ``from foo import bar``

The message includes the suggested rewrite (which may not be correct at
current), for example:

.. code-block:: sh

    $ flake8 file.py
    file.py:1:1: I200 Unnecessary import alias - rewrite as 'from foo import bar'.
