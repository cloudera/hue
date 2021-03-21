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

import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { UUID } from 'utils/hueUtils';

export const NAME = 'download-result-modal';

export const SHOW_DOWNLOAD_RESULT_MODAL_EVENT = 'show.download.result.modal';

// prettier-ignore
const TEMPLATE = `
  <div class="modal-header">
    <!-- ko if: isDownloading -->
    <h2 class="modal-title">${ I18n('Your download is being prepared') }</h2>
    <!-- /ko -->
    <!-- ko if: downloadTruncated -->
    <h2 class="modal-title">${ I18n('Your downloaded results have been truncated') }</h2>
    <!-- /ko -->
  </div>
  <div class="modal-body">
    <!-- ko if: isDownloading -->
    ${ I18n('Please wait, it might take a while...') } <i class="fa fa-spinner fa-spin"></i>
    <!-- /ko -->
    <!-- ko if: downloadTruncated -->
    ${ I18n('The number of resulting rows was too big to be downloaded and the resulting file has been truncated to') }
    <strong data-bind="text: downloadCounter"></strong>
    ${ I18n('rows.') }
    <!-- /ko -->
  </div>
  <div class="modal-footer">
    <!-- ko if: isDownloading -->
    <button data-bind="click: cancelDownload" class="btn btn-danger disable-feedback">${ I18n('Cancel Download') }</button>
    <!-- /ko -->
    <!-- ko if: downloadTruncated -->
    <button class="btn disable-feedback" data-dismiss="modal">${ I18n('Close') }</button>
    <!-- /ko -->
  </div>
`;

class DownloadResultModal {
  constructor(params, $downloadProgressModal) {
    if (typeof trackOnGA == 'function') {
      trackOnGA('notebook/download/' + params.format);
    }

    const executable = params.executable;
    this.$downloadProgressModal = $downloadProgressModal;

    this.isDownloading = ko.observable(true);
    this.downloadTruncated = ko.observable(false);
    this.downloadCounter = ko.observable(0);

    const id = executable.executor.snippet ? executable.executor.snippet.id : UUID();

    params.executable.toContext(id).then(jsonContext => {
      this.cookieId = 'download-' + id;
      $.cookie(this.cookieId, null, { expires: -1, path: '/' });

      this.addAndSubmitDownloadForm(jsonContext, params.format);

      this.checkDownloadInterval = -1;
      this.trackCookie();
    });
  }

  trackCookie() {
    let timesChecked = 0;
    this.checkDownloadInterval = window.setInterval(() => {
      if (!$.cookie(this.cookieId)) {
        if (timesChecked > 9) {
          this.$downloadProgressModal.show();
        }
      } else {
        window.clearInterval(this.checkDownloadInterval);
        try {
          const cookieContent = $.cookie(this.cookieId);
          const result = JSON.parse(
            cookieContent
              .substr(1, cookieContent.length - 2)
              .replace(/\\"/g, '"')
              .replace(/\\054/g, ',')
          );
          this.downloadTruncated(result.truncated);
          this.downloadCounter(result.row_counter);
          this.isDownloading(false);
          if (this.downloadTruncated()) {
            this.$downloadProgressModal.show();
          } else {
            this.$downloadProgressModal.hide();
          }
        } catch (e) {
          this.isDownloading(false);
          this.$downloadProgressModal.hide();
        }
      }
      timesChecked++;
    }, 500);
  }

  addAndSubmitDownloadForm(jsonContext, format) {
    const $downloadForm = $(
      '<form method="POST" class="download-form" style="display: inline" action="' +
        window.HUE_BASE_URL +
        '/notebook/download"></form>'
    );

    $('<input type="hidden" name="csrfmiddlewaretoken" />')
      .val(window.CSRF_TOKEN)
      .appendTo($downloadForm);
    $('<input type="hidden" name="notebook" />').val(jsonContext.notebook).appendTo($downloadForm);
    $('<input type="hidden" name="snippet" />').val(jsonContext.snippet).appendTo($downloadForm);
    $('<input type="hidden" name="format" />').val(format).appendTo($downloadForm);
    this.$downloadProgressModal.append($downloadForm);
    $downloadForm.submit();
  }

  cancelDownload() {
    window.clearInterval(this.checkDownloadInterval);
    this.$downloadProgressModal.hide();
  }
}

const cleanAndRemoveKoElement = selector => {
  const $element = $(selector);
  if ($element.length) {
    ko.cleanNode($element[0]);
    $element.remove();
  }
};

componentUtils.registerComponent(NAME, undefined, TEMPLATE).then(() => {
  huePubSub.subscribe(SHOW_DOWNLOAD_RESULT_MODAL_EVENT, params => {
    cleanAndRemoveKoElement('#downloadProgressModal');
    const $downloadProgressModal = $(
      '<div id="downloadProgressModal" data-bind="component: { name: \'' +
        NAME +
        '\', params: $data }" data-keyboard="true" class="modal hide fade downloadProgressModal" tabindex="-1"></div>'
    );
    $('body').append($downloadProgressModal);

    const model = new DownloadResultModal(params, $downloadProgressModal);
    ko.applyBindings(model, $downloadProgressModal[0]);
  });
});
