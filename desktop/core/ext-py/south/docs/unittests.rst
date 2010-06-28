Unit Test Integration
=====================

By default, South's syncdb command will also apply migrations if it's run in
non-interactive mode, which includes when you're running tests - it will run
every migration every time you run your tests.

If you want the test runner to use syncdb instead of migrate - for example, if
your migrations are taking way too long to apply - simply set
``SOUTH_TESTS_MIGRATE = False`` in settings.py.

South's own unit tests
----------------------

South has its own set of unit tests; these will also be run when you run
./manage.py test. They do some fiddling with Django internals to set up a
proper test environment; it's non-destructive, but if it's fouling up your own
tests please submit a ticket about it.

You can also set ``SKIP_SOUTH_TESTS=True`` in settings.py to stop South's tests
running, should they be causing issues.