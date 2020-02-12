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

import 'ko/components/simpleAceEditor/ko.simpleAceEditor';
import 'ko/components/ko.contextSelector';
import 'ko/components/ko.dropDown';

import componentUtils from 'ko/components/componentUtils';
import DisposableComponent from 'ko/components/DisposableComponent';
import { CONFIG_REFRESHED_EVENT, GET_KNOWN_CONFIG_EVENT } from 'utils/hueConfig';
import huePubSub from 'utils/huePubSub';

export const NAME = 'quick-query-context';

// prettier-ignore
const TEMPLATE = `
<div class="context-popover-flex-fill" style="overflow: auto;">
  <!-- ko hueSpinner: { spin: loadingConfig, center: true, size: 'xlarge' } --><!-- /ko -->
  <!-- ko ifnot: loadingConfig -->
    <div style="display: inline-block" data-bind="component: { 
        name: 'hue-drop-down',
        params: {
          value: interpreter,
          labelAttribute: 'displayName',
          entries: availableInterpreters,
          linkTitle: 'Active connector'
        }
      }
    "></div>
    <!-- ko if: interpreter() -->
      <div class="margin-left-10" style="display: inline-block">
        <!-- ko component: {
          name: 'hue-context-selector',
          params: {
            sourceType: interpreter().type,
            compute: compute,
            namespace: namespace,
            availableDatabases: availableDatabases,
            database: database,
            hideLabels: true
          }
        } --><!-- /ko -->
      </div>
    <!-- /ko -->
    <!-- ko ifnot: loadingContext -->
    <div style="margin: 10px;" data-bind="
      component: { 
        name: 'hue-simple-ace-editor-multi',
        params: {
          autocomplete: autocomplete,
          value: statement,
          lines: 5,
          aceOptions: {
            minLines: 10,
            maxLines: 25
          },
          mode: dialect,
          database: database,
          namespace: namespace,
          compute: compute,
          temporaryOnly: true
        }
      }
    "></div>
    <div>
      
    </div>
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

    // TODO: Switch over to connector in ko.simpleAceEditor
    this.namespace = ko.observable();
    this.compute = ko.observable();

    this.loadingConfig = ko.observable(true);

    this.statement = ko.observable();

    this.loadingContext = ko.pureComputed(
      () => !this.namespace() || !this.compute() || !this.database()
    );

    this.executor = undefined;

    this.dialect = ko.pureComputed(() => this.interpreter() && this.interpreter().dialect);
    this.autocomplete = ko.pureComputed(
      () => this.interpreter() && { type: this.interpreter().dialect }
    );

    this.subscribe(CONFIG_REFRESHED_EVENT, this.updateFromConfig.bind(this));
    huePubSub.publish(GET_KNOWN_CONFIG_EVENT, this.updateFromConfig.bind(this));
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
