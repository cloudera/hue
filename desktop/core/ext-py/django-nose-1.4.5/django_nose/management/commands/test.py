# coding: utf-8
"""
Add extra options from the test runner to the ``test`` command.

This enables browsing all the nose options from the command line.
"""
from __future__ import unicode_literals

from django.conf import settings
from django.core.management.commands.test import Command
from django.test.utils import get_runner


TestRunner = get_runner(settings)

if hasattr(TestRunner, 'options'):
    extra_options = TestRunner.options
else:
    extra_options = []


class Command(Command):
    """Implement the ``test`` command."""

    option_list = getattr(Command, 'option_list', ()) + tuple(extra_options)
