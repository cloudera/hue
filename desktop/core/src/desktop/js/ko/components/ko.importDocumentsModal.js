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
import HueFileEntry from 'doc/hueFileEntry';

export const HIDE_EVENT = 'hide.import.documents.modal';
export const SHOW_EVENT = 'show.import.documents.modal';
export const SHOWN_EVENT = 'import.documents.modal.shown';

const TEMPLATE = `
<div class="modal-header">
  <button type="button" class="close" data-dismiss="modal" aria-label="${I18n(
    'Close'
  )}"><span aria-hidden="true">&times;</span></button>
  <!-- ko if: isHistory -->
  <h2 class="modal-title">${I18n('Import Query History')}</h2>
  <!-- /ko -->
  <!-- ko ifnot: isHistory -->
  <h2 class="modal-title">${I18n('Import Hue Documents')}</h2>
  <!-- /ko -->
</div>

<!-- ko ifnot: imported --> 
<div class="modal-body">
  <!-- ko with: activeEntry -->
  <form id="importDocumentsForm" class="form-horizontal" style="display: inline" enctype="multipart/form-data">
    <div data-bind="visible: uploading() || uploadComplete()">
      <span data-bind="visible: uploading()">${I18n('Importing...')}</span>
      <span data-bind="visible: !uploadFailed() && uploadComplete()">${I18n(
        'Import complete!'
      )}</span>
      <span data-bind="visible: uploadFailed">${I18n('Import failed!')}</span>
      <progress data-bind="visible: uploading() || uploadComplete()" id="importDocumentsProgress" value="0" max="100" style="width: 560px;"></progress>
    </div>
    <div class="pull-right">
      <!-- ko ifnot: uploading() || uploadComplete() -->
      <input type="button" class="btn" data-clear="fileupload" data-bind="click: closeUploadModal" value="${I18n(
        'Cancel'
      )}" />
      <input type="submit" class="btn btn-danger" data-clear="fileupload" data-bind="enable: importEnabled, click: function() { upload($parent.importComplete) }" value="${I18n(
        'Import'
      )}" />
      <!-- /ko -->
      <!-- ko if: uploading() || uploadComplete() -->
      <input type="button" class="btn" data-clear="fileupload" data-bind="click: closeUploadModal" value="${I18n(
        'Close'
      )}" />
      <!-- /ko -->
    </div>

    <div class="fileupload fileupload-new" data-provides="fileupload" data-bind="visible: !uploading() && !uploadComplete()">
      <span class="btn btn-file">
        <span class="fileupload-new">${I18n('Select json file')}</span>
        <span class="fileupload-exists">${I18n('Change')}</span>
        <input id="importDocumentInput" type="file" name="documents" accept=".json" data-bind="value: selectedImportFile" />
      </span>
      &nbsp;&nbsp;<span class="fileupload-preview"></span>
      <a href="#" class="fileupload-exists" data-clear="fileupload"><i class="fa fa-times"></i></a>
    </div>
    <input type="hidden" name="path" data-bind="value: definition().path" />
  </form>
  <!-- /ko -->
</div>
<!-- /ko -->
<!-- ko if: imported -->
<div class="modal-body">
  <!-- ko with: activeEntry -->
  <div class="center" style="display: none;" data-bind="visible: importedDocumentCount() == 0">
    <i class="fa fa-spinner fa-spin fa-2x"></i>
  </div>
  <!-- ko if: importedDocumentCount() > 0 -->
  <ul>
    <li> ${I18n('Imported: ')} <span data-bind="text: importedDocSummary()['count']"></span></li>
    <li> ${I18n(
      'Created: '
    )} <span data-bind="text: importedDocSummary()['created_count']"></span></li>
    <li> ${I18n(
      'Updated: '
    )} <span data-bind="text: importedDocSummary()['updated_count']"></span></li>
  </ul>

  <!-- ko ifnot: showTable() -->
  <a href="javascript:void(0)" class="margin-left-10 margin-top-10" data-bind="click: toggleShowTable">${I18n(
    'Show Details'
  )} <i class="fa fa-caret-down"></i></a>
  <!-- /ko -->
  <!-- ko if: showTable() -->
  <a href="javascript:void(0)" class="margin-left-10 margin-top-10" data-bind="click: toggleShowTable">${I18n(
    'Hide Details'
  )} <i class="fa fa-caret-up"></i></a>
  <table class="table table-condensed">
    <thead>
      <tr>
        <th>${I18n('Name')}</th>
        <th>${I18n('Type')}</th>
        <th>${I18n('Owner')}</th>
      </tr>
    </thead>
    <tbody data-bind="foreach: importedDocSummary()['documents']">
      <tr>
        <td data-bind="text: $data.name"> </td>
        <td data-bind="text: $data.type"> </td>
        <td data-bind="text: $data.owner"> </td>
      </tr>
    </tbody>
  </table>
  <!-- /ko -->
  <!-- /ko -->
  <!-- /ko -->
</div>
<!-- /ko -->
`;

class ImportDocumentsModal {
  constructor(params) {
    if (!params) {
      params = {};
    }
    this.activeEntry = ko.observable(params.fileEntry);
    if (!params.fileEntry) {
      this.activeEntry(
        new HueFileEntry({
          activeEntry: this.activeEntry,
          trashEntry: ko.observable(),
          app: 'documents',
          user: self.user,
          activeSort: ko.observable('defaultAsc'),
          definition: {
            name: '/',
            type: 'directory'
          }
        })
      );
    }
    this.imported = ko.observable(false);
    this.isHistory = ko.observable(params.isHistory);

    this.importComplete = () => {
      if (params.importedCallback) {
        params.importedCallback();
      }
      this.imported(true);
    };
  }
}

componentUtils.registerComponent('import-documents-modal', undefined, TEMPLATE).then(() => {
  huePubSub.subscribe(SHOW_EVENT, params => {
    huePubSub.publish(HIDE_EVENT);

    const $importDocumentsModal = $(
      '<div id="importDocumentsModal" data-bind="descendantsComplete: descendantsComplete, component: { name: \'import-documents-modal\', params: params }" data-keyboard="true" class="modal hide fade fileupload-modal" tabindex="-1"></div>'
    );
    $('body').append($importDocumentsModal);

    const data = {
      params: new ImportDocumentsModal(params),
      descendantsComplete: () => {
        huePubSub.publish(SHOWN_EVENT);
      }
    };

    ko.applyBindings(data, $importDocumentsModal[0]);
    $importDocumentsModal.modal('show');
  });

  huePubSub.subscribe('hide.import.documents.modal', () => {
    const $importDocumentsModal = $('#importDocumentsModal');
    if ($importDocumentsModal.length > 0) {
      $importDocumentsModal.modal('hide');
      ko.cleanNode($importDocumentsModal[0]);
      $importDocumentsModal.remove();
    }
  });
});
