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

import { Directive } from 'vue';
import defer from 'utils/timing/defer';

interface ClickOutsideHTMLElement extends HTMLElement {
  clickOutsideHandler?: (event: MouseEvent) => void;
}

export const removeClickOutsideHandler = (element: ClickOutsideHTMLElement): void => {
  if (element.clickOutsideHandler) {
    document.removeEventListener('click', element.clickOutsideHandler);
    element.clickOutsideHandler = undefined;
  }
};

export const addClickOutsideHandler = (
  element: ClickOutsideHTMLElement,
  callback: (event: MouseEvent) => void
): (() => void) => {
  removeClickOutsideHandler(element);
  element.clickOutsideHandler = (event: MouseEvent) => {
    if (document.contains(<Node>event.target) && !element.contains(<Node>event.target)) {
      callback(event);
    }
  };
  document.addEventListener('click', element.clickOutsideHandler);
  return () => {
    removeClickOutsideHandler(element);
  };
};

export const clickOutsideDirective: Directive<
  ClickOutsideHTMLElement,
  ((event: MouseEvent) => void) | undefined
> = {
  mounted: (element, binding) => {
    defer(() => {
      if (binding.value && typeof binding.value === 'function') {
        addClickOutsideHandler(element, binding.value);
      }
    });
  },
  unmounted: removeClickOutsideHandler
};
