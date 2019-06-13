from __future__ import absolute_import, unicode_literals

import contextlib
import socket
import sys
from io import BytesIO

import pytest
from case import Mock, call, patch

from amqp import sasl
from amqp.serialization import _write_table


class test_SASL:
    def test_sasl_notimplemented(self):
        mech = sasl.SASL()
        with pytest.raises(NotImplementedError):
            mech.mechanism
        with pytest.raises(NotImplementedError):
            mech.start(None)

    def test_plain(self):
        username, password = 'foo', 'bar'
        mech = sasl.PLAIN(username, password)
        response = mech.start(None)
        assert isinstance(response, bytes)
        assert response.split(b'\0') == \
            [b'', username.encode('utf-8'), password.encode('utf-8')]

    def test_plain_no_password(self):
        username, password = 'foo', None
        mech = sasl.PLAIN(username, password)
        response = mech.start(None)
        assert response == NotImplemented

    def test_amqplain(self):
        username, password = 'foo', 'bar'
        mech = sasl.AMQPLAIN(username, password)
        response = mech.start(None)
        assert isinstance(response, bytes)
        login_response = BytesIO()
        _write_table({b'LOGIN': username, b'PASSWORD': password},
                     login_response.write, [])
        expected_response = login_response.getvalue()[4:]
        assert response == expected_response

    def test_amqplain_no_password(self):
        username, password = 'foo', None
        mech = sasl.AMQPLAIN(username, password)
        response = mech.start(None)
        assert response == NotImplemented

    def test_gssapi_missing(self):
        gssapi = sys.modules.pop('gssapi', None)
        GSSAPI = sasl._get_gssapi_mechanism()
        with pytest.raises(NotImplementedError):
            GSSAPI()
        if gssapi is not None:
            sys.modules['gssapi'] = gssapi

    @contextlib.contextmanager
    def fake_gssapi(self):
        orig_gssapi = sys.modules.pop('gssapi', None)
        orig_gssapi_raw = sys.modules.pop('gssapi.raw', None)
        orig_gssapi_raw_misc = sys.modules.pop('gssapi.raw.misc', None)
        gssapi = sys.modules['gssapi'] = Mock()
        sys.modules['gssapi.raw'] = gssapi.raw
        sys.modules['gssapi.raw.misc'] = gssapi.raw.misc

        class GSSError(Exception):
            pass

        gssapi.raw.misc.GSSError = GSSError
        try:
            yield gssapi
        finally:
            if orig_gssapi is None:
                del sys.modules['gssapi']
            else:
                sys.modules['gssapi'] = orig_gssapi
            if orig_gssapi_raw is None:
                del sys.modules['gssapi.raw']
            else:
                sys.modules['gssapi.raw'] = orig_gssapi_raw
            if orig_gssapi_raw_misc is None:
                del sys.modules['gssapi.raw.misc']
            else:
                sys.modules['gssapi.raw.misc'] = orig_gssapi_raw_misc

    def test_gssapi_rdns(self):
        with self.fake_gssapi() as gssapi, \
                patch('socket.gethostbyaddr') as gethostbyaddr:
            connection = Mock()
            connection.transport.sock.getpeername.return_value = ('192.0.2.0',
                                                                  5672)
            connection.transport.sock.family = socket.AF_INET
            gethostbyaddr.return_value = ('broker.example.org', (), ())
            GSSAPI = sasl._get_gssapi_mechanism()

            mech = GSSAPI(rdns=True)
            mech.start(connection)

            connection.transport.sock.getpeername.assert_called()
            gethostbyaddr.assert_called_with('192.0.2.0')
            gssapi.Name.assert_called_with(b'amqp@broker.example.org',
                                           gssapi.NameType.hostbased_service)

    def test_gssapi_no_rdns(self):
        with self.fake_gssapi() as gssapi:
            connection = Mock()
            connection.transport.host = 'broker.example.org'
            GSSAPI = sasl._get_gssapi_mechanism()

            mech = GSSAPI()
            mech.start(connection)

            gssapi.Name.assert_called_with(b'amqp@broker.example.org',
                                           gssapi.NameType.hostbased_service)

    def test_gssapi_step_without_client_name(self):
        with self.fake_gssapi() as gssapi:
            context = Mock()
            context.step.return_value = b'secrets'
            name = Mock()
            gssapi.SecurityContext.return_value = context
            gssapi.Name.return_value = name
            connection = Mock()
            connection.transport.host = 'broker.example.org'
            GSSAPI = sasl._get_gssapi_mechanism()

            mech = GSSAPI()
            response = mech.start(connection)

            gssapi.SecurityContext.assert_called_with(name=name, creds=None)
            context.step.assert_called_with(None)
            assert response == b'secrets'

    def test_gssapi_step_with_client_name(self):
        with self.fake_gssapi() as gssapi:
            context = Mock()
            context.step.return_value = b'secrets'
            client_name, service_name, credentials = Mock(), Mock(), Mock()
            gssapi.SecurityContext.return_value = context
            gssapi.Credentials.return_value = credentials
            gssapi.Name.side_effect = [client_name, service_name]
            connection = Mock()
            connection.transport.host = 'broker.example.org'
            GSSAPI = sasl._get_gssapi_mechanism()

            mech = GSSAPI(client_name='amqp-client/client.example.org')
            response = mech.start(connection)
            gssapi.Name.assert_has_calls([
                call(b'amqp-client/client.example.org'),
                call(b'amqp@broker.example.org',
                     gssapi.NameType.hostbased_service)])
            gssapi.Credentials.assert_called_with(name=client_name)
            gssapi.SecurityContext.assert_called_with(name=service_name,
                                                      creds=credentials)
            context.step.assert_called_with(None)
            assert response == b'secrets'

    def test_external(self):
        mech = sasl.EXTERNAL()
        response = mech.start(None)
        assert isinstance(response, bytes)
        assert response == b''
