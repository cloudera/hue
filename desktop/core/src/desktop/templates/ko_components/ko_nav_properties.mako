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
from desktop.views import _ko
from django.utils.translation import ugettext as _
%>

<%def name="navProperties()">
  <script type="text/html" id="nav-properties-template">
     <!-- ko if: loading -->
     <div data-bind="hueSpinner: { spin: loading }"></div>
     <!-- /ko -->
     <!-- ko ifnot: loading -->
     <div class="hue-nav-properties" data-bind="foreach: properties">
       <div class="hue-nav-property"><div class="hue-nav-property-key" data-bind="text: key"></div><div class="hue-nav-property-value" data-bind="html: value"></div></div>
     </div>
     <!-- /ko -->
  </script>

  <script type="text/javascript">
    (function () {

      function NavProperty(key, value) {
        var self = this;
        self.key = key;
        self.value = value;
      }

      /**
       * @param {object} params
       * @param {DataCatalogEntry} [params.catalogEntry]
       *
       * @constructor
       */
      function NavProperties(params) {
        var self = this;

        self.hasErrors = ko.observable(false);
        self.loading = ko.observable(true);
        self.properties = ko.observableArray();

        self.catalogEntry = params.catalogEntry;

        self.loadProperties();
      }

      NavProperties.prototype.loadProperties = function () {
        var self = this;
        self.loading(true);
        self.hasErrors(false);

        ko.unwrap(self.catalogEntry).getNavigatorMeta().done(function (navigatorMeta) {
          var newProps = [];
          if (navigatorMeta.properties) {
            Object.keys(navigatorMeta.properties).forEach(function (key) {
              newProps.push(new NavProperty(key, navigatorMeta.properties[key]));
            });
            newProps.sort(function (a, b) {
              return a.key.localeCompare(b.key);
            })
          }
          self.properties(newProps);
        }).fail(function () {
          self.hasErrors(true);
        }).always(function () {
          self.loading(false);
        });
      };

      ko.components.register('nav-properties', {
        viewModel: NavProperties,
        template: { element: 'nav-properties-template' }
      });
    })();
  </script>
</%def>
