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
from django.utils.translation import ugettext as _

from desktop import conf
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko
%>

<%def name="docBrowser(is_embeddable=False)">

  <script src="${ static('desktop/ext/js/bootstrap-fileupload.js') }" type="text/javascript" charset="utf-8"></script>
  <script src="${ static('desktop/ext/js/jquery/plugins/jquery.hotkeys.js') }"></script>
  <link href="${ static('desktop/css/home.css') }" rel="stylesheet">
  <link href="${ static('desktop/ext/css/bootstrap-fileupload.css') }" rel="stylesheet">

  <script type="text/html" id="doc-browser-template">
    <div class="doc-browser-drag-helper">
      <i class="fa fa-fw"></i><span class="drag-text">4 entries</span>
    </div>

    <div id="shareDocumentModal" data-keyboard="true" class="modal hide fade" tabindex="-1">
      <!-- ko with: activeEntry -->
      <!-- ko with: selectedEntry -->
      <!-- ko with: document -->
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${_('Sharing')} - <span data-bind="text: $parent.definition().name"></span></h2>
      </div>
      <div class="modal-body" style="overflow-y: visible; height: 240px">
        <!-- ko with: definition -->
        <div class="row-fluid" data-bind="visible: !$parent.hasErrors()">
          <div class="span6">
            <h4 class="muted" style="margin-top:0px">${_('Read')}</h4>
            <div data-bind="visible: (perms.read.users.length == 0 && perms.read.groups.length == 0)">${_('The document is not shared for read.')}</div>
            <ul class="unstyled airy" data-bind="foreach: perms.read.users">
              <li>
                <span class="badge badge-info" data-bind="css: { 'badge-left' : $parents[1].fileEntry.canModify() }"><i class="fa fa-user"></i> <span data-bind="text: prettyName, css:{ 'notpretty': prettyName === '' }, attr:{ 'data-id': id }"></span></span><span class="badge badge-right trash-share" data-bind="visible: $parents[1].fileEntry.canModify(), click: function() { $parents[1].removeUserReadShare($data) }"> <i class="fa fa-times"></i></span>
              </li>
            </ul>
            <ul class="unstyled airy" data-bind="foreach: perms.read.groups">
              <li>
                <span class="badge badge-info" data-bind="css: { 'badge-left' : $parents[1].fileEntry.canModify() }"><i class="fa fa-users"></i> ${ _('Group') } &quot;<span data-bind="text: name"></span>&quot;</span><span class="badge badge-right trash-share" data-bind="visible: $parents[1].fileEntry.canModify(), click: function() { $parents[1].removeGroupReadShare($data) }"> <i class="fa fa-times"></i></span>
              </li>
            </ul>
          </div>

          <div class="span6">
            <h4 class="muted" style="margin-top: 0">${_('Modify')}</h4>
            <div data-bind="visible: (perms.write.users.length == 0 && perms.write.groups.length == 0)">${_('The document is not shared for modify.')}</div>
            <ul class="unstyled airy" data-bind="foreach: perms.write.users">
              <li>
                <span class="badge badge-info badge-left" data-bind="css: { 'badge-left' : $parents[1].fileEntry.canModify() }"><i class="fa fa-user"></i> <span data-bind="text: prettyName, css:{'notpretty': prettyName == ''}, attr:{'data-id': id}"></span></span><span class="badge badge-right trash-share" data-bind="visible: $parents[1].fileEntry.canModify(), click: function() { $parents[1].removeUserWriteShare($data) }"> <i class="fa fa-times"></i></span>
              </li>
            </ul>
            <ul class="unstyled airy" data-bind="foreach: perms.write.groups">
              <li>
                <span class="badge badge-info badge-left" data-bind="css: { 'badge-left' : $parents[1].fileEntry.canModify() }"><i class="fa fa-users"></i> ${ _('Group') } &quot;<span data-bind="text: name"></span>&quot;</span><span class="badge badge-right trash-share" data-bind="visible: $parents[1].fileEntry.canModify(), click: function() { $parents[1].removeGroupWriteShare($data) }"> <i class="fa fa-times"></i></span>
              </li>
            </ul>
          </div>
        </div>
        <!-- /ko -->
        <div class="doc-browser-empty animated" style="display: none;" data-bind="visible: loading">
          <i class="fa fa-spinner fa-spin fa-2x" style="color: #999;"></i>
        </div>
        <div class="doc-browser-empty animated" style="display: none;" data-bind="visible: hasErrors() && ! loading()">
          ${ _('There was an error loading the document.')}
        </div>
        <div style="margin-top: 20px" data-bind="visible: fileEntry.canModify() && ! hasErrors() && ! loading()">
          <div class="input-append">
            <input id="documentShareTypeahead" type="text" style="width: 420px" placeholder="${_('Type a username or a group name')}">
            <div class="btn-group" style="overflow:visible">
              <a class="btn btn-primary" data-bind="click: function () { if (selectedUserOrGroup()) { handleTypeAheadSelection() }}, css: { 'disabled': !selectedUserOrGroup() }"><i class="fa fa-plus-circle"></i> <span data-bind="text: selectedPerm() == 'read' ? '${ _('Read') }' : '${ _('Modify') }'"></span></a>
              <a class="btn btn-primary dropdown-toggle" data-bind="css: { 'disabled': !selectedUserOrGroup() }" data-toggle="dropdown"><span class="caret"></span></a>
              <ul class="dropdown-menu">
                <li><a data-bind="click: function () { selectedPerm('read'); handleTypeAheadSelection() }" href="javascript:void(0)"><i class="fa fa-plus"></i> ${ _('Read') }</a></li>
                <li><a data-bind="click: function () { selectedPerm('write'); handleTypeAheadSelection() }" href="javascript:void(0)"><i class="fa fa-plus"></i> ${ _('Modify') }</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <a href="#" data-dismiss="modal" class="btn disable-feedback disable-enter">${_('Close')}</a>
      </div>
      <!-- /ko -->
      <!-- /ko -->
      <!-- /ko -->
    </div>

    <div id="importDocumentsModal" data-keyboard="true" class="modal hide fade fileupload-modal" tabindex="-1">
      <!-- ko with: activeEntry -->
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${_('Import Hue documents')}</h2>
      </div>
        <form id="importDocumentsForm" class="form-horizontal" style="display: inline" enctype="multipart/form-data">
          <div class="modal-body">
            <div data-bind="visible: uploading() || uploadComplete()">
              <span data-bind="visible: uploading()">${ _('Importing...') }</span>
              <span data-bind="visible: !uploadFailed() && uploadComplete()">${ _('Import complete!') }</span>
              <span data-bind="visible: uploadFailed">${ _('Import failed!') }</span>
              <progress data-bind="visible: uploading() || uploadComplete()" id="importDocumentsProgress" value="0" max="100" style="width: 560px;"></progress>
            </div>
            <div class="pull-right">
              <!-- ko ifnot: uploading() || uploadComplete() -->
              <input type="button" class="btn" data-clear="fileupload" data-bind="click: closeUploadModal" value="${ _('Cancel') }" />
              <input type="submit" class="btn btn-danger" data-clear="fileupload" data-bind="enable: importEnabled, click: upload" value="${ _('Import') }" />
              <!-- /ko -->
              <!-- ko if: uploading() || uploadComplete() -->
              <input type="button" class="btn" data-clear="fileupload" data-bind="click: closeUploadModal" value="${ _('Close') }" />
              <!-- /ko -->
            </div>

            <div class="fileupload fileupload-new" data-provides="fileupload" data-bind="visible: !uploading() && !uploadComplete()">
              <span class="btn btn-file" style="line-height: 29px">
                <span class="fileupload-new">${ _('Select json file') }</span>
                <span class="fileupload-exists">${ _('Change') }</span>
                <input id="importDocumentInput" type="file" name="documents" accept=".json" data-bind="value: selectedImportFile" />
              </span>
              &nbsp;&nbsp;<span class="fileupload-preview"></span>
              <a href="#" class="fileupload-exists" data-clear="fileupload"><i class="fa fa-times"></i></a>
            </div>
            ${ csrf_token(request) | n,unicode }
            <input type="hidden" name="path" data-bind="value: definition().path" />
          </div>
        </form>
      <!-- /ko -->
    </div>

    <div id="importDocumentData" data-keyboard="true" class="modal hide fade" tabindex="-1">
      <!-- ko with: activeEntry -->
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <h2 class="modal-title">${_('Import Hue documents')}</h2>
      </div>
      <div class="modal-body">
        <div class="center" style="display: none;" data-bind="visible: importedDocumentCount() == 0">
          <i class="fa fa-spinner fa-spin fa-2x"></i>
        </div>
        <!-- ko if: importedDocumentCount() > 0 -->
          <ul>
            <li> ${_('Imported: ')} <span data-bind="text: importedDocSummary()['count']"></span></li>
            <li> ${_('Created: ')} <span data-bind="text: importedDocSummary()['created_count']"></span></li>
            <li> ${_('Updated: ')} <span data-bind="text: importedDocSummary()['updated_count']"></span></li>
          </ul>

          <!-- ko ifnot: showTable() -->
          <a href="javascript:void(0)" class="margin-left-10 margin-top-10" data-bind="click: toggleShowTable">${_('Show Details')} <i class="fa fa-caret-down"></i></a>
          <!-- /ko -->
          <!-- ko if: showTable() -->
          <a href="javascript:void(0)" class="margin-left-10 margin-top-10" data-bind="click: toggleShowTable">${_('Hide Details')} <i class="fa fa-caret-up"></i></a>
            <table class="table table-condensed">
              <thead>
                <tr>
                  <th>${_('Name')}</th>
                  <th>${_('Type')}</th>
                  <th>${_('Owner')}</th>
                </tr>
              </thead>
              <tbody data-bind="foreach: importedDocSummary()['documents']">
                <tr>
                  <td data-bind="text: $data.name"> </td>
                  <td data-bind="text: $data.type"> </td>
                  <td data-bind="text: $data.owner"> </td>
                </tr>
              </tbody>
            </table>
          <!-- /ko -->
        <!-- /ko -->
      </div>
      <div class="modal-footer">
        <input data-dismiss="modal" type="button" class="btn" value="${ _('Close') }" data-bind="click: closeUploadModal"/>
      </div>
      <!-- /ko -->
    </div>

    <div id="createDirectoryModal" data-keyboard="true" class="modal hide fade" tabindex="-1">
      <!-- ko with: activeEntry -->
      <form class="form-horizontal">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
          <h2 class="modal-title">${_('Create Directory')}</h2>
        </div>
        <div class="modal-body ">
          <input id="newDirectoryName" class="input large-as-modal" type="text" placeholder="${ _('Directory name') }" />
        </div>
        <div class="modal-footer">
          <input type="button" class="btn" data-dismiss="modal" data-bind="click: function () { $('#newDirectoryName').val(null) }" value="${ _('Cancel') }">
          <input type="submit" class="btn btn-primary disable-feedback" value="${ _('Create') }" data-bind="click: function () { if ($('#newDirectoryName').val()) { $data.createDirectory($('#newDirectoryName').val()); $('#createDirectoryModal').modal('hide'); } }"/>
        </div>
      </form>
      <!-- /ko -->
    </div>

    <div id="renameDirectoryModal" data-keyboard="true" class="modal hide fade" tabindex="-1">
      <!-- ko with: activeEntry -->
      <form class="form-horizontal">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
          <h2 class="modal-title">${_('Rename Directory')}</h2>
        </div>
        <div class="modal-body ">
          <input id="renameDirectoryName" class="input large-as-modal" type="text" placeholder="${ _('Directory name') }" />
        </div>
        <div class="modal-footer">
          <input type="button" class="btn" data-dismiss="modal" data-bind="click: function () { $('#renameDirectoryName').val(null) }" value="${ _('Cancel') }">
          <input type="submit" class="btn btn-primary disable-feedback" value="${ _('Rename') }" data-bind="click: function () { if ($('#renameDirectoryName').val()) { $data.selectedEntry().renameDirectory($('#renameDirectoryName').val()); $('#renameDirectoryModal').modal('hide'); } }"/>
        </div>
      </form>
      <!-- /ko -->
    </div>

    <div id="restoreFromTrashModal" data-keyboard="true" class="modal hide fade" tabindex="-1">
      <!-- ko with: activeEntry -->
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <!-- ko if: selectedEntries().length > 0 -->
        <h2 class="modal-title">${ _('Restore these document(s) to Home directory?') }</h2>
        <!-- /ko -->
      </div>
      <div class="modal-body">
        <ul data-bind="foreach: selectedEntries()">
          <li> <span data-bind="text: $data.definition().name"></span> </li>
        </ul>
      </div>
      <div class="modal-footer">
        <input type="button" class="btn" data-dismiss="modal" value="${ _('Cancel') }">
        <input type="submit" data-bind="click: function() { restoreFromTrash() }" class="btn btn-danger" value="${_('Yes')}"/>
      </div>
      <!-- /ko -->
    </div>

    <div id="deleteEntriesModal" data-keyboard="true" class="modal hide fade" tabindex="-1">
      <!-- ko with: activeEntry -->
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
        <!-- ko if: entriesToDelete().length === 0 -->
        <h2 class="modal-title">${ _('The trash is empty') }</h2>
        <!-- /ko -->
        <!-- ko if: entriesToDelete().length > 0 -->
        <h2 class="modal-title"> ${ _('Do you really want to delete the following document(s)?') } </h2>
        <!-- /ko -->
      </div>
      <div class="modal-body">
        <div class="doc-browser-empty animated" style="display: none;" data-bind="visible: selectedDocsWithDependents().length === 0">
          <i class="fa fa-spinner fa-spin fa-2x"></i>
        </div>
        <ul data-bind="foreach: selectedDocsWithDependents()">
          <li>
            <span data-bind="text: $data.name"></span>
            <!-- ko if: $data.dependents.length > 0 -->
              (${_('used by')}
              <a class="pointer" data-bind="hueLink: $data.dependents[0].absoluteUrl, text: $data.dependents[0].name"></a>
              <!-- ko if: $data.dependents.length > 1 -->
              ${_('and')} <a class="pointer" data-bind="hueLink: $data.dependents[1].absoluteUrl, text: $data.dependents[1].name"></a>
                <!-- ko if: $data.dependents.length > 2 -->
                  ${_('and')} <span data-bind="text: $data.dependents.length - 2"></span> ${_('other')}
                <!-- /ko -->
              <!-- /ko -->
              )
            <!-- /ko -->
          </li>
        </ul>
      </div>
      <div class="modal-footer">
        <!-- ko if: entriesToDelete().length === 0 -->
        <input type="button" class="btn" data-dismiss="modal" value="${ _('Close') }">
        <!-- /ko -->
        <!-- ko if: entriesToDelete().length > 0 -->
        <input type="button" class="btn" data-dismiss="modal" value="${ _('Cancel') }">
        <input type="submit" data-bind="click: function() { if (isTrash() || isTrashed()) { removeDocuments(true) } else { moveToTrash() } }, disable: deletingEntries" class="btn btn-danger disable-feedback" value="${_('Yes')}"/>
        <!-- /ko -->
      </div>
      <!-- /ko -->
    </div>

    <div class="doc-browser-container" data-bind="docSelect: activeEntry.entries, docDroppable: { entries: activeEntry.entries }">
      <div class="doc-browser-action-bar">
        <h4 class="doc-browser-main-header">
          <div data-bind="with: activeEntry">
            <ul class="doc-browser-breadcrumbs">
              <!-- ko if: isRoot -->
              <li class="active"><div class="doc-browser-drop-target">${ _('My documents') }</div></li>
              <!-- /ko -->

              <!-- ko if: definition().isSearchResult -->
              <li class="active"><div class="doc-browser-drop-target">${ _('Result for') }: <!-- ko text: definition().name --><!-- /ko --></div></li>
              <!-- /ko -->
              <!-- ko ifnot: definition().isSearchResult -->
              <!-- ko foreach: breadcrumbs -->
              <li><div class="doc-browser-drop-target" data-bind="docDroppable: { entries: $parent.entries, disableSelect: true }"><a href="javascript:void(0);" data-bind="text: isRoot() ? '${ _('My documents') }' : (isTrash() ? '${ _('Trash') }' : definition().name), click: open"></a></div></li>
              <li class="divider">&gt;</li>
              <!-- /ko -->
              <!-- ko ifnot: isRoot -->
              <li class="active"><div class="doc-browser-drop-target" data-bind="text: isTrash() ? '${ _('Trash') }' : definition().name"></div></li>
              <!-- /ko -->
              <!-- /ko -->
            </ul>
          </div>
        </h4>
        <div class="doc-browser-folder-actions" data-bind="visible: activeEntry && activeEntry() && !activeEntry().hasErrors()">
          <!-- ko if: searchVisible -->
          <div class="doc-browser-action doc-browser-search-container"><input class="clearable" type="text" placeholder="${ _('Search for name, description, etc...') }" data-bind="hasFocus: searchFocus, textInput: searchQuery, clearable: searchQuery"></div>
          <!-- /ko -->
          <!-- ko with: activeEntry -->
          <div class="doc-browser-action doc-browser-type-filter margin-right-10" data-bind="component: { name: 'hue-drop-down', params: { value: serverTypeFilter, entries: $root.allDocumentTypes, linkTitle: '${ _ko('Type filter') }' } }"><</div>
          <div><a class="inactive-action doc-browser-action margin-right-20" title="${_('Search')}" href="javascript:void(0);" data-bind="tooltip: { placement: 'bottom', delay: 750 }, toggle: $parent.searchVisible, click: function () { $parent.searchFocus($parent.searchVisible()) }, css: { 'blue' : ($parent.searchVisible() || $parent.searchQuery()) }"><i class="fa fa-fw fa-search"></i></a></div>
          <!-- ko if: app === 'documents' -->
          <div>
            <span class="dropdown">
              <a class="inactive-action doc-browser-action" title="${_('New document')}" data-toggle="dropdown" data-bind="tooltip: { placement: 'bottom', delay: 750 }, css: { 'disabled': isTrash() || isTrashed() }" href="javascript:void(0);"><span class="fa-stack fa-fw" style="width: 1.28571429em"><i class="fa fa-file-o fa-stack-1x"></i><i class="fa fa-plus-circle fa-stack-1x" style="font-size: 14px; margin-left: 6px; margin-top: 6px;"></i></span></a>
              <ul class="dropdown-menu less-padding document-types" style="margin-top:10px; width: 175px;" role="menu">
                % if 'beeswax' in apps:
                  <li>
                    <a title="${_('Hive Query')}"
                    % if is_embeddable:
                      data-bind="click: function() { huePubSub.publish('open.editor.new.query', {type: 'hive', 'directoryUuid': getDirectory()}); }" href="javascript:void(0);"
                    % else:
                      data-bind="hueLink: addDirectoryParamToUrl('${ url('notebook:editor') }?type=hive')"
                    % endif
                    >
                      <img src="${ static(apps['beeswax'].icon_path) }" class="app-icon" alt="${ _('Hive icon') }"/> ${_('Hive Query')}
                    </a>
                  </li>
                % endif
                % if 'impala' in apps:
                  <li>
                    <a title="${_('Impala Query')}"
                    % if is_embeddable:
                      data-bind="click: function() { huePubSub.publish('open.editor.new.query', {type: 'impala', 'directoryUuid': getDirectory()}); }" href="javascript:void(0);"
                    % else:
                      data-bind="hueLink: addDirectoryParamToUrl('${ url('notebook:editor') }?type=impala')"
                    % endif
                    >
                      <img src="${ static(apps['impala'].icon_path) }" class="app-icon" alt="${ _('Impala icon') }"/> ${_('Impala Query')}
                    </a>
                </li>
                % endif
                <%
                from notebook.conf import SHOW_NOTEBOOKS
                %>
                % if SHOW_NOTEBOOKS.get():
                  <li>
                    <a title="${_('Notebook')}" data-bind="hueLink: addDirectoryParamToUrl('${ url('notebook:index') }')">
                      <i style="font-size: 24px; line-height: 24px; vertical-align: middle; color: #0B7FAD;" class="fa app-icon fa-fw fa-file-text-o"></i> ${_('Notebook')}
                    </a>
                  </li>
                % endif
                % if 'pig' in apps:
                  <li>
                    <a title="${_('Pig Script')}" data-bind="hueLink: addDirectoryParamToUrl('${ url('pig:index') }')">
                      <img src="${ static(apps['pig'].icon_path) }" class="app-icon" alt="${ _('Pig icon') }"/> ${_('Pig Script')}
                    </a>
                  </li>
                % endif
                % if 'oozie' in apps:
                  <li>
                    <a title="${_('Oozie Workflow')}" data-bind="hueLink: addDirectoryParamToUrl('${ url('oozie:new_workflow') }')">
                      <img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon" alt="${ _('Oozie workflow icon') }"/> ${_('Workflow') if is_embeddable else _('Oozie Workflow')}
                    </a>
                  </li>
                  <li>
                    <a title="${_('Oozie Coordinator')}" data-bind="hueLink: addDirectoryParamToUrl('${ url('oozie:new_coordinator') }')">
                      <img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon" alt="${ _('Oozie coordinator icon') }"/> ${_('Coordinator') if is_embeddable else _('Oozie Coordinator')}
                    </a>
                  </li>
                  <li>
                    <a title="${_('Oozie Bundle')}" data-bind="hueLink: addDirectoryParamToUrl('${ url('oozie:new_bundle') }')">
                      <img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon" alt="${ _('Oozie bundle icon') }"/> ${_('Bundle') if is_embeddable else _('Oozie Bundle')}
                    </a>
                  </li>
                % endif
                % if 'search' in apps:
                  <li>
                    <a title="${_('Solr Search')}" data-bind="hueLink: addDirectoryParamToUrl('${ url('search:new_search') }')">
                      <img src="${ static('search/art/icon_search_48.png') }" class="app-icon" alt="${ _('Search icon') }"/> ${_('Dashboard')}
                    </a>
                  </li>
                % endif
              </ul>
            </span>
          </div>
          <!-- /ko -->
          <div><a class="inactive-action doc-browser-action" title="${_('New folder')}" href="javascript:void(0);" data-bind="tooltip: { placement: 'bottom', delay: 750 }, click: function () { showNewDirectoryModal() }, css: { 'disabled': isTrash() || isTrashed() }"><span class="fa-stack fa-fw" style="width: 1.28571429em;"><i class="fa fa-folder-o fa-stack-1x" ></i><i class="fa fa-plus-circle fa-stack-1x" style="font-size: 14px; margin-left: 7px; margin-top: 3px;"></i></span></a></div>
          <div><a class="inactive-action doc-browser-action" title="${_('Rename folder')}" href="javascript:void(0);" data-bind="tooltip: { placement: 'bottom', delay: 750 }, click: function () { showRenameDirectoryModal() }, css: { 'disabled': isTrash() || isTrashed() || selectedEntry() === null || (selectedEntry() != null && !selectedEntry().isDirectory()) }"><i class="fa fa-fw fa-edit"></i></a></div>
          <!-- ko if: isTrash() -->
            <div><a class="inactive-action doc-browser-action" href="javascript:void(0);" data-bind="tooltip: { placement: 'bottom', delay: 750 }, click: function() { showRestoreConfirmation(); }, css: { 'disabled': selectedEntries().length === 0 }, attr: { 'title' : '${ _('Restore to Home ') }' }">
              <i class="fa fa-fw fa-undo"></i></a>
            </div>
          <!-- /ko -->
          <div><a class="inactive-action doc-browser-action" href="javascript:void(0);" data-bind="tooltip: { placement: 'bottom', delay: 750 }, click: function() {getSelectedDocsWithDependents(); showDeleteConfirmation();}, css: { 'disabled': selectedEntries().length === 0 || (sharedWithMeSelected() && ! superuser) }, attr: { 'title' : isTrash() || isTrashed() ? '${ _('Delete forever') }' : '${ _('Move to trash') }' }">
            <i class="fa fa-fw fa-times"></i></a>
          </div>
          <!-- ko if: app === 'documents' -->
          <div><a class="inactive-action doc-browser-action" title="${_('Share')}" href="javascript:void(0);" data-bind="tooltip: { placement: 'bottom', delay: 750 }, click: function() { showSharingModal(null) }, css: { 'disabled': selectedEntries().length !== 1 || (selectedEntries().length === 1 && selectedEntries()[0].isTrashed) }"><i class="fa fa-fw fa-users"></i></a></div>
          <!-- /ko -->
          <div style="margin-top: 2px"><a class="inactive-action doc-browser-action" title="${_('Export all or selected documents')}" href="javascript:void(0);" data-bind="tooltip: { placement: 'bottom', delay: 750 }, click: download"><i class="fa fa-fw fa-download"></i></a></div>
          <div><a class="inactive-action doc-browser-action" title="${_('Import documents')}" href="javascript:void(0);" data-bind="tooltip: { placement: 'bottom', delay: 750 }, click: showUploadModal, css: { 'disabled': isTrash() || isTrashed() }"><i class="fa fa-fw fa-upload"></i></a></div>
          <!-- ko if: app === 'documents' -->
          <div class="margin-left-20" data-bind="contextMenu: { menuSelector: '.hue-context-menu' }">
            <a class="inactive-action doc-browser-action" title="${_('Show trash')}" href="javascript:void(0);" data-bind="tooltip: { placement: 'bottom', delay: 750 }, click: showTrash, trashDroppable, css: { 'blue' : isTrash() || isTrashed() }">
              <i class="fa fa-fw fa-trash-o"></i>
            </a>
            <!-- ko if: isTrash() || isTrashed() -->
            <ul class="hue-context-menu">
              <li><a href="javascript:void(0);" data-bind="click: emptyTrash"><i class="fa fa-fw fa-times"></i> ${ _('Empty trash') }</a></li>
            </ul>
            <!-- /ko -->
          </div>
          <!-- ko component: { name: 'hue-favorite-app', params: { hue4: IS_HUE_4, app: 'home' }} --><!-- /ko -->
          <!-- /ko -->
          <!-- /ko -->
        </div>
      </div>

      <!-- ko with: activeEntry -->
      <!-- ko if: entries().length > 0 -->
      <div class="doc-browser-header">
        <div class="doc-browser-primary-col" data-bind="click: function () { setSort('name') }, css: { 'sorting_asc' : activeSort() === 'nameAsc', 'sorting_desc' : activeSort() === 'nameDesc', 'sorting' : activeSort().indexOf('name') !== 0 }">${ _('Name') }</div>
        <div class="doc-browser-attr-group">
          <div class="doc-browser-attr-col doc-browser-description" data-bind="click: function () { setSort('description') }, css: { 'sorting_asc' : activeSort() === 'descriptionAsc', 'sorting_desc' : activeSort() === 'descriptionDesc', 'sorting' : activeSort().indexOf('description') !== 0 }">${ _('Description') }</div>
          <div class="doc-browser-attr-col doc-browser-type" data-bind="click: function () { setSort('type') }, css: { 'sorting_asc' : activeSort() === 'typeAsc', 'sorting_desc' : activeSort() === 'typeDesc', 'sorting' : activeSort().indexOf('type') !== 0 }">${ _('Type') }</div>
          <div class="doc-browser-attr-col doc-browser-owner" data-bind="click: function () { setSort('owner') }, css: { 'sorting_asc' : activeSort() === 'ownerAsc', 'sorting_desc' : activeSort() === 'ownerDesc', 'sorting' : activeSort().indexOf('owner') !== 0 }">${ _('Owner') }</div>
          <div class="doc-browser-attr-col doc-browser-modified" data-bind="click: function () { setSort('lastModified') }, css: { 'sorting_asc' : activeSort() === 'lastModifiedAsc', 'sorting_desc' : activeSort() === 'lastModifiedDesc', 'sorting' : activeSort().indexOf('lastModified') !== 0 }">${ _('Last Modified') }</div>
        </div>
      </div>
      <!-- /ko -->

      <div class="doc-browser-empty animated" style="display:none;" data-bind="visible: entries().length == 0 && ! hasErrors() && ! loading() && ! definition().isSearchResult && ! isTrash()">
        ${ _('The current folder is empty, you can add a new document or folder form the top right menu')}
      </div>
      <div class="doc-browser-empty animated" style="display:none;" data-bind="visible: entries().length == 0 && ! hasErrors() && ! loading() && ! definition().isSearchResult && isTrash()">
        ${ _('The trash is empty')}
      </div>
      <div class="doc-browser-empty animated" style="display:none;" data-bind="visible: entries().length == 0 && ! hasErrors() && ! loading() && definition().isSearchResult">
        ${ _('No documents found matching your query')}
      </div>
      <div class="doc-browser-empty animated" style="display: none;" data-bind="visible: hasErrors() && app === 'documents' && ! loading()">
        ${ _('There was an error loading the documents')}
      </div>
      <div class="doc-browser-empty animated" style="display: none;" data-bind="visible: entries().length === 0 && loading()">
        <i class="fa fa-spinner fa-spin fa-2x" style="color: #999;"></i>
      </div>
      <!-- /ko -->

      <div class="doc-browser-list" data-bind="with: activeEntry" >
        <ul class="doc-browser-entries" data-bind="foreachVisible: { data: entries, minHeight: 42, container: '.doc-browser-list' }">
          <li data-bind="docSelect: $parent.entries, docDroppable: { entries: $parent.entries }, css: { 'doc-browser-selected': selected }">
            <div class="doc-browser-row" data-bind="contextMenu: { scrollContainer: '.doc-browser-list', menuSelector: '.hue-context-menu', beforeOpen: beforeContextOpen }">
              <ul class="hue-context-menu">
                <!-- ko if: isTrashed -->
                <li><a href="javascript:void(0);" data-bind="click: function() { $parent.getSelectedDocsWithDependents(); $parent.showDeleteConfirmation(); }"><i class="fa fa-fw fa-times"></i> ${ _('Delete') } <span data-bind="visible: $parent.selectedEntries().length > 1, text: '(' + $parent.selectedEntries().length + ')'"></span></a></li>
                <li><a href="javascript:void(0);" data-bind="click: function() { $parent.showRestoreConfirmation(); }"><i class="fa fa-fw fa-undo"></i> ${ _('Restore to Home') } <span data-bind="visible: $parent.selectedEntries().length > 1, text: '(' + $parent.selectedEntries().length + ')'"></span></a></li>
                <!-- /ko -->
                <!-- ko ifnot: isTrashed -->
                <!-- ko if: isDirectory -->
                <li data-bind="css: { 'disabled': $parent.selectedEntries().length !== 1 }"><a href="javascript:void(0);" data-bind="click: showRenameDirectoryModal, css: { 'disabled': $parent.selectedEntries().length !== 1 }"><i class="fa fa-fw fa-edit"></i> ${ _('Rename') }</a></li>
                <!-- /ko -->
                <li data-bind="css: { 'disabled': $parent.selectedEntries().length !== 1 }"><a href="javascript:void(0);" data-bind="click: open, css: { 'disabled': $parent.selectedEntries().length !== 1 }"><i class="fa fa-fw fa-file-o"></i> ${ _('Open') }</a></li>
                <li><a href="javascript:void(0);" data-bind="click: contextMenuDownload"><i class="fa fa-fw fa-download"></i> ${ _('Download') } <span data-bind="visible: $parent.selectedEntries().length > 1, text: '(' + $parent.selectedEntries().length + ')'"></span></a></li>
                <li data-bind="visible: ! $altDown(), css: { 'disabled' : $parent.sharedWithMeSelected()  && ! $parent.superuser }"><a href="javascript:void(0);" data-bind="click: function () { $parent.getSelectedDocsWithDependents(); $parent.showDeleteConfirmation(); }, css: { 'disabled' : $parent.sharedWithMeSelected() && ! $parent.superuser }">
                  <i class="fa fa-fw fa-times"></i> ${ _('Move to trash') } <span data-bind="visible: $parent.selectedEntries().length > 1, text: '(' + $parent.selectedEntries().length + ')'"></span></a>
                </li>
                <li data-bind="visible: $altDown(), css: { 'disabled' : $parent.sharedWithMeSelected() && ! $parent.superuser }"><a href="javascript:void(0);" data-bind="click: function() { $parent.showDeleteConfirmation(); }, css: { 'disabled' : $parent.sharedWithMeSelected() && ! $parent.superuser}"><i class="fa fa-fw fa-times"></i> ${ _('Delete forever') } <span data-bind="visible: $parent.selectedEntries().length > 1, text: '(' + $parent.selectedEntries().length + ')'"></span></a></li>
                <li data-bind="css: { 'disabled': $parent.selectedEntries().length !== 1 }"><a href="javascript:void(0);" data-bind="click: function() { $parent.showSharingModal(); }, css: { 'disabled': $parent.selectedEntries().length !== 1 }"><i class="fa fa-fw fa-users"></i> ${ _('Share') }</a> </li>
                <!-- /ko -->
              </ul>
              <div class="doc-browser-primary-col">
                <!-- ko template: { name: 'document-icon-template', data: { document: $data, showShareAddon: true } } --><!-- /ko -->
                <a href="javascript: void(0);" data-bind="text: definition().name, click: open, hueLink: definition().type === 'directory' ? '' : definition().absoluteUrl, attr: { 'title': definition().name }" class="margin-left-5"></a>
              </div>
              <div class="doc-browser-attr-group">
                <!-- ko with: definition -->
                <div class="doc-browser-attr-col doc-browser-description" data-bind="text: description, attr: { 'title': description }"></div>
                <div class="doc-browser-attr-col doc-browser-type" data-bind="text: DocumentTypeGlobals[type] || type"></div>
                <div class="doc-browser-attr-col doc-browser-owner" data-bind="text: owner, attr: { 'title': owner }"></div>
                <div class="doc-browser-attr-col doc-browser-modified" data-bind="text: localeFormat(last_modified)"></div>
                <!-- /ko -->
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      ko.bindingHandlers.trashDroppable = {
        init: function(element, valueAccessor, allBindings, boundEntry) {
          var dragData;
          huePubSub.subscribe('doc.browser.dragging', function (data) {
            dragData = data;
          });
          var $element = $(element);
          $element.droppable({
            drop: function () {
              if (dragData && !dragData.dragToSelect) {
                boundEntry.moveToTrash();
                $element.removeClass('blue');
              }
            },
            over: function () {
              if (dragData && !dragData.dragToSelect) {
                $element.addClass('blue');
              }
            },
            out: function () {
              $element.removeClass('blue');
            }
          })
        }
      };

      ko.bindingHandlers.docDroppable = {
        init: function(element, valueAccessor, allBindings, boundEntry, bindingContext) {
          var options = valueAccessor();
          var allEntries = options.entries;
          var $element = $(element);
          var dragToSelect = false;
          var alreadySelected = false;
          huePubSub.subscribe('doc.drag.to.select', function (value) {
            alreadySelected = boundEntry && boundEntry.selected ? boundEntry.selected() : false;
            dragToSelect = value;
          });
          $element.droppable({
            drop: function (ev, ui) {
              if (! dragToSelect && boundEntry.isDirectory && boundEntry.isDirectory()) {
                var entriesToMove = $.grep(allEntries(), function (entry) {
                  return entry.selected() && ! entry.isSharedWithMe();
                });
                if (entriesToMove.length > 0) {
                  boundEntry.moveHere(entriesToMove);
                  boundEntry.load();
                }
              }
              $element.removeClass('doc-browser-drop-hover');
            },
            over: function () {
              if (! dragToSelect && boundEntry.isDirectory && boundEntry.isDirectory()) {
                var movableCount = allEntries().filter(function (entry) {
                  return entry.selected() && ! entry.isSharedWithMe();
                }).length;
                if (movableCount > 0) {
                  $element.addClass('doc-browser-drop-hover');
                }
              }
            },
            out: function (event, ui) {
              if (! dragToSelect && boundEntry.isDirectory && boundEntry.isDirectory()) {
                $element.removeClass('doc-browser-drop-hover');
              }
            }
          })
        }
      };

      ko.bindingHandlers.docSelect = {
        init: function(element, valueAccessor, allBindings, boundEntry, bindingContext) {
          var $element = $(element);
          $element.attr('unselectable', 'on').css('user-select', 'none').on('selectstart', false);
          var allEntries = valueAccessor();

          var dragStartY = -1;
          var dragStartX = -1;
          var dragToSelect = false;
          var allRows;
          $element.draggable({
            start: function (event, ui) {
              allRows = $('.doc-browser-row');
              var $container = $('.doc-browser-drag-container');

              var selectedEntries = allEntries ? $.grep(allEntries(), function (entry) {
                return entry.selected();
              }) : [];

              dragToSelect = boundEntry && boundEntry.selected ? ! boundEntry.selected() : true;

              huePubSub.publish('doc.browser.dragging', {
                selectedEntries: selectedEntries,
                originEntry: boundEntry ? boundEntry.parent : null,
                dragToSelect: dragToSelect
              });

              dragStartX = event.clientX;
              dragStartY = event.clientY;

              huePubSub.publish('doc.drag.to.select', dragToSelect);

              if (dragToSelect && selectedEntries.length > 0 && ! (event.metaKey || event.ctrlKey)){
                $.each(selectedEntries, function (idx, selectedEntry) {
                  if (selectedEntry !== boundEntry) {
                   selectedEntry.selected(false);
                  }
                });
                selectedEntries = [];
              }

              if (boundEntry && boundEntry.selected) {
                boundEntry.selected(true);
              }
              if (dragToSelect && allEntries) {
                allEntries().forEach(function (entry) {
                  entry.alreadySelected = entry.selected();
                })
              }

              if (! dragToSelect) {
                var $helper = $('.doc-browser-drag-helper').clone().show();
                var sharedCount = selectedEntries.filter(function (entry) {
                  return entry.isSharedWithMe();
                }).length;
                if (sharedCount === selectedEntries.length) {
                  $helper.hide();
                } else if (selectedEntries.length > 1 && sharedCount > 0) {
                  $helper.find('.drag-text').text(selectedEntries.length + ' ${ _('selected') } (' + sharedCount + ' ${ _('shared ignored') })');
                  $helper.find('i').removeClass().addClass('fa fa-fw fa-clone');
                } else if (selectedEntries.length > 1) {
                  $helper.find('.drag-text').text(selectedEntries.length + ' ${ _('selected') }');
                  $helper.find('i').removeClass().addClass('fa fa-fw fa-clone');
                } else {
                  $helper.find('.drag-text').text(boundEntry.definition().name);
                  $helper.find('i').removeClass().addClass($element.find('.doc-browser-primary-col i').attr('class'));
                }

                $helper.appendTo($container);
              } else {
                $('<div>').addClass('doc-browser-drag-select').appendTo('body');
              }
            },
            drag: function (event) {
              var startX = Math.min(event.clientX, dragStartX);
              var startY = Math.min(event.clientY, dragStartY);
              if (dragToSelect) {
                allRows.each(function (idx, row) {
                  var boundingRect = row.getBoundingClientRect();
                  var boundObject = ko.dataFor(row);
                  if ((dragStartY <= boundingRect.top && event.clientY >= boundingRect.top) ||
                      (event.clientY <= boundingRect.bottom && dragStartY >= boundingRect.bottom)) {
                    boundObject.selected(true);
                  } else if (!boundObject.alreadySelected) {
                    boundObject.selected(false);
                  }
                });
                $('.doc-browser-drag-select').css({
                  top: startY + 'px',
                  left: startX + 'px',
                  height: Math.max(event.clientY, dragStartY) - startY + 'px',
                  width: Math.max(event.clientX, dragStartX) - startX + 'px'
                })
              }
            },
            stop: function (event) {
              $('.doc-browser-drag-select').remove();
              var elementAtStart = document.elementFromPoint(dragStartX, dragStartY);
              var elementAtStop = document.elementFromPoint(event.clientX, event.clientY);
              if (elementAtStart.nodeName === "A" && elementAtStop.nodeName === "A" && Math.sqrt((dragStartX-event.clientX)*(dragStartX-event.clientX) + (dragStartY-event.clientY)*(dragStartY-event.clientY)) < 8) {
                $(elementAtStop).trigger('click');
              }
            },
            helper: function (event) {
              if (typeof boundEntry !== 'undefined' && boundEntry.selected && boundEntry.selected()) {
                return $('<div>').addClass('doc-browser-drag-container');
              }
              return $('<div>');
            },
            appendTo: "body",
            cursorAt: {
              top: 0,
              left: 0
            }
          });

          var clickHandler = function (clickedEntry, event) {
            if (allEntries) {
              var clickedIndex = $.inArray(clickedEntry, allEntries());

              if (event.metaKey || event.ctrlKey) {
                clickedEntry.selected(!clickedEntry.selected());
              } else if (event.shiftKey) {
                var lastClickedIndex = ko.utils.domData.get(document, 'last-clicked-entry-index') || 0;
                var lower = Math.min(lastClickedIndex, clickedIndex);
                var upper = Math.max(lastClickedIndex, clickedIndex);
                for (var i = lower; i <= upper; i++) {
                  allEntries()[i].selected(true);
                }
              } else {
                $.each(allEntries(), function (idx, entry) {
                  if (entry !== clickedEntry) {
                    entry.selected(false);
                  }
                });
                clickedEntry.selected(true);
              }
              var selectedEntries = $.grep(allEntries(), function (entry) {
                return entry.selected();
              });
              ko.utils.domData.set(document, 'last-clicked-entry-index', selectedEntries.length > 0 ? clickedIndex : 0);
            }
          };

          ko.bindingHandlers.multiClick.init(element, function () {
            return {
              click: clickHandler,
              dblClick: boundEntry.open
            }
          }, allBindings, boundEntry, bindingContext);
        }
      };

      /**
       * @param {Object} params
       * @param {HueFileEntry} params.activeEntry - Observable holding the current directory
       * @constructor
       */
      function DocBrowser (params) {
        var self = this;
        self.activeEntry = params.activeEntry;

        self.searchQuery = ko.observable().extend({ throttle: 500 });
        self.searchQuery.subscribe(function (query) {
          self.activeEntry().search(query);
        });

        self.searchVisible = ko.observable(false);
        self.searchFocus = ko.observable(false);

        huePubSub.subscribe('file.browser.directory.opened', function () {
          self.searchQuery('');
          self.searchVisible(false);
          $('.tooltip').hide();
        });

        var keepSelectionSelector = '.doc-browser-entries, .doc-browser-folder-actions, .doc-browser-header, .doc-browser-search-container, .modal';
        $(document).click(function (event) {
          var $target = $(event.target);
          if (!$target.is(keepSelectionSelector) && $target.parents(keepSelectionSelector).length === 0 && self.activeEntry()) {
            self.activeEntry().selectedEntries().forEach(function (entry) {
              entry.selected(false);
            });
          }
        });
        $(window).bind('keydown', 'ctrl+a alt+a meta+a', function (e) {
          self.activeEntry().entries().forEach(function (entry) {
            entry.selected(true);
          });
          e.preventDefault();
          return false;
        });
      }

      ko.components.register('doc-browser', {
        viewModel: DocBrowser,
        template: { element: 'doc-browser-template' }
      });
    })();
  </script>
</%def>