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
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="dir" file="listdir_components.mako" />
<%namespace name="fb_components" file="fb_components.mako" />

${commonheader(_('File Browser'), 'filebrowser', user)}

<div class="container-fluid">
    <h1>${_('File Browser')}</h1>
    <%actionbar:render>
        <%def name="search()">
            <input type="text" class="input-xlarge search-query" placeholder="${_('Search for file name')}" data-bind="value: searchQuery">
        </%def>
        <%def name="actions()">
            <button class="btn fileToolbarBtn" title="${_('Rename')}" data-bind="click: renameFile, enable: selectedFiles().length == 1"><i class="icon-font"></i> ${_('Rename')}</button>
            <button class="btn fileToolbarBtn" title="${_('Move')}" data-bind="click: move, enable: selectedFiles().length == 1"><i class="icon-random"></i> ${_('Move')}</button>
            %if is_fs_superuser:
                <button class="btn fileToolbarBtn" title="${_('Change Owner / Group')}" data-bind="click: changeOwner, enable: selectedFiles().length == 1"><i class="icon-user"></i> ${_('Change Owner / Group')}</button>
            %endif
            <button class="btn fileToolbarBtn" title="${_('Change Permissions')}" data-bind="click: changePermissions, enable: selectedFiles().length == 1"><i class="icon-list-alt"></i> ${_('Change Permissions')}</button>
            <button class="btn fileToolbarBtn" title="${_('Delete')}" data-bind="click: deleteSelected, enable: selectedFiles().length == 1"><i class="icon-trash"></i> ${_('Delete')}</button>
        </%def>
        <%def name="creation()">
            <div id="upload-dropdown" class="btn-group" style="display: inline-block;">
                <a href="#" class="btn upload-link dropdown-toggle" title="${_('Upload')}" data-toggle="dropdown"><i class="icon-upload"></i> ${_('Upload')}</a>
                <ul class="dropdown-menu">
                  <li><a href="#" tabindex="-1" class="upload-link" title="${_('Upload files')}" data-bind="click: uploadFile">${_('Upload files')}</a></li>
                  <li class="divider"></li>
                  <li><a href="#" tabindex="-1" class="upload-link" title="${_('Upload archive')}" data-bind="click: uploadArchive">${_('Upload archive')}</a></li>
                </ul>
            </div>
            <a href="#" class="btn create-directory-link" title="${_('New directory')}"><i class="icon-folder-close"></i> ${_('New directory')}</a>
        </%def>
    </%actionbar:render>
    % if breadcrumbs:
        ${fb_components.breadcrumbs(path, breadcrumbs, True)}
    %endif
    <div class="scrollable">
        ${dir.list_table_browser(files, path_enc, current_request_path, cwd_set)}
    </div>
</div>

${commonfooter(messages)}
