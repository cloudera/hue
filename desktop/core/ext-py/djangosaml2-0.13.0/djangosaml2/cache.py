# Copyright (C) 2011-2012 Yaco Sistemas (http://www.yaco.es)
# Copyright (C) 2010 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from saml2.cache import Cache
from saml2.ident import code, decode


class DjangoSessionCacheAdapter(dict):
    """A cache of things that are stored in the Django Session"""

    key_prefix = '_saml2'

    def __init__(self, django_session, key_suffix):
        self.session = django_session
        self.key = self.key_prefix + key_suffix

        super(DjangoSessionCacheAdapter, self).__init__(self._get_objects())

    def _get_objects(self):
        return self.session.get(self.key, {})

    def _set_objects(self, objects):
        self.session[self.key] = objects

    def sync(self):
        objs = {}
        objs.update(self)
        self._set_objects(objs)


class OutstandingQueriesCache(object):
    """Handles the queries that have been sent to the IdP and have not
    been replied yet.
    """

    def __init__(self, django_session):
        self._db = DjangoSessionCacheAdapter(django_session,
                                             '_outstanding_queries')

    def outstanding_queries(self):
        return self._db._get_objects()

    def set(self, saml2_session_id, came_from):
        self._db[saml2_session_id] = came_from
        self._db.sync()

    def delete(self, saml2_session_id):
        if saml2_session_id in self._db:
            del self._db[saml2_session_id]
            self._db.sync()


class IdentityCache(Cache):
    """Handles information about the users that have been succesfully
    logged in.

    This information is useful because when the user logs out we must
    know where does he come from in order to notify such IdP/AA.

    The current implementation stores this information in the Django session.
    """

    def __init__(self, django_session):
        self._db = DjangoSessionCacheAdapter(django_session, '_identities')
        self._sync = True

    def get(self, name_id, entity_id, *args, **kwargs):
        info = super(IdentityCache, self).get(name_id, entity_id, *args, **kwargs)
        try:
            name_id = info['name_id']
        except KeyError:
            pass
        else:
            info = dict(info)
            info['name_id'] = decode(name_id)

        return info

    def set(self, name_id, entity_id, info, *args, **kwargs):
        try:
            name_id = info['name_id']
        except KeyError:
            pass
        else:
            info = dict(info)
            info['name_id'] = code(name_id)
        return super(IdentityCache, self).set(name_id, entity_id, info, *args, **kwargs)


class StateCache(DjangoSessionCacheAdapter):
    """Store state information that is needed to associate a logout
    request with its response.
    """

    def __init__(self, django_session):
        super(StateCache, self).__init__(django_session, '_state')
