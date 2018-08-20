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


%if node['properties'].get('auto-cluster'):
  <start to="${ node_mapping[node['children'][0]['to']].name }-start"/>

  <action name="${ node['name'] }-start"${ common.credentials(node['altus_action']['properties']['credentials']) }${ common.retry_max(node['altus_action']['properties']['retry_max']) }${ common.retry_interval(node['altus_action']['properties']['retry_interval']) }>
      <shell xmlns="uri:oozie:shell-action:0.1">
          <job-tracker>${'${'}jobTracker}</job-tracker>
          <name-node>${'${'}nameNode}</name-node>

          ${ common.prepares(node['altus_action']['properties']['prepares']) }
          % if node['altus_action']['properties']['job_xml']:
            <job-xml>${ node['altus_action']['properties']['job_xml'] }</job-xml>
          % endif
          ${ common.configuration(node['altus_action']['properties']['job_properties']) }

          <exec>${ node['altus_action']['properties']['shell_command'] }</exec>

          % for param in node['altus_action']['properties']['arguments']:
            <argument>${ param['value'] }</argument>
          % endfor
          
          % for param in node['altus_action']['properties']['env_var']:
            <env-var>${ param['value'] }</env-var>
          % endfor            

          ${ common.distributed_cache(node['altus_action']['properties']['files'], node['altus_action']['properties']['archives']) }

          % if node['altus_action']['properties']['capture_output']:
            <capture-output/>
          % endif
      </shell>
      <ok to="${ node_mapping[node['children'][0]['to']].name }"/>
      ##<error to="${ node_mapping[node['children'][1]['error']].name }"/>
      ${ common.sla(node) }
  </action>
%else:
    <start to="${ node_mapping[node['children'][0]['to']].name }"/>
%endif
