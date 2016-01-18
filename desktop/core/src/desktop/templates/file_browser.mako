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

<%def name="fileBrowser()">
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
      flex: 0 0 auto;

      overflow: hidden;
      padding: 2px;
      clear: both;
    }

    .fb-header {
      border-bottom: 1px solid #f1f1f1;
      letter-spacing: 0.035em;
      font-size: 15px;
      color: #737373;
    }

    .fb-list {
      flex: 1 1 auto;
      overflow-y: scroll;
      overflow-x: hidden;
    }

    .fb-breadcrumb {
      display: inline-block;
    }

    .fb-folder-actions {
      display: inline-block;
      position: absolute;
      right: 10px;
      top: 0;
      height: 50px;
      line-height: 50px;
    }

    .fb-list ul {
      list-style: none;
      padding: 4px 0;
      margin: 0;
    }

    .fb-list li {
      clear: both;
      height: 35px;
      line-height: 35px;
      padding: 2px;
      margin: 0;
      color: #444;
      font-size: 13px;
      cursor: pointer;
    }

    .fb-selected {
      background-color: #DBE8F1;
    }

    .fb-list i {
      color: #666;
      font-size: 20px;
      margin-right: 8px;
      font-weight: lighter;
    }

    .fb-action {
      font-size: 25px;
      margin-left: 5px;
    }

    .fb-primary-col {
      float: left;
      display: inline-block;
      height: 30px;
      vertical-align: middle;
      padding-left: 8px;
      text-overflow: ellipsis;
    }

    .fb-primary-col .fa {
      vertical-align: middle;
    }

    .fb-attr-group {
      float: right;
      display: inline-block;
      height: 30px;
    }

    .fb-attr-col {
      display: inline-block;;
      height: 30px;
      line-height: 30px;
      vertical-align: middle;
    }

    .active-breadcrumb {
      padding: 0 12px;
      color: #444;
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

    .hueBreadcrumbBar a {
      color: #338BB8 !important;
      display: inline !important;
    }

    .divider {
      color: #CCC;
    }
  </style>

  <script type="text/html" id="fb-template">
    <div id="importDocumentsModal" class="modal hide fade fileupload-modal">
      <!-- ko with: currentDirectory -->
      <div class="modal-header">
        <a href="#" class="close" data-clear="importDocumentsForm" data-bind="click: closeUploadModal">&times;</a>
        <h3>${_('Import Hue documents')}</h3>
      </div>
        <div class="modal-body form-horizontal">
          <form id="importDocumentsForm" style="display: inline" enctype="multipart/form-data">
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
            <input type="hidden" name="path" data-bind="value: path" />
          </form>
        </div>
        <div class="modal-footer">
          <!-- ko ifnot: uploading() || uploadComplete() -->
          <a href="#" class="btn" data-clear="importDocumentsForm" data-bind="click: closeUploadModal">${ _('Cancel') }</a>
          <a herf="#" class="btn btn-danger" data-bind="click: upload">${ _('Import') }</a>
          <!-- /ko -->
          <!-- ko if: uploading() || uploadComplete() -->
          <a href="#" class="btn" data-clear="importDocumentsForm" data-bind="click: closeUploadModal">${ _('Close') }</a>
          <!-- /ko -->
        </div>

      <!-- /ko -->
    </div>
    <div id="createDirectoryModal" class="modal hide fade">
      <!-- ko with: currentDirectory -->
      <div class="modal-body form-horizontal">
        <div class="control-group">
          <label class="control-label" for="newDirectoryName">${ _('Name') }</label>
          <div class="controls">
            <input id="newDirectoryName" type="text" /></label>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <input type="button" class="btn" data-dismiss="modal" value="${ _('Cancel') }">
        <input type="button" class="btn" value="${ _('Create') }" data-bind="click: function () { $data.createDirectory($('#newDirectoryName').val()); $('#createDirectoryModal').modal('hide'); }"/>
      </div>
      <!-- /ko -->
    </div>
    <div id="deleteDirectoryModal" class="modal hide fade">
      <!-- ko with: currentDirectory -->
      <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times</a>
        <h3>${ _('Do you really want to delete:') } <span data-bind="text: name"></span></h3>
      </div>
      <div class="modal-footer">
        <input type="button" class="btn" data-dismiss="modal" value="${ _('Cancel') }">
        <input type="submit" data-bind="click: function () { $parents[1].currentDirectory($data.parent); $data.delete(); $('#deleteDirectoryModal').modal('hide'); }" class="btn btn-danger" value="${_('Yes')}"/>
      </div>
      <!-- /ko -->
    </div>
    <div class="fb-container">
      <div class="fb-action-bar">
        <h4>
          <div class="fb-breadcrumb" data-bind="with: currentDirectory">
            <ul class="nav nav-pills hueBreadcrumbBar">
              <!-- ko if: isRoot -->
              <li class="active-breadcrumb">${ _('My documents') }</li>
              <!-- /ko -->

              <!-- ko foreach: breadcrumbs -->
              <li><a href="javascript:void(0);" data-bind="text: isRoot ? '${ _('My documents') }' : name, click: function () { $parents[1].currentDirectory($data); } "></a> <span class="divider">&gt;</span></li>
              <!-- /ko -->
              <!-- ko ifNot: isRoot -->
              <li class="active-breadcrumb" data-bind="text: name"></li>
              <!-- /ko -->
            </ul>
          </div>
        </h4>
        <div class="fb-folder-actions" data-bind="with: currentDirectory">
          <!-- ko if: app === 'documents' -->
          <span class="dropdown">
            <a class="inactive-action fb-action" data-toggle="dropdown" href="javascript:void(0);"><span class="fa-stack fa-fw" style="width: 1.28571429em"><i class="fa fa-file-o fa-stack-1x"></i><i class="fa fa-plus-circle fa-stack-1x" style="font-size: 14px; margin-left: 6px; margin-top: 6px;"></i></span></a>
            <ul class="dropdown-menu" style="margin-top:10px; width: 175px;" role="menu">
              % if 'beeswax' in apps:
                <li><a href="${ url('beeswax:index') }"><img src="${ static(apps['beeswax'].icon_path) }" class="app-icon"/> ${_('Hive Query')}</a></li>
              % endif
              % if 'impala' in apps:
                <li><a href="${ url('impala:index') }"><img src="${ static(apps['impala'].icon_path) }" class="app-icon"/> ${_('Impala Query')}</a></li>
              % endif
              % if 'pig' in apps:
                <li><a href="${ url('pig:index') }"><img src="${ static(apps['pig'].icon_path) }" class="app-icon"/> ${_('Pig Script')}</a></li>
              % endif
              % if 'spark' in apps:
                <li><a href="${ url('notebook:index') }"><img src="${ static(apps['spark'].icon_path) }" class="app-icon"/> ${_('Spark Job')}</a></li>
              % endif
              % if 'oozie' in apps:
                <li><a href="${ url('oozie:new_workflow') }"><img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="app-icon"/> ${_('Oozie Workflow')}</a></li>
                <li><a href="${ url('oozie:new_coordinator') }"><img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="app-icon"/> ${_('Oozie Coordinator')}</a></li>
                <li><a href="${ url('oozie:new_bundle') }"><img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="app-icon"/> ${_('Oozie Bundle')}</a></li>
              % endif
            </ul>
          </span>
          <!-- /ko -->
          <a class="inactive-action fb-action" href="javascript:void(0);" data-bind="click: function () { $('#createDirectoryModal').modal('show'); }"><span class="fa-stack fa-fw" style="width: 1.28571429em;"><i class="fa fa-folder-o fa-stack-1x" ></i><i class="fa fa-plus-circle fa-stack-1x" style="font-size: 14px; margin-left: 7px; margin-top: 3px;"></i></span></a>
          <!-- ko ifnot: isRoot -->
          <a class="inactive-action fb-action" href="javascript:void(0);" data-bind="click: function () { $('#deleteDirectoryModal').modal('show'); }"><i class="fa fa-fw fa-times"></i></a>
          <!-- /ko -->
          <a class="inactive-action fb-action" href="javascript:void(0);"><i class="fa fa-fw fa-users"></i></a>
          <a class="inactive-action fb-action" href="javascript:void(0);" data-bind="click: download"><i class="fa fa-fw fa-download"></i></a>
          <a class="inactive-action fb-action" href="javascript:void(0);" data-bind="click: showUploadModal"><i class="fa fa-fw fa-upload"></i></a>
        </div>
      </div>
      <div class="fb-header">
        <div class="fb-primary-col">${ _('Name') }</div>
        <div class="fb-attr-group">
          <div class="fb-attr-col fb-type">${ _('Type') }</div>
          <div class="fb-attr-col fb-owner">${ _('Owner') }</div>
          <div class="fb-attr-col fb-modified">${ _('Last Modified') }</div>
        </div>
      </div>
      <div class="fb-list" data-bind="with: currentDirectory">
        <ul data-bind="foreach: { data: entries, itemHeight: 39, scrollableElement: '.fb-list' }">
          <li data-bind="fileSelect: $parent.entries, css: { 'fb-selected': selected }">
            <div style="width: 100%; height: 100%" data-bind="contextMenu: '.hue-context-menu'">
              <ul class="hue-context-menu">
                <li><a href="javascript:void(0);" data-bind="click: contextMenuDownload"><i class="fa fa-download"></i> ${ _('Download') }</a></li>
              </ul>
              <div class="fb-primary-col">
                <i class="fa fa-fw" data-bind="css: { 'fa-folder-o' : definition.type === 'directory', 'fa-file-o': definition.type !== 'directory' }"></i>
                <a href="javascript: void(0);" data-bind="text: name, click: open"></a>
              </div>
              <div class="fb-attr-group">
                <!-- ko with: definition -->
                <div class="fb-attr-col fb-type" data-bind="text: type"></div>
                <div class="fb-attr-col fb-owner" data-bind="text: owner"></div>
                <div class="fb-attr-col fb-modified" data-bind="text: last_modified"></div>
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
          'knockout'
        ], factory);
      } else {
        factory(ko);
      }
    }(function (ko) {

      ko.bindingHandlers.fileSelect = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
          $(element).attr('unselectable', 'on').css('user-select', 'none').on('selectstart', false);

          var allEntries = valueAccessor();

          var clickHandler = function (clickedEntry, event) {
            var clickedIndex = $.inArray(clickedEntry, allEntries());

            if (event.metaKey) {
              clickedEntry.selected(!clickedEntry.selected());
            } else if (event.shiftKey) {
              var lastClickedIndex = ko.utils.domData.get(document, 'last-clicked-file-index');
              var lower = Math.min(lastClickedIndex, clickedIndex);
              var upper = Math.max(lastClickedIndex, clickedIndex);
              for (var i = lower; i <= upper; i++) {
                allEntries()[i].selected(true);
              }
            } else {
              var otherSelected = false;
              $.each(allEntries(), function (idx, entry) {
                if (entry !== clickedEntry) {
                  otherSelected = otherSelected || entry.selected();
                  entry.selected(false);
                }
              });
              if (otherSelected) {
                clickedEntry.selected(true);
              } else {
                clickedEntry.selected(! clickedEntry.selected());
              }
            }

            ko.utils.domData.set(document, 'last-clicked-file-index', clickedIndex);
          };

          ko.bindingHandlers.multiClick.init(element, function () {
            return {
              click: clickHandler,
              dblClick: viewModel.open
            }
          }, allBindings, viewModel, bindingContext);
        }
      };

      /**
       * @param {Object} params
       * @param {HueFileEntry} params.currentDirectory - Observable holding the current directory
       * @constructor
       */
      function FileBrowser (params) {
        var self = this;
        self.currentDirectory = params.currentDirectory;
      }

      ko.components.register('file-browser', {
        viewModel: FileBrowser,
        template: { element: 'fb-template' }
      });
    }));
  </script>
</%def>