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

  from desktop.views import commonheader, commonfooter, _ko
  from desktop import conf
%>

<div id="catalogComponents" class="main-content">
  <div class="vertical-full container-fluid">
    <div class="vertical-full row-fluid panel-container">
      <div class="content-panel home-container">
        <div id="catalogComponents">
          <input data-bind="value: query"/>
          <a class="btn" data-bind="click: search">Search</a>
        </div>

        <div class="row-fluid">
          <div class="span2">
            Facets

            <!-- ko foreach: $root.resultFacets() -->
              <div data-bind="text: name"></div>
              <ul>
                <!-- ko foreach: values -->
                  <li>
                    <span data-bind="text: name"></span>
                    <span data-bind="text: value"></span>
                  </li>
                <!-- /ko -->
              </ul>
            <!-- /ko -->
          </div>
          <div class="span10">
            Results

            <!-- ko foreach: $root.resultResults() -->
              <div>
                <i class="fa fa-info"></i>
                <span data-bind="text: type"></span>
                <span data-bind="text: hue_name"></span>
                <span data-bind="text: description"></span>
              </div>
            <!-- /ko -->
          </div>
        </div>

      </div>
    </div>
  </div>
</div>

<script type="text/javascript">

  var CatalogViewModel = (function () {

    var CatalogViewModel = function () {
      var self = this;
      self.apiHelper = window.apiHelper;

      self.query = ko.observable("");

      self.result = ko.observable("");

      self.resultFacets = ko.pureComputed(function() {
        var facets = [];
        if (self.result()) {
          $.each(self.result().facets, function(key, values) {
            var facetValues = []
            $.each(values, function(key, value) {
              facetValues.push({name: key, value: value});
            });
            facets.push({name: key, values: facetValues});
          });
        }
        return facets;
      });
      self.resultResults = ko.pureComputed(function() {
        return self.result() ? self.result().results : [];
      });
    };

    CatalogViewModel.prototype.search = function () {
      var self = this;
      self.apiHelper.fetchNavEntitiesInteractive({
        query: self.query(),
        facets: ['type', 'owner', 'tags', 'lastModified']
      }).done(function (response) {
        self.result(ko.mapping.fromJS(response));
      }).fail(function (errorResponse) {
        console.log(errorResponse);
      })
    };

    return CatalogViewModel;
  })();

  (function () {
    $(document).ready(function () {
      ko.applyBindings(new CatalogViewModel(), $('#catalogComponents')[0]);
    });
  })();
</script>