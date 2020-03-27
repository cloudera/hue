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
import I18n from 'utils/i18n';
import DisposableComponent from 'ko/components/DisposableComponent';
import { simpleGet, simplePost } from 'api/apiUtils';
import huePubSub from 'utils/huePubSub';

export const NAME = 'connectors-config';

// prettier-ignore
const TEMPLATE = `
<script type="text/html" id="installed-connectors-page">
  <div class="row-fluid">
    <a href="javascript:void(0)" data-bind="click: addNewConnector">
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
  <div class="card card-small margin-top-10">

    <div class="card-body clearfix">
      <div class="span2">
        <div data-bind="dockable: { scrollable: ${ window.MAIN_SCROLLABLE }, jumpCorrection: 0, topSnap: '${ window.BANNER_TOP_HTML ? '78px' : '50px' }', triggerAdjust: 0 }">
          <ul class="nav nav-pills nav-stacked">
            <li data-bind="css: { 'active': $parent.selectedConnectorCategory() === 'All' }">
              <a href="javascript:void(0)" data-bind="text: 'All', click: function() { $parent.selectedConnectorCategory('All') }"></a>
            </li>
            <!-- ko foreach: $parent.categories -->
            <li data-bind="css: { 'active': $parents[1].selectedConnectorCategory() === type }">
              <a href="javascript:void(0)" data-bind="text: name, click: function(){ $parents[1].selectedConnectorCategory(type) }"></a>
            </li>
            <!-- /ko -->
          </ul>
        </div
      </div>

      <div class="span10">
        <div data-bind="dockable: { scrollable: ${ window.MAIN_SCROLLABLE }, jumpCorrection: 0, topSnap: '${ window.BANNER_TOP_HTML ? '78px' : '50px' }', triggerAdjust: 0 }">
          <span class="pull-right">
            <a href="https://docs.gethue.com/administrator/configuration/" target="_blank">
              <i class="fa fa-question-circle"></i> ${ I18n('Help') }
            </a>
          </span>
          <input type="text" data-bind="clearable: $parent.connectorsFilter, valueUpdate: 'afterkeydown'"
              class="input-xlarge pull-right margin-bottom-10" placeholder="${ I18n('Filter...') }">
        </div>

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
                <tr data-bind="click: $parents[1].editConnector">
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
                    <!-- ko if: $parent.section() == 'installed-connectors-page' -->
                      <a href="javascript:void(0)" data-bind="click: function() { $parent.selectedConnectorCategory($data.category); $parent.addNewConnector(); }">
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
        <a href="javascript:void(0)" data-bind="click: $parent.updateConnector">
          ${ I18n('Update') }
        </a>
        <a href="javascript:void(0)" data-bind="click: $parent.deleteConnector">
          ${ I18n('Delete') }
        </a>
      <!-- /ko -->
      <!-- ko ifnot: id -->
        <a href="javascript:void(0)" data-bind="click: $parent.updateConnector">
          ${ I18n('Save') }
        </a>
        <a href="javascript:void(0)" data-bind="click: function() { $parent.section('add-connector-page'); }">
          ${ I18n('Cancel') }
        </a>
      <!-- /ko -->
    <!-- /ko -->
    <a href="javascript:void(0)" data-bind="click: $parent.testConnector">
      ${ I18n('Test connection') }
    </a>
    <span>
      <i class="fa fa-question" data-bind="visible: !$parent.testConnectionExecuted()"></i>
      <i class="fa fa-check" data-bind="visible: $parent.testConnectionExecuted() && $parent.testConnectionErrors().length"></i>
      <i class="fa fa-exclamation" data-bind="visible: $parent.testConnectionExecuted() && !$parent.testConnectionErrors().length"></i>
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
  <a href="javascript:void(0)" data-bind="click: function() { selectedConnectorCategory('All'); section('installed-connectors-page'); }">
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

class ConnectorsConfig extends DisposableComponent {
  constructor() {
    super();
    this.section = ko.observable('installed-connectors-page');
    this.categories = ko.observableArray();
    this.selectedConnectorCategory = ko.observable('All');
    this.connectorsFilter = ko.observable();

    this.testConnectionExecuted = ko.observable(false);
    this.testConnectionErrors = ko.observable('');

    // Handle two types of objects are being listed: connector instances and types
    this.instances = ko.observableArray(); // Connector instances (e.g. connector to a MySql DB on a certain host)
    this.instance = ko.observable();

    this.connectors = ko.observableArray(); // Connector types (e.g. mysql dialect)
    this.connector = ko.observable();

    this.selectedConnectors = ko.pureComputed(() => {
      const connectors =
        this.section() === 'installed-connectors-page' ? this.instances() : this.connectors();
      if (this.selectedConnectorCategory() === 'All') {
        return connectors;
      }
      return connectors.filter(
        connector => connector.category === this.selectedConnectorCategory()
      );
    });

    this.filteredConnectors = ko.pureComputed(() => {
      if (!this.connectorsFilter()) {
        return this.selectedConnectors();
      }

      const lowerQuery = this.connectorsFilter().toLowerCase();
      const filteredConnectors = [];
      this.selectedConnectors().forEach(connector => {
        const filteredConnector = {
          category: connector.category,
          category_name: this.categories().find(cat => cat.type === connector.category)
            .category_name,
          values: []
        };
        filteredConnector.values = connector.values.filter(
          subMetricKey => subMetricKey.name.toLowerCase().indexOf(lowerQuery) !== -1
        );
        if (filteredConnector.values.length > 0) {
          filteredConnectors.push(filteredConnector);
        }
      });
      return filteredConnectors;
    });

    this.addNewConnector = () => {
      this.testConnectionExecuted(false);
      this.testConnectionErrors('');
      this.section('add-connector-page');
    };

    this.fetchConnectors = () => {
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
    };

    this.editConnector = data => {
      if (this.section() === 'installed-connectors-page') {
        this.instance(data);
      } else {
        this.newConnector(data.dialect);
      }
      this.section('connector-page');
    };

    this.newConnector = dialect => {
      simpleGet(
        '/desktop/connectors/api/instance/new/' + dialect,
        {},
        {
          successCallback: data => {
            this.instance(ko.mapping.fromJS(data.connector));
          }
        }
      );
    };

    this.fetchConnector = id => {
      simpleGet(
        '/desktop/connectors/api/instance/get/' + id,
        {},
        {
          successCallback: data => {
            this.instance(ko.mapping.fromJS(data.connector));
          }
        }
      );
    };

    this.deleteConnector = connector => {
      simplePost(
        '/desktop/connectors/api/instance/delete',
        {
          connector: ko.mapping.toJSON(connector)
        },
        {
          successCallback: data => {
            this.section('installed-connectors-page');
            this.fetchConnectors();
            huePubSub.publish('cluster.config.refresh.config');
          }
        }
      );
    };

    this.updateConnector = connector => {
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
            huePubSub.publish('cluster.config.refresh.config');
          }
        }
      );
    };

    this.fetchConnectorTypes = () => {
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
    };

    this.testConnector = connector => {
      this.testConnectionExecuted(false);
      this.testConnectionErrors('');

      simplePost(
        '/desktop/connectors/api/instance/test',
        {
          connector: ko.mapping.toJSON(connector)
        },
        {
          successCallback: data => {
            this.testConnectionExecuted(true);
            this.testConnectionErrors(data.warnings);
          }
        }
      );
    };
  }
}

componentUtils.registerComponent(NAME, ConnectorsConfig, TEMPLATE);
