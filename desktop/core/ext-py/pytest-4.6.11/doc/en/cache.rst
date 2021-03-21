.. _`cache_provider`:
.. _cache:


Cache: working with cross-testrun state
=======================================



Usage
---------

The plugin provides two command line options to rerun failures from the
last ``pytest`` invocation:

* ``--lf``, ``--last-failed`` - to only re-run the failures.
* ``--ff``, ``--failed-first`` - to run the failures first and then the rest of
  the tests.

For cleanup (usually not needed), a ``--cache-clear`` option allows to remove
all cross-session cache contents ahead of a test run.

Other plugins may access the `config.cache`_ object to set/get
**json encodable** values between ``pytest`` invocations.

.. note::

    This plugin is enabled by default, but can be disabled if needed: see
    :ref:`cmdunregister` (the internal name for this plugin is
    ``cacheprovider``).


Rerunning only failures or failures first
-----------------------------------------------

First, let's create 50 test invocation of which only 2 fail::

    # content of test_50.py
    import pytest

    @pytest.mark.parametrize("i", range(50))
    def test_num(i):
        if i in (17, 25):
           pytest.fail("bad luck")

If you run this for the first time you will see two failures:

.. code-block:: pytest

    $ pytest -q
    .................F.......F........................                   [100%]
    ================================= FAILURES =================================
    _______________________________ test_num[17] _______________________________

    i = 17

        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17, 25):
    >          pytest.fail("bad luck")
    E          Failed: bad luck

    test_50.py:6: Failed
    _______________________________ test_num[25] _______________________________

    i = 25

        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17, 25):
    >          pytest.fail("bad luck")
    E          Failed: bad luck

    test_50.py:6: Failed
    2 failed, 48 passed in 0.12 seconds

If you then run it with ``--lf``:

.. code-block:: pytest

    $ pytest --lf
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-4.x.y, py-1.x.y, pluggy-0.x.y
    cachedir: $PYTHON_PREFIX/.pytest_cache
    rootdir: $REGENDOC_TMPDIR
    collected 50 items / 48 deselected / 2 selected
    run-last-failure: rerun previous 2 failures

    test_50.py FF                                                        [100%]

    ================================= FAILURES =================================
    _______________________________ test_num[17] _______________________________

    i = 17

        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17, 25):
    >          pytest.fail("bad luck")
    E          Failed: bad luck

    test_50.py:6: Failed
    _______________________________ test_num[25] _______________________________

    i = 25

        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17, 25):
    >          pytest.fail("bad luck")
    E          Failed: bad luck

    test_50.py:6: Failed
    ================= 2 failed, 48 deselected in 0.12 seconds ==================

You have run only the two failing test from the last run, while 48 tests have
not been run ("deselected").

Now, if you run with the ``--ff`` option, all tests will be run but the first
previous failures will be executed first (as can be seen from the series
of ``FF`` and dots):

.. code-block:: pytest

    $ pytest --ff
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-4.x.y, py-1.x.y, pluggy-0.x.y
    cachedir: $PYTHON_PREFIX/.pytest_cache
    rootdir: $REGENDOC_TMPDIR
    collected 50 items
    run-last-failure: rerun previous 2 failures first

    test_50.py FF................................................        [100%]

    ================================= FAILURES =================================
    _______________________________ test_num[17] _______________________________

    i = 17

        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17, 25):
    >          pytest.fail("bad luck")
    E          Failed: bad luck

    test_50.py:6: Failed
    _______________________________ test_num[25] _______________________________

    i = 25

        @pytest.mark.parametrize("i", range(50))
        def test_num(i):
            if i in (17, 25):
    >          pytest.fail("bad luck")
    E          Failed: bad luck

    test_50.py:6: Failed
    =================== 2 failed, 48 passed in 0.12 seconds ====================

.. _`config.cache`:

New ``--nf``, ``--new-first`` options: run new tests first followed by the rest
of the tests, in both cases tests are also sorted by the file modified time,
with more recent files coming first.

Behavior when no tests failed in the last run
---------------------------------------------

When no tests failed in the last run, or when no cached ``lastfailed`` data was
found, ``pytest`` can be configured either to run all of the tests or no tests,
using the ``--last-failed-no-failures`` option, which takes one of the following values:

.. code-block:: bash

    pytest --last-failed --last-failed-no-failures all    # run all tests (default behavior)
    pytest --last-failed --last-failed-no-failures none   # run no tests and exit

The new config.cache object
--------------------------------

.. regendoc:wipe

Plugins or conftest.py support code can get a cached value using the
pytest ``config`` object.  Here is a basic example plugin which
implements a :ref:`fixture` which re-uses previously created state
across pytest invocations::

    # content of test_caching.py
    import pytest
    import time

    def expensive_computation():
        print("running expensive computation...")

    @pytest.fixture
    def mydata(request):
        val = request.config.cache.get("example/value", None)
        if val is None:
            expensive_computation()
            val = 42
            request.config.cache.set("example/value", val)
        return val

    def test_function(mydata):
        assert mydata == 23

If you run this command for the first time, you can see the print statement:

.. code-block:: pytest

    $ pytest -q
    F                                                                    [100%]
    ================================= FAILURES =================================
    ______________________________ test_function _______________________________

    mydata = 42

        def test_function(mydata):
    >       assert mydata == 23
    E       assert 42 == 23

    test_caching.py:17: AssertionError
    -------------------------- Captured stdout setup ---------------------------
    running expensive computation...
    1 failed in 0.12 seconds

If you run it a second time the value will be retrieved from
the cache and nothing will be printed:

.. code-block:: pytest

    $ pytest -q
    F                                                                    [100%]
    ================================= FAILURES =================================
    ______________________________ test_function _______________________________

    mydata = 42

        def test_function(mydata):
    >       assert mydata == 23
    E       assert 42 == 23

    test_caching.py:17: AssertionError
    1 failed in 0.12 seconds

See the :ref:`cache-api` for more details.


Inspecting Cache content
------------------------

You can always peek at the content of the cache using the
``--cache-show`` command line option:

.. code-block:: pytest

    $ pytest --cache-show
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-4.x.y, py-1.x.y, pluggy-0.x.y
    cachedir: $PYTHON_PREFIX/.pytest_cache
    rootdir: $REGENDOC_TMPDIR
    cachedir: $PYTHON_PREFIX/.pytest_cache
    --------------------------- cache values for '*' ---------------------------
    cache/lastfailed contains:
      {'test_50.py::test_num[17]': True,
       'test_50.py::test_num[25]': True,
       'test_assert1.py::test_function': True,
       'test_assert2.py::test_set_comparison': True,
       'test_caching.py::test_function': True,
       'test_foocompare.py::test_compare': True}
    cache/nodeids contains:
      ['test_caching.py::test_function']
    cache/stepwise contains:
      []
    example/value contains:
      42

    ======================= no tests ran in 0.12 seconds =======================

``--cache-show`` takes an optional argument to specify a glob pattern for
filtering:

.. code-block:: pytest

    $ pytest --cache-show example/*
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-4.x.y, py-1.x.y, pluggy-0.x.y
    cachedir: $PYTHON_PREFIX/.pytest_cache
    rootdir: $REGENDOC_TMPDIR
    cachedir: $PYTHON_PREFIX/.pytest_cache
    ----------------------- cache values for 'example/*' -----------------------
    example/value contains:
      42

    ======================= no tests ran in 0.12 seconds =======================

Clearing Cache content
----------------------

You can instruct pytest to clear all cache files and values
by adding the ``--cache-clear`` option like this:

.. code-block:: bash

    pytest --cache-clear

This is recommended for invocations from Continuous Integration
servers where isolation and correctness is more important
than speed.


Stepwise
--------

As an alternative to ``--lf -x``, especially for cases where you expect a large part of the test suite will fail, ``--sw``, ``--stepwise`` allows you to fix them one at a time. The test suite will run until the first failure and then stop. At the next invocation, tests will continue from the last failing test and then run until the next failing test. You may use the ``--stepwise-skip`` option to ignore one failing test and stop the test execution on the second failing test instead. This is useful if you get stuck on a failing test and just want to ignore it until later.
