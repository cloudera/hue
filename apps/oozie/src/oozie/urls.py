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

import sys

from oozie.views import editor as oozie_views_editor
from oozie.views import editor2 as oozie_views_editor2
from oozie.views import api as oozie_views_api
from oozie.views import dashboard as oozie_views_dashboard

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path

IS_URL_NAMESPACED = True


urlpatterns = [

  re_path(r'^list_workflows/?$', oozie_views_editor.list_workflows, name='list_workflows'),
  re_path(r'^list_trashed_workflows/?$', oozie_views_editor.list_trashed_workflows, name='list_trashed_workflows'),
  re_path(r'^create_workflow/?$', oozie_views_editor.create_workflow, name='create_workflow'),
  re_path(r'^edit_workflow/(?P<workflow>\d+)/?$', oozie_views_editor.edit_workflow, name='edit_workflow'),
  re_path(r'^delete_workflow$', oozie_views_editor.delete_workflow, name='delete_workflow'),
  re_path(r'^restore_workflow/?$', oozie_views_editor.restore_workflow, name='restore_workflow'),
  re_path(r'^clone_workflow/(?P<workflow>\d+)$', oozie_views_editor.clone_workflow, name='clone_workflow'),
  re_path(r'^submit_workflow/(?P<workflow>\d+)$', oozie_views_editor.submit_workflow, name='submit_workflow'),
  re_path(r'^schedule_workflow/(?P<workflow>\d+)$', oozie_views_editor.schedule_workflow, name='schedule_workflow'),
  re_path(r'^import_workflow/?$', oozie_views_editor.import_workflow, name='import_workflow'),
  re_path(r'^import_coordinator/?$', oozie_views_editor.import_coordinator, name='import_coordinator'),
  re_path(r'^export_workflow/(?P<workflow>\d+)$', oozie_views_editor.export_workflow, name='export_workflow'),

  re_path(r'^list_coordinators(?:/(?P<workflow_id>[-\w]+))?/?$', oozie_views_editor.list_coordinators, name='list_coordinators'),
  re_path(r'^list_trashed_coordinators/?$', oozie_views_editor.list_trashed_coordinators, name='list_trashed_coordinators'),
  re_path(r'^create_coordinator(?:/(?P<workflow>[-\w]+))?/?$', oozie_views_editor.create_coordinator, name='create_coordinator'),
  re_path(r'^edit_coordinator/(?P<coordinator>[-\w]+)$', oozie_views_editor.edit_coordinator, name='edit_coordinator'),
  re_path(r'^delete_coordinator$', oozie_views_editor.delete_coordinator, name='delete_coordinator'),
  re_path(r'^restore_coordinator$', oozie_views_editor.restore_coordinator, name='restore_coordinator'),
  re_path(r'^clone_coordinator/(?P<coordinator>\d+)$', oozie_views_editor.clone_coordinator, name='clone_coordinator'),
  re_path(
    r'^create_coordinator_dataset/(?P<coordinator>[-\w]+)$',
    oozie_views_editor.create_coordinator_dataset,
    name='create_coordinator_dataset'
  ),
  re_path(r'^edit_coordinator_dataset/(?P<dataset>\d+)$', oozie_views_editor.edit_coordinator_dataset, name='edit_coordinator_dataset'),
  re_path(
    r'^create_coordinator_data/(?P<coordinator>[-\w]+)/(?P<data_type>(input|output))$',
    oozie_views_editor.create_coordinator_data,
    name='create_coordinator_data'
  ),
  re_path(r'^submit_coordinator/(?P<coordinator>\d+)$', oozie_views_editor.submit_coordinator, name='submit_coordinator'),

  re_path(r'^list_bundles$', oozie_views_editor.list_bundles, name='list_bundles'),
  re_path(r'^list_trashed_bundles$', oozie_views_editor.list_trashed_bundles, name='list_trashed_bundles'),
  re_path(r'^create_bundle$', oozie_views_editor.create_bundle, name='create_bundle'),
  re_path(r'^edit_bundle/(?P<bundle>\d+)$', oozie_views_editor.edit_bundle, name='edit_bundle'),
  re_path(r'^submit_bundle/(?P<bundle>\d+)$', oozie_views_editor.submit_bundle, name='submit_bundle'),
  re_path(r'^clone_bundle/(?P<bundle>\d+)$', oozie_views_editor.clone_bundle, name='clone_bundle'),
  re_path(r'^delete_bundle$', oozie_views_editor.delete_bundle, name='delete_bundle'),
  re_path(r'^restore_bundle$', oozie_views_editor.restore_bundle, name='restore_bundle'),
  re_path(
    r'^create_bundled_coordinator/(?P<bundle>\d+)$', oozie_views_editor.create_bundled_coordinator, name='create_bundled_coordinator'
  ),
  re_path(
    r'^edit_bundled_coordinator/(?P<bundle>\d+)/(?P<bundled_coordinator>\d+)$',
    oozie_views_editor.edit_bundled_coordinator,
    name='edit_bundled_coordinator'
  ),

  re_path(r'^list_history$', oozie_views_editor.list_history, name='list_history'), # Unused
  re_path(r'^list_history/(?P<record_id>[-\w]+)$', oozie_views_editor.list_history_record, name='list_history_record'),
  re_path(r'^install_examples/?$', oozie_views_editor.install_examples, name='install_examples'),
]

urlpatterns += [

  re_path(r'^editor/workflow/list/?$', oozie_views_editor2.list_editor_workflows, name='list_editor_workflows'),
  re_path(r'^editor/workflow/edit/?$', oozie_views_editor2.edit_workflow, name='edit_workflow'),
  re_path(r'^editor/workflow/new/?$', oozie_views_editor2.new_workflow, name='new_workflow'),
  re_path(r'^editor/workflow/delete/?$', oozie_views_editor2.delete_job, name='delete_editor_workflow'),
  re_path(r'^editor/workflow/copy/?$', oozie_views_editor2.copy_workflow, name='copy_workflow'),
  re_path(r'^editor/workflow/save/?$', oozie_views_editor2.save_workflow, name='save_workflow'),
  re_path(r'^editor/workflow/submit/(?P<doc_id>\d+)$', oozie_views_editor2.submit_workflow, name='editor_submit_workflow'),
  re_path(
    r'^editor/workflow/submit_single_action/(?P<doc_id>\d+)/(?P<node_id>.+)$',
    oozie_views_editor2.submit_single_action,
    name='submit_single_action'
  ),
  re_path(r'^editor/workflow/new_node/?$', oozie_views_editor2.new_node, name='new_node'),
  re_path(r'^editor/workflow/add_node/?$', oozie_views_editor2.add_node, name='add_node'),
  re_path(r'^editor/workflow/parameters/?$', oozie_views_editor2.workflow_parameters, name='workflow_parameters'),
  re_path(r'^editor/workflow/action/parameters/?$', oozie_views_editor2.action_parameters, name='action_parameters'),
  re_path(r'^editor/workflow/gen_xml/?$', oozie_views_editor2.gen_xml_workflow, name='gen_xml_workflow'),
  re_path(r'^editor/workflow/open_v1/?$', oozie_views_editor2.open_old_workflow, name='open_old_workflow'),

  re_path(r'^editor/coordinator/list/?$', oozie_views_editor2.list_editor_coordinators, name='list_editor_coordinators'),
  re_path(r'^editor/coordinator/edit/?$', oozie_views_editor2.edit_coordinator, name='edit_coordinator'),
  re_path(r'^editor/coordinator/new/?$', oozie_views_editor2.new_coordinator, name='new_coordinator'),
  re_path(r'^editor/coordinator/delete/?$', oozie_views_editor2.delete_job, name='delete_editor_coordinator'),
  re_path(r'^editor/coordinator/copy/?$', oozie_views_editor2.copy_coordinator, name='copy_coordinator'),
  re_path(r'^editor/coordinator/save/?$', oozie_views_editor2.save_coordinator, name='save_coordinator'),
  re_path(r'^editor/coordinator/submit/(?P<doc_id>[-\w]+)$', oozie_views_editor2.submit_coordinator, name='editor_submit_coordinator'),
  re_path(r'^editor/coordinator/gen_xml/?$', oozie_views_editor2.gen_xml_coordinator, name='gen_xml_coordinator'),
  re_path(r'^editor/coordinator/open_v1/?$', oozie_views_editor2.open_old_coordinator, name='open_old_coordinator'),
  re_path(r'^editor/coordinator/parameters/?$', oozie_views_editor2.coordinator_parameters, name='coordinator_parameters'),

  re_path(r'^editor/bundle/list/?$', oozie_views_editor2.list_editor_bundles, name='list_editor_bundles'),
  re_path(r'^editor/bundle/edit/?$', oozie_views_editor2.edit_bundle, name='edit_bundle'),
  re_path(r'^editor/bundle/new/?$', oozie_views_editor2.new_bundle, name='new_bundle'),
  re_path(r'^editor/bundle/delete/?$', oozie_views_editor2.delete_job, name='delete_editor_bundle'),
  re_path(r'^editor/bundle/copy/?$', oozie_views_editor2.copy_bundle, name='copy_bundle'),
  re_path(r'^editor/bundle/save/?$', oozie_views_editor2.save_bundle, name='save_bundle'),
  re_path(r'^editor/bundle/submit/(?P<doc_id>\d+)$', oozie_views_editor2.submit_bundle, name='editor_submit_bundle'),
  re_path(r'^editor/bundle/open_v1/?$', oozie_views_editor2.open_old_bundle, name='open_old_bundle'),
]


urlpatterns += [

  re_path(r'^workflows/?$', oozie_views_api.workflows, name='workflows'),
  re_path(r'^workflows/(?P<workflow>\d+)$', oozie_views_api.workflow, name='workflow'),
  re_path(r'^workflows/(?P<workflow>\d+)/save$', oozie_views_api.workflow_save, name='workflow_save'),
  re_path(r'^workflows/(?P<workflow>\d+)/actions$', oozie_views_api.workflow_actions, name='workflow_actions'),
  re_path(
    r'^workflows/(?P<workflow>\d+)/nodes/(?P<node_type>\w+)/validate$',
    oozie_views_api.workflow_validate_node,
    name='workflow_validate_node'
  ),
  re_path(r'^workflows/autocomplete_properties/?$', oozie_views_api.autocomplete_properties, name='autocomplete_properties'),
]


urlpatterns += [

  re_path(r'^$', oozie_views_dashboard.list_oozie_workflows, name='index'),

  re_path(r'^list_oozie_workflows/?$', oozie_views_dashboard.list_oozie_workflows, name='list_oozie_workflows'),
  re_path(r'^list_oozie_coordinators/?$', oozie_views_dashboard.list_oozie_coordinators, name='list_oozie_coordinators'),
  re_path(r'^list_oozie_bundles/?$', oozie_views_dashboard.list_oozie_bundles, name='list_oozie_bundles'),
  re_path(r'^list_oozie_workflow/(?P<job_id>[-\w]+)/?$', oozie_views_dashboard.list_oozie_workflow, name='list_oozie_workflow'),
  re_path(r'^list_oozie_coordinator/(?P<job_id>[-\w]+)/?$', oozie_views_dashboard.list_oozie_coordinator, name='list_oozie_coordinator'),
  re_path(
    r'^list_oozie_workflow_action/(?P<action>[-\w@]+)/?$',
    oozie_views_dashboard.list_oozie_workflow_action,
    name='list_oozie_workflow_action'
  ),
  re_path(r'^list_oozie_bundle/(?P<job_id>[-\w]+)$', oozie_views_dashboard.list_oozie_bundle, name='list_oozie_bundle'),

  re_path(r'^rerun_oozie_job/(?P<job_id>[-\w]+)(?:/(?P<app_path>.+?))?/?$', oozie_views_dashboard.rerun_oozie_job, name='rerun_oozie_job'),
  re_path(
    r'^rerun_oozie_coord/(?P<job_id>[-\w]+)(?:/(?P<app_path>.+?))?/?$',
    oozie_views_dashboard.rerun_oozie_coordinator,
    name='rerun_oozie_coord'
  ),
  re_path(
    r'^rerun_oozie_bundle/(?P<job_id>[-\w]+)/(?P<app_path>.+?)$', oozie_views_dashboard.rerun_oozie_bundle, name='rerun_oozie_bundle'
  ),
  re_path(r'^sync_coord_workflow/(?P<job_id>[-\w]+)$', oozie_views_dashboard.sync_coord_workflow, name='sync_coord_workflow'),
  re_path(
    r'^manage_oozie_jobs/(?P<job_id>[-\w]+)/(?P<action>(start|suspend|resume|kill|rerun|change|ignore))$',
    oozie_views_dashboard.manage_oozie_jobs,
    name='manage_oozie_jobs'
  ),
  re_path(r'^bulk_manage_oozie_jobs/?$', oozie_views_dashboard.bulk_manage_oozie_jobs, name='bulk_manage_oozie_jobs'),

  re_path(r'^submit_external_job/(?P<application_path>.+?)$', oozie_views_dashboard.submit_external_job, name='submit_external_job'),
  re_path(r'^get_oozie_job_log/(?P<job_id>[-\w]+)$', oozie_views_dashboard.get_oozie_job_log, name='get_oozie_job_log'),

  re_path(r'^list_oozie_info/?$', oozie_views_dashboard.list_oozie_info, name='list_oozie_info'),

  re_path(r'^list_oozie_sla/?$', oozie_views_dashboard.list_oozie_sla, name='list_oozie_sla'),
]