from oauth2.test import unittest
from mock import Mock
from oauth2.web import Response
from oauth2.web.wsgi import Request, Application
from oauth2 import Provider


class RequestTestCase(unittest.TestCase):
    def test_initialization_no_post_data(self):
        request_method = "TEST"
        query_string = "foo=bar&baz=buz"

        environment = {"REQUEST_METHOD": request_method,
                       "QUERY_STRING": query_string,
                       "PATH_INFO": "/"}

        request = Request(environment)

        self.assertEqual(request.method, request_method)
        self.assertEqual(request.query_params, {"foo": "bar", "baz": "buz"})
        self.assertEqual(request.query_string, query_string)
        self.assertEqual(request.post_params, {})

    def test_initialization_with_post_data(self):
        content_length = "42"
        request_method = "POST"
        query_string = ""
        content = "foo=bar&baz=buz".encode('utf-8')

        wsgi_input_mock = Mock(spec=["read"])
        wsgi_input_mock.read.return_value = content

        environment = {"CONTENT_LENGTH": content_length,
                       "CONTENT_TYPE": "application/x-www-form-urlencoded",
                       "REQUEST_METHOD": request_method,
                       "QUERY_STRING": query_string,
                       "PATH_INFO": "/",
                       "wsgi.input": wsgi_input_mock}

        request = Request(environment)

        wsgi_input_mock.read.assert_called_with(int(content_length))
        self.assertEqual(request.method, request_method)
        self.assertEqual(request.query_params, {})
        self.assertEqual(request.query_string, query_string)
        self.assertEqual(request.post_params, {"foo": "bar", "baz": "buz"})

    def test_get_param(self):
        request_method = "TEST"
        query_string = "foo=bar&baz=buz"

        environment = {"REQUEST_METHOD": request_method,
                       "QUERY_STRING": query_string,
                       "PATH_INFO": "/a-url"}

        request = Request(environment)

        result = request.get_param("foo")

        self.assertEqual(result, "bar")

        result_default = request.get_param("na")

        self.assertEqual(result_default, None)

    def test_post_param(self):
        content_length = "42"
        request_method = "POST"
        query_string = ""
        content = "foo=bar&baz=buz".encode('utf-8')

        wsgi_input_mock = Mock(spec=["read"])
        wsgi_input_mock.read.return_value = content

        environment = {"CONTENT_LENGTH": content_length,
                       "CONTENT_TYPE": "application/x-www-form-urlencoded",
                       "REQUEST_METHOD": request_method,
                       "QUERY_STRING": query_string,
                       "PATH_INFO": "/",
                       "wsgi.input": wsgi_input_mock}

        request = Request(environment)

        result = request.post_param("foo")

        self.assertEqual(result, "bar")

        result_default = request.post_param("na")

        self.assertEqual(result_default, None)

        wsgi_input_mock.read.assert_called_with(int(content_length))

    def test_header(self):
        environment = {"REQUEST_METHOD": "GET",
                       "QUERY_STRING": "",
                       "PATH_INFO": "/",
                       "HTTP_AUTHORIZATION": "Basic abcd"}

        request = Request(env=environment)

        self.assertEqual(request.header("authorization"), "Basic abcd")
        self.assertIsNone(request.header("unknown"))
        self.assertEqual(request.header("unknown", default=0), 0)


class ServerTestCase(unittest.TestCase):
    def test_call(self):
        body = "body"
        headers = {"header": "value"}
        path = "/authorize"
        status_code = 200
        http_code = "200 OK"

        environment = {"PATH_INFO": path, "myvar": "value"}

        request_mock = Mock(spec=Request)
        request_class_mock = Mock(return_value=request_mock)

        response_mock = Mock(spec=Response)
        response_mock.body = body
        response_mock.headers = headers
        response_mock.status_code = status_code

        provider_mock = Mock(spec=Provider)
        provider_mock.dispatch.return_value = response_mock

        start_response_mock = Mock()

        wsgi = Application(provider=provider_mock, authorize_uri=path,
                           request_class=request_class_mock,
                           env_vars=["myvar"])
        result = wsgi(environment, start_response_mock)

        request_class_mock.assert_called_with(environment)
        provider_mock.dispatch.assert_called_with(request_mock,
                                                  {"myvar": "value"})
        start_response_mock.assert_called_with(http_code,
                                               list(headers.items()))
        self.assertEqual(result, [body.encode('utf-8')])
