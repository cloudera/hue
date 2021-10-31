// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { ComponentOptions, Component, createApp, h } from 'vue';
import wrapper, { WebComponentOptions } from './wrapper/index';

export interface HueComponentOptions<T extends Component> extends ComponentOptions<T> {
  hueBaseUrl?: string;
}

const isRegistered = (tag: string): boolean => !!window.customElements?.get(tag);

export const wrap = <T extends Component>(
  tag: string,
  component: { new (): T },
  options?: WebComponentOptions
): void => {
  if (!isRegistered(tag) && window.customElements) {
    const customElement: CustomElementConstructor = wrapper(component, createApp, h, options);
    window.customElements.define(tag, customElement);
  }
};

export const isDefined = async (tag: string): Promise<void> => {
  new Promise(async (resolve, reject) => {
    if (!window.customElements) {
      reject('Web components are not supported!');
    }
    try {
      await window.customElements.whenDefined(tag);
    } catch (e) {
      reject(e);
      return;
    }
    resolve();
  });
};
