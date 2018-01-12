# coding: utf-8
"""The django_nose module."""
from __future__ import unicode_literals

from django_nose.runner import BasicNoseRunner, NoseTestSuiteRunner
from django_nose.testcases import FastFixtureTestCase
assert BasicNoseRunner
assert NoseTestSuiteRunner
assert FastFixtureTestCase

VERSION = (1, 4, 5)
__version__ = '.'.join(map(str, VERSION))
