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
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="layout.mako" />
<%namespace name="macros" file="macros.mako" />

${ commonheader(_('Search'), "search", user) | n,unicode }

<%def name="indexProperty(key)">
  %if key in solr_core["status"][hue_core.name]["index"]:
      ${ solr_core["status"][hue_core.name]["index"][key] }
    %endif
</%def>
<%def name="coreProperty(key)">
  %if key in solr_core["status"][hue_core.name]:
      ${ solr_core["status"][hue_core.name][key] }
    %endif
</%def>

<%layout:skeleton>

  <%def name="title()">
    <h1>${_('Search Admin - ')}${hue_core.label}</h1>
  </%def>

  <%def name="navigation()">
    ${ layout.sidebar(hue_core.name, 'index') }
  </%def>

  <%def name="content()">
    <ul class="nav nav-tabs">
      <li class="active"><a href="#index" data-toggle="tab">${_('Index properties')}</a></li>
      <li><a href="#core" data-toggle="tab">${_('Core properties')}</a></li>
    </ul>
    <div class="tab-content">
      <div class="tab-pane active" id="index">
        <table class="table">
          <thead>
          <tr>
            <th width="20%">${_('Property')}</th>
            <th>${_('Value')}</th>
          </tr>
          </thead>
          <tbody>
          <tr>
            <td>sizeInBytes</td>
            <td>${ indexProperty('sizeInBytes') }</td>
          </tr>
          <tr>
            <td>segmentCount</td>
            <td>${ indexProperty('segmentCount') }</td>
          </tr>
          <tr>
            <td>maxDoc</td>
            <td>${ indexProperty('maxDoc') }</td>
          </tr>
          <tr>
            <td>lastModified</td>
            <td>${ indexProperty('lastModified') }</td>
          </tr>
          <tr>
            <td>current</td>
            <td>${ indexProperty('current') }</td>
          </tr>
          <tr>
            <td>version</td>
            <td>${ indexProperty('version') }</td>
          </tr>
          <tr>
            <td>directory</td>
            <td>${ indexProperty('directory') }</td>
          </tr>
          <tr>
            <td>numDocs</td>
            <td>${ indexProperty('numDocs') }</td>
          </tr>
          <tr>
            <td>hasDeletions</td>
            <td>${ indexProperty('hasDeletions') }</td>
          </tr>
          <tr>
            <td>size</td>
            <td>${ indexProperty('size') }</td>
          </tr>
          </tbody>
        </table>
      </div>
      <div class="tab-pane" id="core">
        <table class="table">
          <thead>
          <tr>
            <th width="20%">${_('Property')}</th>
            <th>${_('Value')}</th>
          </tr>
          </thead>
          <tbody>
          <tr>
            <td>uptime</td>
            <td>${ coreProperty('uptime') }</td>
          </tr>
          <tr>
            <td>name</td>
            <td>${ coreProperty('name') }</td>
          </tr>
          <tr>
            <td>isDefaultCore</td>
            <td>${ coreProperty('isDefaultCore') }</td>
          </tr>
          <tr>
            <td>dataDir</td>
            <td>${ coreProperty('dataDir') }</td>
          </tr>
          <tr>
            <td>instanceDir</td>
            <td>${ coreProperty('instanceDir') }</td>
          </tr>
          <tr>
            <td>startTime</td>
            <td>${ coreProperty('startTime') }</td>
          </tr>
          <tr>
            <td>config</td>
            <td>${ coreProperty('config') }</td>
          </tr>
          <tr>
            <td>schema</td>
            <td>${ coreProperty('schema') }</td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>

  </%def>
</%layout:skeleton>

${ commonfooter(messages) | n,unicode }


