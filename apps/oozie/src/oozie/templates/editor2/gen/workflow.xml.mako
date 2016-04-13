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


<workflow-app name="${ wf.validated_name }" xmlns="${ 'uri:oozie:workflow:0.5' if wf.has_some_slas else workflow['properties']['schema_version'] | n,unicode }"${ ' xmlns:sla="uri:oozie:sla:0.2"' if wf.has_some_slas else '' | n,unicode }>
  % if workflow['properties']['job_xml'] or workflow['properties']['properties']:
  <global>
    % if workflow['properties']['job_xml']:
      <job-xml>${ workflow['properties']['job_xml'] | x }</job-xml>
    % endif
    % if workflow['properties']['properties']:
      ${ common.configuration(workflow['properties']['properties']) | x }
    % endif
  </global>
  % endif
  % if wf.credentials and mapping.get('security_enabled'):
  <credentials>
    % for cred_type in wf.credentials:
    <%
      credential = mapping['credentials'][cred_type]
    %>
    <credential name="${ credential['xml_name'] }" type="${ cred_type }">
    % for name, value in credential['properties']:
      <property>
        <name>${ name }</name>
        <value>${ value }</value>
      </property>
    % endfor
    </credential>
    % endfor
  </credentials>
  % endif
  % for node in nodes:
      ${ node.to_xml(mapping, node_mapping, workflow_mapping) | n }
  % endfor
  ${ common.sla(workflow) }
</workflow-app>
