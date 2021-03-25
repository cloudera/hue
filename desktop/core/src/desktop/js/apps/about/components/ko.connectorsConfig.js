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

import { simpleGet, simplePost } from 'api/apiUtils';
import { REFRESH_CONFIG_TOPIC } from 'config/events';
import componentUtils from 'ko/components/componentUtils';
import DisposableComponent from 'ko/components/DisposableComponent';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

export const NAME = 'connectors-config';

// prettier-ignore
const TEMPLATE = `
<script type="text/html" id="installed-connectors-page">
  <div class="row-fluid">
    <a href="javascript:void(0)" data-bind="click: addNewConnector.bind($data)">
      + Connector
    </a>
  </div>

  <div data-bind="template: { name: 'connectors-page', data: instances() }"></div>

</script>


<script type="text/html" id="add-connector-page">
  <div class="row-fluid">
    Add a Connector
  </div>

  <div data-bind="template: { name: 'connectors-page', data: connectors() }"></div>
</script>


<script type="text/html" id="connectors-page">
  <div style="margin: 0 10px;">
    <div class="pull-right" style="display: inline-block">
      <div style="display: inline-block; margin-right: 10px;" data-bind="component: {
          name: 'hue-drop-down',
          params: {
            fixedPosition: true,
            value: $parent.selectedConnectorCategory,
            labelAttribute: 'name',
            entries: $parent.filterCategories,
            linkTitle: '${ I18n('Category') }'
          }
        }
      "></div>
      <input type="text" class="input-large" style="padding: 3px 4px; border-radius: 2px; margin-top: 8px; margin-right: 10px;" placeholder="${ I18n('Filter...') }" data-bind="
          clearable: $parent.connectorsFilter,
          valueUpdate: 'afterkeydown'
      ">
      <span>
        <a href="https://docs.gethue.com/administrator/configuration/connectors/" target="_blank">
          <i class="fa fa-question-circle"></i> ${ I18n('Help') }
        </a>
      </span>
    </div>
  </div>

  <div class="card card-small margin-top-10">
    <div class="card-body clearfix">

      <div class="span10">
        <div class="margin-top-10">
          <div data-bind="foreach: $parent.filteredConnectors()">
            <h4 data-bind="text: category_name"></h4>
            <table class="table table-condensed">
              <thead>
                <tr>
                  <th width="30%">${ I18n('Name') }</th>
                  <th>${ I18n('Description') }</th>
                </tr>
              </thead>
              <!-- ko if: $data.values.length > 0 -->
              <tbody data-bind="foreach: values">
                <tr data-bind="click: $parents[2].editConnector.bind($parents[2])">
                  <td data-bind="text: nice_name"></td>
                  <td data-bind="text: description"></td>
                </tr>
              </tbody>
              <!-- /ko -->
              <!-- ko ifnot: $data.values.length > 0 -->
              <tfoot>
                <tr>
                  <td colspan="2">
                    ${ I18n('No connectors') }
                    <!-- ko if: $parents[1].section() === 'installed-connectors-page' -->
                      <a href="javascript:void(0)" data-bind="click: function() { $parents[1].selectedConnectorCategory($data.category); $parents[1].addNewConnector(); }">
                        ${ I18n('Add one ?') }
                      </a>
                    <!-- /ko -->
                  </td>
                </tr>
              </tfoot>
              <!-- /ko -->
            </table>
          </div>

          <!-- ko if: $parent.filteredConnectors().length == 0 -->
          <table class="table table-condensed">
            <thead>
              <tr>
                <th width="30%">${ I18n('Name') }</th>
                <th>${ I18n('Instances') }</th>
              </tr>
            </thead>
            <tfoot>
              <tr>
                <td colspan="2">
                  ${ I18n('No connectors') }
                  <!-- ko if: $parent.section() == 'installed-connectors-page' -->
                    <a href="javascript:void(0)" data-bind="click: function() { $parent.selectedConnectorCategory($data.category); $parent.addNewConnector(); }">
                      ${ I18n('Add one ?') }
                    </a>
                  <!-- /ko -->
                </td>
              </tr>
            </tfoot>
          </table>
          <!-- /ko -->
        </div>
      </div>
    </div>

  </div>
</script>


<script type="text/html" id="connector-page">
  <div class="row-fluid">
    <input data-bind="value: nice_name">
    <!-- ko if: typeof id != 'undefined' -->
      <!-- ko if: id -->
        (<span data-bind="text: name"></span>)
        <a href="javascript:void(0)" data-bind="click: $parent.updateConnector.bind($parent)">
          ${ I18n('Update') }
        </a>
        <a href="javascript:void(0)" data-bind="click: $parent.deleteConnector.bind($parent)">
          ${ I18n('Delete') }
        </a>
      <!-- /ko -->
      <!-- ko ifnot: id -->
        <a href="javascript:void(0)" data-bind="click: $parent.updateConnector.bind($parent)">
          ${ I18n('Save') }
        </a>
        <a href="javascript:void(0)" data-bind="click: function() { $parent.section('add-connector-page'); }">
          ${ I18n('Cancel') }
        </a>
      <!-- /ko -->
    <!-- /ko -->
    <a href="javascript:void(0)" data-bind="click: $parent.testConnector.bind($parent)">
      ${ I18n('Test connection') }
    </a>
    <span>
      <i class="fa fa-spinner fa-spin" data-bind="visible: $parent.testConnectionExecuting()"></i>
      <i class="fa fa-question" data-bind="visible: !$parent.testConnectionExecuted() && !$parent.testConnectionExecuting()"></i>
      <i class="fa fa-check" data-bind="visible: $parent.testConnectionExecuted() && !$parent.testConnectionErrors().length"></i>
      <i class="fa fa-exclamation" data-bind="visible: $parent.testConnectionExecuted() && $parent.testConnectionErrors().length"></i>
      <span data-bind="visible: $parent.testConnectionExecuted() && $parent.testConnectionErrors().length, text: $parent.testConnectionErrors">
      </span>
    </span>
    <table class="table table-condensed">
      <thead>
        <tr>
          <th width="30%">${ I18n('Name') }</th>
          <th>${ I18n('Value') }</th>
        </tr>
      </thead>
      <tbody data-bind="foreach: settings">
        <tr>
          <td data-bind="text: name"></td>
          <td><input data-bind="value: value" class="input-xxlarge"></td>
        </tr>
      </tbody>
    </table>
  </div>
</script>

<div class="container-fluid">
  <a href="javascript:void(0)" data-bind="click: function() { section('installed-connectors-page'); }">
    ${ I18n('Connectors') }
  </a>

  <!-- ko if: section() === 'installed-connectors-page' -->
    <div data-bind="template: { name: 'installed-connectors-page' }"></div>
  <!-- /ko -->

  <!-- ko if: section() === 'add-connector-page' -->
    <div data-bind="template: { name: 'add-connector-page' }"></div>
  <!-- /ko -->

  <!-- ko if: section() === 'connector-page' && instance() -->
    <div data-bind="template: { name: 'connector-page', data: instance() }"></div>
  <!-- /ko -->
</div>
`;

const ALL_CATEGORY = { type: 'all', name: I18n('All') };

class ConnectorsConfig extends DisposableComponent {
  constructor() {
    super();

    this.section = ko.observable('installed-connectors-page');
    this.section.subscribe(() => {
      this.connectorsFilter('');
      this.testConnectionExecuted(false);
    });
    this.categories = ko.observableArray();
    this.filterCategories = ko.pureComputed(() => {
      return [ALL_CATEGORY].concat(this.categories());
    });
    this.selectedConnectorCategory = ko.observable(ALL_CATEGORY);
    this.connectorsFilter = ko.observable();

    this.testConnectionExecuted = ko.observable(false);
    this.testConnectionExecuting = ko.observable(false);
    this.testConnectionErrors = ko.observable('');

    // Handle two types of objects are being listed: connector instances and types
    this.instances = ko.observableArray(); // Connector instances (e.g. connector to a MySql DB on a certain host)
    this.instance = ko.observable();

    this.connectors = ko.observableArray(); // Connector types (e.g. mysql dialect)
    this.connector = ko.observable();

    this.selectedConnectors = ko.pureComputed(() => {
      const connectors =
        this.section() === 'installed-connectors-page' ? this.instances() : this.connectors();
      if (this.selectedConnectorCategory() === ALL_CATEGORY) {
        return connectors;
      }
      return connectors.filter(
        connector => connector.category === this.selectedConnectorCategory().type
      );
    });

    this.filteredConnectors = ko.pureComputed(() => {
      if (!this.connectorsFilter()) {
        return this.selectedConnectors();
      }

      const lowerQuery = this.connectorsFilter().toLowerCase();
      const filteredConnectors = [];
      const categoryIndex = this.categories().reduce((index, category) => {
        index[category.type] = category.category_name;
        return index;
      }, {});

      this.selectedConnectors().forEach(connector => {
        const filteredConnector = {
          category: connector.category,
          category_name: categoryIndex[connector.category],
          values: connector.values.filter(
            val => val.nice_name.toLowerCase().indexOf(lowerQuery) !== -1
          )
        };
        if (filteredConnector.values.length > 0) {
          filteredConnectors.push(filteredConnector);
        }
      });
      return filteredConnectors;
    });

    this.fetchConnectors();
  }

  addNewConnector() {
    this.section('add-connector-page');
  }

  fetchConnectors() {
    this.fetchConnectorTypes(); // TODO: might be cleaner to chain below
    simpleGet(
      '/desktop/connectors/api/instances/',
      {},
      {
        successCallback: data => {
          this.instances(data.connectors);
        }
      }
    );
  }

  editConnector(data) {
    if (this.section() === 'installed-connectors-page') {
      this.instance(data);
    } else {
      this.newConnector(data.dialect, data.interface);
    }
    this.section('connector-page');
  }

  newConnector(dialect, con_interface) {
    simpleGet(
      '/desktop/connectors/api/instance/new/' + dialect + '/' + con_interface,
      {},
      {
        successCallback: data => {
          this.instance(ko.mapping.fromJS(data.connector));
        }
      }
    );
  }

  fetchConnector(id) {
    simpleGet(
      '/desktop/connectors/api/instance/get/' + id,
      {},
      {
        successCallback: data => {
          this.instance(ko.mapping.fromJS(data.connector));
        }
      }
    );
  }

  deleteConnector(connector) {
    simplePost(
      '/desktop/connectors/api/instance/delete',
      {
        connector: ko.mapping.toJSON(connector)
      },
      {
        successCallback: data => {
          this.section('installed-connectors-page');
          this.fetchConnectors();
          huePubSub.publish(REFRESH_CONFIG_TOPIC);
        }
      }
    );
  }

  updateConnector(connector) {
    simplePost(
      '/desktop/connectors/api/instance/update',
      {
        connector: ko.mapping.toJSON(connector)
      },
      {
        successCallback: data => {
          connector.id = data.connector.id;
          this.section('installed-connectors-page');
          this.fetchConnectors();
          huePubSub.publish(REFRESH_CONFIG_TOPIC);
        }
      }
    );
  }

  fetchConnectorTypes() {
    simpleGet(
      '/desktop/connectors/api/types/',
      {},
      {
        successCallback: data => {
          this.connectors(data.connectors);
          this.categories(data.categories);
        }
      }
    );
  }

  testConnector(connector) {
    this.testConnectionExecuted(false);
    this.testConnectionExecuting(true);
    this.testConnectionErrors('');

    simplePost(
      '/desktop/connectors/api/instance/test',
      {
        connector: ko.mapping.toJSON(connector)
      },
      {
        successCallback: data => {
          this.testConnectionExecuted(true);
          this.testConnectionExecuting(false);
          this.testConnectionErrors(data.warnings);
        }
      }
    );
  }
}

componentUtils.registerComponent(NAME, ConnectorsConfig, TEMPLATE);
