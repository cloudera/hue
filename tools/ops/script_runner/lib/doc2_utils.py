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

import json
import re
import logging
import difflib

from desktop.models import Document2
#DOC2_NAME_INVALID_CHARS = "[<>/{}[\]~`u'\xe9'u'\xfa'u'\xf3'u'\xf1'u'\xed']"
DOC2_NAME_INVALID_CHARS = "[<>/{}\[\]]"

LOG = logging.getLogger(__name__)

def removeInvalidChars(fixString):
  fixString = re.sub(r'[^\x00-\x7f]',r'', fixString)
  return re.sub(DOC2_NAME_INVALID_CHARS, '', fixString)


def findMatchingQuery(user, id, name, query, include_history=False, all=False, values=False):
#Returns list of matching queries.  If all = False
#returns at first found for speed
  name = removeInvalidChars(name)
#  LOG.info("finding queries that match name: %s" % name)
  documents = getSavedQueries(user=user, name=name, include_history=include_history)
  matchdocs = []
  matchvalues = []
   
  for doc in documents:
    if all == True or not matchdocs:
      matchdata = json.loads(doc.data)
      matchname = removeInvalidChars(doc.name)
#      LOG.info("found name: matchname: %s" % matchname)
      if 'snippets' in matchdata:
        matchquery = matchdata['snippets'][0]['statement_raw']
        if re.match(name, matchname) and id != doc.id:
#          LOG.info("Query name: %s and matchname: %s are similar" % (name, matchname))
#          LOG.info("Comparing queries:")
          if query == matchquery:
#            LOG.info("MATCHED QUERY: name: %s: id: %s" % (name, id))
            matchdocs.append(doc) 
            matchvalues.append(doc.id)

  if values == False:
#    LOG.info("returning %s matching docs" % len(matchdocs))
    return matchdocs
  else:
#    LOG.info("returning %s matching doc ids" % len(matchdocs))
    return matchvalues


def getSavedQueries(user, name=None, include_history=False):
#mimic api call to get saved queries
  perms = 'both'
  include_trashed = False
  flatten = True
  if name:
#    LOG.info("getting queries that match name: %s" % name)
    if include_history:
      documents = Document2.objects.filter(name__contains=name, owner=user, type__in=['query-hive', 'query-impala'])
#      documents = Document2.objects.filter(name__iregex=r'%s.*' %name, owner=user, type__in=['query-hive', 'query-impala'])
    else:
      documents = Document2.objects.filter(name__contains=name, owner=user, type__in=['query-hive', 'query-impala'], is_history=include_history)
#      documents = Document2.objects.filter(name__iregex=r'%s.*' %name, owner=user, type__in=['query-hive', 'query-impala'], is_history=include_history)
  else:
#    LOG.info("getting all queries")
    if include_history:
      documents = Document2.objects.filter(
        user=user,
        include_trashed=include_trashed,
        type__in=['query-hive', 'query-impala']
      )
    else:
      documents = Document2.objects.filter(
        user=user,
        include_history=include_history,
        include_trashed=include_trashed,
        type__in=['query-hive', 'query-impala']
      )

#  LOG.info("returning queries, total count: %s" % len(documents))
  return documents


