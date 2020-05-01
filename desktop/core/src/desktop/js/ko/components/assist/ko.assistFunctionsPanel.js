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

import apiHelper from 'api/apiHelper';
import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import { PigFunctions, SqlFunctions } from 'sql/sqlFunctions';
import I18n from 'utils/i18n';
import { CONFIG_REFRESHED_EVENT, filterEditorConnectors } from 'utils/hueConfig';

export const NAME = 'assist-functions-panel';
// prettier-ignore
const TEMPLATE = `
  <div class="assist-inner-panel">
    <div class="assist-flex-panel">
      <div class="assist-flex-header">
        <div class="assist-inner-header">
          <div class="function-dialect-dropdown" data-bind="component: { name: 'hue-drop-down', params: { fixedPosition: true, value: activeDialect, entries: availableDialects, linkTitle: '${I18n(
            'Selected dialect'
          )}' } }" style="display: inline-block"></div>
        </div>
      </div>
      <div class="assist-flex-search">
        <div class="assist-filter">
          <form autocomplete="off">
            <input class="clearable" type="text" ${ window.PREVENT_AUTOFILL_INPUT_ATTRS } placeholder="Filter..." data-bind="clearable: query, value: query, valueUpdate: 'afterkeydown'">
          </form>
        </div>
      </div>
      <div data-bind="css: { 'assist-flex-fill': !selectedFunction(), 'assist-flex-half': selectedFunction() }">
        <!-- ko ifnot: query -->
        <ul class="assist-function-categories" data-bind="foreach: activeCategories">
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
        <div class="assist-panel-close"><button class="close" data-bind="click: function() { $parent.selectedFunction(null); }">&times;</button></div>
        <div class="assist-function-signature blue" data-bind="draggableText: { text: draggable, meta: { type: 'function' } }, text: signature, event: { 'dblclick': function () { huePubSub.publish('editor.insert.at.cursor', { text: draggable }); } }"></div>
        <!-- ko if: description -->
        <div data-bind="html: descriptionMatch"></div>
        <!-- /ko -->
      </div>
      <!-- /ko -->
    </div>
  </div>
`;

class AssistFunctionsPanel {
  constructor(params) {
    this.categories = {};

    this.connector = params.connector;

    this.activeDialect = ko.observable();
    this.availableDialects = ko.observableArray();

    this.query = ko.observable().extend({ rateLimit: 400 });
    this.selectedFunction = ko.observable();

    const selectedFunctionPeDialect = {};

    this.selectedFunction.subscribe(newFunction => {
      if (newFunction) {
        selectedFunctionPeDialect[this.activeDialect()] = newFunction;
        if (!newFunction.category.open()) {
          newFunction.category.open(true);
        }
      }
    });

    this.activeCategories = ko.observableArray();

    this.filteredFunctions = ko.pureComputed(() => {
      const result = [];
      const lowerCaseQuery = this.query().toLowerCase();
      const replaceRegexp = new RegExp('(' + lowerCaseQuery + ')', 'i');
      this.activeCategories().forEach(category => {
        category.functions.forEach(fn => {
          if (fn.signature.toLowerCase().indexOf(lowerCaseQuery) === 0) {
            fn.weight = 2;
            fn.signatureMatch(fn.signature.replace(replaceRegexp, '<b>$1</b>'));
            fn.descriptionMatch(fn.description);
            result.push(fn);
          } else if (fn.signature.toLowerCase().indexOf(lowerCaseQuery) !== -1) {
            fn.weight = 1;
            fn.signatureMatch(fn.signature.replace(replaceRegexp, '<b>$1</b>'));
            fn.descriptionMatch(fn.description);
            result.push(fn);
          } else if (
            fn.description &&
            fn.description.toLowerCase().indexOf(lowerCaseQuery) !== -1
          ) {
            fn.signatureMatch(fn.signature);
            fn.descriptionMatch(fn.description.replace(replaceRegexp, '<b>$1</b>'));
            fn.weight = 0;
            result.push(fn);
          } else {
            if (fn.signatureMatch() !== fn.signature) {
              fn.signatureMatch(fn.signature);
            }
            if (fn.descriptionMatch() !== fn.desciption) {
              fn.descriptionMatch(fn.description);
            }
          }
        });
      });
      result.sort((a, b) => {
        if (a.weight !== b.weight) {
          return b.weight - a.weight;
        }
        return a.signature.localeCompare(b.signature);
      });
      return result;
    });

    this.activeDialect.subscribe(newDialect => {
      if (newDialect) {
        this.selectedFunction(selectedFunctionPeDialect[newDialect]);
        this.activeCategories(this.categories[newDialect]);
        apiHelper.setInTotalStorage('assist', 'function.panel.active.dialect', newDialect);
      }
    });

    const updateDialect = dialect => {
      this.availableDialects().every(availableDialect => {
        if (availableDialect.toLowerCase() === dialect) {
          if (this.activeDialect() !== availableDialect) {
            this.activeDialect(availableDialect);
          }
          return false;
        }
        return true;
      });
    };

    this.connector.subscribe(connector => {
      if (connector) {
        updateDialect(connector.dialect);
      }
    });

    const configUpdated = () => {
      const lastActiveDialect =
        this.activeDialect() ||
        apiHelper.getFromTotalStorage('assist', 'function.panel.active.dialect');

      const uniqueDialects = {};

      const configuredDialects = filterEditorConnectors(connector => {
        const isMatch =
          !uniqueDialects[connector.dialect] &&
          (connector.dialect === 'hive' ||
            connector.dialect === 'impala' ||
            connector.dialect === 'pig');
        uniqueDialects[connector.dialect] = true;
        return isMatch;
      }).map(connector => connector.dialect);
      configuredDialects.sort();
      this.availableDialects(configuredDialects);

      this.availableDialects().forEach(dialect => {
        this.initFunctions(dialect);
      });

      if (
        lastActiveDialect &&
        this.availableDialects().find(dialect => dialect === lastActiveDialect)
      ) {
        this.activeDialect(lastActiveDialect);
      } else {
        this.activeDialect(
          this.availableDialects().length ? this.availableDialects()[0] : undefined
        );
      }
      if (this.connector()) {
        updateDialect(this.connector().dialect);
      }
    };

    configUpdated();
    huePubSub.subscribe(CONFIG_REFRESHED_EVENT, configUpdated);
  }

  initFunctions(dialect) {
    this.categories[dialect] = [];
    const functions =
      dialect === 'pig'
        ? PigFunctions.CATEGORIZED_FUNCTIONS
        : SqlFunctions.CATEGORIZED_FUNCTIONS[dialect.toLowerCase()];

    functions.forEach(category => {
      const koCategory = {
        name: category.name,
        open: ko.observable(false),
        functions: Object.keys(category.functions).map(key => {
          const fn = category.functions[key];
          return {
            draggable: fn.draggable,
            signature: fn.signature,
            signatureMatch: ko.observable(fn.signature),
            description: fn.description,
            descriptionMatch: ko.observable(fn.description)
          };
        })
      };
      koCategory.functions.forEach(fn => {
        fn.category = koCategory;
      });
      this.categories[dialect].push(koCategory);
    });
  }
}

componentUtils.registerStaticComponent(NAME, AssistFunctionsPanel, TEMPLATE);

export default AssistFunctionsPanel;
