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

    <action name="${ node['name'] }"${ common.credentials(node['properties']['credentials']) }${ common.retry_max(node['properties']['retry_max']) }${ common.retry_interval(node['properties']['retry_interval']) }>
        <email xmlns="uri:oozie:email-action:0.2">
            <to>${ node['properties']['to'] }</to>
            % if node['properties']['cc']:
            <cc>${ node['properties']['cc'] }</cc>
            % endif
            % if node['properties']['bcc']:
            <bcc>${ node['properties']['bcc'] }</bcc>
            % endif
            <subject>${ node['properties']['subject'] }</subject>
            <body>${ node['properties']['body'] }</body>
            % if node['properties']['content_type']:
            <content_type>${ node['properties']['content_type'] }</content_type>
            % endif
            % if node['properties']['attachment']:
            <attachment>${ node['properties']['attachment'] }</attachment>
            % endif
        </email>
        <ok to="${ node_mapping[node['children'][0]['to']].name }"/>
        <error to="${ node_mapping[node['children'][1]['error']].name }"/>
        ${ common.sla(node) }
    </action>
