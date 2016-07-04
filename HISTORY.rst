=======
History
=======

Pending Release
---------------

* New release notes here

1.0.1 (2016-07-04)
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
