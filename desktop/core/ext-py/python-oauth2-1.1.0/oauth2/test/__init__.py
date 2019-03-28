import sys

# Enables unit tests to work under Python 2.6
# Code copied from
# https://github.com/facebook/tornado/blob/master/tornado/test/util.py
if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest
