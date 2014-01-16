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

import logging
import json
import time


from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib.i18n import force_unicode
from desktop.models import Document, DocumentTag


LOG = logging.getLogger(__name__)


def list_docs(request):
  docs = Document.objects.get_docs(request.user).order_by('-last_modified')[:1000]
  return HttpResponse(json.dumps(massaged_documents_for_json(docs)), mimetype="application/json")


def list_tags(request):
  tags = DocumentTag.objects.get_tags(user=request.user)
  return HttpResponse(json.dumps(massaged_tags_for_json(tags, request.user)), mimetype="application/json")


def massaged_documents_for_json(documents):
  return [massage_doc_for_json(doc) for doc in documents]


def massage_doc_for_json(doc):
  perms = doc.list_permissions()
  return {
      'id': doc.id,
      'contentType': doc.content_type.name,
      'icon': doc.icon,
      'name': doc.name,
      'url': doc.content_object.get_absolute_url(),
      'description': doc.description,
      'tags': [{'id': tag.id, 'name': tag.tag} for tag in doc.tags.all()],
      'perms': {
        'read': {
          'users': [{'id': user.id, 'username': user.username} for user in perms.users.all()],
          'groups': [{'id': group.id, 'name': group.name} for group in perms.groups.all()]
        }
      },
      'owner': doc.owner.username,
      'lastModified': doc.last_modified.strftime("%x %X"),
      'lastModifiedInMillis': time.mktime(doc.last_modified.timetuple())
    }

def massaged_tags_for_json(tags, user):
  ts = []
  trash = DocumentTag.objects.get_trash_tag(user)
  history = DocumentTag.objects.get_history_tag(user)

  for tag in tags:
    massaged_tag = {
      'id': tag.id,
      'name': tag.tag,
      'isTrash': tag.id == trash.id,
      'isHistory': tag.id == history.id,
      'isExample': tag.tag == DocumentTag.EXAMPLE
    }
    ts.append(massaged_tag)

  return ts

def add_tag(request):
  response = {'status': -1, 'message': ''}

  if request.method == 'POST':
    try:
      tag = DocumentTag.objects.create_tag(request.user, request.POST['name'])
      response['tag_id'] = tag.id
      response['status'] = 0
    except Exception, e:
      response['message'] = force_unicode(e)
  else:
    response['message'] = _('POST request only')

  return HttpResponse(json.dumps(response), mimetype="application/json")


def tag(request):
  response = {'status': -1, 'message': ''}

  if request.method == 'POST':
    request_json = json.loads(request.POST['data'])
    try:
      tag = DocumentTag.objects.tag(request.user, request_json['doc_id'], request_json.get('tag'), request_json.get('tag_id'))
      response['tag_id'] = tag.id
      response['status'] = 0
    except Exception, e:
      response['message'] = force_unicode(e)
  else:
    response['message'] = _('POST request only')

  return HttpResponse(json.dumps(response), mimetype="application/json")


def update_tags(request):
  response = {'status': -1, 'message': ''}

  if request.method == 'POST':
    request_json = json.loads(request.POST['data'])
    try:
      doc = DocumentTag.objects.update_tags(request.user, request_json['doc_id'], request_json['tag_ids'])
      response['doc'] = massage_doc_for_json(doc)
      response['status'] = 0
    except Exception, e:
      response['message'] = force_unicode(e)
  else:
    response['message'] = _('POST request only')

  return HttpResponse(json.dumps(response), mimetype="application/json")


def remove_tags(request):
  response = {'status': -1, 'message': _('Error')}

  if request.method == 'POST':
    request_json = json.loads(request.POST['data'])
    try:
      for tag_id in request_json['tag_ids']:
        DocumentTag.objects.delete_tag(tag_id, request.user)
      response['message'] = _('Tag(s) removed!')
      response['status'] = 0
    except Exception, e:
      response['message'] = force_unicode(e)
  else:
    response['message'] = _('POST request only')

  return HttpResponse(json.dumps(response), mimetype="application/json")


def update_permissions(request):
  response = {'status': -1, 'message': _('Error')}

  if request.method == 'POST':
    data = json.loads(request.POST['data'])
    doc_id = request.POST['doc_id']
    try:
      doc = Document.objects.get_doc(doc_id, request.user)
      doc.sync_permissions(data)
      response['message'] = _('Permissions updated!')
      response['status'] = 0
      response['doc'] = massage_doc_for_json(doc)
    except Exception, e:
      response['message'] = force_unicode(e)
  else:
    response['message'] = _('POST request only')

  return HttpResponse(json.dumps(response), mimetype="application/json")
