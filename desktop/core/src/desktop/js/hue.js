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

var locale = 'en-US';

import $ from 'jquery';
import _ from 'lodash';
import filesize from 'filesize';
import ko from 'knockout';
import komapping from 'knockout.mapping';
import page from 'page';
import hueUtils from 'utils/hueUtils';
import hueAnalytics from 'utils/hueAnalytics';
import hueDebug from 'utils/hueDebug';
import huePubSub from 'utils/huePubSub';
import hueDrop from 'utils/hueDrop';
import localforage from 'localforage';
import 'knockout-switch-case';
import 'ext/ko.editable.custom';

// TODO: Migrate away
window.$ = $;
window._ = _;
window.filesize = filesize;
window.jQuery = $;
window.ko = ko;
window.ko.mapping = komapping;
window.page = page;
window.hueUtils = hueUtils;
window.hueAnalytics = hueAnalytics;
window.hueDebug = hueDebug;
window.huePubSub = huePubSub;
window.hueDrop = hueDrop;
window.localforage = localforage;