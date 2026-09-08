#!/usr/bin/env python

# This file stolen and edited from cherrypy, so we should not assign
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""A high-speed, production ready, thread pooled, generic WSGI server.

Copyright (c) 2016, Florent Gallaire (fgallaire@gmail.com)
Copyright (c) 2004-2016, CherryPy Team (team@cherrypy.org)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

For those of you wanting to understand internals of this module, here's the
basic call flow. The server's listening thread runs a very tight loop,
sticking incoming connections onto a Queue::

    server = WSGIServer(...)
    server.start()
    while True:
        tick()
        # This blocks until a request comes in:
        child = socket.accept()
        conn = HTTPConnection(child, ...)
        server.requests.put(conn)

Worker threads are kept in a pool and poll the Queue, popping off and then
handling each connection in turn. Each connection can consist of an arbitrary
number of requests and their responses, so we run a nested loop::

    while True:
        conn = server.requests.get()
        conn.communicate()
        ->  while True:
                req = HTTPRequest(...)
                req.parse_request()
                ->  # Read the Request-Line, e.g. "GET /page HTTP/1.1"
                    req.rfile.readline()
                    read_headers(req.rfile, req.inheaders)
                req.respond()
                ->  response = app(...)
                    try:
                        for chunk in response:
                            if chunk:
                                req.write(chunk)
                    finally:
                        if hasattr(response, "close"):
                            response.close()
                if req.close_connection:
                    return
"""

__version__ = '1.3'

__all__ = ['HTTPRequest', 'HTTPConnection', 'HTTPServer',
           'SizeCheckWrapper', 'KnownLengthRFile', 'ChunkedRFile',
           'CP_makefile',
           'MaxSizeExceeded', 'NoSSLError', 'FatalSSLAlert',
           'WorkerThread', 'ThreadPool', 'SSLAdapter',
           'WSGIServer',
           'Gateway', 'WSGIGateway', 'WSGIGateway_10', 'WSGIGateway_u0',
           'WSGIPathInfoDispatcher',
           'socket_errors_to_ignore']

import json

import os

try:
    import queue
except:
    import Queue as queue
import re
import email.utils
import socket
import sys
import threading
import time
import traceback as traceback_

try:
    from urllib.parse import unquote_to_bytes, urlparse
except ImportError:
    from urlparse import unquote as unquote_to_bytes
    from urlparse import urlparse
import errno
import logging

try:
    # prefer slower Python-based io module
    import _pyio as io
except ImportError:
    # Python 2.6
    import io

try:
    import pkg_resources
except ImportError:
    pass

if 'win' in sys.platform and hasattr(socket, "AF_INET6"):
    if not hasattr(socket, 'IPPROTO_IPV6'):
        socket.IPPROTO_IPV6 = 41
    if not hasattr(socket, 'IPV6_V6ONLY'):
        socket.IPV6_V6ONLY = 27

DEFAULT_BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE

PY2 = sys.version[0] == '2'
PY3 = sys.version[0] == '3'

if PY3:
    string_types = str,
    text_type = str
    binary_type = bytes


    def ntob(n, encoding='ISO-8859-1'):
        """Return the given native string as a byte string in the given
        encoding.
        """
        # In Python 3, the native string type is unicode
        return n.encode(encoding)


    def bton(b, encoding='ISO-8859-1'):
        return b.decode(encoding)
else:
    string_types = basestring,
    text_type = unicode
    binary_type = str


    def ntob(n, encoding='ISO-8859-1'):
        """Return the given native string as a byte string in the given
        encoding.
        """
        # In Python 2, the native string type is bytes. Assume it's already
        # in the given encoding, which for ISO-8859-1 is almost always what
        # was intended.
        return n


    def bton(b, encoding='ISO-8859-1'):
        return b

LF = ntob('\n')
CRLF = ntob('\r\n')
TAB = ntob('\t')
SPACE = ntob(' ')
COLON = ntob(':')
SEMICOLON = ntob(';')
EMPTY = ntob('')
NUMBER_SIGN = ntob('#')
QUESTION_MARK = ntob('?')
ASTERISK = ntob('*')
FORWARD_SLASH = ntob('/')
quoted_slash = re.compile(ntob("(?i)%2F"))


def plat_specific_errors(*errnames):
    """Return error numbers for all errors in errnames on this platform.

    The 'errno' module contains different global constants depending on
    the specific platform (OS). This function will return the list of
    numeric values for a given list of potential names.
    """
    errno_names = dir(errno)
    nums = [getattr(errno, k) for k in errnames if k in errno_names]
    # de-dupe the list
    return list(dict.fromkeys(nums).keys())


socket_error_eintr = plat_specific_errors("EINTR", "WSAEINTR")

socket_errors_to_ignore = plat_specific_errors(
    "EPIPE",
    "EBADF", "WSAEBADF",
    "ENOTSOCK", "WSAENOTSOCK",
    "ETIMEDOUT", "WSAETIMEDOUT",
    "ECONNREFUSED", "WSAECONNREFUSED",
    "ECONNRESET", "WSAECONNRESET",
    "ECONNABORTED", "WSAECONNABORTED",
    "ENETRESET", "WSAENETRESET",
    "EHOSTDOWN", "EHOSTUNREACH",
)
socket_errors_to_ignore.append("timed out")
socket_errors_to_ignore.append("The read operation timed out")
if sys.platform == 'darwin':
    socket_errors_to_ignore.append(plat_specific_errors("EPROTOTYPE"))

socket_errors_nonblocking = plat_specific_errors(
    'EAGAIN', 'EWOULDBLOCK', 'WSAEWOULDBLOCK')

comma_separated_headers = [
    ntob(h) for h in
    ['Accept', 'Accept-Charset', 'Accept-Encoding',
     'Accept-Language', 'Accept-Ranges', 'Allow', 'Cache-Control',
     'Connection', 'Content-Encoding', 'Content-Language', 'Expect',
     'If-Match', 'If-None-Match', 'Pragma', 'Proxy-Authenticate', 'TE',
     'Trailer', 'Transfer-Encoding', 'Upgrade', 'Vary', 'Via', 'Warning',
     'WWW-Authenticate']
]

if not hasattr(logging, 'statistics'):
    logging.statistics = {}


def read_headers(rfile, hdict=None):
    """Read headers from the given stream into the given header dict.

    If hdict is None, a new header dict is created. Returns the populated
    header dict.

    Headers which are repeated are folded together using a comma if their
    specification so dictates.

    This function raises ValueError when the read bytes violate the HTTP spec.
    You should probably return "400 Bad Request" if this happens.
    """
    if hdict is None:
        hdict = {}

    while True:
        line = rfile.readline()
        if not line:
            # No more data--illegal end of headers
            raise ValueError("Illegal end of headers.")

        if line == CRLF:
            # Normal end of headers
            break
        if not line.endswith(CRLF):
            raise ValueError("HTTP requires CRLF terminators")

        if line[0] in (SPACE, TAB):
            # It's a continuation line.
            v = line.strip()
        else:
            try:
                k, v = line.split(COLON, 1)
            except ValueError:
                raise ValueError("Illegal header line.")
            # TODO: what about TE and WWW-Authenticate?
            k = k.strip().title()
            v = v.strip()
            hname = k

        if k in comma_separated_headers:
            existing = hdict.get(hname)
            if existing:
                v = b", ".join((existing, v))
        hdict[hname] = v

    return hdict


class MaxSizeExceeded(Exception):
    pass


class SizeCheckWrapper(object):
    """Wraps a file-like object, raising MaxSizeExceeded if too large."""

    def __init__(self, rfile, maxlen):
        self.rfile = rfile
        self.maxlen = maxlen
        self.bytes_read = 0

    def _check_length(self):
        if self.maxlen and self.bytes_read > self.maxlen:
            raise MaxSizeExceeded()

    def read(self, size=None):
        data = self.rfile.read(size)
        self.bytes_read += len(data)
        self._check_length()
        return data

    def readline(self, size=None):
        if size is not None:
            data = self.rfile.readline(size)
            self.bytes_read += len(data)
            self._check_length()
            return data

        # User didn't specify a size ...
        # We read the line in chunks to make sure it's not a 100MB line !
        res = []
        while True:
            data = self.rfile.readline(256)
            self.bytes_read += len(data)
            self._check_length()
            res.append(data)
            # See https://github.com/cherrypy/cherrypy/issues/421
            if len(data) < 256 or data[-1:] == LF:
                return EMPTY.join(res)

    def readlines(self, sizehint=0):
        # Shamelessly stolen from StringIO
        total = 0
        lines = []
        line = self.readline()
        while line:
            lines.append(line)
            total += len(line)
            if 0 < sizehint <= total:
                break
            line = self.readline()
        return lines

    def close(self):
        self.rfile.close()

    def __iter__(self):
        return self

    def __next__(self):
        data = next(self.rfile)
        self.bytes_read += len(data)
        self._check_length()
        return data

    def next(self):
        data = self.rfile.next()
        self.bytes_read += len(data)
        self._check_length()
        return data


class KnownLengthRFile(object):
    """Wraps a file-like object, returning an empty string when exhausted."""

    def __init__(self, rfile, content_length):
        self.rfile = rfile
        self.remaining = content_length

    def read(self, size=None):
        if self.remaining == 0:
            return b''
        if size is None:
            size = self.remaining
        else:
            size = min(size, self.remaining)

        data = self.rfile.read(size)
        self.remaining -= len(data)
        return data

    def readline(self, size=None):
        if self.remaining == 0:
            return b''
        if size is None:
            size = self.remaining
        else:
            size = min(size, self.remaining)

        data = self.rfile.readline(size)
        self.remaining -= len(data)
        return data

    def readlines(self, sizehint=0):
        # Shamelessly stolen from StringIO
        total = 0
        lines = []
        line = self.readline(sizehint)
        while line:
            lines.append(line)
            total += len(line)
            if 0 < sizehint <= total:
                break
            line = self.readline(sizehint)
        return lines

    def close(self):
        self.rfile.close()

    def __iter__(self):
        return self

    def __next__(self):
        data = next(self.rfile)
        self.remaining -= len(data)
        return data


class ChunkedRFile(object):
    """Wraps a file-like object, returning an empty string when exhausted.

    This class is intended to provide a conforming wsgi.input value for
    request entities that have been encoded with the 'chunked' transfer
    encoding.
    """

    def __init__(self, rfile, maxlen, bufsize=8192):
        self.rfile = rfile
        self.maxlen = maxlen
        self.bytes_read = 0
        self.buffer = EMPTY
        self.bufsize = bufsize
        self.closed = False

    def _fetch(self):
        if self.closed:
            return

        line = self.rfile.readline()
        self.bytes_read += len(line)

        if self.maxlen and self.bytes_read > self.maxlen:
            raise MaxSizeExceeded("Request Entity Too Large", self.maxlen)

        line = line.strip().split(SEMICOLON, 1)

        try:
            chunk_size = line.pop(0)
            chunk_size = int(chunk_size, 16)
        except ValueError:
            raise ValueError("Bad chunked transfer size: " + repr(chunk_size))

        if chunk_size <= 0:
            self.closed = True
            return

        ##            if line: chunk_extension = line[0]

        if self.maxlen and self.bytes_read + chunk_size > self.maxlen:
            raise IOError("Request Entity Too Large")

        chunk = self.rfile.read(chunk_size)
        self.bytes_read += len(chunk)
        self.buffer += chunk

        crlf = self.rfile.read(2)
        if crlf != CRLF:
            raise ValueError(
                "Bad chunked transfer coding (expected '\\r\\n', "
                "got " + repr(crlf) + ")")

    def read(self, size=None):
        data = EMPTY
        while True:
            if size and len(data) >= size:
                return data

            if not self.buffer:
                self._fetch()
                if not self.buffer:
                    # EOF
                    return data

            if size:
                remaining = size - len(data)
                data += self.buffer[:remaining]
                self.buffer = self.buffer[remaining:]
            else:
                data += self.buffer

    def readline(self, size=None):
        data = EMPTY
        while True:
            if size and len(data) >= size:
                return data

            if not self.buffer:
                self._fetch()
                if not self.buffer:
                    # EOF
                    return data

            newline_pos = self.buffer.find(LF)
            if size:
                if newline_pos == -1:
                    remaining = size - len(data)
                    data += self.buffer[:remaining]
                    self.buffer = self.buffer[remaining:]
                else:
                    remaining = min(size - len(data), newline_pos)
                    data += self.buffer[:remaining]
                    self.buffer = self.buffer[remaining:]
            else:
                if newline_pos == -1:
                    data += self.buffer
                else:
                    data += self.buffer[:newline_pos]
                    self.buffer = self.buffer[newline_pos:]

    def readlines(self, sizehint=0):
        # Shamelessly stolen from StringIO
        total = 0
        lines = []
        line = self.readline(sizehint)
        while line:
            lines.append(line)
            total += len(line)
            if 0 < sizehint <= total:
                break
            line = self.readline(sizehint)
        return lines

    def read_trailer_lines(self):
        if not self.closed:
            raise ValueError(
                "Cannot read trailers until the request body has been read.")

        while True:
            line = self.rfile.readline()
            if not line:
                # No more data--illegal end of headers
                raise ValueError("Illegal end of headers.")

            self.bytes_read += len(line)
            if self.maxlen and self.bytes_read > self.maxlen:
                raise IOError("Request Entity Too Large")

            if line == CRLF:
                # Normal end of headers
                break
            if not line.endswith(CRLF):
                raise ValueError("HTTP requires CRLF terminators")

            yield line

    def close(self):
        self.rfile.close()


class HTTPRequest(object):
    """An HTTP Request (and response).

    A single HTTP connection may consist of multiple request/response pairs.
    """

    server = None
    """The HTTPServer object which is receiving this request."""

    conn = None
    """The HTTPConnection object on which this request connected."""

    inheaders = {}
    """A dict of request headers."""

    outheaders = []
    """A list of header tuples to write in the response."""

    ready = False
    """When True, the request has been parsed and is ready to begin generating
    the response. When False, signals the calling Connection that the response
    should not be generated and the connection should close."""

    close_connection = False
    """Signals the calling Connection that the request should close. This does
    not imply an error! The client and/or server may each request that the
    connection be closed."""

    chunked_write = False
    """If True, output will be encoded with the "chunked" transfer-coding.

    This value is set automatically inside send_headers."""

    def __init__(self, server, conn):
        self.server = server
        self.conn = conn

        self.ready = False
        self.started_request = False
        self.scheme = ntob("http")
        if self.server.ssl_adapter is not None:
            self.scheme = ntob("https")
        # Use the lowest-common protocol in case read_request_line errors.
        self.response_protocol = 'HTTP/1.0'
        self.inheaders = {}

        self.status = ""
        self.outheaders = []
        self.sent_headers = False
        self.close_connection = self.__class__.close_connection
        self.chunked_read = False
        self.chunked_write = self.__class__.chunked_write

    def parse_request(self):
        """Parse the next HTTP request start-line and message-headers."""
        self.rfile = SizeCheckWrapper(self.conn.rfile,
                                      self.server.max_request_header_size)
        try:
            success = self.read_request_line()
        except MaxSizeExceeded:
            self.simple_response(
                "414 Request-URI Too Long",
                "The Request-URI sent with the request exceeds the maximum "
                "allowed bytes.")
            return
        else:
            if not success:
                return

        try:
            success = self.read_request_headers()
        except MaxSizeExceeded:
            self.simple_response(
                "413 Request Entity Too Large",
                "The headers sent with the request exceed the maximum "
                "allowed bytes.")
            return
        else:
            if not success:
                return

        self.ready = True

    def read_request_line(self):
        # HTTP/1.1 connections are persistent by default. If a client
        # requests a page, then idles (leaves the connection open),
        # then rfile.readline() will raise socket.error("timed out").
        # Note that it does this based on the value given to settimeout(),
        # and doesn't need the client to request or acknowledge the close
        # (although your TCP stack might suffer for it: cf Apache's history
        # with FIN_WAIT_2).
        request_line = self.rfile.readline()

        # Set started_request to True so communicate() knows to send 408
        # from here on out.
        self.started_request = True
        if not request_line:
            return False

        if request_line == CRLF:
            # RFC 2616 sec 4.1: "...if the server is reading the protocol
            # stream at the beginning of a message and receives a CRLF
            # first, it should ignore the CRLF."
            # But only ignore one leading line! else we enable a DoS.
            request_line = self.rfile.readline()
            if not request_line:
                return False

        if not request_line.endswith(CRLF):
            self.simple_response(
                "400 Bad Request", "HTTP requires CRLF terminators")
            return False

        try:
            method, uri, req_protocol = request_line.strip().split(SPACE, 2)
            req_protocol_str = req_protocol.decode('ascii')
            rp = int(req_protocol_str[5]), int(req_protocol_str[7])
        except (ValueError, IndexError):
            self.simple_response("400 Bad Request", "Malformed Request-Line")
            return False

        self.uri = uri
        self.method = method

        # uri may be an abs_path (including "http://host.domain.tld");
        scheme, authority, path = self.parse_request_uri(uri)
        if path is None:
            self.simple_response("400 Bad Request",
                                 "Invalid path in Request-URI.")
            return False
        if NUMBER_SIGN in path:
            self.simple_response("400 Bad Request",
                                 "Illegal #fragment in Request-URI.")
            return False

        if scheme:
            self.scheme = scheme

        qs = EMPTY
        if QUESTION_MARK in path:
            path, qs = path.split(QUESTION_MARK, 1)

        # Unquote the path+params (e.g. "/this%20path" -> "/this path").
        # http://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html#sec5.1.2
        #
        # But note that "...a URI must be separated into its components
        # before the escaped characters within those components can be
        # safely decoded." http://www.ietf.org/rfc/rfc2396.txt, sec 2.4.2
        # Therefore, "/this%2Fpath" becomes "/this%2Fpath", not "/this/path".
        try:
            atoms = [unquote_to_bytes(x) for x in quoted_slash.split(path)]
        except ValueError:
            ex = sys.exc_info()[1]
            self.simple_response("400 Bad Request", ex.args[0])
            return False
        path = b"%2F".join(atoms)
        self.path = path

        # Note that, like wsgiref and most other HTTP servers,
        # we "% HEX HEX"-unquote the path but not the query string.
        self.qs = qs

        # Compare request and server HTTP protocol versions, in case our
        # server does not support the requested protocol. Limit our output
        # to min(req, server). We want the following output:
        #     request    server     actual written   supported response
        #     protocol   protocol  response protocol    feature set
        # a     1.0        1.0           1.0                1.0
        # b     1.0        1.1           1.1                1.0
        # c     1.1        1.0           1.0                1.0
        # d     1.1        1.1           1.1                1.1
        # Notice that, in (b), the response will be "HTTP/1.1" even though
        # the client only understands 1.0. RFC 2616 10.5.6 says we should
        # only return 505 if the _major_ version is different.
        sp = int(self.server.protocol[5]), int(self.server.protocol[7])

        if sp[0] != rp[0]:
            self.simple_response("505 HTTP Version Not Supported")
            return False

        self.request_protocol = req_protocol
        self.response_protocol = "HTTP/%s.%s" % min(rp, sp)

        return True

    def read_request_headers(self):
        """Read self.rfile into self.inheaders. Return success."""

        # then all the http headers
        try:
            read_headers(self.rfile, self.inheaders)
            # debug log for checking raw request header.
            newHeaders = self.inheaders.copy()
            newHeaders[b'Cookie'] = b''
            newHeaders[b'X-Csrftoken'] = b''
            newHeaders[b'Authorization'] = b''
            logging.debug("==========================Raw request header is:%s=============================",newHeaders)
        except ValueError:
            ex = sys.exc_info()[1]
            self.simple_response("400 Bad Request", ex.args[0])
            return False

        mrbs = self.server.max_request_body_size
        if mrbs and int(self.inheaders.get(b"Content-Length", 0)) > mrbs:
            self.simple_response(
                "413 Request Entity Too Large",
                "The entity sent with the request exceeds the maximum "
                "allowed bytes.")
            return False

        # Persistent connection support
        if self.response_protocol == "HTTP/1.1":
            # Both server and client are HTTP/1.1
            if self.inheaders.get(b"Connection", b"") == b"close":
                self.close_connection = True
        else:
            # Either the server or client (or both) are HTTP/1.0
            if self.inheaders.get(b"Connection", b"") != b"Keep-Alive":
                self.close_connection = True

        # Transfer-Encoding support
        te = None
        if self.response_protocol == "HTTP/1.1":
            te = self.inheaders.get(b"Transfer-Encoding")
            if te:
                te = [x.strip().lower() for x in te.split(b",") if x.strip()]

        self.chunked_read = False

        if te:
            for enc in te:
                if enc == b"chunked":
                    self.chunked_read = True
                else:
                    # Note that, even if we see "chunked", we must reject
                    # if there is an extension we don't recognize.
                    self.simple_response("501 Unimplemented")
                    self.close_connection = True
                    return False

        # From PEP 333:
        # "Servers and gateways that implement HTTP 1.1 must provide
        # transparent support for HTTP 1.1's "expect/continue" mechanism.
        # This may be done in any of several ways:
        #   1. Respond to requests containing an Expect: 100-continue request
        #      with an immediate "100 Continue" response, and proceed normally.
        #   2. Proceed with the request normally, but provide the application
        #      with a wsgi.input stream that will send the "100 Continue"
        #      response if/when the application first attempts to read from
        #      the input stream. The read request must then remain blocked
        #      until the client responds.
        #   3. Wait until the client decides that the server does not support
        #      expect/continue, and sends the request body on its own.
        #      (This is suboptimal, and is not recommended.)
        #
        # We used to do 3, but are now doing 1. Maybe we'll do 2 someday,
        # but it seems like it would be a big slowdown for such a rare case.
        if self.inheaders.get(b"Expect", b"") == b"100-continue":
            # Don't use simple_response here, because it emits headers
            # we don't want. See
            # https://github.com/cherrypy/cherrypy/issues/951
            msg = self.server.protocol.encode('ascii')
            msg += b" 100 Continue\r\n\r\n"
            try:
                self.conn.wfile.write(msg)
            except socket.error:
                x = sys.exc_info()[1]
                if x.args[0] not in socket_errors_to_ignore:
                    raise
        return True

    def parse_request_uri(self, uri):
        """Parse a Request-URI into (scheme, authority, path).

        Note that Request-URI's must be one of::

            Request-URI    = "*" | absoluteURI | abs_path | authority

        Therefore, a Request-URI which starts with a double forward-slash
        cannot be a "net_path"::

            net_path      = "//" authority [ abs_path ]

        Instead, it must be interpreted as an "abs_path" with an empty first
        path segment::

            abs_path      = "/"  path_segments
            path_segments = segment *( "/" segment )
            segment       = *pchar *( ";" param )
            param         = *pchar
        """
        if uri == ASTERISK:
            return None, None, uri

        scheme, authority, path, params, query, fragment = urlparse(uri)
        if scheme and QUESTION_MARK not in scheme:
            # An absoluteURI.
            # If there's a scheme (and it must be http or https), then:
            # http_URL = "http:" "//" host [ ":" port ] [ abs_path [ "?" query
            # ]]
            return scheme, authority, path

        if uri.startswith(FORWARD_SLASH):
            # An abs_path.
            return None, None, uri
        else:
            # An authority.
            return None, uri, None

    def decode_chunked(self):
        """Decode the 'chunked' transfer coding.
           Cuz knox rewrite-mechanism will change the transfer-encoding in request header
        """
        cl = 0
        data = io.BytesIO()
        while True:

            line = self.conn.rfile.readline().decode().strip().split(" ", 1)
            chunk_size = int(line.pop(0), 16)
            if chunk_size <= 0:
                break
                ## if line: chunk_extension = line[0]
            cl += chunk_size
            data.write(self.conn.rfile.read(chunk_size))
            if self.conn.rfile.read(2) != b"\r\n":
                self.simple_response("400 Bad Request",
                                    "Bad chunked transfer coding")
                return None
        data.seek(0)
        # Redirect the input-stream
        self.conn.rfile=data
        return str(cl)

    def respond(self):
        """Call the gateway and write its iterable output."""
        mrbs = self.server.max_request_body_size
        if self.chunked_read:
            len = int(self.decode_chunked(), 0)
            # Rewrite the request header, remove transfer-encoding, rewrite content-length.
            del self.inheaders[b"Transfer-Encoding"]
            self.inheaders[b"Content-Length"]= str(len).encode()
            logging.debug("==========================request content-length is :%s=============================",len)
            self.rfile = KnownLengthRFile(self.conn.rfile, len)
        else:
            cl = int(self.inheaders.get(b"Content-Length", 0))
            if mrbs and mrbs < cl:
                if not self.sent_headers:
                    self.simple_response(
                        "413 Request Entity Too Large",
                        "The entity sent with the request exceeds the "
                        "maximum allowed bytes.")
                return
            self.rfile = KnownLengthRFile(self.conn.rfile, cl)

        self.server.gateway(self).respond()

        if (self.ready and not self.sent_headers):
            self.sent_headers = True
            self.send_headers()
        if self.chunked_write:
            self.conn.wfile.write(b"0\r\n\r\n")

    def simple_response(self, status, msg=""):
        """Write a simple response back to the client."""
        status = str(status)
        proto_status = "%s %s\r\n" % (self.server.protocol, status)
        content_length = "Content-Length: %s\r\n" % len(msg)
        content_type = "Content-Type: text/plain\r\n"
        buf = [
            proto_status.encode("ISO-8859-1"),
            content_length.encode("ISO-8859-1"),
            content_type.encode("ISO-8859-1"),
        ]

        if status[:3] in ("413", "414"):
            # Request Entity Too Large / Request-URI Too Long
            self.close_connection = True
            if self.response_protocol == 'HTTP/1.1':
                # This will not be true for 414, since read_request_line
                # usually raises 414 before reading the whole line, and we
                # therefore cannot know the proper response_protocol.
                buf.append(b"Connection: close\r\n")
            else:
                # HTTP/1.0 had no 413/414 status nor Connection header.
                # Emit 400 instead and trust the message body is enough.
                status = "400 Bad Request"

        buf.append(CRLF)
        if msg:
            if isinstance(msg, text_type):
                msg = msg.encode("ISO-8859-1")
            buf.append(msg)

        try:
            self.conn.wfile.write(EMPTY.join(buf))
        except socket.error:
            x = sys.exc_info()[1]
            if x.args[0] not in socket_errors_to_ignore:
                raise

    def write(self, chunk):
        """Write unbuffered data to the client."""
        if self.chunked_write and chunk:
            chunk_size_hex = hex(len(chunk))[2:].encode('ascii')
            buf = [chunk_size_hex, CRLF, chunk, CRLF]
            self.conn.wfile.write(EMPTY.join(buf))
        else:
            self.conn.wfile.write(chunk)

    def send_headers(self):
        """Assert, process, and send the HTTP response message-headers.

        You must set self.status, and self.outheaders before calling this.
        """
        hkeys = [key.lower() for key, value in self.outheaders]
        status = int(self.status[:3])

        if status == 413:
            # Request Entity Too Large. Close conn to avoid garbage.
            self.close_connection = True
        elif b"content-length" not in hkeys:
            # "All 1xx (informational), 204 (no content),
            # and 304 (not modified) responses MUST NOT
            # include a message-body." So no point chunking.
            if status < 200 or status in (204, 205, 304):
                pass
            else:
                if (self.response_protocol == 'HTTP/1.1'
                        and self.method != b'HEAD'):
                    # Use the chunked transfer-coding
                    self.chunked_write = True
                    self.outheaders.append((b"Transfer-Encoding", b"chunked"))
                else:
                    # Closing the conn is the only way to determine len.
                    self.close_connection = True

        if b"connection" not in hkeys:
            if self.response_protocol == 'HTTP/1.1':
                # Both server and client are HTTP/1.1 or better
                if self.close_connection:
                    self.outheaders.append((b"Connection", b"close"))
            else:
                # Server and/or client are HTTP/1.0
                if not self.close_connection:
                    self.outheaders.append((b"Connection", b"Keep-Alive"))

        if (not self.close_connection) and (not self.chunked_read):
            # Read any remaining request body data on the socket.
            # "If an origin server receives a request that does not include an
            # Expect request-header field with the "100-continue" expectation,
            # the request includes a request body, and the server responds
            # with a final status code before reading the entire request body
            # from the transport connection, then the server SHOULD NOT close
            # the transport connection until it has read the entire request,
            # or until the client closes the connection. Otherwise, the client
            # might not reliably receive the response message. However, this
            # requirement is not be construed as preventing a server from
            # defending itself against denial-of-service attacks, or from
            # badly broken client implementations."
            remaining = getattr(self.rfile, 'remaining', 0)
            if remaining > 0:
                self.rfile.read(remaining)

        if b"date" not in hkeys:
            self.outheaders.append((
                b"Date",
                email.utils.formatdate(usegmt=True).encode('ISO-8859-1'),
            ))

        if b"server" not in hkeys:
            self.outheaders.append((
                b"Server",
                self.server.server_name.encode('ISO-8859-1'),
            ))

        proto = self.server.protocol.encode('ascii')
        buf = [proto + SPACE + self.status + CRLF]
        for k, v in self.outheaders:
            buf.append(k + COLON + SPACE + v + CRLF)
        buf.append(CRLF)
        self.conn.wfile.write(EMPTY.join(buf))


class NoSSLError(Exception):
    """Exception raised when a client speaks HTTP to an HTTPS socket."""
    pass


class FatalSSLAlert(Exception):
    """Exception raised when the SSL implementation signals a fatal alert."""
    pass


class CP_BufferedWriter(io.BufferedWriter):
    """Faux file object attached to a socket object."""

    def write(self, b):
        self._checkClosed()
        if isinstance(b, str):
            raise TypeError("can't write str to binary stream")

        with self._write_lock:
            self._write_buf.extend(b)
            self._flush_unlocked()
            return len(b)

    def _flush_unlocked(self):
        self._checkClosed("flush of closed file")
        while self._write_buf:
            try:
                # ssl sockets only except 'bytes', not bytearrays
                # so perhaps we should conditionally wrap this for perf?
                n = self.raw.write(bytes(self._write_buf))
            except io.BlockingIOError as e:
                n = e.characters_written
            del self._write_buf[:n]


def CP_makefile_PY3(sock, mode='r', bufsize=DEFAULT_BUFFER_SIZE):
    if 'r' in mode:
        return io.BufferedReader(socket.SocketIO(sock, mode), bufsize)
    else:
        return CP_BufferedWriter(socket.SocketIO(sock, mode), bufsize)


class CP_makefile_PY2(getattr(socket, '_fileobject', object)):
    """Faux file object attached to a socket object."""

    def __init__(self, *args, **kwargs):
        self.bytes_read = 0
        self.bytes_written = 0
        socket._fileobject.__init__(self, *args, **kwargs)

    def write(self, data):
        """Sendall for non-blocking sockets."""
        while data:
            try:
                bytes_sent = self.send(data)
                data = data[bytes_sent:]
            except socket.error as e:
                if e.args[0] not in socket_errors_nonblocking:
                    raise

    def send(self, data):
        bytes_sent = self._sock.send(data)
        self.bytes_written += bytes_sent
        return bytes_sent

    def flush(self):
        if self._wbuf:
            buffer = "".join(self._wbuf)
            self._wbuf = []
            self.write(buffer)

    def recv(self, size):
        while True:
            try:
                data = self._sock.recv(size)
                self.bytes_read += len(data)
                return data
            except socket.error as e:
                if (e.args[0] not in socket_errors_nonblocking
                        and e.args[0] not in socket_error_eintr):
                    raise

    class FauxSocket(object):

        """Faux socket with the minimal interface required by pypy"""

        def _reuse(self):
            pass

    _fileobject_uses_str_type = PY2 and isinstance(
        socket._fileobject(FauxSocket())._rbuf, string_types)

    # FauxSocket is no longer needed
    del FauxSocket

    if not _fileobject_uses_str_type:
        def read(self, size=-1):
            # Use max, disallow tiny reads in a loop as they are very
            # inefficient.
            # We never leave read() with any leftover data from a new recv()
            # call in our internal buffer.
            rbufsize = max(self._rbufsize, self.default_bufsize)
            # Our use of StringIO rather than lists of string objects returned
            # by recv() minimizes memory usage and fragmentation that occurs
            # when rbufsize is large compared to the typical return value of
            # recv().
            buf = self._rbuf
            buf.seek(0, 2)  # seek end
            if size < 0:
                # Read until EOF
                # reset _rbuf.  we consume it via buf.
                self._rbuf = io.BytesIO()
                while True:
                    data = self.recv(rbufsize)
                    if not data:
                        break
                    buf.write(data)
                return buf.getvalue()
            else:
                # Read until size bytes or EOF seen, whichever comes first
                buf_len = buf.tell()
                if buf_len >= size:
                    # Already have size bytes in our buffer?  Extract and
                    # return.
                    buf.seek(0)
                    rv = buf.read(size)
                    self._rbuf = io.BytesIO()
                    self._rbuf.write(buf.read())
                    return rv

                # reset _rbuf.  we consume it via buf.
                self._rbuf = io.BytesIO()
                while True:
                    left = size - buf_len
                    # recv() will malloc the amount of memory given as its
                    # parameter even though it often returns much less data
                    # than that.  The returned data string is short lived
                    # as we copy it into a StringIO and free it.  This avoids
                    # fragmentation issues on many platforms.
                    data = self.recv(left)
                    if not data:
                        break
                    n = len(data)
                    if n == size and not buf_len:
                        # Shortcut.  Avoid buffer data copies when:
                        # - We have no data in our buffer.
                        # AND
                        # - Our call to recv returned exactly the
                        #   number of bytes we were asked to read.
                        return data
                    if n == left:
                        buf.write(data)
                        del data  # explicit free
                        break
                    assert n <= left, "recv(%d) returned %d bytes" % (left, n)
                    buf.write(data)
                    buf_len += n
                    del data  # explicit free
                    # assert buf_len == buf.tell()
                return buf.getvalue()

        def readline(self, size=-1):
            buf = self._rbuf
            buf.seek(0, 2)  # seek end
            if buf.tell() > 0:
                # check if we already have it in our buffer
                buf.seek(0)
                bline = buf.readline(size)
                if bline.endswith('\n') or len(bline) == size:
                    self._rbuf = io.BytesIO()
                    self._rbuf.write(buf.read())
                    return bline
                del bline
            if size < 0:
                # Read until \n or EOF, whichever comes first
                if self._rbufsize <= 1:
                    # Speed up unbuffered case
                    buf.seek(0)
                    buffers = [buf.read()]
                    # reset _rbuf.  we consume it via buf.
                    self._rbuf = io.BytesIO()
                    data = None
                    recv = self.recv
                    while data != "\n":
                        data = recv(1)
                        if not data:
                            break
                        buffers.append(data)
                    return "".join(buffers)

                buf.seek(0, 2)  # seek end
                # reset _rbuf.  we consume it via buf.
                self._rbuf = io.BytesIO()
                while True:
                    data = self.recv(self._rbufsize)
                    if not data:
                        break
                    nl = data.find('\n')
                    if nl >= 0:
                        nl += 1
                        buf.write(data[:nl])
                        self._rbuf.write(data[nl:])
                        del data
                        break
                    buf.write(data)
                return buf.getvalue()
            else:
                # Read until size bytes or \n or EOF seen, whichever comes
                # first
                buf.seek(0, 2)  # seek end
                buf_len = buf.tell()
                if buf_len >= size:
                    buf.seek(0)
                    rv = buf.read(size)
                    self._rbuf = io.BytesIO()
                    self._rbuf.write(buf.read())
                    return rv
                # reset _rbuf.  we consume it via buf.
                self._rbuf = io.BytesIO()
                while True:
                    data = self.recv(self._rbufsize)
                    if not data:
                        break
                    left = size - buf_len
                    # did we just receive a newline?
                    nl = data.find('\n', 0, left)
                    if nl >= 0:
                        nl += 1
                        # save the excess data to _rbuf
                        self._rbuf.write(data[nl:])
                        if buf_len:
                            buf.write(data[:nl])
                            break
                        else:
                            # Shortcut.  Avoid data copy through buf when
                            # returning a substring of our first recv().
                            return data[:nl]
                    n = len(data)
                    if n == size and not buf_len:
                        # Shortcut.  Avoid data copy through buf when
                        # returning exactly all of our first recv().
                        return data
                    if n >= left:
                        buf.write(data[:left])
                        self._rbuf.write(data[left:])
                        break
                    buf.write(data)
                    buf_len += n
                    # assert buf_len == buf.tell()
                return buf.getvalue()
    else:
        def read(self, size=-1):
            if size < 0:
                # Read until EOF
                buffers = [self._rbuf]
                self._rbuf = ""
                if self._rbufsize <= 1:
                    recv_size = self.default_bufsize
                else:
                    recv_size = self._rbufsize

                while True:
                    data = self.recv(recv_size)
                    if not data:
                        break
                    buffers.append(data)
                return "".join(buffers)
            else:
                # Read until size bytes or EOF seen, whichever comes first
                data = self._rbuf
                buf_len = len(data)
                if buf_len >= size:
                    self._rbuf = data[size:]
                    return data[:size]
                buffers = []
                if data:
                    buffers.append(data)
                self._rbuf = ""
                while True:
                    left = size - buf_len
                    recv_size = max(self._rbufsize, left)
                    data = self.recv(recv_size)
                    if not data:
                        break
                    buffers.append(data)
                    n = len(data)
                    if n >= left:
                        self._rbuf = data[left:]
                        buffers[-1] = data[:left]
                        break
                    buf_len += n
                return "".join(buffers)

        def readline(self, size=-1):
            data = self._rbuf
            if size < 0:
                # Read until \n or EOF, whichever comes first
                if self._rbufsize <= 1:
                    # Speed up unbuffered case
                    assert data == ""
                    buffers = []
                    while data != "\n":
                        data = self.recv(1)
                        if not data:
                            break
                        buffers.append(data)
                    return "".join(buffers)
                nl = data.find('\n')
                if nl >= 0:
                    nl += 1
                    self._rbuf = data[nl:]
                    return data[:nl]
                buffers = []
                if data:
                    buffers.append(data)
                self._rbuf = ""
                while True:
                    data = self.recv(self._rbufsize)
                    if not data:
                        break
                    buffers.append(data)
                    nl = data.find('\n')
                    if nl >= 0:
                        nl += 1
                        self._rbuf = data[nl:]
                        buffers[-1] = data[:nl]
                        break
                return "".join(buffers)
            else:
                # Read until size bytes or \n or EOF seen, whichever comes
                # first
                nl = data.find('\n', 0, size)
                if nl >= 0:
                    nl += 1
                    self._rbuf = data[nl:]
                    return data[:nl]
                buf_len = len(data)
                if buf_len >= size:
                    self._rbuf = data[size:]
                    return data[:size]
                buffers = []
                if data:
                    buffers.append(data)
                self._rbuf = ""
                while True:
                    data = self.recv(self._rbufsize)
                    if not data:
                        break
                    buffers.append(data)
                    left = size - buf_len
                    nl = data.find('\n', 0, left)
                    if nl >= 0:
                        nl += 1
                        self._rbuf = data[nl:]
                        buffers[-1] = data[:nl]
                        break
                    n = len(data)
                    if n >= left:
                        self._rbuf = data[left:]
                        buffers[-1] = data[:left]
                        break
                    buf_len += n
                return "".join(buffers)


CP_makefile = CP_makefile_PY2 if PY2 else CP_makefile_PY3


class HTTPConnection(object):
    """An HTTP connection (active socket).

    server: the Server object which received this connection.
    socket: the raw socket object (usually TCP) for this connection.
    makefile: a fileobject class for reading from the socket.
    """

    remote_addr = None
    remote_port = None
    ssl_env = None
    rbufsize = DEFAULT_BUFFER_SIZE
    wbufsize = DEFAULT_BUFFER_SIZE
    RequestHandlerClass = HTTPRequest

    def __init__(self, server, sock, makefile=CP_makefile):
        self.server = server
        self.socket = sock
        self.rfile = makefile(sock, "rb", self.rbufsize)
        self.wfile = makefile(sock, "wb", self.wbufsize)
        self.requests_seen = 0

    def communicate(self):
        """Read each request and respond appropriately."""
        request_seen = False
        try:
            while True:
                # (re)set req to None so that if something goes wrong in
                # the RequestHandlerClass constructor, the error doesn't
                # get written to the previous request.
                req = None
                req = self.RequestHandlerClass(self.server, self)

                # This order of operations should guarantee correct pipelining.
                req.parse_request()
                if self.server.stats['Enabled']:
                    self.requests_seen += 1
                if not req.ready:
                    # Something went wrong in the parsing (and the server has
                    # probably already made a simple_response). Return and
                    # let the conn close.
                    return

                request_seen = True
                req.respond()
                if req.close_connection:
                    return
        except socket.error:
            e = sys.exc_info()[1]
            errnum = e.args[0]
            # sadly SSL sockets return a different (longer) time out string
            if (
                    errnum == 'timed out' or
                    errnum == 'The read operation timed out'
            ):
                # Don't error if we're between requests; only error
                # if 1) no request has been started at all, or 2) we're
                # in the middle of a request.
                # See https://github.com/cherrypy/cherrypy/issues/853
                if (not request_seen) or (req and req.started_request):
                    # Don't bother writing the 408 if the response
                    # has already started being written.
                    if req and not req.sent_headers:
                        try:
                            req.simple_response("408 Request Timeout")
                        except FatalSSLAlert:
                            # Close the connection.
                            return
            elif errnum not in socket_errors_to_ignore:
                self.server.error_log("socket.error %s" % repr(errnum),
                                      level=logging.WARNING, traceback=True)
                if req and not req.sent_headers:
                    try:
                        req.simple_response("500 Internal Server Error")
                    except FatalSSLAlert:
                        # Close the connection.
                        return
            return
        except (KeyboardInterrupt, SystemExit):
            raise
        except FatalSSLAlert:
            # Close the connection.
            return
        except NoSSLError:
            if req and not req.sent_headers:
                # Unwrap our wfile
                self.wfile = CP_makefile(
                    self.socket._sock, "wb", self.wbufsize)
                req.simple_response(
                    "400 Bad Request",
                    "The client sent a plain HTTP request, but "
                    "this server only speaks HTTPS on this port.")
                self.linger = True
        except Exception:
            e = sys.exc_info()[1]
            self.server.error_log(repr(e), level=logging.ERROR, traceback=True)
            if req and not req.sent_headers:
                try:
                    req.simple_response("500 Internal Server Error")
                except FatalSSLAlert:
                    # Close the connection.
                    return

    linger = False

    def close(self):
        """Close the socket underlying this connection."""
        self.rfile.close()

        if not self.linger:
            self._close_kernel_socket()
            self.socket.close()
        else:
            # On the other hand, sometimes we want to hang around for a bit
            # to make sure the client has a chance to read our entire
            # response. Skipping the close() calls here delays the FIN
            # packet until the socket object is garbage-collected later.
            # Someday, perhaps, we'll do the full lingering_close that
            # Apache does, but not today.
            pass

    def _close_kernel_socket(self):
        """
        On old Python versions,
        Python's socket module does NOT call close on the kernel
        socket when you call socket.close(). We do so manually here
        because we want this server to send a FIN TCP segment
        immediately. Note this must be called *before* calling
        socket.close(), because the latter drops its reference to
        the kernel socket.
        """
        if PY2 and hasattr(self.socket, '_sock'):
            self.socket._sock.close()


class TrueyZero(object):
    """An object which equals and does math like the integer 0 but evals True.
    """

    def __add__(self, other):
        return other

    def __radd__(self, other):
        return other


trueyzero = TrueyZero()

_SHUTDOWNREQUEST = None


class WorkerThread(threading.Thread):
    """Thread which continuously polls a Queue for Connection objects.

    Due to the timing issues of polling a Queue, a WorkerThread does not
    check its own 'ready' flag after it has started. To stop the thread,
    it is necessary to stick a _SHUTDOWNREQUEST object onto the Queue
    (one for each running WorkerThread).
    """

    conn = None
    """The current connection pulled off the Queue, or None."""

    server = None
    """The HTTP Server which spawned this thread, and which owns the
    Queue and is placing active connections into it."""

    ready = False
    """A simple flag for the calling server to know when this thread
    has begun polling the Queue."""

    def __init__(self, server):
        self.ready = False
        self.server = server

        self.requests_seen = 0
        self.bytes_read = 0
        self.bytes_written = 0
        self.start_time = None
        self.work_time = 0
        self.stats = {
            'Requests': lambda s: self.requests_seen + (
                    (self.start_time is None) and
                    trueyzero or
                    self.conn.requests_seen
            ),
            'Bytes Read': lambda s: self.bytes_read + (
                    (self.start_time is None) and
                    trueyzero or
                    self.conn.rfile.bytes_read
            ),
            'Bytes Written': lambda s: self.bytes_written + (
                    (self.start_time is None) and
                    trueyzero or
                    self.conn.wfile.bytes_written
            ),
            'Work Time': lambda s: self.work_time + (
                    (self.start_time is None) and
                    trueyzero or
                    time.time() - self.start_time
            ),
            'Read Throughput': lambda s: s['Bytes Read'](s) / (
                    s['Work Time'](s) or 1e-6),
            'Write Throughput': lambda s: s['Bytes Written'](s) / (
                    s['Work Time'](s) or 1e-6),
        }
        threading.Thread.__init__(self)

    def run(self):
        self.server.stats['Worker Threads'][self.getName()] = self.stats
        try:
            self.ready = True
            while True:
                conn = self.server.requests.get()
                if conn is _SHUTDOWNREQUEST:
                    return

                self.conn = conn
                if self.server.stats['Enabled']:
                    self.start_time = time.time()
                try:
                    conn.communicate()
                finally:
                    conn.close()
                    if self.server.stats['Enabled']:
                        self.requests_seen += self.conn.requests_seen
                        self.bytes_read += self.conn.rfile.bytes_read
                        self.bytes_written += self.conn.wfile.bytes_written
                        self.work_time += time.time() - self.start_time
                        self.start_time = None
                    self.conn = None
        except (KeyboardInterrupt, SystemExit):
            exc = sys.exc_info()[1]
            self.server.interrupt = exc


class ThreadPool(object):
    """A Request Queue for an HTTPServer which pools threads.

    ThreadPool objects must provide min, get(), put(obj), start()
    and stop(timeout) attributes.
    """

    def __init__(self, server, min=10, max=-1,
                 accepted_queue_size=-1, accepted_queue_timeout=10):
        self.server = server
        self.min = min
        self.max = max
        self._threads = []
        self._queue = queue.Queue(maxsize=accepted_queue_size)
        self._queue_put_timeout = accepted_queue_timeout
        self.get = self._queue.get

    def start(self):
        """Start the pool of threads."""
        logging.info("Hue worker thread num: %s" % (self.min))
        for i in range(self.min):
            self._threads.append(WorkerThread(self.server))
        for worker in self._threads:
            worker.setName("CP Server " + worker.getName())
            worker.start()
        for worker in self._threads:
            while not worker.ready:
                time.sleep(.1)

    def _get_idle(self):
        """Number of worker threads which are idle. Read-only."""
        return len([t for t in self._threads if t.conn is None])

    idle = property(_get_idle, doc=_get_idle.__doc__)

    def put(self, obj):
        self._queue.put(obj, block=True, timeout=self._queue_put_timeout)
        if obj is _SHUTDOWNREQUEST:
            return

    def grow(self, amount):
        """Spawn new worker threads (not above self.max)."""
        if self.max > 0:
            budget = max(self.max - len(self._threads), 0)
        else:
            # self.max <= 0 indicates no maximum
            budget = float('inf')

        n_new = min(amount, budget)

        workers = [self._spawn_worker() for i in range(n_new)]
        while not all(worker.ready for worker in workers):
            time.sleep(.1)
        self._threads.extend(workers)

    def _spawn_worker(self):
        worker = WorkerThread(self.server)
        worker.setName("CP Server " + worker.getName())
        worker.start()
        return worker

    def shrink(self, amount):
        """Kill off worker threads (not below self.min)."""
        # Grow/shrink the pool if necessary.
        # Remove any dead threads from our list
        for t in self._threads:
            if not t.isAlive():
                self._threads.remove(t)
                amount -= 1

        # calculate the number of threads above the minimum
        n_extra = max(len(self._threads) - self.min, 0)

        # don't remove more than amount
        n_to_remove = min(amount, n_extra)

        # put shutdown requests on the queue equal to the number of threads
        # to remove. As each request is processed by a worker, that worker
        # will terminate and be culled from the list.
        for n in range(n_to_remove):
            self._queue.put(_SHUTDOWNREQUEST)

    def stop(self, timeout=5):
        # Must shut down threads here so the code that calls
        # this method can know when all threads are stopped.
        for worker in self._threads:
            self._queue.put(_SHUTDOWNREQUEST)

        # Don't join currentThread (when stop is called inside a request).
        current = threading.currentThread()
        if timeout and timeout >= 0:
            endtime = time.time() + timeout
        while self._threads:
            worker = self._threads.pop()
            if worker is not current and worker.isAlive():
                try:
                    if timeout is None or timeout < 0:
                        worker.join()
                    else:
                        remaining_time = endtime - time.time()
                        if remaining_time > 0:
                            worker.join(remaining_time)
                        if worker.isAlive():
                            # We exhausted the timeout.
                            # Forcibly shut down the socket.
                            c = worker.conn
                            if c and not c.rfile.closed:
                                try:
                                    c.socket.shutdown(socket.SHUT_RD)
                                except TypeError:
                                    # pyOpenSSL sockets don't take an arg
                                    c.socket.shutdown()
                            worker.join()
                except (AssertionError,
                        # Ignore repeated Ctrl-C.
                        # See
                        # https://github.com/cherrypy/cherrypy/issues/691.
                        KeyboardInterrupt):
                    pass

    def _get_qsize(self):
        return self._queue.qsize()

    qsize = property(_get_qsize)


try:
    import fcntl
except ImportError:
    try:
        from ctypes import windll, WinError
        import ctypes.wintypes

        _SetHandleInformation = windll.kernel32.SetHandleInformation
        _SetHandleInformation.argtypes = [
            ctypes.wintypes.HANDLE,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.DWORD,
        ]
        _SetHandleInformation.restype = ctypes.wintypes.BOOL
    except ImportError:
        def prevent_socket_inheritance(sock):
            """Dummy function, since neither fcntl nor ctypes are available."""
            pass
    else:
        def prevent_socket_inheritance(sock):
            """Mark the given socket fd as non-inheritable (Windows)."""
            if not _SetHandleInformation(sock.fileno(), 1, 0):
                raise WinError()
else:
    def prevent_socket_inheritance(sock):
        """Mark the given socket fd as non-inheritable (POSIX)."""
        fd = sock.fileno()
        old_flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFD, old_flags | fcntl.FD_CLOEXEC)

try:
    import ssl
except ImportError:
    ssl = None

try:
    from io import DEFAULT_BUFFER_SIZE
except ImportError:
    DEFAULT_BUFFER_SIZE = -1


class SSLAdapter(object):
    """A wrapper for integrating Python's builtin ssl module with WSGIServer."""

    certificate = None
    """The filename of the server SSL certificate."""

    private_key = None
    """The filename of the server's private key file."""

    certificate_chain = None
    """The filename of the certificate chain file."""

    """The ssl.SSLContext that will be used to wrap sockets where available
    (on Python > 2.7.9 / 3.3)
    """
    context = None

    password = None

    def __init__(self, certfile, keyfile, ca_certs=None, password=None, ssl_cipher_list=None):
        if ssl is None:
            raise ImportError("You must install the ssl module to use HTTPS.")
        self.certificate = certfile
        self.private_key = keyfile
        self.certificate_chain = ca_certs
        self.password = password
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        if ssl_cipher_list is not None:
            self.context.set_ciphers(ssl_cipher_list)
        self.context.load_cert_chain(self.certificate, self.private_key, self.password)

    def bind(self, sock):
        """Wrap and return the given socket."""
        return sock

    def wrap(self, sock):
        """Wrap and return the given socket, plus WSGI environ entries."""
        try:
            if self.context is not None:
                s = self.context.wrap_socket(sock, do_handshake_on_connect=True,
                                             server_side=True)
            else:
                s = ssl.wrap_socket(sock, do_handshake_on_connect=True,
                                    server_side=True, certfile=self.certificate,
                                    keyfile=self.private_key,
                                    ssl_version=ssl.PROTOCOL_SSLv23,
                                    ca_certs=self.certificate_chain)
        except ssl.SSLError:
            e = sys.exc_info()[1]
            if e.errno == ssl.SSL_ERROR_EOF:
                # This is almost certainly due to the cherrypy engine
                # 'pinging' the socket to assert it's connectable;
                # the 'ping' isn't SSL.
                return None, {}
            elif e.errno == ssl.SSL_ERROR_SSL:
                if 'http request' in e.args[1].lower():
                    # The client is speaking HTTP to an HTTPS server.
                    raise NoSSLError
                elif 'unknown protocol' in e.args[1].lower():
                    # The client is speaking some non-HTTP protocol.
                    # Drop the conn.
                    return None, {}
            raise
        return s, self.get_environ(s)

    # TODO: fill this out more with mod ssl env
    def get_environ(self, sock):
        """Create WSGI environ entries to be merged into each request."""
        cipher = sock.cipher()
        ssl_environ = {
            "wsgi.url_scheme": "https",
            "HTTPS": "on",
            'SSL_PROTOCOL': cipher[1],
            'SSL_CIPHER': cipher[0]
            # SSL_VERSION_INTERFACE 	string 	The mod_ssl program version
            # SSL_VERSION_LIBRARY 	string 	The OpenSSL program version
        }
        return ssl_environ

    def makefile(self, sock, mode='r', bufsize=DEFAULT_BUFFER_SIZE):
        return CP_makefile(sock, mode, bufsize)


class HTTPServer(object):
    """An HTTP server."""

    _bind_addr = "127.0.0.1"
    _interrupt = None

    gateway = None
    """A Gateway instance."""

    minthreads = None
    """The minimum number of worker threads to create (default 10)."""

    maxthreads = None
    """The maximum number of worker threads to create (default -1 = no limit).
    """

    server_name = None
    """The name of the server; defaults to socket.gethostname()."""

    protocol = "HTTP/1.1"
    """The version string to write in the Status-Line of all HTTP responses.

    For example, "HTTP/1.1" is the default. This also limits the supported
    features used in the response."""

    request_queue_size = 5
    """The 'backlog' arg to socket.listen(); max queued connections
    (default 5).
    """

    shutdown_timeout = 5
    """The total time, in seconds, to wait for worker threads to cleanly exit.
    """

    timeout = 10
    """The timeout in seconds for accepted connections (default 10)."""

    version = "WSGIserver/" + __version__
    """A version string for the HTTPServer."""

    software = None
    """The value to set for the SERVER_SOFTWARE entry in the WSGI environ.

    If None, this defaults to ``'%s Server' % self.version``."""

    ready = False
    """An internal flag which marks whether the socket is accepting
    connections.
    """

    max_request_header_size = 0
    """The maximum size, in bytes, for request headers, or 0 for no limit."""

    max_request_body_size = 0
    """The maximum size, in bytes, for request bodies, or 0 for no limit."""

    nodelay = True
    """If True (the default since 3.1), sets the TCP_NODELAY socket option."""

    ConnectionClass = HTTPConnection
    """The class to use for handling HTTP connections."""

    ssl_adapter = None
    """An instance of SSLAdapter (or a subclass).

    You must have the corresponding SSL driver library installed."""

    def __init__(self, bind_addr, gateway, minthreads=10, maxthreads=-1,
                 server_name=None):
        self.bind_addr = bind_addr
        self.gateway = gateway

        self.requests = ThreadPool(self, min=minthreads or 1, max=maxthreads)

        if not server_name:
            server_name = socket.gethostname()
        self.server_name = server_name
        self.clear_stats()

    def clear_stats(self):
        self._start_time = None
        self._run_time = 0
        self.stats = {
            'Enabled': False,
            'Bind Address': lambda s: repr(self.bind_addr),
            'Run time': lambda s: (not s['Enabled']) and -1 or self.runtime(),
            'Accepts': 0,
            'Accepts/sec': lambda s: s['Accepts'] / self.runtime(),
            'Queue': lambda s: getattr(self.requests, "qsize", None),
            'Threads': lambda s: len(getattr(self.requests, "_threads", [])),
            'Threads Idle': lambda s: getattr(self.requests, "idle", None),
            'Socket Errors': 0,
            'Requests': lambda s: (not s['Enabled']) and -1 or sum(
                [w['Requests'](w) for w in s['Worker Threads'].values()], 0),
            'Bytes Read': lambda s: (not s['Enabled']) and -1 or sum(
                [w['Bytes Read'](w) for w in s['Worker Threads'].values()], 0),
            'Bytes Written': lambda s: (not s['Enabled']) and -1 or sum(
                [w['Bytes Written'](w) for w in s['Worker Threads'].values()],
                0),
            'Work Time': lambda s: (not s['Enabled']) and -1 or sum(
                [w['Work Time'](w) for w in s['Worker Threads'].values()], 0),
            'Read Throughput': lambda s: (not s['Enabled']) and -1 or sum(
                [w['Bytes Read'](w) / (w['Work Time'](w) or 1e-6)
                 for w in s['Worker Threads'].values()], 0),
            'Write Throughput': lambda s: (not s['Enabled']) and -1 or sum(
                [w['Bytes Written'](w) / (w['Work Time'](w) or 1e-6)
                 for w in s['Worker Threads'].values()], 0),
            'Worker Threads': {},
        }
        logging.statistics["WSGIserver %d" % id(self)] = self.stats

    def runtime(self):
        if self._start_time is None:
            return self._run_time
        else:
            return self._run_time + (time.time() - self._start_time)

    def __str__(self):
        return "%s.%s(%r)" % (self.__module__, self.__class__.__name__,
                              self.bind_addr)

    def _get_bind_addr(self):
        return self._bind_addr

    def _set_bind_addr(self, value):
        if isinstance(value, tuple) and value[0] in ('', None):
            # Despite the socket module docs, using '' does not
            # allow AI_PASSIVE to work. Passing None instead
            # returns '0.0.0.0' like we want. In other words:
            #     host    AI_PASSIVE     result
            #      ''         Y         192.168.x.y
            #      ''         N         192.168.x.y
            #     None        Y         0.0.0.0
            #     None        N         127.0.0.1
            # But since you can get the same effect with an explicit
            # '0.0.0.0', we deny both the empty string and None as values.
            raise ValueError("Host values of '' or None are not allowed. "
                             "Use '0.0.0.0' (IPv4) or '::' (IPv6) instead "
                             "to listen on all active interfaces.")
        self._bind_addr = value

    bind_addr = property(
        _get_bind_addr,
        _set_bind_addr,
        doc="""The interface on which to listen for connections.

        For TCP sockets, a (host, port) tuple. Host values may be any IPv4
        or IPv6 address, or any valid hostname. The string 'localhost' is a
        synonym for '127.0.0.1' (or '::1', if your hosts file prefers IPv6).
        The string '0.0.0.0' is a special IPv4 entry meaning "any active
        interface" (INADDR_ANY), and '::' is the similar IN6ADDR_ANY for
        IPv6. The empty string or None are not allowed.

        For UNIX sockets, supply the filename as a string.

        Systemd socket activation is automatic and doesn't require tempering
        with this variable""")

    def start(self):
        """Run the server forever."""
        self._interrupt = None

        if self.software is None:
            self.software = "%s Server" % self.version

        # Select the appropriate socket
        self.socket = None
        if os.getenv('LISTEN_PID', None):
            # systemd socket activation
            self.socket = socket.fromfd(3, socket.AF_INET, socket.SOCK_STREAM)
        elif isinstance(self.bind_addr, string_types):
            # AF_UNIX socket

            # So we can reuse the socket...
            try:
                os.unlink(self.bind_addr)
            except:
                pass

            # So everyone can access the socket...
            try:
                os.chmod(self.bind_addr, 0o777)
            except:
                pass

            info = [
                (socket.AF_UNIX, socket.SOCK_STREAM, 0, "", self.bind_addr)]
        else:
            # AF_INET or AF_INET6 socket
            # Get the correct address family for our host (allows IPv6
            # addresses)
            host, port = self.bind_addr
            try:
                info = socket.getaddrinfo(
                    host, port, socket.AF_UNSPEC,
                    socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
            except socket.gaierror:
                if ':' in self.bind_addr[0]:
                    info = [(socket.AF_INET6, socket.SOCK_STREAM,
                             0, "", self.bind_addr + (0, 0))]
                else:
                    info = [(socket.AF_INET, socket.SOCK_STREAM,
                             0, "", self.bind_addr)]

        if not self.socket:
            msg = "No socket could be created"
            for res in info:
                af, socktype, proto, canonname, sa = res
                try:
                    self.bind(af, socktype, proto)
                    break
                except socket.error as serr:
                    msg = "%s -- (%s: %s)" % (msg, sa, serr)
                    if self.socket:
                        self.socket.close()
                    self.socket = None

            if not self.socket:
                raise socket.error(msg)

        # Timeout so KeyboardInterrupt can be caught on Win32
        self.socket.settimeout(1)
        self.socket.listen(self.request_queue_size)

        # Create worker threads
        self.requests.start()

        self.ready = True
        self._start_time = time.time()
        while self.ready:
            try:
                self.tick()
            except (KeyboardInterrupt, SystemExit):
                self.stop()
            except:
                self.error_log("Error in HTTPServer.tick", level=logging.ERROR,
                               traceback=True)

            if self.interrupt:
                while self.interrupt is True:
                    # Wait for self.stop() to complete. See _set_interrupt.
                    time.sleep(0.1)
                if self.interrupt:
                    raise self.interrupt

    def error_log(self, msg="", level=20, traceback=False):
        # Override this in subclasses as desired
        sys.stderr.write(msg + '\n')
        sys.stderr.flush()
        if traceback:
            tblines = traceback_.format_exc()
            sys.stderr.write(tblines)
            sys.stderr.flush()

    def bind(self, family, type, proto=0):
        """Create (or recreate) the actual socket object."""
        self.socket = socket.socket(family, type, proto)
        prevent_socket_inheritance(self.socket)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.nodelay and not isinstance(self.bind_addr, str):
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        if self.ssl_adapter is not None:
            self.socket = self.ssl_adapter.bind(self.socket)

        # If listening on the IPV6 any address ('::' = IN6ADDR_ANY),
        # activate dual-stack. See
        # https://github.com/cherrypy/cherrypy/issues/871.
        if (hasattr(socket, 'AF_INET6') and family == socket.AF_INET6
                and self.bind_addr[0] in ('::', '::0', '::0.0.0.0')):
            try:
                self.socket.setsockopt(
                    socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            except (AttributeError, socket.error):
                # Apparently, the socket option is not available in
                # this machine's TCP stack
                pass

        self.socket.bind(self.bind_addr)

    def tick(self):
        """Accept a new connection and put it on the Queue."""
        try:
            s, addr = self.socket.accept()
            if self.stats['Enabled']:
                self.stats['Accepts'] += 1
            if not self.ready:
                return

            prevent_socket_inheritance(s)
            if hasattr(s, 'settimeout'):
                s.settimeout(self.timeout)

            makefile = CP_makefile
            ssl_env = {}
            # if ssl cert and key are set, we try to be a secure HTTP server
            if self.ssl_adapter is not None:
                try:
                    s, ssl_env = self.ssl_adapter.wrap(s)
                except NoSSLError:
                    msg = ("The client sent a plain HTTP request, but "
                           "this server only speaks HTTPS on this port.")
                    buf = ["%s 400 Bad Request\r\n" % self.protocol,
                           "Content-Length: %s\r\n" % len(msg),
                           "Content-Type: text/plain\r\n\r\n",
                           msg]

                    sock_to_make = s if PY3 else s._sock
                    wfile = makefile(sock_to_make, "wb", DEFAULT_BUFFER_SIZE)
                    try:
                        wfile.write(ntob("".join(buf)))
                    except socket.error:
                        x = sys.exc_info()[1]
                        if x.args[0] not in socket_errors_to_ignore:
                            raise
                    return
                if not s:
                    return
                makefile = self.ssl_adapter.makefile
                # Re-apply our timeout since we may have a new socket object
                if hasattr(s, 'settimeout'):
                    s.settimeout(self.timeout)

            conn = self.ConnectionClass(self, s, makefile)

            if not isinstance(self.bind_addr, string_types):
                # optional values
                # Until we do DNS lookups, omit REMOTE_HOST
                if addr is None:  # sometimes this can happen
                    # figure out if AF_INET or AF_INET6.
                    if len(s.getsockname()) == 2:
                        # AF_INET
                        addr = ('0.0.0.0', 0)
                    else:
                        # AF_INET6
                        addr = ('::', 0)
                conn.remote_addr = addr[0]
                conn.remote_port = addr[1]

            conn.ssl_env = ssl_env

            try:
                self.requests.put(conn)
            except queue.Full:
                # Just drop the conn. TODO: write 503 back?
                conn.close()
                return
        except socket.timeout:
            # The only reason for the timeout in start() is so we can
            # notice keyboard interrupts on Win32, which don't interrupt
            # accept() by default
            return
        except socket.error:
            x = sys.exc_info()[1]
            if self.stats['Enabled']:
                self.stats['Socket Errors'] += 1
            if x.args[0] in socket_error_eintr:
                # I *think* this is right. EINTR should occur when a signal
                # is received during the accept() call; all docs say retry
                # the call, and I *think* I'm reading it right that Python
                # will then go ahead and poll for and handle the signal
                # elsewhere. See
                # https://github.com/cherrypy/cherrypy/issues/707.
                return
            if x.args[0] in socket_errors_nonblocking:
                # Just try again. See
                # https://github.com/cherrypy/cherrypy/issues/479.
                return
            if x.args[0] in socket_errors_to_ignore:
                # Our socket was closed.
                # See https://github.com/cherrypy/cherrypy/issues/686.
                return
            raise

    def _get_interrupt(self):
        return self._interrupt

    def _set_interrupt(self, interrupt):
        self._interrupt = True
        self.stop()
        self._interrupt = interrupt

    interrupt = property(_get_interrupt, _set_interrupt,
                         doc="Set this to an Exception instance to "
                             "interrupt the server.")

    def stop(self):
        """Gracefully shutdown a server that is serving forever."""
        self.ready = False
        if self._start_time is not None:
            self._run_time += (time.time() - self._start_time)
        self._start_time = None

        sock = getattr(self, "socket", None)
        if sock:
            if not isinstance(self.bind_addr, string_types):
                # Touch our own socket to make accept() return immediately.
                try:
                    host, port = sock.getsockname()[:2]
                except socket.error:
                    x = sys.exc_info()[1]
                    if x.args[0] not in socket_errors_to_ignore:
                        # Changed to use error code and not message
                        # See
                        # https://github.com/cherrypy/cherrypy/issues/860.
                        raise
                else:
                    # Note that we're explicitly NOT using AI_PASSIVE,
                    # here, because we want an actual IP to touch.
                    # localhost won't work if we've bound to a public IP,
                    # but it will if we bound to '0.0.0.0' (INADDR_ANY).
                    for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC,
                                                  socket.SOCK_STREAM):
                        af, socktype, proto, canonname, sa = res
                        s = None
                        try:
                            s = socket.socket(af, socktype, proto)
                            # See
                            # http://groups.google.com/group/cherrypy-users/
                            #     browse_frm/thread/bbfe5eb39c904fe0
                            s.settimeout(1.0)
                            s.connect((host, port))
                            s.close()
                        except socket.error:
                            if s:
                                s.close()
            if hasattr(sock, "close"):
                sock.close()
            self.socket = None

        self.requests.stop(self.shutdown_timeout)


class Gateway(object):
    """A base class to interface HTTPServer with other systems, such as WSGI.
    """

    def __init__(self, req):
        self.req = req

    def respond(self):
        """Process the current request. Must be overridden in a subclass."""
        raise NotImplemented


# ------------------------------- WSGI Stuff -------------------------------- #


class WSGIServer(HTTPServer):
    """A subclass of HTTPServer which calls a WSGI application."""

    wsgi_version = (1, 0)
    """The version of WSGI to produce."""

    def __init__(self, wsgi_app, host='0.0.0.0', port=8080, numthreads=10,
                 server_name=None, max=-1, request_queue_size=5, timeout=10,
                 shutdown_timeout=5, accepted_queue_size=-1,
                 accepted_queue_timeout=10, certfile=None, keyfile=None,
                 ca_certs=None, password=None, ssl_cipher_list=None):
        self.requests = ThreadPool(self, min=numthreads or 1, max=max,
                                   accepted_queue_size=accepted_queue_size,
                                   accepted_queue_timeout=accepted_queue_timeout)
        self.wsgi_app = wsgi_app
        self.gateway = wsgi_gateways[self.wsgi_version]

        self.bind_addr = (host, port)
        if not server_name:
            server_name = socket.gethostname()
        self.server_name = server_name
        self.request_queue_size = request_queue_size

        self.timeout = timeout
        self.shutdown_timeout = shutdown_timeout
        self.clear_stats()
        if certfile and keyfile:
            self.ssl_adapter = SSLAdapter(certfile, keyfile, ca_certs, password, ssl_cipher_list)

    def _get_numthreads(self):
        return self.requests.min

    def _set_numthreads(self, value):
        self.requests.min = value

    numthreads = property(_get_numthreads, _set_numthreads)


class WSGIGateway(Gateway):
    """A base class to interface HTTPServer with WSGI."""

    def __init__(self, req):
        self.req = req
        self.started_response = False
        self.env = self.get_environ()
        self.remaining_bytes_out = None

    def get_environ(self):
        """Return a new environ dict targeting the given wsgi.version"""
        raise NotImplemented

    def respond(self):
        """Process the current request."""
        response = self.req.server.wsgi_app(self.env, self.start_response)
        try:
            for chunk in response:
                # "The start_response callable must not actually transmit
                # the response headers. Instead, it must store them for the
                # server or gateway to transmit only after the first
                # iteration of the application return value that yields
                # a NON-EMPTY string, or upon the application's first
                # invocation of the write() callable." (PEP 333)
                if chunk:
                    if not isinstance(chunk, binary_type):
                        raise ValueError("WSGI Applications must yield bytes")
                    self.write(chunk)
        finally:
            if hasattr(response, "close"):
                response.close()

    def start_response(self, status, headers, exc_info=None):
        """WSGI callable to begin the HTTP response."""
        # "The application may call start_response more than once,
        # if and only if the exc_info argument is provided."
        if self.started_response and not exc_info:
            raise AssertionError("WSGI start_response called a second "
                                 "time with no exc_info.")
        self.started_response = True

        # "if exc_info is provided, and the HTTP headers have already been
        # sent, start_response must raise an error, and should raise the
        # exc_info tuple."
        if self.req.sent_headers:
            try:
                if PY2:
                    exec('raise exc_info[0], exc_info[1], exc_info[2]')
                else:
                    raise exc_info[0](exc_info[1]).with_traceback(exc_info[2])
            finally:
                exc_info = None

        self.req.status = self._encode_status(status)

        for k, v in headers:
            if not isinstance(k, str):
                raise TypeError(
                    "WSGI response header key %r is not of type str." % k)
            if not isinstance(v, str):
                raise TypeError(
                    "WSGI response header value %r is not of type str." % v)
            if k.lower() == 'content-length':
                self.remaining_bytes_out = int(v)
            out_header = ntob(k), ntob(v)
            self.req.outheaders.append(out_header)

        return self.write

    @staticmethod
    def _encode_status(status):
        """
        According to PEP 3333, when using Python 3, the response status
        and headers must be bytes masquerading as unicode; that is, they
        must be of type "str" but are restricted to code points in the
        "latin-1" set.
        """
        if PY2:
            return status
        if not isinstance(status, str):
            raise TypeError("WSGI response status is not of type str.")
        return status.encode('ISO-8859-1')

    def write(self, chunk):
        """WSGI callable to write unbuffered data to the client.

        This method is also used internally by start_response (to write
        data from the iterable returned by the WSGI application).
        """
        if not self.started_response:
            raise AssertionError("WSGI write called before start_response.")

        chunklen = len(chunk)
        rbo = self.remaining_bytes_out
        if rbo is not None and chunklen > rbo:
            if not self.req.sent_headers:
                # Whew. We can send a 500 to the client.
                self.req.simple_response(
                    "500 Internal Server Error",
                    "The requested resource returned more bytes than the "
                    "declared Content-Length.")
            else:
                # Dang. We have probably already sent data. Truncate the chunk
                # to fit (so the client doesn't hang) and raise an error later.
                chunk = chunk[:rbo]

        if not self.req.sent_headers:
            self.req.sent_headers = True
            self.req.send_headers()

        self.req.write(chunk)

        if rbo is not None:
            rbo -= chunklen
            if rbo < 0:
                raise ValueError(
                    "Response body exceeds the declared Content-Length.")


class WSGIGateway_10(WSGIGateway):
    """A Gateway class to interface HTTPServer with WSGI 1.0.x."""

    def get_environ(self):
        """Return a new environ dict targeting the given wsgi.version"""
        req = self.req
        env = {
            # set a non-standard environ entry so the WSGI app can know what
            # the *real* server protocol is (and what features to support).
            # See http://www.faqs.org/rfcs/rfc2145.html.
            'ACTUAL_SERVER_PROTOCOL': req.server.protocol,
            'PATH_INFO': bton(req.path),
            'QUERY_STRING': bton(req.qs),
            'REMOTE_ADDR': req.conn.remote_addr or '',
            'REMOTE_PORT': str(req.conn.remote_port or ''),
            'REQUEST_METHOD': bton(req.method),
            'REQUEST_URI': bton(req.uri),
            'SCRIPT_NAME': '',
            'SERVER_NAME': req.server.server_name,
            # Bah. "SERVER_PROTOCOL" is actually the REQUEST protocol.
            'SERVER_PROTOCOL': bton(req.request_protocol),
            'SERVER_SOFTWARE': req.server.software,
            'wsgi.errors': sys.stderr,
            'wsgi.input': req.rfile,
            'wsgi.multiprocess': False,
            'wsgi.multithread': True,
            'wsgi.run_once': False,
            'wsgi.url_scheme': bton(req.scheme),
            'wsgi.version': (1, 0),
        }

        if isinstance(req.server.bind_addr, string_types):
            # AF_UNIX. This isn't really allowed by WSGI, which doesn't
            # address unix domain sockets. But it's better than nothing.
            env["SERVER_PORT"] = ""
        else:
            env["SERVER_PORT"] = str(req.server.bind_addr[1])

        # Request headers
        env.update(
            ("HTTP_" + bton(k).upper().replace("-", "_"), bton(v))
            for k, v in req.inheaders.items()
        )

        # CONTENT_TYPE/CONTENT_LENGTH
        ct = env.pop("HTTP_CONTENT_TYPE", None)
        if ct is not None:
            env["CONTENT_TYPE"] = ct
        cl = env.pop("HTTP_CONTENT_LENGTH", None)
        if cl is not None:
            env["CONTENT_LENGTH"] = cl

        if req.conn.ssl_env:
            env.update(req.conn.ssl_env)

        return env


class WSGIGateway_u0(WSGIGateway_10):
    """A Gateway class to interface HTTPServer with WSGI u.0.

    WSGI u.0 is an experimental protocol, which uses unicode for keys
    and values in both Python 2 and Python 3.
    """

    def get_environ(self):
        """Return a new environ dict targeting the given wsgi.version"""
        req = self.req
        env_10 = WSGIGateway_10.get_environ(self)
        env = dict(map(self._decode_key, self.items()))
        env['wsgi.version'] = ('u', 0)

        # Request-URI
        enc = env.setdefault('wsgi.url_encoding', 'utf-8')
        try:
            env["PATH_INFO"] = req.path.decode(enc)
            env["QUERY_STRING"] = req.qs.decode(enc)
        except UnicodeDecodeError:
            # Fall back to latin 1 so apps can transcode if needed.
            env['wsgi.url_encoding'] = 'ISO-8859-1'
            env["PATH_INFO"] = env_10["PATH_INFO"]
            env["QUERY_STRING"] = env_10["QUERY_STRING"]

        env.update(map(self._decode_value, self.items()))

        return env

    @staticmethod
    def _decode_key(k, v):
        if PY2:
            k = k.decode('ISO-8859-1')
        return k, v

    @staticmethod
    def _decode_value(k, v):
        skip_keys = 'REQUEST_URI', 'wsgi.input'
        if PY3 or not isinstance(v, bytes) or k in skip_keys:
            return k, v
        return k, v.decode('ISO-8859-1')


wsgi_gateways = {
    (1, 0): WSGIGateway_10,
    ('u', 0): WSGIGateway_u0,
}

# Multi components
MULTI_CONFIG_SEPARATE = '|'
MULTI_KEY_SEPARATE = ';'


# Global User Desktop Setting
class UserDesktopSetting(object):
    def __init__(self):
        self.userDesktopSettingInfo = {}
        self.USER_SETTING_DB_NAME = 'user_desktop_setting'
        self.USER_NAME = 'user_name'
        self.APP_NAME = 'app_name'
        self.SERVICE_NAME = 'service_name'

    def set(self, user_name, app_name, app_server_name):
        set_status = False
        if user_name in self.userDesktopSettingInfo and app_name in self.userDesktopSettingInfo[user_name]:
            if self.userDesktopSettingInfo[user_name][app_name] == app_server_name:
                return True

        exist_status, exist_result = self._check_setting_exist(user_name, app_name)
        if exist_status is False:
            return False
        if exist_result is False:
            excute_status = self._add_setting_to_db(user_name, app_name, app_server_name)
        else:
            excute_status = self._update_setting_to_db(user_name, app_name, app_server_name)

        if excute_status is True:
            self.userDesktopSettingInfo[user_name][app_name] = app_server_name
            return True
        else:
            return False

    def get(self, user_name, app_name, default_name):
        if user_name in self.userDesktopSettingInfo and app_name in self.userDesktopSettingInfo[user_name]:
            return True, self.userDesktopSettingInfo[user_name][app_name]

        exist_status, exist_result = self._check_setting_exist(user_name, app_name)
        if exist_status is False:
            return False, None
        if exist_result is False:
            self.userDesktopSettingInfo[user_name] = {
                app_name: default_name,
            }
            return True, default_name

        query_status, query_result = self._get_setting_from_db(user_name, app_name)
        if query_status is False:
            return False, None
        self.userDesktopSettingInfo[user_name] = {
            app_name: query_result,
        }
        return True, query_result

    def _add_setting_to_db(self, user_name, app_name, service_name):
        '''add new user setting to db'''
        logging.info("Add setting for app %s, which name is: %s, to user %s." % (app_name, service_name, user_name))
        sql_cmd = 'INSERT INTO "%s" ("%s", "%s", "%s") values(\'%s\', \'%s\', \'%s\')' % (
            self.USER_SETTING_DB_NAME,
            self.USER_NAME,
            self.APP_NAME,
            self.SERVICE_NAME,
            user_name,
            app_name,
            service_name
        )
        add_status = self._guassdb_handler(sql_cmd, need_result=False)
        if add_status is False:
            return False
        else:
            return True

    def _update_setting_to_db(self, user_name, app_name, service_name):
        '''update exist user setting to db'''
        sql_cmd = 'update "%s" set "%s"=\'%s\' where "%s"=\'%s\' and "%s"=\'%s\'' % (
            self.USER_SETTING_DB_NAME,
            self.SERVICE_NAME,
            service_name,
            self.USER_NAME,
            user_name,
            self.APP_NAME,
            app_name
        )
        update_status = self._guassdb_handler(sql_cmd, need_result=False)
        if update_status is False:
            return False
        else:
            return True

    def _get_setting_from_db(self, user_name, app_name):
        '''get user app setting from db'''
        logging.debug("Query setting for app %s to user %s." % (app_name, user_name))
        sql_cmd = 'select "%s" from "%s" where "%s"=\'%s\' and "%s"=\'%s\'' % (
            self.SERVICE_NAME,
            self.USER_SETTING_DB_NAME,
            self.USER_NAME,
            user_name,
            self.APP_NAME,
            app_name
        )
        get_status, get_result = self._guassdb_handler(sql_cmd, need_result=True)
        if get_status is False or len(get_result) < 1:
            return False, None
        return True, get_result[0]

    def _check_setting_exist(self, user_name, app_name):
        '''check whether user have app setting'''
        sql_cmd = 'select count(*) from "%s" where "%s"=\'%s\' and "%s"=\'%s\'' % (
            self.USER_SETTING_DB_NAME,
            self.USER_NAME,
            user_name,
            self.APP_NAME,
            app_name
        )
        get_status, get_result = self._guassdb_handler(sql_cmd, need_result=True)
        if get_status is False or len(get_result) < 1:
            return False, False
        if get_result[0] == 0:
            return True, False
        else:
            return True, True

    def _guassdb_handler(self, sql_cmd, need_result=False):
        '''function about GuassDB connection'''
        from django.db import connection
        excute_status = False
        if need_result is True:
            excute_result = None
        cursor = connection.cursor()
        try:
            cursor.execute(sql_cmd)
            if need_result is True:
                excute_result = cursor.fetchone()
            excute_status = True
            cursor.close()
        except Exception as e:
            logging.error("Excute %s failed, error message is: %s." % (sql_cmd, e))
        finally:
            if need_result is True:
                return excute_status, excute_result
            else:
                return excute_status


gUserDesktopSetting = UserDesktopSetting()


# Store imformation in memory to avoid file writing all the time
class HueSystemSetting(object):
    def __init__(self):
        import configobj
        self._current_workspace = os.getcwd()
        self._config_file_path = self._current_workspace + '/desktop/conf/hue.ini'
        self._env_file_path = self._current_workspace + '/desktop/ENV_VARS'
        self._special_app_name = {
            'hive_server_name': [],
            'oozie_server_name': [],
            'zookeeper_server_name': []
        }
        self._special_url_info = ['oozie_url', 'solr_url']
        self._reverse_system_config = {}
        self._duplicated_config_name = []
        if os.path.isfile(self._config_file_path) is False:
            logging.error('%s does not exist, this should not happen except compile test.' % self._config_file_path)
            time.sleep(10)
            return

        self._system_config_object = configobj.ConfigObj(self._config_file_path)

        # for fast index scan for 1 level config and which is a unique name
        # like:
        #   'liboozie': {'oozie_server_port': '21003'}
        # not index for:
        #   'notebook' : {'solr': {'name': 'Solr SQL'}}
        for system_config in self._system_config_object:
            system_config_section = self._system_config_object[system_config]
            for second_config_tag in system_config_section:
                system_config_value = system_config_section[second_config_tag]
                if isinstance(system_config_value, str) is False:
                    continue
                if system_config_value in self._duplicated_config_name:
                    continue
                if system_config_value in self._reverse_system_config:
                    self._duplicated_config_name.append(system_config_value)
                    del self._reverse_system_config[system_config_value]
                    continue
                self._reverse_system_config[second_config_tag] = system_config

    def check(self, config_name):
        if config_name in self._reverse_system_config:
            return True
        else:
            return False

    def get(self, config_name):
        if self.check(config_name) is False:
            return False, None
        return True, self._system_config_object[self._reverse_system_config[config_name]][config_name]

    def update(self, config_name, config_value):
        if self.check(config_name) is False:
            return False
        self._system_config_object[self._reverse_system_config[config_name]][config_name] = config_value
        return True

    def update_all(self):
        if os.path.isfile(self._env_file_path) is False:
            logging.warn('%s does not exist, this should not happen often' % self._env_file_path)
            return

        with open(self._env_file_path, "r") as _env_vars_file:
            env_vars_info = _env_vars_file.readlines()
            for file_line in env_vars_info:
                if file_line.find('=') < 0:
                    continue
                line_info = file_line.replace('\\:', ':').strip().split('=')
                if len(line_info) < 2:
                    continue
                line_tag = line_info[0]
                if line_tag not in self._special_app_name:
                    continue
                self._special_app_name[line_tag] = sorted(
                    self._value_handler(line_info[1], special_mode=True).split(MULTI_CONFIG_SEPARATE))

            for file_line in env_vars_info:
                if file_line.find('=') < 0:
                    continue
                line_info = file_line.replace('\\:', ':').strip().split('=')
                if len(line_info) < 2:
                    continue
                line_tag = line_info[0]
                if line_tag not in self._reverse_system_config:
                    continue
                if line_tag in self._special_url_info:
                    continue
                self.update(line_tag, self._value_handler(line_info[1]))

    def get_user_index(self, user_name, app_name, target_config):
        if user_name is None:
            return 0
        default_name = target_config.get(data_index=0)
        get_status, user_server_name = gUserDesktopSetting.get(user_name, app_name, default_name)
        if get_status is False:
            return 0
        if hasattr(target_config, 'grab_key') is False or target_config.grab_key not in self._reverse_system_config:
            return 0
        all_server_names = self._system_config_object[self._reverse_system_config[target_config.grab_key]][
            target_config.grab_key].split(MULTI_CONFIG_SEPARATE)
        if user_server_name not in all_server_names:
            return 0
        name_index = 0
        for server_name in all_server_names:
            if server_name == user_server_name:
                return name_index
            name_index += 1
        return 0

    def _value_handler(self, value_string, special_mode=False):
        result_string = ''
        try:
            if value_string.find('configurations') < 0:
                return value_string
            json_value = json.loads(value_string)
            if 'configurations' not in json_value or len(json_value['configurations']) < 1:
                logging.debug('Manage error: %s is not a legal value as expected.' % value_string)
                return ''
            for service_info in json_value['configurations']:
                if 'serviceName' not in service_info or 'values' not in service_info:
                    logging.debug('Manage error: %s is not a legal value as expected.' % value_string)
                    return ''
            if special_mode is True:
                for service_info in json_value['configurations']:
                    if result_string != '':
                        result_string += MULTI_CONFIG_SEPARATE + service_info['serviceName']
                    else:
                        result_string = service_info['serviceName']
                return result_string

            for app_tag_name in self._special_app_name:
                if json_value['configurations'][0]['serviceName'] not in self._special_app_name[app_tag_name]:
                    continue
                for app_service_name in self._special_app_name[app_tag_name]:
                    for service_info in json_value['configurations']:
                        if service_info['serviceName'] != app_service_name:
                            continue
                        if result_string != '':
                            result_string += MULTI_CONFIG_SEPARATE + ';'.join(service_info['values'])
                        else:
                            result_string = ';'.join(service_info['values'])
                        break
            return result_string
        except ValueError:
            return result_string


gHueSystemSetting = HueSystemSetting()


class WSGIPathInfoDispatcher(object):
    """A WSGI dispatcher for dispatch based on the PATH_INFO.

    apps: a dict or list of (path_prefix, app) pairs.
    """

    def __init__(self, apps):
        try:
            apps = list(apps.items())
        except AttributeError:
            pass

        # Sort the apps by len(path), descending
        by_path_len = lambda app: len(app[0])
        apps.sort(key=by_path_len, reverse=True)

        # The path_prefix strings must start, but not end, with a slash.
        # Use "" instead of "/".
        self.apps = [(p.rstrip("/"), a) for p, a in apps]

    def __call__(self, environ, start_response):
        path = environ["PATH_INFO"] or "/"
        for p, app in self.apps:
            # The apps list should be sorted by length, descending.
            if path.startswith(p + "/") or path == p:
                environ = environ.copy()
                environ["SCRIPT_NAME"] = environ["SCRIPT_NAME"] + p
                environ["PATH_INFO"] = path[len(p):]
                return app(environ, start_response)

        start_response('404 Not Found', [('Content-Type', 'text/plain'),
                                         ('Content-Length', '0')])
        return ['']
