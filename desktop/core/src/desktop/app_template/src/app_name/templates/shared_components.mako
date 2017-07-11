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
${'<%!'}
from django.utils.translation import ugettext as _
${'%>'}

${'<%!'}
def is_selected(section, matcher):
  if section == matcher:
    return "active"
  else:
    return ""
${'%>'}

${'<%'}def name="menubar(section='')">
  <div class="navbar hue-title-bar nokids">
    <div class="navbar-inner">
      <div class="container-fluid">
        <div class="nav-collapse">
          <ul class="nav">
            <li class="app-header">
              <a href="/${app_name}">
                <img src="${"${"} static('${app_name}/art/icon_${app_name}_48.png') }" class="app-icon"  alt="${"${"} _('App icon') }"/>
                ${" ".join(word.capitalize() for word in app_name.split("_"))}
              </a>
             </li>
             <li class="${'$'}{is_selected(section, 'mytab')}"><a href="#">Tab 1</a></li>
             <li class="${'$'}{is_selected(section, 'mytab2')}"><a href="#">Tab 2</a></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
${'</%'}def>
