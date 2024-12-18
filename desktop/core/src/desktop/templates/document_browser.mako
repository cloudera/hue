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
                <!-- ko if: searchVisible -->
                <div class="doc-browser-action doc-browser-search-container pull-left"><input class="clearable" type="text" placeholder="${ _('Search for name, description, etc...') }" data-bind="hasFocus: searchFocus, textInput: searchQuery, clearable: searchQuery"></div>
                <!-- /ko -->
                <!-- ko with: activeEntry -->
                <div class="doc-browser-action doc-browser-type-filter margin-right-10 pull-left" data-bind="component: { name: 'hue-drop-down', params: { value: serverTypeFilter, entries: DOCUMENT_TYPES, linkTitle: '${ _ko('Type filter') }' } }"></div>
                <a class="btn margin-right-20" title="${_('Search')}" href="javascript:void(0);" data-bind="tooltip: { placement: 'bottom', delay: 750 }, toggle: $parent.searchVisible, click: function () { $parent.searchFocus($parent.searchVisible()) }, css: { 'blue' : ($parent.searchVisible() || $parent.searchQuery()) }"><i class="fa fa-fw fa-search"></i></a>
                <!-- ko if: app === 'documents' -->
                <div class="inline">
                  <span class="dropdown">
                    <a class="btn" title="${_('New document')}" data-toggle="dropdown" data-bind="tooltip: { placement: 'bottom', delay: 750 }, css: { 'disabled': isTrash() || isTrashed() || ! canModify() }" href="javascript:void(0);" style="height: 20px"><svg class="hi"><use href="#hi-file"></use><use href="#hi-plus-addon"></use></svg></a>
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
                        <a href="javascript:void(0);" data-bind="click: function () {  huePubSub.publish('show.create.directory.modal', $data); }"><svg class="hi"><use href="#hi-folder"></use><use href="#hi-plus-addon"></use></svg> ${_('New folder')}</a>
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
                    <svg class="hi"><use href="#hi-documents"></use></svg>
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
                <li data-bind="css: { 'disabled': isDirectory() || isTrashed() }">
                  <a href="javascript:void(0);" data-bind="click: function () { $parent.copy()  }, css: { 'disabled': isDirectory() || isTrashed() }"><i class="fa fa-fw fa-files-o"></i> ${_('Copy')} <span data-bind="visible: $parent.selectedEntries().length > 1, text: '(' + $parent.selectedEntries().length + ')'"></span></a>
                </li>
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
  <script src="${ static('desktop/js/document-inline.js') }" type="text/javascript"></script>
</%def>
