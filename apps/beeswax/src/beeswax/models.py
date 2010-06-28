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

import copy
import logging
import datetime
import traceback
from enum import Enum

from django.db import models
from django.contrib.auth.models import User

from desktop.lib.django_util import PopupException
from beeswaxd.ttypes import QueryState

LOG = logging.getLogger(__name__)

QUERY_SUBMISSION_TIMEOUT = datetime.timedelta(0, 60 * 60)               # 1 hr

class QueryHistory(models.Model):
  """
  Holds metadata about all queries that have been executed.
  """
  STATE = Enum('submitted', 'running', 'available', 'failed', 'expired')

  # Map from (thrift) server state
  STATE_MAP = {
    QueryState.CREATED          : STATE.submitted,
    QueryState.INITIALIZED      : STATE.submitted,
    QueryState.COMPILED         : STATE.running,
    QueryState.RUNNING          : STATE.running,
    QueryState.FINISHED         : STATE.available,
    QueryState.EXCEPTION        : STATE.failed
  }

  owner = models.ForeignKey(User, db_index=True)
  query = models.CharField(max_length=1024)
  last_state = models.IntegerField(db_index=True)
  # If true, this query will eventually return tabular results.
  has_results = models.BooleanField(default=False)
  submission_date = models.DateTimeField(auto_now_add=True)
  # Only query in the "submitted" state is allowed to have no server_id
  server_id = models.CharField(max_length=1024, null=True)
  log_context = models.CharField(max_length=1024, null=True)
  # Some queries (like read/drop table) don't have a design
  design = models.ForeignKey('SavedQuery', to_field='id', null=True)
  # Notify on completion
  notify = models.BooleanField(default=False)

  class Meta:
    ordering = ['-submission_date']

  def save_state(self, new_state):
    """Set the last_state from an enum, and save"""
    if self.last_state != new_state.index:
      if new_state.index < self.last_state:
        backtrace = ''.join(traceback.format_stack(limit=5))
        LOG.error("Invalid query state transition: %s -> %s\n%s" % \
                  (QueryHistory.STATE[self.last_state], new_state, backtrace))
        return
      self.last_state = new_state.index
      self.save()

  def get_server_id(self):
    """
    get_server_id() ->  (True/False, server-side query id)

    The boolean indicates success/failure. The server_id follows, and may be None.
    Note that the server_id can legally be None when the query is just submitted.
    This method handles the various cases of the server_id being absent.

    Does not issue RPC.
    """
    if self.server_id:
      return (True, self.server_id)

    # Query being submitted have no server_id?
    if self.last_state == QueryHistory.STATE.submitted.index:
      # (1) Really? Check the submission date.
      #     This is possibly due to the server dying when compiling the query
      if self.submission_date.now() - self.submission_date > QUERY_SUBMISSION_TIMEOUT:
        LOG.error("Query submission taking too long. Expiring id %s: [%s]..." %
                  (self.id, self.query[:40]))
        self.save_state(QueryHistory.STATE.expired)
        return (False, None)
      else:
        # (2) It's not an error. Return the current state
        LOG.debug("Query %s (submitted) has no server id yet" % (self.id,))
        return (True, None)
    else:
      # (3) It has no server_id for no good reason. A case (1) will become this
      #     after we expire it. Note that we'll never be able to recover this
      #     query.
      LOG.error("Query %s (%s) has no server id [%s]..." %
                (self.id, QueryHistory.STATE[self.last_state], self.query[:40]))
      self.save_state(QueryHistory.STATE.expired)
      return (False, None)



class SavedQuery(models.Model):
  """
  Stores the query/report that people have save or submitted.

  Note that this used to be called QueryDesign. Any references to 'design'
  probably mean a SavedQuery.
  """
  DEFAULT_NEW_DESIGN_NAME = 'My saved query'
  AUTO_DESIGN_SUFFIX = ' (new)'
  TYPES = (HQL, REPORT) = range(2)

  type = models.IntegerField(null=False)
  owner = models.ForeignKey(User, db_index=True)
  # Data is a json of dictionary. See the beeswax.design module.
  data = models.TextField(max_length=65536)
  name = models.CharField(max_length=64)
  desc = models.TextField(max_length=1024)
  mtime = models.DateTimeField(auto_now=True)
  # An auto design is a place-holder for things users submit but not saved.
  # We still want to store it as a design to allow users to save them later.
  is_auto = models.BooleanField(default=False, db_index=True)

  class Meta:
    ordering = ['-mtime']

  def clone(self):
    """clone() -> A new SavedQuery with a deep copy of the same data"""
    design = SavedQuery(type=self.type, owner=self.owner)
    design.data = copy.deepcopy(self.data)
    design.name = copy.deepcopy(self.name)
    design.desc = copy.deepcopy(self.desc)
    design.is_auto = copy.deepcopy(self.is_auto)
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
      msg = 'Cannot retrieve Beeswax design id %s' % (id,)
      raise err

    if owner is not None and design.owner != owner:
      msg = 'Design id %s does not belong to user %s' % (id, owner)
      LOG.error(msg)
      raise PopupException(msg)

    if type is not None and design.type != type:
      msg = 'Type mismatch for design id %s (owner %s) - Expects %s got %s' % \
            (id, owner, design.type, type)
      LOG.error(msg)
      raise PopupException(msg)

    return design


class MetaInstall(models.Model):
  """
  Metadata about the installation. Should have at most one row.
  """
  installed_example = models.BooleanField()

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
