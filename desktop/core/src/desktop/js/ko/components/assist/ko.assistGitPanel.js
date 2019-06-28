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

import ko from 'knockout';

import apiHelper from 'api/apiHelper';
import AssistGitEntry from 'ko/components/assist/assistGitEntry';
import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

const TEMPLATE = `
  <script type="text/html" id="git-details-title">
    <span data-bind="text: definition.name"></span>
  </script>

  <script type="text/html" id="assist-git-header-actions">
    <div class="assist-db-header-actions">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.git.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${I18n(
        'Manual refresh'
      )}"></i></a>
    </div>
  </script>

  <!-- ko with: selectedGitEntry -->
  <div class="assist-flex-header assist-breadcrumb" >
    <!-- ko if: parent !== null -->
    <a href="javascript: void(0);" data-bind="click: function () { huePubSub.publish('assist.selectGitEntry', parent); }">
      <i class="fa fa-fw fa-chevron-left"></i>
      <i class="fa fa-fw fa-folder-o"></i>
      <span data-bind="text: path, attr: {'title': path }"></span>
    </a>
    <!-- /ko -->
    <!-- ko if: parent === null -->
    <div>
      <i class="fa fa-fw fa-folder-o"></i>
      <span data-bind="text: path"></span>
    </div>
    <!-- /ko -->
    <!-- ko template: 'assist-git-header-actions' --><!-- /ko -->
  </div>
  <div class="assist-flex-fill assist-git-scrollable" data-bind="delayedOverflow">
    <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
      <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
      <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 22, container: '.assist-git-scrollable' }">
        <li class="assist-entry assist-table-link" style="position: relative;" data-bind="visibleOnHover: { 'selector': '.assist-actions' }">

          <a href="javascript:void(0)" class="assist-entry assist-table-link" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.name }">
            <!-- ko if: definition.type === 'dir' -->
            <i class="fa fa-fw fa-folder-o muted valign-middle"></i>
            <!-- /ko -->
            <!-- ko ifnot: definition.type === 'dir' -->
            <i class="fa fa-fw fa-file-o muted valign-middle"></i>
            <!-- /ko -->
            <span draggable="true" data-bind="text: definition.name, draggableText: { text: '\\\\'' + path + '\\\\'', meta: {'type': 'git', 'definition': definition} }"></span>
          </a>
        </li>
      </ul>
      <!-- ko if: !loading() && entries().length === 0 -->
      <ul class="assist-tables">
        <li class="assist-entry"><span class="assist-no-entries">${I18n(
          'Empty directory'
        )}</span></li>
      </ul>
      <!-- /ko -->
    </div>
    <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
    <div class="assist-errors" data-bind="visible: ! loading() && hasErrors()">
      <span>${I18n('Error loading contents.')}</span>
    </div>
  </div>
  <!-- /ko -->
`;

class AssistGitPanel {
  /**
   * @param {Object} options
   * @constructor
   **/
  constructor(options) {
    const self = this;

    self.selectedGitEntry = ko.observable();
    self.reload = function() {
      const lastKnownPath = apiHelper.getFromTotalStorage(
        'assist',
        'currentGitPath',
        window.USER_HOME_DIR
      );
      const parts = lastKnownPath.split('/');
      parts.shift();

      const currentEntry = new AssistGitEntry({
        definition: {
          name: '/',
          type: 'dir'
        },
        parent: null
      });

      currentEntry.loadDeep(parts, entry => {
        self.selectedGitEntry(entry);
        entry.open(true);
      });
    };

    huePubSub.subscribe('assist.selectGitEntry', entry => {
      self.selectedGitEntry(entry);
      apiHelper.setInTotalStorage('assist', 'currentGitPath', entry.path);
    });

    huePubSub.subscribe('assist.git.refresh', () => {
      huePubSub.publish('assist.clear.git.cache');
      self.reload();
    });
  }

  init() {
    this.reload();
  }
}

componentUtils.registerComponent('hue-assist-git-panel', AssistGitPanel, TEMPLATE);
