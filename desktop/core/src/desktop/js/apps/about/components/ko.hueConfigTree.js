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

import apiHelper from 'api/apiHelper';
import componentUtils from 'ko/components/componentUtils';
import I18n from 'utils/i18n';
import DisposableComponent from 'ko/components/DisposableComponent';

export const NAME = 'hue-config-tree';

// prettier-ignore
const TEMPLATE = `
<script id="config-values-template" type="text/html">
  <tr>
    <th>
    <!-- ko if: config.is_anonymous -->
      <i>(${ I18n('default section') })</i>
    <!-- /ko -->
    <!-- ko ifnot: config.is_anonymous -->
      <span data-bind="text: config.key"></span>
    <!-- /ko -->
    </th>
    <td data-bind="css: { 'border-top': depth === 1 ? '0' : null }">
      <!-- ko if: typeof config.values !== 'undefined' -->
        <!-- ko if: config.help || !config.values.length -->
        <i data-bind="text: config.help || '${ I18n('No help available.') }'"></i>
        <!-- /ko -->
        <table class="table table-condensed recurse">
          <tbody>
            <!-- ko foreach: config.values -->
              <!-- ko template: { name: 'config-values-template', data: { config: $data, depth: $parent.depth + 1 } } --><!-- /ko -->
            <!-- /ko -->
          </tbody>
        </table>
        <!-- /ko -->
      <!-- ko if: typeof config.value !== 'undefined' -->
        <code data-bind="text: config.value"></code><br/>
        <i data-bind="text: config.help || '${ I18n('No help available.') }'"></i>
        <span class="muted">${ I18n('Default:') } <i data-bind="text: config.default"></i></span>
      <!-- /ko -->
    </td>
  </tr>
</script>

<div class="container-fluid">
  <!-- ko hueSpinner: { spin:  loading, center: true, size: 'large' } --><!-- /ko -->
  <!-- ko ifnot: loading -->
    <!-- ko if: errorMessage -->
      <div class="alert alert-error" style="margin: 20px" data-bind="text: errorMessage"></div>
    <!-- /ko -->
    <!-- ko ifnot: errorMessage -->
      <div class="row-fluid">
        <div class="card card-home">
          <div class="pull-right muted margin-top-30">
            ${ I18n('Configuration files located in') } <code style="color: #0B7FAD" data-bind="text: configDir"></code>
          </div>
          <h1 class="inline-block margin-top-20">
            ${ I18n('Sections') }
          </h1>
          <form class="form-inline" autocomplete="off">
            <input class="inline-autocomp-input" type="text" ${ window.PREVENT_AUTOFILL_INPUT_ATTRS } placeholder="${ I18n('Filter...') }" data-bind="textInput: filter, clearable: { value: filter }">
          </form>
          <div class="card-body clearfix">
            <div class="span2">
              <ul class="nav nav-pills nav-stacked" data-bind="foreach: filteredSections">
                <li data-bind="
                    css: { 'active': $data.key === $parent.selectedKey() },
                    click: function () { $parent.selectedKey($data.key) }
                  ">
                  <a href="javascript: void(0);" data-bind="text: key"></a>
                </li>
              </ul>
            </div>
            <div class="span10" data-bind="with: selectedConfig">
              <div class="tab-content">
                <div class="tab-pane active">
                  <!-- ko if: values.length -->
                  <table class="table table-condensed recurse">
                    <tbody data-bind="foreach: values">
                      <!-- ko template: { name: 'config-values-template', data: { config: $data, depth: 1 } } --><!-- /ko -->
                    </tbody>
                  </table>
                  <!-- /ko -->
                  <!-- ko ifnot: values.length -->
                    <i>${ I18n('Empty configuration section') }</i>
                  <!-- /ko -->
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="card card-home" style="margin-top: 50px">
          <h2 class="card-heading simple">${ I18n('Installed Applications') }</h2>
          <div class="card-body" data-bind="foreach: apps">
            <!-- ko if: has_ui -->
              <a href="javascript: void(0);" data-bind="hueLink: display_name"><span class="badge badge-info" data-bind="text: name"></span></a>
            <!-- /ko -->
            <!-- ko ifnot: has_ui -->
              <span class="badge" title="${ I18n('This app does not have a UI') }" data-bind="text: name"></span>
            <!-- /ko -->
          </div>
        </div>
      </div>
    <!-- /ko -->
  <!-- /ko -->
</div>
`;

const filterConfig = (config, lowerCaseFilter) => {
  if (
    (config.value && config.value.indexOf(lowerCaseFilter) !== -1) ||
    (!config.is_anonymous && config.key.indexOf(lowerCaseFilter) !== -1)
  ) {
    return config;
  }

  if (config.values) {
    const values = [];
    config.values.forEach(val => {
      const filtered = filterConfig(val, lowerCaseFilter);
      if (filtered) {
        values.push(filtered);
      }
    });
    if (values.length) {
      return {
        key: config.key,
        is_anonymous: config.is_anonymous,
        help: config.help,
        values: values
      };
    }
  }
};

class HueConfigTree extends DisposableComponent {
  constructor(params) {
    super();
    this.loading = ko.observable(true);

    this.filter = ko.observable().extend({ throttle: 500 });

    this.errorMessage = ko.observable();
    this.apps = ko.observableArray();
    this.config = ko.observableArray();
    this.configDir = ko.observable();
    this.selectedKey = ko.observable();

    this.filteredSections = ko.pureComputed(() => {
      if (!this.filter()) {
        return this.config();
      }
      const lowerCaseFilter = this.filter().toLowerCase();

      const foundConfigs = [];
      let selectedFound = false;
      this.config().forEach(config => {
        const filtered = filterConfig(config, lowerCaseFilter);
        if (filtered) {
          foundConfigs.push(filtered);
          if (this.selectedKey() && this.selectedKey() === filtered.key) {
            selectedFound = true;
          }
        }
      });

      if (!selectedFound) {
        if (foundConfigs.length) {
          this.selectedKey(foundConfigs[0].key);
        } else {
          this.selectedKey(undefined);
        }
      }

      return foundConfigs;
    });

    this.selectedConfig = ko.pureComputed(() =>
      this.filteredSections().find(section => section.key === this.selectedKey())
    );

    this.load();
  }

  async load() {
    this.loading(true);
    this.errorMessage(undefined);
    try {
      const response = await apiHelper.fetchHueConfigAsync();
      this.config(response.config);
      this.configDir(response.conf_dir);
      this.apps(response.apps);
      this.selectedKey(this.config().length ? this.config()[0].key : undefined);
    } catch (err) {
      this.errorMessage(err);
    }
    this.loading(false);
  }
}

componentUtils.registerComponent(NAME, HueConfigTree, TEMPLATE);
