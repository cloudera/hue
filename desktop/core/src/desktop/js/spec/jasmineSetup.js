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
import ko from 'knockout';

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

export const koSetup = () => {
  let originalLoadTemplate;
  let wrapper;

  beforeEach(() => {
    originalLoadTemplate = ko.components.defaultLoader.loadTemplate;
    ko.components.defaultLoader.loadTemplate = (name, templateConfig, callback) => {
      const div = window.document.createElement('div');
      div.innerHTML = templateConfig;
      callback(div.children);
    };

    wrapper = window.document.createElement('div');
    wrapper.classList.add('component-wrapper');
    window.document.querySelector('body').appendChild(wrapper);
  });

  afterEach(() => {
    ko.components.defaultLoader.loadTemplate = originalLoadTemplate;
    wrapper.parentNode.removeChild(wrapper);
    ko.cleanNode(wrapper);
    expect(window.document.querySelectorAll('[data-test]').length).toEqual(0);
  });

  return {
    renderComponent: async (name, data) =>
      new Promise(resolve => {
        const element = window.document.createElement('div');
        element.setAttribute('data-bind', `component: { name: "${name}", params: $data }`);
        wrapper.appendChild(element);
        ko.applyBindings(data, wrapper);
        window.setTimeout(() => {
          resolve(wrapper);
        }, 0);
      }),

    renderKo: async (html, viewModel) =>
      new Promise(resolve => {
        wrapper.innerHTML = html;
        ko.applyBindings(viewModel, wrapper);
        window.setTimeout(() => {
          resolve(wrapper);
        }, 0);
      }),

    waitForKoUpdate: async () => {
      return new Promise(resolve => {
        window.setTimeout(resolve, 0);
      });
    }
  };
};
