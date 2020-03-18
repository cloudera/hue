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
    renderComponent: async (name, data, instantTimeout) =>
      new Promise((resolve, reject) => {
        const element = window.document.createElement('div');
        element.setAttribute(
          'data-bind',
          `descendantsComplete: descendantsComplete, component: { name: "${name}", params: params }`
        );
        wrapper.appendChild(element);

        try {
          ko.components.get(name, comp => {
            if (comp.createViewModel) {
              const origSetTimeout = window.setTimeout;
              if (instantTimeout) {
                window.setTimeout = cb => cb();
                comp.createViewModel(data, { element: element });
                window.setTimeout = origSetTimeout;
              } else {
                comp.createViewModel(data, { element: element });
              }

              ko.applyBindings(
                {
                  descendantsComplete: () => resolve(wrapper),
                  params: data
                },
                wrapper
              );
            } else {
              reject('no createViewModel function found on component ' + name);
            }
          });
        } catch (e) {
          reject(e);
        }
      }),

    renderKo: async (html, viewModel) =>
      new Promise(resolve => {
        const setupContainer = window.document.createElement('div');
        setupContainer.setAttribute(
          'data-bind',
          '{ descendantsComplete: descendantsComplete, with: model }'
        );

        const container = window.document.createElement('div');
        container.innerHTML = html;
        setupContainer.appendChild(container);

        const data = {
          model: viewModel,
          descendantsComplete: () => resolve(container)
        };

        ko.applyBindings(data, setupContainer);
      }),

    waitForKoUpdate: async () =>
      new Promise(resolve => {
        window.setTimeout(resolve, 0);
      })
  };
};

export const waitForObservableChange = async observable =>
  new Promise(resolve => {
    const sub = observable.subscribe(() => {
      sub.dispose();
      resolve();
    });
  });

export const simulateInput = (element, text) => {
  element.value = text;
  element.dispatchEvent(new Event('change'));
};
