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

<%def name="menubar()">
  <div class="page-header">
    <h1 class="currentApp">
      <a href="/${app_name}"><img src="${ static('desktop/art/icon_hue_48.png') }" class="app-icon" />
        ${ _('About Hue') }</a>
    </h1>

    % if user.is_superuser:
      <ul class="nav nav-tabs">
        <li class="active"><a href="${url("about:admin_wizard")}">${_('Quick Start')}</a></li>
        <li><a href="${url("desktop.views.dump_config")}">${_('Configuration')}</a></li>
        <li><a href="${url("desktop.views.log_view")}">${_('Server Logs')}</a></li>
      </ul>
    % endif
  </div>
</%def>
