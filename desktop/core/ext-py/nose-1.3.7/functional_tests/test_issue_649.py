# -*- coding: utf-8 -*-
import os
import sys
import unittest
from nose.plugins.capture import Capture
from nose.plugins import PluginTester

support = os.path.join(os.path.dirname(__file__), 'support')

class TestIssue649(PluginTester, unittest.TestCase):
    activate = ''
    args = ['-v']
    plugins = [Capture()]
    suitepath = os.path.join(support, 'issue649')

    def runTest(self):
        print str(self.output)
        assert 'UnicodeDecodeError' not in self.output
