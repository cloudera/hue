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
import { CONTEXT_SELECTOR_COMPONENT } from 'ko/components/ko.contextSelector';
import { HUE_DROP_DOWN_COMPONENT } from 'ko/components/ko.dropDown';
import { SIMPLE_RESULT_GRID_COMPONENT } from 'apps/notebook2/components/resultGrid/ko.simpleResultGrid';

import 'apps/notebook2/components/ExecutableActionsKoBridge.vue';

import componentUtils from 'ko/components/componentUtils';
import DisposableComponent from 'ko/components/DisposableComponent';
import Executor from 'apps/notebook2/execution/executor';
import SqlExecutable from 'apps/notebook2/execution/sqlExecutable';
import sqlStatementsParser from 'parse/sqlStatementsParser';
import { CONFIG_REFRESHED_EVENT, filterEditorConnectors } from 'utils/hueConfig';

export const NAME = 'quick-query-context';

// prettier-ignore
const TEMPLATE = `
<div class="context-popover-flex-fill" style="overflow: auto;">
  <div style="display: inline-block" data-bind="
    component: {
      name: '${ HUE_DROP_DOWN_COMPONENT }',
      params: {
        value: connector,
        labelAttribute: 'displayName',
        entries: availableConnectors,
        linkTitle: 'Active connector'
      }
    }
  "></div>
  <!-- ko if: connector() -->
    <div class="margin-left-10" style="display: inline-block" data-bind="
      component: {
        name: '${ CONTEXT_SELECTOR_COMPONENT }',
        params: {
          connector: connector,
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
    <!-- ko with: connector -->
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
      <executable-actions-ko-bridge data-bind="vueKoProps: {
          executableObservable: $parent.activeExecutable
        }"></executable-actions-ko-bridge>
      <div data-bind="
        component: {
          name: '${ SIMPLE_RESULT_GRID_COMPONENT }',
          params: { activeExecutable: $parent.activeExecutable }
        }
      "></div>
    <!-- /ko -->
  <!-- /ko -->
</div>
`;

class QuickQueryContext extends DisposableComponent {
  constructor(params) {
    super(params);

    this.availableConnectors = ko.observableArray();
    this.connector = ko.observable();

    this.availableDatabases = ko.observableArray();
    this.database = ko.observable();

    this.activeExecutable = ko.observable();

    // TODO: Switch over to connector in ko.simpleAceEditor
    this.namespace = ko.observable();
    this.compute = ko.observable();

    this.statement = ko.observable();

    this.loadingContext = ko.pureComputed(
      () => !this.namespace() || !this.compute() || !this.database()
    );
    this.dialect = ko.pureComputed(() => this.connector() && this.connector().dialect);
    this.type = ko.pureComputed(() => this.connector() && this.connector().id);
    this.defaultLimit = ko.observable(10);

    this.executor = new Executor({
      sourceType: this.type,
      namespace: this.namespace,
      compute: this.compute,
      connector: this.connector,
      defaultLimit: this.defaultLimit
    });

    this.autocomplete = ko.pureComputed(
      () => this.connector() && { type: this.connector().dialect, connector: this.connector }
    );

    this.updateFromConfig();
    this.subscribe(CONFIG_REFRESHED_EVENT, this.updateFromConfig.bind(this));

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

  updateFromConfig() {
    const configuredSqlConnectors = filterEditorConnectors(connector => connector.is_sql);
    this.availableConnectors(configuredSqlConnectors);

    const found =
      this.connector() &&
      this.availableConnectors().some(connector => {
        if (connector.id === this.connector().id) {
          this.connector(connector);
          return true;
        }
      });
    if (!found) {
      this.connector(this.availableConnectors().length ? this.availableConnectors()[0] : undefined);
    }
  }
}

componentUtils.registerComponent(NAME, QuickQueryContext, TEMPLATE);
