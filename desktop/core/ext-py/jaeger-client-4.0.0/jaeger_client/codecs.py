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

from __future__ import absolute_import

from opentracing import (
    InvalidCarrierException,
    SpanContextCorruptedException,
)
from .constants import (
    BAGGAGE_HEADER_KEY,
    BAGGAGE_HEADER_PREFIX,
    DEBUG_ID_HEADER_KEY,
    TRACE_ID_HEADER,
)
from .span_context import SpanContext
from .constants import SAMPLED_FLAG, DEBUG_FLAG

import six
from six.moves import urllib_parse


class Codec(object):
    def inject(self, span_context, carrier):
        raise NotImplementedError()

    def extract(self, carrier):
        raise NotImplementedError()


class TextCodec(Codec):
    def __init__(self,
                 url_encoding=False,
                 trace_id_header=TRACE_ID_HEADER,
                 baggage_header_prefix=BAGGAGE_HEADER_PREFIX,
                 debug_id_header=DEBUG_ID_HEADER_KEY,
                 baggage_header=BAGGAGE_HEADER_KEY):
        self.url_encoding = url_encoding
        self.trace_id_header = trace_id_header.lower().replace('_', '-')
        self.baggage_prefix = baggage_header_prefix.lower().replace('_', '-')
        self.debug_id_header = debug_id_header.lower().replace('_', '-')
        self.baggage_header = baggage_header
        self.prefix_length = len(baggage_header_prefix)

    def inject(self, span_context, carrier):
        if not isinstance(carrier, dict):
            raise InvalidCarrierException('carrier not a collection')
        # Note: we do not url-encode the trace ID because the ':' separator
        # is not a problem for HTTP header values
        carrier[self.trace_id_header] = span_context_to_string(
            trace_id=span_context.trace_id, span_id=span_context.span_id,
            parent_id=span_context.parent_id, flags=span_context.flags)
        baggage = span_context.baggage
        if baggage:
            for key, value in six.iteritems(baggage):
                encoded_key = key
                if self.url_encoding:
                    if six.PY2 and isinstance(value, six.text_type):
                        encoded_value = urllib_parse.quote(value.encode('utf-8'))
                    else:
                        encoded_value = urllib_parse.quote(value)
                    # we assume that self.url_encoding means we are injecting
                    # into HTTP headers. httplib does not like unicode strings
                    # so we convert the key to utf-8. The URL-encoded value is
                    # already a plain string.
                    if six.PY2 and isinstance(key, six.text_type):
                        encoded_key = key.encode('utf-8')
                else:
                    if six.PY3 and isinstance(value, six.binary_type):
                        encoded_value = str(value, 'utf-8')
                    else:
                        encoded_value = value
                if six.PY3 and isinstance(key, six.binary_type):
                    encoded_key = str(key, 'utf-8')
                # Leave the below print(), you will thank me next time you debug unicode strings
                # print('adding baggage', key, '=>', value, 'as', encoded_key, '=>', encoded_value)
                header_key = '%s%s' % (self.baggage_prefix, encoded_key)
                carrier[header_key] = encoded_value

    def extract(self, carrier):
        if not hasattr(carrier, 'items'):
            raise InvalidCarrierException('carrier not a collection')
        trace_id, span_id, parent_id, flags = None, None, None, None
        baggage = None
        debug_id = None
        for key, value in six.iteritems(carrier):
            uc_key = key.lower()
            if uc_key == self.trace_id_header:
                if self.url_encoding:
                    value = urllib_parse.unquote(value)
                trace_id, span_id, parent_id, flags = \
                    span_context_from_string(value)
            elif uc_key.startswith(self.baggage_prefix):
                if self.url_encoding:
                    value = urllib_parse.unquote(value)
                attr_key = key[self.prefix_length:]
                if baggage is None:
                    baggage = {attr_key.lower(): value}
                else:
                    baggage[attr_key.lower()] = value
            elif uc_key == self.debug_id_header:
                if self.url_encoding:
                    value = urllib_parse.unquote(value)
                debug_id = value
            elif uc_key == self.baggage_header:
                if self.url_encoding:
                    value = urllib_parse.unquote(value)
                baggage = self._parse_baggage_header(value, baggage)
        if not trace_id or not span_id:
            # reset all IDs
            trace_id, span_id, parent_id, flags = None, None, None, None
        if not trace_id and not debug_id and not baggage:
            return None
        return SpanContext(trace_id=trace_id, span_id=span_id,
                           parent_id=parent_id, flags=flags,
                           baggage=baggage, debug_id=debug_id)

    def _parse_baggage_header(self, header, baggage):
        for part in header.split(','):
            kv = part.strip().split('=')
            if len(kv) == 2:
                if not baggage:
                    baggage = {}
                baggage[kv[0]] = kv[1]
        return baggage


class BinaryCodec(Codec):
    """
    BinaryCodec is a no-op.

    """
    def inject(self, span_context, carrier):
        if not isinstance(carrier, bytearray):
            raise InvalidCarrierException('carrier not a bytearray')
        pass  # TODO binary encoding not implemented

    def extract(self, carrier):
        if not isinstance(carrier, bytearray):
            raise InvalidCarrierException('carrier not a bytearray')
        # TODO binary encoding not implemented
        return None


def span_context_to_string(trace_id, span_id, parent_id, flags):
    """
    Serialize span ID to a string
        {trace_id}:{span_id}:{parent_id}:{flags}

    Numbers are encoded as variable-length lower-case hex strings.
    If parent_id is None, it is written as 0.

    :param trace_id:
    :param span_id:
    :param parent_id:
    :param flags:
    """
    parent_id = parent_id or 0
    return '{:x}:{:x}:{:x}:{:x}'.format(trace_id, span_id, parent_id, flags)


def span_context_from_string(value):
    """
    Decode span ID from a string into a TraceContext.
    Returns None if the string value is malformed.

    :param value: formatted {trace_id}:{span_id}:{parent_id}:{flags}
    """
    if type(value) is list and len(value) > 0:
        # sometimes headers are presented as arrays of values
        if len(value) > 1:
            raise SpanContextCorruptedException(
                'trace context must be a string or array of 1: "%s"' % value)
        value = value[0]
    if not isinstance(value, six.string_types):
        raise SpanContextCorruptedException(
            'trace context not a string "%s"' % value)
    parts = value.split(':')
    if len(parts) != 4:
        raise SpanContextCorruptedException(
            'malformed trace context "%s"' % value)
    try:
        trace_id = int(parts[0], 16)
        span_id = int(parts[1], 16)
        parent_id = int(parts[2], 16)
        flags = int(parts[3], 16)
        if trace_id < 1 or span_id < 1 or parent_id < 0 or flags < 0:
            raise SpanContextCorruptedException(
                'malformed trace context "%s"' % value)
        if parent_id == 0:
            parent_id = None
        return trace_id, span_id, parent_id, flags
    except ValueError as e:
        raise SpanContextCorruptedException(
            'malformed trace context "%s": %s' % (value, e))


# String constants identifying the interop format.
ZipkinSpanFormat = 'zipkin-span-format'


class ZipkinCodec(Codec):
    """
    ZipkinCodec handles ZipkinSpanFormat, which is an interop format
    used by TChannel.

    """
    def inject(self, span_context, carrier):
        if not isinstance(carrier, dict):
            raise InvalidCarrierException('carrier not a dictionary')
        carrier['trace_id'] = span_context.trace_id
        carrier['span_id'] = span_context.span_id
        carrier['parent_id'] = span_context.parent_id
        carrier['traceflags'] = span_context.flags

    def extract(self, carrier):
        if isinstance(carrier, dict):
            trace_id = carrier.get('trace_id')
            span_id = carrier.get('span_id')
            parent_id = carrier.get('parent_id')
            flags = carrier.get('traceflags')
        else:
            if hasattr(carrier, 'trace_id'):
                trace_id = getattr(carrier, 'trace_id')
            else:
                raise InvalidCarrierException('carrier has no trace_id')
            if hasattr(carrier, 'span_id'):
                span_id = getattr(carrier, 'span_id')
            else:
                raise InvalidCarrierException('carrier has no span_id')
            if hasattr(carrier, 'parent_id'):
                parent_id = getattr(carrier, 'parent_id')
            else:
                raise InvalidCarrierException('carrier has no parent_id')
            if hasattr(carrier, 'traceflags'):
                flags = getattr(carrier, 'traceflags')
            else:
                raise InvalidCarrierException('carrier has no traceflags')
        if not trace_id:
            return None
        return SpanContext(trace_id=trace_id, span_id=span_id,
                           parent_id=parent_id, flags=flags,
                           baggage=None)


def header_to_hex(header):
    if not isinstance(header, (str, six.text_type)):
        raise SpanContextCorruptedException(
            'malformed trace context "%s", expected hex string' % header)

    try:
        return int(header, 16)
    except ValueError:
        raise SpanContextCorruptedException(
            'malformed trace context "%s", expected hex string' % header)


class B3Codec(Codec):
    """
    Support B3 header properties
    https://github.com/openzipkin/b3-propagation

    """
    trace_header = 'X-B3-TraceId'
    _trace_header_lc = trace_header.lower()
    span_header = 'X-B3-SpanId'
    _span_header_lc = span_header.lower()
    parent_span_header = 'X-B3-ParentSpanId'
    _parent_span_header_lc = parent_span_header.lower()
    sampled_header = 'X-B3-Sampled'
    _sampled_header_lc = sampled_header.lower()
    flags_header = 'X-B3-Flags'
    _flags_header_lc = flags_header.lower()

    def inject(self, span_context, carrier):
        if not isinstance(carrier, dict):
            raise InvalidCarrierException('carrier not a dictionary')
        carrier[self.trace_header] = format(span_context.trace_id, 'x').zfill(16)
        carrier[self.span_header] = format(span_context.span_id, 'x').zfill(16)
        if span_context.parent_id is not None:
            carrier[self.parent_span_header] = format(span_context.parent_id, 'x').zfill(16)
        if span_context.flags & DEBUG_FLAG == DEBUG_FLAG:
            carrier[self.flags_header] = '1'
        elif span_context.flags & SAMPLED_FLAG == SAMPLED_FLAG:
            carrier[self.sampled_header] = '1'

    def extract(self, carrier):
        if not isinstance(carrier, dict):
            raise InvalidCarrierException('carrier not a dictionary')
        trace_id = span_id = parent_id = None
        flags = 0x00
        for header_key, header_value in six.iteritems(carrier):
            if header_value is None:
                continue
            lower_key = header_key.lower()
            if lower_key == self._trace_header_lc:
                trace_id = header_to_hex(header_value)
            elif lower_key == self._span_header_lc:
                span_id = header_to_hex(header_value)
            elif lower_key == self._parent_span_header_lc:
                parent_id = header_to_hex(header_value)
            elif lower_key == self._sampled_header_lc and header_value == '1':
                flags |= SAMPLED_FLAG
            elif lower_key == self._flags_header_lc and header_value == '1':
                flags |= DEBUG_FLAG
        if not trace_id or not span_id:
            return None
        return SpanContext(trace_id=trace_id, span_id=span_id,
                           parent_id=parent_id, flags=flags,
                           baggage=None)
