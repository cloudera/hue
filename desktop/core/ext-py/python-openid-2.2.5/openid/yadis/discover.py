# -*- test-case-name: openid.test.test_yadis_discover -*-
__all__ = ['discover', 'DiscoveryResult', 'DiscoveryFailure']

from cStringIO import StringIO

from openid import fetchers

from openid.yadis.constants import \
     YADIS_HEADER_NAME, YADIS_CONTENT_TYPE, YADIS_ACCEPT_HEADER
from openid.yadis.parsehtml import MetaNotFound, findHTMLMeta

class DiscoveryFailure(Exception):
    """Raised when a YADIS protocol error occurs in the discovery process"""
    identity_url = None

    def __init__(self, message, http_response):
        Exception.__init__(self, message)
        self.http_response = http_response

class DiscoveryResult(object):
    """Contains the result of performing Yadis discovery on a URI"""

    # The URI that was passed to the fetcher
    request_uri = None

    # The result of following redirects from the request_uri
    normalized_uri = None

    # The URI from which the response text was returned (set to
    # None if there was no XRDS document found)
    xrds_uri = None

    # The content-type returned with the response_text
    content_type = None

    # The document returned from the xrds_uri
    response_text = None

    def __init__(self, request_uri):
        """Initialize the state of the object

        sets all attributes to None except the request_uri
        """
        self.request_uri = request_uri

    def usedYadisLocation(self):
        """Was the Yadis protocol's indirection used?"""
        return self.normalized_uri != self.xrds_uri

    def isXRDS(self):
        """Is the response text supposed to be an XRDS document?"""
        return (self.usedYadisLocation() or
                self.content_type == YADIS_CONTENT_TYPE)

def discover(uri):
    """Discover services for a given URI.

    @param uri: The identity URI as a well-formed http or https
        URI. The well-formedness and the protocol are not checked, but
        the results of this function are undefined if those properties
        do not hold.

    @return: DiscoveryResult object

    @raises Exception: Any exception that can be raised by fetching a URL with
        the given fetcher.
    @raises DiscoveryFailure: When the HTTP response does not have a 200 code.
    """
    result = DiscoveryResult(uri)
    resp = fetchers.fetch(uri, headers={'Accept': YADIS_ACCEPT_HEADER})
    if resp.status not in (200, 206):
        raise DiscoveryFailure(
            'HTTP Response status from identity URL host is not 200. '
            'Got status %r' % (resp.status,), resp)

    # Note the URL after following redirects
    result.normalized_uri = resp.final_url

    # Attempt to find out where to go to discover the document
    # or if we already have it
    result.content_type = resp.headers.get('content-type')

    result.xrds_uri = whereIsYadis(resp)

    if result.xrds_uri and result.usedYadisLocation():
        resp = fetchers.fetch(result.xrds_uri)
        if resp.status not in (200, 206):
            exc = DiscoveryFailure(
                'HTTP Response status from Yadis host is not 200. '
                'Got status %r' % (resp.status,), resp)
            exc.identity_url = result.normalized_uri
            raise exc
        result.content_type = resp.headers.get('content-type')

    result.response_text = resp.body
    return result



def whereIsYadis(resp):
    """Given a HTTPResponse, return the location of the Yadis document.

    May be the URL just retrieved, another URL, or None, if I can't
    find any.

    [non-blocking]

    @returns: str or None
    """
    # Attempt to find out where to go to discover the document
    # or if we already have it
    content_type = resp.headers.get('content-type')

    # According to the spec, the content-type header must be an exact
    # match, or else we have to look for an indirection.
    if (content_type and
        content_type.split(';', 1)[0].lower() == YADIS_CONTENT_TYPE):
        return resp.final_url
    else:
        # Try the header
        yadis_loc = resp.headers.get(YADIS_HEADER_NAME.lower())

        if not yadis_loc:
            # Parse as HTML if the header is missing.
            #
            # XXX: do we want to do something with content-type, like
            # have a whitelist or a blacklist (for detecting that it's
            # HTML)?
            try:
                yadis_loc = findHTMLMeta(StringIO(resp.body))
            except MetaNotFound:
                pass

        return yadis_loc

