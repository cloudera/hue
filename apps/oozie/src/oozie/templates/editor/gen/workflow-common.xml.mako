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
  import posixpath
  from oozie.utils import smart_path
%>


<%def name="filelink(path)">${ '#' in path and path or path + '#' + posixpath.basename(path) }</%def>


<%def name="credentials(credentials)">\
<% value = ','.join(cred['name'] for cred in credentials if cred['value']) %>\
% if value:
${ ' cred="%s"' % value | n,unicode }\
% endif
</%def>


<%def name="prepares(prepares)">
        % if prepares:
            <prepare>
                % for p in prepares:
                  <%
                    operation = p['type']
                    path = p['value']
                  %>
                  <${ operation } path="${ smart_path(path, mapping) }"/>
                % endfor
            </prepare>
        % endif
</%def>


<%def name="configuration(properties)">
        % if properties:
            <configuration>
                % for p in properties:
                <property>
                    <name>${ p['name'] }</name>
                    <value>${ p['value'] }</value>
                </property>
                % endfor
            </configuration>
        % endif
</%def>


<%def name="distributed_cache(files, archives)">
    % for f in files:
        % if f:
            <file>${ filelink(f) }</file>
        % endif
    % endfor
    % for a in archives:
        % if a:
            <archive>${ filelink(a['name']) }</archive>
        % endif
    % endfor
</%def>


<%def name="sla(element)">
        % if element.sla_enabled:
          <sla:info>
          % for sla in element.sla:
            % if sla['value'] and sla['key'] != 'enabled':
            <sla:${ sla['key'] }>${ sla['value'] }</sla:${ sla['key'] }>
            % endif
          % endfor
          </sla:info>
        % endif
</%def>
