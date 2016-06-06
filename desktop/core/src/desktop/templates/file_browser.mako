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
from desktop import conf
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
from desktop.views import _ko
%>

<%namespace name="hueIcons" file="/hue_icons.mako" />

<%def name="fileBrowser()">
  ${ hueIcons.symbols() }

  <style>
    .fb-container {
      position: absolute;
      top: 0;
      bottom: 0;
      right: 0;
      left: 0;
      display: flex;
      flex-direction: column;
    }

    .fb-action-bar,
    .fb-header {
      -ms-flex: 0 0 auto;
      flex: 0 0 auto;
      overflow: hidden;
      padding: 2px;
      clear: both;
      display: -ms-flexbox;
      display: flex;
      -ms-flex-wrap: nowrap;
      flex-wrap: nowrap;
    }

    .fb-header {
      border-bottom: 1px solid #f1f1f1;
      letter-spacing: 0.035em;
      font-size: 15px;
      color: #737373;
    }

    .fb-empty {
      letter-spacing: 0.035em;
      font-size: 15px;
      color: #737373;
      padding: 40px 0;
      text-align: center;
      -webkit-animation-name: fadeIn;
      animation-name: fadeIn;
    }

    .fb-list {
      -ms-flex: 1 1 auto;
      flex: 1 1 auto;
      overflow-y: scroll;
      overflow-x: hidden;
    }

    .fb-breadcrumbs {
      padding: 9px 9px;
      margin: 0 10px 10px 10px;
      list-style: none outside none;
    }

    .fb-breadcrumbs li {
      line-height: 36px;
      padding: 0;
      vertical-align: middle;
      display: inline-block;
      height: 36px;
      border-bottom: 2px solid transparent;
    }

    .fb-breadcrumbs .fb-drop-target {
      padding: 0 6px;
    }

    .active {
      padding: 0 12px;
      color: #444;
    }

    .fb-breadcrumbs li:not(.divider):not(.active):hover {
      border-bottom: 2px solid #338BB8;
    }

    .fb-breadcrumbs a {
      color: #338BB8 !important;
    }

    .fb-breadcrumbs a:hover {
      text-decoration: none;
    }

    .fb-main-header {
      position: relative;
    }

    .fb-folder-actions {
      display: inline-block;
      position: absolute;
      right: 10px;
      top: 14px;
      height: 50px;
      line-height: 50px;
    }

    .fb-folder-actions > div {
      float: left;
    }

    .fb-list {
      padding: 4px 0;
    }

    .fb-entries {
      list-style: none;
      margin: 0;
    }

    .fb-entries > li {
      clear: both;
      line-height: 42px;
      border: 1px solid transparent;
      margin: 1px;
      color: #444;
      font-size: 14px;
      cursor: pointer;
    }

    .fb-entries > li:hover:not(.fb-selected) {
      background-color: #E8F5FE;
    }

    .fb-selected {
      background-color: #DBE8F1;
    }

    .fb-list i {
      color: #338BB8;
      font-size: 20px;
      font-weight: lighter;
    }

    .fb-list .hi {
      color: #338BB8;
      font-size: 24px;
    }

    .fb-action {
      font-size: 25px;
      margin-left: 5px;
    }

    .fb-row {
      display: -ms-flexbox;
      display: flex;
      -ms-flex-wrap: nowrap;
      flex-wrap: nowrap;
      width: 100%;
      height: 100%;
    }

    .fb-primary-col {
      -ms-flex: 2;
      flex: 2;
      vertical-align: middle;
      padding-left: 8px;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
      padding-right: 20px;
    }

    .fb-header .fb-primary-col {
      height: 30px;
      line-height: 30px;
    }

    .fb-row .fb-primary-col {
      height: 42px;
    }

    .fb-primary-col .fa {
      vertical-align: middle;
    }

    .fb-primary-col .hi {
      vertical-align: middle;
      display: inline-block;
      margin-bottom: 0.2em;
    }

    .fb-attr-group {
      -ms-flex: 1;
      flex: 1;
      white-space: nowrap;
      float: right;
      display: inline-block;
      height: 30px;
    }

    .fb-row .fb-attr-group {
      height: 42px;
    }

    .fb-attr-col {
      display: inline-block;;
      height: 30px;
      line-height: 30px;
      vertical-align: middle;
      padding-right: 20px;
    }

    .fb-row .fb-attr-col {
      margin-bottom: 2px;
    }

    .fb-shared-icon-active {
      color: #338BB8 !important;
    }

    .fb-type {
      width: 140px;
    }

    .fb-owner {
      width: 170px;
    }

    .fb-modified {
      width: 150px;
    }

    .fb-drag-container {
      position: fixed;
    }

    .fb-drag-select {
      position: fixed;
      border: 1px solid #338BB8;
      cursor: pointer;
    }

    .fb-drag-helper {
      display: none;
      position: absolute;
      width: auto;
      text-overflow: ellipsis;
      white-space: nowrap;
      top: -15px;
      left: 10px;
      height: 30px;
      line-height: 30px;
      vertical-align: middle;
      padding: 1px 12px 1px 7px;
      cursor: pointer;
      background-color: #338BB8;
      color: #DBE8F1;
      border-radius: 2px;
      z-index: 1000;
    }

    .fb-drag-helper i {
      line-height: 30px;
      vertical-align: middle;
      margin-right: 8px;
      font-size: 16px;
    }

    .fb-drop-target {
      border: 1px solid transparent;
    }

    .fb-drop-hover {
      border: 1px solid #338BB8 !important;
    }

    .hueBreadcrumbBar a {
      color: #338BB8 !important;
      display: inline !important;
    }

    .divider {
      color: #CCC;
    }

    .large-as-modal {
      width: 95%;
    }

    @-webkit-keyframes fb-search-visible {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    @keyframes fb-search-visible {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    .fb-search-container {
      position: absolute;
      top: 26px;
      right: 330px;

      -webkit-animation-name: fb-search-visible;
      animation-name: fb-search-visible;
      -webkit-animation-duration: 0.4s;
      animation-duration: 0.4s;
    }

    .fb-search-container input {
      width: 300px;
    }

    .typeahead .active {
      padding: 0;
    }
  </style>

  <script type="text/html" id="fb-template">
    <div class="fb-drag-helper">
      <i class="fa fa-fw"></i><span class="drag-text">4 entries</span>
    </div>

    <div id="shareDocumentModal" data-keyboard="true" class="modal hide fade" tabindex="-1">
      <!-- ko with: activeEntry -->
      <!-- ko with: selectedEntry -->
      <!-- ko with: document -->
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h3>${_('Sharing')} - <span data-bind="text: $parent.definition().name"></span></h3>
      </div>
      <div class="modal-body" style="overflow-y: visible">
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
        <div class="fb-empty animated" style="display: none;" data-bind="visible: loading">
          <i class="fa fa-spinner fa-spin fa-2x" style="color: #999;"></i>
        </div>
        <div class="fb-empty animated" style="display: none;" data-bind="visible: hasErrors() && ! loading()">
          ${ _('There was an error loading the document.')}
        </div>
        <div style="margin-top: 20px" data-bind="visible: fileEntry.canModify() && ! hasErrors() && ! loading()">
          <div class="input-append">
            <input id="documentShareTypeahead" type="text" style="width: 420px" placeholder="${_('Type a username or a group name')}">
            <div class="btn-group" style="overflow:visible">
              <a class="btn" data-bind="click: function () { if (selectedUserOrGroup()) { handleTypeAheadSelection() }}, css: { 'disabled': !selectedUserOrGroup() }"><i class="fa fa-plus-circle"></i> <span data-bind="text: selectedPerm() == 'read' ? '${ _('Read') }' : '${ _('Modify') }'"></span></a>
              <a class="btn dropdown-toggle" data-bind="css: { 'disabled': !selectedUserOrGroup() }" data-toggle="dropdown"><span class="caret"></span></a>
              <ul class="dropdown-menu">
                <li><a data-bind="click: function () { selectedPerm('read') }" href="javascript:void(0)">${ _('Read') }</a></li>
                <li><a data-bind="click: function () { selectedPerm('write') }" href="javascript:void(0)">${ _('Modify') }</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <!-- ko if: selectedUserOrGroup()  -->
        <a class="btn btn-primary" data-bind="click: handleTypeAheadSelection" href="javascript:void(0)">${ _('Add') }</a>
        <!-- /ko -->
        <!-- ko ifnot: selectedUserOrGroup() -->
        <a href="#" data-dismiss="modal" class="btn btn-primary disable-feedback disable-enter">${_('Close')}</a>
        <!-- /ko -->
      </div>
      <!-- /ko -->
      <!-- /ko -->
      <!-- /ko -->
    </div>

    <div id="importDocumentsModal" data-keyboard="true" class="modal hide fade fileupload-modal" tabindex="-1">
      <!-- ko with: activeEntry -->
      <div class="modal-header">
        <a href="#" class="close" data-clear="importDocumentsForm" data-bind="click: closeUploadModal">&times;</a>
        <h3>${_('Import Hue documents')}</h3>
      </div>
        <form id="importDocumentsForm" class="form-horizontal" style="display: inline" enctype="multipart/form-data">
          <div class="modal-body">
              <div class="control-group" data-bind="visible: !uploading() && !uploadComplete()">
                <label class="control-label" for="importDocumentInput">${ _('Select json file') }</label>
                <div class="controls">
                  <input id="importDocumentInput" style="line-height: 10px; margin-top: 5px;" type="file" name="documents" accept=".json" />
                </div>
              </div>
              <span data-bind="visible: !uploadFailed() && uploadComplete()">${ _('Import complete!') }</span>
              <span data-bind="visible: uploadFailed">${ _('Import failed!') }</span>
              <progress data-bind="visible: uploading() || uploadComplete()" id="importDocumentsProgress" value="0" max="100" style="width: 560px;"></progress>
              ${ csrf_token(request) | n,unicode }
              <input type="hidden" name="path" data-bind="value: definition().path" />
          </div>
          <div class="modal-footer">
            <!-- ko ifnot: uploading() || uploadComplete() -->
            <input type="button" class="btn" data-clear="importDocumentsForm" data-bind="click: closeUploadModal" value="${ _('Cancel') }" />
            <input type="submit" class="btn btn-danger" data-bind="click: upload" value="${ _('Import') }" />
            <!-- /ko -->
            <!-- ko if: uploading() || uploadComplete() -->
            <a href="#" class="btn" data-clear="importDocumentsForm" data-bind="click: closeUploadModal">${ _('Close') }</a>
            <!-- /ko -->
          </div>
        </form>

      <!-- /ko -->
    </div>

    <div id="createDirectoryModal" data-keyboard="true" class="modal hide fade" tabindex="-1">
      <!-- ko with: activeEntry -->
      <form class="form-horizontal">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal" data-bind="click: function () { $('#newDirectoryName').val(null) }" aria-hidden="true">&times;</button>
          <h3>${_('Create Directory')}</h3>
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

    <div id="deleteEntriesModal" data-keyboard="true" class="modal hide fade" tabindex="-1">
      <!-- ko with: activeEntry -->
      <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times</a>
        <!-- ko if: entriesToDelete().length === 0 -->
        <h3>${ _('The trash is empty') }</h3>
        <!-- /ko -->
        <!-- ko if: entriesToDelete().length > 0 -->
        <h3>${ _('Do you really want to delete') }
          <!-- ko if: entriesToDelete().length == 1 --> <span data-bind="text: entriesToDelete()[0].definition().name"></span><!-- /ko -->
          <!-- ko if: entriesToDelete().length > 1 --> <span data-bind="text: entriesToDelete().length"></span> ${ _('entries') }<!-- /ko -->
        ?</h3>
        <!-- /ko -->
      </div>
      <div class="modal-footer">
        <!-- ko if: entriesToDelete().length === 0 -->
        <input type="button" class="btn" data-dismiss="modal" value="${ _('Close') }">
        <!-- /ko -->
        <!-- ko if: entriesToDelete().length > 0 -->
        <input type="button" class="btn" data-dismiss="modal" value="${ _('Cancel') }">
        <input type="submit" data-bind="click: function() { removeDocuments(true); }" class="btn btn-danger" value="${_('Yes')}"/>
        <!-- /ko -->
      </div>
      <!-- /ko -->
    </div>

    <div class="fb-container">
      <div class="fb-action-bar">
        <h4 class="fb-main-header">
          <div data-bind="with: activeEntry">
            <ul class="fb-breadcrumbs">
              <!-- ko if: isRoot -->
              <li class="active"><div class="fb-drop-target">${ _('My documents') }</div></li>
              <!-- /ko -->

              <!-- ko if: definition().isSearchResult -->
              <li class="active"><div class="fb-drop-target">${ _('Result for') }: <!-- ko text: definition().name --><!-- /ko --></div></li>
              <!-- /ko -->
              <!-- ko ifnot: definition().isSearchResult -->
              <!-- ko foreach: breadcrumbs -->
              <li><div class="fb-drop-target" data-bind="fileDroppable: { entries: $parent.entries, disableSelect: true }"><a href="javascript:void(0);" data-bind="text: isRoot() ? '${ _('My documents') }' : (isTrash() ? '${ _('Trash') }' : definition().name), click: open"></a></div></li>
              <li class="divider">&gt;</li>
              <!-- /ko -->
              <!-- ko ifnot: isRoot -->
              <li class="active"><div class="fb-drop-target" data-bind="text: isTrash() ? '${ _('Trash') }' : definition().name"></div></li>
              <!-- /ko -->
              <!-- /ko -->
            </ul>
          </div>
        </h4>
        <!-- ko if: searchVisible -->
        <div class="fb-search-container">
          <input class="clearable" type="text" placeholder="Search for name, description, etc..." data-bind="hasFocus: searchFocus, textInput: searchQuery, clearable: searchQuery">
        </div>
        <!-- /ko -->
        <!-- ko with: activeEntry -->
        <div class="fb-folder-actions" data-bind="visible: ! hasErrors()">
          <div><a class="inactive-action fb-action" title="${_('Search')}" href="javascript:void(0);" data-bind="toggle: $parent.searchVisible, click: function () { $parent.searchFocus($parent.searchVisible()) }, css: { 'blue' : ($parent.searchVisible() || $parent.searchQuery()) }"><i class="fa fa-fw fa-search"></i></a></div>
          <!-- ko if: app === 'documents' -->
          <div>
            <span class="dropdown">
              <a class="inactive-action fb-action" title="${_('New document')}" data-toggle="dropdown" data-bind="css: { 'disabled': isTrash() || isTrashed() }" href="javascript:void(0);"><span class="fa-stack fa-fw" style="width: 1.28571429em"><i class="fa fa-file-o fa-stack-1x"></i><i class="fa fa-plus-circle fa-stack-1x" style="font-size: 14px; margin-left: 6px; margin-top: 6px;"></i></span></a>
              <ul class="dropdown-menu" style="margin-top:10px; width: 175px;" role="menu">
                % if 'beeswax' in apps:
                  <li><a title="${_('Hive Query')}" data-bind="attr: { href: addDirectoryParamToUrl('${ url('notebook:editor') }?type=hive') }"><img src="${ static(apps['beeswax'].icon_path) }" class="app-icon"/> ${_('Hive Query')}</a></li>
                % endif
                % if 'impala' in apps:
                  <li><a title="${_('Impala Query')}" data-bind="attr: { href: addDirectoryParamToUrl('${ url('notebook:editor') }?type=impala') }"><img src="${ static(apps['impala'].icon_path) }" class="app-icon"/> ${_('Impala Query')}</a></li>
                % endif
                % if 'pig' in apps:
                  <li><a title="${_('Pig Script')}" data-bind="attr: { href: addDirectoryParamToUrl('${ url('pig:index') }') }"><img src="${ static(apps['pig'].icon_path) }" class="app-icon"/> ${_('Pig Script')}</a></li>
                % endif
                <%
                from notebook.conf import SHOW_NOTEBOOKS
                %>
                % if SHOW_NOTEBOOKS.get():
                  <li><a title="${_('Notebook')}" data-bind="attr: { href: addDirectoryParamToUrl('${ url('notebook:index') }') }"><i style="font-size: 24px; line-height: 24px; vertical-align: middle; color: #338BB8;" class="fa app-icon fa-fw fa-file-text-o"></i> ${_('Notebook')}</a></li>
                % endif
                % if 'oozie' in apps:
                  <li><a title="${_('Oozie Workflow')}" data-bind="attr: { href: addDirectoryParamToUrl('${ url('oozie:new_workflow') }') }"><img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon"/> ${_('Oozie Workflow')}</a></li>
                  <li><a title="${_('Oozie Coordinator')}" data-bind="attr: { href: addDirectoryParamToUrl('${ url('oozie:new_coordinator') }') }"><img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon"/> ${_('Oozie Coordinator')}</a></li>
                  <li><a title="${_('Oozie Bundle')}" data-bind="attr: { href: addDirectoryParamToUrl('${ url('oozie:new_bundle') }') }"><img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon"/> ${_('Oozie Bundle')}</a></li>
                % endif
                % if 'search' in apps:
                  <li><a title="${_('Solr Search')}" data-bind="attr: { href: addDirectoryParamToUrl('${ url('search:index') }') }"><img src="${ static('search/art/icon_search_48.png') }" class="app-icon"/>${_('Search Dashboard')}</a></li>
                % endif
              </ul>
            </span>
          </div>
          <!-- /ko -->
          <div><a class="inactive-action fb-action" title="${_('New folder')}" href="javascript:void(0);" data-bind="click: function () { showNewDirectoryModal() }, css: { 'disabled': isTrash() || isTrashed() }"><span class="fa-stack fa-fw" style="width: 1.28571429em;"><i class="fa fa-folder-o fa-stack-1x" ></i><i class="fa fa-plus-circle fa-stack-1x" style="font-size: 14px; margin-left: 7px; margin-top: 3px;"></i></span></a></div>
          <div><a class="inactive-action fb-action" href="javascript:void(0);" data-bind="click: function () { if (isTrash() || isTrashed() || (sharedWithMeSelected() && superuser)) { showDeleteConfirmation() } else { moveToTrash() } }, css: { 'disabled': selectedEntries().length === 0 || (sharedWithMeSelected() && ! superuser) }, attr: { 'title' : isTrash() || isTrashed() || (sharedWithMeSelected() && superuser) ? '${ _('Delete forever') }' : '${ _('Move to trash') }' }"><i class="fa fa-fw fa-times"></i></a></div>
          <!-- ko if: app === 'documents' -->
          <div><a class="inactive-action fb-action" title="${_('Share')}" href="javascript:void(0);" data-bind="click: function() { showSharingModal(null) }, css: { 'disabled': selectedEntries().length !== 1 || (selectedEntries().length === 1 && selectedEntries()[0].isTrashed) }"><i class="fa fa-fw fa-users"></i></a></div>
          <!-- /ko -->
          <div style="margin-top: 2px"><a class="inactive-action fb-action" title="${_('Download')}" href="javascript:void(0);" data-bind="click: download"><i class="fa fa-fw fa-download"></i></a></div>
          <div><a class="inactive-action fb-action" title="${_('Upload')}" href="javascript:void(0);" data-bind="click: showUploadModal, css: { 'disabled': isTrash() || isTrashed() }"><i class="fa fa-fw fa-upload"></i></a></div>
          <!-- ko if: app === 'documents' -->
          <div class="margin-left-20" data-bind="contextMenu: { menuSelector: '.hue-context-menu' }">
            <a class="inactive-action fb-action" title="${_('Show trash')}" href="javascript:void(0);" data-bind="click: showTrash, trashDroppable, css: { 'blue' : isTrash() || isTrashed() }">
              <i class="fa fa-fw fa-trash-o"></i>
            </a>
            <ul class="hue-context-menu">
              <li><a href="javascript:void(0);" data-bind="click: emptyTrash"><i class="fa fa-fw fa-times"></i> ${ _('Empty trash') }</a></li>
            </ul>
          </div>
          <!-- /ko -->
        </div>
        <!-- /ko -->
      </div>

      <!-- ko with: activeEntry -->
      <!-- ko if: entries().length > 0 -->
      <div class="fb-header">
        <div class="fb-primary-col" data-bind="click: function () { setSort('name') }, css: { 'sorting_asc' : activeSort() === 'nameAsc', 'sorting_desc' : activeSort() === 'nameDesc', 'sorting' : activeSort().indexOf('name') !== 0 }">${ _('Name') }</div>
        <div class="fb-attr-group">
          <div class="fb-attr-col fb-type" data-bind="click: function () { setSort('type') }, css: { 'sorting_asc' : activeSort() === 'typeAsc', 'sorting_desc' : activeSort() === 'typeDesc', 'sorting' : activeSort().indexOf('type') !== 0 }">${ _('Type') }</div>
          <div class="fb-attr-col fb-owner" data-bind="click: function () { setSort('owner') }, css: { 'sorting_asc' : activeSort() === 'ownerAsc', 'sorting_desc' : activeSort() === 'ownerDesc', 'sorting' : activeSort().indexOf('owner') !== 0 }">${ _('Owner') }</div>
          <div class="fb-attr-col fb-modified" data-bind="click: function () { setSort('lastModified') }, css: { 'sorting_asc' : activeSort() === 'lastModifiedAsc', 'sorting_desc' : activeSort() === 'lastModifiedDesc', 'sorting' : activeSort().indexOf('lastModified') !== 0 }">${ _('Last Modified') }</div>
        </div>
      </div>
      <!-- /ko -->

      <div class="fb-empty animated" style="display:none;" data-bind="visible: entries().length == 0 && ! hasErrors() && ! loading() && ! definition().isSearchResult && ! isTrash()">
        ${ _('The current folder is empty, you can add a new file or folder form the top right menu')}
      </div>
      <div class="fb-empty animated" style="display:none;" data-bind="visible: entries().length == 0 && ! hasErrors() && ! loading() && ! definition().isSearchResult && isTrash()">
        ${ _('The trash is empty')}
      </div>
      <div class="fb-empty animated" style="display:none;" data-bind="visible: entries().length == 0 && ! hasErrors() && ! loading() && definition().isSearchResult">
        ${ _('No documents found matching your query')}
      </div>
      <div class="fb-empty animated" style="display: none;" data-bind="visible: hasErrors() && app === 'documents' && ! loading()">
        ${ _('There was an error loading the documents')}
      </div>
      <div class="fb-empty animated" style="display: none;" data-bind="visible: entries().length === 0 && loading()">
        <i class="fa fa-spinner fa-spin fa-2x" style="color: #999;"></i>
      </div>
      <!-- /ko -->

      <div class="fb-list" data-bind="with: activeEntry" >
        <ul class="fb-entries" data-bind="foreachVisible: { data: entries, minHeight: 39, container: '.fb-list' }">
          <li data-bind="fileSelect: $parent.entries, fileDroppable: { entries: $parent.entries }, css: { 'fb-selected': selected }">
            <div class="fb-row" data-bind="contextMenu: { scrollContainer: '.fb-list', menuSelector: '.hue-context-menu', beforeOpen: beforeContextOpen }">
              <ul class="hue-context-menu">
                <!-- ko if: isTrashed -->
                <li><a href="javascript:void(0);" data-bind="click: function() { $parent.showDeleteConfirmation(); }"><i class="fa fa-fw fa-times"></i> ${ _('Delete') } <span data-bind="visible: $parent.selectedEntries().length > 1, text: '(' + $parent.selectedEntries().length + ')'"></span></a></li>
                <!-- /ko -->
                <!-- ko ifnot: isTrashed -->
                <li data-bind="css: { 'disabled': $parent.selectedEntries().length !== 1 }"><a href="javascript:void(0);" data-bind="click: open, css: { 'disabled': $parent.selectedEntries().length !== 1 }"><i class="fa fa-fw fa-file-o"></i> ${ _('Open') }</a></li>
                <li><a href="javascript:void(0);" data-bind="click: contextMenuDownload"><i class="fa fa-fw fa-download"></i> ${ _('Download') } <span data-bind="visible: $parent.selectedEntries().length > 1, text: '(' + $parent.selectedEntries().length + ')'"></span></a></li>
                <li data-bind="visible: ! $altDown() && !($parent.sharedWithMeSelected() && $parent.superuser), css: { 'disabled' : $parent.sharedWithMeSelected()  && ! $parent.superuser }"><a href="javascript:void(0);" data-bind="click: function () { $parent.moveToTrash(); }, css: { 'disabled' : $parent.sharedWithMeSelected() && ! $parent.superuser }"><i class="fa fa-fw fa-trash-o"></i> ${ _('Move to trash') } <span data-bind="visible: $parent.selectedEntries().length > 1, text: '(' + $parent.selectedEntries().length + ')'"></span></a></li>
                <li data-bind="visible: $altDown() || ($parent.sharedWithMeSelected() && $parent.superuser), css: { 'disabled' : $parent.sharedWithMeSelected() && ! $parent.superuser }"><a href="javascript:void(0);" data-bind="click: function() { $parent.showDeleteConfirmation(); }, css: { 'disabled' : $parent.sharedWithMeSelected() && ! $parent.superuser}"><i class="fa fa-fw fa-times"></i> ${ _('Delete forever') } <span data-bind="visible: $parent.selectedEntries().length > 1, text: '(' + $parent.selectedEntries().length + ')'"></span></a></li>
                <li data-bind="css: { 'disabled': $parent.selectedEntries().length !== 1 }"><a href="javascript:void(0);" data-bind="click: function() { $parent.showSharingModal(); }, css: { 'disabled': $parent.selectedEntries().length !== 1 }"><i class="fa fa-fw fa-users"></i> ${ _('Share') }</a> </li>
                <!-- /ko -->
              </ul>
              <div class="fb-primary-col">
                <svg class="hi">
                  <!-- ko if: isDirectory -->
                  <use xlink:href="#hi-folder"></use>
                  <!-- /ko -->
                  <!-- ko ifnot: isDirectory -->
                  <!-- ko switch: definition().type -->
                  <!-- ko case: 'link-pigscript' --><use xlink:href="#hi-file-pig"></use><!-- /ko -->
                  <!-- ko case: 'link-workflow' --><use xlink:href="#hi-file-job-designer"></use><!-- /ko -->
                  <!-- ko case: 'notebook' --><use xlink:href="#hi-file-notebook"></use><!-- /ko -->
                  <!-- ko case: 'oozie-bundle2' --><use xlink:href="#hi-file-oozie-bundle"></use><!-- /ko -->
                  <!-- ko case: 'oozie-coordinator2' --><use xlink:href="#hi-file-oozie-coordinator"></use><!-- /ko -->
                  <!-- ko case: 'oozie-workflow2' --><use xlink:href="#hi-file-oozie-workflow"></use><!-- /ko -->
                  <!-- ko case: 'query-hive' --><use xlink:href="#hi-file-hive"></use><!-- /ko -->
                  <!-- ko case: 'query-impala' --><use xlink:href="#hi-file-impala"></use><!-- /ko -->
                  <!-- ko case: 'search-dashboard' --><use xlink:href="#hi-file-search"></use><!-- /ko -->
                  <!-- ko case: $default --><use xlink:href="#hi-file"></use><!-- /ko -->
                  <!-- /ko -->
                  <!-- /ko -->

                  <!-- ko if: (isShared() || isSharedWithMe()) && selected() -->
                  <use xlink:href="#hi-share-addon-selected"></use>
                  <!-- /ko -->
                  <!-- ko if: (isShared() || isSharedWithMe()) && !selected() -->
                  <use xlink:href="#hi-share-addon"></use>
                  <!-- /ko -->
                </svg>
                <a href="javascript: void(0);" data-bind="text: definition().name, click: open, attr: { 'title': definition().name, 'href': definition().type === 'directory' ? '#' : definition().absoluteUrl }" class="margin-left-5"></a>
              </div>
              <div class="fb-attr-group">
                <!-- ko with: definition -->
                <div class="fb-attr-col fb-type">
                  <!-- ko switch: type -->
                  <!-- ko case: 'directory' -->${ _('Directory')}<!-- /ko -->
                  <!-- ko case: 'link-pigscript' -->${ _('Pig Script')}<!-- /ko -->
                  <!-- ko case: 'link-workflow' -->${ _('Job Design')}<!-- /ko -->
                  <!-- ko case: 'notebook' -->${ _('Notebook')}<!-- /ko -->
                  <!-- ko case: 'oozie-bundle2' -->${ _('Oozie Bundle')}<!-- /ko -->
                  <!-- ko case: 'oozie-coordinator2' -->${ _('Oozie Coordinator')}<!-- /ko -->
                  <!-- ko case: 'oozie-workflow2' -->${ _('Oozie Workflow')}<!-- /ko -->
                  <!-- ko case: 'query-hive' -->${ _('Hive Query')}<!-- /ko -->
                  <!-- ko case: 'query-impala' -->${ _('Impala Query')}<!-- /ko -->
                  <!-- ko case: 'search-dashboard' -->${ _('Search Dashboard')}<!-- /ko -->
                  <!-- ko case: $default -->
                  <!-- ko text: $value --><!-- /ko -->
                  <!-- /ko -->
                  <!-- /ko -->
                </div>
                <div class="fb-attr-col fb-owner" data-bind="text: owner, attr: { 'title': owner }"></div>
                <div class="fb-attr-col fb-modified" data-bind="text: localeFormat(last_modified)"></div>
                <!-- /ko -->
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    (function (factory) {
      if(typeof require === "function") {
        define('fileBrowser', [
          'knockout',
          'ko.switch-case'
        ], factory);
      } else {
        factory(ko);
      }
    }(function (ko) {

      ko.bindingHandlers.trashDroppable = {
        init: function(element, valueAccessor, allBindings, boundEntry) {
          var dragData;
          huePubSub.subscribe('file.browser.dragging', function (data) {
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

      ko.bindingHandlers.fileDroppable = {
        init: function(element, valueAccessor, allBindings, boundEntry, bindingContext) {
          var options = valueAccessor();
          var allEntries = options.entries;
          var disableSelect = options.disableSelect || false;
          var $element = $(element);
          var dragToSelect = false;
          var alreadySelected = false;
          huePubSub.subscribe('fb.drag.to.select', function (value) {
            alreadySelected = boundEntry.selected();
            dragToSelect = value;
          });
          $element.droppable({
            drop: function (ev, ui) {
              if (! dragToSelect && boundEntry.isDirectory()) {
                var entriesToMove = $.grep(allEntries(), function (entry) {
                  return entry.selected() && ! entry.isSharedWithMe();
                });
                if (entriesToMove.length > 0) {
                  boundEntry.moveHere(entriesToMove);
                  boundEntry.load();
                }
              }
              $element.removeClass('fb-drop-hover');
            },
            over: function () {
              if (dragToSelect && ! disableSelect) {
                boundEntry.selected(true);
              } else if (! dragToSelect && boundEntry.isDirectory()) {
                var movableCount = allEntries().filter(function (entry) {
                  return entry.selected() && ! entry.isSharedWithMe();
                }).length;
                if (movableCount > 0) {
                  $element.addClass('fb-drop-hover');
                }
              }
            },
            out: function (event, ui) {
              if (!(alreadySelected && (event.metaKey || event.ctrlKey)) && dragToSelect && ! disableSelect) {
                var originTop = ui.draggable[0].getBoundingClientRect().top;
                var elementMiddle = element.getBoundingClientRect().top + (element.getBoundingClientRect().height / 2)
                if ((originTop > elementMiddle && ui.position.top > elementMiddle) ||
                    (originTop < elementMiddle && ui.position.top < elementMiddle)) {
                  boundEntry.selected(false);
                }
              } else if (! dragToSelect && boundEntry.isDirectory()) {
                $element.removeClass('fb-drop-hover');
              }
            }
          })
        }
      };

      ko.bindingHandlers.fileSelect = {
        init: function(element, valueAccessor, allBindings, boundEntry, bindingContext) {
          var $element = $(element);
          $element.attr('unselectable', 'on').css('user-select', 'none').on('selectstart', false);
          var allEntries = valueAccessor();

          var dragStartY = -1;
          var dragStartX = -1;
          var dragToSelect = false;
          $element.draggable({
            start: function (event, ui) {
              var $container = $('.fb-drag-container');

              var selectedEntries = $.grep(allEntries(), function (entry) {
                return entry.selected();
              });

              dragToSelect = ! boundEntry.selected();

              huePubSub.publish('file.browser.dragging', {
                selectedEntries: selectedEntries,
                originEntry: boundEntry.parent,
                dragToSelect: dragToSelect
              });

              dragStartX = event.clientX;
              dragStartY = event.clientY;

              huePubSub.publish('fb.drag.to.select', dragToSelect);

              if (dragToSelect && selectedEntries.length > 0 && ! (event.metaKey || event.ctrlKey)){
                $.each(selectedEntries, function (idx, selectedEntry) {
                  if (selectedEntry !== boundEntry) {
                   selectedEntry.selected(false);
                  }
                });
                selectedEntries = [];
              }

              boundEntry.selected(true);

              if (! dragToSelect) {
                var $helper = $('.fb-drag-helper').clone().show();
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
                  $helper.find('i').removeClass().addClass($element.find('.fb-primary-col i').attr('class'));
                }

                $helper.appendTo($container);
              } else {
                $('<div>').addClass('fb-drag-select').appendTo('body');
              }
            },
            drag: function (event) {
              var startX = Math.min(event.clientX, dragStartX);
              var startY = Math.min(event.clientY, dragStartY);
              if (dragToSelect) {
                $('.fb-drag-select').css({
                  top: startY + 'px',
                  left: startX + 'px',
                  height: Math.max(event.clientY, dragStartY) - startY + 'px',
                  width: Math.max(event.clientX, dragStartX) - startX + 'px'
                })
              }
            },
            stop: function (event) {
              $('.fb-drag-select').remove();
              var elementAtStart = document.elementFromPoint(dragStartX, dragStartY);
              var elementAtStop = document.elementFromPoint(event.clientX, event.clientY);
              if (elementAtStart.nodeName === "A" && elementAtStop.nodeName === "A" && Math.sqrt((dragStartX-event.clientX)*(dragStartX-event.clientX) + (dragStartY-event.clientY)*(dragStartY-event.clientY)) < 8) {
                $(elementAtStop).trigger('click');
              }
            },
            helper: function (event) {
              if (boundEntry.selected()) {
                return $('<div>').addClass('fb-drag-container');
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
            var clickedIndex = $.inArray(clickedEntry, allEntries());

            if (event.metaKey || event.ctrlKey) {
              clickedEntry.selected(!clickedEntry.selected());
            } else if (event.shiftKey) {
              var lastClickedIndex = ko.utils.domData.get(document, 'last-clicked-file-index') || 0;
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
            ko.utils.domData.set(document, 'last-clicked-file-index', selectedEntries.length > 0 ? clickedIndex : 0);
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
      function FileBrowser (params) {
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
        });

        $(document).click(function (event) {
          var $target = $(event.target);
          if ($target.parents('.fb-entries, .fb-folder-actions, .fb-header, .fb-search-container, .modal').length === 0) {
            self.activeEntry().selectedEntries().forEach(function (entry) {
              entry.selected(false);
            });
          }
        });
      }

      ko.components.register('file-browser', {
        viewModel: FileBrowser,
        template: { element: 'fb-template' }
      });
    }));
  </script>
</%def>