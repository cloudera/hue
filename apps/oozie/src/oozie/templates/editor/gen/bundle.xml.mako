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
  from oozie.models import BundledCoordinator
%>

<bundle-app name="${ bundle.name }"
  xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'
  xmlns="${ bundle.schema_version }">
  % if bundle.get_parameters():
  <parameters>
    % for p in bundle.get_parameters():
    <property>
        <name>${ p['name'] }</name>
        <value>${ p['value'] }</value>
    </property>
    % endfor
  </parameters>
  % endif

  <controls>
     <kick-off-time>${ bundle.kick_off_time_utc }</kick-off-time>
  </controls>


  % for bundled in BundledCoordinator.objects.filter(bundle=bundle):
  <coordinator name='${ bundled.coordinator.name }-${ bundled.id }' >
     <app-path>${'${'}nameNode}${ mapping['coord_%s_dir' % bundled.coordinator.id] }</app-path>
       <configuration>
         <property>
            <name>wf_application_path</name>
            <value>${ mapping['wf_%s_dir' % bundled.coordinator.coordinatorworkflow.id] }</value>
        </property>
         % for param in bundled.get_parameters():
         <property>
            <name>${ param['name'] }</name>
            <value>${ param['value'] }</value>
        </property>
        % endfor
      </configuration>
  </coordinator>
  % endfor
</bundle-app>
