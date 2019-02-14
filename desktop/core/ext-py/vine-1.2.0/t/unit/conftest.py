from __future__ import absolute_import, unicode_literals

import pytest


@pytest.fixture(autouse=True)
def zzzz_test_cases_calls_setup_teardown(request):
    if request.instance:
        # we set the .patching attribute for every test class.
        setup = getattr(request.instance, 'setup', None)
        # we also call .setup() and .teardown() after every test method.
        setup and setup()
    yield
    if request.instance:
        teardown = getattr(request.instance, 'teardown', None)
        teardown and teardown()


@pytest.fixture(autouse=True)
def test_cases_has_patching(request, patching):
    if request.instance:
        request.instance.patching = patching
