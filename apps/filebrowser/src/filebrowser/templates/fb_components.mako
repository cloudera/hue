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
    % if from_listdir:
        <div class="subnavContainer">
            <div class="subnav">
                <p class="pull-right">
                    <input type="text" class="input-xlarge search-query" placeholder="${_('Search for file name')}" data-bind="value: searchQuery">
                </p>
                <p style="padding: 4px">
                    <button class="btn fileToolbarBtn" title="${_('Rename')}" data-bind="click: renameFile, enable: selectedFiles().length == 1"><i class="icon-font"></i> ${_('Rename')}</button>
                    <button class="btn fileToolbarBtn" title="${_('Move')}" data-bind="click: move, enable: selectedFiles().length == 1"><i class="icon-random"></i> ${_('Move')}</button>
                    %if is_fs_superuser:
                    <button class="btn fileToolbarBtn" title="${_('Change Owner / Group')}" data-bind="click: changeOwner, enable: selectedFiles().length == 1"><i class="icon-user"></i> ${_('Change Owner / Group')}</button>
                    %endif
                    <button class="btn fileToolbarBtn" title="${_('Change Permissions')}" data-bind="click: changePermissions, enable: selectedFiles().length == 1"><i class="icon-list-alt"></i> ${_('Change Permissions')}</button>
                    <button class="btn fileToolbarBtn" title="${_('Delete')}" data-bind="click: deleteSelected, enable: selectedFiles().length == 1"><i class="icon-trash"></i> ${_('Delete')}</button>
                    &nbsp;&nbsp;&nbsp;&nbsp;
                    <a href="#" class="btn upload-link" title="${_('Upload files')}"><i class="icon-upload"></i> ${_('Upload files')}</a>
                    <a href="#" class="btn create-directory-link" title="${_('New directory')}"><i class="icon-folder-close"></i> ${_('New directory')}</a>
                    &nbsp;&nbsp;&nbsp;&nbsp;
                </p>
            </div>
        </div>
        <br/>
        <ul class="nav nav-pills hueBreadcrumbBar">
            <li><a href="${url('filebrowser.views.view', path=urlencode(path))}?default_to_home"><i class="icon-home"></i> ${_('Home')}</a></li>
            <li>
                <span style="float:right; margin-top:10px;"><i id="editBreadcrumb" class="icon-pencil hand" rel="tooltip" title="${_('Edit path')}"></i></span>
                <ul class="hueBreadcrumb" data-bind="foreach: breadcrumbs" style="padding-right:40px">
                    <li data-bind="visible: label == '/'"><a href="#" data-bind="click: show"><span class="divider" data-bind="text: label"></span></a></li>
                    <li data-bind="visible: label != '/'"><a href="#" data-bind="text: label, click: show"></a><span class="divider">/</span></li>
                </ul>
                <input id="hueBreadcrumbText" type="text" class="input-xlarge" style="margin-top:4px;margin-right:4px;display:none" data-bind="value: currentPath" />
            </li>
        </ul>
    % else:
        <ul class="nav nav-pills hueBreadcrumbBar">
            <li><a href="${url('filebrowser.views.view', path=urlencode(path))}?default_to_home"><i class="icon-home"></i> ${_('Home')}</a></li>
            <li>
                <ul class="hueBreadcrumb">
                        % for breadcrumb_item in breadcrumbs:
                        <% label = breadcrumb_item['label'] %>
                        %if label == '/':
                                <li><a href="/filebrowser/view${breadcrumb_item['url']}"><span
                                        class="divider">${label | h}</span></a></li>
                        %else:
                                <li><a href="/filebrowser/view${breadcrumb_item['url']}">${label | h}</a><span class="divider">/</span></li>
                        %endif
                        % endfor
                </ul>
            </li>
        </ul>
    % endif

    <style type="text/css">
        .subnavContainer {
            height: 36px;
        }
        .hueBreadcrumbBar {
            padding: 8px 15px;
            margin: 0 0 20px;
            list-style: none;
            border: 1px solid #E5E5E5;
            -webkit-border-radius: 4px;
            -moz-border-radius: 4px;
            border-radius: 4px;
        }
        .hueBreadcrumb {
            margin: 0!important;
        }
    </style>
</%def>
