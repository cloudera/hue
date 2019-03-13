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

import I18n from 'utils/i18n';

ko.bindingHandlers.tagEditor = {
  init: function(element, valueAccessor) {
    let options = valueAccessor();
    const $element = $(element);

    const validRegExp = options.validRegExp ? new RegExp(options.validRegExp) : undefined;

    const showValidationError = function() {
      const $errorWrapper = $element.siblings('.selectize-error');
      if (options.invalidMessage && $errorWrapper.length > 0) {
        $errorWrapper.find('.message').text(options.invalidMessage);
        $errorWrapper.show();
        window.setTimeout(() => {
          $errorWrapper.fadeOut(400, () => {
            $errorWrapper.hide();
          });
        }, 5000);
      }
    };

    options = $.extend(
      {
        plugins: ['remove_button'],
        options: $.map(options.setTags(), value => {
          return { value: value, text: value };
        }),
        delimiter: ',',
        items: options.setTags(),
        closeAfterSelect: true,
        persist: true,
        preload: true,
        create: function(input) {
          if (typeof validRegExp !== 'undefined' && !validRegExp.test(input)) {
            showValidationError();
            return false;
          }

          return {
            value: input.replace(/\s/g, '-'),
            text: input.replace(/\s/g, '-')
          };
        }
      },
      options
    );

    const $readOnlyContainer = $('<div>')
      .hide()
      .addClass('selectize-control selectize-read-only multi')
      .attr('style', $element.attr('style'))
      .insertAfter($(element));

    if (!options.readOnly) {
      $readOnlyContainer.on('mouseover', () => {
        $readOnlyContainer.find('.selectize-actions').addClass('selectize-actions-visible');
      });

      $readOnlyContainer.on('mouseout', () => {
        $readOnlyContainer.find('.selectize-actions').removeClass('selectize-actions-visible');
      });
    }

    $element.hide();

    let currentSelectize;
    let optionsBeforeEdit = [];

    const saveOnClickOutside = function(event) {
      if (
        $.contains(document, event.target) &&
        currentSelectize &&
        !$.contains(currentSelectize.$wrapper[0], event.target)
      ) {
        if (currentSelectize.getValue() !== optionsBeforeEdit.join(',')) {
          options.onSave(currentSelectize.getValue());
        }
        $(document).off('click', saveOnClickOutside);
        $(document).off('keyup', hideOnEscape);
        showReadOnly();
      }
    };

    const hideOnEscape = function(event) {
      if (event.which === 27) {
        showReadOnly();
      }
    };

    let sizeCheckInterval = -1;

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      window.clearInterval(sizeCheckInterval);
    });

    const showEdit = function() {
      window.clearInterval(sizeCheckInterval);
      optionsBeforeEdit = options.setTags().concat();
      options.options = $.map(options.setTags(), value => {
        return { value: value, text: value };
      });
      currentSelectize = $element.selectize(options)[0].selectize;
      $readOnlyContainer.hide();
      $element
        .next()
        .find('.selectize-input')
        .css('padding-right', '38px');
      $element
        .next()
        .find('input')
        .focus();
      const $editActions = $('<div>')
        .addClass('selectize-actions')
        .appendTo($element.next());
      $('<i>')
        .addClass('fa fa-check')
        .click(() => {
          if (currentSelectize.getValue() !== optionsBeforeEdit.join(',')) {
            options.onSave(currentSelectize.getValue());
          }
          showReadOnly();
        })
        .appendTo($editActions);
      $('<i>')
        .addClass('fa fa-close')
        .click(() => {
          showReadOnly();
        })
        .appendTo($editActions);
      window.setTimeout(() => {
        $(document).on('click', saveOnClickOutside);
        $(document).on('keyup', hideOnEscape);
      }, 0);
    };

    let lastKnownOffsetWidth = -1;
    let lastKnownOffsetHeight = -1;

    const addReadOnlyTagsTillOverflow = function($readOnlyInner) {
      $readOnlyInner.empty();
      const tagElements = [];
      options.setTags().forEach(tag => {
        tagElements.push(
          $('<div>')
            .text(tag)
            .appendTo($readOnlyInner)
        );
      });

      if (!options.readOnly && !options.hasErrors()) {
        $('<i>')
          .addClass('fa fa-pencil selectize-edit pointer')
          .attr('title', I18n('Edit tags'))
          .appendTo($readOnlyInner);
        $readOnlyInner.click(() => {
          showEdit();
        });
      }

      if (!options.overflowEllipsis) {
        return;
      }

      if (
        $readOnlyInner[0].offsetHeight < $readOnlyInner[0].scrollHeight ||
        ($readOnlyInner[0].offsetWidth < $readOnlyInner[0].scrollWidth && tagElements.length)
      ) {
        tagElements[tagElements.length - 1].after(
          $('<div>')
            .addClass('hue-tag-overflow')
            .text('...')
        );
      }

      while (
        tagElements.length &&
        ($readOnlyInner[0].offsetHeight < $readOnlyInner[0].scrollHeight ||
          $readOnlyInner[0].offsetWidth < $readOnlyInner[0].scrollWidth)
      ) {
        tagElements.pop().remove();
      }

      lastKnownOffsetWidth = $readOnlyInner[0].offsetWidth;
      lastKnownOffsetHeight = $readOnlyInner[0].offsetHeight;
    };

    const showReadOnly = function() {
      window.clearInterval(sizeCheckInterval);
      $(document).off('click', saveOnClickOutside);
      $(document).off('keyup', hideOnEscape);
      if (currentSelectize) {
        currentSelectize.destroy();
        $element.hide();
        $element.val(options.setTags().join(','));
      }
      $readOnlyContainer.empty();
      const $readOnlyInner = $('<div>')
        .addClass('selectize-input items not-full has-options has-items')
        .appendTo($readOnlyContainer);
      if (options.setTags().length > 0) {
        addReadOnlyTagsTillOverflow($readOnlyInner);
        if (options.overflowEllipsis) {
          sizeCheckInterval = window.setInterval(() => {
            if (
              $readOnlyInner[0].offsetWidth !== lastKnownOffsetWidth ||
              $readOnlyInner[0].offsetHeight !== lastKnownOffsetHeight
            ) {
              addReadOnlyTagsTillOverflow($readOnlyInner);
            }
          }, 500);
        }
      } else {
        if (options.hasErrors()) {
          $('<span>')
            .addClass('selectize-no-tags')
            .text(options.errorMessage)
            .appendTo($readOnlyInner);
        } else {
          $('<span>')
            .addClass('selectize-no-tags')
            .text(options.emptyPlaceholder)
            .appendTo($readOnlyInner);
        }

        if (!options.readOnly && !options.hasErrors()) {
          $('<i>')
            .addClass('fa fa-pencil selectize-edit pointer')
            .attr('title', I18n('Edit tags'))
            .appendTo($readOnlyInner);
          $readOnlyInner.click(() => {
            showEdit();
          });
        }
      }

      $readOnlyContainer.attr('title', options.setTags().join(', '));

      $readOnlyContainer.show();
    };

    showReadOnly();
  }
};
