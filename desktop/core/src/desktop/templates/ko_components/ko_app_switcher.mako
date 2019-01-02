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
from desktop import conf
from desktop.lib.i18n import smart_unicode

from django.utils.translation import ugettext as _
from desktop.views import _ko
%>

<%def name="appSwitcher()">

  <script type="text/html" id="hue-app-switcher-template">
    <ul class="cui-app-switcher nav navbar-nav">
      <li class="dropdown">
        <button class="btn btn-flat" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true" role="button">
          <i class="fa fa-th"></i>
        </button>

        <ul class="dropdown-menu pull-right" role="menu">
          <!-- ko foreach: links -->
          <li class="nav-item">
            <!-- ko if: $data.divider -->
            <div class="divider"></div>
            <!-- /ko -->
            <!-- ko ifnot: $data.divider -->
            <a role="button" class="nav-link" data-bind="attr: { href: link }">
              <span class="app-switcher-app-icon">
                <!-- ko if: $data.icon -->
                <i data-bind="attr: { class: icon }"></i>
                <!-- /ko -->
                <!-- ko if: $data.img -->
                <!-- ko template: 'app-switcher-icon-template' --><!-- /ko -->
                <!-- /ko -->
              </span>
              <span class="app-switcher-app-name" data-bind="text: label"></span>
            </a>
            <!-- /ko -->
          </li>
          <!-- /ko -->
        </ul>
      </li>
    </ul>
  </script>

  <script type="text/javascript">
    (function () {
      var apps = {
          hue: {
            label: 'Data Warehouse',
            icon: 'altus-icon altus-adb-query'
          },
          cdsw: {
            label: 'Data Science',
            icon:'altus-icon altus-ds'
          },
          dataFlow: {
            label: 'Data Engineering',
            icon:'altus-icon altus-workload'
          },
          navigator: {
            label: 'Data Stewart',
            icon: 'altus-icon altus-adb'
          },
          navopt: {
            label: 'Admin',
            icon: 'altus-icon altus-iam'
          }
      };

      var AppSwitcher = function AppSwitcher(params) {
        var self = this;

        self.links = ko.observableArray([]);

        var altusLinks = [{
            product: 'hue',
            link: 'https://sso.staging.aem.cloudera.com'
          },
          {
            product: 'cdsw',
            link: 'https://sso.staging.aem.cloudera.com'
          },
          {
            product: 'dataFlow',
            link: 'https://sso.staging.aem.cloudera.com'
          },
          {
            product: 'navigator',
            link: 'https://sso.staging.aem.cloudera.com'
          },
          {
            product: 'navopt',
            link: 'https://sso.staging.aem.cloudera.com'
          }
        ];

        var onPremLinks = [{
            product: 'cdsw',
            link: '/'
          },
          {
            divider: true
          }
          , {
            product: 'cm',
            link: '/'
          }, {
            product: 'navigator',
            link: '/'
          }
        ];

        var applyLinks = function (links) {
          var newLinks = [];
          links.forEach(function (link) {
            if (link.product) {
              var lookup = apps[link.product];
              if (lookup) {
                lookup.link = link.link;
                newLinks.push(lookup);
              }
            } else {
              newLinks.push(link);
            }
          });
          self.links(newLinks);
        };

        params.onPrem.subscribe(function (newValue) {
          if (newValue) {
            applyLinks(onPremLinks);
          } else {
            applyLinks(altusLinks);
          }
        });

        applyLinks(altusLinks);
      };

      ko.components.register('hue-app-switcher', {
        viewModel: AppSwitcher,
        template: { element: 'hue-app-switcher-template' }
      });
    })();
  </script>

</%def>