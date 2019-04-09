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

      self.section = ko.observable('connectors-page');

      self.instances = ko.observableArray();
      self.instance = ko.observable();

      self.connectors = ko.observableArray();
      self.selectedConnectorCategory = ko.observable('All');
      self.connectorsFilter = ko.observable();
      self.connector = ko.observable();

      self.selectedConnectors = ko.pureComputed(function () {
        return self.connectors().filter(function (connector) {
          return self.selectedConnectorCategory() == 'All' || connector.category == self.selectedConnectorCategory();
        });
      });
      self.filteredConnectors = ko.pureComputed(function () {
        var connectors = self.selectedConnectors();

        if (self.connectorsFilter()) {
          var lowerQuery = self.connectorsFilter().toLowerCase();
          var filteredConnectors = []
          connectors.forEach(function (connectors) {
            var _connectors = {"category": connectors.category, "values": []};
            _connectors.values = connectors.values.filter(function (subMetricKey) {
              return subMetricKey.name.toLowerCase().indexOf(lowerQuery) !== -1;
            });
            if (_connectors.values.length > 0) {
              filteredConnectors.push(_connectors);
            }
          });
          connectors = filteredConnectors;
        }

        return connectors;
      });

      self.addNewConnector = function () {
        self.fetchConnectorTypes();
        self.section('add-connector-page');
      };

      self.fetchConnectors = function () {
        self.apiHelper.simpleGet('/desktop/connectors/api/instances/', {}, {successCallback: function (data) {
          self.instances(data.connectors);
        }});
      };
      self.fetchConnector = function (name) {
        self.apiHelper.simpleGet('/desktop/connectors/api/instance/get/' + name, {successCallback: function (data) {
          self.instance(data.connector);
        }});
      };
      self.deleteConnector = function (connector) {
        self.apiHelper.simplePost('/desktop/connectors/api/instance/delete', {'connector': ko.mapping.toJSON(connector)}, {successCallback: function (data) {
          self.section('connectors-page');
          self.fetchConnectors();
        }});
      };
      self.updateConnector = function (connector) {
        self.apiHelper.simplePost('/desktop/connectors/api/instance/update', {'connector': ko.mapping.toJSON(connector)}, {successCallback: function (data) {
          console.log('Success');
        }});
      };
      self.fetchConnectorTypes = function () {
        self.apiHelper.simpleGet('/desktop/connectors/api/types/', {}, {successCallback: function (data) {
          self.connectors(data.connectors);
        }});
      };
    }

    $(document).ready(function () {
      var viewModel = new ConnectorsViewModel();
      ko.applyBindings(viewModel, $('#connectorsComponents')[0]);
    });
  })();
</script>


${layout.menubar(section='connectors')}


<div id="connectorsComponents" class="container-fluid">

  <a href="javascript:void(0)" data-bind="click: function() { section('connectors-page'); }">
    Connectors
  </a>

  <!-- ko if: section() == 'connectors-page' -->
    <div data-bind="template: { name: 'connectors-page', data: $root.instances() }"></div>
  <!-- /ko -->

  <!-- ko if: section() == 'connector-page' -->
    <div data-bind="template: { name: 'connector-page', data: $root.instance() }"></div>
  <!-- /ko -->

  <!-- ko if: section() == 'add-connector-page' -->
    <div data-bind="template: { name: 'add-connector-page' }"></div>
  <!-- /ko -->

</div>


<script type="text/html" id="connectors-page">
  <div class="row-fluid">
    <a href="javascript:void(0)" data-bind="click: $root.addNewConnector">
      + Connector
    </a>
  </div>

  <div class="margin-top-10">
    <table class="table table-condensed">
      <thead>
        <tr>
          <th width="30%">${ _('Name') }</th>
          <th>${ _('') }</th>
        </tr>
      </thead>
      <tbody data-bind="foreach: $data">
        <tr data-bind="click: function() { $root.instance($data); $root.section('connector-page'); }">
          <td data-bind="text: name"></td>
          <td data-bind="text: ''"></td>
        </tr>
      </tbody>
    </table>
    <!-- ko ifnot: $data -->
      ${ _('There are no connectors configured.') }
      <a href="javascript:void(0)" data-bind="click: $root.addNewConnector">
        ${ _('Add one ?') }
      </a>
    <!-- /ko -->
</script>


<script type="text/html" id="connector-page">
  <div class="row-fluid">
    <span data-bind="text: name"></span>
    <a href="javascript:void(0)" data-bind="click: $root.deleteConnector">
      ${ _('Delete') }
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
          <td data-bind="text: value"></td>
        </tr>
      </tbody>
    </table>
  </div>
</script>


<script type="text/html" id="add-connector-page">
  <div class="card card-small margin-top-10">
    ##<div data-bind="dockable: { scrollable: ${ MAIN_SCROLLABLE }, jumpCorrection: 0, topSnap: '${ TOP_SNAP }', triggerAdjust: 0 }">

    <div class="card-body clearfix">
      <div class="span2">
        <ul class="nav nav-pills nav-stacked">
          <li data-bind="css: { 'active': $root.selectedConnectorCategory() === 'All' }">
            <a href="javascript:void(0)" data-bind="text: 'All', click: function(){ $root.selectedConnectorCategory('All') }"></a>
          </li>
          <!-- ko foreach: connectors() -->
          <li data-bind="css: { 'active': $root.selectedConnectorCategory() === category }">
            <a href="javascript:void(0)" data-bind="text: category, click: function(){ $root.selectedConnectorCategory(category) }"></a>
          </li>
          <!-- /ko -->
        </ul>
      </div>

      <div class="span10">
          <span class="pull-right">
            <a href="http://gethue.com" target="_blank">
              <i class="fa fa-question-circle"></i> ${ _('Help') }
            </a>
          </span>

          <input type="text" data-bind="clearable: connectorsFilter, valueUpdate: 'afterkeydown'"
              class="input-xlarge pull-right margin-bottom-10" placeholder="${ _('Filter...') }">

          <div class="margin-top-10">
            <div data-bind="foreach: filteredConnectors()">
              <h4 data-bind="text: category"></h4>
              <table class="table table-condensed">
                <thead>
                  <tr>
                    <th width="30%">${ _('Name') }</th>
                    <th>${ _('Instances') }</th>
                  </tr>
                </thead>
                <!-- ko if: $data.values -->
                <tbody data-bind="foreach: values">
                  <tr data-bind="click: function() { $root.instance(name); }">
                    <td data-bind="text: name"></td>
                    <td data-bind="text: instances.length > 0 ? instances.length : ''"></td>
                  </tr>
                </tbody>
                <!-- /ko -->
                <!-- ko ifnot: $data.values -->
                <tfoot>
                  <tr>
                    <td colspan="2">${ _('There are no connectors matching your filter') }</td>
                  </tr>
                </tfoot>
                <!-- /ko -->
              </table>
            </div>

            <!-- ko if: filteredConnectors().length == 0 -->
            <table class="table table-condensed">
              <thead>
                <tr>
                  <th width="30%">${ _('Name') }</th>
                  <th>${ _('Instances') }</th>
                </tr>
              </thead>
              <tfoot>
                <tr>
                  <td colspan="2">${ _('There are no connectors matching your filter') }</td>
                </tr>
              </tfoot>
            </table>
            <!-- /ko -->
          </div>
        </div>
      </div>
    </div>
    ## </div>

  </div>
</script>
