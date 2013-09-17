#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for requests_kerberos."""

from mock import Mock, patch
import requests
import kerberos
import requests_kerberos
import unittest

# kerberos.authClientInit() is called with the service name (HTTP@FQDN) and
# returns 1 and a kerberos context object on success. Returns -1 on failure.
clientInit_complete = Mock(return_value=(1, "CTX"))
clientInit_error = Mock(return_value=(-1, "CTX"))

# kerberos.authGSSClientStep() is called with the kerberos context object
# returned by authGSSClientInit and the negotiate auth token provided in the
# http response's www-authenticate header. It returns 0 or 1 on success. 0
# Indicates that authentication is progressing but not complete.
clientStep_complete = Mock(return_value=1)
clientStep_continue = Mock(return_value=0)
clientStep_error = Mock(return_value=-1)
clientStep_exception = Mock(side_effect=kerberos.GSSError)

# kerberos.authGSSCLientResponse() is called with the kerberos context which
# was initially returned by authGSSClientInit and had been mutated by a call by
# authGSSClientStep. It returns a string.
clientResponse = Mock(return_value="GSSRESPONSE")

# Note: we're not using the @mock.patch decorator:
# > My only word of warning is that in the past, the patch decorator hides
# > tests when using the standard unittest library.
# > -- sigmavirus24 in https://github.com/requests/requests-kerberos/issues/1



class KerberosTestCase(unittest.TestCase):

    def setUp(self):
        """Setup."""
        clientInit_complete.reset_mock()
        clientInit_error.reset_mock()
        clientStep_complete.reset_mock()
        clientStep_continue.reset_mock()
        clientStep_error.reset_mock()
        clientStep_exception.reset_mock()
        clientResponse.reset_mock()

    def tearDown(self):
        """Teardown."""
        pass

    def test_negotate_value_extraction(self):
        response = requests.Response()
        response.headers = {'www-authenticate': 'negotiate token'}
        self.assertEqual(
            requests_kerberos.kerberos_._negotiate_value(response),
            'token'
        )

    def test_negotate_value_extraction_none(self):
        response = requests.Response()
        response.headers = {}
        self.assertTrue(
            requests_kerberos.kerberos_._negotiate_value(response) is None
        )

    def test_generate_request_header(self):
        with patch.multiple('kerberos',
                            authGSSClientInit=clientInit_complete,
                            authGSSClientResponse=clientResponse,
                            authGSSClientStep=clientStep_continue):
            response = requests.Response()
            response.url = "http://www.example.org/"
            response.headers = {'www-authenticate': 'negotiate token'}
            auth = requests_kerberos.HTTPKerberosAuth()
            self.assertEqual(
                auth.generate_request_header(response),
                "Negotiate GSSRESPONSE"
            )
            clientInit_complete.assert_called_with("HTTP@www.example.org")
            clientStep_continue.assert_called_with("CTX", "token")
            clientResponse.assert_called_with("CTX")

    def test_generate_request_header_init_error(self):
        with patch.multiple('kerberos',
                            authGSSClientInit=clientInit_error,
                            authGSSClientResponse=clientResponse,
                            authGSSClientStep=clientStep_continue):
            response = requests.Response()
            response.url = "http://www.example.org/"
            response.headers = {'www-authenticate': 'negotiate token'}
            auth = requests_kerberos.HTTPKerberosAuth()
            self.assertEqual(
                auth.generate_request_header(response),
                None
            )
            clientInit_error.assert_called_with("HTTP@www.example.org")
            self.assertFalse(clientStep_continue.called)
            self.assertFalse(clientResponse.called)

    def test_generate_request_header_step_error(self):
        with patch.multiple('kerberos',
                            authGSSClientInit=clientInit_complete,
                            authGSSClientResponse=clientResponse,
                            authGSSClientStep=clientStep_error):
            response = requests.Response()
            response.url = "http://www.example.org/"
            response.headers = {'www-authenticate': 'negotiate token'}
            auth = requests_kerberos.HTTPKerberosAuth()
            self.assertEqual(
                auth.generate_request_header(response),
                None
            )
            clientInit_complete.assert_called_with("HTTP@www.example.org")
            clientStep_error.assert_called_with("CTX", "token")
            self.assertFalse(clientResponse.called)

    def test_authenticate_user(self):
        with patch.multiple('kerberos',
                            authGSSClientInit=clientInit_complete,
                            authGSSClientResponse=clientResponse,
                            authGSSClientStep=clientStep_continue):

            response_ok = requests.Response()
            response_ok.url = "http://www.example.org/"
            response_ok.status_code = 200
            response_ok.headers = {'www-authenticate': 'negotiate servertoken'}

            connection = Mock()
            connection.send = Mock(return_value=response_ok)

            raw = Mock()
            raw.release_conn = Mock(return_value=None)

            request = requests.Request()
            response = requests.Response()
            response.request = request
            response.url = "http://www.example.org/"
            response.headers = {'www-authenticate': 'negotiate token'}
            response.status_code = 401
            response.connection = connection
            response._content = ""
            response.raw = raw
            auth = requests_kerberos.HTTPKerberosAuth()
            r = auth.authenticate_user(response)

            self.assertTrue(response in r.history)
            self.assertEqual(r, response_ok)
            self.assertEqual(request.headers['Authorization'], 'Negotiate GSSRESPONSE')
            connection.send.assert_called_with(request)
            raw.release_conn.assert_called_with()
            clientInit_complete.assert_called_with("HTTP@www.example.org")
            clientStep_continue.assert_called_with("CTX", "token")
            clientResponse.assert_called_with("CTX")


    def test_handle_401(self):
        with patch.multiple('kerberos',
                            authGSSClientInit=clientInit_complete,
                            authGSSClientResponse=clientResponse,
                            authGSSClientStep=clientStep_continue):

            response_ok = requests.Response()
            response_ok.url = "http://www.example.org/"
            response_ok.status_code = 200
            response_ok.headers = {'www-authenticate': 'negotiate servertoken'}

            connection = Mock()
            connection.send = Mock(return_value=response_ok)

            raw = Mock()
            raw.release_conn = Mock(return_value=None)

            request = requests.Request()
            response = requests.Response()
            response.request = request
            response.url = "http://www.example.org/"
            response.headers = {'www-authenticate': 'negotiate token'}
            response.status_code = 401
            response.connection = connection
            response._content = ""
            response.raw = raw
            auth = requests_kerberos.HTTPKerberosAuth()
            r = auth.handle_401(response)

            self.assertTrue(response in r.history)
            self.assertEqual(r, response_ok)
            self.assertEqual(request.headers['Authorization'], 'Negotiate GSSRESPONSE')
            connection.send.assert_called_with(request)
            raw.release_conn.assert_called_with()
            clientInit_complete.assert_called_with("HTTP@www.example.org")
            clientStep_continue.assert_called_with("CTX", "token")
            clientResponse.assert_called_with("CTX")

    def test_authenticate_server(self):
        with patch.multiple('kerberos', authGSSClientStep=clientStep_complete):

            response_ok = requests.Response()
            response_ok.url = "http://www.example.org/"
            response_ok.status_code = 200
            response_ok.headers = {'www-authenticate': 'negotiate servertoken',
                                   'authorization': 'Negotiate GSSRESPONSE'
            }

            auth = requests_kerberos.HTTPKerberosAuth()
            auth.context = {"www.example.org": "CTX"}
            result = auth.authenticate_server(response_ok)

            self.assertTrue(result)
            clientStep_complete.assert_called_with("CTX", "servertoken")

    def test_handle_other(self):
        with patch('kerberos.authGSSClientStep', clientStep_complete):

            response_ok = requests.Response()
            response_ok.url = "http://www.example.org/"
            response_ok.status_code = 200
            response_ok.headers = {'www-authenticate': 'negotiate servertoken',
                                   'authorization': 'Negotiate GSSRESPONSE'
            }

            auth = requests_kerberos.HTTPKerberosAuth()
            auth.context = {"www.example.org": "CTX"}

            r = auth.handle_other(response_ok)

            self.assertEqual(r, response_ok)
            clientStep_complete.assert_called_with("CTX", "servertoken")

    def test_handle_response_200(self):
        with patch('kerberos.authGSSClientStep', clientStep_complete):

            response_ok = requests.Response()
            response_ok.url = "http://www.example.org/"
            response_ok.status_code = 200
            response_ok.headers = {'www-authenticate': 'negotiate servertoken',
                                   'authorization': 'Negotiate GSSRESPONSE'
            }

            auth = requests_kerberos.HTTPKerberosAuth()
            auth.context = {"www.example.org": "CTX"}

            r = auth.handle_response(response_ok)

            self.assertEqual(r, response_ok)
            clientStep_complete.assert_called_with("CTX", "servertoken")

    def test_handle_response_200_mutual_auth_required_failure(self):
        with patch('kerberos.authGSSClientStep', clientStep_error):

            response_ok = requests.Response()
            response_ok.url = "http://www.example.org/"
            response_ok.status_code = 200
            response_ok.headers = {}

            auth = requests_kerberos.HTTPKerberosAuth()
            auth.context = {"www.example.org": "CTX"}

            self.assertRaises(requests_kerberos.MutualAuthenticationError,
                              auth.handle_response,
                              response_ok)

            self.assertFalse(clientStep_error.called)

    def test_handle_response_200_mutual_auth_required_failure_2(self):
        with patch('kerberos.authGSSClientStep', clientStep_exception):

            response_ok = requests.Response()
            response_ok.url = "http://www.example.org/"
            response_ok.status_code = 200
            response_ok.headers = {'www-authenticate': 'negotiate servertoken',
                                   'authorization': 'Negotiate GSSRESPONSE'
            }

            auth = requests_kerberos.HTTPKerberosAuth()
            auth.context = {"www.example.org": "CTX"}

            self.assertRaises(requests_kerberos.MutualAuthenticationError,
                              auth.handle_response,
                              response_ok)

            clientStep_exception.assert_called_with("CTX", "servertoken")

    def test_handle_response_200_mutual_auth_optional_hard_failure(self):
        with patch('kerberos.authGSSClientStep', clientStep_error):

            response_ok = requests.Response()
            response_ok.url = "http://www.example.org/"
            response_ok.status_code = 200
            response_ok.headers = {'www-authenticate': 'negotiate servertoken',
                                   'authorization': 'Negotiate GSSRESPONSE'
            }

            auth = requests_kerberos.HTTPKerberosAuth(requests_kerberos.OPTIONAL)
            auth.context = {"www.example.org": "CTX"}


            self.assertRaises(requests_kerberos.MutualAuthenticationError,
                              auth.handle_response,
                              response_ok)

            clientStep_error.assert_called_with("CTX", "servertoken")


    def test_handle_response_200_mutual_auth_optional_soft_failure(self):
        with patch('kerberos.authGSSClientStep', clientStep_error):

            response_ok = requests.Response()
            response_ok.url = "http://www.example.org/"
            response_ok.status_code = 200

            auth = requests_kerberos.HTTPKerberosAuth(requests_kerberos.OPTIONAL)
            auth.context = {"www.example.org": "CTX"}

            r = auth.handle_response(response_ok)

            self.assertEqual(r, response_ok)

            self.assertFalse(clientStep_error.called)

    def test_handle_response_500_mutual_auth_required_failure(self):
        with patch('kerberos.authGSSClientStep', clientStep_error):

            response_500 = requests.Response()
            response_500.url = "http://www.example.org/"
            response_500.status_code = 500
            response_500.headers = {}
            response_500.request = "REQUEST"
            response_500.connection = "CONNECTION"
            response_500._content = "CONTENT"
            response_500.encoding = "ENCODING"
            response_500.raw = "RAW"
            response_500.cookies = "COOKIES"

            auth = requests_kerberos.HTTPKerberosAuth()
            auth.context = {"www.example.org": "CTX"}

            r = auth.handle_response(response_500)

            self.assertNotEqual(r, response_500)
            self.assertNotEqual(r.headers, response_500.headers)
            self.assertEqual(r.status_code, response_500.status_code)
            self.assertEqual(r.encoding, response_500.encoding)
            self.assertEqual(r.raw, response_500.raw)
            self.assertEqual(r.url, response_500.url)
            self.assertEqual(r.reason, response_500.reason)
            self.assertEqual(r.connection, response_500.connection)
            self.assertEqual(r.content, b'')
            self.assertNotEqual(r.cookies, response_500.cookies)

            self.assertFalse(clientStep_error.called)

    def test_handle_response_500_mutual_auth_optional_failure(self):
        with patch('kerberos.authGSSClientStep', clientStep_error):

            response_500 = requests.Response()
            response_500.url = "http://www.example.org/"
            response_500.status_code = 500
            response_500.headers = {}
            response_500.request = "REQUEST"
            response_500.connection = "CONNECTION"
            response_500._content = "CONTENT"
            response_500.encoding = "ENCODING"
            response_500.raw = "RAW"
            response_500.cookies = "COOKIES"

            auth = requests_kerberos.HTTPKerberosAuth(requests_kerberos.OPTIONAL)
            auth.context = {"www.example.org": "CTX"}

            r = auth.handle_response(response_500)

            self.assertEqual(r, response_500)

            self.assertFalse(clientStep_error.called)


    def test_handle_response_401(self):
        with patch.multiple('kerberos',
                            authGSSClientInit=clientInit_complete,
                            authGSSClientResponse=clientResponse,
                            authGSSClientStep=clientStep_continue):

            response_ok = requests.Response()
            response_ok.url = "http://www.example.org/"
            response_ok.status_code = 200
            response_ok.headers = {'www-authenticate': 'negotiate servertoken'}

            connection = Mock()
            connection.send = Mock(return_value=response_ok)

            raw = Mock()
            raw.release_conn = Mock(return_value=None)

            request = requests.Request()
            response = requests.Response()
            response.request = request
            response.url = "http://www.example.org/"
            response.headers = {'www-authenticate': 'negotiate token'}
            response.status_code = 401
            response.connection = connection
            response._content = ""
            response.raw = raw
            auth = requests_kerberos.HTTPKerberosAuth()
            r = auth.handle_response(response)

            self.assertTrue(response in r.history)
            self.assertEqual(r, response_ok)
            self.assertEqual(request.headers['Authorization'], 'Negotiate GSSRESPONSE')
            connection.send.assert_called_with(request)
            raw.release_conn.assert_called_with()
            clientInit_complete.assert_called_with("HTTP@www.example.org")
            clientStep_continue.assert_called_with("CTX", "token")
            clientResponse.assert_called_with("CTX")

if __name__ == '__main__':
    unittest.main()
