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

import huePubSub from 'utils/huePubSub';

// TODO: Depends on impalaDagre

ko.bindingHandlers.impalaDagre = (function() {
  return {
    init: function(element, valueAccessor, allBindingsAccessor) {
      const id = $(element).attr('id');
      element._impalaDagre = impalaDagre(id);
      const clickSubscription = huePubSub.subscribe('impala.node.moveto', value => {
        element._impalaDagre.moveTo(value);
      });
      const selectSubscription = huePubSub.subscribe('impala.node.select', value => {
        element._impalaDagre.select(value);
      });
      ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
        clickSubscription.remove();
        selectSubscription.remove();
      });
    },
    update: function(element, valueAccessor) {
      const props = ko.unwrap(valueAccessor());
      element._impalaDagre.metrics(props.metrics);
      element._impalaDagre.height(props.height);
      element._impalaDagre.update(props.value);
    }
  };
})();
