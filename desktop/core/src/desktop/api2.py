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
import StringIO
import zipfile

from datetime import datetime

from django.contrib.auth.models import Group, User
from django.core import management

from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.export_csvxls import make_response
from desktop.lib.i18n import smart_str, force_unicode
from desktop.models import Document2, Document, Directory, FilesystemException, uuid_default

from notebook.connectors.base import Notebook
from notebook.views import upgrade_session_properties


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
def search_documents(request):
  """
  Returns the directories and documents based on given params that are accessible by the current user
  Optional params:
    perms=<mode>       - Controls whether to retrieve owned, shared, or both. Defaults to both.
    include_history=<bool> - Controls whether to retrieve history docs. Defaults to false.
    flatten=<bool>     - Controls whether to return documents in a flat list, or roll up documents to a common directory
                         if possible. Defaults to true.
    page=<n>           - Controls pagination. Defaults to 1.
    limit=<n>          - Controls limit per page. Defaults to all.
    type=<type>        - Show documents of given type(s) (directory, query-hive, query-impala, query-mysql, etc).
                         Defaults to all.
    sort=<key>         - Sort by the attribute <key>, which is one of: "name", "type", "owner", "last_modified"
                         Accepts the form "-last_modified", which sorts in descending order.
                         Defaults to "-last_modified".
    text=<frag>       -  Search for fragment "frag" in names and descriptions.
  """

  response = {
    'documents': []
  }

  perms = request.GET.get('perms', 'both').lower()
  include_history = json.loads(request.GET.get('include_history', 'false'))
  include_trashed = json.loads(request.GET.get('include_trashed', 'true'))
  flatten = json.loads(request.GET.get('flatten', 'true'))

  if perms not in ['owned', 'shared', 'both']:
    raise PopupException(_('Invalid value for perms, acceptable values are: owned, shared, both.'))

  documents = Document2.objects.documents(
    user=request.user,
    perms=perms,
    include_history=include_history,
    include_trashed=include_trashed
  )

  # Refine results
  response.update(_filter_documents(request, queryset=documents, flatten=flatten))

  # Paginate
  response.update(_paginate(request, queryset=response['documents']))

  # Serialize results
  response['documents'] = [doc.to_dict() for doc in response.get('documents', [])]

  return JsonResponse(response)


@api_error_handler
def get_document(request):
  """
  Returns the document or directory found for the given uuid or path and current user.
  If a directory is found, return any children documents too.
  Optional params:
    page=<n>    - Controls pagination. Defaults to 1.
    limit=<n>   - Controls limit per page. Defaults to all.
    type=<type> - Show documents of given type(s) (directory, query-hive, query-impala, query-mysql, etc). Default to all.
    sort=<key>  - Sort by the attribute <key>, which is one of:
                    "name", "type", "owner", "last_modified"
                  Accepts the form "-last_modified", which sorts in descending order.
                  Default to "-last_modified".
    text=<frag> - Search for fragment "frag" in names and descriptions.
    data=<false|true> - Return all the data of the document. Default to false.
    dependencies=<false|true> - Return all the dependencies and dependents of the document. Default to false.
  """
  path = request.GET.get('path', '/')
  uuid = request.GET.get('uuid')
  with_data = request.GET.get('data', 'false').lower() == 'true'
  with_dependencies = request.GET.get('dependencies', 'false').lower() == 'true'

  if uuid:
    if uuid.isdigit():
      document = Document2.objects.document(user=request.user, doc_id=uuid)
    else:
      document = Document2.objects.get_by_uuid(user=request.user, uuid=uuid)
  else:  # Find by path
    document = Document2.objects.get_by_path(user=request.user, path=path)

  response = {
    'document': document.to_dict(),
    'parent': document.parent_directory.to_dict() if document.parent_directory else None,
    'children': [],
    'dependencies': [],
    'dependents': [],
    'data': ''
  }

  if with_data:
    data = json.loads(document.data)
    # Upgrade session properties for Hive and Impala
    if document.type.startswith('query'):
      notebook = Notebook(document=document)
      notebook = upgrade_session_properties(request, notebook)
      data = json.loads(notebook.data)

    response['data'] = data

  if with_dependencies:
    response['dependencies'] = [dependency.to_dict() for dependency in document.dependencies.all()]
    response['dependents'] = [dependent.to_dict() for dependent in document.dependents.all()]

  # Get children documents if this is a directory
  if document.is_directory:
    directory = Directory.objects.get(id=document.id)

    # If this is the user's home directory, fetch shared docs too
    if document.is_home_directory:
      children = directory.get_children_and_shared_documents(user=request.user)
    else:
      children = directory.get_children_documents()

    # Filter and order results
    response.update(_filter_documents(request, queryset=children, flatten=False))

  # Paginate and serialize Results
  if 'documents' in response:
    response.update(_paginate(request, queryset=response['documents']))
    # Rename documents to children
    response['children'] = response.pop('documents')
    response['children'] = [doc.to_dict() for doc in response['children']]

  return JsonResponse(response)


@api_error_handler
def open_document(request):
  doc_id = request.GET.get('id')

  if doc_id.isdigit():
    document = Document2.objects.document(user=request.user, doc_id=doc_id)
  else:
    document = Document2.objects.get_by_uuid(user=request.user, uuid=doc_id)

  return redirect(document.get_absolute_url())


@api_error_handler
@require_POST
def move_document(request):
  source_doc_uuid = json.loads(request.POST.get('source_doc_uuid'))
  destination_doc_uuid = json.loads(request.POST.get('destination_doc_uuid'))

  if not source_doc_uuid or not destination_doc_uuid:
    raise PopupException(_('move_document requires source_doc_uuid and destination_doc_uuid'))

  source = Document2.objects.get_by_uuid(user=request.user, uuid=source_doc_uuid, perm_type='write')
  destination = Directory.objects.get_by_uuid(user=request.user, uuid=destination_doc_uuid, perm_type='write')

  doc = source.move(destination, request.user)

  return JsonResponse({
    'status': 0,
    'document': doc.to_dict()
  })


@api_error_handler
@require_POST
def create_directory(request):
  parent_uuid = json.loads(request.POST.get('parent_uuid'))
  name = json.loads(request.POST.get('name'))

  if not parent_uuid or not name:
    raise PopupException(_('create_directory requires parent_uuid and name'))

  parent_dir = Directory.objects.get_by_uuid(user=request.user, uuid=parent_uuid, perm_type='write')

  directory = Directory.objects.create(name=name, owner=request.user, parent_directory=parent_dir)

  return JsonResponse({
      'status': 0,
      'directory': directory.to_dict()
  })


@api_error_handler
@require_POST
def update_document(request):
  uuid = json.loads(request.POST.get('uuid'))

  if not uuid:
    raise PopupException(_('update_document requires uuid'))

  document = Document2.objects.get_by_uuid(user=request.user, uuid=uuid, perm_type='write')

  whitelisted_attrs = ['name', 'description']

  for attr in whitelisted_attrs:
    if request.POST.get(attr):
      setattr(document, attr, request.POST.get(attr))

  document.save(update_fields=whitelisted_attrs)

  return JsonResponse({
    'status': 0,
    'document': document.to_dict()
  })



@api_error_handler
@require_POST
def delete_document(request):
  """
  Accepts a uuid and optional skip_trash parameter

  (Default) skip_trash=false, flags a document as trashed
  skip_trash=true, deletes it permanently along with any history dependencies

  If directory and skip_trash=false, all dependencies will also be flagged as trash
  If directory and skip_trash=true, directory must be empty (no dependencies)
  """
  uuid = json.loads(request.POST.get('uuid'))
  skip_trash = json.loads(request.POST.get('skip_trash', 'false'))

  if not uuid:
    raise PopupException(_('delete_document requires uuid'))

  document = Document2.objects.get_by_uuid(user=request.user, uuid=uuid, perm_type='write')

  if skip_trash:
    document.delete()
  else:
    document.trash()

  return JsonResponse({
      'status': 0,
  })


@api_error_handler
@require_POST
def share_document(request):
  """
  Set who else or which other group can interact with the document.

  Example of input: {'read': {'user_ids': [1, 2, 3], 'group_ids': [1, 2, 3]}}
  """
  perms_dict = json.loads(request.POST.get('data'))
  uuid = json.loads(request.POST.get('uuid'))

  if not uuid or not perms_dict:
    raise PopupException(_('share_document requires uuid and perms_dict'))

  doc = Document2.objects.get_by_uuid(user=request.user, uuid=uuid)

  for name, perm in perms_dict.iteritems():
    users = groups = None
    if perm.get('user_ids'):
      users = User.objects.in_bulk(perm.get('user_ids'))
    else:
      users = []

    if perm.get('group_ids'):
      groups = Group.objects.in_bulk(perm.get('group_ids'))
    else:
      groups = []

    doc = doc.share(request.user, name=name, users=users, groups=groups)

  return JsonResponse({
    'status': 0,
    'document': doc.to_dict()
  })


@ensure_csrf_cookie
def export_documents(request):
  if request.GET.get('documents'):
    selection = json.loads(request.GET.get('documents'))
  else:
    selection = json.loads(request.POST.get('documents'))

  # Only export documents the user has permissions to read
  docs = Document2.objects.documents(user=request.user, perms='both', include_history=True, include_trashed=True).\
    filter(id__in=selection).order_by('-id')

  # Add any dependencies to the set of exported documents
  export_doc_set = _get_dependencies(docs)

  # For directories, add any children docs to the set of exported documents
  export_doc_set.update(_get_dependencies(docs, deps_mode=False))

  # Get PKs of documents to export
  doc_ids = [doc.pk for doc in export_doc_set]

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
          LOG.exception(e)
    zfile.close()
    response = HttpResponse(content_type="application/zip")
    response["Content-Length"] = len(f.getvalue())
    response['Content-Disposition'] = 'attachment; filename="hue-documents.zip"'
    response.write(f.getvalue())
    return response
  else:
    return make_response(f.getvalue(), 'json', 'hue-documents')


@ensure_csrf_cookie
def import_documents(request):
  if request.FILES.get('documents'):
    documents = request.FILES['documents'].read()
  else:
    documents = json.loads(request.POST.get('documents'))

  documents = json.loads(documents)
  docs = []

  uuids_map = dict((doc['fields']['uuid'], None) for doc in documents)

  for doc in documents:

    # If doc is not owned by current user, make a copy of the document with current user as owner
    if doc['fields']['owner'][0] != request.user.username:
      doc = _copy_document_with_owner(doc, request.user, uuids_map)
    else:  # Update existing doc or create new
      doc = _create_or_update_document_with_owner(doc, request.user, uuids_map)

    # Set last modified date to now
    doc['fields']['last_modified'] = datetime.now().replace(microsecond=0).isoformat()
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


def _get_dependencies(documents, deps_mode=True):
  """
  Given a list of Document2 objects, perform a depth-first search and return a set of documents with all
   dependencies included
  :param doc_set: set of Document2 objects to include
  :param deps_mode: traverse dependencies relationship, otherwise traverse children relationship
  """
  doc_set = set()

  for doc in documents:
    stack = [doc]
    while stack:
      curr_doc = stack.pop()
      if curr_doc not in doc_set:
        doc_set.add(curr_doc)
        if deps_mode:
          deps_set = set(curr_doc.dependencies.all())
        else:
          deps_set = set(curr_doc.children.all())
        stack.extend(deps_set - doc_set)

  return doc_set


def _copy_document_with_owner(doc, owner, uuids_map):
  home_dir = Directory.objects.get_home_directory(owner)

  doc['fields']['owner'] = [owner.username]
  doc['pk'] = None
  doc['fields']['version'] = 1

  # Retrieve from the import_uuids_map if it's already been reassigned, or assign a new UUID and map it
  old_uuid = doc['fields']['uuid']
  if uuids_map[old_uuid] is None:
    uuids_map[old_uuid] = uuid_default()
  doc['fields']['uuid'] = uuids_map[old_uuid]

  # Remap parent directory if needed
  parent_uuid = doc['fields']['parent_directory'][0]
  if parent_uuid not in uuids_map.keys():
    LOG.warn('Could not find parent directory with UUID: %s in JSON import, will set parent to home directory' %
             parent_uuid)
    doc['fields']['parent_directory'] = [home_dir.uuid, home_dir.version, home_dir.is_history]
  else:
    if uuids_map[parent_uuid] is None:
      uuids_map[parent_uuid] = uuid_default()
    doc['fields']['parent_directory'] = [uuids_map[parent_uuid], 1, False]

  # Remap dependencies if needed
  idx = 0
  for dep_uuid, dep_version, dep_is_history in doc['fields']['dependencies']:
    if dep_uuid not in uuids_map.keys():
      LOG.warn('Could not find dependency UUID: %s in JSON import, may cause integrity errors if not found.' % dep_uuid)
    else:
      if uuids_map[dep_uuid] is None:
        uuids_map[dep_uuid] = uuid_default()
      doc['fields']['dependencies'][idx][0] = uuids_map[dep_uuid]
    idx += 1

  return doc


def _create_or_update_document_with_owner(doc, owner, uuids_map):
  home_dir = Directory.objects.get_home_directory(owner)
  create_new = False

  try:
    owned_docs = Document2.objects.filter(uuid=doc['fields']['uuid'], owner=owner).order_by('-last_modified')
    if owned_docs.exists():
      existing_doc = owned_docs[0]
      doc['pk'] = existing_doc.pk
    else:
      create_new = True
  except FilesystemException, e:
    create_new = True

  if create_new:
    LOG.warn('Could not find document with UUID: %s, will create a new document on import.', doc['fields']['uuid'])
    doc['pk'] = None
    doc['fields']['version'] = 1

  # Verify that parent exists, log warning and set parent to user's home directory if not found
  if doc['fields']['parent_directory']:
    uuid, version, is_history = doc['fields']['parent_directory']
    if uuid not in uuids_map.keys() and \
            not Document2.objects.filter(uuid=uuid, version=version, is_history=is_history).exists():
      LOG.warn('Could not find parent document with UUID: %s, will set parent to home directory' % uuid)
      doc['fields']['parent_directory'] = [home_dir.uuid, home_dir.version, home_dir.is_history]

  # Verify that dependencies exist, raise critical error if any dependency not found
  if doc['fields']['dependencies']:
    for uuid, version, is_history in doc['fields']['dependencies']:
      if not uuid in uuids_map.keys() and \
              not Document2.objects.filter(uuid=uuid, version=version, is_history=is_history).exists():
        raise PopupException(_('Cannot import document, dependency with UUID: %s not found.') % uuid)

  return doc


def _filter_documents(request, queryset, flatten=True):
  """
  Given optional querystring params extracted from the request, filter the given queryset of documents and return a
    dictionary with the refined queryset and filter params
  :param request: request object with params
  :param queryset: Document2 queryset
  :param flatten: Return all results in a flat list if true, otherwise roll up to common directory
  """
  type_filters = request.GET.getlist('type', None)
  sort = request.GET.get('sort', '-last_modified')
  search_text = request.GET.get('text', None)

  documents = queryset.search_documents(
      types=type_filters,
      search_text=search_text,
      order_by=sort)

  # Roll up documents to common directory
  if not flatten:
    documents = documents.exclude(parent_directory__in=documents)

  count = documents.count()

  return {
    'documents': documents,
    'count': count,
    'types': type_filters,
    'text': search_text,
    'sort': sort
  }


def _paginate(request, queryset):
  """
  Given optional querystring params extracted from the request, slice the given queryset of documents for the given page
    and limit, and return the updated queryset along with pagination params used.
  :param request: request object with params
  :param queryset: queryset
  """
  page = int(request.GET.get('page', 1))
  limit = int(request.GET.get('limit', 0))

  if limit > 0:
    offset = (page - 1) * limit
    last = offset + limit
    queryset = queryset.all()[offset:last]

  return {
    'documents': queryset,
    'page': page,
    'limit': limit
  }
