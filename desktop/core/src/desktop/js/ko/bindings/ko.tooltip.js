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
import * as ko from 'knockout';

import { registerBinding } from './bindingUtils';
import escapeOutput from 'utils/html/escapeOutput';

export const NAME = 'tooltip';

registerBinding(NAME, {
  after: ['attr'],
  update: function (element, valueAccessor) {
    const local = ko.utils.unwrapObservable(valueAccessor());
    const options = {
      container: 'body'
    };

    $(element).tooltip('destroy');

    ko.utils.extend(options, local);

    if (options.title) {
      const title = ko.unwrap(options.title); // Not always an observable
      if (typeof title === 'string' && !options.html) {
        options.title = escapeOutput(title);
      }
    }

    $(element).tooltip(options);

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      $(element).tooltip('destroy');
    });
  }
});
