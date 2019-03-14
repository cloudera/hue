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

import componentUtils from './componentUtils';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import I18n from 'utils/i18n';

const TEMPLATE = `
  <div class="context-popover-inline-autocomplete" style="display: flex">
    <div class="context-popover-sample-filter">
      <!-- ko component: {
        name: 'inline-autocomplete',
        params: {
          querySpec: querySpec,
          autocompleteFromEntries: autocompleteFromEntries
        }
      } --><!-- /ko -->
    </div>
    <!-- ko if: showOperations -->
    <div class="context-popover-sample-controls">
      <div class="margin-left-10 inline-block" data-bind="component: { name: 'hue-drop-down', params: { value: operation, entries: operations } }"></div>
      <div class="margin-left-10 inactive-action inline-block">
        <!-- ko if: loadingSamples() || refreshSampleEnabled() -->
        <a href="javascript:void(0);" data-bind="click: function () { refreshSampleEnabled(false); cancelRunningQueries() }"><i class="fa fa-stop"></i></a>
        <!-- /ko -->
        <!-- ko if: !loadingSamples() && !refreshSampleEnabled() -->
        <a href="javascript:void(0);" data-bind="click: function () { loadSamples(true) }"><i class="fa fa-play"></i></a>
        <!-- /ko -->
      </div>
    </div>
    <!-- /ko -->
  </div>

  <table class="table table-condensed table-nowrap">
    <thead>
    <tr>
      <th>${I18n('Sample')}</th>
    </tr>
    </thead>
    <!-- ko if: loadingSamples() && (!refreshSampleEnabled() || (refreshSampleEnabled() && columnSamples().length === 0))  -->
    <tbody>
    <tr>
      <td><!-- ko hueSpinner: { spin: true, inline: true } --><!-- /ko --></td>
    </tr>
    </tbody>
    <!-- /ko -->

    <!-- ko if: !loadingSamples() || (refreshSampleEnabled() && columnSamples().length > 0)  -->
    <tbody data-bind="foreach: filteredColumnSamples">
    <tr>
      <!-- ko if: typeof $parent.onSampleClick === 'function' -->
      <td class="sample-column pointer" data-bind="html: $data, attr: { 'title': hueUtils.html2text($data) }, click: $parent.sampleClick"></td>
      <!-- /ko -->
      <!-- ko ifnot: typeof $parent.onSampleClick === 'function' -->
      <td class="sample-column" data-bind="html: $data, attr: { 'title': hueUtils.html2text($data) }"></td>
      <!-- /ko -->
    </tr>
    </tbody>
    <!-- ko if: filteredColumnSamples().length === 0 -->
    <tbody>
    <tr>
      <!-- ko ifnot: hasErrors -->
      <td style="font-style: italic;">${I18n('No entries found')}</td>
      <!-- /ko -->
      <!-- ko if: hasErrors -->
      <td style="font-style: italic;">${I18n('Error loading samples')}</td>
      <!-- /ko -->
    </tr>
    </tbody>
    <!-- /ko -->
    <!-- /ko -->
  </table>
`;

class FieldSamples {
  constructor(params) {
    const self = this;
    self.catalogEntry = ko.isObservable(params.catalogEntry)
      ? params.catalogEntry
      : ko.observable(params.catalogEntry);
    self.onSampleClick = params.onSampleClick;
    self.refreshSampleInterval = params.refreshSampleInterval;
    self.refreshSampleTimeout = -1;
    self.refreshSampleEnabled = ko.observable(!!self.refreshSampleInterval);

    self.cancellablePromises = [];
    self.querySpec = ko.observable();

    self.hasErrors = ko.observable();
    self.loadingSamples = ko.observable();

    self.showOperations =
      !self.catalogEntry().isTemporary &&
      (self.catalogEntry().getSourceType() === 'impala' ||
        self.catalogEntry().getSourceType() === 'hive');

    self.sampleClick = function(html) {
      self.onSampleClick(hueUtils.html2text(html));
      huePubSub.publish('context.popover.hide');
    };

    self.operations = [
      {
        label: I18n('default'),
        type: 'default'
      },
      {
        label: I18n('distinct'),
        type: 'distinct'
      },
      {
        label: I18n('max'),
        type: 'max'
      },
      {
        label: I18n('min'),
        type: 'min'
      }
    ];

    self.operation = ko.observable(self.operations[0]);

    self.operation.subscribe(() => {
      self.loadSamples();
    });

    self.columnSamples = ko.observableArray();

    self.filteredColumnSamples = ko.pureComputed(() => {
      if (!self.querySpec() || self.querySpec().query === '') {
        return self.columnSamples();
      }

      return self.columnSamples().filter(sampleValue => {
        if (typeof sampleValue === 'undefined' || sampleValue === null) {
          return false;
        }
        return self.querySpec().text.every(text => {
          const textLower = text.toLowerCase();
          return (
            sampleValue
              .toString()
              .toLowerCase()
              .indexOf(textLower) !== -1
          );
        });
      });
    });

    self.autocompleteFromEntries = function(nonPartial, partial) {
      const result = [];
      const partialLower = partial.toLowerCase();
      self.columnSamples().forEach(sample => {
        if (
          sample[0]
            .toString()
            .toLowerCase()
            .indexOf(partialLower) === 0
        ) {
          result.push(nonPartial + partial + sample[0].toString().substring(partial.length));
        }
      });
      return result;
    };

    self.loadSamples();
  }

  loadSamples(refreshCache) {
    const self = this;
    window.clearTimeout(self.refreshSampleTimeout);
    self.cancelRunningQueries();
    self.loadingSamples(true);
    self.cancellablePromises.push(
      self
        .catalogEntry()
        .getSample({
          silenceErrors: true,
          cancellable: true,
          refreshCache: refreshCache,
          operation: self.operation().type
        })
        .done(samples => {
          if (samples.data && samples.data.length) {
            self.columnSamples(samples.data);
          }
        })
        .fail(() => {
          self.hasErrors(true);
        })
        .always(() => {
          self.loadingSamples(false);
          if (self.refreshSampleTimeout && self.refreshSampleEnabled()) {
            self.refreshSampleTimeout = window.setTimeout(() => {
              self.loadSamples(true);
            }, self.refreshSampleInterval);
          }
        })
    );
  }

  cancelRunningQueries() {
    const self = this;
    window.clearTimeout(self.refreshSampleTimeout);
    while (self.cancellablePromises.length) {
      const promise = self.cancellablePromises.pop();
      if (promise.cancel) {
        promise.cancel();
      }
    }
  }

  dispose() {
    const self = this;
    self.cancelRunningQueries();
  }
}

componentUtils.registerComponent('field-samples', FieldSamples, TEMPLATE);
