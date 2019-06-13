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
from security.conf import HIVE_V1, HIVE_V2, SOLR_V2

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


<%def name="menubar(section='', is_embeddable=False)">
  <link href="${ static('security/css/security.css') }" rel="stylesheet">

  <div class="navbar hue-title-bar">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="app-header">
                <a href="/${app_name}">
                  <i class="fa fa-lock"></i>
                  ${ _('Security Browser') if is_embeddable else _('Hadoop Security') }
                </a>
              </li>
              % if HIVE_V1.get():
              <li class="${is_selected(section, 'hive1')}"><a href="${ url('security:hive') }">${_('Hive Tables')}</a></li>
              % endif
              % if HIVE_V2.get():
              <li class="${is_selected(section, 'hive')}"><a href="${ url('security:hive2') }">${_('Hive Tables v2')}</a></li>
              % endif
              % if SOLR_V2.get():
              <li class="${is_selected(section, 'solr')}"><a href="${ url('security:solr') }">${_('Solr Collections')}</a></li>
              % endif
              <li class="${is_selected(section, 'hdfs')}"><a href="${ url('security:hdfs') }">${_('File ACLs')}</a></li>
            </ul>
          </div>
        </div>
      </div>
  </div>
</%def>
