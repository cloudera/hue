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

import { DirectiveOptions } from 'vue';

interface ClickOutsideHTMLElement extends HTMLElement {
  clickOutsideHandler?: (event: MouseEvent) => void;
}

export const clickOutsideDirective: DirectiveOptions = {
  bind: (element: ClickOutsideHTMLElement, binding, vNode) => {
    element.clickOutsideHandler = (event: MouseEvent) => {
      if (
        vNode.context &&
        vNode.context[binding.expression] &&
        document.contains(<Node>event.target) &&
        !element.contains(<Node>event.target)
      ) {
        vNode.context[binding.expression](event);
      }
    };
    document.addEventListener('click', element.clickOutsideHandler);
  },
  unbind: (element: ClickOutsideHTMLElement) => {
    if (element.clickOutsideHandler) {
      document.removeEventListener('click', element.clickOutsideHandler);
      element.clickOutsideHandler = undefined;
    }
  }
};
