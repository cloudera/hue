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
import sys

from django.template.defaultfilters import urlencode, stringformat, filesizeformat, date, time, escape
from desktop.lib.django_util import reverse_with_get, extract_field_data
from django.utils.encoding import smart_str

from filebrowser.conf import ENABLE_EXTRACT_UPLOADED_ARCHIVE, FILE_UPLOAD_CHUNK_SIZE, CONCURRENT_MAX_CONNECTIONS, MAX_FILE_SIZE_UPLOAD_LIMIT

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
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

  <table id="fileBrowserTable" class="table table-condensed table-huedatatable tablescroller-disable" data-bind="style: {'opacity': isLoading() ? '.5': '1'}">
    <thead>
      <tr>
        <th class="sorting_disabled" width="1%"><div data-bind="click: selectAll, css: { 'hue-checkbox': true, 'fa': true, 'fa-check': allSelected}" class="select-all"></div></th>
        <th class="sortable sorting" data-sort="type" width="1%" data-bind="click: sort">&nbsp;</th>
        <th class="sortable sorting_asc" data-sort="name" data-bind="click: sort">${_('Name')}</th>
        <th class="sortable sorting" data-sort="size" width="10%" data-bind="click: sort">${_('Size')}</th>
        <th class="sortable sorting" data-sort="user" width="10%" data-bind="click: sort">${_('User')}</th>
        <th class="sortable sorting" data-sort="group" width="10%" data-bind="click: sort">${_('Group')}</th>
        <th class="sorting_disabled" width="10%">${_('Permissions')}</th>
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
    <div class="pull-right">
        <div class="form-inline pagination-input-form inline">
          <span>${_('Page')}</span>
          <input type="text" data-bind="value: page().number, valueUpdate: 'afterkeydown', event: { change: skipTo }" class="pagination-input" />
          <input type="hidden" id="current_page" data-bind="value: page().number" />
          ${_('of')} <span data-bind="text: page().num_pages"></span>
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
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Extract Archive') }</h2>
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
      <input type="submit" value="${_('Yes')}" class="btn btn-primary" data-bind="click: extractSelectedArchive"/>
    </div>
    <!-- /ko -->
  </div>

  <!-- compress modal -->
  <div id="confirmCompressModal" class="modal hide fade">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Compress Files') }</h2>
    </div>
    <!-- ko if: selectedFiles -->
    <div class="modal-body">
      <div class="form-inline">
        <label>${_('Archive Name')} <input data-bind="textInput: compressArchiveName" type="text" class="margin-left-5 input-xlarge"></label>
        <p class="margin-top-20">${_('Start a task to compress the selected file(s) and/or folder(s)')}</p>
        <ul data-bind="foreach: selectedFiles()">
          <li>
            <i data-bind="css: { 'fa fa-fw muted': true, 'fa-file-o': type == 'file', 'fa-folder-o': type != 'file' }"></i>
            <span data-bind="text: $data.name"> </span>
          </li>
        </ul>
      </div>
    </div>
    <div class="modal-footer">
      <a class="btn" data-dismiss="modal">${_('Cancel')}</a>
      <input type="submit" value="${_('Compress')}" class="btn btn-primary" data-bind="click: archiveOverrideWarning, enable: compressArchiveName().length > 0"/>
    </div>
    <!-- /ko -->
  </div>

  <!-- compress warning modal -->
  <div id="compressWarningModal" class="modal hide fade">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Are you sure you want to override the existing archive?') }</h2>
    </div>
    <!-- ko if: compressArchiveName -->
    <div class="modal-body">
      <ul>
        <li>
          <span data-bind="text: compressArchiveName"> </span>
        </li>
      </ul>
    </div>
    <div class="modal-footer">
      <a class="btn" data-dismiss="modal" data-bind="click: confirmCompressFiles">${_('No')}</a>
      <input type="submit" value="${_('Yes')}" class="btn btn-danger" data-bind="click: compressSelectedFiles"/>
    </div>
    <!-- /ko -->
  </div>

  <!-- delete modal -->
  <div id="deleteModal" class="modal hide fade">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Confirm Delete') }</h2>
    </div>
    <div class="modal-body">
      <!-- ko if: (isS3() && isS3Root()) || (isGS() && isGSRoot()) -->
      <p>${_('Are you sure you want to delete these buckets?')}</p>
      <p class="muted">${_('Deleting a bucket will delete all of its contents and release the bucket name to be reserved by others.')}</p>
      <!-- /ko -->
      <!-- ko ifnot: (isS3() && isS3Root()) && (isGS() && isGSRoot()) -->
      <!-- ko ifnot: $root.skipTrash -->
      <p>${_('Are you sure you want to delete these files?')}</p>
      <!-- /ko -->
      <!-- ko if: $root.skipTrash -->
      <p>${_('Are you sure you want to permanently delete these files?')}</p>
      <!-- /ko -->
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
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Confirm Restore') }</h2>
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
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${ _('Confirm empty trash') }</h2>
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
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${_('Renaming:')} <span id="renameFileName">file name</span></h2>
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
        <input id="renameSrcPath" type="hidden" name="src_path">
        <a class="btn" data-dismiss="modal">${_('Cancel')}</a>
        <input type="submit" value="${_('Rename')}" class="btn btn-primary" />
      </div>
    </div>
  </form>

  <!-- set replication factor modal -->
  <form id="setReplicationFactorForm" action="/filebrowser/set_replication?next=${current_request_path | n,unicode }"  method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix">
    ${ csrf_token(request) | n,unicode }
    <div id="setReplicationModal" class="modal hide fade">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${_('Setting replication factor for :')} <span id="setReplFileName">file name</span></h2>
      </div>
      <div class="modal-body">
        <label>${_('Replication factor')} <input id="newRepFactorInput" name="replication_factor" value="" type="number" class="input-mini"/></label>
      </div>
      <div class="modal-footer">
        <div id="replicationFactorRequiredAlert" class="hide" style="position: absolute; left: 10px;">
          <span class="label label-important">${_('Replication factor is required.')}</span>
        </div>
        <input id="SrcPath" type="hidden" name="src_path">
        <a class="btn" data-dismiss="modal">${_('Cancel')}</a>
        <input type="submit" value="${_('Submit')}" class="btn btn-primary" />
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
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${_('Change Owner/Group')}</h2>
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
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${_('Change Permissions')}</h2>
      </div>
      <div class="modal-body table-margin">
        <table class="table table-condensed">
          <thead>
            <tr>
              <th>&nbsp;</th>
              <th class="center">${_('User')}</th>
              <th class="center">${_('Group')}</th>
              <th class="center">${_('Other')}</th>
              <th class="center">&nbsp;</th>
              <th width="120">&nbsp;</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>${_('Read')}</strong></td>
              <td class="center"><input type="checkbox" name="user_read"></td>
              <td class="center"><input type="checkbox" name="group_read"></td>
              <td class="center"><input type="checkbox" name="other_read"></td>
              <td colspan="2">&nbsp;</td>
            </tr>
            <tr>
              <td><strong>${_('Write')}</strong></td>
              <td class="center"><input type="checkbox" name="user_write"></td>
              <td class="center"><input type="checkbox" name="group_write"></td>
              <td class="center"><input type="checkbox" name="other_write"></td>
              <td colspan="2">&nbsp;</td>
            </tr>
            <tr>
              <td><strong>${_('Execute')}</strong></td>
              <td class="center"><input type="checkbox" name="user_execute"></td>
              <td class="center"><input type="checkbox" name="group_execute"></td>
              <td class="center"><input type="checkbox" name="other_execute"></td>
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
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${_('Move to')}</h2>
      </div>
      <div class="modal-body" style="max-height: 400px; height: 340px; overflow-x:hidden">
        <div id="moveFilechooser"></div>
      </div>
      <div class="modal-footer">
        <div>
          <input type="text" class="input-xlarge disable-autofocus" value="" name="dest_path" id="moveDestination" placeholder="${_('Select a folder or paste a path...')}" />
          <span id="moveNameRequiredAlert" class="hide label label-important">${_('Required')}</span>
        </div>
        <a class="btn" onclick="$('#moveModal').modal('hide');">${_('Cancel')}</a>
        <input data-bind="enable: $root.enableMoveButton()" class="btn btn-primary" type="submit" value="${_('Move')}"/>
      </div>
    </div>
  </form>

  <!-- copy modal -->
  <form id="copyForm" action="/filebrowser/copy" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix">
    ${ csrf_token(request) | n,unicode }
    <div id="copyModal" class="modal hide fade">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${_('Copy to')}</h2>
      </div>
      <div class="modal-body" style="max-height: 400px; height: 340px; overflow-x:hidden">
        <div id="copyFilechooser"></div>
      </div>
      <div class="modal-footer">
        <div>
          <input type="text" class="input-xlarge disable-autofocus" value="" name="dest_path" id="copyDestination" placeholder="${_('Select a folder or paste a path...')}" />
          <span id="copyNameRequiredAlert" class="hide label label-important">${_('Required')}</span>
        </div>
        <a class="btn" onclick="$('#copyModal').modal('hide');">${_('Cancel')}</a>
        <input data-bind="enable: $root.enableCopyButton()" class="btn btn-primary" type="submit" value="${_('Copy')}"/>
      </div>
    </div>
  </form>

  <!-- upload file modal -->
  <div id="uploadFileModal" class="modal hide fade">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${_('Upload to')} <span data-bind="text: currentPath"></span></h2>
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

  <!-- new directory modal -->
  <form id="createDirectoryForm" data-bind="submit: createDirectory" method="POST" enctype="multipart/form-data" class="form-inline form-padding-fix">
    ${ csrf_token(request) | n,unicode }
    <div id="createDirectoryModal" class="modal hide fade">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <!-- ko if: (!isS3() && !isGS() && !isABFS() && !isOFS()) || (isS3() && !isS3Root()) || (isGS() && !isGSRoot()) || (isABFS() && !isABFSRoot()) || (isOFS() && !isOFSServiceID() && !isOFSVol())  -->
        <h2 class="modal-title">${_('Create Directory')}</h2>
        <!-- /ko -->
        <!-- ko if: (isS3() && isS3Root()) || (isGS() && isGSRoot()) || (isOFS() && isOFSVol()) -->
        <h2 class="modal-title">${_('Create Bucket')}</h2>
        <!-- /ko -->
        <!-- ko if: isABFS() && isABFSRoot() -->
        <h2 class="modal-title">${_('Create File System')}</h2>
        <!-- /ko -->
        <!-- ko if: isOFS() && isOFSServiceID() -->
        <h2 class="modal-title">${_('Create Volume')}</h2>
        <!-- /ko -->
      </div>
      <div class="modal-body">
        <label>
          <!-- ko if: (!isS3() && !isGS() && !isABFS() && !isOFS()) || (isS3() && !isS3Root()) || (isGS() && !isGSRoot()) || (isABFS() && !isABFSRoot()) || (isOFS() && !isOFSServiceID() && !isOFSVol()) -->
          ${_('Directory Name')}
          <!-- /ko -->
          <!-- ko if: (isS3() && isS3Root()) || (isGS() && isGSRoot()) || (isOFS() && isOFSVol()) -->
          ${_('Bucket Name')}
          <!-- /ko -->
          <!-- ko if: isABFS() && isABFSRoot() -->
          ${_('File System Name')}
          <!-- /ko -->
          <!-- ko if: isOFS() && isOFSServiceID() -->
          ${_('Volume Name')}
          <!-- /ko -->
          <input id="newDirectoryNameInput" name="name" value="" type="text" class="input-xlarge"/></label>
          <input type="hidden" name="path" data-bind="value: currentPath"/>
      </div>
      <div class="modal-footer">
        <div id="directoryNameRequiredAlert" class="hide" style="position: absolute; left: 10px;">
          <span class="label label-important">${_('Directory name is required.')}</span>
        </div>
        <div id="directoryNameExistsAlert" class="hide" style="position: absolute; left: 10px;">
          <span class="label label-important"><span class="newName"></span> ${_('already exists.')}</span>
        </div>
        <div id="smallFileSystemNameAlert" class="hide" style="position: absolute; left: 10px;">
          <span class="label label-important"><span class="newName"></span> ${_('File system requires namesize to be 3 or more characters')}</span>
        </div>
        <div id="volumeBucketNameAlert" class="hide" style="position: absolute; left: 10px;">
          <span class="label label-important"><span class="newName"></span> ${_('Volume and Bucket name should be 3 to 63 characters.')}</span>
        </div>
        <div id="upperCaseVolumeBucketNameAlert" class="hide" style="position: absolute; left: 10px;">
          <span class="label label-important"><span class="newName"></span> ${_('Upper case characters are not supported for Volume and Bucket names.')}</span>
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
          <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
          <h2 class="modal-title">${_('Create File')}</h2>
        </div>
        <div class="modal-body">
          <label>${_('File Name')} <input id="newFileNameInput" name="name" value="" type="text" class="input-xlarge"/></label>
          <input type="hidden" name="path" data-bind="value: currentPath"/>
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
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <!-- ko if: selectedFile -->
      <h2 class="modal-title" style="word-break: break-all">${_('Summary for')} <span data-bind="text: selectedFile().path"></span></h2>
      <!--/ko -->
    </div>
    <div class="modal-body">
      <div data-bind="visible: isLoadingSummary"><i class="fa fa-spin fa-spinner fa-2x fa-fw" style="color: #CCC"></i></div>
      <table class="table table-condensed" data-bind="visible: !isLoadingSummary()">
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
          <th>${ _('Replication factor') }</th>
          <td data-bind="text: contentSummary().replication()"></td>
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
    <li data-bind="visible: (!isS3() && !isGS() && !isABFS() && !isOFS()) || (isS3() && !isS3Root()) || (isGS() && !isGSRoot()) || (isABFS() && !isABFSRoot()) || (isOFS() && !isOFSServiceID() && !isOFSVol()), css: {'disabled': $root.selectedFiles().length != 1 || isCurrentDirSelected().length > 0}">
    <a href="javascript: void(0)" title="${_('Rename')}" data-bind="click: ($root.selectedFiles().length == 1 && isCurrentDirSelected().length == 0) ? $root.renameFile: void(0)"><i class="fa fa-fw fa-font"></i>
    ${_('Rename')}</a></li>
    <li data-bind="visible: (!isS3() && !isGS() &&  !isABFS() && !isOFS()) || (isS3() && !isS3Root()) || (isGS() && !isGSRoot()) || (isABFS() && !isABFSRoot()) || (isOFS() && !isOFSServiceID() && !isOFSVol()), css: {'disabled': $root.selectedFiles().length == 0 || isCurrentDirSelected().length > 0}">
    <a href="javascript: void(0)" title="${_('Move')}" data-bind="click: ( $root.selectedFiles().length > 0 && isCurrentDirSelected().length == 0) ? $root.move: void(0)"><i class="fa fa-fw fa-random"></i> ${_('Move')}</a></li>
    <li data-bind="visible: (!isS3() && !isGS() && !isABFS() && !isOFS()) || (isS3() && !isS3Root()) || (isGS() && !isGSRoot()) || (isABFS() && !isABFSRoot()) || (isOFS() && !isOFSServiceID() && !isOFSVol()), css: {'disabled': $root.selectedFiles().length == 0 || isCurrentDirSelected().length > 0}">
    <a href="javascript: void(0)" title="${_('Copy')}" data-bind="click: ($root.selectedFiles().length > 0 && isCurrentDirSelected().length == 0) ? $root.copy: void(0)"><i class="fa fa-fw fa-files-o"></i> ${_('Copy')}</a></li>
    % if show_download_button:
    <li data-bind="css: {'disabled': $root.inTrash() || $root.selectedFiles().length != 1 || selectedFile().type != 'file'}">
    <a href="javascript: void(0)" title="${_('Download')}" data-bind="click: (!$root.inTrash() && $root.selectedFiles().length == 1 && selectedFile().type == 'file') ? $root.downloadFile: void(0)">
    <i class="fa fa-fw fa-arrow-circle-o-down"></i> ${_('Download')}</a></li>
    % endif
    <li class="divider" data-bind="visible: isPermissionEnabled()"></li>
    % if is_fs_superuser:
    <li data-bind="css: {'disabled': $root.isCurrentDirSentryManaged || selectedSentryFiles().length > 0 }, visible: isPermissionEnabled()">
      <a href="javascript: void(0)" data-bind="visible: !$root.inTrash(), click: $root.changeOwner, enable: $root.selectedFiles().length > 0">
        <i class="fa fa-fw fa-user"></i> ${_('Change owner / group')}
      </a>
    </li>
    % endif
    <li data-bind="css: {'disabled': $root.isCurrentDirSentryManaged() || selectedSentryFiles().length > 0 }, visible: isPermissionEnabled()">
      <a href="javascript: void(0)" data-bind="visible: !$root.inTrash(), click: $root.changePermissions, enable: $root.selectedFiles().length > 0">
        <i class="fa fa-fw fa-list-alt"></i> ${_('Change permissions')}
      </a>
    </li>
    <li class="divider" data-bind="visible: isCompressEnabled() || isReplicationEnabled() || isSummaryEnabled()"></li>
    % if is_trash_enabled:
    <li data-bind="css: {'disabled': $root.selectedFiles().length == 0 || isCurrentDirSelected().length > 0}">
    <a href="javascript: void(0)" data-bind="click: ($root.selectedFiles().length > 0 && isCurrentDirSelected().length == 0) ? $root.trashSelected: void(0)">
    <i class="fa fa-fw fa-times"></i> ${_('Move to trash')}</a></li>
    % endif
    <li><a href="javascript: void(0)" class="delete-link" title="${_('Delete forever')}" data-bind="enable: $root.selectedFiles().length > 0 && isCurrentDirSelected().length == 0, click: $root.deleteSelected"><i class="fa fa-fw fa-bolt"></i> ${_('Delete forever')}</a></li>
    <li class="divider" data-bind="visible: isSummaryEnabled()"></li>
    <li data-bind="css: {'disabled': selectedFiles().length > 1 }, visible: isSummaryEnabled()">
      <a class="pointer" data-bind="click: function(){ selectedFiles().length == 1 ? showSummary(): void(0)}"><i class="fa fa-fw fa-pie-chart"></i> ${_('Summary')}</a>
    </li>
    <li data-bind="css: {'disabled': inTrash() || !isReplicationEnabled() || selectedFiles().length != 1 || selectedFile().type != 'file'}">
      <a href="javascript: void(0)" title="${_('Set Replication')}" data-bind="click: (!inTrash() && isReplicationEnabled() && selectedFiles().length == 1 && selectedFile().type == 'file') ? setReplicationFactor: void(0)">
        <i class="fa fa-fw fa-hdd-o"></i> ${_('Set replication')}
      </a>
    </li>
    % if ENABLE_EXTRACT_UPLOADED_ARCHIVE.get():
      <li data-bind="css: {'disabled': ! showCompressButton}">
        <a href="javascript: void(0)" title="${_('Compress selection into a single archive')}" data-bind="click: function() { setCompressArchiveDefault(); confirmCompressFiles();}, visible: showCompressButton">
        <i class="fa fa-fw fa-file-archive-o"></i> ${_('Compress')}</a>
      </li>
      <li data-bind="css: {'disabled': selectedFiles().length != 1 || !isArchive(selectedFile().name) || !isCompressEnabled()}">
        <a href="javascript: void(0)" title="${_('Extract selected archive')}" data-bind="visible: selectedFiles().length == 1 && isArchive(selectedFile().name) && isCompressEnabled(), click: confirmExtractArchive">
        <i class="fa fa-fw fa-file-archive-o"></i> ${_('Extract')}</a>
      </li>
    % endif
  <!-- /ko -->
  <!-- ko if: $root.inTrash -->
    <li><a href="#" title="${_('Restore from trash')}" data-bind="visible: inRestorableTrash() &&  selectedFiles().length > 0 && isCurrentDirSelected().length == 0, click: restoreTrashSelected"><i class="fa fa-fw fa-cloud-upload"></i> ${_('Restore')}</a></li>
    <li class="divider"></li>
    <li><a href="#" title="${_('Empty trash')}" data-bind="visible: inTrash(), click: purgeTrash"><i class="fa fa-fw fa-fire"></i> ${_('Empty trash')}</a></li>
  <!-- /ko -->
  </ul>

  <div id="submit-wf-modal" class="modal hide"></div>

  <script id="fileTemplate" type="text/html">
    <tr class="row-animated" style="cursor: pointer" data-bind="visible: !(name == '..' && window.RAZ_IS_ENABLED), drop: { enabled: name !== '.' && type !== 'file' && ((!$root.isS3() || ($root.isS3() && !$root.isS3Root())) || (!$root.isGS() || ($root.isGS() && !$root.isGSRoot()))), value: $data }, event: { mouseover: toggleHover, mouseout: toggleHover, contextmenu: showContextMenu }, click: $root.viewFile, css: { 'row-selected': selected(), 'row-highlighted': highlighted(), 'row-deleted': deleted() }">
      <td class="center" data-bind="click: name !== '..' ? handleSelect : void(0)" style="cursor: default">
        <div data-bind="multiCheck: '#fileBrowserTable', visible: name != '..', css: { 'hue-checkbox': name != '..', 'fa': name != '..', 'fa-check': selected }"></div>
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
        <strong><a href="#" class="draggable-fb" data-bind="drag: { enabled: (!$root.isS3() || ($root.isS3() && !$root.isS3Root()) || (!$root.isGS() || ($root.isGS() && !$root.isGSRoot()))), value: $data }, click: $root.viewFile, text: name, attr: { 'draggable': $.inArray(name, ['.', '..', '.Trash']) === -1 && !isBucket()}"></a></strong>
        <!-- /ko -->
      </td>
      <td>
        <span data-bind="visible: type == 'file', text: stats.size"></span>
      </td>
      <td class="truncate-text" style="max-width: 150px">
        % if is_fs_superuser:
        <span data-bind="text: stats.user, visible: !selected() || $root.isCurrentDirSentryManaged() || isSentryManaged, attr: { 'title':  stats.user }"></span>
        <a href="#" rel="tooltip" title="${_('Change owner')}" data-original-title="${_('Change owner')}"
            data-bind="text: stats.user, visible: !$root.inTrash() && selected() && !$root.isCurrentDirSentryManaged() && !isSentryManaged, click: $root.changeOwner, enable: $root.selectedFiles().length > 0, attr: { 'title':  stats.user }"></a>
        % else:
        <span data-bind="text: stats.user, attr: { 'title':  stats.user }"></span>
        % endif
      </td>
      <td class="truncate-text" style="max-width: 150px">
        % if is_fs_superuser:
        <span data-bind="text: stats.group, visible: ! selected() || $root.isCurrentDirSentryManaged() || isSentryManaged, attr: { 'title':  stats.group }"></span>
        <a href="#" rel="tooltip" title="${_('Change group')}" data-original-title="${_('Change group')}"
            data-bind="text: stats.group, visible: !$root.inTrash() && selected() && !$root.isCurrentDirSentryManaged() && !isSentryManaged, click: $root.changeOwner, attr: { 'title':  stats.group }"></a>
        % else:
        <span data-bind="text: stats.group, attr: { 'title':  stats.group }"></span>
        % endif
      </td>
      <td>
        <span data-bind="text: permissions, visible: $root.isS3() || $root.isGS() || !selected() || $root.isCurrentDirSentryManaged() || isSentryManaged"></span>
        <a href="#" rel="tooltip" title="${_('Change permissions')}"
            data-bind="text: permissions, visible: !$root.isS3() && !$root.isGS() && !$root.inTrash() && selected() && !$root.isCurrentDirSentryManaged() && !isSentryManaged, click: $root.changePermissions" data-original-title="${_('Change permissions')}"></a>
      </td>
      <td data-bind="text: stats.mtime" style="white-space: nowrap;"></td>
    </tr>
  </script>

  <script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>

  <script type="text/template" id="qq-template">
    <div class="qq-uploader-selector" style="margin-left: 10px">
        <div class="qq-upload-drop-area-selector" qq-hide-dropzone><span>${_('Drop the files here to upload')}</span></div>
        <div class="qq-upload-button-selector qq-no-float">${_('Select files')}</div> &nbsp;
        <span class="muted">${_('or drag and drop them here')}</span> &nbsp;
        <span class="muted free-space-info"></span>

        <ul class="qq-upload-list-selector qq-upload-files unstyled qq-no-float" style="margin-right: 0;">
            <li>
                <span class="qq-upload-spinner-selector hide" style="display:none"></span>
                <div class="progress-row dz-processing">
                    <span class="break-word qq-upload-file-selector"></span>
                    <div class="pull-right">
                        <span class="qq-upload-file-selector" style="display:block"></span>
                        <span class="muted qq-upload-size-selector"></span>&nbsp;&nbsp;
                        <a href="#" title="${_('Cancel')}" class="complex-layout"><i class="fa fa-fw fa-times qq-upload-cancel-selector"></i></a>
                        <span class="qq-upload-done-selector" style="display:none"><i class="fa fa-fw fa-check muted"></i></span>
                        <span class="qq-upload-failed-text">${_('Failed')}</span>
                    </div>
                    <div class="progress-row-bar" style="width: 0%;"></div>
                </div>
            </li>
        </ul>
    </div>
  </script>


  <script type="application/json" id="listDirOptions">
    ${ options_json | n }
  </script>
  <script src="${ static('desktop/js/listdir-inline.js') }" type="text/javascript"></script>


</%def>
