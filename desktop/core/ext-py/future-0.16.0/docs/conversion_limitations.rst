.. _futurize-limitations:

Known limitations
-----------------

``futurize`` and ``pasteurize`` are useful to automate much of the
work of porting, particularly the boring repetitive text substitutions. They also
help to flag which parts of the code require attention.

Nevertheless, ``futurize`` and ``pasteurize`` are still incomplete and make
some mistakes, like 2to3, on which they are based. Please report bugs on
`GitHub <https://github.com/PythonCharmers/python-future/>`_. Contributions to
the ``lib2to3``-based fixers for ``futurize`` and ``pasteurize`` are
particularly welcome! Please see :ref:`contributing`.

``futurize`` doesn't currently make the following change automatically:

1. Strings containing ``\U`` produce a ``SyntaxError`` on Python 3. An example is::

       s = 'C:\Users'.

   Python 2 expands this to ``s = 'C:\\Users'``, but Python 3 requires a raw
   prefix (``r'...'``). This also applies to multi-line strings (including
   multi-line docstrings).

Also see the tests in ``future/tests/test_futurize.py`` marked
``@expectedFailure`` or ``@skip`` for known limitations.
