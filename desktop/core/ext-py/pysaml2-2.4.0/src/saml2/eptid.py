# An eduPersonTargetedID comprises
# the entity name of the identity provider, the entity name of the service
# provider, and a opaque string value.
# These strings are separated by "!" symbols. This form is advocated by
# Internet2 and may overtake the other form in due course.

import hashlib
import shelve

import logging

logger = logging.getLogger(__name__)


class Eptid(object):
    def __init__(self, secret):
        self._db = {}
        self.secret = secret

    def make(self, idp, sp, args):
        md5 = hashlib.md5()
        for arg in args:
            md5.update(arg.encode("utf-8"))
        md5.update(sp)
        md5.update(self.secret)
        md5.digest()
        hashval = md5.hexdigest()
        return "!".join([idp, sp, hashval])

    def __getitem__(self, key):
        return self._db[key]

    def __setitem__(self, key, value):
        self._db[key] = value

    def get(self, idp, sp, *args):
        # key is a combination of sp_entity_id and object id
        key = ("__".join([sp, args[0]])).encode("utf-8")
        try:
            return self[key]
        except KeyError:
            val = self.make(idp, sp, args)
            self[key] = val
            return val


class EptidShelve(Eptid):
    def __init__(self, secret, filename):
        Eptid.__init__(self, secret)
        self._db = shelve.open(filename, writeback=True)
