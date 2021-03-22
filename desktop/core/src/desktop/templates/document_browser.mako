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

from desktop import conf
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
%>

<%def name="docBrowser(is_embeddable=False)">

  <script src="${ static('desktop/ext/js/jquery/plugins/jquery.hotkeys.js') }"></script>
  <link href="${ static('desktop/css/home.css') }" rel="stylesheet">

  <script type="text/html" id="doc-browser-template">
    <div class="doc-browser-drag-helper">
      <i class="fa fa-fw"></i><span class="drag-text">4 entries</span>
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

    <div class="doc-browser-container" data-bind="docSelect: activeEntry.entries, docDroppable: { entries: activeEntry.entries }">
      <div class="navbar hue-title-bar">
        <div class="navbar-inner">
          <div class="container-fluid">
            <div class="pull-right" style="padding-right: 10px">
              <div class="doc-browser-folder-actions" data-bind="visible: activeEntry && activeEntry() && !activeEntry().hasErrors()">
                <!-- ko with: activeEntry -->
                <!-- ko if: app === 'documents' -->
                <div class="inline">
                  <span class="dropdown">
                    <a class="btn" title="${_('New document')}" data-toggle="dropdown" data-bind="tooltip: { placement: 'bottom', delay: 750 }, css: { 'disabled': isTrash() || isTrashed() || ! canModify() }" href="javascript:void(0);" style="height: 20px"><svg class="hi"><use xlink:href="#hi-file"></use><use xlink:href="#hi-plus-addon"></use></svg></a>
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
                            <!-- ko template: { name: 'app-icon-template', data: { icon: 'hive' } } --><!-- /ko --> ${_('Hive Query')}
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
                            <!-- ko template: { name: 'app-icon-template', data: { icon: 'impala' } } --><!-- /ko --> ${_('Impala Query')}
                          </a>
                      </li>
                      % endif
                      <%
                      from notebook.conf import SHOW_NOTEBOOKS
                      %>
                      % if SHOW_NOTEBOOKS.get():
                        <li>
                          <a title="${_('Notebook')}" data-bind="hueLink: addDirectoryParamToUrl('${ url('notebook:index') }')">
                            <!-- ko template: { name: 'app-icon-template', data: { icon: 'notebook' } } --><!-- /ko --> ${_('Notebook')}
                          </a>
                        </li>
                      % endif
                      % if 'pig' in apps:
                        <li>
                          <a title="${_('Pig Script')}" data-bind="hueLink: addDirectoryParamToUrl('${ url('pig:index') }')">
                            <!-- ko template: { name: 'app-icon-template', data: { icon: 'pig' } } --><!-- /ko --> ${_('Pig Script')}
                          </a>
                        </li>
                      % endif
                      % if 'oozie' in apps:
                        <li>
                          <a title="${_('Oozie Workflow')}" data-bind="hueLink: addDirectoryParamToUrl('${ url('oozie:new_workflow') }')">
                            <!-- ko template: { name: 'app-icon-template', data: { icon: 'oozie-workflow' } } --><!-- /ko --> ${_('Workflow') if is_embeddable else _('Oozie Workflow')}
                          </a>
                        </li>
                        <li>
                          <a title="${_('Oozie Schedule')}" data-bind="hueLink: addDirectoryParamToUrl('${ url('oozie:new_coordinator') }')">
                            <!-- ko template: { name: 'app-icon-template', data: { icon: 'oozie-coordinator' } } --><!-- /ko --> ${_('Schedule') if is_embeddable else _('Oozie Coordinator')}
                          </a>
                        </li>
                        <li>
                          <a title="${_('Oozie Bundle')}" data-bind="hueLink: addDirectoryParamToUrl('${ url('oozie:new_bundle') }')">
                            <!-- ko template: { name: 'app-icon-template', data: { icon: 'oozie-bundle' } } --><!-- /ko --> ${_('Bundle') if is_embeddable else _('Oozie Bundle')}
                          </a>
                        </li>
                      % endif
                      % if 'search' in apps:
                        <li>
                          <a title="${_('Solr Search')}" data-bind="hueLink: addDirectoryParamToUrl('${ url('search:new_search') }')">
                            <!-- ko template: { name: 'app-icon-template', data: { icon: 'dashboard' } } --><!-- /ko --> ${_('Dashboard')}
                          </a>
                        </li>
                      % endif
                      <li class="divider"></li>
                      <li data-bind="css: { 'disabled': isTrash() || isTrashed() || !canModify() }">
                        <a href="javascript:void(0);" data-bind="click: function () {  huePubSub.publish('show.create.directory.modal', $data); }"><svg class="hi"><use xlink:href="#hi-folder"></use><use xlink:href="#hi-plus-addon"></use></svg> ${_('New folder')}</a>
                      </li>
                    </ul>
                  </span>
                </div>
                <!-- /ko -->

                <!-- ko if: app === 'documents' -->
                <!-- ko if: $root.sharingEnabled() -->
                <a class="btn" title="${_('Share')}" href="javascript:void(0);" data-bind="tooltip: { placement: 'bottom', delay: 750 }, click: function() { showSharingModal() }, css: { 'disabled': selectedEntries().length !== 1 || (selectedEntries().length === 1 && selectedEntries()[0].isTrashed) }"><i class="fa fa-fw fa-users"></i></a>
                <!-- /ko -->
                <!-- /ko -->

                <!-- ko if: app === 'documents' -->
                <div class="margin-left-20 margin-right-20 pull-right doc-browser-type-filter" data-bind="contextMenu: { menuSelector: '.hue-context-menu' }">
                  <!-- ko if: isTrash() || isTrashed() -->
                  <a href="javascript:void(0);" data-bind="click: emptyTrash">
                    <i class="fa fa-fw fa-trash"></i> ${_('Empty trash')}
                  </a>
                  <!-- /ko -->
                  <!-- ko if: !isTrash() && !isTrashed() -->
                  <a class="inactive-action" href="javascript:void(0);" data-bind="click: showTrash, trashDroppable, css: { 'blue' : isTrash() || isTrashed() }">
                    <i class="fa fa-fw fa-trash-o"></i> ${_('Trash')}
                  </a>
                  <!-- /ko -->
                </div>
                <!-- /ko -->

                <div class="dropdown pull-right margin-left-10">
                  <a class="btn" data-toggle="dropdown" href="javascript: void(0)">
                    <i class="fa fa-fw fa-ellipsis-v"></i>
                  </a>
                  <ul class="dropdown-menu">
                    <li data-bind="css: { 'disabled': directorySelected() || selectedEntries().length < 1 || (selectedEntries().length === 1 && selectedEntries()[0].isTrashed) }">
                      <a href="javascript:void(0);" data-bind="click: function () {  copy() }"><i class="fa fa-fw fa-files-o"></i> ${_('Copy')}</a>
                    </li>
                    <!-- ko if: isTrash() -->
                    <li data-bind="css: { 'disabled': selectedEntries().length === 0 }">
                      <a href="javascript:void(0);" data-bind="click: function() { showRestoreConfirmation() }"><i class="fa fa-fw fa-undo"></i> ${ _('Restore to Home ') }</a>
                    </li>
                    <!-- /ko -->
                    <li data-bind="css: { 'disabled': selectedEntries().length === 0 || (sharedWithMeSelected() && !superuser) }">
                      <a href="javascript:void(0);" data-bind="click: function() {huePubSub.publish('doc.show.delete.modal', $data); }"><i class="fa fa-fw fa-times"></i> <span data-bind="text:  isTrash() || isTrashed() ? '${ _ko('Delete forever') }' : '${ _ko('Move to trash') }'"></span></a>
                    </li>
                    <li data-bind="css: { 'disabled': isTrash() || isTrashed() || selectedEntry() === null || !canModify() || (selectedEntry() != null && (!selectedEntry().isDirectory() || !selectedEntry().canModify())) }">
                      <a href="javascript:void(0);" data-bind="click: function () { showRenameDirectoryModal() }"><i class="fa fa-fw fa-edit"></i> ${_('Rename folder')}</a>
                    </li>
                    <li>
                      <a title="${_('Export all or selected documents')}" href="javascript:void(0);" data-bind="click: download"><i class="fa fa-fw fa-download"></i> ${_('Export')}</a>
                    </li>
                    <li data-bind="css: { 'disabled': isTrash() || isTrashed() }">
                      <a href="javascript:void(0);" data-bind="click: showUploadModal"><i class="fa fa-fw fa-upload"></i> ${_('Import')}</a>
                    </li>
                    <!-- ko if: isTrash() || isTrashed() -->
                    <li class="divider"></li>
                    <li>
                      <a href="javascript:void(0);" data-bind="click: emptyTrash"><i class="fa fa-fw fa-times"></i> ${ _('Empty trash') }</a>
                    </li>
                    <!-- /ko -->
                  </ul>
                </div>


                <!-- /ko -->
              </div>
            </div>
            <div class="nav-collapse">
              <ul class="nav">
                <li class="app-header">
                  <a href="/hue/useradmin">
                    <svg class="hi"><use xlink:href="#hi-documents"></use></svg>
                    <!-- ko component: { name: 'hue-favorite-app', params: { app: 'home' }} --><!-- /ko -->
                  </a>
                </li>
               <!-- ko with: activeEntry -->
                  <!-- ko if: isRoot -->
                    <li><div class="doc-browser-drop-target"><a href="javascript:void(0);" data-bind="click: open">${ _('My documents') }</a></div></li>
                  <!-- /ko -->
                  <!-- ko if: definition().isSearchResult -->
                    <li class="active"><div class="doc-browser-drop-target">${ _('Result for') }: <!-- ko text: definition().name --><!-- /ko --></div></li>
                  <!-- /ko -->
                  <!-- ko ifnot: definition().isSearchResult -->
                    <!-- ko foreach: breadcrumbs -->
                      <li><div class="doc-browser-drop-target" data-bind="docDroppable: { entries: $parent.entries, disableSelect: true }"><a href="javascript:void(0);" data-bind="text: isRoot() ? '${ _('My documents') }' : (isTrash() ? '${ _('Trash') }' : definition().name), click: open"></a></div></li>
                      <li class="breadcrumbs-divider">&gt;</li>
                    <!-- /ko -->
                    <!-- ko ifnot: isRoot -->
                      <li class="active"><div class="doc-browser-drop-target" data-bind="text: isTrash() ? '${ _('Trash') }' : definition().name"></div></li>
                    <!-- /ko -->
                  <!-- /ko -->
                <!-- /ko -->
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- ko with: activeEntry -->
      <!-- ko if: entries().length > 0 -->
      <div class="doc-browser-header margin-top-10">
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
                <li><a href="javascript:void(0);" data-bind="click: function() { huePubSub.publish('doc.show.delete.modal', $parent); }"><i class="fa fa-fw fa-times"></i> ${ _('Delete') } <span data-bind="visible: $parent.selectedEntries().length > 1, text: '(' + $parent.selectedEntries().length + ')'"></span></a></li>
                <li><a href="javascript:void(0);" data-bind="click: function() { $parent.showRestoreConfirmation(); }"><i class="fa fa-fw fa-undo"></i> ${ _('Restore to Home') } <span data-bind="visible: $parent.selectedEntries().length > 1, text: '(' + $parent.selectedEntries().length + ')'"></span></a></li>
                <!-- /ko -->
                <!-- ko ifnot: isTrashed -->
                <!-- ko if: isDirectory -->
                <li data-bind="css: { 'disabled': $parent.selectedEntries().length !== 1 }"><a href="javascript:void(0);" data-bind="click: showRenameDirectoryModal, css: { 'disabled': $parent.selectedEntries().length !== 1 }"><i class="fa fa-fw fa-edit"></i> ${ _('Rename') }</a></li>
                <!-- /ko -->
                <li data-bind="css: { 'disabled': $parent.selectedEntries().length !== 1 }"><a href="javascript:void(0);" data-bind="click: open, css: { 'disabled': $parent.selectedEntries().length !== 1 }"><i class="fa fa-fw fa-file-o"></i> ${ _('Open') }</a></li>
                <li><a href="javascript:void(0);" data-bind="click: contextMenuDownload"><i class="fa fa-fw fa-download"></i> ${ _('Download') } <span data-bind="visible: $parent.selectedEntries().length > 1, text: '(' + $parent.selectedEntries().length + ')'"></span></a></li>
                <li data-bind="css: { 'disabled' : $parent.sharedWithMeSelected()  && ! $parent.superuser }"><a href="javascript:void(0);" data-bind="click: function () { huePubSub.publish('doc.show.delete.modal', $parent); }, css: { 'disabled' : $parent.sharedWithMeSelected() && ! $parent.superuser }">
                  <i class="fa fa-fw fa-times"></i> ${ _('Move to trash') } <span data-bind="visible: $parent.selectedEntries().length > 1, text: '(' + $parent.selectedEntries().length + ')'"></span></a>
                </li>
                <!-- ko if: $root.sharingEnabled() -->
                <li data-bind="css: { 'disabled': $parent.selectedEntries().length !== 1 }"><a href="javascript:void(0);" data-bind="click: function() { $parent.showSharingModal(); }, css: { 'disabled': $parent.selectedEntries().length !== 1 }"><i class="fa fa-fw fa-users"></i> ${ _('Share') }</a> </li>
                <!-- /ko -->
                <!-- /ko -->
              </ul>
              <div class="doc-browser-primary-col">
                <!-- ko template: { name: 'document-icon-template', data: { document: $data, showShareAddon: true } } --><!-- /ko -->
                <a href="javascript: void(0);" data-bind="text: definition().name, click: open, hueLink: definition().type === 'directory' ? '' : definition().absoluteUrl, attr: { 'title': definition().name }" class="margin-left-5"></a>
              </div>
              <div class="doc-browser-attr-group">
                <!-- ko with: definition -->
                <div class="doc-browser-attr-col doc-browser-description" data-bind="text: description, attr: { 'title': description }"></div>
                <div class="doc-browser-attr-col doc-browser-type" data-bind="text: window.DOCUMENT_TYPE_I18n[type] || type"></div>
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
          var $element = $(element);
          var dragToSelect = false;
          var selectSub = huePubSub.subscribe('doc.drag.to.select', function (value) {
            dragToSelect = value;
          });

          var dragData;
          var dragSub = huePubSub.subscribe('doc.browser.dragging', function (data) {
            dragData = data;
          });

          ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
            dragSub.remove();
            selectSub.remove();
          });

          $element.droppable({
            drop: function (ev, ui) {
              if (!dragToSelect && dragData && !dragData.dragToSelect && boundEntry.isDirectory && boundEntry.isDirectory()) {
                boundEntry.moveHere(dragData.selectedEntries);
              }
              $element.removeClass('doc-browser-drop-hover');
            },
            over: function () {
              if (!dragToSelect && boundEntry.isDirectory && boundEntry.isDirectory()) {
                var movableCount = dragData.selectedEntries.filter(function (entry) {
                  return entry.selected() && ! entry.isSharedWithMe();
                }).length;
                if (movableCount > 0) {
                  $element.addClass('doc-browser-drop-hover');
                }
              }
            },
            out: function (event, ui) {
              if (!dragToSelect && boundEntry.isDirectory && boundEntry.isDirectory()) {
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
                var $helper = $('.doc-browser-drag-helper').clone().appendTo($container).show();
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
                  if (boundObject) {
                    if ((dragStartY <= boundingRect.top && event.clientY >= boundingRect.top) ||
                        (event.clientY <= boundingRect.bottom && dragStartY >= boundingRect.bottom)) {
                      boundObject.selected(true);
                    } else if (!boundObject.alreadySelected) {
                      boundObject.selected(false);
                    }
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

        huePubSub.subscribe('file.browser.directory.opened', function () {
          self.searchQuery('');
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
