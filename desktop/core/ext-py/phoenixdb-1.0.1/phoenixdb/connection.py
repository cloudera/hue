# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import uuid
import weakref

from phoenixdb import errors
from phoenixdb.cursor import Cursor
from phoenixdb.errors import ProgrammingError
from phoenixdb.meta import Meta

__all__ = ['Connection']

logger = logging.getLogger(__name__)

AVATICA_PROPERTIES = ('autoCommit', 'autocommit', 'readOnly', 'readonly', 'transactionIsolation',
                      'catalog', 'schema')


class Connection(object):
    """Database connection.

    You should not construct this object manually, use :func:`~phoenixdb.connect` instead.
    """

    cursor_factory = None
    """
    The default cursor factory used by :meth:`cursor` if the parameter is not specified.
    """

    def __init__(self, client, cursor_factory=None, **kwargs):
        self._client = client
        self._closed = False
        if cursor_factory is not None:
            self.cursor_factory = cursor_factory
        else:
            self.cursor_factory = Cursor
        self._cursors = []
        self._phoenix_props, avatica_props_init = Connection._map_conn_props(kwargs)
        self.open()

        # TODO we could probably optimize it away if the defaults are not changed
        self.set_session(**avatica_props_init)

    def __del__(self):
        if not self._closed:
            self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self._closed:
            self.close()

    @staticmethod
    def _default_avatica_props():
        return {'autoCommit': False,
                'readOnly': False,
                'transactionIsolation': 0,
                'catalog': '',
                'schema': ''}

    @staticmethod
    def _map_conn_props(conn_props):
        """Sorts and prepocesses args that should be passed to Phoenix and Avatica"""

        avatica_props = dict([(k, conn_props[k]) for k in conn_props.keys() if k in AVATICA_PROPERTIES])
        phoenix_props = dict([(k, conn_props[k]) for k in conn_props.keys() if k not in AVATICA_PROPERTIES])
        avatica_props = Connection._map_legacy_avatica_props(avatica_props)

        return (phoenix_props, avatica_props)

    @staticmethod
    def _map_legacy_avatica_props(props):
        if 'autocommit' in props:
            props['autoCommit'] = bool(props.pop('autocommit'))
        if 'readonly' in props:
            props['readOnly'] = bool(props.pop('readonly'))
        return props

    def open(self):
        """Opens the connection."""
        self._id = str(uuid.uuid4())
        self._client.open_connection(self._id, info=self._phoenix_props)

    def close(self):
        """Closes the connection.
        No further operations are allowed, either on the connection or any
        of its cursors, once the connection is closed.

        If the connection is used in a ``with`` statement, this method will
        be automatically called at the end of the ``with`` block.
        """
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        for cursor_ref in self._cursors:
            cursor = cursor_ref()
            if cursor is not None and not cursor._closed:
                cursor.close()
        self._client.close_connection(self._id)
        self._client.close()
        self._closed = True

    @property
    def closed(self):
        """Read-only attribute specifying if the connection is closed or not."""
        return self._closed

    def commit(self):
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        self._client.commit(self._id)

    def rollback(self):
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        self._client.rollback(self._id)

    def cursor(self, cursor_factory=None):
        """Creates a new cursor.

        :param cursor_factory:
            This argument can be used to create non-standard cursors.
            The class returned must be a subclass of
            :class:`~phoenixdb.cursor.Cursor` (for example :class:`~phoenixdb.cursor.DictCursor`).
            A default factory for the connection can also be specified using the
            :attr:`cursor_factory` attribute.

        :returns:
            A :class:`~phoenixdb.cursor.Cursor` object.
        """
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        cursor = (cursor_factory or self.cursor_factory)(self)
        self._cursors.append(weakref.ref(cursor, self._cursors.remove))
        return cursor

    def set_session(self, **props):
        """Sets one or more parameters in the current connection.

        :param autocommit:
            Switch the connection to autocommit mode.

        :param readonly:
            Switch the connection to read-only mode.
        """
        props = Connection._map_legacy_avatica_props(props)
        self._avatica_props = self._client.connection_sync_dict(self._id, props)

    @property
    def autocommit(self):
        """Read/write attribute for switching the connection's autocommit mode."""
        return self._avatica_props['autoCommit']

    @autocommit.setter
    def autocommit(self, value):
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        self._avatica_props = self._client.connection_sync_dict(self._id, {'autoCommit': bool(value)})

    @property
    def readonly(self):
        """Read/write attribute for switching the connection's readonly mode."""
        return self._avatica_props['readOnly']

    @readonly.setter
    def readonly(self, value):
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        self._avatica_props = self._client.connection_sync_dict(self._id, {'readOnly': bool(value)})

    @property
    def transactionisolation(self):
        return self._avatica_props['_transactionIsolation']

    @transactionisolation.setter
    def transactionisolation(self, value):
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        self._avatica_props = self._client.connection_sync_dict(self._id, {'transactionIsolation': bool(value)})

    def meta(self):
        """Creates a new meta.

        :returns:
            A :class:`~phoenixdb.meta` object.
        """
        if self._closed:
            raise ProgrammingError('The connection is already closed.')
        meta = Meta(self)
        return meta


for name in errors.__all__:
    setattr(Connection, name, getattr(errors, name))
