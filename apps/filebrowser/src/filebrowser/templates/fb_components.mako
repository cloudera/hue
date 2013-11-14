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
from django.template.defaultfilters import urlencode
from django.utils.translation import ugettext as _
%>

<%def name="breadcrumbs(path, breadcrumbs, from_listdir=False)">
    <ul class="nav nav-pills hueBreadcrumbBar">
        % if from_listdir:
        <li><a href="${url('filebrowser.views.view', path=urlencode(path))}?default_to_home" style="line-height:18px"><i class="fa fa-home"></i> ${_('Home')}</a></li>
        <li>
            <span style="float:right; margin-top:10px;"><i id="editBreadcrumb" class="fa fa-pencil hand" rel="tooltip" title="${_('Edit path')}"></i></span>
            <ul class="hueBreadcrumb" data-bind="foreach: breadcrumbs" style="padding-right:40px; padding-top: 12px">
                <li data-bind="visible: label == '/'"><a href="#" data-bind="click: show"><span class="divider" data-bind="text: label"></span></a></li>
                <li data-bind="visible: label != '/'"><a href="#" data-bind="text: label, click: show"></a><span class="divider">/</span></li>
            </ul>
            <input id="hueBreadcrumbText" type="text" class="input-xxlarge" style="margin-top:4px;margin-right:4px;display:none" data-bind="value: currentPath" />
        </li>
        <li class="pull-right">
          <a href="${url('filebrowser.views.view', path=urlencode(path))}?default_to_trash" style="line-height:18px" title="${_('View trash')}">
            <i class="fa fa-trash-o"></i> ${_('View trash')}
          </a>
        </li>
        % else:
        <li><a href="${url('filebrowser.views.view', path=urlencode(path))}?default_to_home"><i class="fa fa-home"></i> ${_('Home')}</a></li>
        <li>
            <ul class="hueBreadcrumb" style="padding-right:40px; padding-top: 12px">
                    % for breadcrumb_item in breadcrumbs:
                    <% label = breadcrumb_item['label'] %>
                    %if label == '/':
                            <li><a href="/filebrowser/view${breadcrumb_item['url']}"><span
                                    class="divider">${label}</span></a></li>
                    %else:
                            <li><a href="/filebrowser/view${breadcrumb_item['url']}">${label}</a><span class="divider">/</span></li>
                    %endif
                    % endfor
            </ul>
        </li>
        % endif
    </ul>
</%def>


<%def name="menubar()">
  <div class="navbar navbar-inverse navbar-fixed-top nokids">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="currentApp">
                <a href="/${app_name}">
                  <img src="/filebrowser/static/art/icon_filebrowser_24.png" />
                  ${ _('File Browser') }
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
  </div>
</%def>
