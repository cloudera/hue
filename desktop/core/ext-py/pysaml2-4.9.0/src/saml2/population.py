import logging

import six

from saml2.cache import Cache

logger = logging.getLogger(__name__)


class Population(object):
    def __init__(self, cache=None):
        if cache:
            if isinstance(cache, six.string_types):
                self.cache = Cache(cache)
            else:
                self.cache = cache
        else:
            self.cache = Cache()

    def add_information_about_person(self, session_info):
        """If there already are information from this source in the cache
        this function will overwrite that information"""

        session_info = dict(session_info)
        name_id = session_info["name_id"]
        issuer = session_info.pop("issuer")
        self.cache.set(name_id, issuer, session_info,
                       session_info["not_on_or_after"])
        return name_id

    def stale_sources_for_person(self, name_id, sources=None):
        """

        :param name_id: Identifier of the subject, a NameID instance
        :param sources: Sources for information about the subject
        :return:
        """
        if not sources:  # assume that all the members has be asked
                         # once before, hence they are represented in the cache
            sources = self.cache.entities(name_id)
        sources = [m for m in sources if not self.cache.active(name_id, m)]
        return sources

    def issuers_of_info(self, name_id):
        return self.cache.entities(name_id)

    def get_identity(self, name_id, entities=None, check_not_on_or_after=True):
        return self.cache.get_identity(name_id, entities, check_not_on_or_after)

    def get_info_from(self, name_id, entity_id, check_not_on_or_after=True):
        return self.cache.get(name_id, entity_id, check_not_on_or_after)

    def subjects(self):
        """Returns the name id's for all the persons in the cache"""
        return self.cache.subjects()

    def remove_person(self, name_id):
        self.cache.delete(name_id)

    def get_entityid(self, name_id, source_id, check_not_on_or_after=True):
        try:
            return self.cache.get(name_id, source_id, check_not_on_or_after)[
                "name_id"]
        except (KeyError, ValueError):
            return ""

    def sources(self, name_id):
        return self.cache.entities(name_id)
