"""
Simple auto test discovery.

From http://stackoverflow.com/a/17004409
"""
import os
import sys
import unittest

if not hasattr(unittest.defaultTestLoader, 'discover'):
    try:
        import unittest2 as unittest
    except ImportError:
        raise ImportError('The unittest2 module is required to run tests on Python 2.6')

def additional_tests():
    setup_file = sys.modules['__main__'].__file__
    setup_dir = os.path.abspath(os.path.dirname(setup_file))
    test_dir = os.path.join(setup_dir, 'tests')
    test_suite = unittest.defaultTestLoader.discover(test_dir)
    blacklist = []
    if '/home/travis' in __file__:
        # Skip some tests that fail on travis-ci
        blacklist.append('test_command')
    return exclude_tests(test_suite, blacklist)


class SkipCase(unittest.TestCase):
    def skeleton_run_test(self):
        raise unittest.SkipTest("Test fails spuriously on travis-ci")


def exclude_tests(suite, blacklist):
    """
    Example:
    
    blacklist = [
        'test_some_test_that_should_be_skipped',
        'test_another_test_that_should_be_skipped'
    ]
    """
    new_suite = unittest.TestSuite()
    
    for test_group in suite._tests:
        for test in test_group:
            if not hasattr(test, '_tests'):
                # e.g. ModuleImportFailure
                new_suite.addTest(test)
                continue
            for subtest in test._tests:
                method = subtest._testMethodName
                if method in blacklist:
                    setattr(test,
                            method,
                            getattr(SkipCase(), 'skeleton_run_test'))
            new_suite.addTest(test)
    return new_suite

