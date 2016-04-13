import gc
import sys
import time
import weakref

from django.dispatch import Signal, receiver
from django.utils import unittest


if sys.platform.startswith('java'):
    def garbage_collect():
        # Some JVM GCs will execute finalizers in a different thread, meaning
        # we need to wait for that to complete before we go on looking for the
        # effects of that.
        gc.collect()
        time.sleep(0.1)
elif hasattr(sys, "pypy_version_info"):
    def garbage_collect():
        # Collecting weakreferences can take two collections on PyPy.
        gc.collect()
        gc.collect()
else:
    def garbage_collect():
        gc.collect()

def receiver_1_arg(val, **kwargs):
    return val

class Callable(object):
    def __call__(self, val, **kwargs):
        return val

    def a(self, val, **kwargs):
        return val

a_signal = Signal(providing_args=["val"])
b_signal = Signal(providing_args=["val"])
c_signal = Signal(providing_args=["val"])
d_signal = Signal(providing_args=["val"], use_caching=True)


class DispatcherTests(unittest.TestCase):
    """Test suite for dispatcher (barely started)"""

    def _testIsClean(self, signal):
        """Assert that everything has been cleaned up automatically"""
        self.assertEqual(signal.receivers, [])

        # force cleanup just in case
        signal.receivers = []

    def testExact(self):
        a_signal.connect(receiver_1_arg, sender=self)
        expected = [(receiver_1_arg,"test")]
        result = a_signal.send(sender=self, val="test")
        self.assertEqual(result, expected)
        a_signal.disconnect(receiver_1_arg, sender=self)
        self._testIsClean(a_signal)

    def testIgnoredSender(self):
        a_signal.connect(receiver_1_arg)
        expected = [(receiver_1_arg,"test")]
        result = a_signal.send(sender=self, val="test")
        self.assertEqual(result, expected)
        a_signal.disconnect(receiver_1_arg)
        self._testIsClean(a_signal)

    def testGarbageCollected(self):
        a = Callable()
        a_signal.connect(a.a, sender=self)
        expected = []
        del a
        garbage_collect()
        result = a_signal.send(sender=self, val="test")
        self.assertEqual(result, expected)
        self._testIsClean(a_signal)

    def testCachedGarbagedCollected(self):
        """
        Make sure signal caching sender receivers don't prevent garbage
        collection of senders.
        """
        class sender(object):
            pass
        wref = weakref.ref(sender)
        d_signal.connect(receiver_1_arg)
        d_signal.send(sender, val='garbage')
        del sender
        garbage_collect()
        try:
            self.assertIsNone(wref())
        finally:
            # Disconnect after reference check since it flushes the tested cache.
            d_signal.disconnect(receiver_1_arg)

    def testMultipleRegistration(self):
        a = Callable()
        a_signal.connect(a)
        a_signal.connect(a)
        a_signal.connect(a)
        a_signal.connect(a)
        a_signal.connect(a)
        a_signal.connect(a)
        result = a_signal.send(sender=self, val="test")
        self.assertEqual(len(result), 1)
        self.assertEqual(len(a_signal.receivers), 1)
        del a
        del result
        garbage_collect()
        self._testIsClean(a_signal)

    def testUidRegistration(self):
        def uid_based_receiver_1(**kwargs):
            pass

        def uid_based_receiver_2(**kwargs):
            pass

        a_signal.connect(uid_based_receiver_1, dispatch_uid = "uid")
        a_signal.connect(uid_based_receiver_2, dispatch_uid = "uid")
        self.assertEqual(len(a_signal.receivers), 1)
        a_signal.disconnect(dispatch_uid = "uid")
        self._testIsClean(a_signal)

    def testRobust(self):
        """Test the sendRobust function"""
        def fails(val, **kwargs):
            raise ValueError('this')
        a_signal.connect(fails)
        result = a_signal.send_robust(sender=self, val="test")
        err = result[0][1]
        self.assertIsInstance(err, ValueError)
        self.assertEqual(err.args, ('this',))
        a_signal.disconnect(fails)
        self._testIsClean(a_signal)

    def testDisconnection(self):
        receiver_1 = Callable()
        receiver_2 = Callable()
        receiver_3 = Callable()
        a_signal.connect(receiver_1)
        a_signal.connect(receiver_2)
        a_signal.connect(receiver_3)
        a_signal.disconnect(receiver_1)
        del receiver_2
        garbage_collect()
        a_signal.disconnect(receiver_3)
        self._testIsClean(a_signal)

    def test_has_listeners(self):
        self.assertFalse(a_signal.has_listeners())
        self.assertFalse(a_signal.has_listeners(sender=object()))
        receiver_1 = Callable()
        a_signal.connect(receiver_1)
        self.assertTrue(a_signal.has_listeners())
        self.assertTrue(a_signal.has_listeners(sender=object()))
        a_signal.disconnect(receiver_1)
        self.assertFalse(a_signal.has_listeners())
        self.assertFalse(a_signal.has_listeners(sender=object()))


class ReceiverTestCase(unittest.TestCase):
    """
    Test suite for receiver.

    """
    def testReceiverSingleSignal(self):
        @receiver(a_signal)
        def f(val, **kwargs):
            self.state = val
        self.state = False
        a_signal.send(sender=self, val=True)
        self.assertTrue(self.state)

    def testReceiverSignalList(self):
        @receiver([a_signal, b_signal, c_signal])
        def f(val, **kwargs):
            self.state.append(val)
        self.state = []
        a_signal.send(sender=self, val='a')
        c_signal.send(sender=self, val='c')
        b_signal.send(sender=self, val='b')
        self.assertIn('a', self.state)
        self.assertIn('b', self.state)
        self.assertIn('c', self.state)
