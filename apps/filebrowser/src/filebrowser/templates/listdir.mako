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

${ commonheader(_('File Browser'), 'filebrowser', user) | n,unicode }

<div class="container-fluid">
    <h1>${_('File Browser')}</h1>
    <div class="actionbar">
    <%actionbar:render>
        <%def name="search()">
            <input type="text" class="input-large search-query" placeholder="${_('Search for file name')}" data-bind="value: searchQuery">
        </%def>

        <%def name="actions()">
            <button class="btn fileToolbarBtn" title="${_('Rename')}" data-bind="visible: !inTrash(), click: renameFile, enable: selectedFiles().length == 1"><i class="icon-font"></i> ${_('Rename')}</button>
            <button class="btn fileToolbarBtn" title="${_('Move')}" data-bind="click: move, enable: selectedFiles().length > 0"><i class="icon-random"></i> ${_('Move')}</button>
            <button class="btn fileToolbarBtn" title="${_('Copy')}" data-bind="click: copy, enable: selectedFiles().length > 0"><i class="icon-retweet"></i> ${_('Copy')}</button>
            %if is_fs_superuser:
                <button class="btn fileToolbarBtn" title="${_('Change Owner / Group')}" data-bind="visible: !inTrash(), click: changeOwner, enable: selectedFiles().length > 0"><i class="icon-user"></i> ${_('Change Owner / Group')}</button>
            %endif
            <button class="btn fileToolbarBtn" title="${_('Change Permissions')}" data-bind="visible: !inTrash(), click: changePermissions, enable: selectedFiles().length > 0"><i class="icon-list-alt"></i> ${_('Change Permissions')}</button>
            <button class="btn fileToolbarBtn" title="${_('Download')}" data-bind="visible: !inTrash(), click: downloadFile, enable: selectedFiles().length == 1 && selectedFile().type == 'file'"><i class="icon-download-alt"></i> ${_('Download')}</button>
            &nbsp;&nbsp;
            <button class="btn fileToolbarBtn" title="${_('Empty trash')}" data-bind="visible: inTrash(), click: purgeTrash"><i class="icon-fire"></i> ${_('Empty')}</button>
            <button class="btn fileToolbarBtn" title="${_('Restore from trash')}" data-bind="visible: inRestorableTrash(), click: restoreTrashSelected, enable: selectedFiles().length > 0"><i class="icon-cloud-upload"></i> ${_('Restore')}</button>

            <div id="delete-dropdown" class="btn-group" style="display: inline">
              <button href="#" class="btn delete-link dropdown-toggle" title="${_('Delete')}" data-toggle="dropdown" data-bind="visible: !inTrash(), enable: selectedFiles().length > 0">
                <i class="icon-remove"></i> ${_('Delete')}
                <span class="caret"></span>
              </button>
              <ul class="dropdown-menu" style="top: auto">
                <li data-bind="visible: trashEnabled"><a href="#" class="delete-link" title="${_('Move to Trash')}" data-bind="enable: selectedFiles().length > 0, click: trashSelected"><i class="icon-trash"></i> ${_('Move to Trash')}</a></li>
                <li><a href="#" class="delete-link" title="${_('Delete forever')}" data-bind="enable: selectedFiles().length > 0, click: deleteSelected"><i class="icon-bolt"></i> ${_('Delete forever')}</a></li>
              </ul>
            </div>
        </%def>

        <%def name="creation()">
            <div id="upload-dropdown" class="btn-group pull-right" style="display: inline-block; margin-top:0">
              <a href="#" class="btn upload-link dropdown-toggle" title="${_('Upload')}" data-toggle="dropdown" data-bind="visible: !inTrash()">
                <i class="icon-upload"></i> ${_('Upload')}
                <span class="caret"></span>
              </a>
              <ul class="dropdown-menu">
                <li><a href="#" class="upload-link" title="${_('Files')}" data-bind="click: uploadFile"><i class="icon-file-alt"></i> ${_('Files')}</a></li>
                <li><a href="#" class="upload-link" title="${_('Archive')}" data-bind="click: uploadArchive"><i class="icon-gift"></i> ${_('Zip file')}</a></li>
              </ul>
            </div>
            <div class="btn-group" style="display: inline">
              <a href="#" data-toggle="dropdown" class="btn dropdown-toggle" data-bind="visible: !inTrash()">
                <i class="icon-plus-sign"></i> ${_('New')}
                <span class="caret"></span>
              </a>
              <ul class="dropdown-menu" style="top: auto">
                <li><a href="#" class="create-file-link" title="${_('File')}"><i class="icon-file-alt"></i> ${_('File')}</a></li>
                <li><a href="#" class="create-directory-link" title="${_('Directory')}"><i class="icon-folder-close"></i> ${_('Directory')}</a></li>
              </ul>
            </div>
        </%def>
    </%actionbar:render>
    </div>
    <div class="actionbarGhost hide"></div>

    <div class="scrollable">
      <div class="alert alert-warn" data-bind="visible: inTrash">
        ${ _("You are in Hadoop trash. Your files will be under a checkpoint, or timestamp named, directory.") }
      </div>

      % if breadcrumbs:
        ${fb_components.breadcrumbs(path, breadcrumbs, True)}
      %endif

        ${dir.list_table_browser(files, path_enc, current_request_path, cwd_set)}
    </div>
</div>

${ commonfooter(messages) | n,unicode }
