# Copyright (c) 2016 Uber Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import tornado.web
import opentracing
import tornado.ioloop
import tornado.httpclient
from tornado.web import asynchronous
from jaeger_client import Tracer, ConstSampler
from jaeger_client.reporter import NullReporter
import crossdock.server.constants as constants
import crossdock.server.serializer as serializer
from crossdock.server.endtoend import EndToEndHandler
from opentracing_instrumentation import http_client, http_server, get_current_span, request_context
from opentracing_instrumentation.client_hooks import tornado_http
import opentracing.ext.tags as ext_tags
from crossdock.thrift_gen.tracetest.ttypes import ObservedSpan, TraceResponse, Transport, \
    JoinTraceRequest

from tchannel import TChannel, thrift
from crossdock.server.thriftrw_serializer import trace_response_to_thriftrw, \
    join_trace_request_to_thriftrw

DefaultClientPortHTTP = 8080
DefaultServerPortHTTP = 8081
DefaultServerPortTChannel = 8082


tracer = Tracer(
    service_name='python',
    reporter=NullReporter(),
    sampler=ConstSampler(decision=True))
opentracing.tracer = tracer


idl_path = 'idl/thrift/crossdock/tracetest.thrift'
thrift_services = {}


def get_thrift_service(service_name):
    if service_name in thrift_services:
        return thrift_services[service_name]
    thrift_service = thrift.load(path=idl_path, service=service_name)
    thrift_services[service_name] = thrift_service
    return thrift_service


def serve():
    """main entry point"""
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info('Python Tornado Crossdock Server Running ...')
    server = Server(DefaultServerPortTChannel)
    endtoend_handler = EndToEndHandler()
    app = make_app(server, endtoend_handler)
    app.listen(DefaultClientPortHTTP)
    app.listen(DefaultServerPortHTTP)
    server.tchannel.listen()
    tornado.ioloop.IOLoop.current().start()


# Tornado Stuff
class MainHandler(tornado.web.RequestHandler):
    def initialize(self, server=None, method=None):
        self.server = server
        self.method = method

    @asynchronous
    def get(self):
        if self.server and self.method:
            self.method(self.server, self.request, self)
        else:
            self.finish()

    @asynchronous
    def post(self):
        if self.server and self.method:
            self.method(self.server, self.request, self)
        else:
            self.finish()

    def head(self):
        pass


def make_app(server, endtoend_handler):
    return tornado.web.Application(
        [
            (r'/', MainHandler),
            (r'/start_trace', MainHandler, (dict(server=server, method=Server.start_trace))),
            (r'/join_trace', MainHandler, (dict(server=server, method=Server.join_trace))),
            (r'/create_traces', MainHandler, (dict(server=endtoend_handler,
                                                   method=EndToEndHandler.generate_traces))),
        ], debug=True, autoreload=False)


# HTTP Tracing Stuff
class UnknownTransportException(Exception):
    pass


def get_observed_span(span):
    return ObservedSpan(
        traceId='%x' % span.trace_id,
        sampled=span.is_sampled(),
        baggage=span.get_baggage_item(constants.baggage_key)
    )


class Server(object):
    def __init__(self, port):
        self.tracer = opentracing.tracer
        self.tchannel = self.make_tchannel(port)

    def make_tchannel(self, port):
        tchannel = TChannel('python', hostport='localhost:%d' % port, trace=True)

        service = get_thrift_service(service_name='python')

        @tchannel.thrift.register(service.TracedService, method='joinTrace')
        @tornado.gen.coroutine
        def join_trace(request):
            join_trace_request = request.body.request or None
            logging.info('TChannel join_trace request: %s', join_trace_request)
            response = yield self.prepare_response(get_current_span(),
                                                   join_trace_request.downstream)
            logging.info('TChannel join_trace response: %s', response)
            raise tornado.gen.Return(trace_response_to_thriftrw(service, response))

        return tchannel

    @tornado.gen.coroutine
    def start_trace(self, request, response_writer):
        start_trace_req = serializer.start_trace_request_from_json(request.body)
        logging.info('HTTP start_trace request: %s', start_trace_req)

        def update_span(span):
            span.set_baggage_item(constants.baggage_key, start_trace_req.baggage)
            span.set_tag(ext_tags.SAMPLING_PRIORITY, start_trace_req.sampled)

        response = yield self.prepare_response(self.get_span(request, update_span),
                                               start_trace_req.downstream)
        logging.info('HTTP start_trace response: %s', response)
        response_writer.write(serializer.traced_service_object_to_json(response))
        response_writer.finish()

    @tornado.gen.coroutine
    def join_trace(self, request, response_writer):
        join_trace_request = serializer.join_trace_request_from_json(request.body)
        logging.info('HTTP join_trace request: %s', join_trace_request)

        response = yield self.prepare_response(self.get_span(request, None),
                                               join_trace_request.downstream)
        logging.info('HTTP join_trace response: %s', response)
        response_writer.write(serializer.traced_service_object_to_json(response))
        response_writer.finish()

    def get_span(self, http_request, update_span_func):
        span = http_server.before_request(http_server.TornadoRequestWrapper(request=http_request),
                                          self.tracer)
        if update_span_func:
            update_span_func(span)

        return span

    @tornado.gen.coroutine
    def prepare_response(self, span, downstream):
        observed_span = get_observed_span(span)
        trace_response = TraceResponse(span=observed_span, notImplementedError='')

        if downstream:
            with request_context.span_in_stack_context(span):
                future = self.call_downstream(span, downstream)
            downstream_trace_resp = yield future
            trace_response.downstream = downstream_trace_resp

        raise tornado.gen.Return(trace_response)

    @tornado.gen.coroutine
    def call_downstream(self, span, downstream):
        if downstream.transport == Transport.HTTP:
            downstream_trace_resp = yield self.call_downstream_http(span, downstream)
        elif downstream.transport == Transport.TCHANNEL:
            downstream_trace_resp = yield self.call_downstream_tchannel(downstream)
        else:
            raise UnknownTransportException('%s' % downstream.transport)
        raise tornado.gen.Return(downstream_trace_resp)

    @tornado.gen.coroutine
    def call_downstream_http(self, span, downstream):
        url = 'http://%s:%s/join_trace' % (downstream.host, downstream.port)
        body = serializer.join_trace_request_to_json(downstream.downstream, downstream.serverRole)

        req = tornado.httpclient.HTTPRequest(url=url, method='POST',
                                             headers={'Content-Type': 'application/json'},
                                             body=body)
        http_client.before_http_request(tornado_http.TornadoRequestWrapper(request=req),
                                        lambda: span)
        client = tornado.httpclient.AsyncHTTPClient()
        http_result = yield client.fetch(req)

        raise tornado.gen.Return(serializer.traceresponse_from_json(http_result.body))

    @tornado.gen.coroutine
    def call_downstream_tchannel(self, downstream):
        downstream_service = get_thrift_service(downstream.serviceName)

        jtr = JoinTraceRequest(downstream.serverRole, downstream.downstream)
        jtr = join_trace_request_to_thriftrw(downstream_service, jtr)

        hostport = '%s:%s' % (downstream.host, downstream.port)
        thrift_result = yield self.tchannel.thrift(downstream_service.TracedService.joinTrace(jtr),
                                                   hostport=hostport)
        raise tornado.gen.Return(thrift_result.body)
