===========================
Flake8 Tautological Imports
===========================

.. image:: https://img.shields.io/pypi/v/flake8_tautological_imports.svg
        :target: https://pypi.python.org/pypi/flake8_tautological_imports

.. image:: https://img.shields.io/travis/adamchainz/flake8_tautological_imports.svg
        :target: https://travis-ci.org/adamchainz/flake8_tautological_imports

.. image:: https://readthedocs.org/projects/flake8_tautological_imports/badge/?version=latest
        :target: https://readthedocs.org/projects/flake8_tautological_imports/?badge=latest
        :alt: Documentation Status


A Flake8 plugin that tells you not to write ``import foo.bar as bar``, but just
``from foo import bar``.

* Free software: ISC license
* Documentation: https://flake8_tautological_imports.readthedocs.org.

Installation
------------

Install from ``pip`` with:

.. code-block:: sh

     pip install flake8-tautological-imports

It will automatically be run as part of ``flake8``.

It outputs one warning code...
