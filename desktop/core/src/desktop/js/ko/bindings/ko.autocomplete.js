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

ko.bindingHandlers.autocomplete = {
  init: function(element, valueAccessor) {
    let options = valueAccessor();
    const $element = $(element);

    const delay = 400;

    const showSpinner = function() {
      if (options.showSpinner) {
        $element.addClass('input-spinner');
      }
    };

    let spinThrottle = -1;
    const hideSpinner = function() {
      window.clearTimeout(spinThrottle);
      $element.removeClass('input-spinner');
    };

    options = $.extend(
      {
        addCount: false,
        closeOnEnter: true,
        blurOnEnter: false,
        classPrefix: 'hue-',
        showOnFocus: false,
        minLength: 0,
        limitWidthToInput: false,
        minWidth: 200,
        disabled: true,
        delay: delay,
        search: function() {
          window.clearTimeout(spinThrottle);
          if (!$element.hueAutocomplete('option', 'disabled')) {
            spinThrottle = window.setTimeout(showSpinner, 50);
          }
        },
        open: function() {
          hideSpinner();
        },
        close: function() {
          hideSpinner();
        }
      },
      options
    );

    if (options.addCount) {
      const oldSource = options.source;
      options.source = function(request, callback) {
        oldSource(request, values => {
          callback(values);
          const $menu = $($element.data('custom-hueAutocomplete').menu.element);
          $menu.children('.autocomplete-count').remove();
          const count = options.realCountCallback
            ? options.realCountCallback()
            : values.filter(value => {
                return !value.divider && !value.noMatch;
              }).length;
          if (count > 0) {
            $('<div>')
              .addClass('autocomplete-count')
              .text('(' + count + ')')
              .appendTo($menu);
          }
        });
      };
    }

    if (typeof $().hueAutocomplete === 'undefined') {
      $.widget('custom.hueAutocomplete', $.ui.autocomplete, {
        _renderItemData: function(ul, item) {
          if (item.error && this.options.errorTemplate) {
            const $li = $(
              '<li data-bind="template: { name: \'' + this.options.errorTemplate + '\' }">'
            )
              .addClass(this.options.classPrefix + 'autocomplete-item')
              .appendTo(ul)
              .data('ui-autocomplete-item', item);
            ko.applyBindings(item, $li[0]);
          } else if (item.noMatch && this.options.noMatchTemplate) {
            const $li = $(
              '<li data-bind="template: { name: \'' + this.options.noMatchTemplate + '\' }">'
            )
              .addClass(this.options.classPrefix + 'autocomplete-item')
              .appendTo(ul)
              .data('ui-autocomplete-item', item);
            ko.applyBindings(item, $li[0]);
          } else if (item.divider) {
            $('<li/>')
              .addClass(this.options.classPrefix + 'autocomplete-divider')
              .appendTo(ul);
          } else {
            const $li = $(
              '<li data-bind="template: { name: \'' +
                this.options.itemTemplate +
                '\', data: $data }">'
            )
              .addClass(this.options.classPrefix + 'autocomplete-item')
              .appendTo(ul)
              .data('ui-autocomplete-item', item);
            ko.applyBindings(item.data, $li[0]);
          }
        },
        _resizeMenu: function() {
          // This overrides the default behaviour of using dropdown width of the same size as input autocomplete box
          if (options.limitWidthToInput) {
            this.menu.element.outerWidth(options.minWidth);
          }
        },
        _renderMenu: function(ul, items) {
          const self = this;
          hideSpinner();
          if (options.limitWidthToInput) {
            ul.css('max-width', Math.max(options.minWidth, $element.outerWidth(true)) + 'px');
          }
          ul.css('min-width', options.minWidth || $element.outerWidth(true));
          ul.css('min-height', options.minHeight || '20px');

          ul.addClass(this.options.classPrefix + 'autocomplete');
          $.each(items, (index, item) => {
            self._renderItemData(ul, item);
          });
        }
      });
    }

    if (options.closeOnEnter || options.onEnter || options.blurOnEnter) {
      $element.on('keyup', e => {
        if (e.which === 13) {
          if (options.reopenPattern && options.reopenPattern.test($element.val())) {
            window.setTimeout(() => {
              $element.hueAutocomplete('search', $element.val());
            }, 0);
            return;
          }
          if (options.closeOnEnter) {
            hideSpinner();
            $element.hueAutocomplete('close');
            // Prevent autocomplete on enter
            $element.hueAutocomplete('option', 'disabled', true);
            window.setTimeout(() => {
              $element.hueAutocomplete('option', 'disabled', false);
            }, delay + 200);
          }
          if (options.valueObservable) {
            options.valueObservable($element.val());
          }
          if (options.onEnter) {
            options.onEnter();
          }
          if (options.blurOnEnter) {
            hideSpinner();
            $element.blur();
          }
        }
      });
    }

    $element.on('keydown', e => {
      // ctrl + backspace to delete words
      if (e.which === 8 && e.ctrlKey) {
        const lastSpaceOrColon = Math.max(
          $element.val().lastIndexOf(' '),
          $element.val().lastIndexOf(':')
        );
        if (lastSpaceOrColon < $element.val().length - 1) {
          if (lastSpaceOrColon !== -1) {
            $element.val($element.val().substring(0, lastSpaceOrColon + 1));
          } else {
            $element.val('');
          }
          e.preventDefault();
          return false;
        }
      } else if (e.which === 32 && e.ctrlKey) {
        $element.hueAutocomplete('search', $element.val());
      }
    });

    if (options.showOnFocus) {
      $element.on('focus', () => {
        $element.hueAutocomplete('search', $element.val());
      });
    }

    const closeSubscription = huePubSub.subscribe('autocomplete.close', () => {
      hideSpinner();
      $element.hueAutocomplete('close');
    });

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      closeSubscription.remove();
    });

    if (options.reopenPattern || options.valueObservable || options.onSelect) {
      const oldSelect = options.select;
      options.select = function(event, ui) {
        if (options.reopenPattern && options.reopenPattern.test(ui.item.value)) {
          window.setTimeout(() => {
            $element.hueAutocomplete('search', $element.val());
          }, 0);
          return;
        }
        if (options.valueObservable) {
          options.valueObservable(ui.item.value);
        }
        if (options.onSelect) {
          options.onSelect(ui.item);
        }
        if (oldSelect) {
          oldSelect(event, ui);
        }
      };
    }

    $element.hueAutocomplete(options);

    const enableAutocomplete = function() {
      if ($element.data('custom-hueAutocomplete')) {
        $element.hueAutocomplete('option', 'disabled', false);
        $element.off('click', enableAutocomplete);
      } else {
        window.setTimeout(enableAutocomplete, 200);
      }
    };
    // IE 11 trick to prevent it from being shown on page refresh
    $element.on('click', enableAutocomplete);
  }
};
