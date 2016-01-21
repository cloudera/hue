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
      flex: 1 1 auto;
      overflow-y: scroll;
      overflow-x: hidden;
    }

    .fb-breadcrumbs {
      padding: 9px 9px;
      margin: 10px;
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
      border: 1px solid transparent;
      margin: 1px;
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
  </style>

  <script type="text/html" id="fb-template">
    <div class="fb-drag-helper">
      <i class="fa fa-fw"></i><span class="drag-text">4 entries</span>
    </div>
    <div id="importDocumentsModal" class="modal hide fade fileupload-modal">
      <!-- ko with: activeEntry -->
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
      <!-- ko with: activeEntry -->
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
    <div id="deleteEntriesModal" class="modal hide fade">
      <!-- ko with: activeEntry -->
      <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times</a>
        <h3>${ _('Do you really want to delete') }
          <!-- ko if: entriesToDelete().length == 1 --> <span data-bind="text: entriesToDelete()[0].name"></span><!-- /ko -->
          <!-- ko if: entriesToDelete().length > 1 --> <span data-bind="text: entriesToDelete().length"></span> ${ _('entries') }<!-- /ko -->
        </h3>
      </div>
      <div class="modal-footer">
        <input type="button" class="btn" data-dismiss="modal" value="${ _('Cancel') }">
        <input type="submit" data-bind="click: performDelete" class="btn btn-danger" value="${_('Yes')}"/>
      </div>
      <!-- /ko -->
    </div>
    <div class="fb-container">
      <div class="fb-action-bar">
        <h4>
          <div data-bind="with: activeEntry">
            <ul class="fb-breadcrumbs">
              <!-- ko if: isRoot -->
              <li class="active"><div class="fb-drop-target">${ _('My documents') }</div></li>
              <!-- /ko -->

              <!-- ko foreach: breadcrumbs -->
              <li><div class="fb-drop-target" data-bind="folderDroppable: $parent.entries"><a href="javascript:void(0);" data-bind="text: isRoot ? '${ _('My documents') }' : name, click: open"></a></div></li>
              <li class="divider">&gt;</li>
              <!-- /ko -->
              <!-- ko ifNot: isRoot -->
              <li class="active"><div class="fb-drop-target" data-bind="text: name"></div></li>
              <!-- /ko -->
            </ul>
          </div>
        </h4>
        <!-- ko with: activeEntry -->
        <div class="fb-folder-actions" data-bind="visible: ! hasErrors()">
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
          <!-- ko if: !isRoot || selectedEntries().length > 0 -->
          <a class="inactive-action fb-action" href="javascript:void(0);" data-bind="click: topMenuDelete"><i class="fa fa-fw fa-times"></i></a>
          <!-- /ko -->
          <!-- ko if: isRoot && selectedEntries().length == 0 -->
          <span class="inactive-action fb-action"><i class="fa fa-fw fa-times"></i></span>
          <!-- /ko -->
          <a class="inactive-action fb-action" href="javascript:void(0);"><i class="fa fa-fw fa-users"></i></a>
          <a class="inactive-action fb-action" href="javascript:void(0);" data-bind="click: download"><i class="fa fa-fw fa-download"></i></a>
          <a class="inactive-action fb-action" href="javascript:void(0);" data-bind="click: showUploadModal"><i class="fa fa-fw fa-upload"></i></a>
        </div>
        <!-- /ko -->
      </div>

      <!-- ko with: activeEntry -->
      <!-- ko if: entries().length > 0 -->
      <div class="fb-header">
        <div class="fb-primary-col">${ _('Name') }</div>
        <div class="fb-attr-group">
          <div class="fb-attr-col fb-type">${ _('Type') }</div>
          <div class="fb-attr-col fb-owner">${ _('Owner') }</div>
          <div class="fb-attr-col fb-modified">${ _('Last Modified') }</div>
        </div>
      </div>
      <!-- /ko -->

      <div class="fb-empty animated" style="display:none;" data-bind="visible: entries().length == 0 && ! hasErrors() && ! loading()">
        ${ _('The current folder is empty. You can add a new file or folder form the top right menu.')}
      </div>
      <div class="fb-empty animated" style="display: none;" data-bind="visible: hasErrors() && app === 'documents' && ! loading()">
        ${ _('There was an error loading the documents.')}
      </div>
      <div class="fb-empty animated" style="display: none;" data-bind="visible: loading">
        <i class="fa fa-spinner fa-spin fa-2x" style="color: #999;"></i>
      </div>
      <!-- /ko -->


      <div class="fb-list" data-bind="with: activeEntry">
        <ul data-bind="foreach: { data: entries, itemHeight: 39, scrollableElement: '.fb-list' }">
          <li data-bind="fileSelect: $parent.entries, folderDroppable: $parent.entries, css: { 'fb-selected': selected }">
            <div style="width: 100%; height: 100%" data-bind="contextMenu: '.hue-context-menu'">
              <ul class="hue-context-menu">
                <li><a href="javascript:void(0);" data-bind="click: contextMenuDownload"><i class="fa fa-download"></i> ${ _('Download') }</a></li>
                <li><a href="javascript:void(0);" data-bind="click: contextMenuDelete"><i class="fa fa-fw fa-times"></i> ${ _('Delete') }</a></li>
              </ul>
              <div class="fb-primary-col">
                <i class="fa fa-fw" data-bind="css: { 'fa-folder-o' : isDirectory, 'fa-file-o': ! isDirectory }"></i>
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

      ko.bindingHandlers.folderDroppable = {
        init: function(element, valueAccessor, allBindings, boundEntry, bindingContext) {
          var allEntries = valueAccessor();
          if (boundEntry.isDirectory) {
            $(element).droppable({
              drop: function (ev, ui) {
                boundEntry.moveHere($.grep(allEntries(), function (entry) {
                  return entry.selected();
                }));
              },
              hoverClass: 'fb-drop-hover'
            })
          }
        }
      };

      ko.bindingHandlers.fileSelect = {
        init: function(element, valueAccessor, allBindings, boundEntry, bindingContext) {
          var $element = $(element);
          $element.attr('unselectable', 'on').css('user-select', 'none').on('selectstart', false);
          var allEntries = valueAccessor();

          $element.draggable({
            start: function (event, ui) {
              var $container = $('.fb-drag-container');

              var selectedEntries = $.grep(allEntries(), function (entry) {
                return entry.selected();
              });

              if (selectedEntries.length === 0) {
                boundEntry.selected(true);
              } else if (selectedEntries.length > 0 && !boundEntry.selected()){
                $.each(selectedEntries, function (idx, selectedEntry) {
                  selectedEntry.selected(false);
                });
                selectedEntries = [];
                boundEntry.selected(true);
              }

              var $helper = $('.fb-drag-helper').clone().show();
              if (selectedEntries.length > 1) {
                $helper.find('.drag-text').text(selectedEntries.length + ' ${ _('selected') }');
                $helper.find('i').removeClass().addClass('fa fa-fw fa-clone');
              } else {
                $helper.find('.drag-text').text(boundEntry.name);
                $helper.find('i').removeClass().addClass($element.find('.fb-primary-col i').attr('class'));
              }

              $helper.appendTo($container);
            },
            helper: function () {
              return $('<div>').addClass('fb-drag-container');
            },
            appendTo: "body",
            cursorAt: {
              top: 0,
              left: 0
            }
          });

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
      }

      ko.components.register('file-browser', {
        viewModel: FileBrowser,
        template: { element: 'fb-template' }
      });
    }));
  </script>
</%def>