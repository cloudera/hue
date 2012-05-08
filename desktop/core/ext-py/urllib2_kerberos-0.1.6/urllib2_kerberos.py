#!/usr/bin/python

# urllib2 with kerberos proof of concept

# Copyright 2008 Lime Nest LLC
# Copyright 2008 Lime Spot LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import logging
import sys
import urllib2 as u2

import kerberos as k


LOG = logging.getLogger("http_kerberos_auth_handler")

class AbstractKerberosAuthHandler:
    """auth handler for urllib2 that does Kerberos HTTP Negotiate Authentication
    """

    def negotiate_value(self, headers):
        """checks for "Negotiate" in proper auth header
        """
        authreq = headers.get(self.auth_header, None)

        if authreq:
            rx = re.compile('(?:.*,)*\s*Negotiate\s*([^,]*),?', re.I)
            mo = rx.search(authreq)
            if mo:
                return mo.group(1)
            else:
                LOG.debug("regex failed on: %s" % authreq)

        else:
            LOG.debug("%s header not found" % self.auth_header)

        return None

    def __init__(self):
        self.retried = 0
        self.context = None

    def generate_request_header(self, req, headers, neg_value):
        self.retried += 1
        LOG.debug("retry count: %d" % self.retried)

        host = req.get_host()
        LOG.debug("req.get_host() returned %s" % host)

        # We need Python 2.4 compatibility
        #tail, sep, head = host.rpartition(':')
        #domain = tail or head
        host_parts = host.rsplit(':', 1)
        domain = host_parts[0]

        result, self.context = k.authGSSClientInit("HTTP@%s" % domain)

        if result < 1:
            LOG.warning("authGSSClientInit returned result %d" % result)
            return None

        LOG.debug("authGSSClientInit() succeeded")

        result = k.authGSSClientStep(self.context, neg_value)

        if result < 0:
            LOG.warning("authGSSClientStep returned result %d" % result)
            return None

        LOG.debug("authGSSClientStep() succeeded")

        response = k.authGSSClientResponse(self.context)
        LOG.debug("authGSSClientResponse() succeeded")
        
        return "Negotiate %s" % response

    def authenticate_server(self, headers):
        neg_value = self.negotiate_value(headers)
        if neg_value is None:
            LOG.critical("mutual auth failed. No negotiate header")
            return None

        result = k.authGSSClientStep(self.context, neg_value)

        if  result < 1:
            # this is a critical security warning
            # should change to a raise --Tim
            LOG.critical("mutual auth failed: authGSSClientStep returned result %d" % result)
            pass

    def clean_context(self):
        if self.context is not None:
            LOG.debug("cleaning context")
            k.authGSSClientClean(self.context)
            self.context = None

    def http_error_auth_reqed(self, host, req, headers):
        neg_value = self.negotiate_value(headers) #Check for auth_header
        if neg_value is not None:
            if not self.retried > 0:
                return self.retry_http_kerberos_auth(req, headers, neg_value)
            else:
                return None
        else:
            self.retried = 0

    def retry_http_kerberos_auth(self, req, headers, neg_value):
        try:
            try:
                neg_hdr = self.generate_request_header(req, headers, neg_value)

                if neg_hdr is None:
                    LOG.debug("neg_hdr was None")
                    return None

                req.add_unredirected_header(self.authz_header, neg_hdr)
                resp = self.parent.open(req)

                self.authenticate_server(resp.info())

                return resp

            except k.GSSError, e:
                LOG.critical("GSSAPI Error: %s/%s" % (e[0][0], e[1][0]))
                return None

        finally:
            self.clean_context()
            self.retried = 0

class ProxyKerberosAuthHandler(u2.BaseHandler, AbstractKerberosAuthHandler):
    """Kerberos Negotiation handler for HTTP proxy auth
    """

    authz_header = 'Proxy-Authorization'
    auth_header = 'proxy-authenticate'

    handler_order = 480 # before Digest auth

    def http_error_407(self, req, fp, code, msg, headers):
        LOG.debug("inside http_error_407")
        host = req.get_host()
        retry = self.http_error_auth_reqed(host, req, headers)
        self.retried = 0
        return retry

class HTTPKerberosAuthHandler(u2.BaseHandler, AbstractKerberosAuthHandler):
    """Kerberos Negotiation handler for HTTP auth
    """

    authz_header = 'Authorization'
    auth_header = 'www-authenticate'

    handler_order = 480 # before Digest auth

    def http_error_401(self, req, fp, code, msg, headers):
        LOG.debug("inside http_error_401")
        host = req.get_host()
        retry = self.http_error_auth_reqed(host, req, headers)
        self.retried = 0
        return retry

def test():
    LOG.setLevel(logging.DEBUG)
    LOG.info("starting test")
    opener = u2.build_opener()
    opener.add_handler(HTTPKerberosAuthHandler())
    resp = opener.open(sys.argv[1])
    print dir(resp), resp.info(), resp.code
    

if __name__ == '__main__':
    test()

