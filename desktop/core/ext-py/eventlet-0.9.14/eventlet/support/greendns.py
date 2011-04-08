#!/usr/bin/env python
'''
    greendns - non-blocking DNS support for Eventlet
'''

# Portions of this code taken from the gogreen project:
#   http://github.com/slideinc/gogreen
#
# Copyright (c) 2005-2010 Slide, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#     * Neither the name of the author nor the names of other
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from eventlet import patcher
from eventlet.green import _socket_nodns
from eventlet.green import time
from eventlet.green import select

dns = patcher.import_patched('dns', 
                             socket=_socket_nodns,
                             time=time,
                             select=select)
for pkg in ('dns.query', 'dns.exception', 'dns.inet', 'dns.message', 
            'dns.rdatatype','dns.resolver', 'dns.reversename'):
   setattr(dns, pkg.split('.')[1], patcher.import_patched(pkg, 
                                                          socket=_socket_nodns,
                                                          time=time,
                                                          select=select))

socket = _socket_nodns

DNS_QUERY_TIMEOUT = 10.0

#
# Resolver instance used to perfrom DNS lookups.
#
class FakeAnswer(list):
   expiration = 0
class FakeRecord(object):
   pass

class ResolverProxy(object):
    def __init__(self, *args, **kwargs):
        self._resolver = None
        self._filename = kwargs.get('filename', '/etc/resolv.conf')
        self._hosts = {}
        if kwargs.pop('dev', False):
            self._load_etc_hosts()

    def _load_etc_hosts(self):
        try:
            fd = open('/etc/hosts', 'r')
            contents = fd.read()
            fd.close()
        except (IOError, OSError):
            return
        contents = [line for line in contents.split('\n') if line and not line[0] == '#']
        for line in contents:
            line = line.replace('\t', ' ')
            parts = line.split(' ')
            parts = [p for p in parts if p]
            if not len(parts):
                continue
            ip = parts[0]
            for part in parts[1:]:
                self._hosts[part] = ip

    def clear(self):
        self._resolver = None

    def query(self, *args, **kwargs):
        if self._resolver is None:
            self._resolver = dns.resolver.Resolver(filename = self._filename)
            self._resolver.cache = dns.resolver.Cache()

        query = args[0]
        if query is None:
            args = list(args)
            query = args[0] = '0.0.0.0'
        if self._hosts and self._hosts.get(query):
            answer = FakeAnswer()
            record = FakeRecord()
            setattr(record, 'address', self._hosts[query])
            answer.append(record)
            return answer
        return self._resolver.query(*args, **kwargs)
#
# cache
#
resolver  = ResolverProxy(dev=True)

def resolve(name):
    error = None
    rrset = None

    if rrset is None or time.time() > rrset.expiration:
        try:
            rrset = resolver.query(name)
        except dns.exception.Timeout, e:
            error = (socket.EAI_AGAIN, 'Lookup timed out')
        except dns.exception.DNSException, e:
            error = (socket.EAI_NODATA, 'No address associated with hostname')
        else:
            pass
            #responses.insert(name, rrset)

    if error:
        if rrset is None:
            raise socket.gaierror(error)
        else:
            sys.stderr.write('DNS error: %r %r\n' % (name, error))
    return rrset
#
# methods
#
def getaliases(host):
    """Checks for aliases of the given hostname (cname records)
    returns a list of alias targets
    will return an empty list if no aliases
    """
    cnames = []
    error = None

    try:
        answers = dns.resolver.query(host, 'cname')
    except dns.exception.Timeout, e:
        error = (socket.EAI_AGAIN, 'Lookup timed out')
    except dns.exception.DNSException, e:
        error = (socket.EAI_NODATA, 'No address associated with hostname')
    else:
        for record in answers:
            cnames.append(str(answers[0].target))

    if error:
        sys.stderr.write('DNS error: %r %r\n' % (host, error))

    return cnames

def getaddrinfo(host, port, family=0, socktype=0, proto=0, flags=0):
    """Replacement for Python's socket.getaddrinfo.

    Currently only supports IPv4.  At present, flags are not
    implemented.
    """
    socktype = socktype or socket.SOCK_STREAM

    if is_ipv4_addr(host):
        return [(socket.AF_INET, socktype, proto, '', (host, port))]

    rrset = resolve(host)
    value = []

    for rr in rrset:
        value.append((socket.AF_INET, socktype, proto, '', (rr.address, port)))
    return value

def gethostbyname(hostname):
    """Replacement for Python's socket.gethostbyname.

    Currently only supports IPv4.
    """
    if is_ipv4_addr(hostname):
        return hostname

    rrset = resolve(hostname)
    return rrset[0].address

def gethostbyname_ex(hostname):
    """Replacement for Python's socket.gethostbyname_ex.

    Currently only supports IPv4.
    """
    if is_ipv4_addr(hostname):
        return (hostname, [], [hostname])

    rrset = resolve(hostname)
    addrs = []

    for rr in rrset:
        addrs.append(rr.address)
    return (hostname, [], addrs)

def getnameinfo(sockaddr, flags):
    """Replacement for Python's socket.getnameinfo.

    Currently only supports IPv4.
    """
    try:
        host, port = sockaddr
    except (ValueError, TypeError):
        if not isinstance(sockaddr, tuple):
            del sockaddr  # to pass a stdlib test that is
                          # hyper-careful about reference counts
            raise TypeError('getnameinfo() argument 1 must be a tuple')
        else:
            # must be ipv6 sockaddr, pretending we don't know how to resolve it
            raise socket.gaierror(-2, 'name or service not known')

    if (flags & socket.NI_NAMEREQD) and (flags & socket.NI_NUMERICHOST):
        # Conflicting flags.  Punt.
        raise socket.gaierror(
            (socket.EAI_NONAME, 'Name or service not known'))

    if is_ipv4_addr(host):
        try:
            rrset =	resolver.query(
                dns.reversename.from_address(host), dns.rdatatype.PTR)
            if len(rrset) > 1:
                raise socket.error('sockaddr resolved to multiple addresses')
            host = rrset[0].target.to_text(omit_final_dot=True)
        except dns.exception.Timeout, e:
            if flags & socket.NI_NAMEREQD:
                raise socket.gaierror((socket.EAI_AGAIN, 'Lookup timed out'))
        except dns.exception.DNSException, e:
            if flags & socket.NI_NAMEREQD:
                raise socket.gaierror(
                    (socket.EAI_NONAME, 'Name or service not known'))
    else:
        try:
            rrset = resolver.query(host)
            if len(rrset) > 1:
                raise socket.error('sockaddr resolved to multiple addresses')
            if flags & socket.NI_NUMERICHOST:
                host = rrset[0].address
        except dns.exception.Timeout, e:
            raise socket.gaierror((socket.EAI_AGAIN, 'Lookup timed out'))
        except dns.exception.DNSException, e:
            raise socket.gaierror(
                (socket.EAI_NODATA, 'No address associated with hostname'))

        if not (flags & socket.NI_NUMERICSERV):
            proto = (flags & socket.NI_DGRAM) and 'udp' or 'tcp'
            port = socket.getservbyport(port, proto)

    return (host, port)

def is_ipv4_addr(host):
    """is_ipv4_addr returns true if host is a valid IPv4 address in
    dotted quad notation.
    """
    try:
        d1, d2, d3, d4 = map(int, host.split('.'))
    except (ValueError, AttributeError):
        return False

    if 0 <= d1 <= 255 and 0 <= d2 <= 255 and 0 <= d3 <= 255 and 0 <= d4 <= 255:
        return True
    return False

def _net_read(sock, count, expiration):
    """coro friendly replacement for dns.query._net_write
    Read the specified number of bytes from sock.  Keep trying until we
    either get the desired amount, or we hit EOF.
    A Timeout exception will be raised if the operation is not completed
    by the expiration time.
    """
    s = ''
    while count > 0:
        try:
            n = sock.recv(count)
        except socket.timeout:
            ## Q: Do we also need to catch coro.CoroutineSocketWake and pass?
            if expiration - time.time() <= 0.0:
                raise dns.exception.Timeout
        if n == '':
            raise EOFError
        count = count - len(n)
        s = s + n
    return s

def _net_write(sock, data, expiration):
    """coro friendly replacement for dns.query._net_write
    Write the specified data to the socket.
    A Timeout exception will be raised if the operation is not completed
    by the expiration time.
    """
    current = 0
    l = len(data)
    while current < l:
        try:
            current += sock.send(data[current:])
        except socket.timeout:
            ## Q: Do we also need to catch coro.CoroutineSocketWake and pass?
            if expiration - time.time() <= 0.0:
                raise dns.exception.Timeout

def udp(
    q, where, timeout=DNS_QUERY_TIMEOUT, port=53, af=None, source=None,
    source_port=0, ignore_unexpected=False):
    """coro friendly replacement for dns.query.udp
    Return the response obtained after sending a query via UDP.

    @param q: the query
    @type q: dns.message.Message
    @param where: where to send the message
    @type where: string containing an IPv4 or IPv6 address
    @param timeout: The number of seconds to wait before the query times out.
    If None, the default, wait forever.
    @type timeout: float
    @param port: The port to which to send the message.  The default is 53.
    @type port: int
    @param af: the address family to use.  The default is None, which
    causes the address family to use to be inferred from the form of of where.
    If the inference attempt fails, AF_INET is used.
    @type af: int
    @rtype: dns.message.Message object
    @param source: source address.  The default is the IPv4 wildcard address.
    @type source: string
    @param source_port: The port from which to send the message.
    The default is 0.
    @type source_port: int
    @param ignore_unexpected: If True, ignore responses from unexpected
    sources.  The default is False.
    @type ignore_unexpected: bool"""

    wire = q.to_wire()
    if af is None:
        try:
            af = dns.inet.af_for_address(where)
        except:
            af = dns.inet.AF_INET
    if af == dns.inet.AF_INET:
        destination = (where, port)
        if source is not None:
            source = (source, source_port)
    elif af == dns.inet.AF_INET6:
        destination = (where, port, 0, 0)
        if source is not None:
            source = (source, source_port, 0, 0)

    s = socket.socket(af, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        expiration = dns.query._compute_expiration(timeout)
        if source is not None:
            s.bind(source)
        try:
            s.sendto(wire, destination)
        except socket.timeout:
            ## Q: Do we also need to catch coro.CoroutineSocketWake and pass?
            if expiration - time.time() <= 0.0:
                raise dns.exception.Timeout
        while 1:
            try:
                (wire, from_address) = s.recvfrom(65535)
            except socket.timeout:
                ## Q: Do we also need to catch coro.CoroutineSocketWake and pass?
                if expiration - time.time() <= 0.0:
                    raise dns.exception.Timeout
            if from_address == destination:
                break
            if not ignore_unexpected:
                raise dns.query.UnexpectedSource(
                    'got a response from %s instead of %s'
                        % (from_address, destination))
    finally:
        s.close()

    r = dns.message.from_wire(wire, keyring=q.keyring, request_mac=q.mac)
    if not q.is_response(r):
        raise dns.query.BadResponse()
    return r

def tcp(q, where, timeout=DNS_QUERY_TIMEOUT, port=53,
   af=None, source=None, source_port=0):
    """coro friendly replacement for dns.query.tcp
    Return the response obtained after sending a query via TCP.

    @param q: the query
    @type q: dns.message.Message object
    @param where: where to send the message
    @type where: string containing an IPv4 or IPv6 address
    @param timeout: The number of seconds to wait before the query times out.
    If None, the default, wait forever.
    @type timeout: float
    @param port: The port to which to send the message.  The default is 53.
    @type port: int
    @param af: the address family to use.  The default is None, which
    causes the address family to use to be inferred from the form of of where.
    If the inference attempt fails, AF_INET is used.
    @type af: int
    @rtype: dns.message.Message object
    @param source: source address.  The default is the IPv4 wildcard address.
    @type source: string
    @param source_port: The port from which to send the message.
    The default is 0.
    @type source_port: int"""

    wire = q.to_wire()
    if af is None:
        try:
            af = dns.inet.af_for_address(where)
        except:
            af = dns.inet.AF_INET
    if af == dns.inet.AF_INET:
        destination = (where, port)
        if source is not None:
            source = (source, source_port)
    elif af == dns.inet.AF_INET6:
        destination = (where, port, 0, 0)
        if source is not None:
            source = (source, source_port, 0, 0)
    s = socket.socket(af, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        expiration = dns.query._compute_expiration(timeout)
        if source is not None:
            s.bind(source)
        try:
            s.connect(destination)
        except socket.timeout:
            ## Q: Do we also need to catch coro.CoroutineSocketWake and pass?
            if expiration - time.time() <= 0.0:
                raise dns.exception.Timeout

        l = len(wire)
        # copying the wire into tcpmsg is inefficient, but lets us
        # avoid writev() or doing a short write that would get pushed
        # onto the net
        tcpmsg = struct.pack("!H", l) + wire
        _net_write(s, tcpmsg, expiration)
        ldata = _net_read(s, 2, expiration)
        (l,) = struct.unpack("!H", ldata)
        wire = _net_read(s, l, expiration)
    finally:
        s.close()
    r = dns.message.from_wire(wire, keyring=q.keyring, request_mac=q.mac)
    if not q.is_response(r):
        raise dns.query.BadResponse()
    return r

def reset():
   resolver.clear()

# Install our coro-friendly replacements for the tcp and udp query methods.
dns.query.tcp = tcp
dns.query.udp = udp

