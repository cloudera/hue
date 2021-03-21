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
import * as ko from 'knockout';

import componentUtils from './componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

export const HIDE_DELETE_DOC_MODAL_EVENT = 'doc.hide.delete.modal';
export const SHOW_DELETE_DOC_MODAL_EVENT = 'doc.show.delete.modal';
export const DELETE_DOC_MODAL_SHOWN_EVENT = 'doc.delete.modal.shown';

const TEMPLATE = `
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
`;

componentUtils.registerComponent('delete-entry', undefined, TEMPLATE).then(() => {
  const removeDeleteDocModal = () => {
    const $deleteEntriesModal = $('#deleteEntriesModal');
    if ($deleteEntriesModal.length > 0) {
      ko.cleanNode($deleteEntriesModal[0]);
      $deleteEntriesModal.remove();
    }
  };

  huePubSub.subscribe(SHOW_DELETE_DOC_MODAL_EVENT, docViewModel => {
    removeDeleteDocModal();

    if (!docViewModel.entriesToDelete().length && docViewModel.selectedEntries().length) {
      docViewModel.entriesToDelete(docViewModel.selectedEntries());
    }

    if (
      docViewModel.entriesToDelete().length === 0 ||
      (docViewModel.sharedWithMeSelected() && !docViewModel.superuser)
    ) {
      return;
    }

    docViewModel.getSelectedDocsWithDependents();

    const data = {
      params: docViewModel,
      descendantsComplete: () => {
        huePubSub.publish(DELETE_DOC_MODAL_SHOWN_EVENT);
      }
    };

    const $deleteEntriesModal = $(
      '<div id="deleteEntriesModal" data-bind="descendantsComplete: descendantsComplete, component: { name: \'delete-entry\', params: params }" data-keyboard="true" class="modal hide fade" tabindex="-1"></div>'
    );
    $('body').append($deleteEntriesModal);

    ko.applyBindings(data, $deleteEntriesModal[0]);

    $deleteEntriesModal.modal('show');
  });

  huePubSub.subscribe(HIDE_DELETE_DOC_MODAL_EVENT, removeDeleteDocModal);
});
