# -*- coding: utf-8 -*-

# test/scaffold.py
# Part of python-daemon, an implementation of PEP 3143.
#
# Copyright © 2007–2009 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE.GPL-2 for details.

""" Scaffolding for unit test modules.
    """

import unittest
import doctest
import logging
import os
import sys
import operator
import textwrap
from minimock import (
    Mock,
    TraceTracker as MockTracker,
    mock,
    restore as mock_restore,
    )

test_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(test_dir)
if not test_dir in sys.path:
    sys.path.insert(1, test_dir)
if not parent_dir in sys.path:
    sys.path.insert(1, parent_dir)

# Disable all but the most critical logging messages
logging.disable(logging.CRITICAL)


def get_python_module_names(file_list, file_suffix='.py'):
    """ Return a list of module names from a filename list. """
    module_names = [m[:m.rfind(file_suffix)] for m in file_list
        if m.endswith(file_suffix)]
    return module_names


def get_test_module_names(module_list, module_prefix='test_'):
    """ Return the list of module names that qualify as test modules. """
    module_names = [m for m in module_list
        if m.startswith(module_prefix)]
    return module_names


def make_suite(path=test_dir):
    """ Create the test suite for the given path. """
    loader = unittest.TestLoader()
    python_module_names = get_python_module_names(os.listdir(path))
    test_module_names = get_test_module_names(python_module_names)
    suite = loader.loadTestsFromNames(test_module_names)

    return suite


def get_function_signature(func):
    """ Get the function signature as a mapping of attributes. """
    arg_count = func.func_code.co_argcount
    arg_names = func.func_code.co_varnames[:arg_count]

    arg_defaults = {}
    func_defaults = ()
    if func.func_defaults is not None:
        func_defaults = func.func_defaults
    for (name, value) in zip(arg_names[::-1], func_defaults[::-1]):
        arg_defaults[name] = value

    signature = {
        'name': func.__name__,
        'arg_count': arg_count,
        'arg_names': arg_names,
        'arg_defaults': arg_defaults,
        }

    non_pos_names = list(func.func_code.co_varnames[arg_count:])
    COLLECTS_ARBITRARY_POSITIONAL_ARGS = 0x04
    if func.func_code.co_flags & COLLECTS_ARBITRARY_POSITIONAL_ARGS:
        signature['var_args'] = non_pos_names.pop(0)
    COLLECTS_ARBITRARY_KEYWORD_ARGS = 0x08
    if func.func_code.co_flags & COLLECTS_ARBITRARY_KEYWORD_ARGS:
        signature['var_kw_args'] = non_pos_names.pop(0)

    return signature


def format_function_signature(func):
    """ Format the function signature as printable text. """
    signature = get_function_signature(func)

    args_text = []
    for arg_name in signature['arg_names']:
        if arg_name in signature['arg_defaults']:
            arg_default = signature['arg_defaults'][arg_name]
            arg_text_template = "%(arg_name)s=%(arg_default)r"
        else:
            arg_text_template = "%(arg_name)s"
        args_text.append(arg_text_template % vars())
    if 'var_args' in signature:
        args_text.append("*%(var_args)s" % signature)
    if 'var_kw_args' in signature:
        args_text.append("**%(var_kw_args)s" % signature)
    signature_args_text = ", ".join(args_text)

    func_name = signature['name']
    signature_text = (
        "%(func_name)s(%(signature_args_text)s)" % vars())

    return signature_text


class TestCase(unittest.TestCase):
    """ Test case behaviour. """

    def failUnlessRaises(self, exc_class, func, *args, **kwargs):
        """ Fail unless the function call raises the expected exception.

            Fail the test if an instance of the exception class
            ``exc_class`` is not raised when calling ``func`` with the
            arguments ``*args`` and ``**kwargs``.

            """
        try:
            super(TestCase, self).failUnlessRaises(
                exc_class, func, *args, **kwargs)
        except self.failureException:
            exc_class_name = exc_class.__name__
            msg = (
                "Exception %(exc_class_name)s not raised"
                " for function call:"
                " func=%(func)r args=%(args)r kwargs=%(kwargs)r"
                ) % vars()
            raise self.failureException(msg)

    def failIfIs(self, first, second, msg=None):
        """ Fail if the two objects are identical.

            Fail the test if ``first`` and ``second`` are identical,
            as determined by the ``is`` operator.

            """
        if first is second:
            if msg is None:
                msg = "%(first)r is %(second)r" % vars()
            raise self.failureException(msg)

    def failUnlessIs(self, first, second, msg=None):
        """ Fail unless the two objects are identical.

            Fail the test unless ``first`` and ``second`` are
            identical, as determined by the ``is`` operator.

            """
        if first is not second:
            if msg is None:
                msg = "%(first)r is not %(second)r" % vars()
            raise self.failureException(msg)

    assertIs = failUnlessIs
    assertNotIs = failIfIs

    def failIfIn(self, first, second, msg=None):
        """ Fail if the second object is in the first.

            Fail the test if ``first`` contains ``second``, as
            determined by the ``in`` operator.

            """
        if second in first:
            if msg is None:
                msg = "%(second)r is in %(first)r" % vars()
            raise self.failureException(msg)

    def failUnlessIn(self, first, second, msg=None):
        """ Fail unless the second object is in the first.

            Fail the test unless ``first`` contains ``second``, as
            determined by the ``in`` operator.

            """
        if second not in first:
            if msg is None:
                msg = "%(second)r is not in %(first)r" % vars()
            raise self.failureException(msg)

    assertIn = failUnlessIn
    assertNotIn = failIfIn

    def failUnlessOutputCheckerMatch(self, want, got, msg=None):
        """ Fail unless the specified string matches the expected.

            Fail the test unless ``want`` matches ``got``, as
            determined by a ``doctest.OutputChecker`` instance. This
            is not an equality check, but a pattern match according to
            the ``OutputChecker`` rules.

            """
        checker = doctest.OutputChecker()
        want = textwrap.dedent(want)
        source = ""
        example = doctest.Example(source, want)
        got = textwrap.dedent(got)
        checker_optionflags = reduce(operator.or_, [
            doctest.ELLIPSIS,
            ])
        if not checker.check_output(want, got, checker_optionflags):
            if msg is None:
                diff = checker.output_difference(
                    example, got, checker_optionflags)
                msg = "\n".join([
                    "Output received did not match expected output",
                    "%(diff)s",
                    ]) % vars()
            raise self.failureException(msg)

    assertOutputCheckerMatch = failUnlessOutputCheckerMatch

    def failUnlessMockCheckerMatch(self, want, tracker=None, msg=None):
        """ Fail unless the mock tracker matches the wanted output.

            Fail the test unless `want` matches the output tracked by
            `tracker` (defaults to ``self.mock_tracker``. This is not
            an equality check, but a pattern match according to the
            ``minimock.MinimockOutputChecker`` rules.

            """
        if tracker is None:
            tracker = self.mock_tracker
        if not tracker.check(want):
            if msg is None:
                diff = tracker.diff(want)
                msg = "\n".join([
                    "Output received did not match expected output",
                    "%(diff)s",
                    ]) % vars()
            raise self.failureException(msg)

    def failIfMockCheckerMatch(self, want, tracker=None, msg=None):
        """ Fail if the mock tracker matches the specified output.

            Fail the test if `want` matches the output tracked by
            `tracker` (defaults to ``self.mock_tracker``. This is not
            an equality check, but a pattern match according to the
            ``minimock.MinimockOutputChecker`` rules.

            """
        if tracker is None:
            tracker = self.mock_tracker
        if tracker.check(want):
            if msg is None:
                diff = tracker.diff(want)
                msg = "\n".join([
                    "Output received matched specified undesired output",
                    "%(diff)s",
                    ]) % vars()
            raise self.failureException(msg)

    assertMockCheckerMatch = failUnlessMockCheckerMatch
    assertNotMockCheckerMatch = failIfMockCheckerMatch

    def failIfIsInstance(self, obj, classes, msg=None):
        """ Fail if the object is an instance of the specified classes.

            Fail the test if the object ``obj`` is an instance of any
            of ``classes``.

            """
        if isinstance(obj, classes):
            if msg is None:
                msg = (
                    "%(obj)r is an instance of one of %(classes)r"
                    ) % vars()
            raise self.failureException(msg)

    def failUnlessIsInstance(self, obj, classes, msg=None):
        """ Fail unless the object is an instance of the specified classes.

            Fail the test unless the object ``obj`` is an instance of
            any of ``classes``.

            """
        if not isinstance(obj, classes):
            if msg is None:
                msg = (
                    "%(obj)r is not an instance of any of %(classes)r"
                    ) % vars()
            raise self.failureException(msg)

    assertIsInstance = failUnlessIsInstance
    assertNotIsInstance = failIfIsInstance

    def failUnlessFunctionInTraceback(self, traceback, function, msg=None):
        """ Fail if the function is not in the traceback.

            Fail the test if the function ``function`` is not at any
            of the levels in the traceback object ``traceback``.

            """
        func_in_traceback = False
        expect_code = function.func_code
        current_traceback = traceback
        while current_traceback is not None:
            if expect_code is current_traceback.tb_frame.f_code:
                func_in_traceback = True
                break
            current_traceback = current_traceback.tb_next

        if not func_in_traceback:
            if msg is None:
                msg = (
                    "Traceback did not lead to original function"
                    " %(function)s"
                    ) % vars()
            raise self.failureException(msg)

    assertFunctionInTraceback = failUnlessFunctionInTraceback

    def failUnlessFunctionSignatureMatch(self, first, second, msg=None):
        """ Fail if the function signatures do not match.

            Fail the test if the function signature does not match
            between the ``first`` function and the ``second``
            function.

            The function signature includes:

            * function name,

            * count of named parameters,

            * sequence of named parameters,

            * default values of named parameters,

            * collector for arbitrary positional arguments,

            * collector for arbitrary keyword arguments.

            """
        first_signature = get_function_signature(first)
        second_signature = get_function_signature(second)

        if first_signature != second_signature:
            if msg is None:
                first_signature_text = format_function_signature(first)
                second_signature_text = format_function_signature(second)
                msg = (textwrap.dedent("""\
                    Function signatures do not match:
                        %(first_signature)r != %(second_signature)r
                    Expected:
                        %(first_signature_text)s
                    Got:
                        %(second_signature_text)s""")
                    ) % vars()
            raise self.failureException(msg)

    assertFunctionSignatureMatch = failUnlessFunctionSignatureMatch


class Exception_TestCase(TestCase):
    """ Test cases for exception classes. """

    def __init__(self, *args, **kwargs):
        """ Set up a new instance """
        self.valid_exceptions = NotImplemented
        super(Exception_TestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        """ Set up test fixtures. """
        for exc_type, params in self.valid_exceptions.items():
            args = (None, ) * params['min_args']
            params['args'] = args
            instance = exc_type(*args)
            params['instance'] = instance

        super(Exception_TestCase, self).setUp()

    def test_exception_instance(self):
        """ Exception instance should be created. """
        for params in self.valid_exceptions.values():
            instance = params['instance']
            self.failIfIs(None, instance)

    def test_exception_types(self):
        """ Exception instances should match expected types. """
        for params in self.valid_exceptions.values():
            instance = params['instance']
            for match_type in params['types']:
                match_type_name = match_type.__name__
                fail_msg = (
                    "%(instance)r is not an instance of"
                    " %(match_type_name)s"
                    ) % vars()
                self.failUnless(
                    isinstance(instance, match_type),
                    msg=fail_msg)
