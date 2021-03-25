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

import { CONFIG_REFRESHED_TOPIC } from 'config/events';
import { filterEditorConnectors } from 'config/hueConfig';
import componentUtils from 'ko/components/componentUtils';
import { HUE_DROP_DOWN_COMPONENT } from 'ko/components/ko.dropDown';
import sqlReferenceRepository from 'sql/reference/sqlReferenceRepository';
import {
  CLEAR_UDF_CACHE_EVENT,
  DESCRIBE_UDF_EVENT,
  getUdfCategories,
  UDF_DESCRIBED_EVENT
} from 'sql/reference/sqlUdfRepository';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';

export const NAME = 'assist-functions-panel';
// prettier-ignore
const TEMPLATE = `
  <div class="assist-inner-panel">
    <div class="assist-flex-panel">
      <div class="assist-flex-header">
        <div class="assist-inner-header">
          <div class="function-dialect-dropdown" style="display: inline-block" data-bind="
              component: {
                name: '${ HUE_DROP_DOWN_COMPONENT }',
                params: {
                  fixedPosition: true,
                  value: activeConnectorUdfs,
                  entries: availableConnectorUdfs,
                  linkTitle: '${I18n('Selected type')}'
                 }
              }
            "></div>
            <div class="pull-right" style="margin-right: 15px;" data-bind="with: activeConnectorUdfs">
               <!-- ko ifnot: loading -->
                 <a class="inactive-action" href="javascript:void(0)" data-bind="click: refresh" title="${I18n('Refresh')}">
                   <i class="pointer fa fa-refresh"></i>
                 </a>
               <!-- /ko -->
               <!-- ko if: loading -->
                 <i class="fa fa-refresh fa-spin blue"></i>
               <!-- /ko -->
            </div>
        </div>
      </div>
      <!-- ko with: activeConnectorUdfs -->
        <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
        <!-- ko ifnot: loading -->
          <div class="assist-flex-search">
            <div class="assist-filter">
              <form autocomplete="off">
                <input class="clearable" type="text" ${ window.PREVENT_AUTOFILL_INPUT_ATTRS } placeholder="Filter..." data-bind="clearable: query, value: query, valueUpdate: 'afterkeydown'">
              </form>
            </div>
          </div>
          <div data-bind="css: { 'assist-flex-fill': !selectedFunction(), 'assist-flex-half': selectedFunction() }">
            <!-- ko ifnot: query -->
              <ul class="assist-function-categories" data-bind="foreach: categories">
                <li>
                  <a class="black-link" href="javascript: void(0);" data-bind="toggle: open"><i class="fa fa-fw" data-bind="css: { 'fa-chevron-right': !open(), 'fa-chevron-down': open }"></i> <span data-bind="text: name"></span></a>
                  <ul class="assist-functions" data-bind="slideVisible: open, foreach: functions">
                    <li data-bind="tooltip: { title: description, placement: 'left', delay: 1000 }">
                      <a class="assist-field-link" href="javascript: void(0);" data-bind="draggableText: { text: draggable, meta: { type: 'function' } }, css: { 'blue': $parents[1].selectedFunction() === $data }, multiClick: { click: function () { $parents[1].selectedFunction($data); }, dblClick: function () { huePubSub.publish('editor.insert.at.cursor', { text: draggable }); } }, text: signature"></a>
                    </li>
                  </ul>
                </li>
              </ul>
            <!-- /ko -->
            <!-- ko if: query -->
              <!-- ko if: filteredFunctions().length > 0 -->
              <ul class="assist-functions" data-bind="foreach: filteredFunctions">
                <li data-bind="tooltip: { title: description, placement: 'left', delay: 1000 }">
                  <a class="assist-field-link" href="javascript: void(0);" data-bind="draggableText: { text: draggable, meta: { type: 'function' } }, css: { 'blue': $parent.selectedFunction() === $data }, multiClick: { click: function () { $parent.selectedFunction($data); }, dblClick: function () { huePubSub.publish('editor.insert.at.cursor', { text: draggable }); } }, html: signatureMatch"></a>
                </li>
              </ul>
              <!-- /ko -->
              <!-- ko if: filteredFunctions().length === 0 -->
              <ul class="assist-functions">
                <li class="assist-no-entries">${I18n('No results found.')}</li>
              </ul>
              <!-- /ko -->
            <!-- /ko -->
          </div>
          <!-- ko if: selectedFunction -->
            <div class="assist-flex-half assist-function-details" data-bind="with: selectedFunction">
              <!-- ko hueSpinner: { spin: !loaded(), center: true, size: 'large' } --><!-- /ko -->
              <!-- ko if: loaded -->
              <div class="assist-panel-close"><button class="close" data-bind="click: function() { $parent.selectedFunction(null); }">&times;</button></div>
              <div class="assist-function-signature blue" data-bind="draggableText: { text: draggable, meta: { type: 'function' } }, text: signature, event: { 'dblclick': function () { huePubSub.publish('editor.insert.at.cursor', { text: draggable }); } }"></div>
              <!-- ko if: description -->
              <div data-bind="html: descriptionMatch"></div>
              <!-- /ko -->
              <!-- /ko -->
            </div>
          <!-- /ko -->
        <!-- /ko -->
      <!-- /ko -->
    </div>
  </div>
`;

class ConnectorUdfCategories {
  constructor(connector) {
    this.connector = connector;
    this.loading = ko.observable(true);
    this.initialized = false;

    this.label = this.connector.displayName;

    this.categories = ko.observableArray([]);

    this.query = ko.observable().extend({ rateLimit: 400 });

    this.selectedFunction = ko.observable();

    this.selectedFunction.subscribe(selectedUdf => {
      if (selectedUdf) {
        if (!selectedUdf.category.open()) {
          selectedUdf.category.open(true);
        }
        if (!selectedUdf.loaded()) {
          huePubSub.publish(DESCRIBE_UDF_EVENT, {
            connector: this.connector,
            udfName: selectedUdf.name
          });
        }
      }
    });

    huePubSub.subscribe(UDF_DESCRIBED_EVENT, details => {
      // TODO: Show UDFs from databases in the assist functions panel
      if (!details.database && details.connector.id === this.connector.id) {
        this.categories().some(category =>
          category.functions.some(udf => {
            if (udf.name === details.udf.name) {
              udf.loaded(details.udf.described);
              udf.signature(details.udf.signature);
              udf.signatureMatch(details.udf.signature);
              udf.description(details.udf.description);
              udf.descriptionMatch(details.udf.description);
              udf.loaded(details.udf.described);
              return true;
            }
          })
        );
      }
    });

    this.filteredFunctions = ko.pureComputed(() => {
      const result = [];
      if (this.loading()) {
        return result;
      }
      const lowerCaseQuery = this.query().toLowerCase();
      const replaceRegexp = new RegExp('(' + lowerCaseQuery + ')', 'i');
      this.categories().forEach(category => {
        category.functions.forEach(fn => {
          if (fn.signature().toLowerCase().indexOf(lowerCaseQuery) === 0) {
            fn.weight = 2;
            fn.signatureMatch(fn.signature().replace(replaceRegexp, '<b>$1</b>'));
            fn.descriptionMatch(fn.description());
            result.push(fn);
          } else if (fn.signature().toLowerCase().indexOf(lowerCaseQuery) !== -1) {
            fn.weight = 1;
            fn.signatureMatch(fn.signature().replace(replaceRegexp, '<b>$1</b>'));
            fn.descriptionMatch(fn.description());
            result.push(fn);
          } else if (
            fn.description() &&
            fn.description().toLowerCase().indexOf(lowerCaseQuery) !== -1
          ) {
            fn.signatureMatch(fn.signature());
            fn.descriptionMatch(fn.description().replace(replaceRegexp, '<b>$1</b>'));
            fn.weight = 0;
            result.push(fn);
          } else {
            if (fn.signatureMatch() !== fn.signature()) {
              fn.signatureMatch(fn.signature());
            }
            if (fn.descriptionMatch() !== fn.description()) {
              fn.descriptionMatch(fn.description());
            }
          }
        });
      });
      result.sort((a, b) => {
        if (a.weight !== b.weight) {
          return b.weight - a.weight;
        }
        return a.signature().localeCompare(b.signature());
      });
      return result;
    });
  }

  async init() {
    if (this.initialized) {
      return;
    }
    await this.getUdfs();
    this.initialized = true;
  }

  async refresh() {
    this.loading(true);
    huePubSub.publish(CLEAR_UDF_CACHE_EVENT, {
      connector: this.connector,
      callback: this.getUdfs.bind(this)
    });
  }

  async getUdfs() {
    this.loading(true);
    const categories = [];
    const functions = await getUdfCategories(sqlReferenceRepository, this.connector);
    functions.forEach(category => {
      const koCategory = {
        name: category.name,
        open: ko.observable(false),
        functions: Object.keys(category.functions).map(key => {
          const fn = category.functions[key];
          return {
            name: fn.name,
            draggable: fn.draggable,
            signature: ko.observable(fn.signature),
            signatureMatch: ko.observable(fn.signature),
            description: ko.observable(fn.description),
            descriptionMatch: ko.observable(fn.description),
            loaded: ko.observable(fn.described)
          };
        })
      };
      koCategory.functions.forEach(fn => {
        fn.category = koCategory;
      });
      categories.push(koCategory);
    });
    this.categories(categories);
    this.loading(false);
  }
}

class AssistFunctionsPanel {
  constructor(params) {
    this.categories = {};

    this.activeConnector = params.activeConnector;

    this.availableConnectorUdfs = ko.observableArray();
    this.activeConnectorUdfs = ko.observable();

    this.activeConnectorUdfs.subscribe(async activeConnectorUdfs => {
      await activeConnectorUdfs.init();
      setInLocalStorage(
        'assist.function.panel.active.connector.type',
        activeConnectorUdfs.connector.type
      );
    });

    const setCategoriesFromConnector = connector => {
      this.availableConnectorUdfs().some(availableConnectorUdfs => {
        if (availableConnectorUdfs.connector.type === connector.type) {
          this.activeConnectorUdfs(availableConnectorUdfs);
          return true;
        }
      });
    };

    this.activeConnector.subscribe(connector => {
      if (connector) {
        setCategoriesFromConnector(connector);
      }
    });

    const configUpdated = () => {
      const lastActiveConnectorType =
        (this.activeConnector() && this.activeConnector().type) ||
        getFromLocalStorage('assist.function.panel.active.connector.type');

      const availableConnectorUdfs = filterEditorConnectors(
        connector => connector.dialect && sqlReferenceRepository.hasUdfCategories(connector.dialect)
      ).map(connector => new ConnectorUdfCategories(connector));

      availableConnectorUdfs.sort((a, b) =>
        a.connector.displayName.localeCompare(b.connector.displayName)
      );

      this.availableConnectorUdfs(availableConnectorUdfs);

      let activeConnectorUdfs;

      if (lastActiveConnectorType) {
        activeConnectorUdfs = this.availableConnectorUdfs().find(
          connectorUdf => connectorUdf.connector.type === lastActiveConnectorType
        );
      }

      if (!activeConnectorUdfs && this.availableConnectorUdfs().length) {
        activeConnectorUdfs = this.availableConnectorUdfs()[0];
      }

      this.activeConnectorUdfs(activeConnectorUdfs);

      setCategoriesFromConnector(this.activeConnector());
    };

    configUpdated();
    huePubSub.subscribe(CONFIG_REFRESHED_TOPIC, configUpdated);
  }
}

componentUtils.registerStaticComponent(NAME, AssistFunctionsPanel, TEMPLATE);

export default AssistFunctionsPanel;
