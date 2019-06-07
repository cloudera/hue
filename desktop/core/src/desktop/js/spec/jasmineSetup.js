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

import JasmineCore from 'jasmine-core';
import { JSDOM } from 'jsdom';

const jsdom = new JSDOM('<!doctype html><html><body></body></html>', {
  url: 'https://www.gethue.com/hue',
  contentType: 'text/html',
  includeNodeLocations: true,
  storageQuota: 10000000
});

const { window } = jsdom;

global.document = window.document;
global.window = window;
global.self = global;
global.navigator = {
  userAgent: 'node.js'
};
global.localStorage = window.localStorage;
global.sessionStorage = window.sessionStorage;

global.getJasmineRequireObj = function() {
  return JasmineCore;
};
