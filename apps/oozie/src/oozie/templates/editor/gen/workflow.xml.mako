## -*- coding: utf-8 -*-
## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%namespace name="common" file="workflow-common.xml.mako" />


<workflow-app name="${ workflow.name | x }" xmlns="${ workflow.schema_version }">
  % if workflow.job_xml or workflow.get_properties():
  <global>
    % if workflow.job_xml:
      <job-xml>${ workflow.job_xml | x }</job-xml>
    % endif
    % if workflow.get_properties():
      ${ common.configuration(workflow.get_properties()) | x }
    % endif
  </global>
  % endif
  % for node in workflow.node_list:
      ${ node.to_xml(mapping) | n }
  % endfor
</workflow-app>
