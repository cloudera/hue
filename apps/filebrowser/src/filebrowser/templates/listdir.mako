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
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="dir" file="listdir_components.mako" />
<%namespace name="fb_components" file="fb_components.mako" />

${ commonheader(None, 'filebrowser', user) | n,unicode }
${ fb_components.menubar() }

<style type="text/css">
  .tooltip.left {
    margin-left: -10px;
  }
</style>

<div class="container-fluid">

  <div class="card card-small">
    <div class="actionbar">
    <%actionbar:render>
      <%def name="search()">
        <input type="text" class="input-large search-query" placeholder="${_('Search for file name')}" data-bind="value: searchQuery">
      </%def>

      <%def name="actions()">
        <div class="btn-toolbar" style="display: inline; vertical-align: middle">
          <div id="ch-dropdown" class="btn-group" style="vertical-align: middle">
            <button href="#" class="btn dropdown-toggle" title="${_('Actions')}" data-toggle="dropdown"
            data-bind="visible:
             !inTrash(), enable: selectedFiles().length > 0">
              <i class="fa fa-cog"></i> ${_('Actions')}
              <span class="caret" style="line-height: 15px"></span>
            </button>
            <ul class="dropdown-menu" style="top: auto">
              <li><a href="#" title="${_('Rename')}" data-bind="visible: !inTrash() && selectedFiles().length == 1, click: renameFile,
              enable: selectedFiles().length == 1 && isCurrentDirSelected().length == 0"><i class="fa fa-font"></i>
              ${_('Rename')}</a></li>
              <li><a href="#"title="${_('Move')}" data-bind="click: move, enable: selectedFiles().length > 0 &&
              isCurrentDirSelected().length == 0"><i class="fa fa-random"></i> ${_('Move')}</a></li>
              <li><a href="#" title="${_('Copy')}" data-bind="click: copy, enable: selectedFiles().length > 0 &&
              isCurrentDirSelected().length == 0"><i class="fa fa-files-o"></i> ${_('Copy')}</a></li>
              <li>
                <a href="#" title="${_('Download')}" data-bind="visible: !inTrash() && selectedFiles().length == 1 && selectedFile().type == 'file', click: downloadFile">
                  <i class="fa fa-arrow-circle-o-down"></i> ${_('Download')}
                </a>
              </li>
              <li class="divider"></li>
              % if is_fs_superuser:
              <li data-bind="css: {'disabled': isCurrentDirSentryManaged() || selectedSentryFiles().length > 0 }">
                <a href="#" data-bind="visible: ! inTrash(), click: changeOwner, enable: selectedFiles().length > 0">
                  <i class="fa fa-user"></i> ${_('Change owner / group')}
                </a>
              </li>
              % endif
              <li data-bind="css: {'disabled': isCurrentDirSentryManaged() || selectedSentryFiles().length > 0 }">
                <a href="#" data-bind="visible: ! inTrash(), click: changePermissions, enable: selectedFiles().length > 0">
                  <i class="fa fa-list-alt"></i> ${_('Change permissions')}
                </a>
              </li>
            </ul>
          </div>
          <button class="btn fileToolbarBtn" title="${_('Restore from trash')}" data-bind="visible: inRestorableTrash(), click: restoreTrashSelected, enable: selectedFiles().length > 0 && isCurrentDirSelected().length == 0"><i class="fa fa-cloud-upload"></i> ${_('Restore')}</button>
          <!-- ko ifnot: inTrash -->
          <div id="delete-dropdown" class="btn-group" style="vertical-align: middle">
            <button id="trash-btn" class="btn toolbarBtn" data-bind="enable: selectedFiles().length > 0 && isCurrentDirSelected().length == 0, click: trashSelected"><i class="fa fa-times"></i> ${_('Move to trash')}</button>
            <button id="trash-btn-caret" class="btn toolbarBtn dropdown-toggle" data-toggle="dropdown" data-bind="enable: selectedFiles().length > 0 && isCurrentDirSelected().length == 0">
              <span class="caret"></span>
            </button>
            <ul class="dropdown-menu">
              <li><a href="#" class="delete-link" title="${_('Delete forever')}" data-bind="enable: selectedFiles().length > 0, click: deleteSelected"><i class="fa fa-bolt"></i> ${_('Delete forever')}</a></li>
            </ul>
          </div>
          <!-- /ko -->
          <button class="btn fileToolbarBtn" title="${_('Submit')}"
            data-bind="visible: selectedFiles().length == 1 && $.inArray(selectedFile().name, ['workflow.xml', 'coordinator.xml', 'bundle.xml']) > -1, click: submitSelected">
            <i class="fa fa-play"></i> ${_('Submit')}
          </button>
        </div>
      </%def>

      <%def name="creation()">
        <button class="btn fileToolbarBtn" title="${_('Empty trash')}" data-bind="visible: inTrash(), click: purgeTrash"><i class="fa fa-fire"></i> ${_('Empty trash')}</button>
        <div class="btn-toolbar" style="display: inline; vertical-align: middle">
          <div id="upload-dropdown" class="btn-group" style="vertical-align: middle">
            <a href="#" class="btn upload-link dropdown-toggle" title="${_('Upload')}" data-toggle="dropdown" data-bind="visible: !inTrash()">
              <i class="fa fa-arrow-circle-o-up"></i> ${_('Upload')}
              <span class="caret"></span>
            </a>
            <ul class="dropdown-menu">
              <li><a href="#" class="upload-link" title="${_('Files')}" data-bind="click: uploadFile"><i class="fa fa-file-o"></i> ${_('Files')}</a></li>
              <li><a href="#" class="upload-link" title="${_('Archive')}" data-bind="click: uploadArchive"><i class="fa fa-gift"></i> ${_('Zip/Tgz file')}</a></li>
            </ul>
          </div>
          <div class="btn-group" style="vertical-align: middle">
            <a href="#" data-toggle="dropdown" class="btn dropdown-toggle" data-bind="visible: !inTrash()">
              <i class="fa fa-plus-circle"></i> ${_('New')}
              <span class="caret"></span>
            </a>
            <ul class="dropdown-menu pull-right" style="top: auto">
              <li><a href="#" class="create-file-link" title="${_('File')}"><i class="fa fa-file-o"></i> ${_('File')}</a></li>
              <li><a href="#" class="create-directory-link" title="${_('Directory')}"><i class="fa fa-folder"></i> ${_('Directory')}</a></li>
            </ul>
          </div>
        </div>
      </%def>
    </%actionbar:render>
    </div>
    <div class="actionbarGhost hide"></div>

    <div class="scrollable">
      <div class="alert alert-warn" data-bind="visible: inTrash">
        ${ _("This is Hadoop trash. Files will be under a checkpoint, or timestamp named, directory.") }
      </div>
      <div class="alert alert-warn" data-bind="visible: isCurrentDirSentryManaged">
        ${ _('The permissions for this folder are managed by the Sentry Namenode plugin.') }
      </div>
      <div class="alert alert-warn" data-bind="visible: ! isCurrentDirSentryManaged() && selectedSentryFiles().length > 0">
        ${ _('The permissions of some of the selected files are managed by the Sentry Namenode plugin.') }
      </div>

      % if breadcrumbs:
        ${fb_components.breadcrumbs(path, breadcrumbs, True)}
      %endif

      <div style="padding-left: 6px">
        ${dir.list_table_browser(files, path_enc, current_request_path, cwd_set)}
      </div>
    </div>
  </div>
</div>

<div class="hoverMsg hide">
  <p class="hoverText"></p>
</div>


${ commonfooter(messages) | n,unicode }
