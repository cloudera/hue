#._cv_part guppy.heapy.test.support

"""Supporting definitions for the Heapy regression test.
Addapted from Python standard module test_support.
"""

import sys

class Error(Exception):
    """Base class for regression test exceptions."""

class TestFailed(Error):
    """Test failed."""

class TestSkipped(Error):
    """Test skipped.

    This can be raised to indicate that a test was deliberatly
    skipped, but not because a feature wasn't available.  For
    example, if some resource can't be used, such as the network
    appears to be unavailable, this should be raised instead of
    TestFailed.
    """

verbose = 1              # Flag set to 0 by regrtest.py
use_resources = None       # Flag set to [] by regrtest.py

# _original_stdout is meant to hold stdout at the time regrtest began.
# This may be "the real" stdout, or IDLE's emulation of stdout, or whatever.
# The point is to have some flavor of stdout the user can actually see.
_original_stdout = None
def record_original_stdout(stdout):
    global _original_stdout
    _original_stdout = stdout

def get_original_stdout():
    return _original_stdout or sys.stdout

def unload(name):
    try:
        del sys.modules[name]
    except KeyError:
        pass

def forget(modname):
    unload(modname)
    import os
    for dirname in sys.path:
        try:
            os.unlink(os.path.join(dirname, modname + '.pyc'))
        except os.error:
            pass

def requires(resource, msg=None):
    if use_resources is not None and resource not in use_resources:
        if msg is None:
            msg = "Use of the `%s' resource not enabled" % resource
        raise TestSkipped(msg)

FUZZ = 1e-6

def fcmp(x, y): # fuzzy comparison function
    if type(x) == type(0.0) or type(y) == type(0.0):
        try:
            x, y = coerce(x, y)
            fuzz = (abs(x) + abs(y)) * FUZZ
            if abs(x-y) <= fuzz:
                return 0
        except:
            pass
    elif type(x) == type(y) and type(x) in (type(()), type([])):
        for i in range(min(len(x), len(y))):
            outcome = fcmp(x[i], y[i])
            if outcome != 0:
                return outcome
        return cmp(len(x), len(y))
    return cmp(x, y)

try:
    unicode
    have_unicode = 1
except NameError:
    have_unicode = 0

import os
# Filename used for testing
if os.name == 'java':
    # Jython disallows @ in module names
    TESTFN = '$test'
elif os.name != 'riscos':
    TESTFN = '@test'
    # Unicode name only used if TEST_FN_ENCODING exists for the platform.
    if have_unicode:
        TESTFN_UNICODE=unicode("@test-\xe0\xf2", "latin-1") # 2 latin characters.
        if os.name=="nt":
            TESTFN_ENCODING="mbcs"
else:
    TESTFN = 'test'
del os

from os import unlink

def findfile(file, here=__file__):
    import os
    if os.path.isabs(file):
        return file
    path = sys.path
    path = [os.path.dirname(here)] + path
    for dn in path:
        fn = os.path.join(dn, file)
        if os.path.exists(fn): return fn
    return file

def verify(condition, reason='test failed'):
    """Verify that condition is true. If not, raise TestFailed.

       The optional argument reason can be given to provide
       a better error text.
    """

    if not condition:
        raise TestFailed(reason)

def vereq(a, b):
    """Raise TestFailed if a == b is false.

    This is better than verify(a == b) because, in case of failure, the
    error message incorporates repr(a) and repr(b) so you can see the
    inputs.

    Note that "not (a == b)" isn't necessarily the same as "a != b"; the
    former is tested.
    """

    if not (a == b):
        raise TestFailed, "%r == %r" % (a, b)

def sortdict(dict):
    "Like repr(dict), but in sorted order."
    items = dict.items()
    items.sort()
    reprpairs = ["%r: %r" % pair for pair in items]
    withcommas = ", ".join(reprpairs)
    return "{%s}" % withcommas

def check_syntax(statement):
    try:
        compile(statement, '<string>', 'exec')
    except SyntaxError:
        pass
    else:
        print 'Missing SyntaxError: "%s"' % statement



#=======================================================================
# Preliminary PyUNIT integration.

import unittest


class BasicTestRunner:
    def run(self, test):
        result = unittest.TestResult()
        test(result)
        return result


def run_suite(suite, testclass=None):
    """Run tests from a unittest.TestSuite-derived class."""
    if verbose:
        runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
    else:
        runner = BasicTestRunner()

    result = runner.run(suite)
    if not result.wasSuccessful():
        if len(result.errors) == 1 and not result.failures:
            err = result.errors[0][1]
        elif len(result.failures) == 1 and not result.errors:
            err = result.failures[0][1]
        else:
            if testclass is None:
                msg = "errors occurred; run in verbose mode for details"
            else:
                msg = "errors occurred in %s.%s" \
                      % (testclass.__module__, testclass.__name__)
            raise TestFailed(msg)
        raise TestFailed(err)


def run_unittest(testclass, debug=0):
    """Run tests from a unittest.TestCase-derived class."""
    suite = unittest.makeSuite(testclass)
    if debug:
	suite.debug()
    else:
	run_suite(suite, testclass)

def debug_unittest(testclass):
    """ Debug tests from a unittest.TestCase-derived class."""
    run_unittest(testclass, debug=1)



#=======================================================================
# doctest driver.

def run_doctest(module, verbosity=None):
    """Run doctest on the given module.  Return (#failures, #tests).

    If optional argument verbosity is not specified (or is None), pass
    test_support's belief about verbosity on to doctest.  Else doctest's
    usual behavior is used (it searches sys.argv for -v).
    """

    import doctest

    if verbosity is None:
        verbosity = verbose
    else:
        verbosity = None

    # Direct doctest output (normally just errors) to real stdout; doctest
    # output shouldn't be compared by regrtest.
    save_stdout = sys.stdout
    sys.stdout = get_original_stdout()
    try:
        f, t = doctest.testmod(module, verbose=verbosity)
        if f:
            raise TestFailed("%d of %d doctests failed" % (f, t))
        return f, t
    finally:
        sys.stdout = save_stdout

# Base test case, tailored for heapy

class TestCase(unittest.TestCase):
    def setUp(self):
	from guppy import Root
	self.python = Root()
	self.guppy = self.python.guppy
	self.heapy = self.guppy.heapy
	self.Part = self.heapy.Part
	self.ImpSet = self.heapy.ImpSet
	self.Use = self.heapy.Use
	self.View = self.heapy.View
	self.allocation_behaves_as_originally = self.heapy.allocation_behaves_as_originally
	self.iso = self.Use.iso
	self.idset = self.Use.idset

    def aseq(self, a, b, cont=0):
	if a != b:
	    print "aseq: Expected: b = ", b
	    print "Got actually  : a = ", a
	    if cont <= 0:
		if cont < 0:
		    pdb.set_trace()
		else:
		    self.assert_(0)
    
    def asis(self, a, b, cont=0):
	if a is not b:
	    print "asis: Expected: b = ", b
	    print "Got actually  : a = ", a
	    if cont <= 0:
		if cont < 0:
		    pdb.set_trace()
		else:
		    self.assert_(0)
    
    def tearDown(self):
	pass


