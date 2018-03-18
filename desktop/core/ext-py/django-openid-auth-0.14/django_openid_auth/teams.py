# Launchpad OpenID Teams Extension support for python-openid
#
# Copyright (C) 2008-2013 Canonical Ltd.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""Team membership support for Launchpad.

The primary form of communication between the RP and Launchpad is an
OpenID authentication request. Our solution is to piggyback a team
membership test onto this interaction.

As part of an OpenID authentication request, the RP includes the
following fields:

  openid.ns.lp:
    An OpenID 2.0 namespace URI for the extension. It is not strictly
    required for 1.1 requests, but including it is good for forward
    compatibility.

    It must be set to: http://ns.launchpad.net/2007/openid-teams

  openid.lp.query_membership:
    A comma separated list of Launchpad team names that the RP is
    interested in.

As part of the positive assertion OpenID response, the following field
will be provided:

  openid.ns.lp:
    (as above)

  openid.lp.is_member:
    A comma separated list of teams that the user is actually a member
    of. The list may be limited to those teams mentioned in the
    request.

    This field must be included in the response signature in order to
    be considered valid (as the response is bounced through the user's
    web browser, an unsigned value could be modified).

@since: 2.1.1
"""

from __future__ import unicode_literals

from openid import oidutil
from openid.extension import Extension
from openid.message import (
    registerNamespaceAlias,
    NamespaceAliasRegistrationError,
)
from six import string_types

__all__ = [
    'TeamsRequest',
    'TeamsResponse',
    'ns_uri',
    'supportsTeams',
]

ns_uri = 'http://ns.launchpad.net/2007/openid-teams'

try:
    registerNamespaceAlias(ns_uri, 'lp')
except NamespaceAliasRegistrationError as e:
    oidutil.log(
        'registerNamespaceAlias(%r, %r) failed: %s' % (ns_uri, 'lp', str(e)))


def supportsTeams(endpoint):
    """Does the given endpoint advertise support for Launchpad Teams?

    @param endpoint: The endpoint object as returned by OpenID discovery
    @type endpoint: openid.consumer.discover.OpenIDEndpoint

    @returns: Whether an lp type was advertised by the endpoint
    @rtype: bool
    """
    return endpoint.usesExtension(ns_uri)


class TeamsNamespaceError(ValueError):
    """The Launchpad teams namespace was not found and could not
    be created using the expected name (there's another extension
    using the name 'lp')

    This is not I{illegal}, for OpenID 2, although it probably
    indicates a problem, since it's not expected that other extensions
    will re-use the alias that is in use for OpenID 1.

    If this is an OpenID 1 request, then there is no recourse. This
    should not happen unless some code has modified the namespaces for
    the message that is being processed.
    """


def getTeamsNS(message):
    """Extract the Launchpad teams namespace URI from the given
    OpenID message.

    @param message: The OpenID message from which to parse Launchpad
        teams. This may be a request or response message.
    @type message: C{L{openid.message.Message}}

    @returns: the lp namespace URI for the supplied message. The
        message may be modified to define a Launchpad teams
        namespace.
    @rtype: C{str}

    @raise ValueError: when using OpenID 1 if the message defines
        the 'lp' alias to be something other than a Launchpad
        teams type.
    """
    # See if there exists an alias for the Launchpad teams type.
    alias = message.namespaces.getAlias(ns_uri)
    if alias is None:
        # There is no alias, so try to add one. (OpenID version 1)
        try:
            message.namespaces.addAlias(ns_uri, 'lp')
        except KeyError as why:
            # An alias for the string 'lp' already exists, but it's
            # defined for something other than Launchpad teams
            raise TeamsNamespaceError(why[0])

    # we know that ns_uri defined, because it's defined in the
    # else clause of the loop as well, so disable the warning
    return ns_uri


class TeamsRequest(Extension):
    """An object to hold the state of a Launchpad teams request.

    @ivar query_membership: A comma separated list of Launchpad team
        names that the RP is interested in.
    @type required: [str]

    @group Consumer: requestField, requestTeams, getExtensionArgs,
                     addToOpenIDRequest
    @group Server: fromOpenIDRequest, parseExtensionArgs
    """

    ns_alias = 'lp'

    def __init__(self, query_membership=None, lp_ns_uri=ns_uri):
        """Initialize an empty Launchpad teams request"""
        Extension.__init__(self)
        self.query_membership = []
        self.ns_uri = lp_ns_uri

        if query_membership:
            self.requestTeams(query_membership)

    # Assign getTeamsNS to a static method so that it can be
    # overridden for testing.
    _getTeamsNS = staticmethod(getTeamsNS)

    def fromOpenIDRequest(cls, request):
        """Create a Launchpad teams request that contains the
        fields that were requested in the OpenID request with the
        given arguments

        @param request: The OpenID request
        @type request: openid.server.CheckIDRequest

        @returns: The newly created Launchpad teams request
        @rtype: C{L{TeamsRequest}}
        """
        self = cls()

        # Since we're going to mess with namespace URI mapping, don't
        # mutate the object that was passed in.
        message = request.message.copy()

        self.ns_uri = self._getTeamsNS(message)
        args = message.getArgs(self.ns_uri)
        self.parseExtensionArgs(args)

        return self

    fromOpenIDRequest = classmethod(fromOpenIDRequest)

    def parseExtensionArgs(self, args, strict=False):
        """Parse the unqualified Launchpad teams request
        parameters and add them to this object.

        This method is essentially the inverse of
        C{L{getExtensionArgs}}. This method restores the serialized
        Launchpad teams request fields.

        If you are extracting arguments from a standard OpenID
        checkid_* request, you probably want to use C{L{fromOpenIDRequest}},
        which will extract the lp namespace and arguments from the
        OpenID request. This method is intended for cases where the
        OpenID server needs more control over how the arguments are
        parsed than that method provides.

        >>> args = message.getArgs(ns_uri)
        >>> request.parseExtensionArgs(args)

        @param args: The unqualified Launchpad teams arguments
        @type args: {str:str}

        @param strict: Whether requests with fields that are not
            defined in the Launchpad teams specification should be
            tolerated (and ignored)
        @type strict: bool

        @returns: None; updates this object
        """
        items = args.get('query_membership')
        if items:
            for team_name in items.split(','):
                try:
                    self.requestTeam(team_name, strict)
                except ValueError:
                    if strict:
                        raise

    def allRequestedTeams(self):
        """A list of all of the Launchpad teams that were
        requested.

        @rtype: [str]
        """
        return self.query_membership

    def wereTeamsRequested(self):
        """Have any Launchpad teams been requested?

        @rtype: bool
        """
        return bool(self.allRequestedTeams())

    def __contains__(self, team_name):
        """Was this team in the request?"""
        return team_name in self.query_membership

    def requestTeam(self, team_name, strict=False):
        """Request the specified team from the OpenID user

        @param team_name: the unqualified Launchpad team name
        @type team_name: str

        @param strict: whether to raise an exception when a team is
            added to a request more than once

        @raise ValueError: when strict is set and the team was
            requested more than once
        """
        if strict:
            if team_name in self.query_membership:
                raise ValueError('That team has already been requested')
        else:
            if team_name in self.query_membership:
                return

        self.query_membership.append(team_name)

    def requestTeams(self, query_membership, strict=False):
        """Add the given list of teams to the request

        @param query_membership: The Launchpad teams request
        @type query_membership: [str]

        @raise ValueError: when a team requested is not a string
            or strict is set and a team was requested more than once
        """
        if isinstance(query_membership, string_types):
            raise TypeError('Teams should be passed as a list of '
                            'strings (not %r)' % (type(query_membership),))

        for team_name in query_membership:
            self.requestTeam(team_name, strict=strict)

    def getExtensionArgs(self):
        """Get a dictionary of unqualified Launchpad teams
        arguments representing this request.

        This method is essentially the inverse of
        C{L{parseExtensionArgs}}. This method serializes the Launchpad
        teams request fields.

        @rtype: {str:str}
        """
        args = {}

        if self.query_membership:
            args['query_membership'] = ','.join(self.query_membership)

        return args


class TeamsResponse(Extension):
    """Represents the data returned in a Launchpad teams response
    inside of an OpenID C{id_res} response. This object will be
    created by the OpenID server, added to the C{id_res} response
    object, and then extracted from the C{id_res} message by the
    Consumer.

    @ivar data: The Launchpad teams data, an array.

    @ivar ns_uri: The URI under which the Launchpad teams data was
        stored in the response message.

    @group Server: extractResponse
    @group Consumer: fromSuccessResponse
    @group Read-only dictionary interface: keys, iterkeys, items, iteritems,
        __iter__, get, __getitem__, keys, has_key
    """

    ns_alias = 'lp'

    def __init__(self, is_member=None, lp_ns_uri=ns_uri):
        Extension.__init__(self)
        if is_member is None:
            self.is_member = []
        else:
            self.is_member = is_member

        self.ns_uri = lp_ns_uri

    def addTeam(self, team_name):
        if team_name not in self.is_member:
            self.is_member.append(team_name)

    def extractResponse(cls, request, is_member_str):
        """Take a C{L{TeamsRequest}} and a list of Launchpad
        team values and create a C{L{TeamsResponse}}
        object containing that data.

        @param request: The Launchpad teams request object
        @type request: TeamsRequest

        @param is_member: The Launchpad teams data for this
            response, as a list of strings.
        @type is_member: {str:str}

        @returns: a Launchpad teams response object
        @rtype: TeamsResponse
        """
        self = cls()
        self.ns_uri = request.ns_uri
        self.is_member = is_member_str.split(',')
        return self

    extractResponse = classmethod(extractResponse)

    # Assign getTeamsNS to a static method so that it can be
    # overridden for testing
    _getTeamsNS = staticmethod(getTeamsNS)

    def fromSuccessResponse(cls, success_response, signed_only=True):
        """Create a C{L{TeamsResponse}} object from a successful OpenID
        library response
        (C{L{openid.consumer.consumer.SuccessResponse}}) response
        message

        @param success_response: A SuccessResponse from consumer.complete()
        @type success_response: C{L{openid.consumer.consumer.SuccessResponse}}

        @param signed_only: Whether to process only data that was
            signed in the id_res message from the server.
        @type signed_only: bool

        @rtype: TeamsResponse
        @returns: A Launchpad teams response containing the data
            that was supplied with the C{id_res} response.
        """
        self = cls()
        self.ns_uri = self._getTeamsNS(success_response.message)
        if signed_only:
            args = success_response.getSignedNS(self.ns_uri)
        else:
            args = success_response.message.getArgs(self.ns_uri)

        if "is_member" in args:
            is_member_str = args["is_member"]
            self.is_member = is_member_str.split(',')

        return self

    fromSuccessResponse = classmethod(fromSuccessResponse)

    def getExtensionArgs(self):
        """Get the fields to put in the Launchpad teams namespace
        when adding them to an id_res message.

        @see: openid.extension
        """
        ns_args = {'is_member': ','.join(self.is_member)}
        return ns_args
