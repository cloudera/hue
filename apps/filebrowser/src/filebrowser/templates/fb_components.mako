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
import datetime
import urllib
from desktop.lib.paths import SAFE_CHARACTERS_URI_COMPONENTS

from django.template.defaultfilters import urlencode, stringformat, date, filesizeformat, time
from django.utils.translation import ugettext as _

from aws import get_client
%>

<%def name="breadcrumbs(path, breadcrumbs, from_listdir=False)">
    % if from_listdir:
      <ul class="nav nav-pills hue-breadcrumbs-bar">
        %if path.lower().find('s3a://') == 0:
          <li style="padding-top: 10px">
            <span class="breadcrumb-link homeLink" title="${ _('S3 region %s') % get_client()._region }">
              <i class="fa fa-fw fa-cubes"></i> ${ get_client()._region }
            </span>
          </li>
        %elif path.lower().find('adl:/') == 0:
          <li style="padding-top: 12px">
            <span class="breadcrumb-link homeLink">
              <svg class="hi"><use xlink:href='#hi-adls'></use></svg>
            </span>
          </li>
        %else:
          <li><a class="pointer breadcrumb-link homeLink" data-bind="click: $root.openHome, attr:{'href': window.HUE_BASE_URL + '/filebrowser/view=${ urllib.quote(path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS) }?default_to_home'}">
            <i class="fa fa-home"></i> ${_('Home')}</a>
          </li>
        %endif
        <li>
          <ul id="editBreadcrumb" class="hue-breadcrumbs editable-breadcrumbs" data-bind="foreach: breadcrumbs" style="padding-right:40px; padding-top: 12px" title="${_('Edit path')}">
            <li data-bind="visible: label.slice(-1) == '/'">
              <a data-bind="click: show, attr: {'href': '${url('filebrowser.views.view', path=urlencode(''))}' + url}"><span class="divider" data-bind="text: label"></span></a>
            </li>
            <li data-bind="visible: label.slice(-1) != '/'">
              <a data-bind="text: label, click: show, attr: {'href': '${url('filebrowser.views.view', path=urlencode(''))}' + url}"></a><span class="divider">/</span>
            </li>
          </ul>
          <input id="hueBreadcrumbText" type="text" style="display:none" data-bind="value: currentPath" autocomplete="off" class="input-xxlarge" />
        </li>
        % if is_trash_enabled:
        <li class="pull-right">
          <a class="pointer breadcrumb-link trashLink" data-bind="click: $root.openTrash, attr:{'href': window.HUE_BASE_URL + '/filebrowser/view=${ urllib.quote(path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS) }?default_to_trash'}" title="${_('View trash')}">
            <i class="fa fa-trash-o"></i> ${_('Trash')}
          </a>
        </li>
        % endif
      </ul>
    % else:
      <ul class="nav nav-pills hue-breadcrumbs-bar">
        <li><a data-bind="hueLink: window.HUE_BASE_URL + '/filebrowser/view=${ urllib.quote(path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS) }?default_to_home'" class="breadcrumb-link homeLink"><i class="fa fa-home"></i> ${_('Home')}</a></li>
        <li>
          <ul class="hue-breadcrumbs" style="padding-right:40px; padding-top: 12px">
          % for breadcrumb_item in breadcrumbs:
            <% label, f_url = breadcrumb_item['label'], breadcrumb_item['url'] %>
            %if label[-1] == '/':
            <li><a data-bind="hueLink: '${'/filebrowser/view=' + f_url}'"><span class="divider">${label}</span></a></li>
            %else:
            <li><a data-bind="hueLink: '${'/filebrowser/view=' + f_url}'">${label}</a><span class="divider">/</span></li>
            %endif
          % endfor
          </ul>
        </li>
      </ul>
    % endif
</%def>


<%def name="menubar()">
  <div class="navbar hue-title-bar nokids">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="app-header">
                <a href="/${app_name}/">
                  <img src="${ static('filebrowser/art/icon_filebrowser_48.png') }" class="app-icon" alt="${ _('File browser icon') }" />
                  ${ _('File Browser') }
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
  </div>
</%def>

