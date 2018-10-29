# coding: utf-8
# vim: tabstop=4 expandtab autoindent shiftwidth=4 fileencoding=utf-8
"""Provides Nose and Django test case assert functions."""

from __future__ import unicode_literals


def _get_nose_vars():
    """Collect assert_*, ok_, and eq_ from nose.tools."""
    from nose import tools
    new_names = {}
    for t in dir(tools):
        if t.startswith('assert_') or t in ('ok_', 'eq_'):
            new_names[t] = getattr(tools, t)
    return new_names


for _name, _value in _get_nose_vars().items():
    vars()[_name] = _value


def _get_django_vars():
    """Collect assert_* methods from Django's TransactionTestCase."""
    import re
    from django.test.testcases import TransactionTestCase
    camelcase = re.compile('([a-z][A-Z]|[A-Z][a-z])')

    def insert_underscore(m):
            """Insert an appropriate underscore into the name."""
            a, b = m.group(0)
            if b.islower():
                return '_{}{}'.format(a, b)
            else:
                return '{}_{}'.format(a, b)

    def pep8(name):
        """Replace camelcase name with PEP8 equivalent."""
        return str(camelcase.sub(insert_underscore, name).lower())

    class Dummy(TransactionTestCase):
        """A dummy test case for gathering current assertion helpers."""

        def nop():
            """Do nothing, dummy test to get an initialized test case."""
            pass
    dummy_test = Dummy('nop')

    new_names = {}
    for assert_name in [at for at in dir(dummy_test)
                        if at.startswith('assert') and '_' not in at]:
        pepd = pep8(assert_name)
        new_names[pepd] = getattr(dummy_test, assert_name)
    return new_names


for _name, _value in _get_django_vars().items():
    vars()[_name] = _value


#
# Additional assertions
#

def assert_code(response, status_code, msg_prefix=''):
    """Assert the response was returned with the given status code."""
    if msg_prefix:
        msg_prefix = '%s: ' % msg_prefix

    assert response.status_code == status_code, \
        'Response code was %d (expected %d)' % (
            response.status_code, status_code)


def assert_ok(response, msg_prefix=''):
    """Assert the response was returned with status 200 (OK)."""
    return assert_code(response, 200, msg_prefix=msg_prefix)


def assert_mail_count(count, msg=None):
    """Assert the number of emails sent.

    The message here tends to be long, so allow for replacing the whole
    thing instead of prefixing.
    """
    from django.core import mail

    if msg is None:
        msg = ', '.join([e.subject for e in mail.outbox])
        msg = '%d != %d %s' % (len(mail.outbox), count, msg)
    # assert_equals is dynamicaly added above. F821 is undefined name error
    assert_equals(len(mail.outbox), count, msg)  # noqa: F821
