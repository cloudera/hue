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
import sys

from django.template.defaultfilters import urlencode
from desktop.views import commonheader, commonfooter

from filebrowser.conf import ENABLE_EXTRACT_UPLOADED_ARCHIVE

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="dir" file="listdir_components.mako" />
<%namespace name="fb_components" file="fb_components.mako" />

%if not is_embeddable:
${ commonheader(None, 'filebrowser', user, request) | n,unicode }
%endif
${ fb_components.menubar() }

<style type="text/css">
  .tooltip.left {
    margin-left: -10px;
  }

  %if is_embeddable:
    .filebrowser .pagination {
      position: inherit;
    }
  %endif
</style>

<div id="${ path.startswith('s3a://') and 'filebrowser_s3Components' or path.startswith('gs://') and 'filebrowser_gsComponents' or path.startswith('abfs://') and 'filebrowser_abfsComponents'  or path.startswith('ofs://') and 'filebrowser_ofsComponents'or 'filebrowserComponents' }" class="container-fluid filebrowser" style="min-height: calc(100vh - 130px);">
  <div class="card card-small">
    <div class="actionbar">
    <%actionbar:render>
      <%def name="search()">
        <input type="text" class="input-large search-query" placeholder="${_('Search for file name')}" data-bind="clearable: searchQuery, valueUpdateDelay: 500">
      </%def>

      <%def name="actions()">
        <div class="btn-toolbar" style="display: inline; vertical-align: middle">
          <div id="ch-dropdown" class="btn-group" style="vertical-align: middle">
            <button class="btn dropdown-toggle" title="${_('Actions')}" data-toggle="dropdown"
            data-bind="visible: !inTrash(), enable: selectedFiles().length > 0 && ((!isS3() && !isGS() && !isABFS() && !isOFS()) || (isS3() && !isS3Root()) || (isGS() && !isGSRoot()) || (isABFS() && !isABFSRoot()) || (isOFS() && !(isOFSRoot() || isOFSServiceID() || isOFSVol())))">
              <i class="fa fa-cog"></i> ${_('Actions')}
              <span class="caret" style="line-height: 15px"></span>
            </button>
            <ul class="dropdown-menu" style="top: auto">
              <li><a data-hue-analytics="filebrowser:actions-menu/rename-click" href="javascript: void(0)" title="${_('Rename')}" data-bind="visible: !inTrash() && selectedFiles().length == 1 && !isOFSServiceID() && !isOFSVol(), click: renameFile,
              enable: selectedFiles().length == 1 && isCurrentDirSelected().length == 0"><i class="fa fa-fw fa-font"></i>
              ${_('Rename')}</a></li>
              <li><a data-hue-analytics="filebrowser:actions-menu/move-click" href="javascript: void(0)" title="${_('Move')}" data-bind="click: move, enable: selectedFiles().length > 0 &&
              isCurrentDirSelected().length == 0"><i class="fa fa-fw fa-random"></i> ${_('Move')}</a></li>
              <li data-bind="css: {'disabled': $root.selectedFiles().length == 0 || isCurrentDirSelected().length > 0}">
              <a data-hue-analytics="filebrowser:actions-menu/copy-click" href="javascript: void(0)" title="${_('Copy')}" data-bind="click: ($root.selectedFiles().length > 0 && isCurrentDirSelected().length == 0) ? $root.copy: void(0), enable: selectedFiles().length > 0 &&
              isCurrentDirSelected().length == 0"><i class="fa fa-fw fa-files-o"></i> ${_('Copy')}</a></li>
              % if show_download_button:
              <li>
                <a data-hue-analytics="filebrowser:actions-menu/download-click" href="javascript: void(0)" title="${_('Download')}" data-bind="visible: !inTrash() && selectedFiles().length == 1 && selectedFile().type == 'file', click: downloadFile">
                  <i class="fa fa-fw fa-arrow-circle-o-down"></i> ${_('Download')}
                </a>
              </li>
              % endif
              <li class="divider" data-bind="visible: isPermissionEnabled()"></li>
              % if is_fs_superuser:
              <li data-bind="css: {'disabled': isCurrentDirSentryManaged() || selectedSentryFiles().length > 0 }">
                <a href="javascript: void(0)" data-bind="visible: ! inTrash(), click: changeOwner, enable: selectedFiles().length > 0">
                  <i class="fa fa-fw fa-user"></i> ${_('Change owner / group')}
                </a>
              </li>
              % endif
              <li data-bind="css: {'disabled': isCurrentDirSentryManaged() || selectedSentryFiles().length > 0 }, visible: isPermissionEnabled()">
                <a href="javascript: void(0)" data-bind="visible: ! inTrash(), click: changePermissions, enable: selectedFiles().length > 0">
                  <i class="fa fa-fw fa-list-alt"></i> ${_('Change permissions')}
                </a>
              </li>
              <li class="divider" data-bind="visible: isCompressEnabled() || isReplicationEnabled() || isSummaryEnabled()"></li>
              <li data-bind="css: {'disabled': inTrash() || selectedFiles().length > 1 }, visible: isSummaryEnabled()">
                <a data-hue-analytics="filebrowser:actions-menu/show-summary-click" class="pointer" data-bind="click: function(){ selectedFiles().length == 1 ? showSummary(): void(0)}">
                  <i class="fa fa-fw fa-pie-chart"></i> ${_('Summary')}
                </a>
              </li>
              <li>
                <a data-hue-analytics="filebrowser:actions-menu/set-replication-click"href="javascript: void(0)" title="${_('Set Replication')}" data-bind="visible: !inTrash() && isReplicationEnabled() && selectedFiles().length == 1 && selectedFile().type == 'file', click: setReplicationFactor">
                  <i class="fa fa-fw fa-hdd-o"></i> ${_('Set replication')}
                </a>
              </li>
              % if not is_trash_enabled:
              <li>
                <a data-hue-analytics="filebrowser:actions-menu/delete-click" href="javascript: void(0)" title="${_('Delete')}" data-bind="visible: !inTrash() && selectedFiles().length > 0 && isCurrentDirSelected().length == 0, click: deleteSelected">
                  <i class="fa fa-fw fa-bolt"></i> ${_('Delete')}
                </a>
              </li>
              % endif
              % if ENABLE_EXTRACT_UPLOADED_ARCHIVE.get():
                <li><a data-hue-analytics="filebrowser:actions-menu/compress-click" href="javascript: void(0)" title="${_('Compress selection into a single archive')}" data-bind="click: function() { setCompressArchiveDefault(); confirmCompressFiles();}, visible: showCompressButton">
                  <i class="fa fa-fw fa-file-archive-o"></i> ${_('Compress')}</a>
                </li>
                <li><a data-hue-analytics="filebrowser:actions-menu/extract-click" href="javascript: void(0)" title="${_('Extract selected archive')}" data-bind="visible: selectedFiles().length == 1 && isArchive(selectedFile().name) && isCompressEnabled(), click: confirmExtractArchive">
                  <i class="fa fa-fw fa-file-archive-o"></i> ${_('Extract')}</a>
                </li>
              % endif
            </ul>
          </div>
          <button data-hue-analytics="filebrowser:copy-path-btn-click" class="btn fileToolbarBtn" title="${_('Copy Path')}" data-bind="enable: selectedFiles().length == 1 && isCurrentDirSelected().length == 0, click: copyPath"><i class="fa fa-fw fa-files-o"></i> ${_('Copy Path')}</button>
          <button data-hue-analytics="filebrowser:open-in-importer-btn-click" class="btn fileToolbarBtn" title="${_('Open in Importer')}" data-bind="enable: selectedFiles().length == 1 && isCurrentDirSelected().length == 0 && selectedFile().type == 'file', click: openInImporter"><i class="fa fa-fw fa-database"></i> ${_('Open in Importer')}</button>
          <button data-hue-analytics="filebrowser:restore-btn-click" class="btn fileToolbarBtn" title="${_('Restore from trash')}" data-bind="visible: inRestorableTrash(), click: restoreTrashSelected, enable: selectedFiles().length > 0 && isCurrentDirSelected().length == 0"><i class="fa fa-cloud-upload"></i> ${_('Restore')}</button>
          <!-- ko ifnot: inTrash -->
          % if is_trash_enabled:
          <div id="delete-dropdown" class="btn-group" style="vertical-align: middle">
            <button id="trash-btn" class="btn toolbarBtn" data-bind="enable: selectedFiles().length > 0 && isCurrentDirSelected().length == 0, click: trashSelected"><i class="fa fa-times"></i> ${_('Move to trash')}</button>
            <button id="trash-btn-caret" class="btn toolbarBtn dropdown-toggle" data-toggle="dropdown" data-bind="enable: selectedFiles().length > 0 && isCurrentDirSelected().length == 0">
              <span class="caret"></span>
            </button>
            <ul class="dropdown-menu">
              <li><a href="javascript: void(0)" class="delete-link" title="${_('Delete forever')}" data-bind="enable: selectedFiles().length > 0, click: deleteSelected"><i class="fa fa-bolt"></i> ${_('Delete forever')}</a></li>
            </ul>
          </div>
          % endif
          <!-- /ko -->
          % if 'oozie' in apps:
            <button class="btn fileToolbarBtn" title="${_('Submit')}"
              data-bind="visible: selectedFiles().length == 1 && $.inArray(selectedFile().name, ['workflow.xml', 'coordinator.xml', 'bundle.xml']) > -1, click: submitSelected">
              <i class="fa fa-fw fa-play"></i> ${_('Submit')}
            </button>
            % if ENABLE_EXTRACT_UPLOADED_ARCHIVE.get():
              <button class="btn extractArchiveBtn" title="${_('Extract zip, tar.gz, bz2 or bzip2')}"
                data-bind="visible: selectedFiles().length == 1 && isArchive(selectedFile().name) && isCompressEnabled(), click: confirmExtractArchive">
                <i class="fa fa-fw fa-file-archive-o"></i> ${_('Extract')}
              </button>
            % endif
          % endif
          % if 'beeswax' in apps:
            <a class="btn" title="${_('Open in Editor')}"
              data-bind="visible: selectedFiles().length == 1 && isSelectedFileSql(), click: openFileInEditor">
              ${_('Open in Editor')}
            </a>
          % endif
        </div>
      </%def>

      <%def name="creation()">
        <button class="btn fileToolbarBtn" title="${_('Empty trash')}" data-bind="visible: inTrash(), click: purgeTrash"><i class="fa fa-fire"></i> ${_('Empty trash')}</button>
        <div class="btn-toolbar" style="display: inline; vertical-align: middle">
          % if show_upload_button:
          <!-- ko if: isS3 -->
            <!-- ko ifnot: isTaskServerEnabled -->
            <a class="btn fileToolbarBtn" title="${_('Upload files')}" data-bind="visible: !inTrash(), css: {'disabled': isS3Root()}, click: function(){ if (!isS3Root()) { uploadFile(false) }}"><i class="fa fa-arrow-circle-o-up"></i> ${_('Upload')}</a>
            <!-- /ko -->
            <!-- ko if: isTaskServerEnabled -->
            <a class="btn fileToolbarBtn" title="${_('Select a file to upload. The file will first be saved locally and then automatically transferred to the designated file system (e.g., S3, Azure) in the background. The upload modal closes immediately after the file is queued, allowing you to continue working. A notification, \'File upload scheduled. Please check the task server page for progress,\' will confirm the upload has started. This feature is especially useful for large files, as it eliminates the need to wait for the upload to complete.')}" data-bind="visible: !inTrash(), css: {'disabled': isS3Root()}, click: function(){ if (!isS3Root()) { checkAndDisplayAvailableSpace(); uploadFile(true); }}"><i class="fa fa-arrow-circle-o-up"></i> ${_('Upload')}</a>
            <!-- /ko -->
          <!-- /ko -->
          <!-- ko if: isGS -->
            <a class="btn fileToolbarBtn" title="${_('Upload files')}" data-bind="visible: !inTrash(), css: {'disabled': isGSRoot()}, click: function(){ if (!isGSRoot()) { uploadFile() }}"><i class="fa fa-arrow-circle-o-up"></i> ${_('Upload')}</a>
          <!-- /ko -->
          <!-- ko if: isABFS -->
            <!-- ko ifnot: isTaskServerEnabled -->
            <a class="btn fileToolbarBtn" title="${_('Upload files')}" data-bind="visible: !inTrash(), css: {'disabled': isABFSRoot()}, click: function(){ if (!isABFSRoot()) { uploadFile(false) }}"><i class="fa fa-arrow-circle-o-up"></i> ${_('Upload')}</a>
            <!-- /ko -->
            <!-- ko if: isTaskServerEnabled -->
            <a class="btn fileToolbarBtn" title="${_('Select a file to upload. The file will first be saved locally and then automatically transferred to the designated file system (e.g., S3, Azure) in the background. The upload modal closes immediately after the file is queued, allowing you to continue working. A notification, \'File upload scheduled. Please check the task server page for progress,\' will confirm the upload has started. This feature is especially useful for large files, as it eliminates the need to wait for the upload to complete.')}" data-bind="visible: !inTrash(), css: {'disabled': isABFSRoot()}, click: function(){ if (!isABFSRoot()) { checkAndDisplayAvailableSpace(); uploadFile(true); }}"><i class="fa fa-arrow-circle-o-up"></i> ${_('Upload')}</a>
            <!-- /ko -->
          <!-- /ko -->
          <!-- ko ifnot: isS3() || isGS() || isABFS() -->
          <!-- ko ifnot: isTaskServerEnabled -->
          <div id="upload-dropdown" class="btn-group" style="vertical-align: middle">
            <a data-hue-analytics="filebrowser:upload-btn-click" href="javascript: void(0)" class="btn upload-link dropdown-toggle" title="${_('Upload')}" data-bind="click: function() { uploadFile(false); }, visible: !inTrash(), css: {'disabled': (isOFS() && (isOFSRoot() || isOFSServiceID() || isOFSVol()))}">
              <i class="fa fa-arrow-circle-o-up"></i> ${_('Upload')}
            </a>
          </div>
          <!-- /ko -->
          <!-- ko if: isTaskServerEnabled -->
          <div id="upload-dropdown" class="btn-group" style="vertical-align: middle">
            <a data-hue-analytics="filebrowser:upload-btn-click" href="javascript: void(0)" class="btn upload-link dropdown-toggle" title="${_('Select a file to upload. The file will first be saved locally and then automatically transferred to the designated file system (e.g., S3, Azure) in the background. The upload modal closes immediately after the file is queued, allowing you to continue working. A notification, \'File upload scheduled. Please check the task server page for progress,\' will confirm the upload has started. This feature is especially useful for large files, as it eliminates the need to wait for the upload to complete.')}" data-bind="click: function() { checkAndDisplayAvailableSpace(); uploadFile(true);}, visible: !inTrash(), css: {'disabled': (isOFS() && (isOFSRoot() || isOFSServiceID() || isOFSVol()))}">
              <i class="fa fa-arrow-circle-o-up"></i> ${_('Upload')}
            </a>
          </div>
          <!-- /ko -->
          <!-- /ko -->
          % endif
          <div class="btn-group" style="vertical-align: middle">
            <a href="javascript: void(0)" data-toggle="dropdown" class="btn dropdown-toggle" data-bind="visible: !inTrash(), css: {'disabled': isOFSRoot()}">
              <i class="fa fa-plus-circle"></i> ${_('New')}
              <span class="caret"></span>
            </a>
            <ul class="dropdown-menu pull-right" style="top: auto">
              <li data-bind="visible: !isS3() && !isGS() && !isABFS() && !isOFS() || isS3() && !isS3Root() || isGS() && !isGSRoot() || isABFS() && !isABFSRoot() || isOFS() && !isOFSServiceID() && !isOFSVol()"><a data-hue-analytics="filebrowser:new-file-btn-click" href="javascript: void(0)" class="create-file-link" title="${_('File')}"><i class="fa fa-file-o"></i> ${_('File')}</a></li>
              <li><a href="javascript: void(0)" class="create-directory-link" title="${_('Directory')}">
                <i class="fa fa-folder"></i>
                <span data-bind="visible: !isS3() && !isGS() && !isABFS() && !isOFS() || isS3() && !isS3Root() || isGS() && !isGSRoot() || isABFS() && !isABFSRoot() || isOFS() && !isOFSServiceID() && !isOFSVol()">${_('Directory')}</span>
                <span data-bind="visible: (isS3() && isS3Root()) || (isGS() && isGSRoot()) || (isOFS() && isOFSVol())">${_('Bucket')}</span>
                <span data-bind="visible: isABFS() && isABFSRoot()">${_('File System')}</span>
                <span data-bind="visible: isOFS() && isOFSServiceID()">${_('Volume')}</span>
              </a></li>
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
      <div class="alert alert-warn" data-bind="visible: errorMessage(), text: errorMessage">
      </div>

      % if breadcrumbs:
        ${fb_components.breadcrumbs(path, breadcrumbs, True)}
      %endif

      <div style="padding-left: 6px">
        ${dir.list_table_browser(files, path_enc, current_request_path, show_download_button, cwd_set)}
      </div>
    </div>
  </div>
  <div class="hoverMsg hide">
    <p class="hoverText"></p>
  </div>
</div>


%if not is_embeddable:
${ commonfooter(request, messages) | n,unicode }
%endif
