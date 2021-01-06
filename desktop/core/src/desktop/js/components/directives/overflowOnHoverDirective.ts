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

interface OverflowOnHoverHTMLElement extends HTMLElement {
  disposeOverflowOnHover?: () => void;
}

interface OverflowOnHoverValue {
  direction?: 'y' | 'x' | 'both';
}

const getOverflowStyle = (
  value: OverflowOnHoverValue
): keyof Pick<CSSStyleDeclaration, 'overflow' | 'overflowX' | 'overflowY'> => {
  if (value && value.direction === 'x') {
    return 'overflowX';
  }
  if (value && value.direction === 'y') {
    return 'overflowY';
  }
  return 'overflow';
};

export const overflowOnHover: DirectiveOptions = {
  bind: (el: OverflowOnHoverHTMLElement, binding) => {
    const value = <OverflowOnHoverValue>binding.value;
    const overflowStyle = getOverflowStyle(value);
    const initialOverflowValue = el.style[overflowStyle];
    el.style[overflowStyle] = 'hidden';

    let isTouch = false;
    const onTouchStart = () => {
      isTouch = true;
    };

    let showDelay = -1;
    const onMouseEnter = () => {
      showDelay = window.setTimeout(() => {
        el.style[overflowStyle] = 'auto';
      }, 30);
    };

    const onMouseLeave = () => {
      window.clearTimeout(showDelay);
      if (!isTouch) {
        el.style[overflowStyle] = 'hidden';
      }
    };

    el.addEventListener('touchstart', onTouchStart);
    el.addEventListener('mouseenter', onMouseEnter);
    el.addEventListener('mouseleave', onMouseLeave);

    el.disposeOverflowOnHover = () => {
      window.clearTimeout(showDelay);
      el.removeEventListener('touchstart', onTouchStart);
      el.removeEventListener('mouseenter', onMouseEnter);
      el.removeEventListener('mouseleave', onMouseLeave);
      el.style[overflowStyle] = initialOverflowValue;
    };
  },
  unbind: (el: OverflowOnHoverHTMLElement) => {
    if (el.disposeOverflowOnHover) {
      el.disposeOverflowOnHover();
    }
  }
};
