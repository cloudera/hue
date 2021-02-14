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

import { ComponentOptions, Component } from 'vue';
import wrapper from './wrapper/index';

export interface HueComponentOptions<T extends Component> extends ComponentOptions<T> {
  hueBaseUrl?: string;
}

const isRegistered = function (tag: string): boolean {
  return window.customElements.get(tag) !== undefined;
};

export const wrap = <T extends Component>(
  tag: string,
  component: { new (): T },
  options?: ElementDefinitionOptions
): void => {
  if (!isRegistered(tag)) {
    const customElement: CustomElementConstructor = wrapper(component);
    window.customElements.define(tag, customElement, options);
  }
};
