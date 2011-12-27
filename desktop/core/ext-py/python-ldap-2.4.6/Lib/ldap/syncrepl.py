# -*- coding: utf-8 -*-
"""
ldap.syncrepl - for implementing syncrepl consumer (see RFC 4533)

See http://www.python-ldap.org/ for project details.

$Id: syncrepl.py,v 1.2 2011/10/26 19:40:17 stroeder Exp $
"""

#__all__ = [
#  '',
#  '',
#]

from uuid import UUID

# Imports from python-ldap 2.4+
import ldap.ldapobject
from ldap.controls import RequestControl,ResponseControl,KNOWN_RESPONSE_CONTROLS

# Imports from pyasn1
from pyasn1.type import tag,namedtype,namedval,univ,constraint
from pyasn1.codec.ber import encoder,decoder

__all__ = [ 'SyncreplConsumer' ]

# RFC 4533:
#
#       syncUUID ::= OCTET STRING (SIZE(16))
#       syncCookie ::= OCTET STRING

class syncUUID(univ.OctetString):
    subtypeSpec = constraint.ValueSizeConstraint(16,16)

class syncCookie(univ.OctetString):
    pass

# 2.2.  Sync Request Control
#
#    The Sync Request Control is an LDAP Control [RFC4511] where the
#    controlType is the object identifier 1.3.6.1.4.1.4203.1.9.1.1 and the
#    controlValue, an OCTET STRING, contains a BER-encoded
#    syncRequestValue.  The criticality field is either TRUE or FALSE.
#
#       syncRequestValue ::= SEQUENCE {
#           mode ENUMERATED {
#               -- 0 unused
#               refreshOnly       (1),
#               -- 2 reserved
#               refreshAndPersist (3)
#           },
#           cookie     syncCookie OPTIONAL,
#           reloadHint BOOLEAN DEFAULT FALSE
#       }
#
#    The Sync Request Control is only applicable to the SearchRequest
#    Message.

class syncRequestMode(univ.Enumerated):
    namedValues = namedval.NamedValues(
        ('refreshOnly', 1),
        ('refreshAndPersist', 3)
    )
    subtypeSpec = univ.Enumerated.subtypeSpec + constraint.SingleValueConstraint(1,3)

class syncRequestValue(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('mode', syncRequestMode()),
        namedtype.OptionalNamedType('cookie', syncCookie()),
        namedtype.DefaultedNamedType('reloadHint', univ.Boolean(False))
    )

class SyncRequestControl(RequestControl):
    controlType = '1.3.6.1.4.1.4203.1.9.1.1'

    def __init__(self, criticality=1, cookie=None, mode='refreshOnly', reloadHint=False):
        self.criticality = criticality
        self.cookie = cookie
        self.mode = mode
        self.reloadHint = reloadHint

    def encodeControlValue(self):
        r = syncRequestValue()
        r.setComponentByName('mode', syncRequestMode(self.mode))
        if self.cookie is not None:
            r.setComponentByName('cookie', syncCookie(self.cookie))
        if self.reloadHint:
            r.setComponentbyName('reloadHint', univ.Boolean(self.reloadHint))
        return encoder.encode(r)

# 2.3.  Sync State Control
#
#    The Sync State Control is an LDAP Control [RFC4511] where the
#    controlType is the object identifier 1.3.6.1.4.1.4203.1.9.1.2 and the
#    controlValue, an OCTET STRING, contains a BER-encoded syncStateValue.
#    The criticality is FALSE.
#
#       syncStateValue ::= SEQUENCE {
#           state ENUMERATED {
#               present (0),
#               add (1),
#               modify (2),
#               delete (3)
#           },
#           entryUUID syncUUID,
#           cookie    syncCookie OPTIONAL
#       }
#
#    The Sync State Control is only applicable to SearchResultEntry and
#    SearchResultReference Messages.

class syncStateOp(univ.Enumerated):
    namedValues = namedval.NamedValues(
        ('present', 0),
        ('add', 1),
        ('modify', 2),
        ('delete', 3)
    )
    subtypeSpec = univ.Enumerated.subtypeSpec + constraint.SingleValueConstraint(0,1,2,3)

class syncStateValue(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('state', syncStateOp()),
        namedtype.NamedType('entryUUID', syncUUID()),
        namedtype.OptionalNamedType('cookie', syncCookie())
    )

class SyncStateControl(ResponseControl):
    controlType = '1.3.6.1.4.1.4203.1.9.1.2'
    opnames = ( 'present', 'add', 'modify', 'delete' )

    def decodeControlValue(self, encodedControlValue):
        d = decoder.decode(encodedControlValue, asn1Spec = syncStateValue())
        state = d[0].getComponentByName('state')
        uuid = UUID(bytes=d[0].getComponentByName('entryUUID'))
        self.cookie = d[0].getComponentByName('cookie')
        self.state = self.__class__.opnames[int(state)]
        self.entryUUID = str(uuid)
        if self.cookie is not None:
            self.cookie = str(self.cookie)

KNOWN_RESPONSE_CONTROLS[SyncStateControl.controlType] = SyncStateControl

# 2.4.  Sync Done Control
#
#    The Sync Done Control is an LDAP Control [RFC4511] where the
#    controlType is the object identifier 1.3.6.1.4.1.4203.1.9.1.3 and the
#    controlValue contains a BER-encoded syncDoneValue.  The criticality
#    is FALSE (and hence absent).
#
#       syncDoneValue ::= SEQUENCE {
#           cookie          syncCookie OPTIONAL,
#           refreshDeletes  BOOLEAN DEFAULT FALSE
#       }
#
#    The Sync Done Control is only applicable to the SearchResultDone
#    Message.

class syncDoneValue(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.OptionalNamedType('cookie', syncCookie()),
        namedtype.DefaultedNamedType('refreshDeletes', univ.Boolean(False))
    )

class SyncDoneControl(ResponseControl):
    controlType = '1.3.6.1.4.1.4203.1.9.1.3'

    def decodeControlValue(self, encodedControlValue):
        d = decoder.decode(encodedControlValue, asn1Spec = syncDoneValue())
        self.cookie = d[0].getComponentByName('cookie')
        self.refreshDeletes = d[0].getComponentByName('refreshDeletes')
        if self.cookie is not None:
            self.cookie = str(self.cookie)
        if self.refreshDeletes is not None:
            self.refreshDeletes = bool(self.refreshDeletes)

KNOWN_RESPONSE_CONTROLS[SyncDoneControl.controlType] = SyncDoneControl


# 2.5.  Sync Info Message
#
#    The Sync Info Message is an LDAP Intermediate Response Message
#    [RFC4511] where responseName is the object identifier
#    1.3.6.1.4.1.4203.1.9.1.4 and responseValue contains a BER-encoded
#    syncInfoValue.  The criticality is FALSE (and hence absent).
#
#       syncInfoValue ::= CHOICE {
#           newcookie      [0] syncCookie,
#           refreshDelete  [1] SEQUENCE {
#               cookie         syncCookie OPTIONAL,
#               refreshDone    BOOLEAN DEFAULT TRUE
#           },
#           refreshPresent [2] SEQUENCE {
#               cookie         syncCookie OPTIONAL,
#               refreshDone    BOOLEAN DEFAULT TRUE
#           },
#           syncIdSet      [3] SEQUENCE {
#               cookie         syncCookie OPTIONAL,
#               refreshDeletes BOOLEAN DEFAULT FALSE,
#               syncUUIDs      SET OF syncUUID
#           }
#       }
#

class refreshDelete(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.OptionalNamedType('cookie', syncCookie()),
        namedtype.DefaultedNamedType('refreshDone', univ.Boolean(True))
    )

class refreshPresent(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.OptionalNamedType('cookie', syncCookie()),
        namedtype.DefaultedNamedType('refreshDone', univ.Boolean(True))
    )

class syncUUIDs(univ.SetOf):
    componentType = syncUUID()

class syncIdSet(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.OptionalNamedType('cookie', syncCookie()),
        namedtype.DefaultedNamedType('refreshDeletes', univ.Boolean(False)),
        namedtype.NamedType('syncUUIDs', syncUUIDs())
    )

class syncInfoValue(univ.Choice):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType(
            'newcookie',
            syncCookie().subtype(
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 0)
            )
        ),
        namedtype.NamedType(
            'refreshDelete',
            refreshDelete().subtype(
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 1)
            )
        ),
        namedtype.NamedType(
            'refreshPresent',
            refreshPresent().subtype(
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 2)
            )
        ),
        namedtype.NamedType(
            'syncIdSet',
            syncIdSet().subtype(
                implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 3)
            )
        )
    )

class SyncInfoMessage:
    responseName = '1.3.6.1.4.1.4203.1.9.1.4'

    def __init__(self, encodedMessage):
        d = decoder.decode(encodedMessage, asn1Spec = syncInfoValue())
        self.newcookie = None
        self.refreshDelete = None
        self.refreshPresent = None
        self.syncIdSet = None

        for attr in [ 'newcookie', 'refreshDelete', 'refreshPresent', 'syncIdSet']:
            comp = d[0].getComponentByName(attr)

            if comp is not None:

                if attr == 'newcookie':
                    self.newcookie = str(comp)
                    return

                val = dict()

                cookie = comp.getComponentByName('cookie')
                if cookie is not None:
                    val['cookie'] = str(cookie)

                if attr.startswith('refresh'):
                    val['refreshDone'] = bool(comp.getComponentByName('refreshDone'))
                elif attr == 'syncIdSet':
                    uuids = []
                    ids = comp.getComponentByName('syncUUIDs')
                    for i in range(len(ids)):
                        uuid = UUID(bytes=str(ids.getComponentByPosition(i)))
                        uuids.append(str(uuid))
                    val['syncUUIDs'] = uuids
                    val['refreshDeletes'] = bool(comp.getComponentByName('refreshDeletes'))

                setattr(self,attr,val)
                return


class SyncreplConsumer:
    """
    SyncreplConsumer - LDAP syncrepl consumer object.

    """

    def syncrepl_search(self, base, scope, mode='refreshOnly', cookie=None, **search_args):
        """
        Starts syncrepl search operation.

        base, scope, and **search_args are passed along to
        self.search_ext unmodified (aside from adding a Sync
        Request control to any serverctrls provided).

        mode provides syncrepl mode. Can be 'refreshOnly'
        to finish after synchronization, or
        'refreshAndPersist' to persist (continue to
        receive updates) after synchronization.

        cookie: an opaque value representing the replication
        state of the client.  Subclasses should override
        the syncrepl_set_cookie() and syncrepl_get_cookie()
        methods to store the cookie appropriately, rather than
        passing it.

        """
        if cookie is None:
            cookie = self.syncrepl_get_cookie()

        syncreq = SyncRequestControl(cookie=cookie, mode=mode)

        if 'serverctrls' in search_args:
            search_args['serverctrls'] += [syncreq]
        else:
            search_args['serverctrls'] = [syncreq]

        self.__refreshDone = False
        return self.search_ext(base, scope, **search_args)


    def syncrepl_poll(self, msgid=-1, timeout=None, all=0):
        """
        polls for and processes responses to the syncrepl_search() operation.
        Returns False when operation finishes, True if it is in progress, or
        raises an exception on error.

        If timeout is specified, raises ldap.TIMEOUT in the event of a timeout.

        If all is set to a nonzero value, poll() will return only when finished
        or when an exception is raised.

        """
        while True:
            type, msg, mid, ctrls, n, v = self.result4(
                    msgid=msgid, timeout=timeout,
                    add_intermediates=1, add_ctrls=1, all = 0
                    )

            if type == 101:
                # search result. This marks the end of a refreshOnly session.
                # look for a SyncDone control, save the cookie, and if necessary
                # delete non-present entries.
                for c in ctrls:
                    if c.__class__.__name__ != 'SyncDoneControl':
                        continue
                    self.syncrepl_present(None,refreshDeletes=c.refreshDeletes)
                    if c.cookie is not None:
                        self.syncrepl_set_cookie(c.cookie)

                return False

            elif type == 100:
                # search entry with associated SyncState control
                for m in msg:
                    dn, attrs, ctrls = m
                    for c in ctrls:
                        if c.__class__.__name__ != 'SyncStateControl':
                            continue
                        if c.state == 'present':
                            self.syncrepl_present([c.entryUUID])
                        elif c.state == 'delete':
                            self.syncrepl_delete([c.entryUUID])
                        else:
                            self.syncrepl_entry(dn, attrs, c.entryUUID)
                            if self.__refreshDone is False:
                                self.syncrepl_present([c.entryUUID])
                        if c.cookie is not None:
                            self.syncrepl_set_cookie(c.cookie)
                        break

            elif type == 121:
                # Intermediate message. If it is a SyncInfoMessage, parse it
                for m in msg:
                    rname, resp, ctrls = m
                    if rname != SyncInfoMessage.responseName:
                        continue
                    sim = SyncInfoMessage(resp)
                    if sim.newcookie is not None:
                        self.syncrepl_set_cookie(sim.newcookie)
                    elif sim.refreshPresent is not None:
                        self.syncrepl_present(None, refreshDeletes=False)
                        if 'cookie' in sim.refreshPresent:
                            self.syncrepl_set_cookie(sim.refreshPresent['cookie'])
                        self.__refreshDone=sim.refreshPresent['refreshDone']
                    elif sim.refreshDelete is not None:
                        self.syncrepl_present(None, refreshDeletes=True)
                        if 'cookie' in sim.refreshDelete:
                            self.syncrepl_set_cookie(sim.refreshDelete['cookie'])
                        self.__refreshDone=sim.refreshDelete['refreshDone']
                    elif sim.syncIdSet is not None:
                        if sim.syncIdSet['refreshDeletes'] is True:
                            self.syncrepl_delete(sim.syncIdSet['syncUUIDs'])
                        else:
                            self.syncrepl_present(sim.syncIdSet['syncUUIDs'])
                        if 'cookie' in sim.syncIdSet:
                            self.syncrepl_set_cookie(sim.syncIdSet['cookie'])
                        pass

            if all == 0:
                return True


    # virtual methods -- subclass must override these to do useful work

    def syncrepl_set_cookie(self, cookie):
        """
        Called by syncrepl_poll() to store a new cookie provided by the server.
        """
        pass

    def syncrepl_get_cookie(self):
        """
        Called by syncrepl_search() to retreive the cookie stored by syncrepl_set_cookie()
        """
        pass

    def syncrepl_present(self, uuids, refreshDeletes=False):
        """
        Called by syncrepl_poll() whenever entry UUIDs are presented to the client.
        syncrepl_present() is given a list of entry UUIDs (uuids) and a flag
        (refreshDeletes) which indicates whether the server explicitly deleted
        non-present entries during the refresh operation.

        If called with a list of uuids, the syncrepl_present() implementation
        should record those uuids as present in the directory.

        If called with uuids set to None and refreshDeletes set to False,
        syncrepl_present() should delete all non-present entries from the local
        mirror, and reset the list of recorded uuids.

        If called with uuids set to None and refreshDeletes set to True,
        syncrepl_present() should reset the list of recorded uuids, without
        deleting any entries.

        """
        pass

    def syncrepl_delete(self, uuids):
        """
        Called by syncrepl_poll() to delete entries. A list
        of UUIDs of the entries to be deleted is given in the
        uuids parameter.

        """
        pass

    def syncrepl_entry(self, dn, attrs, uuid):
        """
        Called by syncrepl_poll() for any added or modified entries.

        The provided uuid is used to identify the provided entry in
        any future modification (including dn modification), deletion,
        and presentation operations.

        """
        pass
