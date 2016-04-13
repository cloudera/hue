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
%>

<%namespace name="common" file="workflow-common.xml.mako" />

    <action name="${ node }"${ common.credentials(node.credentials) }>
        <fs>
            % for param in node.get_deletes():
              <delete path='${ smart_path(param['name'], mapping) }'/>
            % endfor

            % for param in node.get_mkdirs():
              <mkdir path='${ smart_path(param['name'], mapping) }'/>
            % endfor

            % for param in node.get_moves():
              <move source='${ smart_path(param['source'], mapping) }' target='${ smart_path(param['destination'], mapping) }'/>
            % endfor

            % for param in node.get_chmods():
              <%
                if param['recursive']:
                  recursive = 'true'
                else:
                  recursive = 'false'
              %>
              <chmod path='${ smart_path(param['path'], mapping) }' permissions='${ param['permissions'] }' dir-files='${ recursive }'/>
            % endfor

            % for param in node.get_touchzs():
              <touchz path='${ smart_path(param['name'], mapping) }'/>
            % endfor
        </fs>
        <ok to="${ node.get_oozie_child('ok') }"/>
        <error to="${ node.get_oozie_child('error') }"/>
        ${ common.sla(node) }
    </action>
