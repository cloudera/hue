"""Unit tests for new super() implementation."""

from __future__ import absolute_import, division, unicode_literals
import sys

from future.tests.base import unittest, skip26, expectedFailurePY2
from future import utils
from future.builtins import super


class A(object):
    def f(self):
        return 'A'
    @classmethod
    def cm(cls):
        return (cls, 'A')

class B(A):
    def f(self):
        return super().f() + 'B'
    @classmethod
    def cm(cls):
        return (cls, super().cm(), 'B')

class C(A):
    def f(self):
        return super().f() + 'C'
    @classmethod
    def cm(cls):
        return (cls, super().cm(), 'C')

class D(C, B):
    def f(self):
        return super().f() + 'D'
    def cm(cls):
        return (cls, super().cm(), 'D')

class E(D):
    pass

class F(E):
    f = E.f

class G(A):
    pass


class TestSuper(unittest.TestCase):

    def test_basics_working(self):
        self.assertEqual(D().f(), 'ABCD')

    def test_class_getattr_working(self):
        self.assertEqual(D.f(D()), 'ABCD')

    def test_subclass_no_override_working(self):
        self.assertEqual(E().f(), 'ABCD')
        self.assertEqual(E.f(E()), 'ABCD')

    @expectedFailurePY2    # not working yet: infinite loop
    def test_unbound_method_transfer_working(self):
        self.assertEqual(F().f(), 'ABCD')
        self.assertEqual(F.f(F()), 'ABCD')

    def test_class_methods_still_working(self):
        self.assertEqual(A.cm(), (A, 'A'))
        self.assertEqual(A().cm(), (A, 'A'))
        self.assertEqual(G.cm(), (G, 'A'))
        self.assertEqual(G().cm(), (G, 'A'))

    def test_super_in_class_methods_working(self):
        d = D()
        self.assertEqual(d.cm(), (d, (D, (D, (D, 'A'), 'B'), 'C'), 'D'))
        e = E()
        self.assertEqual(e.cm(), (e, (E, (E, (E, 'A'), 'B'), 'C'), 'D'))

    def test_super_with_closure(self):
        # Issue4360: super() did not work in a function that
        # contains a closure
        class E(A):
            def f(self):
                def nested():
                    self
                return super().f() + 'E'

        self.assertEqual(E().f(), 'AE')

    # We declare this test invalid: __class__ should be a class.
    # def test___class___set(self):
    #     # See issue #12370
    #     class X(A):
    #         def f(self):
    #             return super().f()
    #         __class__ = 413
    #     x = X()
    #     self.assertEqual(x.f(), 'A')
    #     self.assertEqual(x.__class__, 413)

    @unittest.skipIf(utils.PY2, "no __class__ on Py2")
    def test___class___instancemethod(self):
        # See issue #14857
        class X(object):
            def f(self):
                return __class__
        self.assertIs(X().f(), X)

    @unittest.skipIf(utils.PY2, "no __class__ on Py2")
    def test___class___classmethod(self):
        # See issue #14857
        class X(object):
            @classmethod
            def f(cls):
                return __class__
        self.assertIs(X.f(), X)

    @unittest.skipIf(utils.PY2, "no __class__ on Py2")
    def test___class___staticmethod(self):
        # See issue #14857
        class X(object):
            @staticmethod
            def f():
                return __class__
        self.assertIs(X.f(), X)

    def test_obscure_super_errors(self):
        def f():
            super()
        self.assertRaises(RuntimeError, f)
        def f(x):
            del x
            super()
        self.assertRaises(RuntimeError, f, None)
        # class X(object):
        #     def f(x):
        #         nonlocal __class__
        #         del __class__
        #         super()
        # self.assertRaises(RuntimeError, X().f)

    def test_cell_as_self(self):
        class X(object):
            def meth(self):
                super()

        def f():
            k = X()
            def g():
                return k
            return g
        c = f().__closure__[0]
        self.assertRaises(TypeError, X.meth, c)

    def test_properties(self):
        class Harmless(object):
            bomb = ''

            def walk(self):
                return self.bomb

        class Dangerous(Harmless):
            @property
            def bomb(self):
                raise Exception("Kaboom")

            def walk(self):
                return super().walk()

        class Elite(Dangerous):
            bomb = 'Defused'

        self.assertEqual(Elite().walk(), 'Defused')


class TestSuperFromTestDescrDotPy(unittest.TestCase):
    """
    These are from Python 3.3.5/Lib/test/test_descr.py
    """
    @skip26
    def test_classmethods(self):
        # Testing class methods...
        class C(object):
            def foo(*a): return a
            goo = classmethod(foo)
        c = C()
        self.assertEqual(C.goo(1), (C, 1))
        self.assertEqual(c.goo(1), (C, 1))
        self.assertEqual(c.foo(1), (c, 1))
        class D(C):
            pass
        d = D()
        self.assertEqual(D.goo(1), (D, 1))
        self.assertEqual(d.goo(1), (D, 1))
        self.assertEqual(d.foo(1), (d, 1))
        self.assertEqual(D.foo(d, 1), (d, 1))
        # Test for a specific crash (SF bug 528132)
        def f(cls, arg): return (cls, arg)
        ff = classmethod(f)
        self.assertEqual(ff.__get__(0, int)(42), (int, 42))
        self.assertEqual(ff.__get__(0)(42), (int, 42))

        # Test super() with classmethods (SF bug 535444)
        self.assertEqual(C.goo.__self__, C)
        self.assertEqual(D.goo.__self__, D)
        self.assertEqual(super(D,D).goo.__self__, D)
        self.assertEqual(super(D,d).goo.__self__, D)
        self.assertEqual(super(D,D).goo(), (D,))
        self.assertEqual(super(D,d).goo(), (D,))

        # Verify that a non-callable will raise
        meth = classmethod(1).__get__(1)
        self.assertRaises(TypeError, meth)

        # Verify that classmethod() doesn't allow keyword args
        try:
            classmethod(f, kw=1)
        except TypeError:
            pass
        else:
            self.fail("classmethod shouldn't accept keyword args")

        # cm = classmethod(f)
        # self.assertEqual(cm.__dict__, {})
        # cm.x = 42
        # self.assertEqual(cm.x, 42)
        # self.assertEqual(cm.__dict__, {"x" : 42})
        # del cm.x
        # self.assertTrue(not hasattr(cm, "x"))

    def test_supers(self):
        # Testing super...

        class A(object):
            def meth(self, a):
                return "A(%r)" % a

        self.assertEqual(A().meth(1), "A(1)")

        class B(A):
            def __init__(self):
                self.__super = super(B, self)
            def meth(self, a):
                return "B(%r)" % a + self.__super.meth(a)

        self.assertEqual(B().meth(2), "B(2)A(2)")

        class C(A):
            def meth(self, a):
                return "C(%r)" % a + self.__super.meth(a)
        C._C__super = super(C)

        self.assertEqual(C().meth(3), "C(3)A(3)")

        class D(C, B):
            def meth(self, a):
                return "D(%r)" % a + super(D, self).meth(a)

        self.assertEqual(D().meth(4), "D(4)C(4)B(4)A(4)")

        # # Test for subclassing super

        # class mysuper(super):
        #     def __init__(self, *args):
        #         return super(mysuper, self).__init__(*args)

        # class E(D):
        #     def meth(self, a):
        #         return "E(%r)" % a + mysuper(E, self).meth(a)

        # self.assertEqual(E().meth(5), "E(5)D(5)C(5)B(5)A(5)")

        # class F(E):
        #     def meth(self, a):
        #         s = self.__super # == mysuper(F, self)
        #         return "F(%r)[%s]" % (a, s.__class__.__name__) + s.meth(a)
        # F._F__super = mysuper(F)

        # self.assertEqual(F().meth(6), "F(6)[mysuper]E(6)D(6)C(6)B(6)A(6)")

        # Make sure certain errors are raised

        try:
            super(D, 42)
        except TypeError:
            pass
        else:
            self.fail("shouldn't allow super(D, 42)")

        try:
            super(D, C())
        except TypeError:
            pass
        else:
            self.fail("shouldn't allow super(D, C())")

        try:
            super(D).__get__(12)
        except TypeError:
            pass
        else:
            self.fail("shouldn't allow super(D).__get__(12)")

        try:
            super(D).__get__(C())
        except TypeError:
            pass
        else:
            self.fail("shouldn't allow super(D).__get__(C())")

        # Make sure data descriptors can be overridden and accessed via super
        # (new feature in Python 2.3)

        class DDbase(object):
            def getx(self): return 42
            x = property(getx)

        class DDsub(DDbase):
            def getx(self): return "hello"
            x = property(getx)

        dd = DDsub()
        self.assertEqual(dd.x, "hello")
        self.assertEqual(super(DDsub, dd).x, 42)

        # Ensure that super() lookup of descriptor from classmethod
        # works (SF ID# 743627)

        class Base(object):
            aProp = property(lambda self: "foo")

        class Sub(Base):
            @classmethod
            def test(klass):
                return super(Sub,klass).aProp

        self.assertEqual(Sub.test(), Base.aProp)

        # Verify that super() doesn't allow keyword args
        try:
            super(Base, kw=1)
        except TypeError:
            pass
        else:
            self.assertEqual("super shouldn't accept keyword args")


if __name__ == "__main__":
    unittest.main()
