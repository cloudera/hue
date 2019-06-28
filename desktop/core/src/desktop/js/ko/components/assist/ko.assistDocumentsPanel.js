// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import $ from 'jquery';
import ko from 'knockout';

import apiHelper from 'api/apiHelper';
import componentUtils from 'ko/components/componentUtils';
import HueFileEntry from 'doc/hueFileEntry';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { DOCUMENT_TYPES } from 'doc/docSupport';

const TEMPLATE = `
  <script type="text/html" id="document-context-items">
    <!-- ko if: definition().type === 'directory' -->
    <li><a href="javascript: void(0);" data-bind="click: open"><i class="fa fa-fw fa-folder-open-o"></i> ${I18n(
      'Open folder'
    )}</a></li>
    <!-- /ko -->
    <!-- ko if: definition().type !== 'directory' -->
    <li><a href="javascript: void(0);" data-bind="click: function(data) { showContextPopover(data, { target: $parentContext.$contextSourceElement }, { left: -15, top: 2 }); }"><i class="fa fa-fw fa-info"></i> ${I18n(
      'Show details'
    )}</a></li>
    <li><a href="javascript: void(0);" data-bind="click: open"><i class="fa fa-fw fa-edit"></i> ${I18n(
      'Open document'
    )}</a></li>
    <li><a href="javascript: void(0);" data-bind="click: function() { huePubSub.publish('doc.show.delete.modal', $data); activeEntry().getSelectedDocsWithDependents(); activeEntry().showDeleteConfirmation(); }"><i class="fa fa-fw fa-trash-o"></i> ${I18n(
      'Delete document'
    )}</a></li>
    <!-- /ko -->
  </script>
  
  <script type="text/html" id="assist-document-header-actions">
    <div class="assist-db-header-actions">
      <!-- ko if: !loading() -->
      <div class="highlightable" data-bind="css: { 'highlight': $parent.highlightTypeFilter() }, component: { name: 'hue-drop-down', params: { fixedPosition: true, value: typeFilter, searchable: true, entries: DOCUMENT_TYPES, linkTitle: '${I18n(
        'Document type'
      )}' } }" style="display: inline-block"></div>
      <!-- /ko -->
      <span class="dropdown new-document-drop-down">

        <a class="inactive-action dropdown-toggle" data-toggle="dropdown" data-bind="dropdown" href="javascript:void(0);">
          <i class="pointer fa fa-plus" title="${I18n('New document')}"></i>
        </a>
        <ul class="dropdown-menu less-padding document-types" style="margin-top:3px; margin-left:-140px; width: 175px;position: absolute;" role="menu">
            <!-- ko if: window.HUE_APPS.indexOf('beeswax') !== -1 -->
              <li>
                <a title="${I18n(
                  'Hive Query'
                )}" data-bind="click: function() { huePubSub.publish('open.editor.new.query', {type: 'hive', 'directoryUuid': $data.getDirectory()}); }" href="javascript:void(0);">
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'hive' } } --><!-- /ko --> ${I18n(
                    'Hive Query'
                  )}
                </a>
              </li>
            <!-- /ko -->
            <!-- ko if: window.HUE_APPS.indexOf('impala') !== -1 -->
              <li>
                <a title="${I18n(
                  'Impala Query'
                )}" class="dropdown-item" data-bind="click: function() { huePubSub.publish('open.editor.new.query', {type: 'impala', 'directoryUuid': $data.getDirectory()}); }" href="javascript:void(0);">
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'impala' } } --><!-- /ko --> ${I18n(
                    'Impala Query'
                  )}
                </a>
            </li>
            <!-- /ko -->
            <!-- ko if: window.SHOW_NOTEBOOKS -->
              <li>
                <a title="${I18n(
                  'Notebook'
                )}" data-bind="click: function() { $('.new-document-drop-down').removeClass('open');}, hueLink: $data.addDirectoryParamToUrl(window.HUE_URLS.NOTEBOOK_INDEX)">
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'notebook' } } --><!-- /ko --> ${I18n(
                    'Notebook'
                  )}
                </a>
              </li>
            <!-- /ko -->
            <!-- ko if: window.HUE_APPS.indexOf('pig') !== -1 -->
              <li>
                <a title="${I18n(
                  'Pig Script'
                )}" data-bind="click: function() { $('.new-document-drop-down').removeClass('open');}, hueLink: $data.addDirectoryParamToUrl(window.HUE_URLS.PIG_INDEX)">
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'pig' } } --><!-- /ko --> ${I18n(
                    'Pig Script'
                  )}
                </a>
              </li>
            <!-- /ko -->
            <!-- ko if: window.HUE_APPS.indexOf('oozie') !== -1 -->
              <li>
                <a title="${I18n(
                  'Oozie Workflow'
                )}" data-bind="click: function() { $('.new-document-drop-down').removeClass('open');}, hueLink: $data.addDirectoryParamToUrl(window.HUE_URLS.OOZIE_NEW_WORKFLOW)">
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'oozie-workflow' } } --><!-- /ko --> ${I18n(
                    'Workflow'
                  )}
                </a>
              </li>
              <li>
                <a title="${I18n(
                  'Oozie Schedule'
                )}" data-bind="click: function() { $('.new-document-drop-down').removeClass('open');}, hueLink: $data.addDirectoryParamToUrl(window.HUE_URLS.OOZIE_NEW_COORDINATOR)">
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'oozie-coordinator' } } --><!-- /ko --> ${I18n(
                    'Schedule'
                  )}
                </a>
              </li>
              <li>
                <a title="${I18n(
                  'Oozie Bundle'
                )}" data-bind="click: function() { $('.new-document-drop-down').removeClass('open');}, hueLink: $data.addDirectoryParamToUrl(window.HUE_URLS.OOZIE_NEW_BUNDLE)">
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'oozie-bundle' } } --><!-- /ko --> ${I18n(
                    'Bundle'
                  )}
                </a>
              </li>
            <!-- /ko -->
            <!-- ko if: window.HUE_APPS.indexOf('search') !== -1 -->
              <li>
                <a title="${I18n(
                  'Solr Search'
                )}" data-bind="click: function() { $('.new-document-drop-down').removeClass('open');}, hueLink: $data.addDirectoryParamToUrl(window.HUE_URLS.SEARCH_NEW_SEARCH)">
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'dashboard' } } --><!-- /ko --> ${I18n(
                    'Dashboard'
                  )}
                </a>
              </li>
            <!-- /ko -->
            <li class="divider"></li>
            <li data-bind="css: { 'disabled': $data.isTrash() || $data.isTrashed() || !$data.canModify() }">
              <a href="javascript:void(0);" data-bind="click: function () { $('.new-document-drop-down').removeClass('open'); huePubSub.publish('show.create.directory.modal', $data); $data.showNewDirectoryModal()}"><svg class="hi"><use xlink:href="#hi-folder"></use><use xlink:href="#hi-plus-addon"></use></svg> ${I18n(
                'New folder'
              )}</a>
            </li>
          </ul>
      </span>
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.document.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${I18n(
        'Manual refresh'
      )}"></i></a>
    </div>
  </script>

  <!-- ko with: activeEntry -->
  <div class="assist-flex-header assist-breadcrumb" style="overflow: visible">
    <!-- ko ifnot: isRoot -->
    <a href="javascript: void(0);" data-bind="click: function () { if (loaded()) { parent.makeActive(); } }">
      <i class="fa fa-fw fa-chevron-left"></i>
      <i class="fa fa-fw fa-folder-o"></i>
      <span data-bind="text: definition().name, attr: {'title': definition().name }"></span>
    </a>
    <!-- /ko -->
    <!-- ko if: isRoot -->
    <div>
      <i class="fa fa-fw fa-folder-o"></i>
      <span>/</span>
    </div>
    <!-- /ko -->
    <!-- ko template: 'assist-document-header-actions' --><!-- /ko -->
  </div>
  <div class="assist-flex-search">
    <div class="assist-filter"><input class="clearable" type="text" placeholder="${I18n(
      'Filter...'
    )}" data-bind="clearable: filter, value: filter, valueUpdate: 'afterkeydown'"/></div>
  </div>
  <div class="assist-flex-fill assist-file-scrollable" data-bind="delayedOverflow">
    <div data-bind="visible: ! loading() && ! hasErrors() && entries().length > 0">
      <!-- ko if: filteredEntries().length == 0 -->
      <ul class="assist-tables">
        <li class="assist-entry"><span class="assist-no-entries">${I18n(
          'No documents found'
        )}</span></li>
      </ul>
      <!-- /ko -->
      <ul class="assist-tables" data-bind="foreachVisible: { data: filteredEntries, minHeight: 27, container: '.assist-file-scrollable' }">
        <li class="assist-entry assist-file-entry" data-bind="appAwareTemplateContextMenu: { template: 'document-context-items', scrollContainer: '.assist-file-scrollable', beforeOpen: beforeContextOpen }, assistFileDroppable, assistFileDraggable, visibleOnHover: { 'selector': '.assist-file-actions' }">
          <div class="assist-file-actions table-actions">
            <a class="inactive-action" href="javascript:void(0)" data-bind="click: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${I18n(
              'Show details'
            )}"></i></a>
          </div>
          <a href="javascript:void(0)" class="assist-entry assist-document-link" data-bind="click: open, attr: {'title': name }">
            <!-- ko template: { name: 'document-icon-template', data: { document: $data, showShareAddon: false } } --><!-- /ko -->
            <span class="highlightable" data-bind="css: { 'highlight': highlight }, text: definition().name"></span>
          </a>
        </li>
      </ul>
    </div>
    <div data-bind="visible: !loading() && ! hasErrors() && entries().length === 0">
      <span class="assist-no-entries">${I18n('Empty directory')}</span>
    </div>
    <div class="center" data-bind="visible: loading() && ! hasErrors()">
      <i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i>
    </div>
    <div class="assist-errors" data-bind="visible: ! loading() && hasErrors()">
      <span>${I18n('Error loading contents.')}</span>
    </div>
  </div>
  <!-- /ko -->
`;

class AssistDocumentsPanel {
  /**
   * @param {Object} options
   * @param {string} options.user
   * @constructor
   **/
  constructor(options) {
    const self = this;
    self.user = options.user;

    self.activeEntry = ko.observable();
    self.activeSort = ko.observable('defaultAsc');
    self.typeFilter = ko.observable(DOCUMENT_TYPES[0]); // all is first

    self.highlightTypeFilter = ko.observable(false);

    const lastOpenedUuid = apiHelper.getFromTotalStorage('assist', 'last.opened.assist.doc.uuid');

    if (lastOpenedUuid) {
      self.activeEntry(
        new HueFileEntry({
          activeEntry: self.activeEntry,
          trashEntry: ko.observable(),
          app: 'documents',
          user: self.user,
          activeSort: self.activeSort,
          typeFilter: self.typeFilter,
          definition: {
            uuid: lastOpenedUuid,
            type: 'directory'
          }
        })
      );
    } else {
      self.fallbackToRoot();
    }

    self.activeEntry.subscribe(newEntry => {
      if (!newEntry.loaded()) {
        const loadedSub = newEntry.loaded.subscribe(loaded => {
          if (
            loaded &&
            !newEntry.hasErrors() &&
            newEntry.definition() &&
            newEntry.definition().uuid
          ) {
            apiHelper.setInTotalStorage(
              'assist',
              'last.opened.assist.doc.uuid',
              newEntry.definition().uuid
            );
          }
          loadedSub.dispose();
        });
      } else if (!newEntry.hasErrors() && newEntry.definition() && newEntry.definition().uuid) {
        apiHelper.setInTotalStorage(
          'assist',
          'last.opened.assist.doc.uuid',
          newEntry.definition().uuid
        );
      }
    });

    self.reload = () => {
      self.activeEntry().load(
        () => {},
        () => {
          self.fallbackToRoot();
        }
      );
    };

    huePubSub.subscribe('assist.document.refresh', () => {
      huePubSub.publish('assist.clear.document.cache');
      self.reload();
    });

    huePubSub.subscribe('assist.doc.highlight', details => {
      huePubSub.publish('assist.show.documents');
      huePubSub.publish('context.popover.hide');
      const whenLoaded = $.Deferred().done(() => {
        self.activeEntry().highlightInside(details.docUuid);
      });
      if (
        self.activeEntry() &&
        self.activeEntry().definition() &&
        self.activeEntry().definition().uuid === details.parentUuid
      ) {
        if (self.activeEntry().loaded() && !self.activeEntry().hasErrors()) {
          whenLoaded.resolve();
        } else {
          const loadedSub = self.activeEntry().loaded.subscribe(newVal => {
            if (newVal) {
              if (!self.activeEntry().hasErrors()) {
                whenLoaded.resolve();
              }
              whenLoaded.reject();
              loadedSub.remove();
            }
          });
        }
        self.activeEntry().highlight(details.docUuid);
      } else {
        self.activeEntry(
          new HueFileEntry({
            activeEntry: self.activeEntry,
            trashEntry: ko.observable(),
            app: 'documents',
            user: self.user,
            activeSort: self.activeSort,
            typeFilter: self.typeFilter,
            definition: {
              uuid: details.parentUuid,
              type: 'directory'
            }
          })
        );
        self.activeEntry().load(
          () => {
            whenLoaded.resolve();
          },
          () => {
            whenLoaded.reject();
            self.fallbackToRoot();
          }
        );
      }
    });
  }

  setTypeFilter(newType) {
    const self = this;
    DOCUMENT_TYPES.some(docType => {
      if (docType.type === newType) {
        self.typeFilter(docType);
        return true;
      }
    });
    self.highlightTypeFilter(true);
    window.setTimeout(() => {
      self.highlightTypeFilter(false);
    }, 600);
  }

  fallbackToRoot() {
    const self = this;
    if (
      !self.activeEntry() ||
      (self.activeEntry().definition() &&
        (self.activeEntry().definition().path !== '/' || self.activeEntry().definition().uuid))
    ) {
      apiHelper.setInTotalStorage('assist', 'last.opened.assist.doc.uuid', null);
      self.activeEntry(
        new HueFileEntry({
          activeEntry: self.activeEntry,
          trashEntry: ko.observable(),
          app: 'documents',
          user: self.user,
          activeSort: self.activeSort,
          typeFilter: self.typeFilter,
          definition: {
            name: '/',
            type: 'directory'
          }
        })
      );
      self.activeEntry().load();
    }
  }

  init() {
    const self = this;
    if (!self.activeEntry().loaded()) {
      self.activeEntry().load(
        () => {},
        () => {
          self.fallbackToRoot();
        },
        true
      );
    }
  }
}

componentUtils.registerComponent('hue-assist-documents-panel', AssistDocumentsPanel, TEMPLATE);
