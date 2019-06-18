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

<%!
  from oozie.utils import smart_path
  from oozie.conf import ENABLE_CRON_SCHEDULING
%>

<%namespace name="common" file="workflow-common.xml.mako" />


<%def name="render_dataset_instance(dataset)">
  % if dataset.data['instance_choice'] == 'default':
    <instance>${ '${'}coord:current(0)}</instance>
  % elif dataset.data['instance_choice'] == 'single':
    % if not dataset.data['is_advanced_start_instance']:
      <instance>${ '${'}coord:current(${ dataset.data['start_instance'] })}</instance>
    % else:
      <instance>${ dataset.data['advanced_start_instance'] }</instance>
    % endif
  % else:
    <start-instance>
      % if not dataset.data['is_advanced_start_instance']:
        ${ '${'}coord:current(${ dataset.data['start_instance'] })}
      % else:
        ${ dataset.data['advanced_start_instance'] }
      % endif
    </start-instance>
    <end-instance>
      % if not dataset.data['is_advanced_end_instance']:
        ${ '${'}coord:current(${ dataset.data['end_instance'] })}
      % else:
        ${ dataset.data['advanced_end_instance'] }
      % endif
    </end-instance>
  % endif
</%def>


<coordinator-app name="${ coord.validated_name | x }"
  % if ENABLE_CRON_SCHEDULING.get():
  frequency="${ coord.cron_frequency }"
  % else:
  frequency="${ coord.frequency }"
  % endif
  start="${ coord.start_server_tz }" end="${ coord.end_server_tz }" timezone="${ coord.data['properties']['timezone'] }"
  xmlns="${ 'uri:oozie:coordinator:0.4' if coord.sla_enabled else coord.data['properties']['schema_version'] | n,unicode }"
  ${ 'xmlns:sla="uri:oozie:sla:0.2"' if coord.sla_enabled else '' | n,unicode }>
  % if coord.data['properties'].get('timeout') or coord.data['properties'].get('concurrency') or coord.data['properties'].get('execution') or coord.data['properties'].get('throttle'):
  <controls>
    % if coord.data['properties'].get('timeout'):
    <timeout>${ coord.data['properties']['timeout'] }</timeout>
    % endif
    % if coord.data['properties'].get('concurrency'):
    <concurrency>${ coord.data['properties']['concurrency'] }</concurrency>
    % endif
    % if coord.data['properties'].get('execution'):
    <execution>${ coord.data['properties']['execution'] }</execution>
    % endif
    % if coord.data['properties'].get('throttle'):
    <throttle>${ coord.data['properties']['throttle'] }</throttle>
    % endif
  </controls>
  % endif

  % if coord.datasets:
  <datasets>
    % for dataset in coord.datasets:
    <dataset name="${ dataset.data['name'] }" frequency="${ dataset.frequency }"
             initial-instance="${ dataset.start_server_tz }" timezone="${ dataset.timezone }">
      <uri-template>${ smart_path(dataset.data['dataset_variable'], mapping, is_coordinator=True) }</uri-template>
      % if dataset.data['use_done_flag']:
      <done-flag>${ dataset.data['done_flag'] }</done-flag>
      % else:
      <done-flag></done-flag>
      % endif
    </dataset>
    % endfor
  </datasets>
  % endif

  % if coord.inputDatasets:
  <input-events>
    % for dataset in coord.inputDatasets:
    <data-in name="${ dataset.data['workflow_variable'] }" dataset="${ dataset.data['name'] }">
      ${ render_dataset_instance(dataset) }
    </data-in>
    % endfor
  </input-events>
  % endif

  % if coord.outputDatasets:
  <output-events>
    % for dataset in coord.outputDatasets:
    <data-out name="${ dataset.data['workflow_variable'] }" dataset="${ dataset.data['name'] }">
      ${ render_dataset_instance(dataset) }
    </data-out>
    % endfor
  </output-events>
  % endif

  <action>
    <workflow>
      <app-path>${'${'}wf_application_path}</app-path>
      % if coord.inputDatasets or coord.outputDatasets or coord.properties:
      <configuration>
        % for dataset in coord.inputDatasets:
          <property>
            <name>${ dataset.data['name'] }</name>
            <value>${'${'}coord:dataIn('${ dataset.data['name'] }')}</value>
          </property>
        % endfor
        % for dataset in coord.outputDatasets:
        <property>
          <name>${ dataset.data['name'] }</name>
          <value>${'${'}coord:dataOut('${ dataset.data['name'] }')}</value>
        </property>
        % endfor
        % for property in coord.properties:
        <property>
          % if property['name'] in ['start_date', 'end_date']:
            <name>${ property['name'] }</name>
            <value>${'${' + property['name']}}</value>
          % else:
            <name>${ property['name'] }</name>
            <value>${ property['value'] }</value>
          % endif
        </property>
        % endfor
      </configuration>
      % endif
   </workflow>
   ${ common.sla(coord.data) }
  </action>
</coordinator-app>
