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
import tempfile
import time
import StringIO
import zipfile

from django.core import management
from django.shortcuts import redirect
from django.utils import html

from desktop.lib.django_util import JsonResponse
from desktop.lib.export_csvxls import make_response
from desktop.lib.i18n import smart_str
from desktop.models import Document2, Document
from django.http import HttpResponse


LOG = logging.getLogger(__name__)


def get_document(request):
  if request.GET.get('id'):
    doc = Document2.objects.get(id=request.GET['id'])
  else:
    doc = Document2.objects.get(uuid=request.GET['uuid'])

  response = _massage_doc_for_json(doc, request.user, with_data=request.GET.get('with_data'))

  return JsonResponse(response)


def _massage_doc_for_json(document, user, with_data=False):

  massaged_doc = {
    'id': document.id,
    'uuid': document.uuid,

    'owner': document.owner.username,
    'type': html.conditional_escape(document.type),
    'name': html.conditional_escape(document.name),
    'description': html.conditional_escape(document.description),

    'isMine': document.owner == user,
    'lastModified': document.last_modified.strftime("%x %X"),
    'lastModifiedInMillis': time.mktime(document.last_modified.timetuple()),
    'version': document.version,
    'is_history': document.is_history,

    # tags
    # dependencies
  }

  if with_data:
    massaged_doc['data'] = document.data_dict

  return massaged_doc


def export_documents(request):
  if request.GET.get('documents'):
    selection = json.loads(request.GET.get('documents'))
  else:
    selection = json.loads(request.POST.get('documents'))

  # If non admin, only export documents the user owns
  docs = Document2.objects
  if not request.user.is_superuser:
    docs = docs.filter(owner=request.user)
  docs = docs.filter(id__in=selection).order_by('-id')
  doc_ids = docs.values_list('id', flat=True)

  f = StringIO.StringIO()

  if doc_ids:
    doc_ids = ','.join(map(str, doc_ids))
    management.call_command('dumpdata', 'desktop.Document2', primary_keys=doc_ids, indent=2, use_natural_keys=True, verbosity=2, stdout=f)

  if request.GET.get('format') == 'json':
    return JsonResponse(f.getvalue(), safe=False)
  elif request.GET.get('format') == 'zip':
    zfile = zipfile.ZipFile(f, 'w')
    zfile.writestr("hue.json", f.getvalue())
    for doc in docs:
      if doc.type == 'notebook':
        try:
          from spark.models import Notebook
          zfile.writestr("notebook-%s-%s.txt" % (doc.name, doc.id), smart_str(Notebook(document=doc).get_str()))
        except Exception, e:
          print e
          LOG.exception(e)
    zfile.close()
    response = HttpResponse(content_type="application/zip")
    response["Content-Length"] = len(f.getvalue())
    response['Content-Disposition'] = 'attachment; filename="hue-documents.zip"'
    response.write(f.getvalue())
    return response
  else:
    return make_response(f.getvalue(), 'json', 'hue-documents')



def import_documents(request):
  if request.FILES.get('documents'):
    documents = request.FILES['documents'].read()
  else:
    documents = json.loads(request.POST.get('documents'))

  documents = json.loads(documents)
  docs = []

  for doc in documents:
    if not request.user.is_superuser:
      doc['fields']['owner'] = [request.user.username]
    owner = doc['fields']['owner'][0]

    doc['fields']['tags'] = []

    if Document2.objects.filter(uuid=doc['fields']['uuid'], owner__username=owner).exists():
      doc['pk'] = Document2.objects.get(uuid=doc['fields']['uuid'], owner__username=owner).pk
    else:
      doc['pk'] = None

    docs.append(doc)

  f = tempfile.NamedTemporaryFile(mode='w+', suffix='.json')
  f.write(json.dumps(docs))
  f.flush()

  stdout = StringIO.StringIO()
  try:
    management.call_command('loaddata', f.name, stdout=stdout)
  except Exception, e:
    return JsonResponse({'message': smart_str(e)})

  Document.objects.sync()

  if request.POST.get('redirect'):
    return redirect(request.POST.get('redirect'))
  else:
    return JsonResponse({'message': stdout.getvalue()})
