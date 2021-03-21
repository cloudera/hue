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

function setProps(el, props) {
  for (const key in props) {
    el.setAttribute(key, props[key]);
  }
  Object.assign(el, props);
}

ko.bindingHandlers.vueKoProps = {
  init: (element, valueAccessor) => {
    const data = valueAccessor();
    setProps(element, data);
  }
};

ko.bindingHandlers.vueProps = {
  init: (element, valueAccessor) => {
    const data = valueAccessor();
    setProps(element, ko.toJS(data));
  }
};

ko.bindingHandlers.vueEvents = {
  init: (element, valueAccessor) => {
    const data = valueAccessor();
    for (const [eventName, handler] of Object.entries(data)) {
      element.addEventListener(eventName, handler);
    }
  }
};
