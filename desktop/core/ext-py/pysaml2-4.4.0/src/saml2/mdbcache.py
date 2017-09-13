#!/usr/bin/env python
import logging
from pymongo.mongo_client import MongoClient

__author__ = 'rolandh'

#import cjson
import time
from datetime import datetime

from saml2 import time_util
from saml2.cache import ToOld
from saml2.time_util import TIME_FORMAT

logger = logging.getLogger(__name__)


class Cache(object):
    def __init__(self, server=None, debug=0, db=None):
        if server:
            connection = MongoClient(server)
        else:
            connection = MongoClient()

        if db:
            self._db = connection[db]
        else:
            self._db = connection.pysaml2

        self._cache = self._db.collection
        self.debug = debug

    def delete(self, subject_id):
        self._cache.remove({"subject_id": subject_id})

    def get_identity(self, subject_id, entities=None,
                     check_not_on_or_after=True):
        """ Get all the identity information that has been received and
        are still valid about the subject.

        :param subject_id: The identifier of the subject
        :param entities: The identifiers of the entities whoes assertions are
            interesting. If the list is empty all entities are interesting.
        :return: A 2-tuple consisting of the identity information (a
            dictionary of attributes and values) and the list of entities
            whoes information has timed out.
        """
        res = {}
        oldees = []
        if not entities:
            for item in self._cache.find({"subject_id": subject_id}):
                try:
                    info = self._get_info(item, check_not_on_or_after)
                except ToOld:
                    oldees.append(item["entity_id"])
                    continue

                for key, vals in info["ava"].items():
                    try:
                        tmp = set(res[key]).union(set(vals))
                        res[key] = list(tmp)
                    except KeyError:
                        res[key] = vals
        else:
            for entity_id in entities:
                try:
                    info = self.get(subject_id, entity_id,
                                    check_not_on_or_after)
                except ToOld:
                    oldees.append(entity_id)
                    continue

                for key, vals in info["ava"].items():
                    try:
                        tmp = set(res[key]).union(set(vals))
                        res[key] = list(tmp)
                    except KeyError:
                        res[key] = vals

        return res, oldees

    def _get_info(self, item, check_not_on_or_after=True):
        """ Get session information about a subject gotten from a
        specified IdP/AA.

        :param item: Information stored
        :return: The session information as a dictionary
        """
        timestamp = item["timestamp"]

        if check_not_on_or_after and not time_util.not_on_or_after(timestamp):
            raise ToOld()

        try:
            return item["info"]
        except KeyError:
            return None

    def get(self, subject_id, entity_id, check_not_on_or_after=True):
        res = self._cache.find_one({"subject_id": subject_id,
                                    "entity_id": entity_id})
        if not res:
            return {}
        else:
            return self._get_info(res, check_not_on_or_after)

    def set(self, subject_id, entity_id, info, timestamp=0):
        """ Stores session information in the cache. Assumes that the subject_id
        is unique within the context of the Service Provider.

        :param subject_id: The subject identifier
        :param entity_id: The identifier of the entity_id/receiver of an
            assertion
        :param info: The session info, the assertion is part of this
        :param timestamp: A time after which the assertion is not valid.
        """

        if isinstance(timestamp, datetime) or isinstance(timestamp,
                                                         time.struct_time):
            timestamp = time.strftime(TIME_FORMAT, timestamp)

        doc = {"subject_id": subject_id,
               "entity_id": entity_id,
               "info": info,
               "timestamp": timestamp}

        _ = self._cache.insert(doc)

    def reset(self, subject_id, entity_id):
        """ Scrap the assertions received from a IdP or an AA about a special
        subject.

        :param subject_id: The subjects identifier
        :param entity_id: The identifier of the entity_id of the assertion
        :return:
        """
        self._cache.update({"subject_id": subject_id, "entity_id": entity_id},
                           {"$set": {"info": {}, "timestamp": 0}})

    def entities(self, subject_id):
        """ Returns all the entities of assertions for a subject, disregarding
        whether the assertion still is valid or not.

        :param subject_id: The identifier of the subject
        :return: A possibly empty list of entity identifiers
        """
        try:
            return [i["entity_id"] for i in self._cache.find({"subject_id":
                    subject_id})]
        except ValueError:
            return []

    def receivers(self, subject_id):
        """ Another name for entities() just to make it more logic in the IdP
            scenario """
        return self.entities(subject_id)

    def active(self, subject_id, entity_id):
        """ Returns the status of assertions from a specific entity_id.

        :param subject_id: The ID of the subject
        :param entity_id: The entity ID of the entity_id of the assertion
        :return: True or False depending on if the assertion is still
            valid or not.
        """

        item = self._cache.find_one({"subject_id": subject_id,
                                     "entity_id": entity_id})
        try:
            return time_util.not_on_or_after(item["timestamp"])
        except ToOld:
            return False

    def subjects(self):
        """ Return identifiers for all the subjects that are in the cache.

        :return: list of subject identifiers
        """

        subj = [i["subject_id"] for i in self._cache.find()]

        return list(set(subj))

    def update(self, subject_id, entity_id, ava):
        """ """
        item = self._cache.find_one({"subject_id": subject_id,
                                     "entity_id": entity_id})
        info = item["info"]
        info["ava"].update(ava)
        self._cache.update({"subject_id": subject_id, "entity_id": entity_id},
                           {"$set": {"info": info}})

    def valid_to(self, subject_id, entity_id, newtime):
        """ """
        self._cache.update({"subject_id": subject_id, "entity_id": entity_id},
                           {"$set": {"timestamp": newtime}})

    def clear(self):
        self._cache.remove()