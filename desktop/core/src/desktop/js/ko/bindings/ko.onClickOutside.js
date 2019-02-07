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
import ko from 'knockout';

ko.bindingHandlers.onClickOutside = {
  update: function(element, valueAccessor, allBindingsAccessor, viewModel) {
    const options = valueAccessor();
    const func = typeof options === 'function' ? options : options.onOutside;

    const onDocumentClick = function(event) {
      if ($.contains(document, event.target) && !$.contains(element, event.target)) {
        const result = func.bind(viewModel)();
        if (typeof result === 'undefined' || result) {
          $(document).off('click', onDocumentClick);
        }
      }
    };

    $(document).off('click', onDocumentClick);
    $(document).on('click', onDocumentClick);

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      $(document).off('click', onDocumentClick);
    });
  }
};
