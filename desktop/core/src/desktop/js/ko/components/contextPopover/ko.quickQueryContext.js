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

import { MULTI_NAME as SIMPLE_ACE_MULTI } from 'ko/components/simpleAceEditor/ko.simpleAceEditor';
import { NAME as CONTEXT_SELECTOR } from 'ko/components/ko.contextSelector';
import { NAME as DROP_DOWN } from 'ko/components/ko.dropDown';
import { NAME as EXECUTABLE_ACTIONS } from 'apps/notebook2/components/ko.executableActions';
import { NAME as SIMPLE_RESULT_GRID } from 'apps/notebook2/components/resultGrid/ko.simpleResultGrid';

import componentUtils from 'ko/components/componentUtils';
import DisposableComponent from 'ko/components/DisposableComponent';
import Executor from 'apps/notebook2/execution/executor';
import SqlExecutable from 'apps/notebook2/execution/sqlExecutable';
import sqlStatementsParser from 'parse/sqlStatementsParser';
import { CONFIG_REFRESHED_EVENT, GET_KNOWN_CONFIG_EVENT } from 'utils/hueConfig';
import huePubSub from 'utils/huePubSub';

export const NAME = 'quick-query-context';

// prettier-ignore
const TEMPLATE = `
<div class="context-popover-flex-fill" style="overflow: auto;">
  <!-- ko hueSpinner: { spin: loadingConfig, center: true, size: 'xlarge' } --><!-- /ko -->
  <!-- ko ifnot: loadingConfig -->
    <div style="display: inline-block" data-bind="
      component: {
        name: '${ DROP_DOWN }',
        params: {
          value: interpreter,
          labelAttribute: 'displayName',
          entries: availableInterpreters,
          linkTitle: 'Active connector'
        }
      }
    "></div>
    <!-- ko if: interpreter() -->
      <div class="margin-left-10" style="display: inline-block" data-bind="
        component: {
          name: '${ CONTEXT_SELECTOR }',
          params: {
            sourceType: interpreter().type,
            compute: compute,
            namespace: namespace,
            availableDatabases: availableDatabases,
            database: database,
            hideLabels: true
          }
        }
      "></div>
    <!-- /ko -->
    <!-- ko ifnot: loadingContext -->
      <!-- ko with: interpreter -->
        <div style="margin: 10px;" data-bind="
          component: {
            name: '${ SIMPLE_ACE_MULTI }',
            params: {
              autocomplete: $parent.autocomplete,
              value: $parent.statement,
              lines: 3,
              aceOptions: {
                minLines: 3,
                maxLines: 5
              },
              mode: dialect,
              database: $parent.database,
              availableDatabases: $parent.availableDatabases,
              namespace: $parent.namespace,
              compute: $parent.compute,
              executor: $parent.executor,
              activeExecutable: $parent.activeExecutable
            }
          }
        "></div>
        <div data-bind="
          component: {
            name: '${ EXECUTABLE_ACTIONS }',
            params: { activeExecutable: $parent.activeExecutable }
          }
        "></div>
        <div data-bind="
          component: {
            name: '${ SIMPLE_RESULT_GRID }',
            params: { activeExecutable: $parent.activeExecutable }
          }
        "></div>
      <!-- /ko -->
    <!-- /ko -->
  <!-- /ko -->
</div>
`;

class QuickQueryContext extends DisposableComponent {
  constructor(params) {
    super(params);

    this.availableInterpreters = ko.observableArray();
    this.interpreter = ko.observable();

    this.availableDatabases = ko.observableArray();
    this.database = ko.observable();

    this.activeExecutable = ko.observable();

    // TODO: Switch over to connector in ko.simpleAceEditor
    this.namespace = ko.observable();
    this.compute = ko.observable();

    this.loadingConfig = ko.observable(true);

    this.statement = ko.observable();

    this.loadingContext = ko.pureComputed(
      () => !this.namespace() || !this.compute() || !this.database()
    );
    this.dialect = ko.pureComputed(() => this.interpreter() && this.interpreter().dialect);
    this.type = ko.pureComputed(() => this.interpreter() && this.interpreter().type);
    this.defaultLimit = ko.observable(10);

    this.executor = new Executor({
      sourceType: this.type,
      namespace: this.namespace,
      compute: this.compute,
      connector: this.interpreter,
      defaultLimit: this.defaultLimit
    });

    this.autocomplete = ko.pureComputed(
      () => this.interpreter() && { type: this.interpreter().dialect }
    );

    this.subscribe(CONFIG_REFRESHED_EVENT, this.updateFromConfig.bind(this));
    huePubSub.publish(GET_KNOWN_CONFIG_EVENT, this.updateFromConfig.bind(this));

    let refreshExecutableThrottle = -1;
    const refreshExecutable = () => {
      window.clearTimeout(refreshExecutableThrottle);
      refreshExecutableThrottle = window.setTimeout(() => {
        const parsedStatement = sqlStatementsParser.parse(this.statement() || '')[0];

        const executable = new SqlExecutable({
          executor: this.executor,
          parsedStatement: parsedStatement,
          database: this.database()
        });
        this.activeExecutable(executable);
        this.executor.setExecutables([executable]);
      }, 200);
    };

    this.subscribe(this.statement, refreshExecutable);
    this.subscribe(this.database, refreshExecutable);
  }

  updateFromConfig(config) {
    if (
      config &&
      config.app_config &&
      config.app_config.editor &&
      config.app_config.editor.interpreters
    ) {
      this.availableInterpreters(
        config.app_config.editor.interpreters.filter(interpreter => interpreter.is_sql)
      );
    } else {
      this.availableInterpreters([]);
    }

    const found =
      this.interpreter() &&
      this.availableInterpreters().some(interpreter => {
        if (interpreter.type === this.interpreter().type) {
          this.interpreter(interpreter);
          return true;
        }
      });
    if (!found) {
      this.interpreter(
        this.availableInterpreters().length ? this.availableInterpreters()[0] : undefined
      );
    }
    this.loadingConfig(false);
  }
}

componentUtils.registerComponent(NAME, QuickQueryContext, TEMPLATE);
