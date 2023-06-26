import ldap
from ldap import SCOPE_SUBTREE
from saml2.userinfo import UserInfo


class UserInfoLDAP(UserInfo):
    def __init__(self, uri, base, filter_pattern, scope=SCOPE_SUBTREE,
                 tls=False, user="", passwd="", attr=None, attrsonly=False):
        UserInfo.__init__(self)
        self.ldapuri = uri
        self.base = base
        self.filter_pattern = filter_pattern
        self.scope = scope
        self.tls = tls
        self.attr = attr
        self.attrsonly = attrsonly
        self.ld = ldap.initialize(uri)
        self.ld.protocol_version = ldap.VERSION3
        self.ld.simple_bind_s(user, passwd)

    def __call__(self, userid, base="", filter_pattern="", scope=SCOPE_SUBTREE,
                 tls=False, attr=None, attrsonly=False, **kwargs):

        if filter_pattern:
            _filter = filter_pattern % userid
        else:
            _filter = self.filter_pattern % userid

        _base = base or self.base
        _scope = scope or self.scope
        _attr = attr or self.attr
        _attrsonly = attrsonly or self.attrsonly
        arg = [_base, _scope, _filter, _attr, _attrsonly]
        res = self.ld.search_s(*arg)
        # should only be one entry and the information per entry is
        # the tuple (dn, ava)
        return res[0][1]