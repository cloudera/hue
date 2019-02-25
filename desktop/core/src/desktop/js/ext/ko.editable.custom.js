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

// based on the original https://github.com/brianchance/knockout-x-editable

import $ from 'jquery';
import ko from 'knockout';

ko.bindingHandlers.editable = {
  init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    var $element = $(element),
        value = valueAccessor(),
        allBindings = allBindingsAccessor(),
        editableOptions = allBindings.editableOptions || {};

    editableOptions.value = ko.utils.unwrapObservable(value);

    if (!editableOptions.name) {
      $.each(bindingContext.$data, function (k, v) {
        if (v == value) {
          editableOptions.name = k;
          return false;
        }
      });
    }

    //wrap calls to knockout.validation
    if (!editableOptions.validate && value.isValid) {
      editableOptions.validate = function (testValue) {
        //have to set to new value, then call validate, then reset to original value
        //not pretty, but works
        var initalValue = value();
        value(testValue);
        var res = value.isValid() ? null : ko.utils.unwrapObservable(value.error);
        value(initalValue);
        return res;
      }
    }

    if ((editableOptions.type === 'select' || editableOptions.type === 'checklist' || editableOptions.type === 'typeahead') && !editableOptions.source && editableOptions.options) {
      if (editableOptions.optionsCaption)
        editableOptions.prepend = editableOptions.optionsCaption;

      //taken directly from ko.bindingHandlers['options']
      function applyToObject(object, predicate, defaultValue) {
        var predicateType = typeof predicate;
        if (predicateType === "function")    // Given a function; run it against the data value
          return predicate(object);
        else if (predicateType === "string") // Given a string; treat it as a property name on the data value
          return object[predicate];
        else                                // Given no optionsText arg; use the data value itself
          return defaultValue;
      }

      editableOptions.source = function () {
        return ko.utils.arrayMap(editableOptions.options(), function (item) {
          var optionValue = applyToObject(item, editableOptions.optionsValue, item);
          var optionText = applyToObject(item, editableOptions.optionsText, optionText);

          return {
            value: ko.utils.unwrapObservable(optionValue),
            text: ko.utils.unwrapObservable(optionText)
          };
        });
      }
    }

    if (editableOptions.visible && ko.isObservable(editableOptions.visible)) {
      editableOptions.toggle = 'manual';
    }

    var onActionRender = undefined;

    if (editableOptions.inlineEditAction) {
      onActionRender = function ($container, overflowing) {
        if (!overflowing) {
          var $editAction = $('<a href="javascript:void(0);"><i class="fa fa-fw fa-pencil"></i></a>');
          if (editableOptions.inlineEditAction.editClass) {
            $editAction.addClass(editableOptions.inlineEditAction.editClass);
          }
          $editAction.on('click', function () {
            $editable.editable('toggle');
          });
          $editAction.appendTo($container);
        }
      }
    }

    var addPlaceHolder = function ($container) {
      if (editableOptions.placeholder) {
        $('<div>').addClass('editable-inline-empty').text(editableOptions.placeholder).click(function () {
          $editable.editable('toggle');
        }).appendTo($container);
      }
    };

    var multiLineEllipsisHandler;
    if (editableOptions.multiLineEllipsis) {
      editableOptions.display = function (value) {
        if (!value) {
          if (multiLineEllipsisHandler) {
            multiLineEllipsisHandler.pause();
          }
          var $container = $(this);
          $container.empty();
          addPlaceHolder($container);
          if (onActionRender) {
            onActionRender($container);
          }
          return;
        }

        if (!multiLineEllipsisHandler) {
          multiLineEllipsisHandler = new MultiLineEllipsisHandler({
            element: this,
            text: value,
            overflowHeight: editableOptions.multiLineEllipsis.overflowHeight,
            expandable: editableOptions.multiLineEllipsis,
            expandActionClass: editableOptions.multiLineEllipsis.expandActionClass,
            linkify: true,
            onActionRender: onActionRender
          });

          ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
            multiLineEllipsisHandler.dispose();
          });
        } else {
          multiLineEllipsisHandler.setText(value);
          multiLineEllipsisHandler.resume();
        }
      }
    } else if (onActionRender) {
      editableOptions.display = function (value) {
        var $container = $(this);
        if (!value) {
          addPlaceHolder($container);
        } else {
          $('<span>').html(value).appendTo($container);
        }
        onActionRender($container);
      };

      onActionRender = function ($container) {
        var $editAction = $('<a href="javascript:void(0);"><i class="fa fa-fw fa-pencil"></i></a>');
        if (editableOptions.inlineEditAction.editClass) {
          $editAction.addClass(editableOptions.inlineEditAction.editClass);
        }
        $editAction.appendTo($container);
      }
    }

    //create editable
    var $editable = $element.editable(editableOptions);

    if (editableOptions.multiLineEllipsis) {
      $editable.off('.multiLine');
      $editable.on('hidden.multiLine', function () {
        if (multiLineEllipsisHandler && ko.unwrap(value)) {
          multiLineEllipsisHandler.resume();
        }
      });
      $editable.on('shown.multiLine', function () {
        if (multiLineEllipsisHandler) {
          multiLineEllipsisHandler.pause();
        }
      })
    }

    //update observable on save
    if (ko.isObservable(value)) {
      $editable.on('save.ko', function (e, params) {
        var newValue = params.newValue || '';
        if (editableOptions.type === 'wysihtml5') {
          if (editableOptions.skipNewLines) {
            newValue = newValue.replace(/<br\s*[\/]?>/gi, ' ').replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
          } else {
            newValue = newValue.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
          }
        } else {
          newValue = newValue.replace(/<(?:.|\n)*?>/gm, '');

          if (editableOptions.type !== 'textarea') {
            newValue = newValue.replace(/\r?\n|\r/g, ' ');
          }
        }
        value(newValue);
      })
    }

    if (editableOptions.toggleElement) {
      var $clickable = $element.parent().find(editableOptions.toggleElement);
      if ($element.parents('.show-inactive-on-hover').length > 0) {
        $clickable = $element.parents('.show-inactive-on-hover').find(editableOptions.toggleElement);
      }
      if ($clickable !== null) {
        $clickable.on('click', function (e) {
          e.stopPropagation();
          e.preventDefault();
          $editable.editable('toggle');
        });
      }
    }

    if (editableOptions.save) {
      $editable.on('save', editableOptions.save.bind(viewModel));
    }

    //setup observable to fire only when editable changes, not when options change
    //http://www.knockmeout.net/2012/06/knockoutjs-performance-gotcha-3-all-bindings.html
    ko.computed({
      read: function () {
        var _allBindings = ko.utils.unwrapObservable(allBindingsAccessor());
        var _options = _allBindings.editableOptions || {};
        if (_options.enabled != null && _options.enabled) {
          $editable.editable('enable');
        }
        else {
          $editable.editable('disable');
        }
        var val = ko.utils.unwrapObservable(valueAccessor());
        if (val === null) val = '';
        $editable.editable('setValue', val, true)
      },
      owner: this,
      disposeWhenNodeIsRemoved: element
    });

    if (editableOptions.visible && ko.isObservable(editableOptions.visible)) {
      ko.computed({
        read: function () {
          var val = ko.utils.unwrapObservable(editableOptions.visible());
          if (val)
            $editable.editable('show');
        },
        owner: this,
        disposeWhenNodeIsRemoved: element
      });

      $editable.on('hidden.ko', function (e, params) {
        editableOptions.visible(false);
      });
    }
  }
};