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

import componentUtils from './componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

const TEMPLATE = `
  <!-- ko with: activeEntry -->
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${I18n(
      'Close'
    )}"><span aria-hidden="true">&times;</span></button>
    <!-- ko if: entriesToDelete().length === 0 -->
    <h2 class="modal-title">${I18n('The trash is empty')}</h2>
    <!-- /ko -->
    <!-- ko if: entriesToDelete().length > 0 -->
    <h2 class="modal-title"> ${I18n(
      'Do you really want to delete the following document(s)?'
    )} </h2>
    <!-- /ko -->
  </div>
  <div class="modal-body">
    <div class="doc-browser-empty animated" style="display: none;" data-bind="visible: entriesToDelete().length > 0 && selectedDocsWithDependents().length === 0">
      <i class="fa fa-spinner fa-spin fa-2x"></i>
    </div>
    <ul data-bind="foreach: selectedDocsWithDependents()">
      <li>
        <span data-bind="text: $data.name"></span>
        <!-- ko if: $data.dependents.length > 0 -->
          (${I18n('used by')}
          <a class="pointer" data-bind="hueLink: $data.dependents[0].absoluteUrl, text: $data.dependents[0].name"></a>
          <!-- ko if: $data.dependents.length > 1 -->
          ${I18n(
            'and'
          )} <a class="pointer" data-bind="hueLink: $data.dependents[1].absoluteUrl, text: $data.dependents[1].name"></a>
            <!-- ko if: $data.dependents.length > 2 -->
              ${I18n('and')} <span data-bind="text: $data.dependents.length - 2"></span> ${I18n(
  'other'
)}
            <!-- /ko -->
          <!-- /ko -->
          )
        <!-- /ko -->
      </li>
    </ul>
  </div>
  <div class="modal-footer">
    <!-- ko if: entriesToDelete().length === 0 -->
    <input type="button" class="btn" data-dismiss="modal" value="${I18n('Close')}">
    <!-- /ko -->
    <!-- ko if: entriesToDelete().length > 0 -->
    <input type="button" class="btn" data-dismiss="modal" value="${I18n('Cancel')}">
    <input type="submit" data-bind="click: function() { if (isTrash() || isTrashed()) { removeDocuments(true) } else { moveToTrash() } }, disable: deletingEntries" class="btn btn-danger disable-feedback" value="${I18n(
      'Yes'
    )}"/>
    <!-- /ko -->
  </div>
  <!-- /ko -->
`;

componentUtils.registerComponent('delete-entry', undefined, TEMPLATE).done(() => {
  huePubSub.subscribe('doc.show.delete.modal', docViewModel => {
    let $deleteEntriesModal = $('#deleteEntriesModal');
    if ($deleteEntriesModal.length > 0) {
      ko.cleanNode($deleteEntriesModal[0]);
      $deleteEntriesModal.remove();
    }

    $deleteEntriesModal = $(
      '<div id="deleteEntriesModal" data-bind="component: { name: \'delete-entry\', params: $data }" data-keyboard="true" class="modal hide fade" tabindex="-1"/>'
    );
    $(window.HUE_CONTAINER).append($deleteEntriesModal);

    ko.applyBindings(docViewModel, $deleteEntriesModal[0]);
  });
});
