from __future__ import absolute_import, unicode_literals

from vine.abstract import Thenable
from vine.promises import promise


class CanThen(object):

    def then(self, x, y):
        pass


class CannotThen(object):
    pass


class test_Thenable:

    def test_isa(self):
        assert isinstance(CanThen(), Thenable)
        assert not isinstance(CannotThen(), Thenable)

    def test_promise(self):
        assert isinstance(promise(lambda x: x), Thenable)
