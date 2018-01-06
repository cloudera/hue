import warnings

from eventlet.support import six
from eventlet.green import httplib
from eventlet.zipkin import api


# see https://twitter.github.io/zipkin/Instrumenting.html
HDR_TRACE_ID = 'X-B3-TraceId'
HDR_SPAN_ID = 'X-B3-SpanId'
HDR_PARENT_SPAN_ID = 'X-B3-ParentSpanId'
HDR_SAMPLED = 'X-B3-Sampled'


if six.PY2:
    __org_endheaders__ = httplib.HTTPConnection.endheaders
    __org_begin__ = httplib.HTTPResponse.begin

    def _patched_endheaders(self):
        if api.is_tracing():
            trace_data = api.get_trace_data()
            new_span_id = api.generate_span_id()
            self.putheader(HDR_TRACE_ID, hex_str(trace_data.trace_id))
            self.putheader(HDR_SPAN_ID, hex_str(new_span_id))
            self.putheader(HDR_PARENT_SPAN_ID, hex_str(trace_data.span_id))
            self.putheader(HDR_SAMPLED, int(trace_data.sampled))
            api.put_annotation('Client Send')

        __org_endheaders__(self)

    def _patched_begin(self):
        __org_begin__(self)

        if api.is_tracing():
            api.put_annotation('Client Recv (%s)' % self.status)


def patch():
    if six.PY2:
        httplib.HTTPConnection.endheaders = _patched_endheaders
        httplib.HTTPResponse.begin = _patched_begin
    if six.PY3:
        warnings.warn("Since current Python thrift release \
        doesn't support Python 3, eventlet.zipkin.http \
        doesn't also support Python 3 (http.client)")


def unpatch():
    if six.PY2:
        httplib.HTTPConnection.endheaders = __org_endheaders__
        httplib.HTTPResponse.begin = __org_begin__
    if six.PY3:
        pass


def hex_str(n):
    """
    Thrift uses a binary representation of trace and span ids
    HTTP headers use a hexadecimal representation of the same
    """
    return '%0.16x' % (n,)
