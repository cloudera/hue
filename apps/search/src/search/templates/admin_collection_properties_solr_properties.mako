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
  from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="layout.mako" />
<%namespace name="macros" file="macros.mako" />


<%def name="indexProperty(key)">
  % if hue_collection.is_core_only:
    % if key in solr_collection["status"][hue_collection.name]["index"]:
      ${ solr_collection["status"][hue_collection.name]["index"][key] }
    % endif
  % else:
    % for key, value in solr_collection.iteritems():
      ${ key } : ${ value }
    % endfor
  % endif
</%def>

<%def name="collectionProperty(key)">
  % if hue_collection.is_core_only:
    % if key in solr_collection["status"][hue_collection.name]:
      ${ solr_collection["status"][hue_collection.name][key] }
    % endif
  % else:
    % for key, value in solr_collection.iteritems():
      ${ key } : ${ value }
    % endfor
  % endif
</%def>

<%layout:skeleton>
  <%def name="title()">
  </%def>

  <%def name="content()">

  % if not hue_collection.is_core_only:
    <div class="tab-content">
      <div class="tab-pane active" id="index_properties">
        <table class="table">
          <thead>
          <tr>
            <th width="20%">${_('Property')}</th>
            <th>${_('Value')}</th>
          </tr>
          </thead>
          <tbody>
          <tr>
            % for key, value in solr_collection.iteritems():
              <td>${ key }</td>
              <td>${ value }</td>
            % endfor
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  % else:
    <ul class="nav nav-tabs">
      <li class="active"><a href="#index_properties" data-toggle="tab">${_('Index properties')}</a></li>
      <li><a href="#collection_properties" data-toggle="tab">${_('Collection properties')}</a></li>
    </ul>

    <div class="tab-content">
      <div class="tab-pane active" id="index_properties">
        <table class="table">
          <thead>
          <tr>
            <th width="20%">${_('Property')}</th>
            <th>${_('Value')}</th>
          </tr>
          </thead>
          <tbody>
          <tr>
            % for key, value in solr_collection.iteritems():
              <td>${ key }</td>
              <td>${ value }</td>
            % endfor
          </tr>
          </tbody>
        </table>
      </div>
      <div class="tab-pane" id="collection_properties">
        <table class="table">
          <thead>
          <tr>
            <th width="20%">${_('Property')}</th>
            <th>${_('Value')}</th>
          </tr>
          </thead>
          <tbody>
          <tr>
            % for key, value in solr_collection.iteritems():
              <td>${ key }</td>
              <td>${ value }</td>
            % endfor
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  % endif

  </%def>
</%layout:skeleton>
