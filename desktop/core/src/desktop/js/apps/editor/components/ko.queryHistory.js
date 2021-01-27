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

import apiHelper from 'api/apiHelper';
import componentUtils from 'ko/components/componentUtils';
import DisposableComponent from 'ko/components/DisposableComponent';
import I18n from 'utils/i18n';
import { ExecutionStatus } from 'apps/editor/execution/executable';
import { sleep } from 'utils/hueUtils';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import { SHOW_EVENT } from 'ko/components/ko.importDocumentsModal';

export const NAME = 'query-history';
export const HISTORY_CLEARED_EVENT = 'query.history.cleared';
export const ADD_TO_HISTORY_EVENT = 'query.history.add';

import { NAME as PAGINATOR_COMPONENT } from './ko.paginator';

// prettier-ignore
const TEMPLATE = `
<div class="clear-history-modal modal hide fade">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="${ I18n('Close') }"><span aria-hidden="true">&times;</span></button>
    <h2 class="modal-title">${ I18n('Confirm History Clear') }</h2>
  </div>
  <div class="modal-body">
    <p>${ I18n('Are you sure you want to clear the query history?') }</p>
  </div>
  <div class="modal-footer">
    <a class="btn" data-dismiss="modal">${ I18n('No') }</a>
    <a class="btn btn-danger disable-feedback" data-bind="click: clearHistory.bind($data)">${ I18n('Yes') }</a>
  </div>
</div>

<div class="snippet-tab-actions">
  <form autocomplete="off" class="inline-block">
    <input class="input-small search-input" type="text" ${ window.PREVENT_AUTOFILL_INPUT_ATTRS } placeholder="${ I18n('Search...') }" data-bind="
        textInput: historyFilter,
        clearable: historyFilter
      "/>
  </form>
  <div class="pull-right">
    <div class="btn-group">
      <button class="btn btn-mini btn-editor" data-bind="enable: history().length, click: showClearHistoryModal.bind($data)">
        <i class="fa fa-fw fa-calendar-times-o"></i> ${ I18n('Clear') }
      </button>
    </div>
    <div class="btn-group">
      <button class="btn btn-mini btn-editor" data-bind="enable: history().length, click: exportHistory.bind($data)">
        <i class="fa fa-fw fa-download"></i> ${ I18n('Export') }
      </button>
      <button class="btn btn-mini btn-editor" data-bind="click: importHistory.bind($data)">
        <i class="fa fa-fw fa-upload"></i> ${ I18n('import') }
      </button>
    </div>
  </div>
</div>

<div class="snippet-tab-body">
  <!-- ko if: loadingHistory -->
    <div>
      <h1 class="empty"><i class="fa fa-spinner fa-spin"></i> ${ I18n('Loading...') }</h1>
    </div>
  <!-- /ko -->

  <!-- ko ifnot: loadingHistory -->
    <!-- ko if: !history().length -->
      <!-- ko ifnot: historyFilter -->
        <div class="margin-top-10 margin-left-10" style="font-style: italic">${ I18n("No queries to be shown.") }</div>
      <!-- /ko -->
      <!-- ko if: historyFilter -->
        <div class="margin-top-10 margin-left-10" style="font-style: italic">${ I18n('No queries found for') } <strong data-bind="text: historyFilter"></strong>.</div>
      <!-- /ko -->
    <!-- /ko -->

    <!-- ko if: history().length -->
      <table class="table table-condensed margin-top-10 history-table">
        <tbody data-bind="foreach: history">
          <tr data-bind="
              click: function() {
                $parent.openNotebook(uuid);
              },
              css: {
                'highlight': uuid === $parent.currentNotebook.uuid(),
                'pointer': uuid !== $parent.currentNotebook.uuid()
              }
            ">
            <td style="width: 100px" class="muted" data-bind="style: { 'border-top-width': $index() === 0 ? '0' : ''}">
              <span data-bind="momentFromNow: { data: lastExecuted, interval: 10000, titleFormat: 'LLL' }"></span>
            </td>
            <td style="width: 25px" class="muted" data-bind="style: { 'border-top-width': $index() === 0 ? '0' : ''}">
              <!-- ko switch: status -->
                <!-- ko case: 'running' -->
                <div class="history-status" data-bind="tooltip: { title: '${ I18n("Query running") }', placement: 'bottom' }"><i class="fa fa-fighter-jet fa-fw"></i></div>
                <!-- /ko -->
                <!-- ko case: 'streaming' -->
                <div class="history-status" data-bind="tooltip: { title: '${ I18n("Query streaming") }', placement: 'bottom' }"><i class="fa fa-fighter-jet fa-fw"></i></div>
                <!-- /ko -->
                <!-- ko case: 'failed' -->
                <div class="history-status" data-bind="tooltip: { title: '${ I18n("Query failed") }', placement: 'bottom' }"><i class="fa fa-exclamation fa-fw"></i></div>
                <!-- /ko -->
                <!-- ko case: 'available' -->
                <div class="history-status" data-bind="tooltip: { title: '${ I18n("Result available") }', placement: 'bottom' }"><i class="fa fa-check fa-fw"></i></div>
                <!-- /ko -->
                <!-- ko case: 'expired' -->
                <div class="history-status" data-bind="tooltip: { title: '${ I18n("Result expired") }', placement: 'bottom' }"><i class="fa fa-unlink fa-fw"></i></div>
                <!-- /ko -->
              <!-- /ko -->
            </td>
            <td style="width: 25px" class="muted" data-bind="
                ellipsis: {
                  data: name,
                  length: 30
                },
                style: {
                  'border-top-width': $index() === 0 ? '0' : ''
                }
              "></td>
            <td data-bind="
                style: {
                  'border-top-width': $index() === 0 ? '0' : ''
                },
                click: function() {
                  $parent.openNotebook(uuid)
                },
                clickBubble: false
              "><div data-bind="highlight: { value: query, dialect: $parent.dialect }"></div></td>
          </tr>
        </tbody>
      </table>
    <!-- /ko -->

    <!-- ko component: {
      name: '${ PAGINATOR_COMPONENT }',
      params: {
        currentPage: historyCurrentPage,
        totalPages: historyTotalPages,
        onPageChange: onPageChange
      }
    } --><!-- /ko -->
  <!-- /ko -->
</div>
`;

const QUERIES_PER_PAGE = 50;

const AVAILABLE_INTERVAL = 60000 * 5;
const STARTING_RUNNING_INTERVAL = 30000;

const trimEllipsis = str => str.substring(0, 1000) + (str.length > 1000 ? '...' : '');

class QueryHistory extends DisposableComponent {
  constructor(params, element) {
    super();
    this.currentNotebook = params.currentNotebook;
    this.dialect = params.dialect;
    this.openFunction = params.openFunction;
    this.element = element;

    this.loadingHistory = ko.observable(true);
    this.history = ko.observableArray();
    this.historyFilter = ko.observable('').extend({ rateLimit: 900 });

    this.historyCurrentPage = ko.observable(1);
    this.totalHistoryCount = ko.observable(0);
    this.historyTotalPages = ko.pureComputed(() =>
      Math.max(1, Math.ceil(this.totalHistoryCount() / QUERIES_PER_PAGE))
    );

    this.refreshStatusFailed = false;

    this.addDisposalCallback(() => {
      this.refreshStatusFailed = true; // Cancels the status check intervals
    });

    let fetchTimeout = -1;
    const throttledFetch = () => {
      window.clearTimeout(fetchTimeout);
      fetchTimeout = window.setTimeout(this.fetchHistory.bind(this), 10);
    };

    this.subscribe(this.historyFilter, () => {
      if (this.historyCurrentPage() !== 1) {
        this.historyCurrentPage(1);
      } else {
        throttledFetch();
      }
    });

    this.onPageChange = throttledFetch;

    this.subscribe(ADD_TO_HISTORY_EVENT, this.addHistoryRecord.bind(this));

    throttledFetch();
  }

  async clearHistory() {
    hueAnalytics.log('notebook', 'clearHistory');

    apiHelper
      .clearNotebookHistory({
        notebookJson: await this.currentNotebook.toContextJson(),
        docType: this.dialect()
      })
      .then(() => {
        this.history.removeAll();
        this.totalHistoryCount(0);
        this.historyFilter('');
        huePubSub.publish(HISTORY_CLEARED_EVENT);
      })
      .fail(xhr => {
        if (xhr.status !== 502) {
          $(document).trigger('error', xhr.responseText);
        }
      });

    const $modal = $(this.element).find('.clear-history-modal');
    $modal.modal('hide');
  }

  async exportHistory() {
    const historyResponse = await apiHelper.getHistory({ type: this.dialect(), limit: 500 });

    if (historyResponse && historyResponse.history) {
      window.location.href =
        window.HUE_BASE_URL +
        '/desktop/api2/doc/export?history=true&documents=[' +
        historyResponse.history.map(historyDoc => historyDoc.id).join(',') +
        ']';
    }
  }

  addHistoryRecord(historyRecord) {
    this.history.unshift({
      url: historyRecord.url,
      query: trimEllipsis(historyRecord.statement),
      lastExecuted: historyRecord.lastExecuted,
      status: ko.observable(historyRecord.status),
      name: historyRecord.name,
      uuid: historyRecord.uuid
    });
    this.totalHistoryCount(this.totalHistoryCount() + 1);
  }

  async fetchHistory() {
    this.loadingHistory(true);

    try {
      const historyData = await apiHelper.getHistory({
        type: this.dialect(),
        limit: QUERIES_PER_PAGE,
        page: this.historyCurrentPage(),
        docFilter: this.historyFilter()
      });

      if (historyData && historyData.history) {
        this.history(
          historyData.history.map(historyRecord => ({
            url: historyRecord.absoluteUrl,
            query: trimEllipsis(historyRecord.data.statement),
            lastExecuted: historyRecord.data.lastExecuted,
            status: ko.observable(historyRecord.data.status),
            name: historyRecord.name,
            uuid: historyRecord.uuid
          }))
        );
      } else {
        this.history([]);
      }

      this.totalHistoryCount(historyData.count);
    } catch (err) {
      this.history([]);
      this.totalHistoryCount(0);
    }

    this.loadingHistory(false);
    this.refreshStatus(
      [ExecutionStatus.starting, ExecutionStatus.running, ExecutionStatus.streaming],
      STARTING_RUNNING_INTERVAL
    );
    this.refreshStatus([ExecutionStatus.available], AVAILABLE_INTERVAL);
  }

  importHistory() {
    huePubSub.publish(SHOW_EVENT, { importedCallback: this.fetchHistory.bind(this) });
  }

  openNotebook(uuid) {
    if (window.getSelection().toString() === '' && uuid !== this.currentNotebook.uuid()) {
      this.openFunction(uuid);
    }
  }

  async refreshStatus(statusesToRefresh, interval) {
    const statusIndex = {};
    statusesToRefresh.forEach(status => {
      statusIndex[status] = true;
    });

    const items = this.history()
      .filter(item => statusIndex[item.status()])
      .slice(0, 25);

    const refreshStatusForItem = async item => {
      if (this.refreshStatusFailed) {
        return;
      }
      try {
        const response = await apiHelper.checkStatus({
          notebookJson: JSON.stringify({ uuid: item.uuid }),
          silenceErrors: true
        });
        if (response.status === -3) {
          item.status(ExecutionStatus.expired);
        } else if (response.status !== 0) {
          item.status(ExecutionStatus.failed);
        } else if (response.query_status.status) {
          item.status(response.query_status.status);
        }
      } catch (err) {
        items.length = 0;
        this.refreshStatusFailed = true;
      } finally {
        if (items.length) {
          await sleep(1000);
          await refreshStatusForItem(items.pop());
        } else if (!this.refreshStatusFailed) {
          await sleep(interval);
          this.refreshStatus(statusesToRefresh, interval);
        }
      }
    };

    if (items.length) {
      await refreshStatusForItem(items.pop());
    } else if (!this.refreshStatusFailed) {
      await sleep(interval);
      this.refreshStatus(statusesToRefresh, interval);
    }
  }

  showClearHistoryModal() {
    const $modal = $(this.element).find('.clear-history-modal');
    $modal.modal('show');
  }
}

componentUtils.registerComponent(
  NAME,
  {
    createViewModel: (params, componentInfo) =>
      new QueryHistory(params, componentInfo.element.parentElement)
  },
  TEMPLATE
);
