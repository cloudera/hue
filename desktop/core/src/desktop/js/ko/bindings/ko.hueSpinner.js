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

/**
 * Binding for adding a spinner to the page
 *
 * Example:
 *
 * <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
 *
 */
ko.bindingHandlers.hueSpinner = {
  update: function(element, valueAccessor) {
    const value = ko.unwrap(valueAccessor());

    const options = {
      size: 'default',
      center: false,
      overlay: false,
      inline: false,
      blackout: false
    };

    let spin = false;
    if (ko.isObservable(valueAccessor())) {
      spin = value();
    } else {
      $.extend(options, value);
      spin = typeof value.spin === 'function' ? value.spin() : value.spin;
    }

    ko.virtualElements.emptyNode(element);

    if (spin) {
      const $container = $('<div>');
      $container.addClass(
        options.overlay
          ? 'hue-spinner-overlay'
          : options.inline
          ? 'hue-spinner-inline'
          : 'hue-spinner'
      );
      if (options.blackout) {
        $container.addClass('hue-spinner-blackout');
      }
      if (!options.overlay) {
        const $spinner = $('<i>');
        $spinner.addClass('fa fa-spinner fa-spin');
        if (options.size === 'large') {
          $spinner.addClass('hue-spinner-large');
        }
        if (options.size === 'xlarge') {
          $spinner.addClass('hue-spinner-xlarge');
        }
        if (options.center) {
          $spinner.addClass('hue-spinner-center');
          if (options.inline) {
            $container.css('width', '100%');
          }
        }
        $container.append($spinner);
      }
      ko.virtualElements.prepend(element, $container[0]);
    }
  }
};

ko.virtualElements.allowedBindings.hueSpinner = true;
