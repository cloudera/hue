#!/usr/bin/env python

import logging
import shelve

from saml2 import SAMLError
from saml2 import time_util
from saml2.ident import code
from saml2.ident import decode


logger = logging.getLogger(__name__)

# The assumption is that any subject may consist of data
# gathered from several different sources, all with their own
# timeout time.


class ToOld(SAMLError):
    pass


class TooOld(ToOld):
    pass


class CacheError(SAMLError):
    pass


class Cache:
    def __init__(self, filename=None):
        if filename:
            self._db = shelve.open(filename, writeback=True, protocol=2)
            self._sync = True
        else:
            self._db = {}
            self._sync = False

    def delete(self, name_id):
        """

        :param name_id: The subject identifier, a NameID instance
        """
        del self._db[code(name_id)]

        if self._sync:
            try:
                self._db.sync()
            except AttributeError:
                pass

    def get_identity(self, name_id, entities=None, check_not_on_or_after=True):
        """Get all the identity information that has been received and
        are still valid about the subject.

        :param name_id: The subject identifier, a NameID instance
        :param entities: The identifiers of the entities whoes assertions are
            interesting. If the list is empty all entities are interesting.
        :return: A 2-tuple consisting of the identity information (a
            dictionary of attributes and values) and the list of entities
            whoes information has timed out.
        """
        if not entities:
            try:
                cni = code(name_id)
                entities = self._db[cni].keys()
            except KeyError:
                return {}, []

        res = {}
        oldees = []
        for entity_id in entities:
            try:
                info = self.get(name_id, entity_id, check_not_on_or_after)
            except TooOld:
                oldees.append(entity_id)
                continue

            if not info:
                oldees.append(entity_id)
                continue

            for key, vals in info["ava"].items():
                try:
                    tmp = set(res[key]).union(set(vals))
                    res[key] = list(tmp)
                except KeyError:
                    res[key] = vals
        return res, oldees

    def get(self, name_id, entity_id, check_not_on_or_after=True):
        """Get session information about a subject gotten from a
        specified IdP/AA.

        :param name_id: The subject identifier, a NameID instance
        :param entity_id: The identifier of the entity_id
        :param check_not_on_or_after: if True it will check if this
             subject is still valid or if it is too old. Otherwise it
             will not check this. True by default.
        :return: The session information
        """
        cni = code(name_id)
        (timestamp, info) = self._db[cni][entity_id]
        info = info.copy()
        if check_not_on_or_after and time_util.after(timestamp):
            raise TooOld(f"past {str(timestamp)}")

        if "name_id" in info and isinstance(info["name_id"], str):
            info["name_id"] = decode(info["name_id"])
        return info or None

    def set(self, name_id, entity_id, info, not_on_or_after=0):
        """Stores session information in the cache. Assumes that the name_id
        is unique within the context of the Service Provider.

        :param name_id: The subject identifier, a NameID instance
        :param entity_id: The identifier of the entity_id/receiver of an
            assertion
        :param info: The session info, the assertion is part of this
        :param not_on_or_after: A time after which the assertion is not valid.
        """
        info = dict(info)
        if "name_id" in info and not isinstance(info["name_id"], str):
            # make friendly to (JSON) serialization
            info["name_id"] = code(name_id)

        cni = code(name_id)
        if cni not in self._db:
            self._db[cni] = {}

        self._db[cni][entity_id] = (not_on_or_after, info)
        if self._sync:
            try:
                self._db.sync()
            except AttributeError:
                pass

    def reset(self, name_id, entity_id):
        """Scrap the assertions received from a IdP or an AA about a special
        subject.

        :param name_id: The subject identifier, a NameID instance
        :param entity_id: The identifier of the entity_id of the assertion
        :return:
        """
        self.set(name_id, entity_id, {}, 0)

    def entities(self, name_id):
        """Returns all the entities of assertions for a subject, disregarding
        whether the assertion still is valid or not.

        :param name_id: The subject identifier, a NameID instance
        :return: A possibly empty list of entity identifiers
        """
        cni = code(name_id)
        return list(self._db[cni].keys())

    def receivers(self, name_id):
        """Another name for entities() just to make it more logic in the IdP
        scenario"""
        return self.entities(name_id)

    def active(self, name_id, entity_id):
        """Returns the status of assertions from a specific entity_id.

        :param name_id: The ID of the subject
        :param entity_id: The entity ID of the entity_id of the assertion
        :return: True or False depending on if the assertion is still
            valid or not.
        """
        try:
            cni = code(name_id)
            (timestamp, info) = self._db[cni][entity_id]
        except KeyError:
            return False

        if not info:
            return False
        else:
            return time_util.not_on_or_after(timestamp)

    def subjects(self):
        """Return identifiers for all the subjects that are in the cache.

        :return: list of subject identifiers
        """
        return [decode(c) for c in self._db.keys()]
