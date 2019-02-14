from __future__ import absolute_import, unicode_literals

from datetime import datetime
from decimal import Decimal
from math import ceil

import pytest

from amqp.basic_message import Message
from amqp.exceptions import FrameSyntaxError
from amqp.platform import pack
from amqp.serialization import GenericContent, _read_item, dumps, loads


class _ANY(object):

    def __eq__(self, other):
        return other is not None

    def __ne__(self, other):
        return other is None


class test_serialization:

    @pytest.mark.parametrize('descr,frame,expected,cast', [
        ('S', b's8thequick', 'thequick', None),
        ('x', b'x\x00\x00\x00\x09thequick\xffIGNORED', b'thequick\xff', None),
        ('b', b'b' + pack('>B', True), True, None),
        ('B', b'B' + pack('>b', 123), 123, None),
        ('U', b'U' + pack('>h', -321), -321, None),
        ('u', b'u' + pack('>H', 321), 321, None),
        ('i', b'i' + pack('>I', 1234), 1234, None),
        ('L', b'L' + pack('>q', -32451), -32451, None),
        ('l', b'l' + pack('>Q', 32451), 32451, None),
        ('f', b'f' + pack('>f', 33.3), 34.0, ceil),
    ])
    def test_read_item(self, descr, frame, expected, cast):
        actual = _read_item(frame)[0]
        actual = cast(actual) if cast else actual
        assert actual == expected

    def test_read_item_V(self):
        assert _read_item(b'V')[0] is None

    def test_roundtrip(self):
        format = b'bobBlLbsbSTx'
        x = dumps(format, [
            True, 32, False, 3415, 4513134, 13241923419,
            True, b'thequickbrownfox', False, 'jumpsoverthelazydog',
            datetime(2015, 3, 13, 10, 23),
            b'thequick\xff'
        ])
        y = loads(format, x)
        assert [
            True, 32, False, 3415, 4513134, 13241923419,
            True, 'thequickbrownfox', False, 'jumpsoverthelazydog',
            datetime(2015, 3, 13, 10, 23), b'thequick\xff'
        ] == y[0]

    def test_int_boundaries(self):
        format = b'F'
        x = dumps(format, [
            {'a': -2147483649, 'b': 2147483648},  # celery/celery#3121
        ])
        y = loads(format, x)
        assert y[0] == [{
            'a': -2147483649, 'b': 2147483648,  # celery/celery#3121
        }]

    def test_loads_unknown_type(self):
        with pytest.raises(FrameSyntaxError):
            loads('y', 'asdsad')

    def test_float(self):
        assert (int(loads(b'fb', dumps(b'fb', [32.31, False]))[0][0] * 100) ==
                3231)

    def test_table(self):
        table = {'foo': 32, 'bar': 'baz', 'nil': None}
        assert loads(b'F', dumps(b'F', [table]))[0][0] == table

    def test_array(self):
        array = [
            'A', 1, True, 33.3,
            Decimal('55.5'), Decimal('-3.4'),
            datetime(2015, 3, 13, 10, 23),
            {'quick': 'fox', 'amount': 1},
            [3, 'hens'],
            None,
        ]
        expected = list(array)
        expected[6] = _ANY()

        assert expected == loads('A', dumps('A', [array]))[0][0]

    def test_array_unknown_type(self):
        with pytest.raises(FrameSyntaxError):
            dumps('A', [[object()]])


class test_GenericContent:

    @pytest.fixture(autouse=True)
    def setup_content(self):
        self.g = GenericContent()

    def test_getattr(self):
        self.g.properties['foo'] = 30
        with pytest.raises(AttributeError):
            self.g.__setstate__
        assert self.g.foo == 30
        with pytest.raises(AttributeError):
            self.g.bar

    def test_load_properties(self):
        m = Message()
        m.properties = {
            'content_type': 'application/json',
            'content_encoding': 'utf-8',
            'application_headers': {
                'foo': 1,
                'id': 'id#1',
            },
            'delivery_mode': 1,
            'priority': 255,
            'correlation_id': 'df31-142f-34fd-g42d',
            'reply_to': 'cosmo',
            'expiration': '2015-12-23',
            'message_id': '3312',
            'timestamp': 3912491234,
            'type': 'generic',
            'user_id': 'george',
            'app_id': 'vandelay',
            'cluster_id': 'NYC',
        }
        s = m._serialize_properties()
        m2 = Message()
        m2._load_properties(m2.CLASS_ID, s)
        assert m2.properties == m.properties

    def test_load_properties__some_missing(self):
        m = Message()
        m.properties = {
            'content_type': 'application/json',
            'content_encoding': 'utf-8',
            'delivery_mode': 1,
            'correlation_id': 'df31-142f-34fd-g42d',
            'reply_to': 'cosmo',
            'expiration': '2015-12-23',
            'message_id': '3312',
            'type': None,
            'app_id': None,
            'cluster_id': None,
        }
        s = m._serialize_properties()
        m2 = Message()
        m2._load_properties(m2.CLASS_ID, s)

    def test_inbound_header(self):
        m = Message()
        m.properties = {
            'content_type': 'application/json',
            'content_encoding': 'utf-8',
        }
        body = 'the quick brown fox'
        buf = b'\0' * 30 + pack('>HxxQ', m.CLASS_ID, len(body))
        buf += m._serialize_properties()
        assert m.inbound_header(buf, offset=30) == 42
        assert m.body_size == len(body)
        assert m.properties['content_type'] == 'application/json'
        assert not m.ready

    def test_inbound_header__empty_body(self):
        m = Message()
        m.properties = {}
        buf = pack('>HxxQ', m.CLASS_ID, 0)
        buf += m._serialize_properties()
        assert m.inbound_header(buf, offset=0) == 12
        assert m.ready

    def test_inbound_body(self):
        m = Message()
        m.body_size = 16
        m.body_received = 8
        m._pending_chunks = [b'the', b'quick']
        m.inbound_body(b'brown')
        assert not m.ready
        m.inbound_body(b'fox')
        assert m.ready
        assert m.body == b'thequickbrownfox'

    def test_inbound_body__no_chunks(self):
        m = Message()
        m.body_size = 16
        m.inbound_body('thequickbrownfox')
        assert m.ready
