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

ko.bindingHandlers.multiCheck = {
  init: function(element, valueAccessor) {
    $(element)
      .attr('unselectable', 'on')
      .css('user-select', 'none')
      .on('selectstart', false);

    const $container = $(ko.unwrap(valueAccessor()));
    $(element).click(e => {
      const $self = $(e.target);
      if ($self.data('noMultiCheck')) {
        $self.data('noMultiCheck', false);
        return;
      }
      const shouldCheck = $self.is(':checked') || !$self.hasClass('fa-check');
      if (e.shiftKey && shouldCheck === $container.data('last-clicked-checkbox-state')) {
        let insideGroup = false;
        let allCheckboxes = $container.find(':checkbox');
        if (allCheckboxes.length === 0) {
          allCheckboxes = $container.find('.hue-checkbox');
        }
        for (let i = 0; i < allCheckboxes.length; i++) {
          const checkbox = allCheckboxes[i];
          if (checkbox === e.target || checkbox === $container.data('last-clicked-checkbox')) {
            if (insideGroup) {
              break;
            }
            insideGroup = true;
            continue;
          }
          if (insideGroup) {
            const $checkbox = $(checkbox);
            $checkbox.data('noMultiCheck', true);
            if (($checkbox.is(':checked') || $checkbox.hasClass('fa-check')) !== shouldCheck) {
              $checkbox.trigger('click');
            }
          }
        }
      }
      $container.data('last-clicked-checkbox', e.target);
      $container.data('last-clicked-checkbox-state', shouldCheck);
    });
  },
  update: function() {}
};
