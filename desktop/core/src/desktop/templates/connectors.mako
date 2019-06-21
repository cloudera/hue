## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<%!
from django.utils.translation import ugettext as _

from desktop import conf
from desktop.views import commonheader, commonfooter
%>

<%
MAIN_SCROLLABLE = "'.page-content'"
if conf.CUSTOM.BANNER_TOP_HTML.get():
  TOP_SNAP = "78px"
else:
  TOP_SNAP = "50px"
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="about_layout.mako" />


<script type="text/javascript">
  (function () {
    var ConnectorsViewModel = function () {
      var self = this;

      self.apiHelper = window.apiHelper;

      self.section = ko.observable('installed-connectors-page');
      self.categories = ko.observableArray();
      self.selectedConnectorCategory = ko.observable('All');
      self.connectorsFilter = ko.observable();

      self.instances = ko.observableArray(); // Saved connectors
      self.instance = ko.observable();

      self.connectors = ko.observableArray(); // Connector forms
      self.connector = ko.observable();

      self.selectedConnectors = ko.pureComputed(function () {
        const connectors = self.section() == 'installed-connectors-page' ? self.instances() : self.connectors();
        return connectors.filter(function (connector) {
          return self.selectedConnectorCategory() == 'All' || connector.category == self.selectedConnectorCategory();
        });
      });
      self.filteredConnectors = ko.pureComputed(function () {
        var connectors = self.selectedConnectors();

        if (self.connectorsFilter()) {
          var lowerQuery = self.connectorsFilter().toLowerCase();
          var filteredConnectors = []
          connectors.forEach(function (connector) {
            var _connector = {"category": connector.category, "category_name": $.grep(categories, function(cat) { return cat.type == connector.category})[0].category_name, "values": []};
            _connector.values = connector.values.filter(function (subMetricKey) {
              return subMetricKey.name.toLowerCase().indexOf(lowerQuery) !== -1;
            });
            if (_connector.values.length > 0) {
              filteredConnectors.push(_connector);
            }
          });
          connectors = filteredConnectors;
        }

        return connectors;
      });

      self.addNewConnector = function () {
        self.section('add-connector-page');
      };

      self.fetchConnectors = function () {
        self.fetchConnectorTypes(); // TODO: might be cleaner to chain below
        self.apiHelper.simpleGet('/desktop/connectors/api/instances/', {}, {successCallback: function (data) {
          self.instances(data.connectors);
        }});
      };
      self.editConnector = function (data) {
        if (self.section() == 'installed-connectors-page') {
          self.instance(data);
        } else {
          self.newConnector(data.type);
        }
        self.section('connector-page');
      };

      self.newConnector = function (type) {
        self.apiHelper.simpleGet('/desktop/connectors/api/instance/new/' + type, {}, {successCallback: function (data) {
          self.instance(ko.mapping.fromJS(data.connector));
        }});
      };
      self.fetchConnector = function (id) {
        self.apiHelper.simpleGet('/desktop/connectors/api/instance/get/' + id, {}, {successCallback: function (data) {
          self.instance(ko.mapping.fromJS(data.connector));
        }});
      };
      self.deleteConnector = function (connector) {
        self.apiHelper.simplePost('/desktop/connectors/api/instance/delete', {'connector': ko.mapping.toJSON(connector)}, {successCallback: function (data) {
          self.section('installed-connectors-page');
          self.fetchConnectors();
          huePubSub.publish('cluster.config.refresh.config');
        }});
      };
      self.updateConnector = function (connector) {
        self.apiHelper.simplePost('/desktop/connectors/api/instance/update', {'connector': ko.mapping.toJSON(connector)}, {successCallback: function (data) {
          connector.id = data.connector.id;
          self.section('installed-connectors-page');
          self.fetchConnectors();
          huePubSub.publish('cluster.config.refresh.config');
        }});
      };
      self.fetchConnectorTypes = function () {
        self.apiHelper.simpleGet('/desktop/connectors/api/types/', {}, {successCallback: function (data) {
          self.connectors(data.connectors);
          self.categories(data.categories);
        }});
      };
    }

    $(document).ready(function () {
      var viewModel = new ConnectorsViewModel();
      ko.applyBindings(viewModel, $('#connectorsComponents')[0]);
    });
  })();
</script>


${ layout.menubar(section='connectors') }


<div id="connectorsComponents" class="container-fluid">

  <a href="javascript:void(0)" data-bind="click: function() { selectedConnectorCategory('All'); section('installed-connectors-page'); }">
    ${ _('Connectors') }
  </a>

  <!-- ko if: section() == 'installed-connectors-page' -->
    <div data-bind="template: { name: 'installed-connectors-page' }"></div>
  <!-- /ko -->

  <!-- ko if: section() == 'add-connector-page' -->
    <div data-bind="template: { name: 'add-connector-page' }"></div>
  <!-- /ko -->

  <!-- ko if: section() == 'connector-page' -->
    <div data-bind="template: { name: 'connector-page', data: $root.instance() }"></div>
  <!-- /ko -->
</div>


<script type="text/html" id="installed-connectors-page">
  <div class="row-fluid">
    <a href="javascript:void(0)" data-bind="click: $root.addNewConnector">
      + Connector
    </a>
  </div>

  <div data-bind="template: { name: 'connectors-page', data: $root.instances() }"></div>

</script>


<script type="text/html" id="add-connector-page">
  <div class="row-fluid">
    Add a Connector
  </div>

  <div data-bind="template: { name: 'connectors-page', data: $root.connectors() }"></div>

</script>


<script type="text/html" id="connectors-page">
  <div class="card card-small margin-top-10">

    <div class="card-body clearfix">
      <div class="span2">
        <div data-bind="dockable: { scrollable: ${ MAIN_SCROLLABLE }, jumpCorrection: 0, topSnap: '${ TOP_SNAP }', triggerAdjust: 0 }">
          <ul class="nav nav-pills nav-stacked">
            <li data-bind="css: { 'active': $root.selectedConnectorCategory() === 'All' }">
              <a href="javascript:void(0)" data-bind="text: 'All', click: function(){ $root.selectedConnectorCategory('All') }"></a>
            </li>
            <!-- ko foreach: $root.categories -->
            <li data-bind="css: { 'active': $root.selectedConnectorCategory() === type }">
              <a href="javascript:void(0)" data-bind="text: name, click: function(){ $root.selectedConnectorCategory(type) }"></a>
            </li>
            <!-- /ko -->
          </ul>
        </div>
      </div>

      <div class="span10">
        <div data-bind="dockable: { scrollable: ${ MAIN_SCROLLABLE }, jumpCorrection: 0, topSnap: '${ TOP_SNAP }', triggerAdjust: 0 }">
          <span class="pull-right">
            <a href="http://gethue.com" target="_blank">
              <i class="fa fa-question-circle"></i> ${ _('Help') }
            </a>
          </span>
          <input type="text" data-bind="clearable: $root.connectorsFilter, valueUpdate: 'afterkeydown'"
              class="input-xlarge pull-right margin-bottom-10" placeholder="${ _('Filter...') }">
        </div>

        <div class="margin-top-10">
          <div data-bind="foreach: $root.filteredConnectors()">
            <h4 data-bind="text: category_name"></h4>
            <table class="table table-condensed">
              <thead>
                <tr>
                  <th width="30%">${ _('Name') }</th>
                  <th>${ _('Description') }</th>
                </tr>
              </thead>
              <!-- ko if: $data.values.length > 0 -->
              <tbody data-bind="foreach: values">
                <tr data-bind="click: $root.editConnector">
                  <td data-bind="text: name"></td>
                  <td data-bind="text: description"></td>
                </tr>
              </tbody>
              <!-- /ko -->
              <!-- ko ifnot: $data.values.length > 0 -->
              <tfoot>
                <tr>
                  <td colspan="2">
                    ${ _('No connectors') }
                    <!-- ko if: $root.section() == 'installed-connectors-page' -->
                      <a href="javascript:void(0)" data-bind="click: function() { $root.selectedConnectorCategory($data.category); $root.addNewConnector(); }">
                        ${ _('Add one ?') }
                      </a>
                    <!-- /ko -->
                  </td>
                </tr>
              </tfoot>
              <!-- /ko -->
            </table>
          </div>

          <!-- ko if: $root.filteredConnectors().length == 0 -->
          <table class="table table-condensed">
            <thead>
              <tr>
                <th width="30%">${ _('Name') }</th>
                <th>${ _('Instances') }</th>
              </tr>
            </thead>
            <tfoot>
              <tr>
                <td colspan="2">
                  ${ _('No connectors') }
                  <!-- ko if: $root.section() == 'installed-connectors-page' -->
                    <a href="javascript:void(0)" data-bind="click: function() { $root.selectedConnectorCategory($data.category); $root.addNewConnector(); }">
                      ${ _('Add one ?') }
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
    <input data-bind="value: name">
    <!-- ko if: typeof id != 'undefined' -->
      <!-- ko if: id -->
        (<span data-bind="text: connector_name"></span>)
        <a href="javascript:void(0)" data-bind="click: $root.updateConnector">
          ${ _('Update') }
        </a>
        <a href="javascript:void(0)" data-bind="click: $root.deleteConnector">
          ${ _('Delete') }
        </a>
      <!-- /ko -->
      <!-- ko ifnot: id -->
        <a href="javascript:void(0)" data-bind="click: $root.updateConnector">
          ${ _('Save') }
        </a>
        <a href="javascript:void(0)" data-bind="click: function() { $root.section('add-connector-page'); }">
          ${ _('Cancel') }
        </a>
      <!-- /ko -->
    <!-- /ko -->
    <a href="javascript:void(0)">
      ${ _('Test connection') }
    </a>
    <table class="table table-condensed">
      <thead>
        <tr>
          <th width="30%">${ _('Name') }</th>
          <th>${ _('Value') }</th>
        </tr>
      </thead>
      <tbody data-bind="foreach: settings">
        <tr>
          <td data-bind="text: name"></td>
          <td><input data-bind="value: value"></td>
        </tr>
      </tbody>
    </table>
  </div>
</script>
