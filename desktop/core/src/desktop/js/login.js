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

import 'regenerator-runtime/runtime';
import 'jquery/jquery.login';
import 'ext/bootstrap.2.3.2.min';
import Dropzone from 'dropzone';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';

window.Dropzone = Dropzone;
window.hueAnalytics = hueAnalytics;
window.huePubSub = huePubSub;

import { createApp } from 'vue';
import TrademarkBanner from 'vue/components/login/TrademarkBanner.vue';
import { createReactComponents } from './reactComponents/createRootElements';

window.addEventListener('DOMContentLoaded', () => {
  createReactComponents('.login-page');

  createApp({
    components: {
      'trademark-banner': TrademarkBanner
    },
    data: () => ({})
  }).mount('#trademark');
});
