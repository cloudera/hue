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
from desktop.lib.conf import BoundContainer, is_anonymous
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="about_layout.mako" />

${ commonheader(_('Configuration'), "about", user) | n,unicode }
${ layout.menubar(section='dump_config') }

<style type="text/css">
  #installedApps {
    margin: 0;
    padding: 0;
    list-style-type: none;
  }

  #installedApps li {
    display: inline;
  }

  .widget-content {
    padding: 10px;
  }
</style>

    <div class="container-fluid">
      <div class="row-fluid">
        <div class="well" style="border-top-width:1px">
        ${_('Configuration files located in')} <code style="color: #338BB8">${conf_dir}</code>
        </div>

        <div class="card card-home">
            <h2 class="card-heading simple">${_('Installed Applications')}</h2>
          <div class="card-body">
            <p>
            <ul id="installedAppsz" class="nav nav-pills">
            % for app in apps:
                % if app.menu_index != 999:
                  <li><a href="/${app.display_name if app.menu_index != 999 else ''}">${app.name}</a></li>
                % else:
                  <li><a>${app.name}</a></li>
                % endif
            % endfor
            </ul>
           </p>
          </div>
        </div>

        <div class="card card-home">
          <h2 class="card-heading simple">${_('Configuration Sections and Variables')}</h2>
          <div class="card-body">
            <p>
              <ul class="nav nav-tabs">
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

              ${showTopLevel(top_level)}

              <br/>
              <br/>
              <br/>
            </p>
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
          <table class="table table-striped recurse">
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
                <p class="dump_config_help"><i>${ config_obj.config.help or _('No help available.') }</i></p>
                ${ recurseList(config_obj.get().values(), depth + 1) }
              % else:
                <p>
                  % if 'password' in config_obj.config.key:
                    ${ "*" * 10 }
                  % else:
                    ${ str(config_obj.get_raw()).decode('utf-8', 'replace') }
                  % endif
                  </p>
                <p class="dump_config_help"><i>${ config_obj.config.help or _('No help available.') }</i></p>
                <p class="dump_config_default">${ _('Default:') } <i>${ str(config_obj.config.default).decode('utf-8', 'replace') }</i></p>
              % endif
              </td>
            </tr>
        </%def>

    </div>

${ commonfooter(messages) | n,unicode }
