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

import $ from 'jquery';

const waitForRendered = (
  selector: string | JQuery,
  condition: (element: JQuery) => boolean,
  callback: (element: JQuery) => void,
  timeout?: number
): void => {
  const $el = (<JQuery>selector).jquery ? <JQuery>selector : $(<string>selector);
  if (condition($el)) {
    callback($el);
  } else {
    window.clearTimeout($el.data('waitForRenderTimeout'));
    const waitForRenderTimeout = window.setTimeout(() => {
      waitForRendered(selector, condition, callback);
    }, timeout || 100);
    $el.data('waitForRenderTimeout', waitForRenderTimeout);
  }
};

export default waitForRendered;
