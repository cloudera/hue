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

import 'jquery/jquery.login';
import 'ext/bootstrap.2.3.2.min';
import Dropzone from 'dropzone';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
window.Dropzone = Dropzone;
window.hueAnalytics = hueAnalytics;
window.huePubSub = huePubSub;
import * as ko from 'knockout';
import 'ko/ko.init';
import { createApp } from 'vue';
import TrademarkBanner from 'vue/components/login/TrademarkBanner.vue';
import { createReactComponents } from './reactComponents/createRootElements';
import ksb from 'knockout-secure-binding';

var options = {
  attribute: "data-bind",        // default is "data-sbind", using "data-bind" to match regular Knockout bindings
  globals: window,               // makes global window object available to bindings
  bindings: ko.bindingHandlers,  // the Knockout binding handlers to use
  noVirtualElements: false       // allows the use of Knockout virtual elements
};
ko.bindingProvider.instance = new ksb(options); // Use the imported 'ksb' as the constructor
function ViewModel() {
  this.someProperty = ko.observable('Initial Value');
}

window.addEventListener('DOMContentLoaded', () => {
  // console.log("test")
  ko.applyBindings(new ViewModel());
  createReactComponents('.login-page');
  createApp({
    components: {
      'trademark-banner': TrademarkBanner
    },
    data: () => ({})
  }).mount('#trademark');
});
