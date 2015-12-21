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
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import html
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.export_csvxls import make_response
from desktop.lib.i18n import smart_str, force_unicode
from desktop.models import Document2, Document, Directory
from desktop.lib.exceptions_renderable import PopupException
from hadoop.fs.hadoopfs import Hdfs


LOG = logging.getLogger(__name__)


def api_error_handler(func):
  def decorator(*args, **kwargs):
    response = {}

    try:
      return func(*args, **kwargs)
    except Exception, e:
      LOG.exception('Error running %s' % func)
      response['status'] = -1
      response['message'] = force_unicode(str(e))
    finally:
      if response:
        return JsonResponse(response)

  return decorator


@api_error_handler
def get_documents(request): # TODO only here for assist
  filters = {
      'owner': request.user
  }

  if request.GET.get('type'):
    filters['type'] = json.loads(request.GET.get('type'))

  return JsonResponse({'documents': [doc.to_dict() for doc in Document2.objects.filter(**filters)]})


@api_error_handler
def get_documents2(request):
  path = request.GET.get('path', '/') # Expects path to be a Directory for now

  try:
    file_doc = Directory.objects.get(owner=request.user, name=path) # TODO perms
  except Directory.DoesNotExist, e:
    if path == '/':
      file_doc = Directory.objects.create(name='/', type='directory', owner=request.user)
      file_doc.dependencies.add(*Document2.objects.filter(owner=request.user).exclude(id=file_doc.id))
    else:
      raise e

  return JsonResponse({
      'file': file_doc.to_dict(),
      'documents': [doc.to_dict() for doc in file_doc.documents()],
      'path': path
  })


@api_error_handler
@require_POST
def move_document(request):
  source_id = request.POST.get('source_id', 'source_id')
  destination_id = request.POST.get('destination_id', 'destination_id')

  # destination exists + is dir?
  source = Document2.objects.document(request.user, uuid=source_id)
  destination = Directory.objects.document(request.user, uuid=destination_id)

  source.move(destination)

  return JsonResponse({'status': 0})


@api_error_handler
@require_POST
def create_directory(request):
  parent_path = json.loads(request.POST.get('parent_path'))
  name = json.loads(request.POST.get('name'))

  parent_dir = Directory.objects.get(owner=request.user, name=parent_path)
  
  path = Hdfs.normpath(parent_path + '/' + name)
  file_doc = Directory.objects.create(name=path, type='directory', owner=request.user)
  parent_dir.dependencies.add(file_doc)

  return JsonResponse({
      'status': 0,
      'file': file_doc.to_dict()
  })


@api_error_handler
@require_POST
def delete_document(request):
  document_id = request.POST.get('document_id')

  document = Document2.objects.document(request.user, id=document_id)
  if document.type == 'directory' and document.dependencies():
    raise PopupException(_('Directory is not empty'))

  document.delete()

  return JsonResponse({
      'status': 0,
  })


@api_error_handler
@require_POST
def update_permissions(requests):
  pass


# TODO security + permissions
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
