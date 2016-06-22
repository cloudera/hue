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
from django.template.defaultfilters import urlencode, stringformat, date, filesizeformat, time
from django.utils.translation import ugettext as _
%>

<%def name="breadcrumbs(path, breadcrumbs, from_listdir=False)">
    % if from_listdir:
      <ul class="nav nav-pills hueBreadcrumbBar">
        <li><a href="${url('filebrowser.views.view', path=urlencode(path))}?default_to_home" class="homeLink"><i class="fa fa-home"></i> ${_('Home')}</a></li>
        <li>
            <ul id="editBreadcrumb" class="hueBreadcrumb editable-breadcrumbs" data-bind="foreach: breadcrumbs" style="padding-right:40px; padding-top: 12px" title="${_('Edit path')}">
                <li data-bind="visible: label.slice(-1) == '/'"><a data-bind="click: show, attr:{'href': '${url('filebrowser.views.view', path=urlencode(''))}' + url}"><span class="divider" data-bind="text: label"></span></a></li>
                <li data-bind="visible: label.slice(-1) != '/'"><a data-bind="text: label, click: show, attr:{'href': '${url('filebrowser.views.view', path=urlencode(''))}' + url}"></a><span class="divider">/</span></li>
            </ul>
            <input id="hueBreadcrumbText" type="text" style="display:none" data-bind="value: currentPath" autocomplete="off" />
        </li>
        <li class="pull-right">
          <a href="${url('filebrowser.views.view', path=urlencode(path))}?default_to_trash" class="trashLink" title="${_('View trash')}">
            <i class="fa fa-trash-o"></i> ${_('Trash')}
          </a>
        </li>
        <li class="pull-right">
          <div class="dropdown history">
            <a href="javascript:void(0)" class="historyLink dropdown-toggle" title="${_('View History')}" data-toggle="dropdown" id="historyDropdown">
              <i class="fa fa-caret-down"></i> ${_('History')}
            </a>
          </div>
        </li>
      </ul>
    % else:
      <ul class="nav nav-pills hueBreadcrumbBar">
        <li><a href="${url('filebrowser.views.view', path=urlencode(path))}?default_to_home" class="homeLink"><i class="fa fa-home"></i> ${_('Home')}</a></li>
        <li>
            <ul class="hueBreadcrumb" style="padding-right:40px; padding-top: 12px">
                    % for breadcrumb_item in breadcrumbs:
                    <% label, f_url = breadcrumb_item['label'], breadcrumb_item['url'] %>
                    %if label[-1] == '/':
                            <li>
                              <a href="${url('filebrowser.views.view', path=f_url)}">
                                <span class="divider">${label}</span>
                              </a>
                            </li>
                    %else:
                            <li>
                              <a href="${url('filebrowser.views.view', path=f_url)}">${label}</a>
                              <span class="divider">/</span></li>
                    %endif
                    % endfor
            </ul>
        </li>
      </ul>
    % endif
</%def>


<%def name="menubar()">
  <div class="navbar navbar-inverse navbar-fixed-top nokids">
      <div class="navbar-inner">
        <div class="container-fluid">
          <div class="nav-collapse">
            <ul class="nav">
              <li class="currentApp">
                <a href="/${app_name}">
                  <img src="${ static('filebrowser/art/icon_filebrowser_48.png') }" class="app-icon" />
                  ${ _('File Browser') }
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
  </div>
</%def>

<%def name="file_sidebar(path_enc, dirname_enc, stats, show_download_button, view=None)">
  <div class="sidebar-nav" style="padding-top: 0">
    <ul class="nav nav-list">
      <li class="nav-header">${_('Actions')}</li>
      % if view:
        <%
          base_url = url('filebrowser.views.view', path=path_enc)
        %>
        % if view['mode'] == "binary":
          <li><a href="${base_url}?mode=text&compression=${view['compression']}"><i class="fa fa-font"></i> ${_('View as text')}</a></li>
        % endif

        % if view['mode'] == "text":
          <li><a href="${base_url}?mode=binary&compression=${view['compression']}"><i class="fa fa-barcode"></i> ${_('View as binary')}</a></li>
        % endif

        % if view['compression'] != "gzip" and path.endswith('.gz'):
          <li><a href="${base_url}?offset=0&length=2000&mode=${view['mode']}&compression=gzip"><i class="fa fa-youtube-play"></i> ${_('Preview as Gzip')}</a></li>
        % endif

        % if view['compression'] != "avro" and view['compression'] != "snappy_avro" and path.endswith('.avro'):
          <li><a href="${base_url}?offset=0&length=2000&mode=${view['mode']}&compression=avro"><i class="fa fa-youtube-play"></i> ${_('Preview as Avro')}</a></li>
        % endif

        % if view['compression'] and view['compression'] != "none":
          <li><a href="${base_url}?offset=0&length=2000&mode=${view['mode']}&compression=none"><i class="fa fa-times-circle"></i> ${_('Stop preview')}</a></li>
        % endif

        % if editable and view['compression'] == "none":
          <li><a href="${url('filebrowser.views.edit', path=path_enc)}"><i class="fa fa-pencil"></i> ${_('Edit file')}</a></li>
        % endif
      % else:
        <li><a href="${url('filebrowser.views.view', path=path_enc)}"><i class="fa fa-eye"></i> ${_('View file')}</a></li>
      % endif

      % if show_download_button:
       <li><a href="${url('filebrowser.views.download', path=path_enc)}"><i class="fa fa-download"></i> ${_('Download')}</a></li>
      % endif
       <li><a href="${url('filebrowser.views.view', path=dirname_enc)}"><i class="fa fa-file-text"></i> ${_('View file location')}</a></li>
       <li><a id="refreshBtn" href="#"><i class="fa fa-refresh"></i> ${_('Refresh')}</a></li>

       % if stats is not None: # Case new file
       <li class="nav-header">${_('Info')}</li>
       <li class="white">
        <dl>
          <dt>${_('Last modified')}</dt>
          <dd>${date(datetime.datetime.fromtimestamp(stats['mtime']))} ${time(datetime.datetime.fromtimestamp(stats['mtime']))}</dd>
          <dt>${_('User')}</dt>
          <dd>${stats['user']}</dd>
          <dt>${_('Group')}</dt>
          <dd>${stats['group']}</dd>
          <dt>${_('Size')}</dt>
          <dd>${stats['size']|filesizeformat}</dd>
          <dt>${_('Mode')}</dt>
          <dd>${stringformat(stats['mode'], "o")}</dd>
        </dl>
       </li>
       % endif
    </ul>
  </div>
</%def>
