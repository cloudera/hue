"""
Tests for the super() function.

Based on Ryan Kelly's magicsuper.tests
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import future.builtins.newsuper
from future.builtins import super
from future.tests.base import unittest
from future import utils


class TestMagicSuper(unittest.TestCase):

    def test_basic_diamond(self):
        class Base(object):
            def calc(self,value):
                return 2 * value
        class Sub1(Base):
            def calc(self,value):
                return 7 + super().calc(value)
        class Sub2(Base):
            def calc(self,value):
                return super().calc(value) - 1
        class Diamond(Sub1,Sub2):
            def calc(self,value):
                return 3 * super().calc(value)
        b = Base()
        s1 = Sub1()
        s2 = Sub2()
        d = Diamond()
        for x in range(10):
            self.assertEqual(b.calc(x),2*x)
            self.assertEqual(s1.calc(x),7+(2*x))
            self.assertEqual(s2.calc(x),(2*x)-1)
            self.assertEqual(d.calc(x),3*(7+((2*x)-1)))

    def test_with_unrelated_methods(self):
        class Base(object):
            def hello(self):
                return "world"
        class Sub(Base):
            def hello(self):
                return "hello " + super().hello()
            def other(self):
                pass
        class SubSub(Sub):
            def other(self):
                return super().other()
        ss = SubSub()
        self.assertEqual(ss.hello(),"hello world")

    @unittest.skipIf(utils.PY3, "this test isn't relevant on Py3")
    def test_fails_for_oldstyle_class(self):
        class OldStyle:
            def testme(self):
                return super().testme()
        o = OldStyle()
        self.assertRaises(RuntimeError,o.testme)

    def test_fails_for_raw_functions(self):
        def not_a_method():
            super().not_a_method()
        self.assertRaises(RuntimeError,not_a_method)
        def not_a_method(self):
            super().not_a_method()
        if utils.PY2:
            self.assertRaises(RuntimeError,not_a_method,self)
        else:
            self.assertRaises(AttributeError,not_a_method,self)

    def assertSuperEquals(self,sobj1,sobj2):
        assert sobj1.__self__ is sobj2.__self__
        assert sobj1.__self_class__ is sobj2.__self_class__
        assert sobj1.__thisclass__ is sobj2.__thisclass__

    def test_call_with_args_does_nothing(self):
        if utils.PY2:
            from __builtin__ import super as builtin_super
        else:
            from builtins import super as builtin_super
        class Base(object):
            def calc(self,value):
                return 2 * value
        class Sub1(Base):
            def calc(self,value):
                return 7 + super().calc(value)
        class Sub2(Base):
            def calc(self,value):
                return super().calc(value) - 1
        class Diamond(Sub1,Sub2):
            def calc(self,value):
                return 3 * super().calc(value)
        for cls in (Base,Sub1,Sub2,Diamond,):
            obj = cls()
            self.assertSuperEquals(builtin_super(cls), super(cls))
            self.assertSuperEquals(builtin_super(cls,obj), super(cls,obj))

    @unittest.skipIf(utils.PY3, "this test isn't relevant for Py3's super()")
    def test_superm(self):
        class Base(object):
            def getit(self):
                return 2
        class Sub(Base):
            def getit(self):
                return 10 * future.builtins.newsuper.superm()
        s = Sub()
        self.assertEqual(s.getit(),20)

    def test_use_inside_dunder_new(self):
        class Terminal(str):
            def __new__(cls, value, token_type):
                self = super().__new__(cls, value)
                self.token_type = token_type
                return self
        DOT = Terminal(".", "dit")
        self.assertTrue(isinstance(DOT, str))
        self.assertTrue(isinstance(DOT, Terminal))

    def test_use_inside_classmethod(self):
        class Base(object):
            @classmethod
            def getit(cls):
                return 42
        class Singleton(Base):
            @classmethod
            def getit(cls):
                print(super())
                return super().getit() + 1
        self.assertEqual(Singleton.getit(), 43)


if __name__ == '__main__':
    unittest.main()

