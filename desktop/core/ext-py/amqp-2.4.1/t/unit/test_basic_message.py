from __future__ import absolute_import, unicode_literals

from case import Mock

from amqp.basic_message import Message


class test_Message:

    def test_message(self):
        m = Message(
            'foo',
            channel=Mock(name='channel'),
            application_headers={'h': 'v'},
        )
        m.delivery_info = {'delivery_tag': '1234'}
        assert m.body == 'foo'
        assert m.channel
        assert m.headers == {'h': 'v'}
        assert m.delivery_tag == '1234'
