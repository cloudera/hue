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

import json
import logging
import os
import re
import tempfile
import zipfile
from builtins import map
from datetime import datetime
from io import StringIO as string_io

from celery.app.control import Control
from django.core import management
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.html import escape
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from beeswax import common
from beeswax.management.commands import beeswax_install_examples
from beeswax.models import Namespace
from desktop import appmanager
from desktop.auth.backend import is_admin
from desktop.conf import (
  COLLECT_USAGE,
  CUSTOM,
  ENABLE_CHUNKED_FILE_UPLOADER,
  ENABLE_CONNECTORS,
  ENABLE_GIST_PREVIEW,
  ENABLE_NEW_STORAGE_BROWSER,
  ENABLE_SHARING,
  ENABLE_WORKFLOW_CREATION_ACTION,
  get_clusters,
  IMPORTER,
  TASK_SERVER_V2,
)
from desktop.lib.conf import BoundContainer, GLOBAL_CONFIG, is_anonymous
from desktop.lib.connectors.models import Connector
from desktop.lib.django_util import JsonResponse, login_notrequired, render
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.export_csvxls import make_response
from desktop.lib.i18n import force_unicode, smart_str
from desktop.lib.paths import get_desktop_root
from desktop.log import DEFAULT_LOG_DIR
from desktop.models import (
  __paginate,
  _get_gist_document,
  Directory,
  Document,
  Document2,
  FilesystemException,
  get_cluster_config,
  get_user_preferences,
  set_user_preferences,
  UserPreferences,
  uuid_default,
)
from desktop.views import _get_config_errors, get_banner_message, serve_403_error
from filebrowser.conf import (
  CONCURRENT_MAX_CONNECTIONS,
  ENABLE_EXTRACT_UPLOADED_ARCHIVE,
  FILE_UPLOAD_CHUNK_SIZE,
  RESTRICT_FILE_EXTENSIONS,
  SHOW_DOWNLOAD_BUTTON,
)
from filebrowser.tasks import check_disk_usage_and_clean_task, document_cleanup_task
from filebrowser.views import MAX_FILEEDITOR_SIZE
from hadoop.cluster import is_yarn
from hbase.management.commands import hbase_setup
from indexer.management.commands import indexer_setup
from metadata.catalog_api import (
  _highlight,
  search_entities as metadata_search_entities,
  search_entities_interactive as metadata_search_entities_interactive,
)
from metadata.conf import has_catalog
from metastore.conf import ALLOW_SAMPLE_DATA_FROM_VIEWS
from notebook.connectors.base import get_interpreter, Notebook
from notebook.management.commands import notebook_setup
from pig.management.commands import pig_setup
from search.management.commands import search_setup
from useradmin.models import Group, User

if hasattr(TASK_SERVER_V2, 'get') and TASK_SERVER_V2.ENABLED.get():
  from desktop.celery import app as celery_app
  from filebrowser.utils import parse_broker_url

LOG = logging.getLogger()


def api_error_handler(func):
  def decorator(*args, **kwargs):
    response = {}

    try:
      return func(*args, **kwargs)
    except Exception as e:
      LOG.exception('Error running %s' % func)
      response['status'] = -1
      response['message'] = force_unicode(str(e))
    finally:
      if response:
        return JsonResponse(response)

  return decorator


@api_error_handler
def get_banners(request):
  banners = {
    'system': get_banner_message(request),
    'configured': CUSTOM.BANNER_TOP_HTML.get()
  }
  return JsonResponse(banners)


@api_error_handler
def get_config(request):
  """
  Returns Hue application's config information.
  Includes settings for various components like storage, task server, importer, etc.
  """
  # Get base cluster configuration
  config = get_cluster_config(request.user)

  # Core application configuration
  config['hue_config'] = {
    'is_admin': is_admin(request.user),
    'is_yarn_enabled': is_yarn(),
    'enable_task_server': TASK_SERVER_V2.ENABLED.get(),
    'enable_workflow_creation_action': ENABLE_WORKFLOW_CREATION_ACTION.get(),
    'allow_sample_data_from_views': ALLOW_SAMPLE_DATA_FROM_VIEWS.get(),
    'enable_sharing': ENABLE_SHARING.get(),
    'collect_usage': COLLECT_USAGE.get(),
  }

  # Storage browser configuration
  config['storage_browser'] = {
    'enable_chunked_file_upload': ENABLE_CHUNKED_FILE_UPLOADER.get(),
    'enable_new_storage_browser': ENABLE_NEW_STORAGE_BROWSER.get(),
    'restrict_file_extensions': RESTRICT_FILE_EXTENSIONS.get(),
    'concurrent_max_connection': CONCURRENT_MAX_CONNECTIONS.get(),
    'file_upload_chunk_size': FILE_UPLOAD_CHUNK_SIZE.get(),
    'enable_file_download_button': SHOW_DOWNLOAD_BUTTON.get(),
    'max_file_editor_size': MAX_FILEEDITOR_SIZE,
    'enable_extract_uploaded_archive': ENABLE_EXTRACT_UPLOADED_ARCHIVE.get(),
  }

  # Importer configuration
  config['importer'] = {
    'is_enabled': IMPORTER.IS_ENABLED.get(),
    'restrict_local_file_extensions': IMPORTER.RESTRICT_LOCAL_FILE_EXTENSIONS.get(),
    'max_local_file_size_upload_limit': IMPORTER.MAX_LOCAL_FILE_SIZE_UPLOAD_LIMIT.get(),
  }

  # Other general configuration
  config['clusters'] = list(get_clusters(request.user).values())
  config['documents'] = {'types': list(Document2.objects.documents(user=request.user).order_by().values_list('type', flat=True).distinct())}
  config['status'] = 0

  return JsonResponse(config)


@api_error_handler
def get_hue_config(request):
  if not is_admin(request.user):
    raise PopupException(_('You must be a superuser.'))

  show_private = request.GET.get('private', False)

  app_modules = appmanager.DESKTOP_MODULES
  config_modules = GLOBAL_CONFIG.get().values()

  if ENABLE_CONNECTORS.get():
    app_modules = [app_module for app_module in app_modules if app_module.name == 'desktop']
    config_modules = [config_module for config_module in config_modules if config_module.config.key == 'desktop']

  apps = [{
    'name': app.name,
    'has_ui': app.menu_index != 999,
    'display_name': app.display_name
  } for app in sorted(app_modules, key=lambda app: app.name)]

  def recurse_conf(modules):
    attrs = []
    for module in modules:
      if not show_private and module.config.private:
        continue

      conf = {
        'help': module.config.help or _('No help available.'),
        'key': module.config.key,
        'is_anonymous': is_anonymous(module.config.key)
      }
      if isinstance(module, BoundContainer):
        conf['values'] = recurse_conf(module.get().values())
      else:
        conf['default'] = str(module.config.default)
        if module.config.secret or 'password' in module.config.key:
          conf['value'] = '*' * 10
        else:
          conf['value'] = str(module.get_raw())
        conf['value'] = re.sub('(.*)://(.*):(.*)@(.*)', r'\1://\2:**********@\4', conf['value'])

      attrs.append(conf)

    return attrs

  return JsonResponse({
    'config': sorted(recurse_conf(config_modules), key=lambda conf: conf.get('key')),
    'conf_dir': os.path.realpath(os.getenv('HUE_CONF_DIR', get_desktop_root('conf'))),
    'apps': apps
  })


@api_error_handler
def get_context_namespaces(request, interface):
  '''
  Namespaces are node cluster contexts (e.g. Hive + Ranger) that can be queried by computes.
  '''
  response = {}
  namespaces = []

  ns_objs = Namespace.objects.filter(dialect=interface)
  if ns_objs:
    namespaces = [{
        'id': ns.id,
        'name': ns.name,
        'status': 'CREATED',
        'computes': [{'id': c['id'], 'type': c['type'], 'name': c['name'], 'dialect': c['dialect'],
                      'interface': c['interface']} for c in ns.get_computes(request.user)]
      } for ns in ns_objs
    ]
    namespaces = [ns for ns in namespaces if ns['computes']]
  else:
    # Currently broken if not sent
    clusters = list(get_clusters(request.user).values())
    namespaces.extend([{
        'id': cluster['id'],
        'name': cluster['name'],
        'status': 'CREATED',
        'computes': [cluster]
      } for cluster in clusters if cluster.get('type') == 'direct'
    ])

  response[interface] = namespaces
  response['status'] = 0

  return JsonResponse(response)


@api_error_handler
def get_context_computes(request, interface):
  '''
  Some clusters like Snowball can have multiple computes for a certain languages (Hive, Impala...).
  '''
  response = {}

  ns = Namespace.objects.filter(dialect=interface).first()
  computes = ns.get_computes(request.user) if ns else None
  if not computes:
    # Currently broken if not sent
    clusters = list(get_clusters(request.user).values())
    computes = [{
        'id': cluster['id'],
        'name': cluster['name'],
        'namespace': cluster['id'],
        'interface': interface,
        'type': cluster['type'],
        'options': {}
      } for cluster in clusters if cluster.get('type') == 'direct'
    ]

  response[interface] = computes
  response['status'] = 0

  return JsonResponse(response)


# Deprecated, not used.
@api_error_handler
def get_context_clusters(request, interface):
  response = {}
  clusters = []

  cluster_configs = list(get_clusters(request.user).values())

  for cluster in cluster_configs:
    cluster = {
      'id': cluster.get('id'),
      'name': cluster.get('name'),
      'status': 'CREATED',
      'environmentType': cluster.get('type'),
      'serviceType': cluster.get('interface'),
      'namespace': '',
      'type': cluster.get('type')
    }

    if cluster.get('type') == 'altus':
      cluster['name'] = 'Altus DE'
      cluster['type'] = 'altus-de'
      clusters.append(cluster)
      cluster = cluster.copy()
      cluster['name'] = 'Altus Data Warehouse'
      cluster['type'] = 'altus-dw'
    elif cluster.get('type') == 'altusv2':
      cluster['name'] = 'Data Warehouse'
      cluster['type'] = 'altus-dw2'

    clusters.append(cluster)

  response[interface] = clusters
  response['status'] = 0

  return JsonResponse(response)


@api_error_handler
def search_documents(request):
  """
  Returns the directories and documents based on given params that are accessible by the current user
  Optional params:
    perms=<mode>       - Controls whether to retrieve owned, shared, or both. Defaults to both.
    include_history=<bool> - Controls whether to retrieve history docs. Defaults to false.
    include_trashed=<bool> - Controls whether to retrieve docs in the trash. Defaults to true.
    include_managed=<bool> - Controls whether to retrieve docs generated by Hue. Defaults to false.
    flatten=<bool>     - Controls whether to return documents in a flat list, or roll up documents to a common directory
                         if possible. Defaults to true.
    page=<n>           - Controls pagination. Defaults to 1.
    limit=<n>          - Controls limit per page. Defaults to all.
    type=<type>        - Show documents of given type(s) (directory, query-hive, query-impala, query-mysql, etc).
                         Defaults to all. Can appear multiple times.
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
  include_managed = json.loads(request.GET.get('include_managed', 'false'))
  flatten = json.loads(request.GET.get('flatten', 'true'))

  if perms not in ['owned', 'shared', 'both']:
    raise PopupException(_('Invalid value for perms, acceptable values are: owned, shared, both.'))

  documents = Document2.objects.documents(
    user=request.user,
    perms=perms,
    include_history=include_history,
    include_trashed=include_trashed,
    include_managed=include_managed
  )

  # Refine results
  response.update(_filter_documents(request, queryset=documents, flatten=flatten))

  # Paginate
  response.update(_paginate(request, queryset=response['documents']))

  # Serialize results
  response['documents'] = [doc.to_dict() for doc in response.get('documents', [])]

  return JsonResponse(response)


def _search(user, perms='both', include_history=False, include_trashed=False, include_managed=False, search_text=None, limit=25):
  response = {
    'documents': []
  }

  documents = Document2.objects.documents(
    user=user,
    perms=perms,
    include_history=include_history,
    include_trashed=include_trashed,
    include_managed=include_managed
  )

  type_filters = None
  sort = '-last_modified'
  search_text = search_text
  flatten = True

  page = 1

  # Refine results
  response.update(__filter_documents(type_filters, sort, search_text, queryset=documents, flatten=flatten))

  # Paginate
  response.update(__paginate(page, limit, queryset=response['documents']))

  return response


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
  uuids = request.GET.get('uuids')
  with_data = request.GET.get('data', 'false').lower() == 'true'
  with_dependencies = request.GET.get('dependencies', 'false').lower() == 'true'

  if uuids:
    response = {
      'data_list': [_get_document_helper(request, uuid, with_data, with_dependencies, path) for uuid in uuids.split(',')],
      'status': 0
    }
  else:
    response = _get_document_helper(request, uuid, with_data, with_dependencies, path)

  return JsonResponse(response)


def _get_document_helper(request, uuid, with_data, with_dependencies, path):
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
    'data': '',
    'status': 0
  }

  response['user_perms'] = {
    'can_read': document.can_read(request.user),
    'can_write': document.can_write(request.user)
  }

  if with_data:
    data = json.loads(document.data)
    # Upgrade session properties for Hive and Impala
    if document.type.startswith('query'):
      from notebook.models import upgrade_session_properties
      notebook = Notebook(document=document)
      notebook = upgrade_session_properties(request, notebook)
      data = json.loads(notebook.data)
      if document.type == 'query-pig':  # Import correctly from before Hue 4.0
        properties = data['snippets'][0]['properties']
        if 'hadoopProperties' not in properties:
          properties['hadoopProperties'] = []
        if 'parameters' not in properties:
          properties['parameters'] = []
        if 'resources' not in properties:
          properties['resources'] = []
      if data.get('uuid') != document.uuid:  # Old format < 3.11
        data['uuid'] = document.uuid

    response['data'] = data

  if with_dependencies:
    response['dependencies'] = [dependency.to_dict() for dependency in document.dependencies.all()]
    response['dependents'] = [dependent.to_dict() for dependent in document.dependents.exclude(is_history=True).all()]

  # Get children documents if this is a directory
  if document.is_directory:
    directory = Directory.objects.get(id=document.id)

    # If this is the user's home directory, fetch shared docs too
    if document.is_home_directory:
      children = directory.get_children_and_shared_documents(user=request.user)
      response.update(_filter_documents(request, queryset=children, flatten=True))
    else:
      children = directory.get_children_documents()
      response.update(_filter_documents(request, queryset=children, flatten=False))

  # Paginate and serialize Results
  if 'documents' in response:
    response.update(_paginate(request, queryset=response['documents']))
    # Rename documents to children
    response['children'] = response.pop('documents')
    response['children'] = [doc.to_dict() for doc in response['children']]

  return response


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
def copy_document(request):
  uuid = json.loads(request.POST.get('uuid', '""'))

  if not uuid:
    raise PopupException(_('copy_document requires uuid'))

  # Document2 and Document model objects are linked and both are saved when saving
  document = Document2.objects.get_by_uuid(user=request.user, uuid=uuid)
  # Document model object
  document1 = document.doc.get()

  if document.type == 'directory':
    raise PopupException(_('Directory copy is not supported'))

  name = document.name + '-copy'

  # Make the copy of the Document2 model object
  copy_document = document.copy(name=name, owner=request.user)
  # Make the copy of Document model object too
  document1.copy(content_object=copy_document, name=name, owner=request.user)

  # Import workspace for all oozie jobs
  if document.type == 'oozie-workflow2' or document.type == 'oozie-bundle2' or document.type == 'oozie-coordinator2':
    from oozie.models2 import _import_workspace, Bundle, Coordinator, Workflow
    # Update the name field in the json 'data' field
    if document.type == 'oozie-workflow2':
      workflow = Workflow(document=document)
      workflow.update_name(name)
      workflow.update_uuid(copy_document.uuid)
      _import_workspace(request.fs, request.user, workflow)
      copy_document.update_data({'workflow': workflow.get_data()['workflow']})
      copy_document.save()

    if document.type == 'oozie-bundle2' or document.type == 'oozie-coordinator2':
      if document.type == 'oozie-bundle2':
        bundle_or_coordinator = Bundle(document=document)
      else:
        bundle_or_coordinator = Coordinator(document=document)
      json_data = bundle_or_coordinator.get_data_for_json()
      json_data['name'] = name
      json_data['uuid'] = copy_document.uuid
      copy_document.update_data(json_data)
      copy_document.save()
      _import_workspace(request.fs, request.user, bundle_or_coordinator)
  elif document.type == 'search-dashboard':
    from dashboard.models import Collection2
    collection = Collection2(request.user, document=document)
    collection.data['collection']['label'] = name
    collection.data['collection']['uuid'] = copy_document.uuid
    copy_document.update_data({'collection': collection.data['collection']})
    copy_document.save()
  # Keep the document and data in sync
  else:
    copy_data = copy_document.data_dict
    if 'name' in copy_data:
      copy_data['name'] = name
    if 'uuid' in copy_data:
      copy_data['uuid'] = copy_document.uuid
    copy_document.update_data(copy_data)
    copy_document.save()

  return JsonResponse({
    'status': 0,
    'document': copy_document.to_dict()
  })


@api_error_handler
@require_POST
def restore_document(request):
  """
  Accepts a uuid

  Restores the document to /home
  """
  uuids = json.loads(request.POST.get('uuids'))

  if not uuids:
    raise PopupException(_('restore_document requires comma separated uuids'))

  for uuid in uuids.split(','):
    document = Document2.objects.get_by_uuid(user=request.user, uuid=uuid, perm_type='write')
    document.restore()

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
  if not is_admin(request.user) and not ENABLE_SHARING.get():
    return serve_403_error(request)

  uuid = request.POST.get('uuid')
  perms_dict = request.POST.get('data')

  if not uuid or not perms_dict:
    raise PopupException(_('share_document requires uuid and perms_dict'))
  else:
    perms_dict = json.loads(perms_dict)
    uuid = json.loads(uuid)

  doc = Document2.objects.get_by_uuid(user=request.user, uuid=uuid)

  for name, perm in perms_dict.items():
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


@api_error_handler
@require_POST
def handle_task_submit(request):
  # Extract the task name and params from the request
  try:
    data = json.loads(request.body)
    task_name = data.get('taskName')
    task_params = data.get('taskParams')
  except json.JSONDecodeError as e:
    return JsonResponse({'error': str(e)}, status=500)

  if task_name == 'document_cleanup':
    keep_days = task_params.get('keep_days')
    task_kwargs = {
      'keep_days': keep_days,
      'user_id': request.user.id,
      'username': request.user.username,
    }
    # Enqueue the document cleanup task with keyword arguments
    task = document_cleanup_task.apply_async(kwargs=task_kwargs)

    # Return a response indicating the task has been scheduled
    return JsonResponse({
      'taskName': task_name,
      'taskParams': task_params,
      'status': 'Scheduled',
      'task_id': task.id,  # The task ID generated by Celery
    })

  elif task_name == 'tmp_clean_up':
    cleanup_threshold = task_params.get('cleanup_threshold')
    disk_check_interval = task_params.get('disk_check_interval')
    task_kwargs = {
      'username': request.user.username,
      'cleanup_threshold': cleanup_threshold,
      'disk_check_interval': disk_check_interval
    }
    task = check_disk_usage_and_clean_task.apply_async(kwargs=task_kwargs)

    return JsonResponse({
      'taskName': task_name,
      'status': 'Scheduled',
      'task_id': task.id,  # The task ID generated by Celery
    })

  return JsonResponse({
    'status': 0
  })


@api_error_handler
@require_GET
def get_tasks(request):
  if not TASK_SERVER_V2.ENABLED.get():
    return JsonResponse({'error': 'Task server is not enabled'}, status=400)

  """Retirve the tasks from the database"""
  redis_client = parse_broker_url(TASK_SERVER_V2.BROKER_URL.get())
  tasks = []
  try:
    # Use scan_iter to efficiently iterate over keys matching the first pattern
    for key in redis_client.scan_iter('celery-task-meta-*'):
      task = json.loads(redis_client.get(key))
      tasks.append(task)

    # Use scan_iter to efficiently iterate over keys matching the second pattern
    for key in redis_client.scan_iter('task:*'):
      task = json.loads(redis_client.get(key))
      tasks.append(task)

    return JsonResponse(tasks, safe=False)
  except Exception as e:
    LOG.exception("Failed to retrieve tasks: %s", str(e))
    return JsonResponse({'error': str(e)}, status=500)
  finally:
    redis_client.close()


@api_error_handler
@require_GET
def check_upload_task_status(request):
  task_id = request.GET.get('task_id')
  if not task_id:
    return JsonResponse({'error': "Missing parameters: task_id is required"}, status=400)

  return _check_upload_task_status(task_id)


def _check_upload_task_status(task_id):
  redis_client = parse_broker_url(TASK_SERVER_V2.BROKER_URL.get())
  try:
    task_key = f'celery-task-meta-{task_id}'
    task_data = redis_client.get(task_key)

    if task_data is None:
      return JsonResponse({'error': 'Task not found'}, status=404)

    task = json.loads(task_data)
    is_finalized = task.get('status') == 'SUCCESS'
    is_running = task.get('status') == 'RUNNING'
    is_failure = task.get('status') == 'FAILURE'
    is_revoked = task.get('status') == 'REVOKED'

    return JsonResponse({'isFinalized': is_finalized, 'isRunning': is_running, 'isFailure': is_failure, 'isRevoked': is_revoked})
  except Exception as e:
    LOG.exception("Failed to check upload status: %s", str(e))
    return JsonResponse({'error': str(e)}, status=500)
  finally:
    redis_client.close()


@api_error_handler
@require_POST
def kill_task(request):
  task_id = request.POST.get('task_id')
  if not task_id:
    return JsonResponse({'error': "Missing parameters: task_id is required"}, status=400)

  # Check the current status of the task
  status_response = _check_upload_task_status(task_id)
  status_data = json.loads(status_response.content)

  if status_data.get('isFinalized') or status_data.get('isRevoked') or status_data.get('isFailure'):
    return JsonResponse({'status': 'info', 'message': f'Task {task_id} has already been completed or revoked.'})

  try:
    control = Control(app=celery_app)
    control.revoke(task_id, terminate=True)
    return JsonResponse({'status': 'success', 'message': f'Task {task_id} has been terminated.'})
  except Exception as e:
    return JsonResponse({'status': 'error', 'message': f'Failed to terminate task {task_id}: {str(e)}'})


@api_error_handler
@require_GET
def get_task_logs(request):
  task_id = request.GET.get('task_id')
  if not task_id:
    return JsonResponse({'error': "Missing parameters: task_id is required"}, status=400)

  log_dir = os.getenv("DESKTOP_LOG_DIR", DEFAULT_LOG_DIR)
  log_file = "%s/celery.log" % (log_dir)
  task_log = []
  escaped_task_id = re.escape(task_id)

  # Using a simpler and more explicit regex to debug
  task_end_pattern = re.compile(rf"\[{escaped_task_id}\].*succeeded")
  task_start_pattern = re.compile(rf"\[{escaped_task_id}\].*received")
  try:
    with open(log_file, 'r') as file:
      recording = False
      for line in file:
        if task_start_pattern.search(line):
          recording = True  # Start recording log lines
        if recording:
          task_log.append(line)
        if task_end_pattern.search(line) and recording:
          break  # Stop recording after finding the end of the task

  except FileNotFoundError:
    return HttpResponse(f'Log file not found at {log_file}', status=404)
  except Exception as e:
    return HttpResponse(str(e), status=500)

  return HttpResponse(''.join(task_log), content_type='text/plain')


@api_error_handler
@require_POST
def share_document_link(request):
  """
  Globally activate or de-activate access to a document for logged-in users.

  Example of input: {"uuid": "xxxx", "perm": "read" / "write" / "off"}
  """
  if not is_admin(request.user) and not ENABLE_SHARING.get():
    return serve_403_error(request)

  uuid = request.POST.get('uuid')
  perm = request.POST.get('perm')

  if not uuid or not perm:
    raise PopupException(_('share_document_link requires uuid and permission data'))
  else:
    uuid = json.loads(uuid)
    perm = json.loads(perm)

  doc = Document2.objects.get_by_uuid(user=request.user, uuid=uuid)
  doc = doc.share_link(request.user, perm=perm)

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

  include_history = request.GET.get('history', 'false') == 'true'

  # Only export documents the user has permissions to read
  docs = Document2.objects.documents(user=request.user, perms='both', include_history=True, include_trashed=True).\
    filter(id__in=selection).order_by('-id')

  # Add any dependencies to the set of exported documents
  export_doc_set = _get_dependencies(docs, include_history=include_history)

  # For directories, add any children docs to the set of exported documents
  export_doc_set.update(_get_dependencies(docs, deps_mode=False))

  # Get PKs of documents to export
  doc_ids = [doc.pk for doc in export_doc_set]
  num_docs = len(doc_ids)

  if len(selection) == 1 and num_docs >= len(selection) and docs[0].name:
    filename = docs[0].name
  else:
    filename = 'hue-documents-%s-(%s)' % (datetime.today().strftime('%Y-%m-%d'), num_docs)

  f = string_io()

  if doc_ids:
    doc_ids = ','.join(map(str, doc_ids))
    management.call_command(
      'dumpdata', 'desktop.Document2', primary_keys=doc_ids, indent=2, use_natural_foreign_keys=True, verbosity=2, stdout=f
    )

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
        except Exception as e:
          LOG.exception(e)
    zfile.close()
    response = HttpResponse(content_type="application/zip")
    response["Content-Length"] = len(f.getvalue())
    response['Content-Disposition'] = b'attachment; filename="%s".zip' % filename
    response.write(f.getvalue())
    return response
  else:
    return make_response(f.getvalue(), 'json', filename)


@ensure_csrf_cookie
def import_documents(request):
  def is_reserved_directory(doc):
    return doc['fields']['type'] == 'directory' and doc['fields']['name'] in (Document2.HOME_DIR, Document2.TRASH_DIR)

  try:
    if request.FILES.get('documents'):
      documents = request.FILES['documents'].read()
    else:
      documents = json.loads(request.POST.get('documents'))

    documents = json.loads(documents)
  except ValueError:
    raise PopupException(_('Failed to import documents, the file does not contain valid JSON.'))

  # Validate documents
  if not _is_import_valid(documents):
    raise PopupException(_('Failed to import documents, the file does not contain the expected JSON schema for Hue documents.'))

  docs = []

  uuids_map = dict((doc['fields']['uuid'], None) for doc in documents if not is_reserved_directory(doc))

  for doc in documents:
    # Filter docs to import, ignoring reserved directories (home and Trash) and history docs
    if not is_reserved_directory(doc):
      # Remove any deprecated fields
      if 'tags' in doc['fields']:
        doc['fields'].pop('tags')

      # If doc is not owned by current user, make a copy of the document with current user as owner
      if doc['fields']['owner'][0] != request.user.username:
        doc = _copy_document_with_owner(doc, request.user, uuids_map)
      else:  # Update existing doc or create new
        doc = _create_or_update_document_with_owner(doc, request.user, uuids_map)

      # For oozie docs replace dependent uuids with the newly created ones
      if doc['fields']['type'].startswith('oozie-'):
        doc = _update_imported_oozie_document(doc, uuids_map)

      # If the doc contains any history dependencies, ignore them
      # NOTE: this assumes that each dependency is exported as an array using the natural PK [uuid, version, is_history]
      deps_minus_history = [dep for dep in doc['fields'].get('dependencies', []) if len(dep) >= 3 and not dep[2]]
      doc['fields']['dependencies'] = deps_minus_history

      # Replace illegal characters
      if '/' in doc['fields']['name']:
        new_name = doc['fields']['name'].replace('/', '-')
        LOG.warning("Found illegal slash in document named: %s, renaming to: %s." % (doc['fields']['name'], new_name))
        doc['fields']['name'] = new_name

      # Set last modified date to now
      doc['fields']['last_modified'] = datetime.now().replace(microsecond=0).isoformat()
      docs.append(doc)

  f = tempfile.NamedTemporaryFile(mode='w+', suffix='.json')
  f.write(json.dumps(docs))
  f.flush()

  stdout = string_io()
  try:
    with transaction.atomic():  # We wrap both commands to commit loaddata & sync
      management.call_command('loaddata', f.name, verbosity=3, traceback=True, stdout=stdout)
      Document.objects.sync()

    if request.POST.get('redirect'):
      return redirect(request.POST.get('redirect'))
    else:
      return JsonResponse({
        'status': 0,
        'message': stdout.getvalue(),
        'count': len(documents),
        'created_count': len([doc for doc in documents if doc['pk'] is None]),
        'updated_count': len([doc for doc in documents if doc['pk'] is not None]),
        'username': request.user.username,
        'documents': [
          dict([
            ('name', doc['fields']['name']),
            ('uuid', doc['fields']['uuid']),
            ('type', doc['fields']['type']),
            ('owner', doc['fields']['owner'][0])
          ]) for doc in docs]
      })
  except Exception as e:
    LOG.error('Failed to run loaddata command in import_documents:\n %s' % stdout.getvalue())
    return JsonResponse({'status': -1, 'message': smart_str(e)})
  finally:
    stdout.close()


def _update_imported_oozie_document(doc, uuids_map):
  for key, value in uuids_map.items():
    if value:
      doc['fields']['data'] = doc['fields']['data'].replace(key, value)

  return doc


def user_preferences(request, key=None):
  response = {'status': 0, 'data': {}}

  if request.method != "POST":
    response['data'] = get_user_preferences(request.user, key)
  else:
    if "set" in request.POST:
      x = set_user_preferences(request.user, key, request.POST["set"])
      response['data'] = {key: x.value}
    elif "delete" in request.POST:
      try:
        x = UserPreferences.objects.get(user=request.user, key=key)
        x.delete()
      except UserPreferences.DoesNotExist:
        pass

  return JsonResponse(response)


@api_error_handler
def gist_create(request):
  '''
  Only supporting Editor App currently.
  '''

  statement = request.POST.get('statement', '')
  gist_type = request.POST.get('doc_type', 'hive')
  name = request.POST.get('name', '')
  _ = request.POST.get('description', '')

  response = _gist_create(request.get_host(), request.is_secure(), request.user, statement, gist_type, name)

  return JsonResponse(response)


def _gist_create(host_domain, is_http_secure, user, statement, gist_type, name=''):
  response = {'status': 0}

  statement_raw = statement
  if not statement.strip().startswith('--'):
    statement = '-- Created by %s\n\n%s' % (user.get_full_name() or user.username, statement)

  if not name:
    name = _('%s Query') % gist_type.capitalize()

  gist_doc = Document2.objects.create(
    name=name,
    type='gist',
    owner=user,
    data=json.dumps({'statement': statement, 'statement_raw': statement_raw}),
    extra=gist_type,
    parent_directory=Document2.objects.get_gist_directory(user)
  )

  response['id'] = gist_doc.id
  response['uuid'] = gist_doc.uuid
  response['link'] = '%(scheme)s://%(host)s/hue/gist?uuid=%(uuid)s' % {
    'scheme': 'https' if is_http_secure else 'http',
    'host': host_domain,
    'uuid': gist_doc.uuid,
  }

  return response


@login_notrequired
@api_error_handler
def gist_get(request):
  gist_uuid = request.GET.get('uuid')

  gist_doc = _get_gist_document(uuid=gist_uuid)

  if ENABLE_GIST_PREVIEW.get() and 'Slackbot-LinkExpanding' in request.META.get('HTTP_USER_AGENT', ''):
    statement = json.loads(gist_doc.data)['statement_raw']
    return render(
      'unfurl_link.mako',
      request, {
        'title': _('SQL gist from %s') % (gist_doc.owner.get_full_name() or gist_doc.owner.username),
        'description': statement if len(statement) < 150 else (statement[:150] + '...'),
        'image_link': None
      }
    )
  else:
    return redirect('/hue/editor?gist=%(uuid)s&type=%(type)s' % {
      'uuid': gist_doc.uuid,
      'type': gist_doc.extra
    })


def search_entities(request):
  sources = json.loads(request.POST.get('sources')) or []

  if 'documents' in sources:
    search_text = json.loads(request.POST.get('query_s', ''))
    entities = _search(user=request.user, search_text=search_text)
    response = {
      'entities': [{
          'hue_name': _highlight(search_text, escape(e.name)),
          'hue_description': _highlight(search_text, escape(e.description)),
          'type': 'HUE',
          'last_modified': e.last_modified,
          'owner': escape(e.owner),
          'doc_type': escape(e.type),
          'originalName': escape(e.name),
          'link': e.get_absolute_url()
        } for e in entities['documents']
      ],
      'count': len(entities['documents']),
      'status': 0
    }

    return JsonResponse(response)
  else:
    if has_catalog(request.user):
      return metadata_search_entities(request)
    else:
      return JsonResponse({'status': 1, 'message': _('Navigator not enabled')})


def search_entities_interactive(request):
  sources = json.loads(request.POST.get('sources')) or []

  if 'documents' in sources:
    search_text = json.loads(request.POST.get('query_s', ''))
    limit = int(request.POST.get('limit', 25))
    entities = _search(user=request.user, search_text=search_text, limit=limit)
    response = {
      'results': [{
          'hue_name': _highlight(search_text, escape(e.name)),
          'hue_description': _highlight(search_text, escape(e.description)),
          'link': e.get_absolute_url(),
          'doc_type': escape(e.type),
          'last_modified': e.last_modified,
          'owner': escape(e.owner),
          'type': 'HUE',
          'uuid': e.uuid,
          'parentUuid': e.parent_directory.uuid,
          'originalName': escape(e.name)
        }
        for e in entities['documents']
      ],
      'count': len(entities['documents']),
      'status': 0
    }

    return JsonResponse(response)
  else:
    if has_catalog(request.user):
      return metadata_search_entities_interactive(request)
    else:
      return JsonResponse({'status': 1, 'message': _('Navigator not enabled')})


def _is_import_valid(documents):
  """
  Validates the JSON file to be imported for schema correctness
  :param documents: object loaded from JSON file
  :return: True if schema seems valid, False otherwise
  """
  return isinstance(documents, list) and \
    all(isinstance(d, dict) for d in documents) and \
    all(all(k in d for k in ('pk', 'model', 'fields')) for d in documents) and \
    all(all(k in d['fields'] for k in ('uuid', 'owner')) for d in documents)


def _get_dependencies(documents, deps_mode=True, include_history=False):
  """
  Given a list of Document2 objects, perform a depth-first search and return a set of documents with all
   dependencies (excluding history docs) included
  :param doc_set: set of Document2 objects to include
  :param deps_mode: traverse dependencies relationship, otherwise traverse children relationship
  """
  doc_set = set()

  for doc in documents:
    stack = [doc]
    while stack:
      curr_doc = stack.pop()
      if curr_doc not in doc_set and (include_history or not curr_doc.is_history):
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

  # Update UUID in data if needed
  if 'data' in doc['fields']:
    data = json.loads(doc['fields']['data'])
    if 'uuid' in data:
      data['uuid'] = uuids_map[old_uuid]
      doc['fields']['data'] = json.dumps(data)

  # Remap parent directory if needed
  parent_uuid = None
  if doc['fields'].get('parent_directory'):
    parent_uuid = doc['fields']['parent_directory'][0]

  if parent_uuid is not None and parent_uuid in list(uuids_map.keys()):
    if uuids_map[parent_uuid] is None:
      uuids_map[parent_uuid] = uuid_default()
    doc['fields']['parent_directory'] = [uuids_map[parent_uuid], 1, False]
  else:
    if parent_uuid is not None:
      LOG.warning('Could not find parent directory with UUID: %s in JSON import, will set parent to home directory' %
                parent_uuid)
    doc['fields']['parent_directory'] = [home_dir.uuid, home_dir.version, home_dir.is_history]

  # Remap dependencies if needed
  idx = 0
  for dep_uuid, dep_version, dep_is_history in doc['fields']['dependencies']:
    if dep_uuid not in list(uuids_map.keys()):
      LOG.warning('Could not find dependency UUID: %s in JSON import, may cause integrity errors if not found.' % dep_uuid)
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
  except FilesystemException:
    create_new = True

  if create_new:
    LOG.warning('Could not find document with UUID: %s, will create a new document on import.', doc['fields']['uuid'])
    doc['pk'] = None
    doc['fields']['version'] = 1

  # Verify that parent exists, log warning and set parent to user's home directory if not found
  if doc['fields']['parent_directory']:
    uuid, version, is_history = doc['fields']['parent_directory']
    if uuid not in list(uuids_map.keys()) and \
            not Document2.objects.filter(uuid=uuid, version=version, is_history=is_history).exists():
      LOG.warning('Could not find parent document with UUID: %s, will set parent to home directory' % uuid)
      doc['fields']['parent_directory'] = [home_dir.uuid, home_dir.version, home_dir.is_history]

  # Verify that dependencies exist, raise critical error if any dependency not found
  # Ignore history dependencies
  if doc['fields']['dependencies']:
    history_deps_list = []
    for index, (uuid, version, is_history) in enumerate(doc['fields']['dependencies']):
      if uuid not in list(uuids_map.keys()) and not is_history and \
      not Document2.objects.filter(uuid=uuid, version=version).exists():
        raise PopupException(_('Cannot import document, dependency with UUID: %s not found.') % uuid)
      elif is_history:
        history_deps_list.insert(0, index)  # Insert in decreasing order to facilitate delete
        LOG.warning('History dependency with UUID: %s ignored while importing document %s' % (uuid, doc['fields']['name']))

    # Delete history dependencies not found in the DB
    for index in history_deps_list:
      del doc['fields']['dependencies'][index]

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

  return __filter_documents(type_filters, sort, search_text, queryset, flatten)


def __filter_documents(type_filters, sort, search_text, queryset, flatten=True):
  documents = queryset.search_documents(
      types=type_filters,
      search_text=search_text,
      order_by=sort
  )

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

  return __paginate(page, limit, queryset)


@api_error_handler
def available_app_examples(request):
  """Returns a dictionary of available apps whose examples can be installed by the admin user."""

  if not is_admin(request.user):
    return JsonResponse({'message': "You must be a Hue admin to access this endpoint."}, status=403)

  supported_app_examples = {'hive', 'impala', 'hbase', 'pig', 'oozie', 'notebook', 'search', 'spark', 'jobsub'}

  # Filter apps based on supported list
  available_examples = {app.name: app.nice_name for app in appmanager.get_apps(request.user) if app.name in supported_app_examples}

  return JsonResponse({'apps': available_examples})


@api_error_handler
def install_app_examples(request):
  app_name = request.POST.get('app_name')
  if not app_name:
    return JsonResponse({'message': "Missing parameter: app_name is required."}, status=400)

  if not is_admin(request.user):
    return JsonResponse({'message': "You must be a Hue admin to access this endpoint."}, status=403)

  # Define supported apps and their setup functions
  setup_functions = {
    'hive': _setup_hive_impala_examples,
    'impala': _setup_hive_impala_examples,
    'hbase': _setup_hbase_examples,
    'pig': _setup_pig_examples,
    'oozie': _setup_oozie_examples,
    'notebook': _setup_notebook_examples,
    'search': _setup_search_examples,
  }

  if app_name not in setup_functions:
    return JsonResponse({'message': f"Unsupported app name: {app_name}"}, status=400)

  response = setup_functions[app_name](request)
  return response if response else JsonResponse({'message': f"Successfully installed examples for {app_name}."})


def _setup_hive_impala_examples(request):
  dialect = request.POST.get('dialect', 'hive')
  db_name = request.POST.get('database_name', 'default')

  if dialect not in ('hive', 'impala'):
    return JsonResponse({'message': "Invalid dialect: Must be 'hive' or 'impala'"}, status=400)

  interpreter = common.find_compute(dialect=dialect, user=request.user)

  # Execute Hive/Impala examples installation
  beeswax_install_examples.Command().handle(dialect=dialect, db_name=db_name, user=request.user, request=request, interpreter=interpreter)


def _setup_hbase_examples(request):
  hbase_setup.Command().handle(user=request.user)


def _setup_pig_examples(request):
  pig_setup.Command().handle()


def _setup_oozie_examples(request):
  # Import dynamically to avoid oozie INSTALLED_APPS error
  from oozie.management.commands import oozie_setup

  oozie_setup.Command().handle()


def _setup_notebook_examples(request):
  try:
    connector = Connector.objects.get(id=request.POST.get('connector_id'))
  except Exception as e:
    LOG.error(f'Error getting connector: {e}')
    connector = None

  if connector:
    dialect = connector.dialect
    db_name = request.POST.get('database_name', 'default')

    # Execute Notebook examples installation using the specified connector
    beeswax_install_examples.Command().handle(
      dialect=dialect,
      db_name=db_name,
      user=request.user,
      interpreter=get_interpreter(connector_type=connector.to_dict()['type'], user=request.user),
      request=request,
    )
  else:
    notebook_setup.Command().handle(user=request.user, dialect=request.POST.get('dialect', 'hive'))


def _setup_search_examples(request):
  data = request.POST.get('data')
  indexer_setup.Command().handle(data=data)

  if data == 'log_analytics_demo':
    search_setup.Command().handle()


@api_error_handler
def check_config(request):
  """Returns the configuration directory and the list of validation errors."""
  response = {
    'hue_config_dir': os.path.realpath(os.getenv("HUE_CONF_DIR", get_desktop_root("conf"))),
    'config_errors': _get_config_errors(request, cache=False),
  }

  return JsonResponse(response)
