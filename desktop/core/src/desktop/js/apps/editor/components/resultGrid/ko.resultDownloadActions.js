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
import DisposableComponent from 'ko/components/DisposableComponent';
import I18n from 'utils/i18n';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import { SHOW_DOWNLOAD_RESULT_MODAL_EVENT } from 'apps/editor/components/resultGrid/ko.resultDownloadModal';

export const NAME = 'result-download-actions';

// prettier-ignore
const TEMPLATE = `
<div class="btn-group">
  <button class="btn btn-mini btn-editor dropdown-toggle" data-toggle="dropdown">
      <!-- ko ifnot: isDownloading -->
      <i class="fa fa-fw fa-download"></i>
      <!-- /ko -->
      <!-- ko if: isDownloading -->
      <i class="fa fa-fw fa-spinner fa-spin"></i>
      <!-- /ko -->
      ${ I18n('Export') }
    <span class="caret"></span>
  </button>
  <ul class="dropdown-menu">
    <li>
      <a href="javascript:void(0)" data-bind="
          click: downloadCsv,
          event: { mouseover: mouseOver, mouseout: mouseOut },
          attr: { 'title': downloadCsvTitle }
        ">
        <i class="fa fa-fw fa-file-o"></i> ${ I18n('CSV') }
      </a>
    </li>
    <li style="display: none;">
      <a href="javascript:void(0)" data-bind="
          click: downloadXls,
          event: { mouseover: mouseOver, mouseout: mouseOut },
          attr: { 'title': downloadXlsTitle }
        ">
        <i class="fa fa-fw fa-file-excel-o"></i> ${ I18n('Excel') }
      </a>
    </li>
    <li>
      <a href="javascript:void(0)" title="${ I18n('Copy the displayed results to your clipboard') }" data-bind="
          clipboard: {
            target: clipboardTarget.bind($data),
            onSuccess: onClipboardSuccess.bind($data)
          }
        ">
        <i class="fa fa-fw fa-clipboard"></i> ${ I18n('Clipboard') }
      </a>
    </li>
    <!-- ko if: window.ENABLE_SQL_INDEXER -->
    <li style="display: none;">
      <a class="download" href="javascript:void(0)" data-bind="click: exportToReport" title="${ I18n('Visually explore the result') }">
        <!-- ko template: { name: 'app-icon-template', data: { icon: 'report' } } --><!-- /ko --> ${ I18n('Report') }
      </a>
    </li>
    <li style="display: none;">
      <a class="download" href="javascript:void(0)" data-bind="click: exportToDashboard" title="${ I18n('Visually explore the result') }">
        <!-- ko template: { name: 'app-icon-template', data: { icon: 'dashboard' } } --><!-- /ko --> ${ I18n('Dashboard') }
      </a>
    </li>
    <!-- /ko -->
    <li style="display: none;">
      <a class="download" href="javascript:void(0)" data-bind="click: exportToFile" title="${ I18n('Export the result into a file, an index, a new table...') }">
        <i class="fa fa-fw fa-cloud-upload"></i> ${ I18n('File') }
      </a>
    </li>
  </ul>
</div>
`;

class ResultDownloadActions extends DisposableComponent {
  constructor(params) {
    super();

    this.activeExecutable = params.activeExecutable;
    this.data = params.data;
    this.meta = params.meta;

    this.isDownloading = ko.observable(false);

    this.downloadCsvTitle = '';
    this.downloadXlsTitle = '';

    const rowLimit = window.DOWNLOAD_ROW_LIMIT;
    const mbLimit = window.DOWNLOAD_BYTES_LIMIT && window.DOWNLOAD_BYTES_LIMIT / 1024 / 1024;
    if (typeof rowLimit !== 'undefined' && typeof mbLimit !== 'undefined') {
      this.downloadCsvTitle = I18n('Download first %s rows or %s MB as CSV', rowLimit, mbLimit);
      this.downloadXlsTitle = I18n('Download first %s rows or %s MB as XLS', rowLimit, mbLimit);
    } else if (typeof mbLimit !== 'undefined') {
      this.downloadCsvTitle = I18n('Download first %s MB as CSV', mbLimit);
      this.downloadXlsTitle = I18n('Download first %s MB as XLS', mbLimit);
    } else if (typeof rowLimit !== 'undefined') {
      this.downloadCsvTitle = I18n('Download first %s rows as CSV', rowLimit);
      this.downloadXlsTitle = I18n('Download first %s rows as XLS', rowLimit);
    }

    let previousOnBeforeUnload = window.onbeforeunload;
    this.mouseOver = () => {
      previousOnBeforeUnload = window.onbeforeunload;
      window.onbeforeunload = undefined;
    };

    this.mouseOut = () => {
      window.onbeforeunload = previousOnBeforeUnload;
    };
  }

  clipboardTarget() {
    const $clipboardContent = $('.clipboard-content');

    if (this.meta().length) {
      let htmlString = '<table><tr>';
      this.meta().forEach((metaCol, idx) => {
        // Skip the row number column
        if (idx > 0) {
          htmlString += `<th>${hueUtils.html2text(metaCol.name)}</th>`;
        }
      });
      htmlString += '</tr>';
      this.data().forEach(row => {
        htmlString += '<tr>';
        row.forEach((cell, idx) => {
          // Skip the row number column
          if (idx > 0) {
            htmlString += `<td>${hueUtils.html2text(cell)}</td>`;
          }
        });
        htmlString += '</tr>';
      });
      $clipboardContent.html(htmlString);
    } else {
      $clipboardContent.html(I18n('Error while copying results.'));
    }
    return $clipboardContent[0];
  }

  onClipboardSuccess(e) {
    $.jHueNotify.info(I18n('%s result(s) copied to the clipboard', this.data().length));
    e.clearSelection();
    $('.clipboard-content').empty();
  }

  downloadCsv() {
    huePubSub.publish(SHOW_DOWNLOAD_RESULT_MODAL_EVENT, {
      format: 'csv',
      executable: this.activeExecutable()
    });
  }

  downloadXls() {
    huePubSub.publish(SHOW_DOWNLOAD_RESULT_MODAL_EVENT, {
      format: 'xls',
      executable: this.activeExecutable()
    });
  }

  exportToDashboard() {
    // saveTarget('dashboard');
    // trySaveResults();
  }

  exportToFile() {
    // savePath('');
    // $('#saveResultsModal' + snippet.id()).modal('show');
  }

  exportToReport() {
    // saveTarget('dashboard');
    // if (notebook.canSave()) {
    //   notebook.save()
    // } else {
    //   $('#saveAsModaleditor').modal('show');
    // }
  }
}

componentUtils.registerComponent(NAME, ResultDownloadActions, TEMPLATE);
