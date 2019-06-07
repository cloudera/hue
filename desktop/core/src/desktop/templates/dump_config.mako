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
import logging

from desktop.lib.conf import BoundContainer, is_anonymous
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _

LOG = logging.getLogger(__name__)
%>

<%namespace name="layout" file="about_layout.mako" />

% if not is_embeddable:
  ${ commonheader(_('Configuration'), "about", user, request, "70px") | n,unicode }
% endif
  ${ layout.menubar(section='dump_config') }

<style type="text/css">
  .card-heading .pull-right {
    font-size: 12px;
    font-weight: normal;
  }
</style>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="card card-home">
      <div class="pull-right muted">
        ${_('Configuration files located in')} <code style="color: #0B7FAD">${conf_dir}</code>
      </div>
      <h1 class="margin-top-20 margin-bottom-30">
        ${_('Sections')}
      </h1>
      <div class="card-body clearfix">
        <div class="span2">
          <ul class="nav nav-pills nav-stacked">
            % for obj in top_level:
              <li
                % if loop.first:
                    class="active"
                % endif
              >
                <a href="#${ obj.config.key }Conf" data-toggle="tab">${ obj.config.key }</a>
              </li>
            % endfor
          </ul>
        </div>
        <div class="span10">
          ${showTopLevel(top_level)}
        </div>
      </div>
    </div>

    <div class="card card-home" style="margin-top: 50px">
      <h2 class="card-heading simple">${_('Installed Applications')}</h2>
      <div class="card-body">
      % for app in apps:
        % if app.menu_index != 999:
          <a href="/${app.display_name}"><span class="badge badge-info">${app.name}</span></a>
        % else:
          <span class="badge" title="${ _('This app does not have a UI') }">${app.name}</span>
        % endif
      % endfor
      </div>
    </div>

  </div>

  <%def name="showTopLevel(config_obj, depth=0)">
    <div class="tab-content">
      % for v in config_obj:
      <%
          # Don't recurse into private variables.
          if v.config.private and not show_private:
              continue
      %>
      <div id="${v.config.key}Conf" class="tab-pane
        % if loop.first:
            active
        % endif
        ">
        ${ recurse(v, depth + 1) }
      </div>
      % endfor
    </div>
  </%def>

    <%def name="recurseList(config_obj, depth=0)">
      <table class="table table-condensed recurse">
      % for v in config_obj:
        <%
          # Don't recurse into private variables.
          if v.config.private and not show_private:
            continue
        %>
        ${ recurse(v, depth + 1) }
      % endfor
      </table>
    </%def>

    <%def name="recurse(config_obj, depth=0)">
        <tr>
         % if depth > 1:
          <th>
          % if is_anonymous(config_obj.config.key):
            <i>(default section)</i>
          % else:
            ${ config_obj.config.key }
          % endif
          </th>
         % endif
         % if depth == 1:
            <td style="border-top:0">
         % else:
            <td>
         % endif
          % if isinstance(config_obj, BoundContainer):
            %if config_obj.config.help or len(config_obj.get().values()) == 0:
            <i>${ config_obj.config.help or _('No help available.') }</i>
            % endif
            ${ recurseList(config_obj.get().values(), depth + 1) }
          % else:
            <code>
            % if 'password' in config_obj.config.key:
              ${ "*" * 10 }
            % else:
              ${ str(config_obj.get_raw()).decode('utf-8', 'replace') }
            % endif
              <%
                config_str = None
                try:
                  config_str = str(config_obj.get_raw()).decode('utf-8', 'replace')
                except:
                  LOG.exception("Potential misconfiguration. Error value of key '%s' in configuration." % config_obj.grab_key)
              %>
              %if config_str == '':
              &nbsp;
              %endif
            </code><br/>
              %if config_obj.config.help:
                <i>${ config_obj.config.help or _('No help available.') }</i>
              %endif
            <span class="muted">${ _('Default:') } <i>${ str(config_obj.config.default).decode('utf-8', 'replace') }</i></span>
          % endif
          </td>
        </tr>
    </%def>

</div>

%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif
