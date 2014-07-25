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


def is_selected(section, matcher):
  if section == matcher:
    return "active"
  else:
    return ""
%>

<%def name="render_field(field, show_label=True, extra_attrs={})">
  % if not field.is_hidden:
    <% group_class = field.errors and "error" or "" %>
    <div class="control-group ${group_class}"
      rel="popover" data-original-title="${ field.label }" data-content="${ field.help_text }">
      % if show_label:
        <label class="control-label">${ field.label }</label>
      % endif
      <div class="controls">
        <% field.field.widget.attrs.update(extra_attrs) %>
        ${ field | n,unicode }
        % if field.errors:
          <span class="help-inline">${ field.errors | n,unicode }</span>
        % endif
      </div>
    </div>
  %endif
</%def>


<%def name="menubar(section='')">
  <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
##			<div class="pull-right" style="padding-right:50px; padding-top:10px">
##              <button type="button" title="${ _('Edit') }" rel="tooltip" data-placement="bottom" data-bind="css: {'btn': true, 'btn-inverse': true}"><i class="fa fa-pencil"></i></button>
##			</div>
            <ul class="nav">
              <li class="currentApp">
                <a href="/${app_name}">
                  <i class="fa fa-lock"></i>
                  ${ _('Hadoop Security') }
                </a>
              </li>
              <li class="${is_selected(section, 'hive')}"><a href="${ url('security:hive') }">${_('Hive')}</a></li>
              <li class="${is_selected(section, 'hdfs')}"><a href="${ url('security:hdfs') }">${_('HDFS')}</a></li>
              <li class="${is_selected(section, 'solr')}"><a href="${ url('security:hive') }s">${_('Solr')}</a></li>
              <li class="${is_selected(section, 'hbase')}"><a href="${ url('security:hive') }">${_('HBase')}</a></li>
            </ul>
          </div>
        </div>
      </div>
  </div>
</%def>
