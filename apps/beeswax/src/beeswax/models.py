#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import datetime
import json
import logging

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse
from django.utils.translation import ugettext as _, ugettext_lazy as _t

from enum import Enum
from TCLIService.ttypes import TSessionHandle, THandleIdentifier, TOperationState, TOperationHandle, TOperationType

from desktop.redaction import global_redaction_engine
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document
from librdbms.server import dbms as librdbms_dbms

from beeswax.design import HQLdesign


LOG = logging.getLogger(__name__)

QUERY_SUBMISSION_TIMEOUT = datetime.timedelta(0, 60 * 60)               # 1 hour

# Constants for DB fields, hue ini
BEESWAX = 'beeswax'
HIVE_SERVER2 = 'hiveserver2'
QUERY_TYPES = (HQL, IMPALA, RDBMS, SPARK) = range(4)

class QueryHistory(models.Model):
  """
  Holds metadata about all queries that have been executed.
  """
  class STATE(Enum):
    submitted = 0
    running = 1
    available = 2
    failed = 3
    expired = 4

  SERVER_TYPE = ((BEESWAX, 'Beeswax'), (HIVE_SERVER2, 'Hive Server 2'),
                 (librdbms_dbms.MYSQL, 'MySQL'), (librdbms_dbms.POSTGRESQL, 'PostgreSQL'),
                 (librdbms_dbms.SQLITE, 'sqlite'), (librdbms_dbms.ORACLE, 'oracle'))

  owner = models.ForeignKey(User, db_index=True)
  query = models.TextField()

  last_state = models.IntegerField(db_index=True)
  has_results = models.BooleanField(default=False)          # If true, this query will eventually return tabular results.
  submission_date = models.DateTimeField(auto_now_add=True)
  # In case of multi statements in a query, these are the id of the currently running statement
  server_id = models.CharField(max_length=1024, null=True)  # Aka secret, only query in the "submitted" state is allowed to have no server_id
  server_guid = models.CharField(max_length=1024, null=True, default=None)
  statement_number = models.SmallIntegerField(default=0)    # The index of the currently running statement
  operation_type = models.SmallIntegerField(null=True)
  modified_row_count = models.FloatField(null=True)
  log_context = models.CharField(max_length=1024, null=True)

  server_host = models.CharField(max_length=128, help_text=_('Host of the query server.'), default='')
  server_port = models.PositiveIntegerField(help_text=_('Port of the query server.'), default=10000)
  server_name = models.CharField(max_length=128, help_text=_('Name of the query server.'), default='')
  server_type = models.CharField(max_length=128, help_text=_('Type of the query server.'), default=BEESWAX, choices=SERVER_TYPE)
  query_type = models.SmallIntegerField(help_text=_('Type of the query.'), default=HQL, choices=((HQL, 'HQL'), (IMPALA, 'IMPALA')))

  design = models.ForeignKey('SavedQuery', to_field='id', null=True) # Some queries (like read/create table) don't have a design
  notify = models.BooleanField(default=False)                        # Notify on completion

  is_redacted = models.BooleanField(default=False)
  extra = models.TextField(default='{}')                   # Json fields for extra properties
  is_cleared = models.BooleanField(default=False)

  class Meta:
    ordering = ['-submission_date']

  @staticmethod
  def build(*args, **kwargs):
    return HiveServerQueryHistory(*args, **kwargs)

  def get_full_object(self):
    return HiveServerQueryHistory.objects.get(id=self.id)

  @staticmethod
  def get(id):
    return HiveServerQueryHistory.objects.get(id=id)

  @staticmethod
  def get_type_name(query_type):
    if query_type == IMPALA:
      return 'impala'
    elif query_type == RDBMS:
      return 'rdbms'
    elif query_type == SPARK:
      return 'spark'
    else:
      return 'beeswax'

  def get_query_server_config(self):
    from beeswax.server.dbms import get_query_server_config

    query_server = get_query_server_config(QueryHistory.get_type_name(self.query_type))
    query_server.update({
        'server_name': self.server_name,
#         'server_host': self.server_host, # Always use the live server configuration as the session is currently tied to the connection
#         'server_port': int(self.server_port),
        'server_type': self.server_type,
    })

    return query_server


  def get_current_statement(self):
    if self.design is not None:
      design = self.design.get_design()
      return design.get_query_statement(self.statement_number)
    else:
      return self.query

  def refresh_design(self, hql_query):
    # Refresh only HQL query part
    query = self.design.get_design()
    query.hql_query = hql_query
    self.design.data = query.dumps()
    self.query = hql_query

  def is_finished(self):
    is_statement_finished = not self.is_running()

    if self.design is not None:
      design = self.design.get_design()
      return is_statement_finished and self.statement_number + 1 == design.statement_count # Last statement
    else:
      return is_statement_finished

  def is_running(self):
    return self.last_state in (QueryHistory.STATE.running.value, QueryHistory.STATE.submitted.value)

  def is_success(self):
    return self.last_state in (QueryHistory.STATE.available.value,)

  def is_failure(self):
    return self.last_state in (QueryHistory.STATE.expired.value, QueryHistory.STATE.failed.value)

  def is_expired(self):
    return self.last_state in (QueryHistory.STATE.expired.value,)

  def set_to_running(self):
    self.last_state = QueryHistory.STATE.running.value

  def set_to_failed(self):
    self.last_state = QueryHistory.STATE.failed.value

  def set_to_available(self):
    self.last_state = QueryHistory.STATE.available.value

  def set_to_expired(self):
    self.last_state = QueryHistory.STATE.expired.value

  def save(self, *args, **kwargs):
    """
    Override `save` to optionally mask out the query from being saved to the
    database. This is because if the beeswax database contains sensitive
    information like personally identifiable information, that information
    could be leaked into the Hue database and logfiles.
    """

    if global_redaction_engine.is_enabled():
      redacted_query = global_redaction_engine.redact(self.query)

      if self.query != redacted_query:
        self.query = redacted_query
        self.is_redacted = True

    super(QueryHistory, self).save(*args, **kwargs)

  def update_extra(self, key, val):
    extra = json.loads(self.extra)
    extra[key] = val
    self.extra = json.dumps(extra)

  def get_extra(self, key):
    return json.loads(self.extra).get(key)


def make_query_context(type, info):
  """
  ``type`` is one of "table" and "design", and ``info`` is the table name or design id.
  Returns a value suitable for GET param.
  """
  if type == 'table':
    return "%s:%s" % (type, info)
  elif type == 'design':
    # Use int() to validate that info is a number
    return "%s:%s" % (type, int(info))
  LOG.error("Invalid query context type: %s" % (type,))
  return ''                                     # Empty string is safer than None


class HiveServerQueryHistory(QueryHistory):
  # Map from (thrift) server state
  STATE_MAP = {
    TOperationState.INITIALIZED_STATE : QueryHistory.STATE.submitted,
    TOperationState.RUNNING_STATE     : QueryHistory.STATE.running,
    TOperationState.FINISHED_STATE    : QueryHistory.STATE.available,
    TOperationState.CANCELED_STATE    : QueryHistory.STATE.failed,
    TOperationState.CLOSED_STATE      : QueryHistory.STATE.expired,
    TOperationState.ERROR_STATE       : QueryHistory.STATE.failed,
    TOperationState.UKNOWN_STATE      : QueryHistory.STATE.failed,
    TOperationState.PENDING_STATE     : QueryHistory.STATE.submitted,
  }

  node_type = HIVE_SERVER2

  class Meta:
    proxy = True

  def get_handle(self):
    secret, guid = HiveServerQueryHandle.get_decoded(self.server_id, self.server_guid)

    return HiveServerQueryHandle(secret=secret,
                                 guid=guid,
                                 has_result_set=self.has_results,
                                 operation_type=self.operation_type,
                                 modified_row_count=self.modified_row_count)

  def save_state(self, new_state):
    self.last_state = new_state.value
    self.save()

  @classmethod
  def is_canceled(self, res):
    return res.operationState in (TOperationState.CANCELED_STATE, TOperationState.CLOSED_STATE)


class SavedQuery(models.Model):
  """
  Stores the query that people have save or submitted.

  Note that this used to be called QueryDesign. Any references to 'design'
  probably mean a SavedQuery.
  """
  DEFAULT_NEW_DESIGN_NAME = _('My saved query')
  AUTO_DESIGN_SUFFIX = _(' (new)')
  TYPES = QUERY_TYPES
  TYPES_MAPPING = {'beeswax': HQL, 'hql': HQL, 'impala': IMPALA, 'rdbms': RDBMS, 'spark': SPARK}

  type = models.IntegerField(null=False)
  owner = models.ForeignKey(User, db_index=True)
  # Data is a json of dictionary. See the beeswax.design module.
  data = models.TextField(max_length=65536)
  name = models.CharField(max_length=80)
  desc = models.TextField(max_length=1024)
  mtime = models.DateTimeField(auto_now=True)
  # An auto design is a place-holder for things users submit but not saved.
  # We still want to store it as a design to allow users to save them later.
  is_auto = models.BooleanField(default=False, db_index=True)
  is_trashed = models.BooleanField(default=False, db_index=True, verbose_name=_t('Is trashed'),
                                   help_text=_t('If this query is trashed.'))

  is_redacted = models.BooleanField(default=False)

  doc = GenericRelation(Document, related_query_name='hql_doc')

  class Meta:
    ordering = ['-mtime']

  def get_design(self):
    try:
      return HQLdesign.loads(self.data)
    except ValueError:
      # data is empty
      pass

  def clone(self, new_owner=None):
    if new_owner is None:
      new_owner = self.owner
    design = SavedQuery(type=self.type, owner=new_owner)
    design.data = self.data
    design.name = self.name
    design.desc = self.desc
    design.is_auto = self.is_auto
    return design

  @classmethod
  def create_empty(cls, app_name, owner, data):
    query_type = SavedQuery.TYPES_MAPPING[app_name]
    design = SavedQuery(owner=owner, type=query_type)
    design.name = SavedQuery.DEFAULT_NEW_DESIGN_NAME
    design.desc = ''

    if global_redaction_engine.is_enabled():
      design.data = global_redaction_engine.redact(data)
    else:
      design.data = data

    design.is_auto = True
    design.save()

    Document.objects.link(design, owner=design.owner, extra=design.type, name=design.name, description=design.desc)
    design.doc.get().add_to_history()

    return design

  @staticmethod
  def get(id, owner=None, type=None):
    """
    get(id, owner=None, type=None) -> SavedQuery object

    Checks that the owner and type match (when given).
    May raise PopupException (type/owner mismatch).
    May raise SavedQuery.DoesNotExist.
    """
    try:
      design = SavedQuery.objects.get(id=id)
    except SavedQuery.DoesNotExist, err:
      msg = _('Cannot retrieve query id %(id)s.') % {'id': id}
      raise err

    if owner is not None and design.owner != owner:
      msg = _('Query id %(id)s does not belong to user %(user)s.') % {'id': id, 'user': owner}
      LOG.error(msg)
      raise PopupException(msg)

    if type is not None and design.type != type:
      msg = _('Type mismatch for design id %(id)s (owner %(owner)s) - Expected %(expected_type)s, got %(real_type)s.') % \
            {'id': id, 'owner': owner, 'expected_type': design.type, 'real_type': type}
      LOG.error(msg)
      raise PopupException(msg)

    return design

  def __str__(self):
    return '%s %s' % (self.name, self.owner)

  def get_query_context(self):
    try:
      return make_query_context('design', self.id)
    except:
      LOG.exception('failed to make query context')
      return ""

  def get_absolute_url(self):
    return reverse(QueryHistory.get_type_name(self.type) + ':execute_design', kwargs={'design_id': self.id})

  def save(self, *args, **kwargs):
    """
    Override `save` to optionally mask out the query from being saved to the
    database. This is because if the beeswax database contains sensitive
    information like personally identifiable information, that information
    could be leaked into the Hue database and logfiles.
    """

    if global_redaction_engine.is_enabled():
      data = json.loads(self.data)

      try:
        query = data['query']['query']
      except KeyError:
        pass
      else:
        redacted_query = global_redaction_engine.redact(query)

        if query != redacted_query:
          data['query']['query'] = redacted_query
          self.is_redacted = True
          self.data = json.dumps(data)

    super(SavedQuery, self).save(*args, **kwargs)


class SessionManager(models.Manager):

  def get_session(self, user, application='beeswax', filter_open=True):
    try:
      q = self.filter(owner=user, application=application).exclude(guid='').exclude(secret='')
      if filter_open:
        q = q.filter(status_code=0)
      return q.latest("last_used")
    except Session.DoesNotExist, e:
      return None

  def get_n_sessions(self, user, n, application='beeswax', filter_open=True):
    q = self.filter(owner=user, application=application).exclude(guid='').exclude(secret='')
    if filter_open:
      q = q.filter(status_code=0)
    return q.order_by("-last_used")[0:n]


class Session(models.Model):
  """
  A sessions is bound to a user and an application (e.g. Bob with the Impala application).
  """
  owner = models.ForeignKey(User, db_index=True)
  status_code = models.PositiveSmallIntegerField()  # ttypes.TStatusCode
  secret = models.TextField(max_length='100')
  guid = models.TextField(max_length='100')
  server_protocol_version = models.SmallIntegerField(default=0)
  last_used = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_t('Last used'))
  application = models.CharField(max_length=128, help_text=_t('Application we communicate with.'), default='beeswax')
  properties = models.TextField(default='{}')

  objects = SessionManager()

  def get_handle(self):
    secret, guid = HiveServerQueryHandle.get_decoded(secret=self.secret, guid=self.guid)

    handle_id = THandleIdentifier(secret=secret, guid=guid)
    return TSessionHandle(sessionId=handle_id)

  def get_properties(self):
    return json.loads(self.properties) if self.properties else {}

  def get_formatted_properties(self):
    return [dict({'key': key, 'value': value}) for key, value in self.get_properties().items()]

  def __str__(self):
    return '%s %s' % (self.owner, self.last_used)


class QueryHandle(object):
  def __init__(self, secret=None, guid=None, operation_type=None, has_result_set=None, modified_row_count=None, log_context=None, session_guid=None):
    self.secret = secret
    self.guid = guid
    self.operation_type = operation_type
    self.has_result_set = has_result_set
    self.modified_row_count = modified_row_count
    self.log_context = log_context

  def is_valid(self):
    return sum([bool(obj) for obj in [self.get()]]) > 0

  def __str__(self):
    return '%s %s' % (self.secret, self.guid)



class HiveServerQueryHandle(QueryHandle):
  """
  QueryHandle for Hive Server 2.

  Store THandleIdentifier base64 encoded in order to be unicode compatible with Django.

  Also store session handle if provided.
  """
  def __init__(self, **kwargs):
    super(HiveServerQueryHandle, self).__init__(**kwargs)
    self.secret, self.guid = self.get_encoded()
    self.session_guid = kwargs.get('session_guid')

  def get(self):
    return self.secret, self.guid

  def get_rpc_handle(self):
    secret, guid = self.get_decoded(self.secret, self.guid)

    operation = getattr(TOperationType, TOperationType._NAMES_TO_VALUES.get(self.operation_type, 'EXECUTE_STATEMENT'))
    return TOperationHandle(operationId=THandleIdentifier(guid=guid, secret=secret),
                            operationType=operation,
                            hasResultSet=self.has_result_set,
                            modifiedRowCount=self.modified_row_count)

  @classmethod
  def get_decoded(cls, secret, guid):
    return base64.decodestring(secret), base64.decodestring(guid)

  def get_encoded(self):
    return base64.encodestring(self.secret), base64.encodestring(self.guid)


# Deprecated. Could be removed.

class BeeswaxQueryHandle(QueryHandle):
  """
  QueryHandle for Beeswax.
  """
  def __init__(self, secret, has_result_set, log_context):
    super(BeeswaxQueryHandle, self).__init__(secret=secret,
                                             has_result_set=has_result_set,
                                             log_context=log_context)

  def get(self):
    return self.secret, None

  def get_rpc_handle(self):
    return BeeswaxdQueryHandle(id=self.secret, log_context=self.log_context)

  # TODO remove
  def get_encoded(self):
    return self.get(), None


class MetaInstall(models.Model):
  """
  Metadata about the installation. Should have at most one row.
  """
  installed_example = models.BooleanField(default=False)

  @staticmethod
  def get():
    """
    MetaInstall.get() -> MetaInstall object

    It helps dealing with that this table has just one row.
    """
    try:
      return MetaInstall.objects.get(id=1)
    except MetaInstall.DoesNotExist:
      return MetaInstall(id=1)
