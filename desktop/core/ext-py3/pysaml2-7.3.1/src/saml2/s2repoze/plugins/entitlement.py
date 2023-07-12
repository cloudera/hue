#!/usr/bin/env python
import shelve

# from repoze.who.interfaces import IChallenger, IIdentifier, IAuthenticator
from repoze.who.interfaces import IMetadataProvider
from zope.interface import implements


class EntitlementMetadataProvider:

    implements(IMetadataProvider)

    def __init__(self, filename, key_attribute):
        # Means I have to do explicit syncs on writes, but also
        # that it's faster on reads since it will cache data
        self._store = shelve.open(filename, writeback=True)
        self.key_attribute = key_attribute

    def keys(self):
        return self._store.keys()

    def get(self, user, attribute):
        return self._store[user][attribute]

    def set(self, user, attribute, value):
        if user not in self._store:
            self._store[user] = {}

        self._store[user][attribute] = value
        self._store.sync()

    def part_of(self, user, virtualorg):
        if virtualorg in self._store[user]["entitlement"]:
            return True
        else:
            return False

    def get_entitlement(self, user, virtualorg):
        try:
            return self._store[user]["entitlement"][virtualorg]
        except KeyError:
            return []

    def store_entitlement(self, user, virtualorg, entitlement=None):
        if user not in self._store:
            self._store[user] = {"entitlement": {}}
        elif "entitlement" not in self._store[user]:
            self._store[user]["entitlement"] = {}

        if entitlement is None:
            entitlement = []
        self._store[user]["entitlement"][virtualorg] = entitlement
        self._store.sync()

    def add_metadata(self, environ, identity):
        # logger = environ.get('repoze.who.logger','')
        try:
            user = self._store[identity.get("repoze.who.userid")]
        except KeyError:
            return

        try:
            vorg = environ["myapp.vo"]
            try:
                ents = user["entitlement"][vorg]
                identity["user"] = {"entitlement": [f"{vorg}:{e}" for e in ents]}
            except KeyError:
                pass
        except KeyError:
            res = []
            for vorg, ents in user["entitlement"].items():
                res.extend([f"{vorg}:{e}" for e in ents])
            identity["user"] = res


def make_plugin(filename, key_attribute=""):
    return EntitlementMetadataProvider(filename, key_attribute)
