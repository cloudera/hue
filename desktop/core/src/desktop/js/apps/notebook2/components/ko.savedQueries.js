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

import * as ko from 'knockout';

import componentUtils from 'ko/components/componentUtils';
import DisposableComponent from 'ko/components/DisposableComponent';
import I18n from 'utils/i18n';
import { NAME as PAGINATOR_COMPONENT } from './ko.paginator';
import apiHelper from 'api/apiHelper';
import { cancelActiveRequest } from 'api/apiUtils';

export const UPDATE_SAVED_QUERIES_EVENT = 'update.saved.queries';
export const NAME = 'saved-queries';

// prettier-ignore
const TEMPLATE = `
<div class="snippet-tab-actions">
  <form autocomplete="off" class="inline-block">
    <input class="input-small search-input" type="text" ${ window.PREVENT_AUTOFILL_INPUT_ATTRS } placeholder="${ I18n('Search...') }" data-bind="
        textInput: filter,
        clearable: filter
      "/>
  </form>
</div>

<div class="snippet-tab-body">
  <!-- ko if: loading -->
    <div>
      <h1 class="empty"><i class="fa fa-spinner fa-spin"></i> ${ I18n('Loading...') }</h1>
    </div>
  <!-- /ko -->

  <!-- ko ifnot: loading -->
    <!-- ko if: hasErrors -->
      <div class="margin-top-10 margin-left-10" style="font-style: italic">${ I18n("Error loading the queries.") }</div>
    <!-- /ko -->
    <!-- ko if: !hasErrors() && !loading() && queries().length === 0 && filter() === '' -->
      <div class="margin-top-10 margin-left-10" style="font-style: italic">${ I18n("You don't have any saved queries.") }</div>
    <!-- /ko -->
    <!-- ko if: !hasErrors() && !loading() && queries().length === 0 && filter() !== '' -->
      <div class="margin-top-10 margin-left-10" style="font-style: italic">${ I18n('No queries found for') } <strong data-bind="text: filter"></strong>.</div>
    <!-- /ko -->
    <!-- ko if: !hasErrors() && !loading() && queries().length > 0 -->
      <table class="table table-condensed margin-top-10 history-table">
        <thead>
        <tr>
          <th style="width: 16%">${ I18n("Name") }</th>
          <th style="width: 50%">${ I18n("Description") }</th>
          <th style="width: 18%">${ I18n("Owner") }</th>
          <th style="width: 16%">${ I18n("Last Modified") }</th>
        </tr>
        </thead>
        <tbody data-bind="foreach: queries">
        <tr data-bind="
            click: function() {
              $parent.openNotebook(uuid);
            },
            css: {
              'highlight': uuid == $parent.currentNotebook.uuid(),
              'pointer': uuid != $parent.currentNotebook.uuid()
            }">
          <td style="width: 16%"><span data-bind="ellipsis: { data: name, length: 50 }"></span></td>
          <td style="width: 50%; white-space: normal"><span data-bind="text: description"></span></td>
          <td style="width: 18%"><span data-bind="text: owner"></span></td>
          <td style="width: 16%"><span data-bind="text: localeFormat(lastModified())"></span></td>
        </tr>
        </tbody>
      </table>
    <!-- /ko -->

    <!-- ko component: {
      name: '${ PAGINATOR_COMPONENT }',
      params: {
        currentPage: currentPage,
        totalPages: totalPages,
        onPageChange: fetchQueries.bind($data)
      }
    } --><!-- /ko -->
  <!-- /ko -->
</div>
`;

const QUERIES_PER_PAGE = 50;

const adaptRawQuery = rawQuery => ({
  uuid: rawQuery.uuid,
  name: ko.observable(rawQuery.name),
  owner: rawQuery.owner,
  description: ko.observable(rawQuery.description),
  lastModified: ko.observable(rawQuery.last_modified)
});

class SavedQueries extends DisposableComponent {
  constructor(params) {
    super();

    this.currentNotebook = params.currentNotebook;
    this.openFunction = params.openFunction;
    this.dialect = params.dialect;
    this.currentTab = params.currentTab;

    this.loading = ko.observable(true);
    this.hasErrors = ko.observable(false);
    this.queries = ko.observableArray();

    this.currentPage = ko.observable(1);
    this.totalPages = ko.observable(1);

    this.lastFetchQueriesRequest = undefined;

    this.filter = ko.observable().extend({ rateLimit: 900 });
    this.filter.subscribe(() => {
      this.fetchQueries();
    });

    this.subscribe(UPDATE_SAVED_QUERIES_EVENT, details => {
      if (!details.save_as) {
        this.queries().some(item => {
          if (item.uuid === details.uuid) {
            item.name(details.name);
            item.description(details.description);
            item.lastModified(details.last_modified);
            return true;
          }
        });
      } else if (this.queries().length) {
        this.queries.unshift(adaptRawQuery(details));
      } else {
        this.fetchQueries();
      }
    });

    if (this.currentTab() === 'savedQueries') {
      this.fetchQueries();
    } else {
      const sub = this.subscribe(this.currentTab, tab => {
        if (tab === 'savedQueries') {
          this.fetchQueries();
          sub.dispose();
        }
      });
    }
  }

  async fetchQueries() {
    cancelActiveRequest(this.lastFetchQueriesRequest);

    this.loading(true);
    this.hasErrors(false);

    this.lastFetchQueriesRequest = apiHelper.searchDocuments({
      successCallback: foundDocuments => {
        this.totalPages(Math.ceil(foundDocuments.count / QUERIES_PER_PAGE));
        this.queries(foundDocuments.documents.map(adaptRawQuery));
        this.loading(false);
        this.hasErrors(false);
      },
      errorCallback: () => {
        this.loading(false);
        this.hasErrors(true);
      },
      page: this.currentPage(),
      limit: QUERIES_PER_PAGE,
      type: 'query-' + this.dialect(),
      query: this.filter(),
      include_trashed: false
    });
  }

  openNotebook(uuid) {
    if (window.getSelection().toString() === '' && uuid !== this.currentNotebook.uuid()) {
      this.openFunction(uuid);
    }
  }
}

componentUtils.registerComponent(NAME, SavedQueries, TEMPLATE);
