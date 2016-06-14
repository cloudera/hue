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

from django.conf.urls import patterns, url


IS_URL_NAMESPACED = True


urlpatterns = patterns(
  'oozie.views.editor',

  url(r'^list_workflows/$', 'list_workflows', name='list_workflows'),
  url(r'^list_trashed_workflows/$', 'list_trashed_workflows', name='list_trashed_workflows'),
  url(r'^create_workflow/$', 'create_workflow', name='create_workflow'),
  url(r'^edit_workflow/(?P<workflow>\d+)$', 'edit_workflow', name='edit_workflow'),
  url(r'^delete_workflow$', 'delete_workflow', name='delete_workflow'),
  url(r'^restore_workflow/$', 'restore_workflow', name='restore_workflow'),
  url(r'^clone_workflow/(?P<workflow>\d+)$', 'clone_workflow', name='clone_workflow'),
  url(r'^submit_workflow/(?P<workflow>\d+)$', 'submit_workflow', name='submit_workflow'),
  url(r'^schedule_workflow/(?P<workflow>\d+)$', 'schedule_workflow', name='schedule_workflow'),
  url(r'^import_workflow/$', 'import_workflow', name='import_workflow'),
  url(r'^import_coordinator/$', 'import_coordinator', name='import_coordinator'),
  url(r'^export_workflow/(?P<workflow>\d+)$', 'export_workflow', name='export_workflow'),

  url(r'^list_coordinators/(?P<workflow_id>[-\w]+)?$', 'list_coordinators', name='list_coordinators'),
  url(r'^list_trashed_coordinators/$', 'list_trashed_coordinators', name='list_trashed_coordinators'),
  url(r'^create_coordinator/(?P<workflow>[-\w]+)?$', 'create_coordinator', name='create_coordinator'),
  url(r'^edit_coordinator/(?P<coordinator>[-\w]+)$', 'edit_coordinator', name='edit_coordinator'),
  url(r'^delete_coordinator$', 'delete_coordinator', name='delete_coordinator'),
  url(r'^restore_coordinator$', 'restore_coordinator', name='restore_coordinator'),
  url(r'^clone_coordinator/(?P<coordinator>\d+)$', 'clone_coordinator', name='clone_coordinator'),
  url(r'^create_coordinator_dataset/(?P<coordinator>[-\w]+)$', 'create_coordinator_dataset', name='create_coordinator_dataset'),
  url(r'^edit_coordinator_dataset/(?P<dataset>\d+)$', 'edit_coordinator_dataset', name='edit_coordinator_dataset'),
  url(r'^create_coordinator_data/(?P<coordinator>[-\w]+)/(?P<data_type>(input|output))$', 'create_coordinator_data', name='create_coordinator_data'),
  url(r'^submit_coordinator/(?P<coordinator>\d+)$', 'submit_coordinator', name='submit_coordinator'),

  url(r'^list_bundles$', 'list_bundles', name='list_bundles'),
  url(r'^list_trashed_bundles$', 'list_trashed_bundles', name='list_trashed_bundles'),
  url(r'^create_bundle$', 'create_bundle', name='create_bundle'),
  url(r'^edit_bundle/(?P<bundle>\d+)$', 'edit_bundle', name='edit_bundle'),
  url(r'^submit_bundle/(?P<bundle>\d+)$', 'submit_bundle', name='submit_bundle'),
  url(r'^clone_bundle/(?P<bundle>\d+)$', 'clone_bundle', name='clone_bundle'),
  url(r'^delete_bundle$', 'delete_bundle', name='delete_bundle'),
  url(r'^restore_bundle$', 'restore_bundle', name='restore_bundle'),
  url(r'^create_bundled_coordinator/(?P<bundle>\d+)$', 'create_bundled_coordinator', name='create_bundled_coordinator'),
  url(r'^edit_bundled_coordinator/(?P<bundle>\d+)/(?P<bundled_coordinator>\d+)$', 'edit_bundled_coordinator', name='edit_bundled_coordinator'),

  url(r'^list_history$', 'list_history', name='list_history'), # Unused
  url(r'^list_history/(?P<record_id>[-\w]+)$', 'list_history_record', name='list_history_record'),
  url(r'^install_examples/$', 'install_examples', name='install_examples'),
)


urlpatterns += patterns(
  'oozie.views.editor2',

  url(r'^editor/workflow/list/$', 'list_editor_workflows', name='list_editor_workflows'),
  url(r'^editor/workflow/edit/$', 'edit_workflow', name='edit_workflow'),
  url(r'^editor/workflow/new/$', 'new_workflow', name='new_workflow'),
  url(r'^editor/workflow/delete/$', 'delete_job', name='delete_editor_workflow'),
  url(r'^editor/workflow/copy/$', 'copy_workflow', name='copy_workflow'),
  url(r'^editor/workflow/save/$', 'save_workflow', name='save_workflow'),
  url(r'^editor/workflow/submit/(?P<doc_id>\d+)$', 'submit_workflow', name='editor_submit_workflow'),
  url(r'^editor/workflow/submit_single_action/(?P<doc_id>\d+)/(?P<node_id>.+)$', 'submit_single_action', name='submit_single_action'),
  url(r'^editor/workflow/new_node/$', 'new_node', name='new_node'),
  url(r'^editor/workflow/add_node/$', 'add_node', name='add_node'),
  url(r'^editor/workflow/parameters/$', 'workflow_parameters', name='workflow_parameters'),
  url(r'^editor/workflow/action/parameters/$', 'action_parameters', name='action_parameters'),
  url(r'^editor/workflow/gen_xml/$', 'gen_xml_workflow', name='gen_xml_workflow'),
  url(r'^editor/workflow/open_v1/$', 'open_old_workflow', name='open_old_workflow'),
  
  url(r'^editor/coordinator/list/$', 'list_editor_coordinators', name='list_editor_coordinators'),
  url(r'^editor/coordinator/edit/$', 'edit_coordinator', name='edit_coordinator'),
  url(r'^editor/coordinator/new/$', 'new_coordinator', name='new_coordinator'),
  url(r'^editor/coordinator/delete/$', 'delete_job', name='delete_editor_coordinator'),
  url(r'^editor/coordinator/copy/$', 'copy_coordinator', name='copy_coordinator'),
  url(r'^editor/coordinator/save/$', 'save_coordinator', name='save_coordinator'),
  url(r'^editor/coordinator/submit/(?P<doc_id>\d+)$', 'submit_coordinator', name='editor_submit_coordinator'),
  url(r'^editor/coordinator/gen_xml/$', 'gen_xml_coordinator', name='gen_xml_coordinator'),
  url(r'^editor/coordinator/open_v1/$', 'open_old_coordinator', name='open_old_coordinator'),
  url(r'^editor/coordinator/parameters/$', 'coordinator_parameters', name='coordinator_parameters'),
  
  url(r'^editor/bundle/list/$', 'list_editor_bundles', name='list_editor_bundles'),
  url(r'^editor/bundle/edit/$', 'edit_bundle', name='edit_bundle'),
  url(r'^editor/bundle/new/$', 'new_bundle', name='new_bundle'),
  url(r'^editor/bundle/delete/$', 'delete_job', name='delete_editor_bundle'),
  url(r'^editor/bundle/copy/$', 'copy_bundle', name='copy_bundle'),
  url(r'^editor/bundle/save/$', 'save_bundle', name='save_bundle'),
  url(r'^editor/bundle/submit/(?P<doc_id>\d+)$', 'submit_bundle', name='editor_submit_bundle'),
  url(r'^editor/bundle/open_v1/$', 'open_old_bundle', name='open_old_bundle'),
)


urlpatterns += patterns(
  'oozie.views.api',

  url(r'^workflows$', 'workflows', name='workflows'),
  url(r'^workflows/(?P<workflow>\d+)$', 'workflow', name='workflow'),
  url(r'^workflows/(?P<workflow>\d+)/save$', 'workflow_save', name='workflow_save'),
  url(r'^workflows/(?P<workflow>\d+)/actions$', 'workflow_actions', name='workflow_actions'),
  url(r'^workflows/(?P<workflow>\d+)/nodes/(?P<node_type>\w+)/validate$', 'workflow_validate_node', name='workflow_validate_node'),
  url(r'^workflows/autocomplete_properties/$', 'autocomplete_properties', name='autocomplete_properties'),
)


urlpatterns += patterns(
  'oozie.views.dashboard',

  url(r'^$', 'list_oozie_workflows', name='index'),

  url(r'^list_oozie_workflows/$', 'list_oozie_workflows', name='list_oozie_workflows'),
  url(r'^list_oozie_coordinators/$', 'list_oozie_coordinators', name='list_oozie_coordinators'),
  url(r'^list_oozie_bundles/$', 'list_oozie_bundles', name='list_oozie_bundles'),
  url(r'^list_oozie_workflow/(?P<job_id>[-\w]+)/$', 'list_oozie_workflow', name='list_oozie_workflow'),
  url(r'^list_oozie_coordinator/(?P<job_id>[-\w]+)/$', 'list_oozie_coordinator', name='list_oozie_coordinator'),
  url(r'^list_oozie_workflow_action/(?P<action>[-\w@]+)/$', 'list_oozie_workflow_action', name='list_oozie_workflow_action'),
  url(r'^list_oozie_bundle/(?P<job_id>[-\w]+)$', 'list_oozie_bundle', name='list_oozie_bundle'),

  url(r'^rerun_oozie_job/(?P<job_id>[-\w]+)/(?P<app_path>.+?)$', 'rerun_oozie_job', name='rerun_oozie_job'),
  url(r'^rerun_oozie_coord/(?P<job_id>[-\w]+)/(?P<app_path>.+?)$', 'rerun_oozie_coordinator', name='rerun_oozie_coord'),
  url(r'^rerun_oozie_bundle/(?P<job_id>[-\w]+)/(?P<app_path>.+?)$', 'rerun_oozie_bundle', name='rerun_oozie_bundle'),
  url(r'^sync_coord_workflow/(?P<job_id>[-\w]+)$', 'sync_coord_workflow', name='sync_coord_workflow'),
  url(r'^manage_oozie_jobs/(?P<job_id>[-\w]+)/(?P<action>(start|suspend|resume|kill|rerun|change|ignore))$', 'manage_oozie_jobs', name='manage_oozie_jobs'),
  url(r'^bulk_manage_oozie_jobs/$', 'bulk_manage_oozie_jobs', name='bulk_manage_oozie_jobs'),

  url(r'^submit_external_job/(?P<application_path>.+?)$', 'submit_external_job', name='submit_external_job'),
  url(r'^get_oozie_job_log/(?P<job_id>[-\w]+)$', 'get_oozie_job_log', name='get_oozie_job_log'),

  url(r'^list_oozie_info/$', 'list_oozie_info', name='list_oozie_info'),

  url(r'^list_oozie_sla/$', 'list_oozie_sla', name='list_oozie_sla'),
)

urlpatterns += patterns(
  'oozie.views.common',
  url(r'^jasmine', 'jasmine', name='jasmine'),
)
