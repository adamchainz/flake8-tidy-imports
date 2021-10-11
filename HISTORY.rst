=======
History
=======

4.5.0 (2021-10-11)
------------------

* Support Flake8 4.

4.4.1 (2021-08-12)
------------------

* Correctly declare dependency on flake8 3.8.0+. This is required as flake8
  moved from optparse to argparse, and the change to ``ban-relative-imports``
  uses argparse features.

4.4.0 (2021-08-11)
------------------

* Add ``parents`` option for ``ban-relative-imports`` that allows using
  relative syntax to import from sibling modules, but not parents.

* Add type hints.

4.3.0 (2021-05-10)
------------------

* Support Python 3.10.

* Stop distributing tests to reduce package size. Tests are not intended to be
  run outside of the tox setup in the repository. Repackagers can use GitHub's
  tarballs per tag.

4.2.1 (2020-12-19)
------------------

* Improved installation instructions in README.

4.2.0 (2020-12-13)
------------------

* Drop Python 3.5 support.
* Support Python 3.9.
* Move license from ISC to MIT License.

4.1.0 (2020-03-25)
------------------

* Make ``{python2to3}`` ban ``functools.wraps`` in favour of ``six.wraps``.

4.0.1 (2020-03-24)
------------------

* Fix ``cStringIO`` message for ``{python2to3}`` built-in ``banned-modules``.
  Previously it looked for ``cStringIO.cStringIO`` which seems to never have
  existed.

4.0.0 (2020-01-04)
------------------

* Add 50 to all rule codes to avoid conflict with ``flake8-import-order``. This
  means rule ``I200`` is now ``I250``, etc.

  If you have configured `flake8's select or ignore options
  <http://flake8.pycqa.org/en/latest/user/violations.html>`__, you may need to
  update it to keep the ``flake8-tidy-imports`` rules active.

3.1.0 (2019-11-15)
------------------

* Support Python 3.8.
* Converted setuptools metadata to configuration file. This meant removing the
  ``__version__`` attribute from the package. If you want to inspect the
  installed version, use
  ``importlib.metadata.version("flake8-tidy-imports")``
  (`docs <https://docs.python.org/3.8/library/importlib.metadata.html#distribution-versions>`__ /
  `backport <https://pypi.org/project/importlib-metadata/>`__).
* Add dependency on ``importlib-metadata``.

3.0.0 (2019-10-15)
------------------

* Add rule ``I202`` to ban relative imports, when activated with the new
  ``ban-relative-imports`` configuration option.
* Update Python support to 3.5-3.7, as 3.4 has reached its end of life.
* Update Flake8 support to 3.0+ only. 3.0.0 was released in 2016 and the plugin
  hasn't been tested with it since.

2.0.0 (2019-02-02)
------------------

* Drop Python 2 support, only Python 3.4+ is supported now.

1.1.0 (2017-07-10)
------------------

* Added a big list of python 2 to 3 import bans for I201, which can be
  activated by adding ``{python2to3}`` to the ``banned-modules`` option.

1.0.6 (2017-03-07)
------------------

* Fixed the whitespace in the help message for ``--banned-modules``.

1.0.5 (2017-01-13)
------------------

* Changed the error message for ``I201`` to be about the banned *import*
  instead of *module*.
* Fix a bug introduced in 1.0.4 that broke parsing relative imports.

1.0.4 (2017-01-12)
------------------

* Don't allow installation with Flake8 3.2.0 which doesn't enable the plugin.
  This bug was fixed in Flake8 3.2.1.
* Use the most specific message available for a banned import.

1.0.3 (2016-11-05)
------------------

* Fixed reading config from flake8 3+

1.0.2 (2016-07-04)
------------------

* Fixed ``I201`` rule to detect banned imports like ``from x import y``.

1.0.1 (2016-07-01)
------------------

* ``I201`` rule that allows you to configure complaining about certain modules
  being imported, e.g. if you are moving from Python 2 to 3 you could stop
  ``urlparse`` being imported in favour of ``six.moves.urllib.parse``.

1.0.0 (2016-01-23)
------------------

* First release on PyPI.
* ``I200`` rule that complains about unnecessary import aliasing, e.g.
  ``from foo import bar as bar``.
