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

import $ from 'jquery';
import * as ko from 'knockout';

import apps from 'ko/components/appSwitcher/apps.v2';
import componentUtils from 'ko/components/componentUtils';
import { getAltusBaseUrl, getMowBaseUrl } from 'ko/components/appSwitcher/environment';

const TEMPLATE = `
  <div class="hue-sidebar-header">
    <a class="hue-app-switcher-trigger" data-bind="toggle: open"><svg class="show"><use xlink:href="#hi-app-picker"></use></svg></a>
    <div class="hue-app-switcher-logo"><svg><use xlink:href="#hi-sidebar-logo"></use></svg></div>
  </div>

  <div class="hue-app-switcher" data-bind="css: { 'open': open }">
    <div class="app-switcher-header">
      <svg class="show"><use xlink:href="#hi-cdp-logo"></use></svg>
      <a href="javascript: void(0);" class="close" data-bind="toggle: open">&times;</a></form>
    </div>

    <ul data-bind="foreach: links">
      <li><a data-bind="attr: { href: url }"><i data-bind="html: svg"></i><span data-bind="text: label"></span></a></li>
    </ul>
  </div>
`;

const getUrl = (baseUrl, path) => {
  if (baseUrl === 'mow') {
    return getMowBaseUrl() + path;
  } else if (baseUrl === 'altus') {
    return getAltusBaseUrl() + path;
  }
  console.warn('Could not find baseUrl for "' + baseUrl + '", using relative link instead.');
  return path;
};

const AppSwitcher = function AppSwitcher() {
  this.links = apps.map(app => {
    return {
      label: app.displayName,
      svg: app.logo,
      url: getUrl(app.baseUrl, app.path)
    };
  });

  this.open = ko.observable(false);

  const closeOnClickOutside = event => {
    if (!this.open()) {
      return;
    }
    if (
      $.contains(document, event.target) &&
      !$.contains($('.hue-app-switcher')[0], event.target)
    ) {
      this.open(false);
    }
  };

  this.open.subscribe(newVal => {
    if (newVal) {
      window.setTimeout(() => {
        $(document).on('click', closeOnClickOutside);
      }, 0);
    } else {
      $(document).off('click', closeOnClickOutside);
    }
  });
};

componentUtils.registerComponent('hue-app-switcher', AppSwitcher, TEMPLATE);
