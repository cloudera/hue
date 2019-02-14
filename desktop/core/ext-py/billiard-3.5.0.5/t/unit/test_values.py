from __future__ import absolute_import
import pytest

from billiard import Value, RawValue, Lock, Process


class test_values:

    codes_values = [
        ('i', 4343, 24234),
        ('d', 3.625, -4.25),
        ('h', -232, 234),
        ('c', 'x'.encode('latin'), 'y'.encode('latin'))
        ]

    def test_issue_229(self):
        """Test fix for issue #229"""

        a = Value('i', 0)
        b = Value('i', 0)

        a.value = 5
        assert a.value == 5
        assert b.value == 0

    @classmethod
    def _test(cls, values):
        for sv, cv in zip(values, cls.codes_values):
            sv.value = cv[2]

    def test_value(self, raw=False):
        if raw:
            values = [RawValue(code, value)
                      for code, value, _ in self.codes_values]
        else:
            values = [Value(code, value)
                      for code, value, _ in self.codes_values]

        for sv, cv in zip(values, self.codes_values):
            assert sv.value == cv[1]

        proc = Process(target=self._test, args=(values,))
        proc.daemon = True
        proc.start()
        proc.join()

        for sv, cv in zip(values, self.codes_values):
            assert sv.value == cv[2]

    def test_rawvalue(self):
        self.test_value(raw=True)

    def test_getobj_getlock(self):
        val1 = Value('i', 5)
        lock1 = val1.get_lock()
        obj1 = val1.get_obj()

        val2 = Value('i', 5, lock=None)
        lock2 = val2.get_lock()
        obj2 = val2.get_obj()

        lock = Lock()
        val3 = Value('i', 5, lock=lock)
        lock3 = val3.get_lock()
        obj3 = val3.get_obj()
        assert lock == lock3

        arr4 = Value('i', 5, lock=False)
        assert not hasattr(arr4, 'get_lock')
        assert not hasattr(arr4, 'get_obj')

        with pytest.raises(AttributeError):
            Value('i', 5, lock='navalue')

        arr5 = RawValue('i', 5)
        assert not hasattr(arr5, 'get_lock')
        assert not hasattr(arr5, 'get_obj')
