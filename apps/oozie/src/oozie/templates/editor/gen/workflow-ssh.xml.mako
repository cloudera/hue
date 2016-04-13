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

    <action name="${ node }"${ common.credentials(node.credentials) }>
        <ssh xmlns="uri:oozie:ssh-action:0.1">
            <host>${ node.user }@${ node.host }</host>
            <command>${ node.command }</command>

            % for param in node.get_params():
              <args>${ param['value'] }</args>
            % endfor

            % if node.capture_output:
              <capture-output/>
            % endif
        </ssh>
        <ok to="${ node.get_oozie_child('ok') }"/>
        <error to="${ node.get_oozie_child('error') }"/>
        ${ common.sla(node) }
    </action>
