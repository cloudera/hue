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

export const SHOW_EVENT = 'show.create.directory.modal';
export const SHOWN_EVENT = 'create.directory.modal.shown';

const TEMPLATE = `
  <!-- ko with: activeEntry -->
  <form class="form-horizontal">
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${I18n(
        'Close'
      )}"><span aria-hidden="true">&times;</span></button>
      <h2 class="modal-title">${I18n('Create Directory')}</h2>
    </div>
    <div class="modal-body ">
      <input id="newDirectoryName" class="input large-as-modal" type="text" placeholder="${I18n(
        'Directory name'
      )}" />
    </div>
    <div class="modal-footer">
      <input type="button" class="btn" data-dismiss="modal" data-bind="click: function () { $('#newDirectoryName').val(null) }" value="${I18n(
        'Cancel'
      )}">
      <input type="submit" class="btn btn-primary disable-feedback" value="${I18n(
        'Create'
      )}" data-bind="click: function () { if ($('#newDirectoryName').val()) { $data.createDirectory($('#newDirectoryName').val()); $('#createDirectoryModal').modal('hide'); } }"/>
    </div>
  </form>
  <!-- /ko -->
`;

componentUtils.registerComponent('create-directory', undefined, TEMPLATE).then(() => {
  huePubSub.subscribe(SHOW_EVENT, docViewModel => {
    if (docViewModel.isTrash() || docViewModel.isTrashed() || !docViewModel.canModify()) {
      return;
    }

    let $createDirectoryModal = $('#createDirectoryModal');
    if ($createDirectoryModal.length > 0) {
      ko.cleanNode($createDirectoryModal[0]);
      $createDirectoryModal.remove();
    }

    const data = {
      params: docViewModel,
      descendantsComplete: () => {
        huePubSub.publish(SHOWN_EVENT);
      }
    };

    $createDirectoryModal = $(
      '<div id="createDirectoryModal" data-bind="descendantsComplete: descendantsComplete, component: { name: \'create-directory\', params: params }" data-keyboard="true" class="modal hide fade" tabindex="-1"></div>'
    );
    $('body').append($createDirectoryModal);

    ko.applyBindings(data, $createDirectoryModal[0]);

    $createDirectoryModal.modal('show');
  });
});
