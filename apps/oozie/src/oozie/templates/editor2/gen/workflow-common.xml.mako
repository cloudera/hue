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
  from oozie.utils import smart_path, contains_symlink
%>


<%def name="filelink(path)">${ '#' in path and path or path + '#' + posixpath.basename(path) }</%def>


<%def name="credentials(credentials)">${ ' cred="%s"' % ','.join(credentials) if credentials else '' | n,unicode }</%def>


<%def name="retry_max(retry)">${ ' retry-max="%(value)s"' % retry[0] if retry else '' | n,unicode }</%def>


<%def name="retry_interval(retry)">${ ' retry-interval="%(value)s"' % retry[0] if retry else '' | n,unicode }</%def>


<%def name="prepares(prepares)">
        % if prepares and any(p for p in prepares if p['value']):
            <prepare>
                % for p in sorted(prepares, key=lambda k: k['type']):
                  <%
                    operation = p['type']
                    path = p['value']
                  %>
                  % if path:
                  <${ operation } path="${ smart_path(path, mapping) }"/>
                  % endif
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
          % if contains_symlink(f['value'], mapping):
            <file>${ f['value'] }</file>
          % else:
            <file>${ filelink(f['value']) }</file>
          % endif
        % endif
    % endfor
    % for a in archives:
        % if a:
            <archive>${ filelink(a['name']) }</archive>
        % endif
    % endfor
</%def>


<%def name="sla(element)">
        % if element['properties']['sla'][0].get('value'):
          <sla:info>
          % for sla in element['properties']['sla']:
            % if sla['value'] and sla['key'] != 'enabled':
            <sla:${ sla['key'] }>${ sla['value'] }</sla:${ sla['key'] }>
            % endif
          % endfor
          </sla:info>
        % endif
</%def>
