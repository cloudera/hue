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
from django.template.defaultfilters import urlencode, stringformat, filesizeformat, date, time, escape
from desktop.lib.django_util import reverse_with_get, extract_field_data
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
%>

<%namespace name="edit" file="editor_components.mako" />

<%def name="list_table_chooser(files, path, current_request_path)">
  ${_table(files, path, current_request_path, 'chooser')}
</%def>

<%def name="list_table_browser(files, path, current_request_path, show_download_button, cwd_set=True)">
  ${_table(files, path, current_request_path, 'view', show_download_button)}
</%def>

<%def name="_table(files, path, current_request_path, view, show_download_button)">

  <link href="${ static('filebrowser/css/listdir_components.css') }" rel="stylesheet" type="text/css">

  <div data-bind="visible: isLoading">
    <i class="fa fa-spinner fa-spin hue-spinner-large hue-spinner-center muted"></i>
  </div>

  <table class="table table-condensed datatables tablescroller-disable" data-bind="style: {'opacity': isLoading() ? '.5': '1'}">
    <thead>
      <tr>
        <th width="1%"><div data-bind="click: selectAll, css: {hueCheckbox: true, 'fa': true, 'fa-check': allSelected}" class="select-all"></div></th>
        <th class="sortable sorting" data-sort="type" width="1%" data-bind="click: sort">&nbsp;</th>
        <th class="sortable sorting_asc" data-sort="name" data-bind="click: sort">${_('Name')}</th>
        <th class="sortable sorting" data-sort="size" width="10%" data-bind="click: sort">${_('Size')}</th>
        <th class="sortable sorting" data-sort="user" width="10%" data-bind="click: sort">${_('User')}</th>
        <th class="sortable sorting" data-sort="group" width="10%" data-bind="click: sort">${_('Group')}</th>
        <th width="10%">${_('Permissions')}</th>
        <th class="sortable sorting" data-sort="mtime" width="15%" data-bind="click: sort">${_('Date')}</th>
      </tr>
    </thead>
    <tbody id="files" data-bind="template: {name: 'fileTemplate', foreach: files}"></tbody>
    <tfoot>
      <tr data-bind="visible: files().length === 0 && !isLoading()">
        <td colspan="8">
          <div class="alert">
            ${_('There are no files matching the search criteria.')}
          </div>
        </td>
      </tr>
    </tfoot>
  </table>

  <div class="pagination">
    <div class="pull-right flush-right">
        <div class="form-inline pagination-input-form inline">
          <span>${_('Page')}</span>
          <input type="text" data-bind="value: page().number, valueUpdate: 'afterkeydown', event: { change: skipTo }" class="pagination-input" />
          <input type="hidden" id="current_page" data-bind="value: page().number" />
          of <span data-bind="text: page().num_pages"></span>
        </div>

        <ul class="inline">
          <li class="first-page prev" data-bind="css: { 'disabled': (page().number === page().start_index || page().num_pages <= 1) }">
            <a href="javascript:void(0);" data-bind="click: firstPage" title="${_('First page')}"><i class="fa fa-fast-backward"></i></a>
          </li>
          <li class="previous-page" data-bind="css: { 'disabled': (page().number === page().start_index || page().num_pages <= 1) }">
            <a href="javascript:void(0);" data-bind="click: previousPage" title="${_('Previous page')}"><i class="fa fa-backward"></i></a>
          </li>
          <li class="next-page" data-bind="css: { 'disabled': page().number === page().num_pages }">
            <a href="javascript:void(0);" data-bind="click: nextPage" title="${_('Next page')}"><i class="fa fa-forward"></i></a>
          </li>
          <li class="last-page next" data-bind="css: { 'disabled': page().number === page().num_pages }">
            <a href="javascript:void(0);" data-bind="click: lastPage" title="${_('Last page')}"><i class="fa fa-fast-forward"></i></a>
          </li>
        </ul>
    </div>

    <p>${_('Show')}
      <select class="input-mini" data-bind="options: recordsPerPageChoices, value: recordsPerPage"></select>
      ${_('of')} <span data-bind="text: page().total_count"></span> ${_('items')}
    </p>
  </div>

  <!-- extract modal -->
  <div id="confirmExtractModal" class="modal hide fade">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3>${_('Extract Archive')}</h3>
    </div>
    <!-- ko if: selectedFile -->
    <div class="modal-body">
      <p>${_('Start a task to extract the contents of this archive.')}</p>
      <ul>
        <li>
          <span data-bind="text: selectedFile().name"> </span>
        </li>
      </ul>
    </div>
    <div class="modal-footer">
      <a class="btn" data-dismiss="modal">${_('No')}</a>
      <input type="submit" value="${_('Yes')}" class="btn btn-danger" data-bind="click: extractSelectedArchive"/>
    </div>
    <!-- /ko -->
  </div>

  <!-- delete modal -->
  <div id="deleteModal" class="modal hide fade">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3>${_('Confirm Delete')}</h3>
    </div>
    <div class="modal-body">
      <!-- ko if: isS3() && isS3Root() -->
      <p>${_('Are you sure you want to delete these buckets?')}</p>
      <p class="muted">${_('Deleting a bucket will delete all of its contents and release the bucket name to be reserved by others.')}</p>
      <!-- /ko -->
      <!-- ko ifnot: isS3() && isS3Root() -->
      <p>${_('Are you sure you want to delete these files?')}</p>
      <ul data-bind="foreach: $root.selectedFiles">
        <li data-bind="visible: $index() <= 10">
          <span data-bind="text: name"></span>
        </li>
      </ul>
      <!-- ko if: $root.selectedFiles().length > 10 -->
        ${_('and')} <span data-bind="text: $root.selectedFiles().length - 10"></span> ${_('others')}.
      <!-- /ko -->
      <!-- /ko -->
    </div>
    <div class="modal-footer">
      <form id="deleteForm" action="/filebrowser/rmtree" method="POST" enctype="multipart/form-data" class="form-stacked">
        ${ csrf_token(request) | n,unicode }
        <a class="btn" data-dismiss="modal">${_('No')}</a>
        <input type="submit" value="${_('Yes')}" class="btn btn-danger" />
      </form>
    </div>
  </div>

  <!-- restore modal -->
  <div id="restoreTrashModal" class="modal hide fade">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3>${_('Confirm Restore')}</h3>
    </div>
    <div class="modal-body">
      <p>${_('Are you sure you want to restore these files?')}</p>
    </div>
    <div class="modal-footer">
      <form id="restoreTrashForm" action="/filebrowser/trash/restore" method="POST" enctype="multipart/form-data" class="form-stacked">
        ${ csrf_token(request) | n,unicode }
        <a class="btn" data-dismiss="modal">${_('No')}</a>
        <input type="submit" value="${_('Yes')}" class="btn btn-primary" />
      </form>
    </div>
  </div>

  <!-- purge modal -->
  <div id="purgeTrashModal" class="modal hide fade">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3>${_('Confirm empty trash')}</h3>
    </div>

    <div class="modal-body">
      <p>${_('Are you sure you want to permanently delete all your trash?')}</p>
    </div>

    <div class="modal-footer">
      <form id="purgeTrashForm" action="/filebrowser/trash/purge" method="POST" enctype="multipart/form-data" class="form-stacked">
        ${ csrf_token(request) | n,unicode }
        <a class="btn" data-dismiss="modal">${_('Cancel')}</a>
        <input type="submit" value="${_('Delete all')}" class="btn btn-danger" />
      </form>
    </div>
  </div>

  <!-- rename modal -->
  <form id="renameForm" action="/filebrowser/rename?next=${current_request_path | n,unicode }" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix">
    ${ csrf_token(request) | n,unicode }
    <div id="renameModal" class="modal hide fade">
      <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Renaming:')} <span id="renameFileName">file name</span></h3>
      </div>
      <div class="modal-body">
        <label>${_('New name')} <input id="newNameInput" name="dest_path" value="" type="text" class="input-xlarge"/></label>
      </div>
      <div class="modal-footer">
        <div id="renameNameRequiredAlert" class="hide" style="position: absolute; left: 10px;">
          <span class="label label-important">${_('Name is required.')}</span>
        </div>
        <div id="renameNameExistsAlert" class="hide" style="position: absolute; left: 10px;">
          <span class="label label-important"><span class="newName"></span> ${_('already exists.')}</span>
        </div>
        <input id="renameSrcPath" type="hidden" name="src_path" type="text">
        <a class="btn" data-dismiss="modal">${_('Cancel')}</a>
        <input type="submit" value="${_('Rename')}" class="btn btn-primary" />
      </div>
    </div>
  </form>

  <!-- chown modal -->
  % if is_fs_superuser:
  <form id="chownForm" action="/filebrowser/chown" method="POST" enctype="multipart/form-data" class="form-stacked form-padding-fix">
    ${ csrf_token(request) | n,unicode }
    <div id="changeOwnerModal" class="modal hide fade">
    <%
      select_filter = is_fs_superuser and 'SelectWithOther' or ''
    %>
      <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Change Owner/Group')}</h3>
      </div>

      <div class="modal-body change-owner-modal-body clearfix" >
        <div class="alert alert-message block-message info">${_('Note: Only the Hadoop superuser, "%(superuser)s" or the HDFS supergroup, "%(supergroup)s" on this file system, may change the owner of a file.') % dict(superuser=superuser, supergroup=supergroup)}</div>
        <div style="padding-left: 15px; padding-bottom: 10px;">
          <label>${_('User')}</label>
          ${ edit.selection("user", users, user.username, "user_other") }
          <label>${_('Group')}</label>
          ${ edit.selection("group", groups, 'supergroup', "group_other") }
          <br />
          <label style="display: inline;">${_('Recursive')}</label> <input type="checkbox" name="recursive" style="margin-bottom:4px">
        </div>
      </div>

      <div class="modal-footer" style="padding-top: 10px;">
        <div id="chownRequired" class="hide" style="position: absolute; left: 10px;">
          <span class="label label-important">${_('Name is required.')}</span>
        </div>
        <a class="btn" onclick="$('#changeOwnerModal').modal('hide');">${_('Cancel')}</a>
        <input class="btn btn-primary" type="submit" value="${_('Submit')}" />
      </div>
    </div>
  </form>
  % endif

  <!-- chmod modal -->
  <form action="/filebrowser/chmod" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix" id="chmodForm">
    ${ csrf_token(request) | n,unicode }
    <div id="changePermissionModal" class="modal hide fade">
      <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Change Permissions:')} </h3>
      </div>
      <div class="modal-body table-margin">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>&nbsp;</th>
              <th class="center">${_('User')}</th>
              <th class="center">${_('Group')}</th>
              <th class="center">${_('Other')}</th>
              <th class="center">&nbsp;</th>
              <th width="120">&nbsp</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>${_('Read')}</strong></td>
              <td class="center"><input type="checkbox" data-bind="attr: {checked: selectedFile.mode }" checked="" name="user_read"></td>
              <td class="center"><input type="checkbox" data-bind="attr: {checked: selectedFile.mode }" checked="" name="group_read"></td>
              <td class="center"><input type="checkbox" data-bind="attr: {checked: selectedFile.mode }" checked="" name="other_read"></td>
              <td colspan="2">&nbsp;</td>
            </tr>
            <tr>
              <td><strong>${_('Write')}</strong></td>
              <td class="center"><input type="checkbox" data-bind="attr: {checked: selectedFile.mode }" checked="" name="user_write"></td>
              <td class="center"><input type="checkbox" data-bind="attr: {checked: selectedFile.mode }" checked="" name="group_write"></td>
              <td class="center"><input type="checkbox" data-bind="attr: {checked: selectedFile.mode }" checked="" name="other_write"></td>
              <td colspan="2">&nbsp;</td>
            </tr>
            <tr>
              <td><strong>${_('Execute')}</strong></td>
              <td class="center"><input type="checkbox" checked="" name="user_execute"></td>
              <td class="center"><input type="checkbox" checked="" name="group_execute"></td>
              <td class="center"><input type="checkbox" checked="" name="other_execute"></td>
              <td colspan="2">&nbsp;</td>
            </tr>
            <tr>
              <td><strong>${_('Sticky')}</strong></td>
              <td colspan="3">&nbsp;</td>
              <td class="center"><input type="checkbox" name="sticky"></td>
              <td>&nbsp;</td>
            </tr>
            <tr>
              <td><strong>${_('Recursive')}</strong></td>
              <td colspan="3">&nbsp;</td>
              <td class="center"><input type="checkbox" name="recursive"></td>
              <td>&nbsp;</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="modal-footer" style="padding-top: 10px;">
        <a class="btn" onclick="$('#changePermissionModal').modal('hide');">${_('Cancel')}</a>
        <input class="btn btn-primary" type="submit" value="${_('Submit')}"/>
      </div>
    </div>
  </form>

  <!-- move modal -->
  <form id="moveForm" action="/filebrowser/move" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix">
    ${ csrf_token(request) | n,unicode }
    <div id="moveModal" class="modal hide fade">
      <div class="modal-header" style="padding-bottom: 10px">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Move to')}</h3>
      </div>
      <div class="modal-body">
        <div id="moveHdfsTree"></div>
      </div>
      <div class="modal-footer">
        <div>
          <input type="text" class="input-xlarge disable-autofocus" value="" name="dest_path" id="moveDestination" placeholder="${_('Select a folder or paste a path...')}" />
          <span id="moveNameRequiredAlert" class="hide label label-important">${_('Required')}</span>
        </div>
        <a class="btn" onclick="$('#moveModal').modal('hide');">${_('Cancel')}</a>
        <input class="btn btn-primary disable-enter" type="submit" value="${_('Move')}"/>
      </div>
    </div>
  </form>

  <!-- copy modal -->
  <form id="copyForm" action="/filebrowser/copy" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix">
    ${ csrf_token(request) | n,unicode }
    <div id="copyModal" class="modal hide fade">
      <div class="modal-header" style="padding-bottom: 10px">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${_('Copy to')}</h3>
      </div>
      <div class="modal-body">
        <div id="copyHdfsTree"></div>
      </div>
      <div class="modal-footer">
        <div>
          <input type="text" class="input-xlarge disable-autofocus" value="" name="dest_path" id="copyDestination" placeholder="${_('Select a folder or paste a path...')}" />
          <span id="copyNameRequiredAlert" class="hide label label-important">${_('Required')}</span>
        </div>
        <a class="btn" onclick="$('#copyModal').modal('hide');">${_('Cancel')}</a>
        <input class="btn btn-primary disable-enter" type="submit" value="${_('Copy')}"/>
      </div>
    </div>
  </form>

  <!-- upload file modal -->
  <div id="uploadFileModal" class="modal hide fade">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal" data-bind="visible: pendingUploads() == 0">&times;</a>
      <h3>${_('Upload to')} <span id="uploadDirName" data-bind="text: currentPath"></span></h3>
    </div>
    <div class="modal-body form-inline">
      <div id="fileUploader" class="uploader">
        <noscript>
          <p>${_('Enable JavaScript to use the file uploader.')}</p>
        </noscript>
      </div>
    </div>
    <div class="modal-footer"></div>
  </div>

  <!-- upload archive modal -->
  <div id="uploadArchiveModal" class="modal hide fade">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal" data-bind="visible: pendingUploads() == 0">&times;</a>
      <h3>${_('Upload and extract in')} <span id="uploadDirName" data-bind="text: currentPath"></span></h3>
    </div>
    <div class="modal-body form-inline">
      <div id="archiveUploader" class="uploader">
        <noscript>
          <p>${_('Enable JavaScript to use the file uploader.')}</p>
        </noscript>
      </div>
    </div>
    <div class="modal-footer"></div>
  </div>

  <!-- new directory modal -->
  <form id="createDirectoryForm" data-bind="submit: createDirectory" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix">
    ${ csrf_token(request) | n,unicode }
    <div id="createDirectoryModal" class="modal hide fade">
      <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <!-- ko if: !isS3() || (isS3() && !isS3Root()) -->
        <h3>${_('Create Directory')}</h3>
        <!-- /ko -->
        <!-- ko if: isS3() && isS3Root() -->
        <h3>${_('Create Bucket')}</h3>
        <!-- /ko -->
      </div>
      <div class="modal-body">
        <label>
          <!-- ko if: !isS3() || (isS3() && !isS3Root()) -->
          ${_('Directory Name')}
          <!-- /ko -->
          <!-- ko if: isS3() && isS3Root() -->
          ${_('Bucket Name')}
          <!-- /ko -->
          <input id="newDirectoryNameInput" name="name" value="" type="text" class="input-xlarge"/></label>
        <input type="hidden" name="path" type="text" data-bind="value: currentPath"/>
      </div>
      <div class="modal-footer">
        <div id="directoryNameRequiredAlert" class="hide" style="position: absolute; left: 10px;">
          <span class="label label-important">${_('Directory name is required.')}</span>
        </div>
        <div id="directoryNameExistsAlert" class="hide" style="position: absolute; left: 10px;">
          <span class="label label-important"><span class="newName"></span> ${_('already exists.')}</span>
        </div>
        <a class="btn" href="#" data-dismiss="modal">${_('Cancel')}</a>
        <input class="btn btn-primary" type="submit" value="${_('Create')}" />
      </div>
    </div>
  </form>

  <!-- new file modal -->
  <form id="createFileForm" data-bind="submit: createFile" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix">
    ${ csrf_token(request) | n,unicode }
    <div id="createFileModal" class="modal hide fade">
        <div class="modal-header">
          <a href="#" class="close" data-dismiss="modal">&times;</a>
          <h3>${_('Create File')}</h3>
        </div>
        <div class="modal-body">
          <label>${_('File Name')} <input id="newFileNameInput" name="name" value="" type="text" class="input-xlarge"/></label>
          <input type="hidden" name="path" type="text" data-bind="value: currentPath"/>
        </div>
        <div class="modal-footer">
           <div id="fileNameRequiredAlert" class="alert-message error hide" style="position: absolute; left: 10px;">
            <span class="label label-important">${_('File name is required.')}</span>
          </div>
          <div id="fileNameExistsAlert" class="hide" style="position: absolute; left: 10px;">
            <span class="label label-important"><span class="newName"></span> ${_('already exists.')}</span>
          </div>
          <a class="btn" href="#" data-dismiss="modal">${_('Cancel')}</a>
          <input class="btn btn-primary" type="submit" value="${_('Create')}" />
        </div>
    </div>
  </form>

  <!-- content summary modal -->
  <div id="contentSummaryModal" class="modal hide fade">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <!-- ko if: selectedFile -->
      <h3 style="word-break: break-all">${_('Summary for')} <span data-bind="text: selectedFile().path"></span></h3>
      <!--/ko -->
    </div>
    <div class="modal-body">
      <div data-bind="visible: isLoadingSummary"><i class="fa fa-spin fa-spinner fa-2x fa-fw" style="color: #CCC"></i></div>
      <table class="table table-striped" data-bind="visible: !isLoadingSummary()">
        <tr>
          <th>${ _('Disk space consumed') }</th>
          <td data-bind="text: formatBytes(contentSummary().spaceConsumed(), 4)"></td>
        </tr>
        <tr>
          <th>${ _('Bytes used') }</th>
          <td data-bind="text: formatBytes(contentSummary().length(), 4)"></td>
        </tr>
        <tr>
          <th>${ _('Namespace quota') }</th>
          <td data-bind="text: formatBytes(contentSummary().quota(), 4)"></td>
        </tr>
        <tr>
          <th>${ _('Disk space quota') }</th>
          <td data-bind="text: formatBytes(contentSummary().spaceQuota(), 4)"></td>
        </tr>
        <tr>
          <th>${ _('Number of directories') }</th>
          <td data-bind="text: contentSummary().directoryCount()"></td>
        </tr>
        <tr>
          <th>${ _('Number of files') }</th>
          <td data-bind="text: contentSummary().fileCount()"></td>
        </tr>
      </table>
    </div>
    <div class="modal-footer">
      <a class="btn" data-dismiss="modal">${_('Close')}</a>
    </div>
  </div>

  <!-- actions context menu -->
  <ul class="context-menu dropdown-menu">
  <!-- ko ifnot: $root.inTrash -->
    <li data-bind="visible: !isS3() || (isS3() && !isS3Root())"><a href="#" title="${_('Rename')}" data-bind="visible: !$root.inTrash() && $root.selectedFiles().length == 1, click: $root.renameFile,
    enable: $root.selectedFiles().length == 1 && isCurrentDirSelected().length == 0"><i class="fa fa-fw fa-font"></i>
    ${_('Rename')}</a></li>
    <li data-bind="visible: !isS3() || (isS3() && !isS3Root())"><a href="#"title="${_('Move')}" data-bind="click: $root.move, enable: $root.selectedFiles().length > 0 &&
    isCurrentDirSelected().length == 0"><i class="fa fa-fw fa-random"></i> ${_('Move')}</a></li>
    <li data-bind="visible: !isS3() || (isS3() && !isS3Root())"><a href="#" title="${_('Copy')}" data-bind="click: $root.copy, enable: $root.selectedFiles().length > 0 &&
    isCurrentDirSelected().length == 0"><i class="fa fa-fw fa-files-o"></i> ${_('Copy')}</a></li>
    % if show_download_button:
    <li><a href="#" title="${_('Download')}" data-bind="visible: !$root.inTrash() && $root.selectedFiles().length == 1 && selectedFile().type == 'file', click: $root.downloadFile"><i class="fa fa-fw fa-arrow-circle-o-down"></i> ${_('Download')}</a></li>
    % endif
    <li class="divider" data-bind="visible: !isS3()"></li>
    % if is_fs_superuser:
    <li data-bind="css: {'disabled': $root.isCurrentDirSentryManaged || selectedSentryFiles().length > 0 }, visible: !isS3()">
      <a href="#" data-bind="visible: !$root.inTrash(), click: $root.changeOwner, enable: $root.selectedFiles().length > 0">
        <i class="fa fa-fw fa-user"></i> ${_('Change owner / group')}
      </a>
    </li>
    % endif
    <li data-bind="css: {'disabled': $root.isCurrentDirSentryManaged() || selectedSentryFiles().length > 0 }, visible: !isS3()">
      <a href="#" data-bind="visible: !$root.inTrash(), click: $root.changePermissions, enable: $root.selectedFiles().length > 0">
        <i class="fa fa-fw fa-list-alt"></i> ${_('Change permissions')}
      </a>
    </li>
    <li class="divider" data-bind="visible: !isS3() || (isS3() && !isS3Root())"></li>
    % if is_trash_enabled:
    <li><a href="#" data-bind="enable: $root.selectedFiles().length > 0 && isCurrentDirSelected().length == 0, click: $root.trashSelected"><i class="fa fa-fw fa-times"></i> ${_('Move to trash')}</a></li>
    %endif
    <li><a href="#" class="delete-link" title="${_('Delete forever')}" data-bind="enable: $root.selectedFiles().length > 0, click: $root.deleteSelected"><i class="fa fa-fw fa-bolt"></i> ${_('Delete forever')}</a></li>
    <li class="divider" data-bind="visible: !isS3()"></li>
    <li data-bind="css: {'disabled': selectedFiles().length > 1 }, visible: !isS3()">
      <a class="pointer" data-bind="click: function(){ selectedFiles().length == 1 ? showSummary(): void(0)}"><i class="fa fa-fw fa-pie-chart"></i> ${_('Summary')}</a>
    </li>
  <!-- /ko -->
  <!-- ko if: $root.inTrash -->
    <li><a href="#" title="${_('Restore from trash')}" data-bind="visible: inRestorableTrash() &&  selectedFiles().length > 0 && isCurrentDirSelected().length == 0, click: restoreTrashSelected"><i class="fa fa-fw fa-cloud-upload"></i> ${_('Restore')}</a></li>
    <li class="divider"></li>
    <li><a href="#" title="${_('Empty trash')}" data-bind="visible: inTrash(), click: purgeTrash"><i class="fa fa-fw fa-fire"></i> ${_('Empty trash')}</a></li>
  <!-- /ko -->
  </ul>

  <div id="submit-wf-modal" class="modal hide"></div>

  <div id="progressStatus" class="uploadstatus well hide">
    <h4>${ _('Upload progress') }</h4>
    <div id="progressStatusBar" class="hide progress active">
      <div class="bar bar-upload"></div>
    </div>
    <div id="progressStatusContent" class="scrollable-uploadstatus">
      <div class="updateStatus"> </div>
    </div>
  <div>
</div>

  <script id="fileTemplate" type="text/html">
    <tr style="cursor: pointer" data-bind="drop: { enabled: name !== '.' && type !== 'file' && (!$root.isS3() || ($root.isS3() && !$root.isS3Root())), value: $data }, event: { mouseover: toggleHover, mouseout: toggleHover, contextmenu: showContextMenu }, click: $root.viewFile, css: { 'row-selected': selected(), 'row-highlighted': highlighted() }">
      <td class="center" data-bind="click: handleSelect" style="cursor: default">
        <div data-bind="visible: name != '..', css: { hueCheckbox: name != '..', 'fa': name != '..', 'fa-check': selected }"></div>
      </td>
      <td class="left"><i data-bind="click: $root.viewFile, css: { 'fa': true,
       % if 'oozie' in apps:
      'fa-play': $.inArray(name, ['workflow.xml', 'coordinator.xml', 'bundle.xml']) > -1,
       % endif
      'fa-file-o': type == 'file', 'fa-folder': type != 'file', 'fa-folder-open': type != 'file' && hovered(), 'fa-cloud': type != 'file' && isBucket() }"></i></td>
      <td data-bind="attr: {'title': tooltip}" rel="tooltip">
        <!-- ko if: name == '..' -->
        <a href="#" data-bind="click: $root.viewFile"><i class="fa fa-level-up"></i></a>
        <!-- /ko -->
        <!-- ko if: name != '..' -->
        <strong><a href="#" data-bind="drag: { enabled: (!$root.isS3() || ($root.isS3() && !$root.isS3Root())), value: $data }, click: $root.viewFile, text: name, attr: { 'draggable': $.inArray(name, ['.', '..', '.Trash']) === -1 && !$root.isS3()}"></a></strong>
        <!-- /ko -->
      </td>
      <td>
        <span data-bind="visible: type == 'file', text: stats.size"></span>
      </td>
      <td>
        % if is_fs_superuser:
        <span data-bind="text: stats.user, visible: !selected() || $root.isCurrentDirSentryManaged() || isSentryManaged"></span>
        <a href="#" rel="tooltip" title="${_('Change owner')}" data-original-title="${_('Change owner')}"
            data-bind="text: stats.user, visible: !$root.inTrash() && selected() && !$root.isCurrentDirSentryManaged() && !isSentryManaged, click: $root.changeOwner, enable: $root.selectedFiles().length > 0"></a>
        % else:
        <span data-bind="text: stats.user"></span>
        % endif
      </td>
      <td>
        % if is_fs_superuser:
        <span data-bind="text: stats.group, visible: ! selected() || $root.isCurrentDirSentryManaged() || isSentryManaged"></span>
        <a href="#" rel="tooltip" title="${_('Change group')}" data-original-title="${_('Change group')}"
            data-bind="text: stats.group, visible: !$root.inTrash() && selected() && !$root.isCurrentDirSentryManaged() && !isSentryManaged, click: $root.changeOwner"></a>
        % else:
        <span data-bind="text: stats.group"></span>
        % endif
      </td>
      <td>
        <span data-bind="text: permissions, visible: $root.isS3() || !selected() || $root.isCurrentDirSentryManaged() || isSentryManaged"></span>
        <a href="#" rel="tooltip" title="${_('Change permissions')}"
            data-bind="text: permissions, visible: !$root.isS3() && !$root.inTrash() && selected() && !$root.isCurrentDirSentryManaged() && !isSentryManaged, click: $root.changePermissions" data-original-title="${_('Change permissions')}"></a>
      </td>
      <td data-bind="text: stats.mtime" style="white-space: nowrap;"></td>
    </tr>
  </script>

  <script src="${ static('desktop/js/jquery.hdfstree.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/ext/js/jquery/plugins/jquery-ui-1.10.4.custom.min.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/js/dropzone.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/js/apiHelper.js') }"></script>


  <script charset="utf-8">
    var _dragged;
    var _dropzone;

    ko.bindingHandlers.drag = {
      update: function (element, valueAccessor, allBindingsAccessor, viewModel) {
        var dragElement = $(element);
        try {
          dragElement.draggable('destroy');
        }
        catch (e) {}
        var dragOptions = {
          helper: 'clone',
          revert: true,
          revertDuration: 0,
          start: function () {
            if ($(element).is('[draggable]')) {
              viewModel.selected(true);
            }
            _dragged = ko.utils.unwrapObservable(valueAccessor().value);
          },
          cursor: "move",
          delay: 300
        };
        dragElement.draggable(dragOptions).disableSelection();
      }
    };

    ko.bindingHandlers.drop = {
      update: function (element, valueAccessor) {
        var dropElement = $(element);
        try {
          dropElement.droppable('destroy');
        }
        catch (e) {}
        if (valueAccessor().enabled) {
          var dropOptions = {
            hoverClass: 'drag-hover',
            drop: function (event, ui) {
              var destpath = valueAccessor().value.path;

              dropElement.fadeOut(200, function () {
                dropElement.fadeIn(200);
              });

              if (destpath) {
                $('#moveDestination').val(destpath);
                viewModel.move('nomodal', _dragged);
              }
            }
          };
          dropElement.droppable(dropOptions);
        }
      }
    };

    var apiHelper = ApiHelper.getInstance();

    // migration to the new history
    if ($.totalStorage('hue_fb_history')) {
      var s3History = [],
        hdfsHistory = [];
      $.totalStorage('hue_fb_history').forEach(function(item) {
        if (item.toLowerCase().indexOf('s3a://') === 0){
          s3History.push(item);
        }
        else {
          hdfsHistory.push(item);
        }
      });
      $.totalStorage('hue_fb_history', null);
      apiHelper.setInTotalStorage('fb', 'history_s3', s3History);
      apiHelper.setInTotalStorage('fb', 'history_hdfs', hdfsHistory);
    }

    var getHistorySlug = function() {
      var slug = 'history_';
      if (viewModel && viewModel.isS3()){
        slug += 's3';
      }
      else {
        slug += 'hdfs';
      }
      return slug;
    }

    var getHistory = function () {
      return apiHelper.getFromTotalStorage('fb', getHistorySlug(), [])
    };

    var showHistory = function () {
      var history = getHistory().slice(0, 10),
        frag = $('<ul/>', {
                  'id': 'hashHistory',
                  'class': 'dropdown-menu',
                  'role': 'menu',
                  'aria-labelledby': 'historyDropdown'
                });

      $('#hashHistory').remove();
      if (history.length === 0){
        $('.history').addClass('no-history');
      }

      history.forEach(function (item) {
        var url = '/filebrowser/#' + item,
          list = $('<li><a href="' + url + '">' + item + '</a></li>');

        $(list).appendTo(frag);
      });

      $('<li>', {
        'class': 'divider'
      }).appendTo(frag);

      $('<li><a href="javascript:void(0)">${ _("Clear history...") }</a></li>')
          .appendTo(frag)
          .on('click', function(){
            apiHelper.setInTotalStorage('fb', getHistorySlug(), []);
            $('.history').addClass('no-history');
          });

      $(frag).appendTo('.history');

      return this;
    };

    var addPathToHistory = function (path) {
      $('.history').removeClass('no-history');
      var history = getHistory();
      if (path != '/filebrowser/') {
        var _basePath = '${url('filebrowser.views.view', path='')}';
        if (path.indexOf(_basePath) > -1) {
          path = path.substr(_basePath.length);
        }

        // ensure no duplicates are pushed to $.totalStorage()
        if (history.indexOf(path) === -1) {
          history.unshift(path);
          $('.history').removeClass('no-history');
        } else {
          history.unshift(history.splice(history.indexOf(path), 1)[0]);
        }
        apiHelper.setInTotalStorage('fb', getHistorySlug(), history.slice(0, 10));
      }
    };

    // ajax modal windows
    var openChownWindow = function (path, user, group, next) {
      $.ajax({
        url: "/filebrowser/chown",
        data: {"path": path, "user": user, "group": group, "next": next},
        beforeSend: function (xhr) {
          xhr.setRequestHeader("X-Requested-With", "Hue");
        },
        dataType: "html",
        success: function (data) {
          $("#changeOwnerModal").html(data);
          $("#changeOwnerModal").modal({
            keyboard:true,
            show:true
          });
        }
      });
    };

    var fileExists = function (newName) {
      if (viewModel) {
        var files = viewModel.files();
        for (var i = 0; i < files.length; i++) {
          if (files[i].name == newName) {
            return true;
          }
        }
      }
      return false;
    };

    var resetActionbar = function() {
      $(".actionbar").attr("style", "min-width: 800px");
      $(".actionbar").data("originalWidth", $(".actionbar").width());
      $(".actionbarGhost").addClass("hide");
    };

    var stripHashes = function (str) {
      return str.replace(/#/gi, encodeURIComponent("#"));
    };

    var formatBytes = function (bytes, decimals) {
      if (bytes == -1) return "${ _('Not available.') }";
      if (bytes == 0) return "0 Byte";
      var k = 1024;
      var dm = decimals + 1 || 3;
      var sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
      var i = Math.floor(Math.log(bytes) / Math.log(k));
      return (bytes / Math.pow(k, i)).toPrecision(dm) + ' ' + sizes[i];
    }

    var Page = function (page) {
      if (page != null) {
        return {
          number: page.number,
          num_pages: page.num_pages,
          previous_page_number: page.previous_page_number,
          next_page_number: page.next_page_number,
          start_index: page.start_index,
          end_index: page.end_index,
          total_count: page.total_count
        }
      }
      return {
      }
    };

    var File = function (file) {
      file.tooltip = "";

      if (file.name == "."){
        file.tooltip = "${_('This folder')}";
      }

      if (file.name == ".."){
        file.tooltip = "${_('One level up')}";
      }

      return {
        name: file.name,
        path: file.path,
        url: file.url,
        type: file.type,
        permissions: file.rwx,
        mode: file.mode,
        isSentryManaged: file.is_sentry_managed,
        stats: {
          size: file.humansize,
          user: file.stats.user,
          group: file.stats.group,
          mtime: file.mtime
        },
        isBucket: ko.pureComputed(function(){
          return file.path.toLowerCase().indexOf('s3a://') == 0 && file.path.substr(5).indexOf('/') == -1
        }),
        selected: ko.observable(false),
        highlighted: ko.observable(file.highlighted || false),
        handleSelect: function (row, e) {
          e.preventDefault();
          e.stopPropagation();
          this.selected(! this.selected());
          this.highlighted(false);
          viewModel.allSelected(false);
        },
        // display the context menu when an item is right/context clicked
        showContextMenu: function (row, e) {
          var cm = $('.context-menu'),
            actions = $('#ch-dropdown'),
            rect = document.querySelector('body').getBoundingClientRect();

          e.stopPropagation();

          // close the actions menu from button area if open
          if (actions.hasClass('open')) {
            actions.removeClass('open');
          }

          // display context menu and ensure it is on-screen
          if ($.inArray(row.name, ['..', '.', '.Trash']) === -1) {
            this.selected(true);
            cm.css({ display: 'block', top: e.pageY - 15, left: (e.pageX < rect.right - 200 ) ? e.pageX : e.pageX - 250 });
            if ($(window).height() - 55 < $('.context-menu').position().top - $('body').scrollTop() + $('.context-menu').height()) {
              cm.css({
                top: e.pageY - $('.context-menu').height()
              });
            }
          } else {
            cm.css({ display: 'none' });
          }
        },
        hovered: ko.observable(false),
        toggleHover: function (row, e) {
          this.hovered(! this.hovered());
        },
        tooltip:file.tooltip
      }
    };

    var Breadcrumb = function (breadcrumb) {
      return {
        url: breadcrumb.url,
        label: breadcrumb.label,
        show: function (breadcrumb, e) {
          var isLeftButton = (e.which || e.button) === 1;
          if (isLeftButton) {
            if (! (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey)) {
              e.stopPropagation();
              e.preventDefault();
              if (this.url == null || this.url == "") {
                // forcing root on empty breadcrumb url
                this.url = "/";
              }

              viewModel.targetPageNum(1);
              viewModel.targetPath("${url('filebrowser.views.view', path='')}" + stripHashes(this.url));
              location.hash = this.url;
            }
            else {
              window.open($(e.target).attr('href'));
            }
          }
        }
      }
    };

    var FileBrowserModel = function (files, page, breadcrumbs, currentDirPath) {
      var self = this;

      if (! $.cookie("hueFilebrowserRecordsPerPage")){
        $.cookie("hueFilebrowserRecordsPerPage", "45");
      }

      self.page = ko.observable(new Page(page));
      self.recordsPerPageChoices = ["15", "30", "45", "60", "100", "200", "1000"],
      self.recordsPerPage = ko.observable($.cookie("hueFilebrowserRecordsPerPage"));
      self.targetPageNum = ko.observable(1);
      self.targetPath = ko.observable("${current_request_path | n,unicode }");
      self.sortBy = ko.observable("name");
      self.sortDescending = ko.observable(false);
      self.searchQuery = ko.observable("");
      self.searchQuery.extend({ rateLimit: 500 });
      self.enableFilterAfterSearch = true;
      self.isCurrentDirSentryManaged = ko.observable(false);
      self.pendingUploads = ko.observable(0);
      self.pendingUploads.subscribe(function (val) {
        if (val > 0) {
          if ($('#uploadFileModal').data('modal')) {
            $('#uploadFileModal').data('modal').$element.off('keyup.dismiss.modal');
            if ($('#uploadFileModal').data('modal').$backdrop){
              $('#uploadFileModal').data('modal').$backdrop.off('click');
            }
          }
          if ($('#uploadArchiveModal').data('modal')) {
            $('#uploadArchiveModal').data('modal').$element.off('keyup.dismiss.modal');
            if ($('#uploadArchiveModal').data('modal').$backdrop) {
              $('#uploadArchiveModal').data('modal').$backdrop.off('click');
            }
          }
        }
      });
      self.lastUploadBatch = ko.observableArray([]);

      self.fileNameSorting = function (l, r) {
        if (l.name == "..") {
          return -1;
        }
        else if (r.name == "..") {
          return 1;
        }
        else if (l.name == ".") {
          return -1;
        }
        else if (r.name == ".") {
          return 1;
        }
        else {
          var _ret = l.name > r.name ? 1 : -1;
          if (self.sortDescending()){
            _ret = _ret * -1;
          }
          return _ret;
        }
      }

      self.files = ko.observableArray(ko.utils.arrayMap(files, function (file) {
        return new File(file);
      }));

      if (self.sortBy() == "name"){
        self.files.sort(self.fileNameSorting);
      }

      self.homeDir = ko.observable("${home_directory}");

      self.breadcrumbs = ko.observableArray(ko.utils.arrayMap(breadcrumbs, function (breadcrumb) {
        return new Breadcrumb(breadcrumb);
      }));

      self.sort = function (viewModel, event) {
        var el = $(event.currentTarget);

        el.siblings(".sortable").attr("class", "sortable sorting");

        self.sortBy(el.data("sort"));

        el.removeClass("sorting");

        if (el.hasClass("sorting_asc")) {
          self.sortDescending(true);
        } else {
          self.sortDescending(false);
        }

        el.attr("class", "sortable");

        if (self.sortDescending() == true) {
          el.addClass("sorting_desc");
        } else {
          el.addClass("sorting_asc");
        }
        self.retrieveData();
      }

      self.isLoading = ko.observable(true);

      self.allSelected = ko.observable(false);

      self.selectedFiles = ko.computed(function () {
        return ko.utils.arrayFilter(self.files(), function (file) {
          return file.selected();
        });
      }, self).extend({ rateLimit: { timeout: 500, method: "notifyWhenChangesStop" } });

      self.selectedSentryFiles = ko.computed(function () {
        return ko.utils.arrayFilter(self.files(), function (file) {
          return file.selected() && file.isSentryManaged;
        });
      }, self).extend({ rateLimit: { timeout: 500, method: "notifyWhenChangesStop" } });

      self.isCurrentDirSelected = ko.computed(function () {
        return ko.utils.arrayFilter(self.files(), function (file) {
          return file.name == "." && file.selected();
        });
      }, self).extend({ rateLimit: { timeout: 500, method: "notifyWhenChangesStop" } });

      self.selectedFile = ko.computed(function () {
        return self.selectedFiles()[0];
      }, self).extend({ rateLimit: { timeout: 500, method: "notifyWhenChangesStop" } });

      self.currentPath = ko.observable(currentDirPath);
      self.currentPath.subscribe(function (path) {
        $(document).trigger('currPathLoaded', { path: path });
      });

      self.isS3 = ko.pureComputed(function () {
        return self.currentPath().toLowerCase().indexOf('s3a://') === 0;
      });

      self.isS3.subscribe(function (newVal) {
        if (newVal) {
          huePubSub.publish('update.autocompleters');
          huePubSub.publish('update.history');
        }
      });

      self.isS3Root = ko.pureComputed(function () {
        return self.isS3() && self.currentPath().toLowerCase() === 's3a://';
      });

      self.inTrash = ko.computed(function() {
        return self.currentPath().match(/^\/user\/.+?\/\.Trash/);
      });

      self.inRestorableTrash = ko.computed(function() {
        return self.currentPath().match(/^\/user\/.+?\/\.Trash\/.+?/);
      });

      self.isLoadingSummary = ko.observable(true);
      self.contentSummary = ko.observable(ko.mapping.fromJS({
        spaceConsumed: -1,
        quota: -1,
        spaceQuota: -1,
        length: 0,
        directoryCount: 0,
        fileCount: 0
      }));
      self.showSummary = function () {
        self.isLoadingSummary(true);
        $("#contentSummaryModal").modal("show");
        $.getJSON("${url('filebrowser.views.content_summary', path='')}" + self.selectedFile().path, function (data) {
          if (data.status == 0) {
            self.contentSummary(ko.mapping.fromJS(data.summary));
            self.isLoadingSummary(false);
          } else {
            $(document).trigger("error", data.message);
            $("#contentSummaryModal").modal("hide");
          }
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
          $("#contentSummaryModal").modal("hide");
        });
      }

      self.getStats = function (callback) {
        $.getJSON(self.targetPath() + (self.targetPath().indexOf('?') > 0 ? '&' : '?') + "pagesize=1&format=json", callback);
      };

      self.retrieveData = function () {
        self.isLoading(true);

        $.getJSON(self.targetPath() + (self.targetPath().indexOf('?') > 0 ? '&' : '?') + "pagesize=" + self.recordsPerPage() + "&pagenum=" + self.targetPageNum() + "&filter=" + self.searchQuery() + "&sortby=" + self.sortBy() + "&descending=" + self.sortDescending() + "&format=json", function (data) {
          if (data.error){
            $(document).trigger("error", data.error);
            self.isLoading(false);
            return false;
          }

          if (data.type != null && data.type == "file") {
            location.href = data.url;
            return false;
          }

          self.updateFileList(data.files, data.page, data.breadcrumbs, data.current_dir_path, data.is_sentry_managed);

          if ($("#hueBreadcrumbText").is(":visible")) {
            $(".hueBreadcrumb").show();
            $("#hueBreadcrumbText").hide();
            $("#editBreadcrumb").show();
          }
        });
      };

      self.updateFileList = function (files, page, breadcrumbs, currentDirPath, isSentryManaged) {
        $(".tooltip").hide();

        self.isCurrentDirSentryManaged(isSentryManaged);

        self.page(new Page(page));

        self.files(ko.utils.arrayMap(files, function (file) {
          file.highlighted = self.lastUploadBatch.indexOf(file.path) > -1;
          return new File(file);
        }));
        self.lastUploadBatch([]);
        if (self.sortBy() == "name"){
          self.files.sort(self.fileNameSorting);
        }

        self.breadcrumbs(ko.utils.arrayMap(breadcrumbs, function (breadcrumb) {
          return new Breadcrumb(breadcrumb);
        }));

        self.currentPath(currentDirPath);

        $('.uploader').trigger('fb:updatePath', {dest:self.currentPath()});

        self.isLoading(false);

        $("*[rel='tooltip']").tooltip({ placement:"left" });

        if ($('.row-highlighted').length > 0) {
          $(window).scrollTop($('.row-highlighted:eq(0)').offset().top - 150);
        }
        else {
          $(window).scrollTop(0);
        }

        resetActionbar();
      };

      self.recordsPerPage.subscribe(function (newValue) {
        $.cookie("hueFilebrowserRecordsPerPage", newValue);
        self.retrieveData();
      });

      self.skipTo = function () {
        var doc = document,
          old_page = doc.querySelector('#current_page').value,
          page = doc.querySelector('.pagination-input');

        if (! isNaN(page.value) && (page.value > 0 && page.value <= self.page().num_pages)) {
          self.goToPage(page.value);
        } else {
          page.value = old_page;
        }
      };

      self.goToPage = function (pageNumber) {
        self.targetPageNum(pageNumber);
        if (location.hash.indexOf("!!") > -1){
          location.hash =  location.hash.substring(0, location.hash.indexOf("!!")) + "!!" + pageNumber;
        } else {
          location.hash += "!!" + pageNumber;
        }
      };

      self.firstPage = function () {
        self.goToPage(1)
      };

      self.previousPage = function () {
        self.goToPage(self.page().previous_page_number)
      };

      self.nextPage = function () {
        self.goToPage(self.page().next_page_number)
      };

      self.lastPage = function () {
        self.goToPage(self.page().num_pages)
      };

      self.selectAll = function () {
        self.allSelected(!self.allSelected());
        ko.utils.arrayForEach(self.files(), function (file) {
          if (file.name != "." && file.name != "..") {
            file.selected(self.allSelected());
          }
        });
        return true;
      };

      self.searchQuery.subscribe(function (newValue) {
        if (newValue !== '' || self.enableFilterAfterSearch) {
          self.filter();
        }
        self.enableFilterAfterSearch = true;
      });

      self.filter = function () {
        self.targetPageNum(1);
        self.retrieveData();
      };

      self.openDefaultFolder = function (vm, e, folderPath) {
        var isLeftButton = (e.which || e.button) === 1;
        if (isLeftButton) {
          if (! (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey)) {
            e.stopPropagation();
            e.preventDefault();
            viewModel.targetPageNum(1);
            viewModel.targetPath("${url('filebrowser.views.view', path='')}?" + folderPath);
            location.hash = '';
            viewModel.retrieveData();
          }
          else {
            window.open("${url('filebrowser.views.view', path='')}?" + folderPath);
          }
        }
      }

      self.openHome = function (vm, e) {
        self.openDefaultFolder(vm, e, 'default_to_home');
      }

      self.openTrash = function (vm, e) {
        self.openDefaultFolder(vm, e, 'default_to_trash');
      }

      self.viewFile = function (file) {
        if (file.type == "dir") {
          // Reset page number so that we don't hit a page that doesn't exist
          self.targetPageNum(1);
          self.enableFilterAfterSearch = false;
          self.searchQuery("");
          self.targetPath("${url('filebrowser.views.view', path='')}" + stripHashes(file.path));
          location.hash = stripHashes(file.path);
        } else {
          location.href = file.url;
        }
      };

      self.editFile = function () {
        location.href = "${url('filebrowser.views.edit', path='')}" + self.selectedFile().path;
      };

      self.downloadFile = function () {
        location.href = "${url('filebrowser.views.download', path='')}" + self.selectedFile().path;
      };

      self.renameFile = function () {
        $("#renameSrcPath").attr("value", self.selectedFile().path);

        $("#renameFileName").text(self.selectedFile().path);

        $("#newNameInput").val(self.selectedFile().name);

        $("#renameForm").attr("action", "/filebrowser/rename?next=${url('filebrowser.views.view', path='')}" + self.currentPath());

        $('#renameForm').ajaxForm({
          dataType:  'json',
          success: function() {
            $("#renameModal").modal('hide');
            self.retrieveData();
          }
        });

        $("#renameModal").modal({
          keyboard:true,
          show:true
        });
      };

      self.move = function (mode, unselectedDrag) {
        var paths = [];

        var isMoveOnSelf = false;
        $(self.selectedFiles()).each(function (index, file) {
          if (file.path == $('#moveDestination').val()){
            isMoveOnSelf = true;
          }
          paths.push(file.path);
        });

        if (paths.length == 0 && typeof unselectedDrag !== 'undefined'){
          paths.push(_dragged.path);
        }

        if (!isMoveOnSelf){
          hiddenFields($("#moveForm"), "src_path", paths);

          $("#moveForm").attr("action", "/filebrowser/move?next=${url('filebrowser.views.view', path='')}" + self.currentPath());

          if (mode === 'nomodal') {
            $.jHueNotify.info('${ _('Items moving to') } "' + $('#moveDestination').val() + '"');
            $("#moveForm").submit();
          } else {
            $("#moveModal").modal({
              keyboard: true,
              show: true
            });

            $('#moveForm').ajaxForm({
              dataType:  'json',
              success: function() {
                $("#moveModal").modal('hide');
                self.retrieveData();
              },
              error: function(xhr){
                $.jHueNotify.error(xhr.responseText);
                resetPrimaryButtonsStatus();
              }
            });

            $("#moveModal").on("shown", function () {
              $("#moveDestination").val('');
              $("#moveNameRequiredAlert").hide();
              $("#moveForm").find("input[name='*dest_path']").removeClass("fieldError");
              $("#moveModal .modal-footer div").show();
              $("#moveHdfsTree").remove();
              $("<div>").attr("id", "moveHdfsTree").appendTo($("#moveModal .modal-body"));
              $("#moveHdfsTree").jHueHdfsTree({
                home: viewModel.isS3() ? "" : "/user/${ user }",
                isS3: viewModel.isS3(),
                initialPath: viewModel.currentPath(),
                onPathChange: function (path) {
                  $("#moveDestination").val((viewModel.isS3() ? "" : (path.indexOf("/") == 0 ? "" : "/")) + path);
                  $("#moveNameRequiredAlert").hide();
                }
              });
            });
          }
        }
        else {
          $.jHueNotify.warn("${ _('You cannot copy a folder into itself.') }");
        }
      };

      self.copy = function () {
        var paths = [];

        $(self.selectedFiles()).each(function (index, file) {
          paths.push(file.path);
        });

        hiddenFields($("#copyForm"), "src_path", paths);

        $("#copyForm").attr("action", "/filebrowser/copy?next=${url('filebrowser.views.view', path='')}" + self.currentPath());

        $("#copyModal").modal({
          keyboard:true,
          show:true
        });

        $('#copyForm').ajaxForm({
          dataType:  'json',
          success: function() {
            $("#copyModal").modal('hide');
            self.retrieveData();
          },
          error: function(xhr){
            $.jHueNotify.error(xhr.responseText);
            resetPrimaryButtonsStatus();
          }
        });

        $("#copyModal").on("shown", function(){
          $("#copyDestination").val('');
          $("#copyNameRequiredAlert").hide();
          $("#copyForm").find("input[name='*dest_path']").removeClass("fieldError");
          $("#copyModal .modal-footer div").show();
          $("#copyHdfsTree").remove();
          $("<div>").attr("id", "copyHdfsTree").appendTo($("#copyModal .modal-body"));
          $("#copyHdfsTree").jHueHdfsTree({
            home: viewModel.isS3() ? "" : "/user/${ user }",
            isS3: viewModel.isS3(),
            initialPath: viewModel.currentPath(),
            onPathChange: function(path){
              $("#copyDestination").val((viewModel.isS3() ? "" : (path.indexOf("/") == 0 ? "" : "/")) + path);
              $("#copyNameRequiredAlert").hide();
            }
          });
        });
      };

      self.changeOwner = function (data, event) {
        if (!self.isCurrentDirSentryManaged()) {
          var paths = [];
          event.preventDefault();
          event.stopPropagation();

          $(self.selectedFiles()).each(function (index, file) {
            paths.push(file.path);
          });

          hiddenFields($("#chownForm"), 'path', paths);

          $("#chownForm").attr("action", "/filebrowser/chown?next=${url('filebrowser.views.view', path='')}" + self.currentPath());

          $("select[name=user]").val(self.selectedFile().stats.user);

          $("#chownForm input[name='group_other']").removeClass("fieldError");
          $("#chownForm input[name='user_other']").removeClass("fieldError");
          $("#chownRequired").hide();

          if ($("select[name=group] option:contains('" + self.selectedFile().stats.group + "')").length > 0) {
            $("select[name=group]").val(self.selectedFile().stats.group);
          } else {
            $("select[name=group]").val("__other__");
            $("input[name=group_other]").val(self.selectedFile().stats.group);
          }

          $("select[name=group]").change();

          $("#changeOwnerModal").modal({
            keyboard: true,
            show: true
          });

          $('#chownForm').ajaxForm({
            dataType:  'json',
            success: function() {
              $("#changeOwnerModal").modal('hide');
              self.retrieveData();
            }
          });
        }
      };

      self.changePermissions = function (data, event) {
        if (!self.isCurrentDirSentryManaged()) {
          var paths = [];

          event.preventDefault();
          event.stopPropagation();

          $(self.selectedFiles()).each(function (index, file) {
            paths.push(file.path);
          });

          hiddenFields($("#chmodForm"), 'path', paths);

          $("#chmodForm").attr("action", "/filebrowser/chmod?next=${url('filebrowser.views.view', path='')}" + self.currentPath());

          $("#changePermissionModal").modal({
            keyboard: true,
            show: true
          });

          $('#chmodForm').ajaxForm({
            dataType:  'json',
            success: function() {
              $("#changePermissionModal").modal('hide');
              self.retrieveData();
            }
          });

          // Initial values for form
          var permissions = ["sticky", "user_read", "user_write", "user_execute", "group_read", "group_write", "group_execute", "other_read", "other_write", "other_execute"].reverse();
          var mode = octal(self.selectedFile().mode) & 01777;

          for (var i = 0; i < permissions.length; i++) {
            if (mode & 1) {
              $("#chmodForm input[name=" + permissions[i] + "]").attr("checked", true);
            } else {
              $("#chmodForm input[name=" + permissions[i] + "]").attr("checked", false);
            }
            mode >>>= 1;
          }
        }
      };

      var deleteSelected = function(skip_trash) {
        var paths = [];

        $(self.selectedFiles()).each(function (index, file) {
          paths.push(file.path);
        });

        hiddenFields($("#deleteForm"), 'path', paths);

        $("#deleteForm").attr("action", "/filebrowser/rmtree" + "?" +
          (skip_trash ? "skip_trash=true&" : "") +
          "next=${url('filebrowser.views.view', path='')}" + self.currentPath());

        $("#deleteModal").modal({
          keyboard:true,
          show:true
        });

        $('#deleteForm').ajaxForm({
          dataType:  'json',
          success: function() {
            $("#deleteModal").modal('hide');
            self.retrieveData();
          }
        });
      };

      self.deleteSelected = function () {
        deleteSelected(true);
      };

      self.trashSelected = function () {
        deleteSelected();
      };

      self.submitSelected = function() {
        % if 'oozie' in apps:
          $.get("${ url('oozie:submit_external_job', application_path='/') }../" + self.selectedFile().path, function (response) {
            $('#submit-wf-modal').html(response);
            $('#submit-wf-modal').modal('show');
          });
        % else:
          $.jHueNotify.warn("${ _('Submitting is not available as the Oozie app is disabled') }");
        % endif
      };

      self.isArchive = function() {
        var fileName = self.selectedFile().name;
        return fileName.endsWith('.zip') || fileName.endsWith('.tar.gz') || fileName.endsWith('.tgz') || fileName.endsWith('.bz2') || fileName.endsWith('.bzip2');
      };

      self.confirmExtractArchive = function() {
        $("#confirmExtractModal").modal({
          keyboard:true,
          show:true
        });
      };

      self.extractSelectedArchive = function() {
        $("#confirmExtractModal").modal("hide");
        $.post("/filebrowser/extract_archive", {
          "archive_name": self.selectedFile().name,
          "upload_path": self.currentPath(),
        }, function (data) {
          if (data.status == 0) {
            var jobId = '';
            if (data.handle) {
              jobId = data.handle.id;
            }
            $.jHueNotify.info("${ _('Oozie job ') }" + jobId + "${_(' submitted for archive extraction.') }");
          } else {
            $(document).trigger("error", data.message);
          }
        }).fail(function (xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        });
      };

      self.createDirectory = function (formElement) {
        $(formElement).attr("action", "/filebrowser/mkdir?next=${url('filebrowser.views.view', path='')}" + self.currentPath());
        if ($.trim($("#newDirectoryNameInput").val()) == "") {
          $("#directoryNameRequiredAlert").show();
          $("#newDirectoryNameInput").addClass("fieldError");
          resetPrimaryButtonsStatus(); //globally available
          return false;
        }

        if (fileExists($("#newDirectoryNameInput").val())) {
          $("#directoryNameExistsAlert").find(".newName").text($("#newDirectoryNameInput").val());
          $("#directoryNameExistsAlert").show();
          $("#newDirectoryNameInput").addClass("fieldError");
          resetPrimaryButtonsStatus(); //globally available
          return false;
        }
        $(formElement).ajaxSubmit({
          dataType:  'json',
          success: function() {
            $("#createDirectoryModal").modal('hide');
            self.retrieveData();
          }
        });
        return false;
      };

      self.createFile = function (formElement) {
        $(formElement).attr("action", "/filebrowser/touch?next=${url('filebrowser.views.view', path='')}" + self.currentPath());
        if ($.trim($("#newFileNameInput").val()) == "") {
          $("#fileNameRequiredAlert").show();
          $("#newFileNameInput").addClass("fieldError");
          resetPrimaryButtonsStatus(); //globally available
          return false;
        }

        if (fileExists($("#newFileNameInput").val())) {
          $("#fileNameExistsAlert").find(".newName").text($("#newFileNameInput").val());
          $("#fileNameExistsAlert").show();
          $("#newFileNameInput").addClass("fieldError");
          resetPrimaryButtonsStatus(); //globally available
          return false;
        }
        $(formElement).ajaxSubmit({
          dataType:  'json',
          success: function() {
            $("#createFileModal").modal('hide');
            self.retrieveData();
          }
        });
        return false;
      };

      self.restoreTrashSelected = function(formElement) {
        var paths = [];

        $(self.selectedFiles()).each(function (index, file) {
          paths.push(file.path);
        });

        hiddenFields($("#restoreTrashForm"), 'path', paths);

        $("#restoreTrashForm").attr("action", "/filebrowser/trash/restore?next=${url('filebrowser.views.view', path='')}" + self.currentPath());

        $("#restoreTrashModal").modal({
          keyboard:true,
          show:true
        });

        $('#restoreTrashForm').ajaxForm({
          dataType:  'json',
          success: function() {
            $("#restoreTrashModal").modal('hide');
            self.retrieveData();
          }
        });
      };

      self.purgeTrash = function(formElement) {
        var paths = [];

        $(self.selectedFiles()).each(function (index, file) {
          paths.push(file.path);
        });

        hiddenFields($("#purgeTrashForm"), 'path', paths);

        $("#purgeTrashForm").attr("action", "/filebrowser/trash/purge?next=${url('filebrowser.views.view', path='')}" + viewModel.homeDir() + "/.Trash");

        $("#purgeTrashModal").modal({
          keyboard:true,
          show:true
        });

        $('#purgeTrashForm').ajaxForm({
          dataType:  'json',
          success: function() {
            $("#purgeTrashModal").modal('hide');
            self.retrieveData();
          }
        });
      };

      self.uploadFile = (function () {
        self.pendingUploads(0);
        var action = "/filebrowser/upload/file";
        var uploader = new qq.FileUploader({
          element: document.getElementById("fileUploader"),
          action: action,
          template: '<div class="qq-uploader" style="margin-left: 10px">' +
          '<div class="qq-upload-drop-area"><span>${_('Drop the files here to upload')}</span></div>' +
          '<div class="qq-upload-button">${_('Select files')}</div> &nbsp; <span class="muted">or drag and drop them here</span>' +
          '<ul class="qq-upload-list qq-upload-files unstyled" style="margin-right: 0;"></ul>' +
          '</div>',
          fileTemplate: '<li><span class="qq-upload-file-extended" style="display:none"></span><span class="qq-upload-spinner hide" style="display:none"></span>' +
          '<div class="progress-row dz-processing">' +
          '<span class="break-word qq-upload-file"></span>' +
          '<div class="pull-right">' +
          '<span class="muted qq-upload-size"></span>&nbsp;&nbsp;' +
          '<a href="#" title="${_('Cancel')}" class="complex-layout"><i class="fa fa-fw fa-times qq-upload-cancel"></i></a>' +
          '<span class="qq-upload-done" style="display:none"><i class="fa fa-fw fa-check muted"></i></span>' +
          '<span class="qq-upload-failed-text">${_('Failed')}</span>' +
          '</div>' +
          '<div class="progress-row-bar" style="width: 0%;"></div>' +
          '</div></li>',
          params: {
            dest: self.currentPath(),
            fileFieldLabel: "hdfs_file"
          },
          onProgress: function (id, fileName, loaded, total) {
            $('.qq-upload-files').find('li').each(function(){
              var listItem = $(this);
              if (listItem.find('.qq-upload-file-extended').text() == fileName){
                listItem.find('.progress-row-bar').css('width', (loaded/total)*100 + '%');
              }
            });
          },
          onComplete: function (id, fileName, response) {
            self.pendingUploads(self.pendingUploads() - 1);
            if (response.status != 0) {
              $(document).trigger('error', "${ _('Error: ') }" + response.data);
            }
            else {
              $(document).trigger('info', response.path + "${ _(' uploaded successfully.') }");
              self.lastUploadBatch.push(response.path);
            }
            if (self.pendingUploads() == 0) {
              $('#uploadFileModal').modal('hide');
              self.retrieveData();
            }
          },
          onSubmit: function (id, fileName, responseJSON) {
            self.pendingUploads(self.pendingUploads() + 1);
          },
          onCancel: function (id, fileName) {
            self.pendingUploads(self.pendingUploads() - 1);
          },
          debug: false
        });

        $("#fileUploader").on('fb:updatePath', function (e, options) {
          uploader.setParams({
            dest: options.dest,
            fileFieldLabel: "hdfs_file"
          });
        });

        return function () {
          $("#uploadFileModal").modal({
            show: true
          });
        };
      })();

      self.uploadArchive = (function () {
        self.pendingUploads(0);
        var uploader = new qq.FileUploader({
          element: document.getElementById("archiveUploader"),
          action: "/filebrowser/upload/archive",
          template: '<div class="qq-uploader" style="margin-left: 10px">' +
          '<div class="qq-upload-drop-area"><span>${_('Drop the archives here to upload and extract them')}</span></div>' +
          '<div class="qq-upload-button">${_('Select ZIP, TGZ or BZ2 files')}</div> &nbsp; <span class="muted">or drag and drop them here</span>' +
          '<ul class="qq-upload-list qq-upload-archives unstyled" style="margin-right: 0;"></ul>' +
          '</div>',
          fileTemplate: '<li><span class="qq-upload-file-extended" style="display:none"></span><span class="qq-upload-spinner hide" style="display:none"></span>' +
          '<div class="progress-row dz-processing">' +
          '<span class="break-word qq-upload-file"></span>' +
          '<div class="pull-right">' +
          '<span class="muted qq-upload-size"></span>&nbsp;&nbsp;' +
          '<a href="#" title="${_('Cancel')}" class="complex-layout"><i class="fa fa-fw fa-times qq-upload-cancel"></i></a>' +
          '<span class="qq-upload-done" style="display:none"><i class="fa fa-fw fa-check muted"></i></span>' +
          '<span class="qq-upload-failed-text">${_('Failed')}</span>' +
          '</div>' +
          '<div class="progress-row-bar" style="width: 0%;"></div>' +
          '</div></li>',
          params: {
            dest: self.currentPath(),
            fileFieldLabel: "archive"
          },
          onProgress: function (id, fileName, loaded, total) {
            $('.qq-upload-archives').find('li').each(function(){
              var listItem = $(this);
              if (listItem.find('.qq-upload-file-extended').text() == fileName){
                listItem.find('.progress-row-bar').css('width', (loaded/total)*100 + '%');
              }
            });
          },
          onComplete: function (id, fileName, response) {
            self.pendingUploads(self.pendingUploads() - 1);
            if (response.status != 0) {
              $(document).trigger('error', "${ _('Error: ') }" + response.data);
            }
            else {
              $(document).trigger('info', response.path + "${ _(' uploaded successfully.') }");
              self.lastUploadBatch.push(response.path);
            }
            if (self.pendingUploads() == 0) {
              $('#uploadArchiveModal').modal('hide');
              self.retrieveData();
            }
          },
          onSubmit: function (id, fileName, responseJSON) {
            self.pendingUploads(self.pendingUploads() + 1);
          },
          onCancel: function (id, fileName) {
            self.pendingUploads(self.pendingUploads() - 1);
          },
          debug: false
        });

        $("#archiveUploader").on('fb:updatePath', function (e, options) {
          uploader.setParams({
            dest: options.dest,
            fileFieldLabel: "archive"
          });
        });

        return function () {
          $("#uploadArchiveModal").modal({
            show: true
          });
        };
      })();

      // Place all values into hidden fields under parent element.
      // Looks for managed hidden fields and handles sizing appropriately.
      var hiddenFields = function (parentEl, name, values) {
        if (!(parentEl instanceof jQuery)){
          parentEl = $(parentEl);
        }
        parentEl.find("input.hidden-field").remove();

        $(values).each(function (index, value) {
          var field = $("<input type='hidden' />");
          field.attr("name", name);
          field.attr("class", "hidden-field")
          field.val(value);
          parentEl.append(field);
        });
      };

      var octal = function (strInt) {
        return parseInt("0" + strInt, 8);
      };
    };

    // hide the context menu based on specific events
    var hideContextMenu = function () {
      var cm = $('.context-menu');

      if (cm.is(':visible')) {
        cm.css({ display: 'none' });
      }
    };

    var viewModel = new FileBrowserModel([], null, [], "/");
    ko.applyBindings(viewModel);

    $(document).ready(function () {
      $('.historyLink').on('click', function (e) {
        if(getHistory().length > 0) {
          showHistory();
        } else {
          e.preventDefault();
          e.stopPropagation();
        }
      });

      // hide context menu
      $('body').on('click', function (e) {
        hideContextMenu();
      });

      $('body').on('contextmenu', function (e) {
        if ($.inArray(e.toElement, $('.datatables *')) === -1) {
          hideContextMenu();
        }
      });

      $('body').on('contextmenu', '.context-menu', function (e) {
        hideContextMenu();
      });

      // Drag and drop uploads from anywhere on filebrowser screen
      if (window.FileReader) {
        var showHoverMsg = function (msg) {
          $('.hoverText').html(msg);
          $('.hoverMsg').removeClass('hide');
        };

        var hideHoverMsg = function () {
          $('.hoverMsg').addClass('hide');
        };

        var _isDraggingOverText = false,
          // determine if the item dragged originated outside DOM
          _isExternalFile = true;

        $('body').on('dragstart', function (e) {
          // External files being dragged into the DOM won't have a dragstart event
          _isExternalFile = false;
        });

        $('body').on('dragend', function (e) {
          _isExternalFile = true;
        });

        $('body').on('dragenter', function (e) {
          e.preventDefault();

          if (_isExternalFile && !($("#uploadFileModal").is(":visible")) && !($("#uploadArchiveModal").is(":visible")) && (!viewModel.isS3() || (viewModel.isS3() && !viewModel.isS3Root()))) {
            showHoverMsg("${_('Drop files here to upload')}");
          }
        });

        $('.hoverText').on('dragenter', function (e) {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          _isDraggingOverText = true;
        });

        $('.hoverText').on('dragleave', function (e) {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          _isDraggingOverText = false;
          _isExternalFile = true;
        });

        $('.hoverMsg').on('dragleave', function (e) {
          if (!_isDraggingOverText) {
            hideHoverMsg();
          }
        });

        $(document).on('currPathLoaded', function (e, ops) {
          try {
            _dropzone.destroy();
          }
          catch (exc) {
          }
          var options = {
            url: '/filebrowser/upload/file?dest=' + ops.path,
            paramName: 'hdfs_file',
            params: {
              dest: ops.path
            },
            autoDiscover: false,
            maxFilesize: 5000000,
            previewsContainer: '#progressStatusContent',
            previewTemplate: '<div class="progress-row">' +
                '<span class="break-word" data-dz-name></span>' +
                '<div class="pull-right">' +
                '<span class="muted" data-dz-size></span>&nbsp;&nbsp;' +
                '<span data-dz-remove><a href="javascript:undefined;" title="${ _('Cancel upload') }"><i class="fa fa-fw fa-times"></i></a></span>' +
                '<span style="display: none" data-dz-uploaded><i class="fa fa-fw fa-check muted"></i></span>' +
                '</div>' +
                '<div class="progress-row-bar" data-dz-uploadprogress></div>' +
                '</div>',
            drop: function (e) {
              $('.hoverMsg').addClass('hide');

              // Ensure dropped item was a file
              if (e.dataTransfer.files.length > 0) {
                $('#progressStatus').removeClass('hide');
                $('#progressStatusBar').removeClass('hide');
                $('#progressStatusBar div').css("width", "0");
              }
            },
            uploadprogress: function (file, progress) {
              $("[data-dz-name]").each(function (cnt, item) {
                if ($(item).text() === file.name) {
                  $(item).parents(".progress-row").find("[data-dz-uploadprogress]").width(progress.toFixed() + "%");
                  if (progress.toFixed() === "100"){
                    $(item).parents(".progress-row").find("[data-dz-remove]").hide();
                    $(item).parents(".progress-row").find("[data-dz-uploaded]").show();
                  }
                }
              });
            },
            totaluploadprogress: function (progress) {
              $('#progressStatusBar div').width(progress.toFixed() + "%");
            },
            canceled: function () {
              $.jHueNotify.info("${_('Upload has been canceled')}");
            },
            complete: function (data) {
              if (data.xhr.response != '') {
                var response = JSON.parse(data.xhr.response);
                if (response && response.status != null) {
                  if (response.status != 0) {
                    $(document).trigger('error', response.data);
                  }
                  else {
                    $(document).trigger('info', response.path + "${ _(' uploaded successfully.') }");
                    viewModel.lastUploadBatch.push(response.path);
                  }
                }
              }
            }
          };
          if (ops.path.toLowerCase() !== 's3a://') {
            _dropzone = new Dropzone(document.body, options);

            _dropzone.on('queuecomplete', function () {
              setTimeout(function () {
                    $('#progressStatus').addClass('hide');
                    $('#progressStatusBar').addClass('hide');
                    $('#progressStatusBar div').css("width", "0");
                    viewModel.retrieveData();
                  },
                  2500);
            });
          }
        });
      }

      $("#chownForm select[name='user']").change(function () {
        if ($(this).val() == "__other__") {
          $("input[name='user_other']").show();
        } else {
          $("input[name='user_other']").hide();
        }
      });

      $("#chownForm select[name='group']").change(function () {
        if ($(this).val() == "__other__") {
          $("input[name='group_other']").show();
        } else {
          $("input[name='group_other']").hide();
        }
      });

      $("#chownForm").submit(function () {
        if ($("#chownForm select[name='user']").val() == null) {
          $("#chownRequired").find(".label").text("${_('User is required.')}");
          $("#chownRequired").show();
          resetPrimaryButtonsStatus(); //globally available
          return false;
        } else if ($("#chownForm select[name='group']").val() == null) {
          $("#chownRequired").find(".label").text("${_('Group is required.')}");
          $("#chownRequired").show();
          resetPrimaryButtonsStatus(); //globally available
          return false;
        } else {
          if ($("#chownForm select[name='group']").val() == "__other__" && $("input[name='group_other']").val() == "") {
            $("#chownRequired").find(".label").text("${_('Specify another group.')}");
            $("#chownForm input[name='group_other']").addClass("fieldError");
            $("#chownRequired").show();
            resetPrimaryButtonsStatus(); //globally available
            return false;
          }

          if ($("#chownForm select[name='user']").val() == "__other__" && $("input[name='user_other']").val() == "") {
            $("#chownRequired").find(".label").text("${_('Specify another user.')}");
            $("#chownForm input[name='user_other']").addClass("fieldError");
            $("#chownRequired").show();
            return false;
            resetPrimaryButtonsStatus(); //globally available
          }
          return true;
        }
      });

      // Modal file chooser
      // The file chooser should be at least 2 levels deeper than the modal container
      $(".fileChooserBtn").on('click', function (e) {
        e.preventDefault();

        var _destination = $(this).attr("data-filechooser-destination");
        var fileChooser = $(this).parent().parent().find(".fileChooserModal");

        fileChooser.jHueFileChooser({
          initialPath:$("input[name='" + _destination + "']").val(),
          onFolderChange:function (folderPath) {
            $("input[name='" + _destination + "']").val(folderPath);
          },
          onFolderChoose:function (folderPath) {
            $("input[name='" + _destination + "']").val(folderPath);
            fileChooser.slideUp();
          },
          selectFolder:true,
          createFolder:true,
          uploadFile:false
        });
        fileChooser.slideDown();
      });

      $("#renameForm").submit(function () {
        if ($("#newNameInput").val() == "") {
          $("#renameNameRequiredAlert").show();
          $("#newNameInput").addClass("fieldError");
          resetPrimaryButtonsStatus(); //globally available
          return false;
        }

        if (fileExists($("#newNameInput").val())) {
          $("#renameNameExistsAlert").find(".newName").text($("#newNameInput").val());
          $("#renameNameExistsAlert").show();
          $("#newNameInput").addClass("fieldError");
          resetPrimaryButtonsStatus(); //globally available
          return false;
        }
        return true;
      });

      $("#newNameInput").focus(function () {
        $("#renameNameRequiredAlert").hide();
        $("#renameNameExistsAlert").hide();
        $("#newNameInput").removeClass("fieldError");
      });

      $("#moveForm").on("submit", function () {
        if ($.trim($("#moveDestination").val()) == "") {
          $("#moveNameRequiredAlert").show();
          $("#moveForm").find("input[name='*dest_path']").addClass("fieldError");
          resetPrimaryButtonsStatus(); //globally available
          return false;
        }
        return true;
      });

      $("#moveForm").bind("keypress", function(e) {
        if (e.keyCode == 13) {
           return false;
        }
       });

      huePubSub.subscribe('update.autocompleters', function(){
        $("#moveDestination").jHueHdfsAutocomplete({
          showOnFocus: true,
          skipKeydownEvents: true,
          onEnter: function (el) {
            $("#jHueHdfsAutocomplete").hide();
          },
          isS3: viewModel.isS3()
        });
        $("#copyDestination").jHueHdfsAutocomplete({
          showOnFocus: true,
          skipKeydownEvents: true,
          onEnter: function (el) {
            $("#jHueHdfsAutocomplete").hide();
          },
          isS3: viewModel.isS3()
        });
      });

      huePubSub.subscribe('update.history', function(){
        if (getHistory().length == 0) {
          $('.history').addClass('no-history');
        }
        else {
          $('.history').removeClass('no-history');
        }
      });


      $("#copyForm").on("submit", function () {
        if ($.trim($("#copyDestination").val()) == "") {
          $("#copyNameRequiredAlert").show();
          $("#copyForm").find("input[name='*dest_path']").addClass("fieldError");
          resetPrimaryButtonsStatus(); //globally available
          return false;
        }
        return true;
      });

      $("#copyForm").bind("keypress", function(e) {
        if (e.keyCode == 13) {
           return false;
        }
       });

      huePubSub.publish('update.autocompleters');

      $(".create-directory-link").click(function () {
        $("#newDirectoryNameInput").val('');
        $("#createDirectoryModal").modal({
          keyboard:true,
          show:true
        });
      });

      $(".create-file-link").click(function () {
        $("#newFileNameInput").val('');
        $("#createFileModal").modal({
          keyboard:true,
          show:true
        });
      });

      $("#newDirectoryNameInput").focus(function () {
        $("#newDirectoryNameInput").removeClass("fieldError");
        $("#directoryNameRequiredAlert").hide();
        $("#directoryNameExistsAlert").hide();
      });

      $("#newFileNameInput").focus(function () {
        $("#newFileNameInput").removeClass("fieldError");
        $("#fileNameRequiredAlert").hide();
        $("#fileNameExistsAlert").hide();
      });

      $(".pathChooser").click(function () {
        var self = this;
        $("#fileChooserRename").jHueFileChooser({
          initialPath:$(self).val(),
          onFileChoose:function (filePath) {
            $(self).val(filePath);
          },
          onFolderChange:function (folderPath) {
            $(self).val(folderPath);
          },
          createFolder:false,
          uploadFile:false
        });
        $("#fileChooserRename").slideDown();
      });

      $("*[rel='tooltip']").tooltip({ placement:"bottom" });

      if (location.hash != null && location.hash.length > 1) {
        var targetPath = "";
        var hash = window.location.hash.substring(1);
        if (hash.search(/(<([^>]+)>)/ig) > -1) {
          hash = encodeURI(hash);
        }
        if (hash != null && hash != "") {
          targetPath = "${url('filebrowser.views.view', path='')}";
          if (hash.indexOf("!!") != 0) {
            targetPath += stripHashes(hash);
          }
          else {
            targetPath = viewModel.targetPath() + hash;
          }
          if (targetPath.indexOf("!!") > -1) {
            viewModel.targetPageNum(targetPath.substring(targetPath.indexOf("!!") + 2) * 1)
            targetPath = targetPath.substring(0, targetPath.indexOf("!!"));
          }
          else {
            viewModel.targetPageNum(1)
          }
        }
        if (window.location.href.indexOf("#") == -1) {
          viewModel.targetPageNum(1);
          targetPath = "${current_request_path | n,unicode }";
        }
        if (targetPath != "") {
          viewModel.targetPath(targetPath);
        }
      }

      viewModel.retrieveData();

      $("#editBreadcrumb").click(function (e) {
        if ($(e.target).is('ul')){
          $(this).hide();
          $(".hueBreadcrumb").hide();
          $("#hueBreadcrumbText").show().focus();
        }
      });

      $("#hueBreadcrumbText").jHueHdfsAutocomplete({
        home: "/user/${ user }/",
        skipKeydownEvents: true,
        onEnter: function (el) {
          viewModel.targetPath("${url('filebrowser.views.view', path='')}" + stripHashes(el.val()));
          viewModel.getStats(function (data) {
            if (data.type != null && data.type == "file") {
              location.href = data.url;
              return false;
            } else {
              location.hash = stripHashes(el.val());
            }
            $("#jHueHdfsAutocomplete").hide();
          });
        },
        onBlur: function() {
          $("#hueBreadcrumbText").hide();
          $(".hueBreadcrumb").show();
          $("#editBreadcrumb").show();
        },
        smartTooltip: "${_('Did you know? You can use the tab key or CTRL + Space to autocomplete file and folder names')}"
      });

      $.ajaxSetup({
        error:function (x, e) {
          if (x.status == 500 && x.responseText.indexOf("jobbrowser") == -1) {
            $(document).trigger("error", "${_('There was a problem with your request.')}");
            $("#hueBreadcrumbText").blur();
          }
        }
      });

      $(window).bind("hashchange", function () {
        var targetPath = "";
        var hash = window.location.hash.substring(1);
        if (hash.search(/(<([^>]+)>)/ig) > -1) {
          hash = encodeURI(hash);
        }

        if (hash != null && hash != "") {
          addPathToHistory(hash);

          targetPath = "${url('filebrowser.views.view', path='')}";
          if (hash.indexOf("!!") != 0) {
            targetPath += stripHashes(hash);
          }
          else {
            targetPath = viewModel.targetPath() + hash;
          }
          if (targetPath.indexOf("!!") > -1) {
            viewModel.targetPageNum(targetPath.substring(targetPath.indexOf("!!") + 2) * 1)
            targetPath = targetPath.substring(0, targetPath.indexOf("!!"));
          }
          else {
            viewModel.targetPageNum(1)
          }
        }
        if (window.location.href.indexOf("#") == -1) {
          viewModel.targetPageNum(1);
          targetPath = "${current_request_path | n,unicode }";
        }
        if (targetPath != "") {
          viewModel.targetPath(targetPath);
          viewModel.retrieveData();
        }
      });

      $(".actionbar").data("originalWidth", $(".actionbar").width());

      $(".actionbarGhost").height($(".actionbar").outerHeight());

      resetActionbar();

      $(window).scroll(function () {
        if ($(window).scrollTop() > 20) {
          $(".actionbar").width($(".actionbar").data("originalWidth"));
          $(".actionbar").css("position", "fixed").css("top", "73px").css("zIndex", "1001");
          $(".actionbarGhost").removeClass("hide");
        } else {
          resetActionbar();
        }
      });

      $("#uploadFileModal").on("shown", function () {
        if (typeof _dropzone != "undefined") {
          _dropzone.disable();
        }
      });
      $("#uploadFileModal").on("hidden", function () {
        if (typeof _dropzone != "undefined") {
          _dropzone.enable();
        }
        $(".qq-upload-list").empty();
        $(".qq-upload-drop-area").hide();
      });
      $("#uploadArchiveModal").on("shown", function () {
        if (typeof _dropzone != "undefined") {
          _dropzone.disable();
        }
      });
      $("#uploadArchiveModal").on("hidden", function () {
        if (typeof _dropzone != "undefined") {
          _dropzone.enable();
        }
        $(".qq-upload-list").empty();
        $(".qq-upload-drop-area").hide();
      });
    });
  </script>
</%def>
