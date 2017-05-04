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

(function () {
  ko.extenders.numeric = function (target, config) {
    var precision = typeof config.precision === 'undefined' ? config : config.precision;
    var roundingMultiplier = Math.pow(10, precision);

    var result = ko.computed({
      read: target,
      write: function (newValue) {
        var current = target(),
            newValueAsNum = isNaN(newValue) ? 0 : parseFloat(+newValue),
            valueToWrite = Math.round(newValueAsNum * roundingMultiplier) / roundingMultiplier;

        if (newValue === '' && config.allowEmpty) {
          valueToWrite = newValue;
        }
        if (valueToWrite !== current) {
          target(valueToWrite);
        } else {
          if (newValue !== current) {
            target.notifySubscribers(valueToWrite);
          }
        }
      }
    }).extend({ notify: 'always' });
    result(target());
    return result;
  };

  ko.extenders.maxLength = function (target, maxLength) {
    var result = ko.computed({
      read: target,
      write: function (val) {
        if (maxLength > 0) {
          if (val.length > maxLength) {
            var limitedVal = val.substring(0, maxLength);
            if (target() === limitedVal) {
              target.notifySubscribers();
            }
            else {
              target(limitedVal);
            }
          }
          else {
            target(val);
          }
        }
        else {
          target(val);
        }
      }
    }).extend({notify: 'always'});
    result(target());
    return result;
  };

  ko.observableDefault = function () {
    var prop = arguments[0], defvalue = arguments[1] || null;
    return ko.observable(typeof prop != "undefined" && prop != null ? prop : defvalue);
  };

  ko.observableArrayDefault = function () {
    var prop = arguments[0], defvalue = arguments[1] || null;
    return ko.observableArray(typeof prop != "undefined" && prop != null ? prop : defvalue);
  };

  ko.bindingHandlers.hueLink = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      if (IS_HUE_4) {
        ko.bindingHandlers.click.init(element, function() {
          return function (data, event) {
            var url = ko.unwrap(valueAccessor());
            if (event.ctrlKey || event.metaKey) {
              window.open('/hue' + (url.indexOf('/') === 0 ? url : '/' + url), '_blank');
            } else {
              huePubSub.publish('open.link', url);
            }
          }
        }, allBindings, viewModel, bindingContext);
        $(element).attr('href', 'javascript: void(0);');
      } else {
        $(element).attr('href', ko.unwrap(valueAccessor()));
      }
    },
    update: function (element, valueAccessor) {
      if (!IS_HUE_4) {
        $(element).attr('href', ko.unwrap(valueAccessor()));
      }
    }

  };

  ko.bindingHandlers.clickToCopy = {
    init: function (element, valueAccessor) {
      $(element).click(function () {
        var $input = $('<textarea>').css({ opacity: 0 }).val(ko.unwrap(valueAccessor())).appendTo('body').select();
        document.execCommand('copy');
        $input.remove()
      });
    }
  };

  ko.bindingHandlers.autocomplete = {
    init: function (element, valueAccessor) {
      var options = valueAccessor();
      var $element = $(element);

      var delay = 400;

      var showSpinner = function () {
        if (options.showSpinner) {
          $element.addClass('input-spinner');
        }
      };

      var spinThrottle = -1;
      var hideSpinner = function () {
        window.clearTimeout(spinThrottle);
        $element.removeClass('input-spinner');
      };

      options = $.extend({
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
        search: function(event, ui) {
          window.clearTimeout(spinThrottle);
          if (!$element.hueAutocomplete("option", "disabled")) {
            spinThrottle = window.setTimeout(showSpinner, 50);
          }
        },
        open: function(event, ui) {
          hideSpinner();
        },
        close: function(event, ui) {
          hideSpinner();
        }
      }, options);

      if (options.addCount) {
        var oldSource = options.source;
        options.source = function (request, callback) {
          oldSource(request, function (values) {
            callback(values);
            var $menu = $($element.data('custom-hueAutocomplete').menu.element);
            $menu.children('.autocomplete-count').remove();
            var count = options.realCountCallback ? options.realCountCallback() : values.filter(function (value) { return ! value.divider && ! value.noMatch }).length;
            if (count > 0) {
              $('<div>').addClass('autocomplete-count').text('(' + count + ')').appendTo($menu);
            }
          });
        }
      }

      if (typeof $().hueAutocomplete === 'undefined') {
        $.widget('custom.hueAutocomplete', $.ui.autocomplete, {
          _renderItemData: function( ul, item ) {
            if (item.error && this.options.errorTemplate) {
              var $li = $('<li data-bind="template: { name: \'' + this.options.errorTemplate + '\' }">')
                  .addClass(this.options.classPrefix + 'autocomplete-item')
                  .appendTo(ul)
                  .data( "ui-autocomplete-item", item );
              ko.applyBindings(item, $li[0]);
            } else if (item.noMatch && this.options.noMatchTemplate) {
              var $li = $('<li data-bind="template: { name: \'' + this.options.noMatchTemplate + '\' }">')
                  .addClass(this.options.classPrefix + 'autocomplete-item')
                  .appendTo(ul)
                  .data( "ui-autocomplete-item", item );
              ko.applyBindings(item, $li[0]);
            } else if (item.divider) {
              $('<li/>').addClass(this.options.classPrefix + 'autocomplete-divider').appendTo(ul);
            } else {
              var $li = $('<li data-bind="template: { name: \'' + this.options.itemTemplate + '\', data: $data }">')
                .addClass(this.options.classPrefix + 'autocomplete-item')
                .appendTo(ul)
                .data( "ui-autocomplete-item", item );
              ko.applyBindings(item.data, $li[0]);
            }
          },
          _renderMenu: function (ul, items) {
            var self = this;
            hideSpinner();
            if (options.limitWidthToInput) {
              ul.css('max-width', Math.max(options.minWidth, $element.outerWidth(true)) + 'px');
            }

            ul.addClass(this.options.classPrefix + 'autocomplete');
            $.each(items, function (index, item) {
              self._renderItemData(ul, item);
            });
          }
        });
      }

      if (options.closeOnEnter || options.onEnter || options.blurOnEnter) {
        $element.on('keyup', function (e) {
          if(e.which === 13) {
            if (options.reopenPattern && options.reopenPattern.test($element.val())) {
              window.setTimeout(function () {
                $element.hueAutocomplete('search', $element.val());
              }, 0);
              return;
            }
            if (options.closeOnEnter) {
              hideSpinner();
              $element.hueAutocomplete('close');
              // Prevent autocomplete on enter
              $element.hueAutocomplete("option", "disabled", true);
              window.setTimeout(function () {
                $element.hueAutocomplete("option", "disabled", false);
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

      $element.on('keydown', function (e) {
        // ctrl + backspace to delete words
        if (e.which === 8 && e.ctrlKey) {
          var lastSpaceOrColon = Math.max($element.val().lastIndexOf(' '), $element.val().lastIndexOf(':'));
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
        $element.on('focus', function () {
          $element.hueAutocomplete('search', $element.val());
        })
      }

      var closeSubscription = huePubSub.subscribe('autocomplete.close', function () {
        hideSpinner();
        $element.hueAutocomplete('close');
      });

      ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
        closeSubscription.remove();
      });

      if (options.reopenPattern || options.valueObservable || options.onSelect) {
        var oldSelect = options.select;
        options.select = function (event, ui) {
          if (options.reopenPattern && options.reopenPattern.test(ui.item.value)) {
            window.setTimeout(function () {
              $element.hueAutocomplete('search', $element.val());
            }, 0);
            return;
          }
          if (options.valueObservable) {
            options.valueObservable(ui.item.value);
          }
          if (options.onSelect) {
            options.onSelect();
          }
          if (oldSelect) {
            oldSelect(event, ui);
          }
        };
      }

      $element.hueAutocomplete(options);

      ko.bindingHandlers.niceScroll.init($element.data('custom-hueAutocomplete').menu.element, function () {});


      var enableAutocomplete = function () {
        if ($element.data('custom-hueAutocomplete')) {
          $element.hueAutocomplete("option", "disabled", false);
        } else {
          window.setTimeout(enableAutocomplete, 200);
        }
      };
      // IE 11 trick to prevent it from being shown on page refresh
      enableAutocomplete();
    }
  };

  ko.bindingHandlers.tagEditor = {
    init: function (element, valueAccessor) {
      var options = valueAccessor();
      var $element = $(element);

      var validRegExp = options.validRegExp ? new RegExp(options.validRegExp) : undefined;

      var showValidationError = function () {
        var $errorWrapper = $element.siblings('.selectize-error');
        if (options.invalidMessage && $errorWrapper.length > 0) {
          $errorWrapper.find('.message').text(options.invalidMessage);
          $errorWrapper.show();
          window.setTimeout(function () {
            $errorWrapper.fadeOut(400, function () {
              $errorWrapper.hide();
            })
          }, 5000);
        }
      };

      options = $.extend({
        plugins: ['remove_button'],
        options: $.map(options.setTags(), function (value) { return { value: value, text: value } }),
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
          }
        }
      }, options);

      var $readOnlyContainer = $('<div>').hide().addClass('selectize-control selectize-read-only multi').attr('style', $element.attr('style')).insertAfter($(element));

      if (!options.readOnly) {
        $readOnlyContainer.on('mouseover', function () {
          $readOnlyContainer.find('.selectize-actions').addClass('selectize-actions-visible');
        });

        $readOnlyContainer.on('mouseout', function () {
          $readOnlyContainer.find('.selectize-actions').removeClass('selectize-actions-visible');
        });
      }

      $element.hide();

      var currentSelectize;
      var optionsBeforeEdit = [];

      var saveOnClickOutside = function (event) {
        if ($.contains(document, event.target) && currentSelectize && !$.contains(currentSelectize.$wrapper[0], event.target)) {
          if (currentSelectize.getValue() !== optionsBeforeEdit.join(',')) {
            options.onSave(currentSelectize.getValue());
          }
          $(document).off('click', saveOnClickOutside);
          $(document).off('keyup', hideOnEscape);
          showReadOnly();
        }
      };

      var hideOnEscape = function (event) {
        if (event.which === 27) {
          showReadOnly();
        }
      };

      var showEdit = function () {
        optionsBeforeEdit = options.setTags().concat();
        options.options = $.map(options.setTags(), function (value) { return { value: value, text: value } });
        currentSelectize = $element.selectize(options)[0].selectize;
        $readOnlyContainer.hide();
        $element.next().find('.selectize-input').css('padding-right', '38px');
        $element.next().find('input').focus();
        var $editActions = $('<div>').addClass('selectize-actions').appendTo($element.next());
        $('<i>').addClass('fa fa-check').click(function () {
          if (currentSelectize.getValue() !== optionsBeforeEdit.join(',')) {
            options.onSave(currentSelectize.getValue());
          }
          showReadOnly();
        }).appendTo($editActions);
        $('<i>').addClass('fa fa-close').click(function () {
          showReadOnly();
        }).appendTo($editActions);
        window.setTimeout(function () {
          $(document).on('click', saveOnClickOutside);
          $(document).on('keyup', hideOnEscape);
        }, 0);
      };

      var showReadOnly = function () {
        $(document).off('click', saveOnClickOutside);
        $(document).off('keyup', hideOnEscape);
        if (currentSelectize) {
          currentSelectize.destroy();
          $element.hide();
          $element.val(options.setTags().join(','))
        }
        $readOnlyContainer.empty();
        var $readOnlyInner = $('<div>').addClass('selectize-input items not-full has-options has-items').appendTo($readOnlyContainer);
        if (options.setTags().length > 0) {
          options.setTags().forEach(function (tag) {
            $('<div>').text(tag).appendTo($readOnlyInner);
          });
        } else if (options.hasErrors()) {
          $('<span>').addClass('selectize-no-tags').text(options.errorMessage).appendTo($readOnlyInner);
        } else {
          $('<span>').addClass('selectize-no-tags').text(options.placeholder).appendTo($readOnlyInner);
        }

        if (! options.readOnly && !options.hasErrors()) {
          $('<i>').addClass('fa fa-edit selectize-edit pointer').appendTo($readOnlyInner);
          $readOnlyInner.click(function () {
            showEdit();
          });
        }

        $readOnlyContainer.show();
      };

      showReadOnly();
    }
  };

  ko.bindingHandlers.toggleOverflow = {
    render: function ($element) {
      if (hueUtils.isOverflowing($element.find('.toggle-overflow'))) {
        $('<div>').addClass('toggle-overflow-gradient').html('<i class="fa fa-caret-down muted"></i>').appendTo($element);
        $element.on('click', function () {
          $element.find('.toggle-overflow-gradient').hide();
          $element.find('.toggle-overflow').css('height', '');
          $element.css('cursor', 'default');
        });
      }
    },
    init: function (element, valueAccessor) {
      var $element = $(element);
      var options = $.extend(valueAccessor(), {});
      $element.wrapInner('<div class="toggle-overflow"></div>');
      if (options.height) {
        $element.find('.toggle-overflow').height(options.height);
      }
      if (options.width) {
        $element.find('.toggle-overflow').width(options.width);
      }
    },
    update: function (element, valueAccessor) {
      var $element = $(element);
      window.setTimeout(function () {
        ko.bindingHandlers.toggleOverflow.render($element);
      }, 100);
    }
  };

  ko.bindingHandlers.draggableText = {
    init: function (element, valueAccessor) {
      var $element = $(element);
      var options = valueAccessor();
      $element.addClass("draggableText");

      var $helper = $("<div>").text(ko.isObservable(options.text) ? options.text() : options.text).css("z-index", "99999");
      var dragStartX = -1;
      var dragStartY = -1;
      $element.draggable({
        helper: function () { return $helper },
        appendTo: "body",
        start: function (event) {
          dragStartX = event.clientX;
          dragStartY = event.clientY;
          huePubSub.publish('draggable.text.meta', options.meta);
        },
        stop: function (event) {
          if (Math.sqrt((dragStartX-event.clientX)*(dragStartX-event.clientX) + (dragStartY-event.clientY)*(dragStartY-event.clientY)) < 10) {
            $helper.remove();
            var elementAtStart = document.elementFromPoint(dragStartX, dragStartY);
            var elementAtStop = document.elementFromPoint(event.clientX, event.clientY);
            if (elementAtStart === elementAtStop) {
              $(elementAtStop).trigger('click');
            }
          }
        },
      });
    }
  };

  /**
   * Binding for adding a spinner to the page
   *
   * Example:
   *
   * <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
   *
   */
  ko.bindingHandlers.hueSpinner = {
    update: function (element, valueAccessor) {
      var value = ko.unwrap(valueAccessor());

      var options = {
        size: 'default',
        center: false,
        overlay: false
      };

      var spin = false;
      if (ko.isObservable(valueAccessor())) {
        spin = value();
      } else {
        $.extend(options, value);
        spin = typeof value.spin === 'function' ? value.spin() : value.spin;
      }

      ko.virtualElements.emptyNode(element);

      if (spin) {
        var $container = $('<div>');
        $container.addClass(options.overlay ? 'hue-spinner-overlay' : 'hue-spinner');
        if (!options.overlay) {
          var $spinner = $('<i>');
          $spinner.addClass('fa fa-spinner fa-spin');
          if (options.size === 'large') {
            $spinner.addClass('hue-spinner-large');
          }
          if (options.size === 'xlarge') {
            $spinner.addClass('hue-spinner-xlarge');
          }
          if (options.center) {
            $spinner.addClass('hue-spinner-center');
          }
        }
        $container.append($spinner);
        ko.virtualElements.prepend(element, $container[0]);
      }
    }
  };
  ko.virtualElements.allowedBindings.hueSpinner = true;

  ko.bindingHandlers.visibleOnHover = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var options = valueAccessor();
      var $element  = $(element);

      var selector = options.selector;
      var showTimeout = -1;
      var hideTimeout = -1;
      ko.utils.domData.set(element, 'visibleOnHover.override', ko.utils.unwrapObservable(options.override) || false);
      var inside = false;

      var show = function () {
        if (options.childrenOnly) {
          $element.children(selector).fadeTo("fast", 1);
        } else {
          $element.find(selector).fadeTo("fast", 1);
        }
        window.clearTimeout(hideTimeout);
      };

      var hide = function () {
        if (! inside) {
          window.clearTimeout(showTimeout);
          hideTimeout = window.setTimeout(function () {
            if (options.childrenOnly) {
              $element.children(selector).fadeTo("fast", 0);
            } else {
              $element.find(selector).fadeTo("fast", 0);
            }
          }, 10);
        }
      };

      ko.utils.domData.set(element, 'visibleOnHover.show', show);
      ko.utils.domData.set(element, 'visibleOnHover.hide', hide);

      if (ko.utils.domData.get(element, 'visibleOnHover.override')) {
        window.setTimeout(show, 1);
      }

      $element.mouseenter(function () {
        showTimeout = window.setTimeout(function () {
          inside = true;
          show();
        }, 300);
      });

      $element.mouseleave(function () {
        window.clearTimeout(showTimeout);
        inside = false;
        if (! ko.utils.domData.get(element, 'visibleOnHover.override')) {
          hide();
        }
      });
    },
    update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      if (ko.utils.unwrapObservable(valueAccessor().override)) {
        ko.utils.domData.set(element, 'visibleOnHover.override', true)
        ko.utils.domData.get(element, 'visibleOnHover.show')()
      } else {
        ko.utils.domData.set(element, 'visibleOnHover.override', false)
        ko.utils.domData.get(element, 'visibleOnHover.hide')();
      }
    }
  };

  /**
   * Binding for jquery UI resizable
   *
   * @type {{init: ko.bindingHandlers.resizable.init}}
   */
  ko.bindingHandlers.resizable = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var options = valueAccessor() || {};
      $(element).resizable(options);
      $(element).children('.ui-resizable-handle').css('z-index', 10000);
    }
  };

  /**
   * This binding can be used to toggle a boolean value on click
   *
   * Example:
   *
   * <div databind="toggle: value">...</div>
   *
   * @type {{init: ko.bindingHandlers.toggle.init}}
   */
  ko.bindingHandlers.toggle = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var value = valueAccessor();
      ko.bindingHandlers.click.init(element, function () {
        return function () {
          value(! value());
        }
      }, allBindings, viewModel, bindingContext);
    }
  };

  ko.bindingHandlers.slideVisible = {
    init: function (element, valueAccessor) {
      var value = valueAccessor();
      $(element).toggle(ko.unwrap(value));
    },
    update: function (element, valueAccessor, allBindings) {
      var value = valueAccessor();
      var onComplete = ko.unwrap(allBindings()).onComplete;
      ko.unwrap(value) ? $(element).slideDown(100, onComplete ? onComplete() : function(){}) : $(element).slideUp(100, onComplete ? onComplete() : function(){});
    }
  };

  ko.bindingHandlers.fadeVisible = {
    init: function (element, valueAccessor) {
      var value = valueAccessor();
      var toggleValue = typeof value.value === "undefined" ? value : value.value;
      $(element).toggle(ko.unwrap(toggleValue));
    },
    update: function (element, valueAccessor) {
      var value = valueAccessor();
      var toggleValue = typeof value.value === "undefined" ? value : value.value;
      var speed = typeof value.speed === "undefined" ? 'normal' : value.speed;
      var fadeOut = typeof value.fadeOut === "undefined" ? false : value.fadeOut;
      $(element).stop();
      if (ko.unwrap(toggleValue)) {
        $(element).fadeIn(speed);
      } else if (fadeOut) {
        $(element).fadeOut(speed);
      } else {
        $(element).hide();
      }
    }
  };

  /**
   * This binding can be used to show a custom context menu on right-click,
   * It assumes that the context menu is nested within the bound element and
   * the selector for the menu has to be supplied as a parameter.
   *
   * Example:
   *
   * <div data-bind="contextMenu: {
   *   menuSelector: '.hue-context-menu',
   *   beforeOpen: function () { ... }
   * }">
   *   <ul class="hue-context-menu">...</ul>
   * </div>
   *
   */
  ko.bindingHandlers.contextMenu = {
    initContextMenu: function ($menu, $scrollContainer) {
      var active = false;

      var currentLeft = 0;
      var currentTop = 0;
      var openScrollTop = 0;
      var openScrollLeft = 0;

      var adjustForScroll = function () {
        $menu.css('top', currentTop - $scrollContainer.scrollTop() + openScrollTop);
        $menu.css('left', currentLeft - $scrollContainer.scrollLeft() + openScrollLeft);
      }

      return {
        show: function (event) {
          $menu.css('top', 0);
          $menu.css('left', 0);
          $menu.css('opacity', 0);
          $menu.show();
          openScrollTop = $scrollContainer.scrollTop();
          openScrollLeft = $scrollContainer.scrollLeft();
          var menuWidth = $menu.outerWidth(true)
          if (event.clientX + menuWidth > $(window).width()) {
            currentLeft = $(window).width() - menuWidth
          } else {
            currentLeft = event.clientX;
          }
          $menu.css('left', currentLeft);

          var menuHeight = $menu.outerHeight(true);
          if (event.clientY + menuHeight > $(window).height()) {
            currentTop = $(window).height() - menuHeight;
          } else {
            currentTop = event.clientY;
          }
          $menu.css('top', currentTop);
          $menu.css('opacity', 1);
          active = true;
          $scrollContainer.on('scroll', adjustForScroll);
        },
        hide: function () {
          if (active) {
            $scrollContainer.off('scroll', adjustForScroll);
            $menu.css('opacity', 0);
            window.setTimeout(function () {
              $menu.hide();
            }, 300);
            active = false;
          }
        }
      }
    },
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var $element = $(element);
      var options = valueAccessor();
      var $menu = $element.find(options.menuSelector);

      bindingContext.$altDown = ko.observable(false);

      window.addEventListener("keydown", function (e) {
        bindingContext.$altDown(e.altKey);
      });

      window.addEventListener("keyup", function (e) {
        bindingContext.$altDown(false);
      });

      var $scrollContainer = $(options.scrollContainer).length > 0 ? $(options.scrollContainer) : $(window);

      var menu = ko.bindingHandlers.contextMenu.initContextMenu($menu, $scrollContainer);

      element.addEventListener("contextmenu", function(event) {
        if(document.selection && document.selection.empty) {
          document.selection.empty();
        } else if(window.getSelection) {
          var sel = window.getSelection();
          sel.removeAllRanges();
        }
        if (typeof options.beforeOpen === 'function') {
          options.beforeOpen.bind(viewModel)();
        }
        menu.show(event);
        huePubSub.publish('contextmenu-active', element);
        event.preventDefault();
        event.stopPropagation();
      });

      huePubSub.subscribe('contextmenu-active', function (origin) {
        if (origin !== element) {
          menu.hide();
        }
      });
      document.addEventListener("contextmenu", function (event) {
        menu.hide();
      });
      $menu.click(function (e) {
        menu.hide();
        e.stopPropagation();
      });
      $(document).click(function (event) {
        if ($element.find($(event.target)).length === 0) {
          menu.hide();
        }
      });
    }
  };


  ko.bindingHandlers.contextSubMenu = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var menuSelector = valueAccessor();
      var $element = $(element);

      var $menu = $element.find(menuSelector);
      var $parentMenu = $element.parent('.hue-context-menu');
      var open = false;

      var closeSubMenu = function () {
        open = false;
        $menu.hide();
        $element.removeClass('active');
      };

      var hideTimeout = -1;
      $element.add($menu).on('mouseenter', function () {
        $element.addClass('active');
        if (!open) {
          huePubSub.publish('hue.sub.menu.close');
        }
        open = true;
        window.clearTimeout(hideTimeout);
        var menuHeight = $menu.outerHeight();
        $menu.css('top', ($element.position().top + $parentMenu.position().top + menuHeight > $(window).height()) ? $(window).height() - menuHeight - 8 : $element.position().top + $parentMenu.position().top);
        $menu.css('left', $element.offset().left + $element.outerWidth(true));
        $menu.css('opacity', 0);
        $menu.show();
        $menu.css('opacity', 1);
        huePubSub.subscribeOnce('hue.sub.menu.close', closeSubMenu);
      });

      $element.add($menu).on('mouseleave', function () {
        window.clearTimeout(hideTimeout);
        hideTimeout = window.setTimeout(closeSubMenu, 300);
      });
    }
  };

  ko.bindingHandlers.appAwareTemplateContextMenu = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      viewModel.$currentApp = ko.observable('');
      huePubSub.subscribe('set.current.app.name', viewModel.$currentApp);
      huePubSub.publish('get.current.app.name');
      ko.bindingHandlers.templateContextMenu.init(element, valueAccessor, allBindings, viewModel, bindingContext);
    }
  };

  ko.bindingHandlers.templateContextMenu = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var options = valueAccessor();

      element.addEventListener("contextmenu", function(event) {
        if(document.selection && document.selection.empty) {
          document.selection.empty();
        } else if(window.getSelection) {
          var sel = window.getSelection();
          sel.removeAllRanges();
        }

        var $menu = $('#hueContextMenu_' + options.template);
        if ($menu.length === 0) {
          $menu = $('<ul id="hueContextMenu_' + options.template  + '" class="hue-context-menu" data-bind="template: { name: \'' + options.template + '\', data: viewModel, afterRender: afterRender }"></ul>').appendTo('body');
        } else {
          ko.cleanNode($menu[0]);
        }
        $menu.data('active', true);

        $menu.css('top', 0);
        $menu.css('left', 0);
        $menu.css('opacity', 0);
        $menu.show();

        var hideMenu = function () {
          if (!$menu.data('active')) {
            $menu.hide();
            ko.cleanNode($menu[0]);
          }
        };

        ko.applyBindings({
          afterRender: function () {
            var menuWidth = $menu.outerWidth(true);
            var menuHeight = $menu.outerHeight(true);
            $menu.css('left', (event.clientX + menuWidth > $(window).width()) ? $(window).width() - menuWidth : event.clientX);
            $menu.css('top', (event.clientY + menuHeight > $(window).height()) ? $(window).height() - menuHeight : event.clientY);
            $menu.css('opacity', 1);
            $(options.scrollContainer).one('scroll', hideMenu);
            window.setTimeout(function () {
              $menu.data('active', false);
              $(document).one('click', hideMenu);
            }, 100);
          },
          viewModel: viewModel
        }, $menu[0]);

        ko.contextFor($menu[0]).$contextSourceElement = element;
        event.preventDefault();
        event.stopPropagation();
      });
    }
  };

  ko.bindingHandlers.multiClick = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var clickHandlerFunction = valueAccessor().click;
      var dblClickHandlerFunction = valueAccessor().dblClick;
      if (!dblClickHandlerFunction && !clickHandlerFunction) {
        return;
      }

      var clickedOnce = false;
      var singleClickTimeout = -1;
      var dblClickTimeout = -1;

      var newValueAccessor = function() {
        return function() {
          var clickArgs = arguments;
          if (!dblClickHandlerFunction && clickHandlerFunction) {
            clickHandlerFunction.apply(viewModel, clickArgs);
            return;
          }
          if (clickedOnce) {
            dblClickHandlerFunction.apply(viewModel, clickArgs);
            clickedOnce = false;
            clearTimeout(singleClickTimeout);
            clearTimeout(dblClickTimeout);
          } else if (clickHandlerFunction) {
            clickedOnce = true;
            singleClickTimeout = window.setTimeout(function() {
              clickHandlerFunction.apply(viewModel, clickArgs);
              dblClickTimeout = window.setTimeout(function() {
                clickedOnce = false;
              }, 100);
            }, 225);
          }
        }
      };

      ko.bindingHandlers.click.init(element, newValueAccessor, allBindings, viewModel, bindingContext);
    }
  };

  ko.bindingHandlers.logScroller = {
    init: function (element, valueAccessor, allBindings) {
      var $element = $(element);

      $element.on("scroll", function () {
        $element.data('lastScrollTop', $element.scrollTop());
      });

      function autoLogScroll () {
        var elementHeight = $element.innerHeight();
        var lastScrollTop = $element.data('lastScrollTop') || 0;
        var lastScrollHeight = $element.data('lastScrollHeight') || elementHeight;

        var stickToBottom = (lastScrollTop + elementHeight) === lastScrollHeight;

        if (stickToBottom) {
          $element.scrollTop(element.scrollHeight - $element.height());
          $element.data('lastScrollTop', $element.scrollTop());
        }

        $element.data('lastScrollHeight', element.scrollHeight);
      }

      var logValue = valueAccessor();
      logValue.subscribe(function () {
        window.setTimeout(autoLogScroll, 200);
      });

      if (typeof allBindings().logScrollerVisibilityEvent !== 'undefined'){
        allBindings().logScrollerVisibilityEvent.subscribe(function () {
          window.setTimeout(autoLogScroll, 0);
        });
      }

      autoLogScroll();
    }
  };

  ko.bindingHandlers.multiCheck = {
    init: function (element, valueAccessor) {
      $(element).attr('unselectable', 'on').css('user-select', 'none').on('selectstart', false);

      var $container = $(ko.unwrap(valueAccessor()));
      $(element).click(function (e, shouldIgnore) {
        var $self = $(e.target);
        if ($self.data('noMultiCheck')) {
          $self.data('noMultiCheck', false);
          return;
        }
        var shouldCheck = $self.is(':checked') || ! $self.hasClass('fa-check');
        if (e.shiftKey && shouldCheck === $container.data('last-clicked-checkbox-state')) {
          var insideGroup = false;
          var allCheckboxes = $container.find(":checkbox");
          if (allCheckboxes.length == 0) {
            allCheckboxes = $container.find(".hueCheckbox");
          }
          for (var i = 0; i < allCheckboxes.length; i++) {
            var checkbox = allCheckboxes[i];
            if (checkbox === e.target || checkbox === $container.data('last-clicked-checkbox')) {
              if (insideGroup) {
                break;
              }
              insideGroup = true;
              continue;
            }
            if (insideGroup) {
              var $checkbox = $(checkbox);
              $checkbox.data('noMultiCheck', true);
              if (($checkbox.is(':checked') || $checkbox.hasClass('fa-check')) !== shouldCheck) {
                $checkbox.trigger("click");
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

  ko.bindingHandlers.numericTextInput = {
    init: function (element, valueAccessor, allBindings) {
      var bindingOptions = ko.unwrap(valueAccessor());
      var numericValue = ko.observable(bindingOptions.value()).extend({ numeric: { precision: bindingOptions.precision, allowEmpty: typeof bindingOptions.allowEmpty !== 'undefined' && bindingOptions.allowEmpty } });
      numericValue.subscribe(function(newValue) { bindingOptions.value(newValue) });
      ko.bindingHandlers.textInput.init(element, function() { return numericValue }, allBindings);
    }
  };

  ko.bindingHandlers.templatePopover = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
      var options = ko.unwrap(valueAccessor());

      var clickTrigger = options.trigger === 'click';
      var $container = $('#popover-container');
      if (! $container.length) {
        $container = $('<div>').attr('id', 'popover-container').appendTo('body');
        $('<div>').addClass('temp-content').hide().appendTo($container);
        $('<div>').addClass('temp-title').hide().appendTo($container);
      }

      var $content = $container.find('.temp-content');
      var $title = $container.find('.temp-title');

      $.extend(options, { html: true, trigger: 'manual', container: '#popover-container' });

      var $element = $(element);

      var visible = false;

      var hidePopover = function () {
        $element.popover('hide');
        visible = false;
        $(document).off('click', hideOnClickOutside)
      };

      huePubSub.subscribe('close.popover', hidePopover);

      var hideOnClickOutside = function (event) {
        if (visible && $element.data('popover') && ! $.contains($element.data('popover').$tip[0], event.target)) {
          hidePopover();
        }
      };

      ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
        if (visible && $element.data('popover')) {
          hidePopover();
        }
      });

      var showPopover = function () {
        ko.renderTemplate(options.contentTemplate, viewModel, {
          afterRender: function () {
            ko.renderTemplate(options.titleTemplate, viewModel, {
              afterRender: function () {
                options.content = $content.html();
                options.title = $title.html();
                $element.popover(options);
                $element.popover('show');
                var $tip = $element.data('popover').$tip;
                ko.cleanNode($tip.get(0));
                ko.applyBindings(viewModel, $tip.get(0));
                $tip.find(".close-popover").click(hidePopover);
                if (options.minWidth) {
                  $(".popover:visible").css('min-width', options.minWidth)
                }
                $content.empty();
                $title.empty();
                $(document).on('click', hideOnClickOutside)
                visible = true;
              }
            }, $title.get(0), 'replaceChildren');
          }
        }, $content.get(0), 'replaceChildren');
      };

      if (clickTrigger) {
        $element.click(function (e) {
          if (visible) {
            hidePopover();
          } else {
            showPopover();
          }
          e.stopPropagation();
        });
      } else {
        $element.mouseenter(showPopover);
        $element.mouseleave(hidePopover);
      }
    }
  };

  ko.bindingHandlers.freshereditor = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var _el = $(element);
      var options = $.extend(valueAccessor(), {});
      _el.html(options.data());
      _el.freshereditor({
        excludes: ['strikethrough', 'removeFormat', 'insertorderedlist', 'justifyfull', 'insertheading1', 'insertheading2', 'superscript', 'subscript']
      });
      _el.freshereditor("edit", true);
      _el.on("mouseup", function () {
        storeSelection();
        updateValues();
      });

      var sourceDelay = -1;
      _el.on("keyup", function () {
        clearTimeout(sourceDelay);
        storeSelection();
        sourceDelay = setTimeout(function () {
          updateValues();
        }, 100);
      });

      $(".chosen-select").chosen({
        disable_search_threshold: 10,
        width: "75%"
      });

      $(document).on("addFieldToVisual", function (e, field) {
        _el.focus();
        pasteHtmlAtCaret("{{" + field.name() + "}}");
      });

      $(document).on("addFunctionToVisual", function (e, fn) {
        _el.focus();
        pasteHtmlAtCaret(fn);
      });

      function updateValues() {
        $("[data-template]")[0].editor.setValue(stripHtmlFromFunctions(_el.html()));
        valueAccessor().data(_el.html());
      }

      function storeSelection() {
        if (window.getSelection) {
          // IE9 and non-IE
          sel = window.getSelection();
          if (sel.getRangeAt && sel.rangeCount) {
            range = sel.getRangeAt(0);
            _el.data("range", range);
          }
        }
        else if (document.selection && document.selection.type != "Control") {
          // IE < 9
          _el.data("selection", document.selection);
        }
      }

      function pasteHtmlAtCaret(html) {
        var sel, range;
        if (window.getSelection) {
          // IE9 and non-IE
          sel = window.getSelection();
          if (sel.getRangeAt && sel.rangeCount) {
            if (_el.data("range")) {
              range = _el.data("range");
            }
            else {
              range = sel.getRangeAt(0);
            }
            range.deleteContents();

            // Range.createContextualFragment() would be useful here but is
            // non-standard and not supported in all browsers (IE9, for one)
            var el = document.createElement("div");
            el.innerHTML = html;
            var frag = document.createDocumentFragment(), node, lastNode;
            while ((node = el.firstChild)) {
              lastNode = frag.appendChild(node);
            }
            range.insertNode(frag);

            // Preserve the selection
            if (lastNode) {
              range = range.cloneRange();
              range.setStartAfter(lastNode);
              range.collapse(true);
              sel.removeAllRanges();
              sel.addRange(range);
            }
          }
        } else if (document.selection && document.selection.type != "Control") {
          // IE < 9
          if (_el.data("selection")) {
            _el.data("selection").createRange().pasteHTML(html);
          }
          else {
            document.selection.createRange().pasteHTML(html);
          }
        }
      }
    }
  };

  ko.bindingHandlers.slider = {
    init: function (element, valueAccessor) {
      var _el = $(element);
      var _options = $.extend(valueAccessor(), {});
      _el.slider({
        min: !isNaN(parseFloat(_options.start())) ? parseFloat(_options.start()) : 0,
        max: !isNaN(parseFloat(_options.end())) ? parseFloat(_options.end()) : 10,
        step: !isNaN(parseFloat(_options.gap())) ? parseFloat(_options.gap()) : 1,
        handle: _options.handle ? _options.handle : 'triangle',
        start: parseFloat(_options.min()),
        end: parseFloat(_options.max()),
        tooltip_split: true,
        tooltip: 'always',
        labels: _options.labels
      });
      _el.on("slide", function (e) {
        _options.start(e.min);
        _options.end(e.max);
        _options.min(e.start);
        _options.max(e.end);
        if (_options.min() < _options.start()){
          _options.start(_options.min());
        }
        if (_options.max() > _options.end()){
          _options.end(_options.max());
        }
        _options.gap(e.step);
        if (typeof _options.properties.initial_start == "function"){
          _options.properties.start(_options.properties.initial_start());
          _options.properties.end(_options.properties.initial_end());
          _options.properties.gap(_options.properties.initial_gap());
        }
      });
      _el.on("slideStop", function (e) {
        viewModel.search();
      });
    },
    update: function (element, valueAccessor) {
      var _options = $.extend(valueAccessor(), {});
    }
  }

  ko.bindingHandlers.daterangepicker = {
    INTERVAL_OPTIONS: [
      {
        value: "+200MILLISECONDS",
        label: "200ms"
      },
      {
        value: "+1SECONDS",
        label: "1s"
      },
      {
        value: "+5SECONDS",
        label: "5s"
      },
      {
        value: "+30SECONDS",
        label: "30s"
      },
      {
        value: "+1MINUTES",
        label: "1m"
      },
      {
        value: "+5MINUTES",
        label: "5m"
      },
      {
        value: "+10MINUTES",
        label: "10m"
      },
      {
        value: "+30MINUTES",
        label: "30m"
      },
      {
        value: "+1HOURS",
        label: "1h"
      },
      {
        value: "+3HOURS",
        label: "3h"
      },
      {
        value: "+6HOURS",
        label: "6h"
      },
      {
        value: "+12HOURS",
        label: "12h"
      },
      {
        value: "+1DAYS",
        label: "1d"
      },
      {
        value: "+7DAYS",
        label: "7d"
      },
      {
        value: "+1MONTHS",
        label: "1M"
      },
      {
        value: "+6MONTHS",
        label: "6M"
      },
      {
        value: "+1YEARS",
        label: "1y"
      },
      {
        value: "+10YEARS",
        label: "10y"
      }
    ],
    EXTRA_INTERVAL_OPTIONS: [],

    init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
      var DATE_FORMAT = "YYYY-MM-DD";
      var TIME_FORMAT = "HH:mm:ss";
      var DATETIME_FORMAT = DATE_FORMAT + " " + TIME_FORMAT;

      var _el = $(element);
      var _options = $.extend(valueAccessor(), {});

      var _intervalOptions = [];
      ko.bindingHandlers.daterangepicker.INTERVAL_OPTIONS.forEach(function (interval) {
        _intervalOptions.push('<option value="' + interval.value + '">' + interval.label + '</option>');
      });

      function enableOptions() {
        var _opts = [];
        var _tmp = $("<div>").html(_intervalOptions.join(""))
        $.each(arguments, function (cnt, item) {
          if (_tmp.find("option[value='+" + item + "']").length > 0) {
            _opts.push('<option value="+' + item + '">' + _tmp.find("option[value='+" + item + "']").eq(0).text() + '</option>');
          }
        });
        return _opts;
      }

      function renderOptions(opts) {
        var _html = "";
        for (var i = 0; i < opts.length; i++) {
          _html += opts[i];
        }
        return _html;
      }

      var _tmpl = $('<div class="simpledaterangepicker">' +
              '<div class="facet-field-cnt custom">' +
              '<div class="facet-field-label facet-field-label-fixed-width"></div>' +
              '<div class="facet-field-switch"><i class="fa fa-calendar muted"></i> <a href="javascript:void(0)">' + KO_DATERANGEPICKER_LABELS.DATE_PICKERS + '</a></div>' +
              '</div>' +
              '<div class="facet-field-cnt picker">' +
              '<div class="facet-field-label facet-field-label-fixed-width"></div>' +
              '<div class="facet-field-switch"><i class="fa fa-calendar-o muted"></i> <a href="javascript:void(0)">' + KO_DATERANGEPICKER_LABELS.CUSTOM_FORMAT + '</a></div>' +
              '</div>' +
              '<div class="facet-field-cnt picker">' +
              '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.START + '</div>' +
              '<div class="input-prepend input-group">' +
              '<span class="add-on input-group-addon"><i class="fa fa-calendar"></i></span>' +
              '<input type="text" class="input-small form-control start-date" />' +
              '</div>' +
              '<div class="input-prepend input-group left-margin">' +
              '<span class="add-on input-group-addon"><i class="fa fa-clock-o"></i></span>' +
              '<input type="text" class="input-mini form-control start-time" />' +
              '</div>' +
              '</div>' +
              '<div class="facet-field-cnt picker">' +
              '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.END + '</div>' +
              '<div class="input-prepend input-group">' +
              '<span class="add-on input-group-addon"><i class="fa fa-calendar"></i></span>' +
              '<input type="text" class="input-small form-control end-date" />' +
              '</div>' +
              '<div class="input-prepend input-group left-margin">' +
              '<span class="add-on input-group-addon"><i class="fa fa-clock-o"></i></span>' +
              '<input type="text" class="input-mini form-control end-time" />' +
              '</div>' +
              '</div>' +
              '<div class="facet-field-cnt picker">' +
              '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.INTERVAL + '</div>' +
              '<div class="input-prepend input-group"><span class="add-on input-group-addon"><i class="fa fa-repeat"></i></span></div>&nbsp;' +
              '<select class="input-small interval-select" style="margin-right: 6px">' +
              renderOptions(_intervalOptions) +
              '</select>' +
              '<input class="input interval hide" type="hidden" value="" />' +
              '</div>' +
              '<div class="facet-field-cnt custom">' +
              '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.START + '</div>' +
              '<div class="input-prepend input-group">' +
              '<span class="add-on input-group-addon"><i class="fa fa-calendar-o"></i></span>' +
              '<input type="text" class="input-large form-control start-date-custom" />' +
              '</div>' +
              '<span class="pointer custom-popover" data-trigger="click" data-toggle="popover" data-placement="right" rel="popover" data-html="true"' +
              '       title="' + KO_DATERANGEPICKER_LABELS.CUSTOM_POPOVER_TITLE + '"' +
              '       data-content="' + KO_DATERANGEPICKER_LABELS.CUSTOM_POPOVER_CONTENT + '">' +
              '&nbsp;&nbsp;<i class="fa fa-question-circle"></i>' +
              ' </span>' +
              '</div>' +
              '<div class="facet-field-cnt custom">' +
              '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.END + '</div>' +
              '<div class="input-prepend input-group">' +
              '<span class="add-on input-group-addon"><i class="fa fa-calendar-o"></i></span>' +
              '<input type="text" class="input-large form-control end-date-custom" />' +
              '</div>' +
              '</div>' +
              '<div class="facet-field-cnt custom">' +
              '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.INTERVAL + '</div>' +
              '<div class="input-prepend input-group">' +
              '<span class="add-on input-group-addon"><i class="fa fa-repeat"></i></span>' +
              '<input type="text" class="input-large form-control interval-custom" />' +
              '</div>' +
              '</div>' +


              '</div>'
      );

      _tmpl.insertAfter(_el);

      $(".custom-popover").popover();

      var _minMoment = moment(_options.min());
      var _maxMoment = moment(_options.max());

      if (_minMoment.isValid() && _maxMoment.isValid()) {
        _tmpl.find(".facet-field-cnt.custom").hide();
        _tmpl.find(".facet-field-cnt.picker").show();
        _tmpl.find(".start-date").val(_minMoment.utc().format(DATE_FORMAT));
        _tmpl.find(".start-time").val(_minMoment.utc().format(TIME_FORMAT));
        _tmpl.find(".end-date").val(_maxMoment.utc().format(DATE_FORMAT));
        _tmpl.find(".end-time").val(_maxMoment.utc().format(TIME_FORMAT));
        _tmpl.find(".interval").val(_options.gap());
        _tmpl.find(".interval-select").val(_options.gap());
        _tmpl.find(".interval-custom").val(_options.gap());
        if (_tmpl.find(".interval-select").val() == null || ko.bindingHandlers.daterangepicker.EXTRA_INTERVAL_OPTIONS.indexOf(_tmpl.find(".interval-select").val()) > -1) {
          pushIntervalValue(_options.gap());
          _tmpl.find(".facet-field-cnt.custom").show();
          _tmpl.find(".facet-field-cnt.picker").hide();
        }
      }
      else {
        _tmpl.find(".facet-field-cnt.custom").show();
        _tmpl.find(".facet-field-cnt.picker").hide();
        _tmpl.find(".start-date-custom").val(_options.min());
        _tmpl.find(".end-date-custom").val(_options.max());
        _tmpl.find(".interval-custom").val(_options.gap());
        pushIntervalValue(_options.gap());
      }

      if (typeof _options.relatedgap != "undefined"){
        pushIntervalValue(_options.relatedgap());
      }

      _tmpl.find(".start-date").datepicker({
        format: DATE_FORMAT.toLowerCase()
      }).on("changeDate", function () {
        rangeHandler(true);
      });

      _tmpl.find(".start-date").on("change", function () {
        rangeHandler(true);
      });

      _tmpl.find(".start-time").timepicker({
        minuteStep: 1,
        showSeconds: true,
        showMeridian: false,
        defaultTime: false
      });

      _tmpl.find(".end-date").datepicker({
        format: DATE_FORMAT.toLowerCase()
      }).on("changeDate", function () {
        rangeHandler(false);
      });

      _tmpl.find(".end-date").on("change", function () {
        rangeHandler(true);
      });

      _tmpl.find(".end-time").timepicker({
        minuteStep: 1,
        showSeconds: true,
        showMeridian: false,
        defaultTime: false
      });

      _tmpl.find(".start-time").on("change", function () {
        // the timepicker plugin doesn't have a change event handler
        // so we need to wait a bit to handle in with the default field event
        window.setTimeout(function () {
          rangeHandler(true)
        }, 200);
      });

      _tmpl.find(".end-time").on("change", function () {
        window.setTimeout(function () {
          rangeHandler(false)
        }, 200);
      });

      if (_minMoment.isValid() && _maxMoment.isValid()) {
        rangeHandler(true);
      }

      _tmpl.find(".facet-field-cnt.picker .facet-field-switch a").on("click", function () {
        _tmpl.find(".facet-field-cnt.custom").show();
        _tmpl.find(".facet-field-cnt.picker").hide();
      });

      _tmpl.find(".facet-field-cnt.custom .facet-field-switch a").on("click", function () {
        _tmpl.find(".facet-field-cnt.custom").hide();
        _tmpl.find(".facet-field-cnt.picker").show();
      });

      _tmpl.find(".start-date-custom").on("change", function () {
        _options.min(_tmpl.find(".start-date-custom").val());
        _tmpl.find(".start-date").val(moment(_options.min()).utc().format(DATE_FORMAT));
        _tmpl.find(".start-time").val(moment(_options.min()).utc().format(TIME_FORMAT));
        _options.start(_options.min());
      });

      _tmpl.find(".end-date-custom").on("change", function () {
        _options.max(_tmpl.find(".end-date-custom").val());
        _tmpl.find(".end-date").val(moment(_options.max()).utc().format(DATE_FORMAT));
        _tmpl.find(".end-time").val(moment(_options.max()).utc().format(TIME_FORMAT));
        _options.end(_options.max());
      });

      _tmpl.find(".interval-custom").on("change", function () {
        _options.gap(_tmpl.find(".interval-custom").val());
        matchIntervals(true);
        if (typeof _options.relatedgap != "undefined"){
          _options.relatedgap(_options.gap());
        }
      });

      function pushIntervalValue(newValue) {
        var _found = false;
        ko.bindingHandlers.daterangepicker.INTERVAL_OPTIONS.forEach(function(interval) {
          if (interval.value == newValue){
            _found = true;
          }
        });
        if (!_found){
          ko.bindingHandlers.daterangepicker.INTERVAL_OPTIONS.push({
            value: newValue,
            label: newValue
          });
          ko.bindingHandlers.daterangepicker.EXTRA_INTERVAL_OPTIONS.push(newValue);
          _intervalOptions.push('<option value="' + newValue + '">' + newValue + '</option>');
        }
      }

      function matchIntervals(fromCustom) {
        _tmpl.find(".interval-select").val(_options.gap());
        if (_tmpl.find(".interval-select").val() == null) {
          if (fromCustom){
            pushIntervalValue(_options.gap());
            if (bindingContext.$root.intervalOptions){
              bindingContext.$root.intervalOptions(ko.bindingHandlers.daterangepicker.INTERVAL_OPTIONS);
            }
          }
          else {
            _tmpl.find(".interval-select").val(_tmpl.find(".interval-select option:first").val());
            _options.gap(_tmpl.find(".interval-select").val());
            if (typeof _options.relatedgap != "undefined"){
              _options.relatedgap(_options.gap());
            }
            _tmpl.find(".interval-custom").val(_options.gap());
          }
        }
      }

      _tmpl.find(".interval-select").on("change", function () {
        _options.gap(_tmpl.find(".interval-select").val());
        if (typeof _options.relatedgap != "undefined"){
          _options.relatedgap(_options.gap());
        }
        _tmpl.find(".interval").val(_options.gap());
        _tmpl.find(".interval-custom").val(_options.gap());
      });

      function rangeHandler(isStart) {
        var startDate = moment(_tmpl.find(".start-date").val() + " " + _tmpl.find(".start-time").val(), DATETIME_FORMAT);
        var endDate = moment(_tmpl.find(".end-date").val() + " " + _tmpl.find(".end-time").val(), DATETIME_FORMAT);
        if (startDate.valueOf() > endDate.valueOf()) {
          if (isStart) {
            _tmpl.find(".end-date").val(startDate.utc().format(DATE_FORMAT));
            _tmpl.find(".end-date").datepicker('setValue', startDate.utc().format(DATE_FORMAT));
            _tmpl.find(".end-date").data("original-val", _tmpl.find(".end-date").val());
            _tmpl.find(".end-time").val(startDate.utc().format(TIME_FORMAT));
          }
          else {
            if (_tmpl.find(".end-date").val() == _tmpl.find(".start-date").val()) {
              _tmpl.find(".end-time").val(startDate.utc().format(TIME_FORMAT));
              _tmpl.find(".end-time").data("timepicker").setValues(startDate.format(TIME_FORMAT));
            }
            else {
              _tmpl.find(".end-date").val(_tmpl.find(".end-date").data("original-val"));
              _tmpl.find(".end-date").datepicker("setValue", _tmpl.find(".end-date").data("original-val"));
            }
            // non-sticky error notification
            $.jHueNotify.notify({
              level: "ERROR",
              message: "The end cannot be before the starting moment"
            });
          }
        }
        else {
          _tmpl.find(".end-date").data("original-val", _tmpl.find(".end-date").val());
          _tmpl.find(".start-date").datepicker("hide");
          _tmpl.find(".end-date").datepicker("hide");
        }

        var _calculatedStartDate = moment(_tmpl.find(".start-date").val() + " " + _tmpl.find(".start-time").val(), DATETIME_FORMAT);
        var _calculatedEndDate = moment(_tmpl.find(".end-date").val() + " " + _tmpl.find(".end-time").val(), DATETIME_FORMAT);

        _options.min(_calculatedStartDate.format("YYYY-MM-DD[T]HH:mm:ss[Z]"));
        _options.start(_options.min());
        _options.max(_calculatedEndDate.format("YYYY-MM-DD[T]HH:mm:ss[Z]"));
        _options.end(_options.max());

        _tmpl.find(".start-date-custom").val(_options.min());
        _tmpl.find(".end-date-custom").val(_options.max());

        var _opts = [];
        // hide not useful options from interval
        if (_calculatedEndDate.diff(_calculatedStartDate, 'minutes') > 1 && _calculatedEndDate.diff(_calculatedStartDate, 'minutes') <= 60) {
          _opts = enableOptions("200MILLISECONDS", "1SECONDS", "1MINUTES", "5MINUTES", "10MINUTES", "30MINUTES");
        }
        if (_calculatedEndDate.diff(_calculatedStartDate, 'hours') > 1 && _calculatedEndDate.diff(_calculatedStartDate, 'hours') <= 12) {
          _opts = enableOptions("5MINUTES", "10MINUTES", "30MINUTES", "1HOURS", "3HOURS");
        }
        if (_calculatedEndDate.diff(_calculatedStartDate, 'hours') > 12 && _calculatedEndDate.diff(_calculatedStartDate, 'hours') < 36) {
          _opts = enableOptions("10MINUTES", "30MINUTES", "1HOURS", "3HOURS", "6HOURS", "12HOURS");
        }
        if (_calculatedEndDate.diff(_calculatedStartDate, 'days') > 1 && _calculatedEndDate.diff(_calculatedStartDate, 'days') <= 7) {
          _opts = enableOptions("30MINUTES", "1HOURS", "3HOURS", "6HOURS", "12HOURS", "1DAYS");
        }
        if (_calculatedEndDate.diff(_calculatedStartDate, 'days') > 7 && _calculatedEndDate.diff(_calculatedStartDate, 'days') <= 14) {
          _opts = enableOptions("3HOURS", "6HOURS", "12HOURS", "1DAYS");
        }
        if (_calculatedEndDate.diff(_calculatedStartDate, 'days') > 14 && _calculatedEndDate.diff(_calculatedStartDate, 'days') <= 31) {
          _opts = enableOptions("12HOURS", "1DAYS", "7DAYS");
        }
        if (_calculatedEndDate.diff(_calculatedStartDate, 'months') >= 1) {
          _opts = enableOptions("1DAYS", "7DAYS", "1MONTHS");
        }
        if (_calculatedEndDate.diff(_calculatedStartDate, 'months') > 6) {
          _opts = enableOptions("1DAYS", "7DAYS", "1MONTHS", "6MONTHS");
        }
        if (_calculatedEndDate.diff(_calculatedStartDate, 'months') > 12) {
          _opts = enableOptions("7DAYS", "1MONTHS", "6MONTHS", "1YEARS", "10YEARS");
        }

        $(".interval-select").html(renderOptions(_opts));

        matchIntervals(true);
      }
    }
  };

  ko.bindingHandlers.stretchDown = {
    init: function (element) {
      var $element = $(element);
      var $parent = $element.parent();

      var lastParentHeight = -1;
      var lastTop = -1;

      function stretch(force) {
        if (lastParentHeight !== $parent.innerHeight() || lastTop !== $element.position().top || force) {
          lastParentHeight = $parent.innerHeight();
          lastTop = $element.position().top;
          $element.height(lastParentHeight - lastTop - ($element.outerHeight(true) - $element.innerHeight()));
          huePubSub.publish('assist.stretchDown', $element);
        }
      }

      window.setInterval(stretch, 200);
      huePubSub.subscribe('assist.forceStretchDown', function(){
        stretch(true);
      });
    }
  };

  ko.bindingHandlers.assistVerticalResizer = {
    init: function (element, valueAccessor) {
      var $container = $(element);
      var options = ko.unwrap(valueAccessor());
      var panelDefinitions = options.panels;

      var timeout = -1;
      var checkForElements = function () {
        var $allPanels = $container.children('.assist-inner-panel');
        var $allExtras = $container.children('.assist-fixed-height');
        if (panelDefinitions().length == $allPanels.length && ($allExtras.length > 0 || options.noFixedHeights)) {
          ko.bindingHandlers.assistVerticalResizer.updateWhenRendered(element, valueAccessor);
        } else {
          timeout = window.setTimeout(checkForElements, 10);
        }
      };

      checkForElements();
      panelDefinitions.subscribe(function () {
        timeout = window.setTimeout(checkForElements, 10);
      })
    },

    updateWhenRendered: function (element, valueAccessor) {
      var self = this;
      var options = ko.unwrap(valueAccessor());
      var apiHelper = options.apiHelper;
      var panelDefinitions = options.panels;

      var $container = $(element);
      var $allPanels = $container.children('.assist-inner-panel');
      var $allResizers = $container.children(".assist-resizer");
      var $allExtras = $container.children('.assist-fixed-height');

      var allExtrasHeight = 0;
      $allExtras.each(function (idx, extra) {
        allExtrasHeight += $(extra).outerHeight(true);
      });

      window.clearInterval($container.data('height_interval'));

      if (panelDefinitions().length === 0) {
        $allExtras.show();
        return;
      }
      if (panelDefinitions().length === 1) {
        var adjustHeightSingle = function () {
          $allPanels.height($container.innerHeight() - allExtrasHeight);
        };

        var heightAdjustInterval = window.setInterval(adjustHeightSingle, 800);
        adjustHeightSingle();
        $container.data('height_interval', heightAdjustInterval);

        $(window).resize(adjustHeightSingle);
        huePubSub.subscribe('assist.forceRender', function () {
          window.setTimeout(adjustHeightSingle, 200);
        });
        $allExtras.show();
        $allPanels.show();
        return;
      }

      var panelRatios = apiHelper.getFromTotalStorage('assist', 'innerPanelRatios', {});

      var totalRatios = 0;
      $.each($allPanels, function (idx, panel) {
        var panelDef = panelDefinitions()[idx];
        if (!panelRatios[panelDef.type]) {
          panelRatios[panelDef.type] = 1 / panelDefinitions().length;
        }
        totalRatios += panelRatios[panelDef.type];
        $(panel).data('minHeight', panelDef.minHeight);
      });

      // Normalize the ratios in case new panels were added or removed.
      if (totalRatios !== 1) {
        var diff = 1 / totalRatios;
        $.each(panelDefinitions(), function (idx, panel) {
          panelRatios[panel.type] = panelRatios[panel.type] * diff;
        });
      }

      var totalHeight = -1;
      var containerTop = $container.offset().top;

      // Resizes all containers according to the set ratios
      var resizeByRatio = function () {
        if (totalHeight == $container.innerHeight()) {
          return;
        }
        $allPanels = $container.children('.assist-inner-panel');
        totalHeight = $container.innerHeight();
        containerTop = $container.offset().top;

        $.each($allPanels, function (idx, panel) {
          var panelDef = panelDefinitions()[idx];
          if (!panelRatios[panelDef.type] || $allPanels.length == 1) {
            panelRatios[panelDef.type] = 1 / panelDefinitions().length;
          }
          totalRatios += panelRatios[panelDef.type];
          $(panel).data('minHeight', panelDef.minHeight);
        });

        var availableForPanels = totalHeight - allExtrasHeight;
        var leftoverSpace = 0;
        $allPanels.each(function (idx, panel) {
          var $panel = $(panel);
          var desiredHeight = availableForPanels * panelRatios[panelDefinitions()[idx].type];
          var newHeight = Math.max($panel.data('minHeight'), desiredHeight);
          $panel.height(newHeight);
          leftoverSpace += newHeight - desiredHeight;
        });
        // The minheight is greater than the ratio so we shrink where possible
        if (leftoverSpace > 0) {
          $allPanels.each(function (idx, panel) {
            if (leftoverSpace === 0) {
              return false;
            }
            var $panel = $(panel);
            var currentHeight = $panel.height();
            var possibleContribution = Math.min(currentHeight - $panel.data('minHeight'), leftoverSpace);
            if (possibleContribution > 0) {
              $panel.height(currentHeight - possibleContribution);
              leftoverSpace -= possibleContribution;
            }
          });
        }
        if ($.fn.niceScroll) {
          $('.assist-flex-fill').getNiceScroll().resize();
        }
      };

      resizeByRatio();
      $(window).resize(resizeByRatio);

      window.setTimeout(resizeByRatio, 1000);
      huePubSub.subscribe('assist.forceRender', function () {
        window.setTimeout(resizeByRatio, 200);
      });

      $allExtras.show();
      $allPanels.show();

      var fitPanelHeights = function ($panelsToResize, desiredTotalHeight) {
        var currentHeightOfPanels = 0;

        var noMoreSpace = true;
        $panelsToResize.each(function (idx, panel) {
          var $panel = $(panel);
          var panelHeight = $panel.outerHeight(true);
          noMoreSpace = noMoreSpace && panelHeight <= $panel.data('minHeight');
          currentHeightOfPanels += panelHeight;
        });

        var distanceToGo = desiredTotalHeight - currentHeightOfPanels;
        if (noMoreSpace && distanceToGo < 0) {
          return;
        }

        // Add all to the first panel if expanding (distanceToGo is positive
        if (distanceToGo >= 0) {
          $panelsToResize.first().height($panelsToResize.first().height() + distanceToGo + 'px');
          return;
        }

        // Remove as much as possible on each panel if shrinking (distanceToGo is negative)
        $panelsToResize.each(function (idx, panel) {
          var $panel = $(panel);
          var initialHeight = $panel.height();
          var newHeight = Math.max($panel.data('minHeight'), initialHeight + distanceToGo);
          if (initialHeight == newHeight) {
            return true;
          }
          $panel.height(newHeight);
          distanceToGo += initialHeight - newHeight;
          if (distanceToGo >= 0) {
            return false;
          }
        });
      };

      $allResizers.each(function (idx, resizer) {
        var $resizer = $(resizer);
        var extrasBeforeHeight = 0;
        $resizer.prevAll('.assist-fixed-height').each(function (idx, extra) {
          extrasBeforeHeight += $(extra).outerHeight(true);
        });
        var $panelsBefore = $resizer.prevAll('.assist-inner-panel');
        var limitBefore = extrasBeforeHeight;
        $panelsBefore.each(function (idx, panel) {
          limitBefore += $(panel).data('minHeight');
        });

        var extrasAfterHeight = allExtrasHeight - extrasBeforeHeight;
        var $panelsAfter = $resizer.nextAll('.assist-inner-panel');
        var requiredSpaceAfter = extrasAfterHeight;
        $panelsAfter.each(function (idx, panel) {
          requiredSpaceAfter += $(panel).data('minHeight');
        });

        $resizer.draggable({
          axis: "y",
          drag: function (event, ui) {
            var limitAfter = totalHeight - requiredSpaceAfter;
            var position = ui.offset.top - containerTop;
            if (position > limitBefore && position < limitAfter) {
              fitPanelHeights($panelsBefore, position - extrasBeforeHeight);
              fitPanelHeights($panelsAfter, totalHeight - extrasAfterHeight - position);
            } else if (position > limitAfter) {
              fitPanelHeights($panelsBefore, limitAfter - extrasBeforeHeight);
              fitPanelHeights($panelsAfter, totalHeight - extrasAfterHeight - limitAfter);
            } else if (position < limitBefore) {
              fitPanelHeights($panelsBefore, limitBefore - extrasBeforeHeight);
              fitPanelHeights($panelsAfter, totalHeight - extrasAfterHeight - limitBefore);
            }

            ui.offset.top = 0;
            ui.position.top = 0;
          },
          stop: function (event, ui) {
            ui.offset.top = 0;
            ui.position.top = 0;
            var totalHeightForPanels = 0;
            $allPanels.each(function (idx, panel) {
              totalHeightForPanels += $(panel).outerHeight(true);
            });
            $allPanels.each(function (idx, panel) {
              panelRatios[panelDefinitions()[idx].type] = $(panel).outerHeight(true) / totalHeightForPanels;
            });
            apiHelper.setInTotalStorage('assist', 'innerPanelRatios', panelRatios);
            if ($.fn.niceScroll) {
              $('.assist-flex-fill').getNiceScroll().resize();
            }
          }
        });
      });
    }
  };

  ko.bindingHandlers.aceResizer = {
    init: function (element, valueAccessor) {
      var options = ko.unwrap(valueAccessor());
      var ace = options.ace;
      var $target = $(options.target);
      var $resizer = $(element);
      var $contentPanel = $(".content-panel");
      var $execStatus = $resizer.prev('.snippet-execution-status');

      var lastEditorSize = $.totalStorage('hue.editor.editor.size') || 131;
      var editorHeight = Math.floor(lastEditorSize / 16);
      $target.height(lastEditorSize);
      var autoExpand = true;

      function throttleChange() {
        if (autoExpand) {
          var maxAutoLines = Math.floor((($(window).height() - 80) / 2) / 16);
          var resized = false;
          if (ace().session.getLength() > editorHeight) {
            if (ace().session.getLength() < maxAutoLines) {
              $target.height(ace().session.getLength() * 16);
            }
            else {
              $target.height(maxAutoLines * 16); // height of maxAutoLines
            }
            resized = true;
          }
          else if (ace().session.getLength() > 8) {
            $target.height((ace().session.getLength()) * 16);
            resized = true;
          }
          else {
            $target.height(8 * 16);
            resized = true;
          }
          if (ace().session.getLength() == editorHeight) {
            resized = false;
          }
          if (resized) {
            ace().resize();
            editorHeight = Math.min(maxAutoLines, ace().session.getLength());
            huePubSub.publish('redraw.fixed.headers');
          }
        }
      }

      var changeTimeout = -1;
      ace().on('change', function () {
        window.clearTimeout(changeTimeout);
        changeTimeout = window.setTimeout(throttleChange, 10)
      });

      $resizer.draggable({
        axis: "y",
        start: options.onStart ? options.onStart : function(){},
        drag: function (event, ui) {
          autoExpand = false;
          var currentHeight = ui.offset.top + $contentPanel.scrollTop() - (125 + $execStatus.outerHeight(true));
          $target.css("height", currentHeight + "px");
          ace().resize();
          ui.offset.top = 0;
          ui.position.top = 0;
        },
        stop: function (event, ui) {
          ui.offset.top = 0;
          ui.position.top = 0;
          $.totalStorage('hue.editor.editor.size', $target.height());
          huePubSub.publish('redraw.fixed.headers');
          $(document).trigger("editorSizeChanged");
        }
      });
    }
  };

  ko.bindingHandlers.logResizer = {
    init: function (element, valueAccessor) {
      var options = ko.unwrap(valueAccessor()),
        $resizer = $(element),
        $parent = $resizer.parents(options.parent),
        $target = $parent.find(options.target),
        onStart = options.onStart,
        onResize = options.onResize;

      var initialHeight = $.totalStorage('hue.editor.logs.size') || 80;

      window.setTimeout(function () {
        $target.css("height", initialHeight + "px");
      }, 0);

      $resizer.draggable({
        axis: "y",
        start: function (event, ui) {
          if (onStart) {
            onStart();
          }
        },
        drag: function (event, ui) {
          var currentHeight = ui.offset.top - $target.offset().top - 20;
          $.totalStorage('hue.editor.logs.size', currentHeight);
          $target.css("height", currentHeight + "px");
          ui.offset.top = 0;
          ui.position.top = 0;
        },
        stop: function (event, ui) {
          ui.offset.top = 0;
          ui.position.top = 0;
          if (onResize) {
            onResize();
          }
        }
      });
    }
  };

  ko.bindingHandlers.splitFlexDraggable = {
    init: function (element, valueAccessor) {
      var options = ko.unwrap(valueAccessor());
      var sidePanelWidth = $.totalStorage(options.appName + '_' + options.orientation + '_panel_width') != null ? $.totalStorage(options.appName + '_' + options.orientation + '_panel_width') : 290;

      var $resizer = $(element);
      var $sidePanel = $(options.sidePanelSelector);
      var $container = $(options.containerSelector);

      var isLeft = options.orientation === 'left';

      var onPosition = options.onPosition || function() {};

      $sidePanel.css('flex-basis', sidePanelWidth + 'px');
      $resizer.draggable({
        axis: 'x',
        containment: $container,
        start: function () {
          sidePanelWidth = $sidePanel.width();
        },
        drag: function (event, ui) {
          if (isLeft) {
            $sidePanel.css('flex-basis', Math.max(sidePanelWidth + ui.position.left, 200) + 'px');
          } else {
            $sidePanel.css('flex-basis', Math.max(sidePanelWidth - ui.position.left, 200) + 'px');
          }
          onPosition();
          ui.position.left = 0;
        },
        stop: function () {
          sidePanelWidth = $sidePanel.width();
          $.totalStorage(options.appName + '_' + options.orientation + '_panel_width', sidePanelWidth);
          window.setTimeout(positionPanels, 100);
          huePubSub.publish('split.panel.resized');
        }
      });

      var positionPanels = function () {
        if (options.sidePanelVisible()) {
          $sidePanel.css('width',  Math.max(sidePanelWidth, 200) + 'px');
          onPosition();
        }
      };

      options.sidePanelVisible.subscribe(positionPanels);

      var positionTimeout = -1;
      $(window).resize(function() {
        window.clearTimeout(positionTimeout);
        positionTimeout = window.setTimeout(function () {
          positionPanels()
        }, 1);
      });

      function initialPositioning() {
        if(! $container.is(':visible') && ! $sidePanel.is(':visible')) {
          window.setTimeout(initialPositioning, 50);
        } else {
          positionPanels();
          // Even though the container is visible some slow browsers might not
          // have rendered the panels
          window.setTimeout(positionPanels, 50);
        }
      }
      initialPositioning();
    }
  };

  ko.bindingHandlers.splitDraggable = {
    init: function (element, valueAccessor) {
      var options = ko.unwrap(valueAccessor());
      var leftPanelWidth = $.totalStorage(options.appName + "_left_panel_width") != null ? Math.max($.totalStorage(options.appName + "_left_panel_width"), 250) : 250;
      var rightPanelWidth = $.totalStorage(options.appName + "_right_panel_width") != null ? Math.max($.totalStorage(options.appName + "_right_panel_width"), 250) : 290;

      var containerSelector = options.containerSelector || ".panel-container";
      var contentPanelSelector = options.contentPanelSelector || ".content-panel";

      var onPosition = options.onPosition || function() {};

      var hasLeftPanel = !!options.leftPanelVisible;
      var hasRightPanel = !!options.rightPanelVisible;

      var isRightPanel = !!options.isRightPanel;

      var $resizer = $(element);
      var $leftPanel = $('.left-panel');
      var $rightPanel = $('.right-panel');
      var $contentPanel = $(contentPanelSelector);
      var $container = $(containerSelector);

      var positionPanels = function () {
        if (isRightPanel) {
          var oppositeWidth = hasLeftPanel && ko.unwrap(options.leftPanelVisible) ? $leftPanel.width() + $resizer.width() : 0;
          var totalWidth = $container.width() - oppositeWidth;
          if (ko.unwrap(options.rightPanelVisible)) {
            $resizer.show();
            rightPanelWidth = Math.min(rightPanelWidth, $container.width() - 100);
            var contentPanelWidth = totalWidth - rightPanelWidth - $resizer.width();
            $rightPanel.css("width", rightPanelWidth + "px");
            $contentPanel.css("width", contentPanelWidth + "px");
            $resizer.css("right", rightPanelWidth + $resizer.width() + "px");
            $contentPanel.css("right", rightPanelWidth + $resizer.width() + "px");
          } else {
            if (oppositeWidth === 0) {
              $contentPanel.css("width", "100%");
            } else {
              $contentPanel.css("width", totalWidth);
            }
            $contentPanel.css("right", "0");
            $resizer.hide();
          }
        } else {
          var oppositeWidth = hasRightPanel && ko.unwrap(options.rightPanelVisible) ? $rightPanel.width() + $resizer.width() : 0;
          var totalWidth = $container.width() - oppositeWidth;
          if (ko.unwrap(options.leftPanelVisible)) {
            $resizer.show();
            leftPanelWidth = Math.min(leftPanelWidth, totalWidth - 100);
            var contentPanelWidth = totalWidth - leftPanelWidth - $resizer.width();
            $leftPanel.css("width", leftPanelWidth + "px");
            $contentPanel.css("width", contentPanelWidth + "px");
            $resizer.css("left", leftPanelWidth + "px");
            $contentPanel.css("left", leftPanelWidth + $resizer.width() + "px");
          } else {
            if (oppositeWidth === 0) {
              $contentPanel.css("width", "100%");
            } else {
              $contentPanel.css("width", totalWidth);
            }
            $contentPanel.css("left", "0");
            $resizer.hide();
          }
        }
        onPosition();
      };

      if (ko.isObservable(options.leftPanelVisible)) {
        options.leftPanelVisible.subscribe(positionPanels);
      }

      if (ko.isObservable(options.rightPanelVisible)) {
        options.rightPanelVisible.subscribe(positionPanels);
      }

      var dragTimeout = -1;
      $resizer.draggable({
        axis: "x",
        containment: $container,
        drag: function (event, ui) {
          if (isRightPanel) {
            ui.position.left = Math.min($container.width() - 200, ui.position.left);
          } else {
            ui.position.left = Math.min($container.width() - $container.position().left - 200, Math.max(250, ui.position.left));
          }

          dragTimeout = window.setTimeout(function () {
            if (isRightPanel) {
              var oppositeWidth = hasLeftPanel && ko.unwrap(options.leftPanelVisible) ? $leftPanel.width() + $resizer.width() : 0;
              var totalWidth = $container.width() - oppositeWidth;
              rightPanelWidth = $container.width() - ui.position.left;
              $rightPanel.css("width", rightPanelWidth + "px");
              $contentPanel.css("width", totalWidth - rightPanelWidth + "px");
              // $contentPanel.css("right", rightPanelWidth + $resizer.width());
            } else {
              var oppositeWidth = hasRightPanel && ko.unwrap(options.rightPanelVisible) ? $rightPanel.width() + $resizer.width() : 0;
              var totalWidth = $container.width() - oppositeWidth;
              leftPanelWidth = ui.position.left;
              $leftPanel.css("width", leftPanelWidth + "px");
              $contentPanel.css("width", totalWidth - leftPanelWidth - $resizer.width() + "px");
              $contentPanel.css("left", leftPanelWidth + $resizer.width());
            }
            onPosition();
          }, 10);

        },
        stop: function () {
          if (isRightPanel) {
            $.totalStorage(options.appName + "_right_panel_width", rightPanelWidth);
          } else {
            $.totalStorage(options.appName + "_left_panel_width", leftPanelWidth);
          }
          window.setTimeout(positionPanels, 100);
          huePubSub.publish('split.panel.resized');
        }
      });


      var positionTimeout = -1;
      $(window).resize(function() {
        window.clearTimeout(positionTimeout);
        positionTimeout = window.setTimeout(function () {
          positionPanels()
        }, 1);
      });

      function initialPositioning() {
        if(! $container.is(":visible")) {
          window.setTimeout(initialPositioning, 50);
        } else {
          positionPanels();
          // Even though the container is visible some slow browsers might not
          // have rendered the panels
          window.setTimeout(positionPanels, 100);
        }
      }
      initialPositioning();
    }
  };

  ko.bindingHandlers.oneClickSelect = {
    init: function (element) {
      $(element).click(function() {
        if (document.selection) {
          var range = document.body.createTextRange();
          range.moveToElementText(element);
          range.select();
        } else if (window.getSelection) {
          var range = document.createRange();
          range.selectNode(element);
          window.getSelection().addRange(range);
        }
      });
    }
  };

  ko.bindingHandlers.augmenthtml = {
    render: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var _val = ko.unwrap(valueAccessor());
      var _enc = $("<span>").html(_val);
      if (_enc.find("style").length > 0) {
        var parser = new less.Parser();
        $(_enc.find("style")).each(function (cnt, item) {
          var _less = "#result-container {" + $(item).text() + "}";
          try {
            parser.parse(_less, function (err, tree) {
              $(item).text(tree.toCSS());
            });
          }
          catch (e) {
          }
        });
        $(element).html(_enc.html());
      }
      else {
        $(element).html(_val);
      }
    },
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      ko.bindingHandlers.augmenthtml.render(element, valueAccessor, allBindingsAccessor, viewModel);
    },
    update: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      ko.bindingHandlers.augmenthtml.render(element, valueAccessor, allBindingsAccessor, viewModel);
    }
  };

  ko.bindingHandlers.clearable = {
    after: ['textInput', 'value', 'valueUpdate'],
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var $element = $(element);

      var params = valueAccessor();
      var valueObservable = ko.isObservable(params) ? params : params.value;

      function tog(v) {
        return v ? "addClass" : "removeClass";
      }

      $element.addClass("clearable");
      $element[tog(valueObservable())]("x");

      $element.on("input", function () {
        $element[tog(this.value)]("x");
      }).on("mousemove", function (e) {
        $element[tog(this.offsetWidth - 18 < e.clientX - this.getBoundingClientRect().left)]("onX");
      })
      .on("click", function (e) {
        if (this.offsetWidth - 18 < e.clientX - this.getBoundingClientRect().left) {
          $element.removeClass("x onX").val("");
          valueObservable("");
          if (typeof params.onClear === 'function') {
            params.onClear();
          }
        }
      });

      if (!allBindingsAccessor()['textInput'] || !allBindingsAccessor()['value']) {
        $element.on("change", function () {
          valueObservable($element.val());
        }).on("blur", function () {
          valueObservable($element.val());
        });

        if (allBindingsAccessor()['valueUpdate'] != null && allBindingsAccessor()['valueUpdate'] == "afterkeydown") {
          $element.on("keyup", function () {
            valueObservable($element.val());
          });
        }
      }

    },
    update: function (element, valueAccessor, allBindingsAccessor) {
      var $element = $(element);
      var params = valueAccessor();
      var valueObservable = ko.isObservable(params) ? params : params.value;

      if (!$element.is(':focus') || valueObservable() !== $element.val()) {
        $element.val(valueObservable());
      }
      if ($element.val() === '') {
        $element.removeClass('x');
      }
    }
  };

  ko.bindingHandlers.clickOutside = {
    init: function (element, valueAccessor) {
      var func = valueAccessor();

      $(document).on('click', function (event) {
        if ($.contains(document, event.target) && !$.contains(element, event.target)) {
          func();
        }
      });
    }
  };

  ko.bindingHandlers.blurHide = {
    init: function (element, valueAccessor) {
      var $el = $(element);
      var prop = valueAccessor();
      $el.on('blur', function () {
        if ($.trim($el.val()) === '') {
          if (ko.isObservable(prop)) {
            prop(false);
          }
        }
      });
    },
    update: function (element, valueAccessor) {
      var $el = $(element);
      var prop = valueAccessor();
      if (ko.isObservable(prop) && prop()) {
        $el.focus();
      }
    }
  }

  ko.bindingHandlers.spinedit = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var options = $.extend({
        minimum: 0,
        maximum: 10000,
        step: 5,
        value: ko.unwrap(valueAccessor()),
        numberOfDecimals: 0
      }, allBindingsAccessor().override);
      $(element).spinedit(options);
      $(element).on("valueChanged", function (e) {
        valueAccessor()(e.value);
      });
    },
    update: function (element, valueAccessor, allBindingsAccessor) {
      $(element).spinedit("setValue", ko.unwrap(valueAccessor()));
    }
  }

  ko.bindingHandlers.codemirror = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var options = $.extend(valueAccessor(), {});
      var editor = CodeMirror.fromTextArea(element, options);
      element.editor = editor;
      editor.setValue(options.data());
      editor.refresh();
      var wrapperElement = $(editor.getWrapperElement());

      $(document).on("refreshCodemirror", function () {
        editor.setSize("100%", 300);
        editor.refresh();
      });

      $(document).on("addFieldToSource", function (e, field) {
        if ($(element).data("template")) {
          editor.replaceSelection("{{" + field.name() + "}}");
        }
      });

      $(document).on("addFunctionToSource", function (e, fn) {
        if ($(element).data("template")) {
          editor.replaceSelection(fn);
        }
      });

      $(".chosen-select").chosen({
        disable_search_threshold: 10,
        width: "75%"
      });
      $('.chosen-select').trigger('chosen:updated');

      var sourceDelay = -1;
      editor.on("change", function (cm) {
        clearTimeout(sourceDelay);
        var _cm = cm;
        sourceDelay = setTimeout(function () {
          var _value = _cm.getValue();
          if (options.stripScript){
            _value = _value.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "");
          }
          valueAccessor().data(_value);
          if ($(".widget-html-pill").parent().hasClass("active")) {
            $("[contenteditable=true]").html(stripHtmlFromFunctions(valueAccessor().data()));
          }
        }, 100);
      });

      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        wrapperElement.remove();
      });
    },
    update: function (element, valueAccessor, allBindingsAccessor) {
      var editor = element.editor;
      editor.refresh();
    }
  };

  ko.bindingHandlers.chosen = {
      init: function(element, valueAccessor, allBindings, viewModel, bindingContext){
          var $element = $(element);
          var options = ko.unwrap(valueAccessor());

          if (typeof options === 'object')
              $element.chosen(options);
          else
              $element.chosen();

          ['options', 'selectedOptions', 'value'].forEach(function(propName){
              if (allBindings.has(propName)){
                  var prop = allBindings.get(propName);
                  if (ko.isObservable(prop)){
                      prop.subscribe(function(){
                          $element.trigger('chosen:updated');
                      });
                  }
              }
          });
      }
  }

  ko.bindingHandlers.tooltip = {
    after: ['attr'],
    init: function (element, valueAccessor) {
      var local = ko.utils.unwrapObservable(valueAccessor()),
          options = {};

      ko.utils.extend(options, local);

      if (options.title) {
        var title = ko.unwrap(options.title); // Not always an observable
        options.title = escapeOutput(title);
      }

      $(element).tooltip(options);

      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        $(element).tooltip("destroy");
      });
    },
    update: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
      var options = ko.utils.unwrapObservable(valueAccessor());
      var self = $(element);
      self.tooltip(options);
    }
  };

  ko.bindingHandlers.typeahead = {
    init: function (element, valueAccessor) {
      var binding = this;
      var elem = $(element);
      var valueAccessor = valueAccessor();

      var source = valueAccessor.nonBindableSource ? valueAccessor.nonBindableSource : function () {
        var _source = ko.utils.unwrapObservable(valueAccessor.source);
        if (valueAccessor.extraKeywords) {
          _source = _source.concat(valueAccessor.extraKeywords.split(" "))
        }

        if (valueAccessor.sourceSuffix && _source) {
          var _tmp = [];
          _source.forEach(function (item) {
            _tmp.push(item + valueAccessor.sourceSuffix);
          });
          _source = _tmp;
        }
        return _source;
      }

      if (valueAccessor.nonBindableSource && valueAccessor.displayProperty) {
        source = ko.utils.arrayMap(valueAccessor.nonBindableSource(), function(item) {
          return item[valueAccessor.displayProperty]();
        });
      }

      var _options = {
        source: source,
        onselect: function (val) {
          if (typeof valueAccessor.target == "function") {
            valueAccessor.target(val);
          }
          else {
            valueAccessor.target = val;
          }
        }
      }

      function extractor(query, extractorSeparator) {
        var result = /([^ ]+)$/.exec(query);
        if (extractorSeparator) {
          result = new RegExp("([^\\" + extractorSeparator + "]+)$").exec(query);
        }
        if (result && result[1])
          return result[1].trim();
        return "";
      }

      if (valueAccessor.multipleValues) {
        var _extractorFound = null;

        function updateExtractors() {
          var _val = elem.val();
          _extractorFound = null;
          var _extractors = (typeof valueAccessor.multipleValuesExtractors == "undefined" || valueAccessor.multipleValuesExtractors == null ? [" "] : valueAccessor.multipleValuesExtractors);
          var _extractorFoundLastIndex = -1;
          _extractors.forEach(function (extractor) {
            if (_val.indexOf(extractor) > -1) {
              if (_val.indexOf(extractor) >= _extractorFoundLastIndex) {
                _extractorFound = extractor;
                _extractorFoundLastIndex = _val.indexOf(extractor);
              }
            }
          });
        }

        _options.updater = function (item) {
          var _val = this.$element.val();
          var _separator = (typeof valueAccessor.multipleValuesSeparator == "undefined" || valueAccessor.multipleValuesSeparator == null ? ":" : valueAccessor.multipleValuesSeparator);
          if (valueAccessor.extraKeywords && valueAccessor.extraKeywords.split(" ").indexOf(item) > -1) {
            _separator = "";
          }
          var isSpecialResult = false;
          if (item.indexOf("<i ") > -1) {
            _separator = "";
            isSpecialResult = true;
          }
          updateExtractors();
          if (_extractorFound != null) {
            return (isSpecialResult ? '"' : '') + _val.substring(0, _val.lastIndexOf(_extractorFound)) + _extractorFound + $.trim(item.replace(/<[^>]*>/gi, "")) + (isSpecialResult ? '"' : '') + _separator;
          }
          else {
            return (isSpecialResult ? '"' : '') + $.trim(item.replace(/<[^>]*>/gi, "")) + (isSpecialResult ? '"' : '') + _separator;
          }
        }
        _options.matcher = function (item) {
          updateExtractors();
          var _tquery = extractor(this.query, _extractorFound);
          if (!_tquery) return false;
          return ~item.toLowerCase().indexOf(_tquery.toLowerCase());
        },
            _options.highlighter = function (item) {
              updateExtractors();
              var _query = extractor(this.query, _extractorFound).replace(/[\-\[\]{}()*+?.:\\\^$|#\s]/g, '\\$&');
              var _result = $.trim(item.replace(/<[^>]*>/gi, "")).replace(new RegExp('(' + _query + ')', 'ig'), function ($1, match) {
                return '<strong>' + match + '</strong>'
              });
              if (item.indexOf("<i ") > -1) {
                _result += " " + item.substr(item.indexOf("<i "));
              }
              return _result;
            }
      }

      if (valueAccessor.completeSolrRanges) {
        elem.on("keyup", function (e) {
          if (e.keyCode != 8 && e.which != 8 && elem.val() && (elem.val().slice(-1) == "[" || elem.val().slice(-1) == "{")) {
            var _index = elem.val().length;
            elem.val(elem.val() + " TO " + (elem.val().slice(-1) == "[" ? "]" : "}"));

            if (element.createTextRange) {
              var range = element.createTextRange();
              range.move("character", _index);
              range.select();
            } else if (element.selectionStart != null) {
              element.focus();
              element.setSelectionRange(_index, _index);
            }

          }
        });
      }

      if (valueAccessor.triggerOnFocus) {
        _options.minLength = 0;
      }

      element.typeahead = elem.typeahead(_options);

      if (valueAccessor.triggerOnFocus) {
        elem.on('focus', function () {
          elem.trigger("keyup");
        });
      }

      elem.blur(function () {
        if (typeof valueAccessor.target == "function") {
          valueAccessor.target(elem.val());
        }
        else {
          valueAccessor.target = elem.val();
        }
      });
    },
    update: function (element, valueAccessor) {
      var elem = $(element);
      var valueAccessor = valueAccessor();
      if (typeof valueAccessor.completeSolrRanges === 'undefined') {
        if (typeof valueAccessor.target == "function") {
          elem.val(valueAccessor.target());
        }
        else {
          elem.val(valueAccessor.target);
        }
      }
      if (valueAccessor.forceUpdateSource) {
        element.typeahead.data('typeahead').source = function () {
          var _source = ko.utils.unwrapObservable(valueAccessor.source);
          if (valueAccessor.extraKeywords) {
            _source = _source.concat(valueAccessor.extraKeywords.split(" "))
          }

          if (valueAccessor.sourceSuffix && _source) {
            var _tmp = [];
            _source.forEach(function (item) {
              _tmp.push(item + valueAccessor.sourceSuffix);
            });
            _source = _tmp;
          }
          return _source;
        }
      }

    }
  };


  ko.bindingHandlers.select2 = {
    init: function (element, valueAccessor, allBindingsAccessor, vm) {
      var options = ko.toJS(valueAccessor()) || {};
      var $element = $(element);

      // When the options are in the binding value accessor the data attribute will be used instead of any <select>
      // tag it's attached to.
      if (ko.isObservable(valueAccessor().options) && ko.isObservable(valueAccessor().value)) {
        var optionsObservable = valueAccessor().options;
        var valueObservable = valueAccessor().value;
        options.data = $.map(optionsObservable(), function (value) {
          return { id: value, text: value }
        });
        options.val = valueObservable();

        var refreshSelect2Data = function () {
          $element.select2("data", $.map(optionsObservable(), function (value) {
            return { id: value, text: value }
          }));
          $element.select2("val", valueObservable());
        };

        valueObservable.subscribe(function (newValue) {
          if (newValue !== $element.select2("val")) {
            refreshSelect2Data();
          }
        });

        optionsObservable.subscribe(refreshSelect2Data);

        window.setTimeout(function () {
          refreshSelect2Data();
        }, 10)
      }

      if (typeof valueAccessor().update != "undefined") {
        if (options.type == "user" && viewModel.selectableHadoopUsers().indexOf(options.update) == -1) {
          viewModel.availableHadoopUsers.push({
            username: options.update
          });
        }
        if (options.type == "group") {
          if (options.update instanceof Array) {
            options.update.forEach(function (opt) {
              if (viewModel.selectableHadoopGroups().indexOf(opt) == -1) {
                viewModel.availableHadoopGroups.push({
                  name: opt
                });
              }
            });
          }
          else if (viewModel.selectableHadoopGroups().indexOf(options.update) == -1) {
            viewModel.availableHadoopGroups.push({
              name: options.update
            });
          }
        }
        if (options.type == "action" && viewModel.availableActions().indexOf(options.update) == -1) {
          viewModel.availableActions.push(options.update);
        }
        if (options.type == "scope" && viewModel.availablePrivileges().indexOf(options.update) == -1) {
          viewModel.availablePrivileges.push(options.update);
        }
        if (options.type == "parameter" && options.update != "") {
          var _found = false;
          allBindingsAccessor().options().forEach(function(opt){
            var _option = opt[allBindingsAccessor().optionsValue];
            if (ko.isObservable(_option)){
              _option = _option();
            }
            if (_option == options.update){
              _found = true;
            }
          });
          if (!_found){
            allBindingsAccessor().options.push({
              name: ko.observable(options.update),
              value: ko.observable(options.update)
            });
          }
        }
      }
      $element
          .select2(options)
          .on("change", function (e) {
            if (typeof e.val != "undefined") {
              if (typeof valueAccessor().update != "undefined") {
                valueAccessor().update(e.val);
              }
              if (typeof valueAccessor().value != "undefined") {
                valueAccessor().value(e.val);
              }
            }
          })
          .on("select2-focus", function (e) {
            if (typeof options.onFocus != "undefined") {
              options.onFocus();
            }
          })
          .on("select2-blur", function (e) {
            if (typeof options.onBlur != "undefined") {
              options.onBlur();
            }
          })
          .on("select2-open", function () {
            $(".select2-input").off("keyup").data("type", options.type).on("keyup", function (e) {
              if (e.keyCode === 13) {
                var _isArray = options.update instanceof Array;
                var _newVal = $(this).val();
                var _type = $(this).data("type");
                if ($.trim(_newVal) != "") {
                  if (_type == "user") {
                    viewModel.availableHadoopUsers.push({
                      username: _newVal
                    });
                  }
                  if (_type == "group") {
                    viewModel.availableHadoopGroups.push({
                      name: _newVal
                    });
                  }
                  if (_type == "action") {
                    viewModel.availableActions.push(_newVal);
                  }
                  if (_type == "scope") {
                    viewModel.availablePrivileges.push(_newVal);
                  }
                  if (_type == "role") {
                    var _r = new Role(viewModel, { name: _newVal });
                    viewModel.tempRoles.push(_r);
                    viewModel.roles.push(_r);
                  }
                  if (_type == "parameter") {
                    var _found = false;
                    allBindingsAccessor().options().forEach(function(opt){
                      if (opt[allBindingsAccessor().optionsValue]() == _newVal){
                        _found = true;
                      }
                    });
                    if (!_found){
                      allBindingsAccessor().options.push({
                        name: ko.observable(_newVal),
                        value: ko.observable(_newVal)
                      });
                    }
                  }
                  if (_isArray) {
                    var _vals = $(element).select2("val");
                    _vals.push(_newVal);
                    $(element).select2("val", _vals, true);
                  }
                  else {
                    $(element).select2("val", _newVal, true);
                  }
                  $(element).select2("close");
                }
              }
            });
          })
    },
    update: function (element, valueAccessor, allBindingsAccessor, vm) {
      if (typeof allBindingsAccessor().visible != "undefined"){
        if ((typeof allBindingsAccessor().visible == "boolean" && allBindingsAccessor().visible) || (typeof allBindingsAccessor().visible == "function" && allBindingsAccessor().visible())) {
          $(element).select2("container").show();
        }
        else {
          $(element).select2("container").hide();
        }
      }
      if (typeof valueAccessor().update != "undefined") {
        $(element).select2("val", valueAccessor().update());
      }
      if (typeof valueAccessor().readonly != "undefined") {
        $(element).select2("readonly", valueAccessor().readonly);
        if (typeof valueAccessor().readonlySetTo != "undefined") {
          valueAccessor().readonlySetTo();
        }
      }
    }
  };

  ko.bindingHandlers.hivechooser = {
    init: function (element, valueAccessor, allBindingsAccessor, vm) {
      var self = $(element);
      var options = ko.unwrap(valueAccessor());
      var complexConfiguration = false;
      if (typeof options === 'function'){
        self.val(options());
      }
      else {
        if (options && options.data){
          self.val(options.data);
          complexConfiguration = true;
        }
        else {
          self.val(options);
        }
      }

      if (complexConfiguration) {
        self.jHueGenericAutocomplete({
          showOnFocus: true,
          skipColumns: ko.unwrap(options.skipColumns),
          skipTables: ko.unwrap(options.skipTables),
          startingPath: options.database + '.',
          rewriteVal: true,
          onPathChange: options.onChange,
          searchEverywhere : ko.unwrap(options.searchEverywhere) || false,
          apiHelperUser: ko.unwrap(options.apiHelperUser) || '',
          apiHelperType: ko.unwrap(options.apiHelperType) || '',
          mainScrollable: ko.unwrap(options.mainScrollable) || $(window)
        });
      }
      else {
        options = allBindingsAccessor();
        function setPathFromAutocomplete(path) {
          self.val(path);
          valueAccessor()(path);
          self.blur();
        }
        self.on("blur", function () {
          valueAccessor()(self.val());
        });
        if (allBindingsAccessor().valueUpdate != null && allBindingsAccessor().valueUpdate == "afterkeydown") {
          self.on("keyup", function () {
            valueAccessor()(self.val());
          });
        }
        self.jHueGenericAutocomplete({
          showOnFocus: true,
          home: "/",
          skipColumns: ko.unwrap(options.skipColumns) || false,
          skipTables: ko.unwrap(options.skipTables) || false,
          apiHelperUser: ko.unwrap(options.apiHelperUser) || '',
          apiHelperType: ko.unwrap(options.apiHelperType) || '',
          mainScrollable: ko.unwrap(options.mainScrollable) || $(window),
          onPathChange: function (path) {
            setPathFromAutocomplete(path);
          },
          onEnter: function (el) {
            setPathFromAutocomplete(el.val());
          },
          onBlur: function () {
            if (self.val().lastIndexOf(".") == self.val().length - 1) {
              self.val(self.val().substr(0, self.val().length - 1));
            }
            valueAccessor()(self.val());
          }
        });
      }

    }
  }

  ko.bindingHandlers.solrchooser = {
    init: function (element, valueAccessor, allBindingsAccessor, vm) {
      var self = $(element);
      self.val(valueAccessor()());

      function setPathFromAutocomplete(path) {
        self.val(path);
        valueAccessor()(path);
        self.blur();
      }

      self.on("blur", function () {
        valueAccessor()(self.val());
      });

      self.jHueGenericAutocomplete({
        showOnFocus: true,
        home: "/",
        serverType: "SOLR",
        onPathChange: function (path) {
          setPathFromAutocomplete(path);
        },
        onEnter: function (el) {
          setPathFromAutocomplete(el.val());
        },
        onBlur: function () {
          if (self.val().lastIndexOf(".") == self.val().length - 1) {
            self.val(self.val().substr(0, self.val().length - 1));
          }
          valueAccessor()(self.val());
        }
      });
    }
  }

  ko.bindingHandlers.hdfsAutocomplete = {
    init: function (element, valueAccessor, allBindingsAccessor, vm) {
      var stripHashes = function (str) {
        return str.replace(/#/gi, encodeURIComponent("#"));
      };

      var self = $(element);
      self.attr("autocomplete", "off");
      self.jHueHdfsAutocomplete({
        skipKeydownEvents: true,
        skipScrollEvent: true
      });
    }
  };

  ko.bindingHandlers.filechooser = {
    init: function (element, valueAccessor, allBindingsAccessor, vm) {
      var $element = $(element);
      var options = ko.unwrap(allBindingsAccessor());
      $element.attr("autocomplete", "off");
      if (typeof valueAccessor() == "function" || typeof valueAccessor().value == "function") {
        $element.val(valueAccessor().value ? valueAccessor().value(): valueAccessor()());
        $element.data("fullPath", $element.val());
        $element.attr("data-original-title", $element.val());
        if (valueAccessor().displayJustLastBit){
          var _val = $element.val();
          $element.val(_val.split("/")[_val.split("/").length - 1]);
        }
        $element.on("blur", function () {
          if (valueAccessor().value){
            if (valueAccessor().displayJustLastBit){
              var _val = $element.data("fullPath");
              valueAccessor().value(_val.substr(0, _val.lastIndexOf("/")) + "/" + $element.val());
            } else {
              valueAccessor().value($element.val());
            }
            $element.data("fullPath", valueAccessor().value());
          } else {
            valueAccessor()($element.val());
            $element.data("fullPath", valueAccessor()());
          }
          $element.attr("data-original-title", $element.data("fullPath"));
        });

        if (options.valueUpdate && options.valueUpdate === 'afterkeydown') {
          $element.on('keyup', function () {
            if (valueAccessor().value){
              valueAccessor().value($element.val());
            } else {
              valueAccessor()($element.val());
            }
          });
        }
      } else {
        $element.val(valueAccessor());
        $element.on("blur", function () {
          valueAccessor($element.val());
        });
        if (options.valueUpdate && options.valueUpdate === 'afterkeydown') {
          $element.on('keyup', function () {
            valueAccessor($element.val());
          });
        }
      }

      $element.after(getFileBrowseButton($element, true, valueAccessor, true, allBindingsAccessor, valueAccessor().isAddon, valueAccessor().isNestedModal, allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.linkMarkup));

      if (allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.openOnFocus) {
        $element.on('focus', function () {
          if ($element.val() === '') {
            $element.siblings('.filechooser-clickable').click();
          }
        });
      }
    }
  };


  function getFileBrowseButton(inputElement, selectFolder, valueAccessor, stripHdfsPrefix, allBindingsAccessor, isAddon, isNestedModal, linkMarkup) {
    var _btn;
    if (isAddon) {
      _btn = $("<span>").addClass("add-on muted pointer filechooser-clickable").text("..");
    } else if (linkMarkup) {
      _btn = $("<a>").addClass("btn").addClass("fileChooserBtn filechooser-clickable").text("..");
    } else {
      _btn = $("<button>").addClass("btn").addClass("fileChooserBtn filechooser-clickable").text("..");
    }
    _btn.click(function (e) {
      e.preventDefault();
      if (!isNestedModal) {
        $("body").addClass("modal-open");
      }
      // check if it's a relative path
      callFileChooser();

      function callFileChooser() {
        var _initialPath = $.trim(inputElement.val()) != "" ? inputElement.val() : "/";
        if ((allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.skipInitialPathIfEmpty && inputElement.val() == "") || (allBindingsAccessor && allBindingsAccessor().filechooserPrefixSeparator)) {
          _initialPath = "";
        }
        if (inputElement.data("fullPath")) {
          _initialPath = inputElement.data("fullPath");
        }
        if (_initialPath.indexOf("hdfs://") > -1) {
          _initialPath = _initialPath.substring(7);
        }

        var supportSelectFolder = !!selectFolder;
        if (typeof allBindingsAccessor().filechooserOptions.selectFolder !== 'undefined') {
          supportSelectFolder = allBindingsAccessor().filechooserOptions.selectFolder;
        }

        $("#filechooser").jHueFileChooser({
          suppressErrors: true,
          selectFolder: supportSelectFolder,
          onFolderChoose: function (filePath) {
            handleChoice(filePath, stripHdfsPrefix);
            if (selectFolder) {
              $("#chooseFile").modal("hide");
              if (!isNestedModal) {
                $(".modal-backdrop").remove();
              }
            }
          },
          onFileChoose: function (filePath) {
            handleChoice(filePath, stripHdfsPrefix);
            $("#chooseFile").modal("hide");
            if (!isNestedModal) {
              $(".modal-backdrop").remove();
            }
          },
          createFolder: allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.createFolder,
          uploadFile: allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.uploadFile,
          initialPath: _initialPath,
          errorRedirectPath: "",
          forceRefresh: true,
          showExtraHome: allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.showExtraHome,
          extraHomeProperties: allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.extraHomeProperties ? allBindingsAccessor().filechooserOptions.extraHomeProperties : {},
          filterExtensions: allBindingsAccessor && allBindingsAccessor().filechooserFilter ? allBindingsAccessor().filechooserFilter : "",
          displayOnlyFolders: allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.displayOnlyFolders
        });
        $("#chooseFile").modal("show");
        if (!isNestedModal) {
          $("#chooseFile").on("hidden", function () {
            $("body").removeClass("modal-open");
            $(".modal-backdrop").remove();
          });
        }
      }

      function handleChoice(filePath, stripHdfsPrefix) {
        if (allBindingsAccessor && allBindingsAccessor().filechooserPrefixSeparator) {
          filePath = inputElement.val().split(allBindingsAccessor().filechooserPrefixSeparator)[0] + '=' + filePath;
        }
        if (allBindingsAccessor && allBindingsAccessor().filechooserOptions && allBindingsAccessor().filechooserOptions.deploymentDir) {
          inputElement.data("fullPath", filePath);
          inputElement.attr("data-original-title", filePath);
          if (filePath.indexOf(allBindingsAccessor().filechooserOptions.deploymentDir) == 0) {
            filePath = filePath.substr(allBindingsAccessor().filechooserOptions.deploymentDir.length + 1);
          }
        }
        if (stripHdfsPrefix) {
          inputElement.val(filePath);
        }
        else {
          inputElement.val("hdfs://" + filePath);
        }
        inputElement.change();
        if (valueAccessor) {
          if (typeof valueAccessor() == "function" || typeof valueAccessor().value == "function") {
            if (valueAccessor().value) {
              valueAccessor().value(inputElement.val());
              if (valueAccessor().displayJustLastBit) {
                inputElement.data("fullPath", inputElement.val());
                inputElement.attr("data-original-title", inputElement.val());
                var _val = inputElement.val();
                inputElement.val(_val.split("/")[_val.split("/").length - 1])
              }
            }
            else {
              valueAccessor()(inputElement.val());
            }
          }
          else {
            valueAccessor(inputElement.val());
          }
        }
      }
    });
    if (allBindingsAccessor && allBindingsAccessor().filechooserDisabled) {
      _btn.addClass("disabled").attr("disabled", "disabled");
    }
    return _btn;
  }

  window.getFileBrowseButton = getFileBrowseButton;

  ko.bindingHandlers.datepicker = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var _el = $(element);
      var _options = ko.unwrap(valueAccessor());
      _el.datepicker({
        format: "yyyy-mm-dd"
      }).on("show", function (e) {
        if (_options.momentFormat) {
          _el.datepicker("setValue", moment(_el.val()).utc().format("YYYY-MM-DD"));
        }
      }).on("changeDate", function (e) {
        setDate(e.date);
      }).on("hide", function (e) {
        setDate(e.date);
      });

      function setDate(d) {
        if (_options.momentFormat) {
          _el.val(moment(d).utc().format(_options.momentFormat));
        }
        allBindings().value(_el.val());
      }
    }
  }


  ko.bindingHandlers.timepicker = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var _el = $(element);
      _el.timepicker({
        minuteStep: 1,
        showSeconds: false,
        showMeridian: false,
        defaultTime: false
      });
    }
  }


  ko.bindingHandlers.textSqueezer = {
    init: function (element, valueAccessor) {
      var value = valueAccessor();
      $(element).text(ko.unwrap(value));
      $(element).textSqueezer({
        decimalPrecision: 2
      });
    },
    update: function (element, valueAccessor) {
      var value = valueAccessor();
      $(element).text(ko.unwrap(value));
      $(element).trigger("redraw");
    }
  };


  ko.toJSONObject = function (koObj) {
    return JSON.parse(ko.toJSON(koObj));
  }

  ko.toCleanJSON = function (koObj) {
    return ko.toJSON(koObj, function (key, value) {
      if (key == "__ko_mapping__") {
        return;
      }
      else {
        return value;
      }
    });
  }


  ko.bindingHandlers.delayedOverflow = {
    init: function (element) {
      var $element = $(element);
      $element.css("overflow", "hidden");

      var scrollTimeout = -1;
      $element.hover(function() {
        scrollTimeout = window.setTimeout(function() {
          $element.css("overflow", "auto");
        }, 500);
      }, function() {
        clearTimeout(scrollTimeout);
        $element.css("overflow", "hidden");
      });
    }
  };

  ko.bindingHandlers.clickForAceFocus = {
    init: function (element, valueAccessor) {
      var editor = valueAccessor();
      $(element).on("click", function(e) {
        if (e.target === element) {
          editor().focus();
          editor().execCommand("gotolineend");
        }
      });
    }
  };

  ko.bindingHandlers.aceEditor = {
    init: function (element, valueAccessor) {

      var $el = $(element);
      var options = ko.unwrap(valueAccessor());
      var snippet = options.snippet;
      var apiHelper = snippet.getApiHelper();
      var aceOptions = options.aceOptions || {};

      var disposeFunctions = [];

      var dispose = function () {
        disposeFunctions.forEach(function (dispose) {
          dispose();
        })
      };

      ko.utils.domNodeDisposal.addDisposeCallback(element, dispose);

      $el.text(snippet.statement_raw());

      window.setTimeout(function () {
        huePubSub.publish('editor.refresh.locations');
      }, 0);

      var editor = ace.edit($el.attr("id"));
      editor.session.setMode(snippet.getAceMode());
      if (navigator.platform && navigator.platform.toLowerCase().indexOf("linux") > -1) {
        editor.setOptions({ fontSize: "14px" });
      }

      function processErrorsAndWarnings(type, list) {
        editor.clearErrorsAndWarnings(type);
        var offset = 0;
        if (snippet.isSqlDialect()) {
          if (editor.getSelectedText()) {
            var selectionRange = editor.getSelectionRange();
            offset = Math.min(selectionRange.start.row, selectionRange.end.row);
          }
          if (snippet.result && snippet.result.statements_count() > 1) {
            offset = snippet.result.statement_range().start.row;
          }
        }
        if (list.length > 0) {
          list.forEach(function (item, cnt) {
            if (item.line !== null) {
              if (type === 'error') {
                editor.addError(item.message, item.line + offset);
              }
              else {
                editor.addWarning(item.message, item.line + offset);
              }
              if (cnt == 0) {
                editor.scrollToLine(item.line + offset, true, true, function () {
                });
                if (item.col !== null) {
                  editor.renderer.scrollCursorIntoView({row: item.line + offset, column: item.col + 10}, 0.5)
                }
              }
            }
          });
        }
      }

      var errorsSub = snippet.errors.subscribe(function (newErrors) {
        processErrorsAndWarnings('error', newErrors);
      });


      var aceWarningsSub = snippet.aceWarnings.subscribe(function (newWarnings) {
        processErrorsAndWarnings('warning', newWarnings);
      });

      var aceErrorsSub = snippet.aceErrors.subscribe(function (newErrors) {
        processErrorsAndWarnings('error', newErrors);
      });

      disposeFunctions.push(function () {
        errorsSub.dispose();
        aceWarningsSub.dispose();
        aceErrorsSub.dispose();
      });

      editor.setTheme($.totalStorage("hue.ace.theme") || "ace/theme/hue");

      var editorOptions = {
        enableSnippets: true,
        showGutter: false,
        showLineNumbers: false,
        showPrintMargin: false,
        scrollPastEnd: 0.1,
        minLines: 1,
        maxLines: 25
      };

      editor.enabledMenuOptions = {
        setShowInvisibles: true,
        setTabSize: true,
        setShowGutter: true
      };

      var errorHighlightingEnabled = snippet.getApiHelper().getFromTotalStorage('hue.ace', 'errorHighlightingEnabled', false);

      editor.customMenuOptions = {
        setEnableAutocompleter: function (enabled) {
          editor.setOption('enableBasicAutocompletion', enabled);
          snippet.getApiHelper().setInTotalStorage('hue.ace', 'enableBasicAutocompletion', enabled);
          if (enabled && $('#setEnableLiveAutocompletion:checked').length === 0) {
            $('#setEnableLiveAutocompletion').trigger('click');
          } else if (!enabled && $('#setEnableLiveAutocompletion:checked').length !== 0) {
            $('#setEnableLiveAutocompletion').trigger('click');
          }
        },
        getEnableAutocompleter: function () {
          return editor.getOption('enableBasicAutocompletion');
        },
        setEnableLiveAutocompletion: function (enabled) {
          editor.setOption('enableLiveAutocompletion', enabled);
          snippet.getApiHelper().setInTotalStorage('hue.ace', 'enableLiveAutocompletion', enabled);
          if (enabled && $('#setEnableAutocompleter:checked').length === 0) {
            $('#setEnableAutocompleter').trigger('click');
          }
        },
        getEnableLiveAutocompletion: function () {
          return editor.getOption('enableLiveAutocompletion');
        }
      };

      if (window.Worker) {
        editor.customMenuOptions.setExperimentalErrorHighlighting = function (enabled) {
          errorHighlightingEnabled = enabled;
          snippet.getApiHelper().setInTotalStorage('hue.ace', 'errorHighlightingEnabled', enabled);
        };
        editor.customMenuOptions.getExperimentalErrorHighlighting = function () {
          return errorHighlightingEnabled;
        };
      }

      $.extend(editorOptions, aceOptions);

      var activeTokens = [];
      if (window.Worker) {
        var aceSqlWorker = new Worker('/static/desktop/js/aceSqlWorker.js?bust=' + Math.random());
        var workerIsReady = false;

        disposeFunctions.push(function () {
          aceSqlWorker.terminate();
        });

        var AceRange = ace.require('ace/range').Range;

        var lastKnownLocations = [];

        var locationsSub = huePubSub.subscribe('get.active.editor.locations', function () {
          huePubSub.publish('editor.active.locations', lastKnownLocations);
        });

        disposeFunctions.push(function () {
          locationsSub.remove();
        });

        aceSqlWorker.onmessage = function(e) {
          workerIsReady = true;
          if (e.data.ping) {
            return;
          }
          if (errorHighlightingEnabled) {
            for (var id in editor.session.getMarkers()) {
              var marker = editor.session.getMarkers()[id];
              if (marker.clazz == "hue-ace-error"){
                editor.session.removeMarker(marker.id);
              }
            }

            if (e.data.errors) {
              e.data.errors.forEach(function (error) {
                if (error.expected.length > 0) {
                  var token = editor.session.getTokenAt(error.loc.first_line - 1, error.loc.first_column);
                  if (token) {
                    token.error = error;
                    editor.session.addMarker(new AceRange(error.loc.first_line - 1, error.loc.first_column, error.loc.last_line - 1, error.loc.last_column), 'hue-ace-error', 'fail');
                  }
                }
              });
            }
          }


          var lastKnownLocations = { id: $el.attr("id"), type: snippet.type(), defaultDatabase: snippet.database(), locations: e.data.locations };

          // Clear out old parse locations to prevent them from being shown when there's a syntax error in the statement
          while(activeTokens.length > 0) {
            delete activeTokens.pop().parseLocation;
          }

          e.data.locations.forEach(function (location) {
            if (location.type === 'statement' || ((location.type === 'table' || location.type === 'column') && typeof location.identifierChain === 'undefined')) {
              return;
            }
            if ((location.type === 'table' && location.identifierChain.length > 1) || (location.type === 'column' && location.identifierChain.length > 2)) {
              var clonedChain = location.identifierChain.concat();
              var dbFound = false;
              if (apiHelper.containsDatabase(snippet.type(), clonedChain[0].name)) {
                clonedChain.shift();
                dbFound = true;
              }
              if (dbFound && clonedChain.length > 1) {
                location.type = 'complex';
              }
            }

            var token = editor.session.getTokenAt(location.location.first_line - 1, location.location.first_column);
            if (token && token.value && /`$/.test(token.value)) {
              // Ace getTokenAt() thinks the first ` is a token, column +1 will include the first and last.
              token = editor.session.getTokenAt(location.location.first_line - 1, location.location.first_column + 1);
            }
            if (token !== null) {
              if (location.type === 'column' && typeof location.tables !== 'undefined' && location.identifierChain.length === 1) {

                var findIdentifierChainInTable = function (tablesToGo) {
                  var nextTable = tablesToGo.shift();
                  if (typeof nextTable.subQuery === 'undefined') {
                    apiHelper.fetchAutocomplete({
                      sourceType: snippet.type(),
                      defaultDatabase: snippet.database(),
                      identifierChain: nextTable.identifierChain,
                      silenceErrors: true,
                      successCallback: function (data) {
                        try {
                          if (typeof data.columns !== 'undefined' && data.columns.indexOf(location.identifierChain[0].name) !== -1) {
                            location.identifierChain = nextTable.identifierChain.concat(location.identifierChain);
                            delete location.tables;
                            token.parseLocation = location;
                            activeTokens.push(token);
                          } else if (tablesToGo.length > 0) {
                            findIdentifierChainInTable(tablesToGo);
                          }
                        } catch (e) {} // TODO: Ignore for subqueries
                      }
                    })
                  } else if (tablesToGo.length > 0) {
                    findIdentifierChainInTable(tablesToGo);
                  }
                };

                findIdentifierChainInTable(location.tables.concat());
              } else {
                token.parseLocation = location;
                activeTokens.push(token);
              }
            }
          });

          huePubSub.publish('editor.active.locations', lastKnownLocations);
        };

        var whenWorkerIsReady = function (callback) {
          if (!workerIsReady) {
            aceSqlWorker.postMessage({ ping: true });
            window.setTimeout(function () {
              whenWorkerIsReady(callback);
            }, 500);
          } else {
            callback();
          }
        };

        var refreshSub = huePubSub.subscribe('editor.refresh.locations', function () {
          if (snippet.getAceMode() === 'ace/mode/hive' || snippet.getAceMode() === 'ace/mode/impala') {
            whenWorkerIsReady(function () {
              aceSqlWorker.postMessage({ text: editor.getValue(), type: snippet.type() });
            });
          }
        });

        disposeFunctions.push(function () {
          refreshSub.remove();
        });
      }

      editorOptions['enableBasicAutocompletion'] = snippet.getApiHelper().getFromTotalStorage('hue.ace', 'enableBasicAutocompletion', true);
      if (editorOptions['enableBasicAutocompletion']) {
        editorOptions['enableLiveAutocompletion'] = snippet.getApiHelper().getFromTotalStorage('hue.ace', 'enableLiveAutocompletion', true);
      }

      editor.setOptions(editorOptions);

      var AceAutocomplete = ace.require("ace/autocomplete").Autocomplete;

      if (!editor.completer) {
        editor.completer = new AceAutocomplete();
      }
      editor.completer.exactMatch = ! snippet.isSqlDialect();

      var initAutocompleters = function () {
        if (editor.completers) {
          editor.completers.length = 0;
          if (snippet.type() === 'hive' || snippet.type() === 'impala') {
            if (options.useNewAutocompleter) {
              editor.useHueAutocompleter = true;
            } else {
              editor.completers.push(snippet.autocompleter);
            }
          } else {
            editor.completers.push(langTools.snippetCompleter);
            editor.completers.push(langTools.textCompleter);
            editor.completers.push(langTools.keyWordCompleter);
            editor.completers.push(snippet.autocompleter);
          }
        }
      };

      var langTools = ace.require("ace/ext/language_tools");
      langTools.textCompleter.setSqlMode(snippet.isSqlDialect());

      initAutocompleters();

      var removeUnicodes = function (value) {
        var UNICODES_TO_REMOVE = /[\u1680\u180E\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u200B\u202F\u205F\u3000\uFEFF]/ig;  //taken from https://www.cs.tut.fi/~jkorpela/chars/spaces.html
        return value.replace(UNICODES_TO_REMOVE, ' ');
      };

      var placeHolderElement = null;
      var placeHolderVisible = false;
      var placeHolderText = snippet.getPlaceHolder();
      if (placeHolderText) {
        placeHolderElement = $("<div>")
          .text(placeHolderText)
          .css("margin-left", "6px")
          .addClass("ace_invisible ace_emptyMessage");
        if (editor.getValue().length == 0) {
          placeHolderElement.appendTo(editor.renderer.scroller);
          placeHolderVisible = true;
        }
      }

      var lastEditorValue = null;
      var checkEditorValueInterval = -1;
      var pasteListener = editor.on('paste', function (e) {
        window.clearInterval(checkEditorValueInterval);
        checkEditorValueInterval = window.setInterval(function () {
          if (lastEditorValue !== editor.getValue()) {
            var lastKnownPosition = editor.getCursorPosition();
            window.clearInterval(checkEditorValueInterval);
            lastEditorValue = editor.getValue();
            editor.setValue(removeUnicodes(lastEditorValue), 1);
            editor.moveCursorToPosition(lastKnownPosition);
          }
        }, 10);
      });

      disposeFunctions.push(function () {
        editor.off('paste', pasteListener);
      });

      var inputListener = editor.on('input', function () {
        if (editor.getValue().length == 0) {
          if (!placeHolderVisible && placeHolderElement) {
            placeHolderElement.appendTo(editor.renderer.scroller);
            placeHolderVisible = true;
          }
        } else {
          placeHolderElement.remove();
          placeHolderVisible = false;
        }
        if (options.updateOnInput) {
          snippet.statement_raw(removeUnicodes(editor.getValue()));
        }
      });

      disposeFunctions.push(function () {
        editor.off('input', inputListener);
      });

      var focusListener = editor.on('focus', function () {
        initAutocompleters();
        snippet.inFocus(true);
        $(".ace-editor").data("last-active-editor", false);
        $el.data("last-active-editor", true);
        if (editor.session.$backMarkers) {
          for (var marker in editor.session.$backMarkers) {
            if (editor.session.$backMarkers[marker].clazz === 'highlighted') {
              editor.session.removeMarker(editor.session.$backMarkers[marker].id);
            }
          }
        }
      });

      disposeFunctions.push(function () {
        editor.off('focus', focusListener);
      });

      var changeCursorThrottle = -1;
      var changeCursorListener = editor.selection.on('changeCursor', function () {
        window.clearTimeout(changeCursorThrottle);
        changeCursorThrottle = window.setTimeout(function () {
          huePubSub.publish('editor.active.cursor.location', { id: $el.attr("id"), position: editor.getCursorPosition(), editor: editor });
        }, 150);
      });

      var changeSelectionListener = editor.selection.on('changeSelection', function () {
        snippet.selectedStatement(editor.getSelectedText());
      });

      disposeFunctions.push(function () {
        window.clearTimeout(changeCursorThrottle);
        editor.selection.off('changeCursor', changeCursorListener);
        editor.selection.off('changeSelection', changeSelectionListener);
      });

      var cursorLocationSub = huePubSub.subscribe('get.active.editor.cursor.location', function () {
        huePubSub.publish('editor.active.cursor.location', { id: $el.attr("id"), position: editor.getCursorPosition(), editor: editor });
      });

      disposeFunctions.push(function () {
        cursorLocationSub.remove();
      });

      var blurListener = editor.on('blur', function () {
        snippet.inFocus(false);
        snippet.statement_raw(removeUnicodes(editor.getValue()));
        if (options.onBlur) {
          options.onBlur($el, removeUnicodes(editor.getValue()));
        }
      });

      disposeFunctions.push(function () {
        editor.off('blur', blurListener);
      });

      // TODO: Move context menu logic to separate module
      (function () {
        var Tooltip = ace.require("ace/tooltip").Tooltip;

        var contextTooltip = new Tooltip(editor.container);
        var tooltipTimeout = -1;
        var disableTooltip = false;
        var lastHoveredToken = null;
        var activeMarkers = [];
        var keepLastMarker = false;

        var hideContextTooltip = function () {
          clearTimeout(tooltipTimeout);
          contextTooltip.hide();
        };

        var clearActiveMarkers = function () {
          hideContextTooltip();
          while (activeMarkers.length > keepLastMarker ? 1 : 0) {
            editor.session.removeMarker(activeMarkers.shift());
          }
        };

        var markLocation = function (parseLocation) {
          var range;
          if (parseLocation.type === 'function') {
            // Todo: Figure out why functions need an extra char at the end
            range = new AceRange(parseLocation.location.first_line - 1, parseLocation.location.first_column - 1, parseLocation.location.last_line - 1, parseLocation.location.last_column);
          } else {
            range = new AceRange(parseLocation.location.first_line - 1, parseLocation.location.first_column - 1, parseLocation.location.last_line - 1, parseLocation.location.last_column - 1);
          }
          activeMarkers.push(editor.session.addMarker(range, 'hue-ace-location'));
          return range;
        };

        var popoverShownSub = huePubSub.subscribe('sql.context.popover.shown', function () {
          hideContextTooltip();
          keepLastMarker = true;
          disableTooltip = true;
        });

        disposeFunctions.push(function () {
          popoverShownSub.remove();
        });

        var popoverHiddenSub = huePubSub.subscribe('sql.context.popover.hidden', function () {
          disableTooltip = false;
          clearActiveMarkers();
          keepLastMarker = false;
        });

        disposeFunctions.push(function () {
          popoverHiddenSub.remove();
        });

        var mousemoveListener = editor.on('mousemove', function (e) {
          clearTimeout(tooltipTimeout);
          var selectionRange = editor.selection.getRange();
          if (selectionRange.isEmpty()) {
            var pointerPosition = editor.renderer.screenToTextCoordinates(e.clientX + 5, e.clientY);
            var endTestPosition = editor.renderer.screenToTextCoordinates(e.clientX + 15, e.clientY);
            if (endTestPosition.column !== pointerPosition.column) {
              var token = editor.session.getTokenAt(pointerPosition.row, pointerPosition.column);
              if (token !== null && token.parseLocation && !disableTooltip) {
                tooltipTimeout = window.setTimeout(function () {
                  var endCoordinates = editor.renderer.textToScreenCoordinates(pointerPosition.row, token.start);

                  var tooltipText = token.parseLocation.type === 'asterisk' ? options.expandStar : options.contextTooltip;
                  if (token.parseLocation.identifierChain) {
                    tooltipText += ' (' + $.map(token.parseLocation.identifierChain, function (identifier) { return identifier.name }).join('.') + ')';
                  } else if (token.parseLocation.function) {
                    tooltipText += ' (' + token.parseLocation.function + ')';
                  }
                  contextTooltip.show(tooltipText, endCoordinates.pageX, endCoordinates.pageY + editor.renderer.lineHeight + 3);
                }, 500);
              } else {
                hideContextTooltip();
              }
              if (lastHoveredToken !== token) {
                clearActiveMarkers();
                if (token !== null && token.parseLocation) {
                  markLocation(token.parseLocation);
                }
                lastHoveredToken = token;
              }
            } else {
              clearActiveMarkers();
              lastHoveredToken = null;
            }
          }
        });

        disposeFunctions.push(function () {
          editor.off('mousemove', mousemoveListener);
        });

        var inputListener = editor.on('input', function (e) {
          clearActiveMarkers();
          lastHoveredToken = null;
        });

        disposeFunctions.push(function () {
          editor.off('input', mousemoveListener);
        });

        var mouseoutListener = function (e) {
          clearActiveMarkers();
          clearTimeout(tooltipTimeout);
          contextTooltip.hide();
          lastHoveredToken = null;
        };

        editor.container.addEventListener('mouseout', mouseoutListener);

        disposeFunctions.push(function () {
          editor.container.removeEventListener('mouseout', mouseoutListener);
        });

        var contextmenuListener = function (e) {
          var selectionRange = editor.selection.getRange();
          huePubSub.publish('sql.context.popover.hide');
          if (selectionRange.isEmpty()) {
            var pointerPosition = editor.renderer.screenToTextCoordinates(e.clientX + 5, e.clientY);
            var token = editor.session.getTokenAt(pointerPosition.row, pointerPosition.column);

            if (token !== null && typeof token.parseLocation !== 'undefined') {
              var range = markLocation(token.parseLocation);
              var startCoordinates = editor.renderer.textToScreenCoordinates(range.start.row, range.start.column);
              var endCoordinates = editor.renderer.textToScreenCoordinates(range.end.row, range.end.column);
              huePubSub.publish('sql.context.popover.show', {
                data: token.parseLocation,
                sourceType: snippet.type(),
                defaultDatabase: snippet.database(),
                pinEnabled: true,
                source: {
                  left: startCoordinates.pageX - 3,
                  top: startCoordinates.pageY,
                  right: endCoordinates.pageX - 3,
                  bottom: endCoordinates.pageY + editor.renderer.lineHeight
                }
              });
              e.preventDefault();
              return false;
            }
          }
        };

        var contextmenuListener = editor.container.addEventListener('contextmenu', contextmenuListener);

        disposeFunctions.push(function () {
          editor.container.removeEventListener('contextmenu', contextmenuListener);
        });

      }());

      editor.previousSize = 0;

      // TODO: Get rid of this
      var idInterval = window.setInterval(function(){
        editor.session.getMode().$id = snippet.getAceMode(); // forces the id again because of Ace command internals
      }, 100);

      disposeFunctions.push(function () {
        window.clearInterval(idInterval);
      });

      editor.middleClick = false;
      var mousedownListener = editor.on('mousedown', function (e) {
        if (e.domEvent.which == 2) { // middle click
          editor.middleClick = true;
          var tempText = editor.getSelectedText();
          if (e.$pos) {
            editor.session.insert(e.$pos, tempText);
          }
          window.setTimeout(function () {
            editor.middleClick = false;
            if (e.$pos) {
              editor.moveCursorTo(e.$pos.row, e.$pos.column + tempText.length);
            }
          }, 200);
        }
      });

      disposeFunctions.push(function () {
        editor.off('mousedown', mousedownListener);
      });

      var aceReplaceSub = huePubSub.subscribe('ace.replace', function (data) {
        var Range = ace.require('ace/range').Range;
        var range = new Range(data.location.first_line - 1, data.location.first_column - 1, data.location.last_line - 1, data.location.last_column - 1);
        editor.getSession().getDocument().replace(range, data.text);
      });

      disposeFunctions.push(function () {
        aceReplaceSub.remove();
      });

      var clickListener = editor.on('click', function (e) {
        editor.clearErrorsAndWarnings();
      });

      disposeFunctions.push(function () {
        editor.off('click', clickListener);
      });

      var changeListener = editor.on("change", function (e) {
        if (snippet.getAceMode() === 'ace/mode/hive' || snippet.getAceMode() === 'ace/mode/impala') {
          aceSqlWorker.postMessage({ text: editor.getValue(), type: snippet.type() });
        }

        snippet.statement_raw(removeUnicodes(editor.getValue()));
        editor.session.getMode().$id = snippet.getAceMode();
        var currentSize = editor.session.getLength();
        if (currentSize != editor.previousSize && currentSize >= editorOptions.minLines && currentSize <= editorOptions.maxLines){
          editor.previousSize = editor.session.getLength();
          $(document).trigger("editorSizeChanged");
        }
        // automagically change snippet type
        var firstLine = editor.session.getLine(0);
        if (firstLine.indexOf("%") == 0 && firstLine.charAt(firstLine.length - 1) == " ") {
          var availableSnippets = snippet.availableSnippets;
          var removeFirstLine = false;
          for (var i = 0; i < availableSnippets.length; i++) {
            if ($.trim(firstLine.substr(1)) == availableSnippets[i].type()) {
              snippet.type(availableSnippets[i].type());
              removeFirstLine = true;
              break;
            }
          }
          if (removeFirstLine) {
            editor.session.remove(new AceRange(0, 0, 0, 200));
          }
        }
      });

      disposeFunctions.push(function () {
        editor.off("change", changeListener);
      });

      editor.commands.addCommand({
        name: "execute",
        bindKey: {win: "Ctrl-Enter", mac: "Command-Enter|Ctrl-Enter"},
        exec: function () {
          snippet.statement_raw(removeUnicodes(editor.getValue()));
          snippet.execute();
        }
      });

      editor.commands.addCommand({
        name: "new",
        bindKey: {win: "Ctrl-e", mac: "Command-e"},
        exec: function () {
          huePubSub.publish('editor.create.new');
        }
      });

      editor.commands.addCommand({
        name: "save",
        bindKey: {win: "Ctrl-s", mac: "Command-s|Ctrl-s"},
        exec: function () {
          huePubSub.publish('editor.save');
        }
      });

      editor.commands.addCommand({
        name: "format",
        bindKey: {win: "Ctrl-i|Ctrl-Shift-f|Ctrl-Alt-l", mac: "Command-i|Ctrl-i|Ctrl-Shift-f|Command-Shift-f|Ctrl-Shift-l|Cmd-Shift-l"},
        exec: function () {
          if (['ace/mode/hive', 'ace/mode/impala', 'ace/mode/sql', 'ace/mode/mysql', 'ace/mode/pgsql', 'ace/mode/sqlite', 'ace/mode/oracle'].indexOf(snippet.getAceMode()) > -1) {
            $.post("/notebook/api/format", {
              statements: editor.getSelectedText() != '' ? editor.getSelectedText() : editor.getValue()
            }, function(data) {
              if (data.status == 0) {
                 if (editor.getSelectedText() != '') {
                  editor.session.replace(editor.session.selection.getRange(), data.formatted_statements);
                } else {
                  editor.setValue(data.formatted_statements);
                  snippet.statement_raw(removeUnicodes(editor.getValue()));
                }
              }
            });
          }
        }
      });

      editor.commands.addCommand({
        name: "gotolinealternative",
        bindKey: {win: "Ctrl-j", mac: "Command-j|Ctrl-j"},
        exec: editor.commands.commands['gotoline'].exec
      });


      var isNewStatement = function () {
        return /^\s*$/.test(editor.getValue()) || /^.*;\s*$/.test(editor.getTextBeforeCursor());
      };

      var insertTableAtCursorSub = huePubSub.subscribe('editor.insert.table.at.cursor', function(details) {
        if ($el.data('last-active-editor')) {
          var qualifiedName = snippet.database() == details.database ? details.name : details.database + '.' + details.name;
          if (isNewStatement()) {
            editor.session.insert(editor.getCursorPosition(), 'SELECT * FROM ' + qualifiedName + ' LIMIT 100;');
          } else {
            editor.session.insert(editor.getCursorPosition(), ' ' + qualifiedName + ' ');
          }
        }
      });

      disposeFunctions.push(function () {
        insertTableAtCursorSub.remove();
      });

      var insertColumnAtCursorSub = huePubSub.subscribe('editor.insert.column.at.cursor', function(details) {
        if ($el.data('last-active-editor')) {
          if (isNewStatement()) {
            var qualifiedFromName = snippet.database() == details.database ? details.table : details.database + '.' + details.table;
            editor.session.insert(editor.getCursorPosition(), 'SELECT '  + details.name + ' FROM ' + qualifiedFromName + ' LIMIT 100;');
          } else {
            editor.session.insert(editor.getCursorPosition(), ' ' + details.name + ' ');
          }
        }
      });

      disposeFunctions.push(function () {
        insertColumnAtCursorSub.remove();
      });

      var dblClickHdfsItemSub = huePubSub.subscribe("assist.dblClickHdfsItem", function(assistHdfsEntry) {
        if ($el.data("last-active-editor")) {
          editor.session.insert(editor.getCursorPosition(), "'" + assistHdfsEntry.path + "'");
        }
      });

      disposeFunctions.push(function () {
        dblClickHdfsItemSub.remove();
      });


      var dblClickGitItemSub = huePubSub.subscribe("assist.dblClickGitItem", function(assistGitEntry) {
        if ($el.data("last-active-editor")) {
          editor.session.setValue(assistGitEntry.fileContent());
        }
      });

      disposeFunctions.push(function () {
        dblClickGitItemSub.remove();
      });

      var dblClickS3ItemSub = huePubSub.subscribe("assist.dblClickS3Item", function(assistS3Entry) {
        if ($el.data("last-active-editor")) {
          editor.session.insert(editor.getCursorPosition(), "'S3A://" + assistS3Entry.path + "'");
        }
      });

      disposeFunctions.push(function () {
        dblClickS3ItemSub.remove();
      });

      var sampleErrorInsertSub = huePubSub.subscribe('sample.error.insert.click', function(popoverEntry) {
          var table = popoverEntry.identifierChain[popoverEntry.identifierChain.length - 1]['name'];
          var text = "SELECT * FROM " + table + " LIMIT 100";
          editor.session.insert(editor.getCursorPosition(), text);
      });

      disposeFunctions.push(function () {
        sampleErrorInsertSub.remove();
      });

      var $tableDropMenu = $el.next('.table-drop-menu');
      var $identifierDropMenu = $tableDropMenu.find('.editor-drop-identifier');


      var hideDropMenu = function () {
        $tableDropMenu.css('opacity', 0);
        window.setTimeout(function () {
          $tableDropMenu.hide();
        }, 300);
      };

      var documentClickListener = function (event) {
        if ($tableDropMenu.find($(event.target)).length === 0) {
          hideDropMenu();
        }
      };

      $(document).on('click', documentClickListener);

      disposeFunctions.push(function () {
        $(document).off('click', documentClickListener);
      });


      var lastMeta = {};
      var draggableTextSub = huePubSub.subscribe('draggable.text.meta', function (meta) {
        lastMeta = meta;
        if (typeof meta !== 'undefined' && typeof meta.database !== 'undefined' && typeof meta.table !== 'undefined') {
          $identifierDropMenu.text(meta.database + '.' + meta.table)
        }
      });

      disposeFunctions.push(function () {
        draggableTextSub.remove();
      });

      var menu = ko.bindingHandlers.contextMenu.initContextMenu($tableDropMenu, $('.content-panel'));

      var setFromDropMenu = function (text) {
        var before = editor.getTextBeforeCursor();
        if (/\S+$/.test(before)) {
          text = " " + text;
        }
        editor.session.insert(editor.getCursorPosition(), text);
        menu.hide();
        editor.focus();
      };

      $tableDropMenu.find('.editor-drop-value').click(function () {
        setFromDropMenu(lastMeta.database + '.' + lastMeta.table);
      });

      $tableDropMenu.find('.editor-drop-select').click(function () {
        setFromDropMenu('SELECT * FROM ' + lastMeta.database + '.' + lastMeta.table + ' LIMIT 100;');
        $tableDropMenu.hide();
      });

      $tableDropMenu.find('.editor-drop-insert').click(function () {
        setFromDropMenu('INSERT INTO ' + lastMeta.database + '.' + lastMeta.table + ' VALUES ();');
      });

      $tableDropMenu.find('.editor-drop-update').click(function () {
        setFromDropMenu('UPDATE ' + lastMeta.database + '.' + lastMeta.table + ' SET ');
      });

      $tableDropMenu.find('.editor-drop-drop').click(function () {
        setFromDropMenu('DROP TABLE ' + lastMeta.database + '.' + lastMeta.table + ';');
      });

      $el.droppable({
        accept: ".draggableText",
        drop: function (e, ui) {
          var position = editor.renderer.screenToTextCoordinates(e.clientX, e.clientY);
          var text = ui.helper.text();
          if (lastMeta.type === 's3' || lastMeta.type === 'hdfs'){
            text = "'" + lastMeta.definition.path + "'";
          }
          editor.moveCursorToPosition(position);
          var before = editor.getTextBeforeCursor();
          if (lastMeta.database && lastMeta.table && ! lastMeta.column && /.*;|^\s*$/.test(before)) {
            menu.show(e);
          } else {
            if (/\S+$/.test(before) && before.charAt(before.length - 1) !== '.') {
              text = " " + text;
            }
            var after = editor.getTextAfterCursor();
            if (after.length > 0 && after.charAt(0) !== ' ' && text.charAt(text.length - 1) !== ' ') {
              text += " ";
            }
            editor.session.insert(position, text);
            position.column += text.length;
            editor.clearSelection();
          }
        }
      });

      var autocompleteTemporarilyDisabled = false;
      var autocompleteThrottle = -1;
      var afterExecListener = editor.commands.on('afterExec', function (e) {
        if (editor.getOption('enableLiveAutocompletion') && e.command.name === "insertstring") {
          if (/\S+\(\)$/.test(e.args)) {
            editor.moveCursorTo(editor.getCursorPosition().row, editor.getCursorPosition().column - 1);
            return;
          }
          window.clearTimeout(autocompleteThrottle);
          autocompleteThrottle = window.setTimeout(function () {
            var textBeforeCursor = editor.getTextBeforeCursor();
            var questionMarkMatch;
            if ($('.hue-ace-autocompleter').length > 0) {
              questionMarkMatch = textBeforeCursor.match(/select\s+(\? from \S+[^.]\s$)/i);
            } else {
              questionMarkMatch = textBeforeCursor.match(/select\s+(\? from \S+[^.]$)/i);
            }
            if (questionMarkMatch && $('.ace_autocomplete:visible').length === 0) {
              editor.moveCursorTo(editor.getCursorPosition().row, editor.getCursorPosition().column - (questionMarkMatch[1].length - 1));
              editor.removeTextBeforeCursor(1);
              window.setTimeout(function () {
                editor.execCommand("startAutocomplete");
              }, 1);
            } else if (/\.$/.test(textBeforeCursor)) {
              window.setTimeout(function () {
                editor.execCommand("startAutocomplete");
              }, 1);
            }
          }, 400);
        }
        editor.session.getMode().$id = snippet.getAceMode(); // forces the id again because of Ace command internals
        // if it's pig and before it's LOAD ' we disable the autocomplete and show a filechooser btn
        if (editor.session.getMode().$id === "ace/mode/pig" && e.args) {
          var textBefore = editor.getTextBeforeCursor();
          if ((e.args == "'" && textBefore.toUpperCase().indexOf("LOAD ") > -1 && textBefore.toUpperCase().indexOf("LOAD ") == textBefore.toUpperCase().length - 5)
              || textBefore.toUpperCase().indexOf("LOAD '") > -1 && textBefore.toUpperCase().indexOf("LOAD '") == textBefore.toUpperCase().length - 6) {
            if (editor.getOption('enableBasicAutocompletion')) {
              editor.disableAutocomplete();
              autocompleteTemporarilyDisabled = true;
            }
            var btn = editor.showFileButton();
            btn.on("click", function (ie) {
              ie.preventDefault();
              // TODO: Turn the ace file chooser into a component and remove css class references
              if (!$($(".ace-filechooser-content")).data('jHueFileChooser')) {
                if ($(".ace-filechooser-content").data("spinner") == null) {
                  $(".ace-filechooser-content").data("spinner", $(".ace-filechooser-content").html());
                } else {
                  $(".ace-filechooser-content").html($(".ace-filechooser-content").data("spinner"));
                }
                $(".ace-filechooser-content").jHueFileChooser({
                  onFileChoose: function (filePath) {
                    editor.session.insert(editor.getCursorPosition(), filePath + "'");
                    editor.hideFileButton();
                    if (autocompleteTemporarilyDisabled) {
                      editor.enableAutocomplete();
                      autocompleteTemporarilyDisabled = false;
                    }
                    $(".ace-filechooser").hide();
                  },
                  selectFolder: false,
                  createFolder: false
                });
              }
              $(".ace-filechooser").css({ "top": $(ie.currentTarget).position().top, "left": $(ie.currentTarget).position().left}).show();
            });
          } else {
            editor.hideFileButton();
            if (autocompleteTemporarilyDisabled) {
              editor.enableAutocomplete();
              autocompleteTemporarilyDisabled = false;
            }
          }
          if (e.args != "'" && textBefore.toUpperCase().indexOf("LOAD '") > -1 && textBefore.toUpperCase().indexOf("LOAD '") == textBefore.toUpperCase().length - 6) {
            editor.hideFileButton();
            if (autocompleteTemporarilyDisabled) {
              editor.enableAutocomplete();
              autocompleteTemporarilyDisabled = false;
            }
          }
        }
      });

      disposeFunctions.push(function () {
        editor.commands.off('afterExec', afterExecListener);
      });
      editor.$blockScrolling = Infinity;
      snippet.ace(editor);
    },

    update: function (element, valueAccessor) {
      var options = ko.unwrap(valueAccessor());
      var snippet = options.snippet;
      if (snippet.ace()) {
        var editor = snippet.ace();
        if (typeof options.readOnly !== 'undefined'){
          editor.setReadOnly(options.readOnly);
        }
        var range = options.highlightedRange ? options.highlightedRange() : null;
        editor.session.setMode(snippet.getAceMode());
        if (range && JSON.stringify(range.start) !== JSON.stringify(range.end)) {
          var conflictingWithErrorMarkers = false;
          if (editor.session.$backMarkers) {
            for (var marker in editor.session.$backMarkers) {
              if (editor.session.$backMarkers[marker].clazz === 'ace_error-line') {
                var errorRange = editor.session.$backMarkers[marker].range;
                if (range.start.row <= errorRange.end.row && range.end.row >= errorRange.start.row) {
                  conflictingWithErrorMarkers = true;
                }
              }
              if (editor.session.$backMarkers[marker].clazz === 'highlighted') {
                editor.session.removeMarker(editor.session.$backMarkers[marker].id);
              }
            }
          }
          if (!conflictingWithErrorMarkers) {
            editor.session.addMarker(new AceRange(range.start.row, range.start.column, range.end.row, range.end.column), 'highlighted', 'line');
            ace.require('ace/lib/dom').importCssString('.highlighted {\
                background-color: #E3F7FF;\
                position: absolute;\
            }');
            editor.scrollToLine(range.start.row, true, true, function () {});
          }
        }
        try {
          editor._emit('change')
        }
        catch (e){}
      }
    }
  };

  ko.bindingHandlers.medium = {
    init: function (element, valueAccessor, allBindings) {
      var editor = new MediumEditor($(element), {
        buttons: ['header1', 'header2', 'bold', 'italic', 'underline', 'quote', 'anchor', 'orderedlist', 'unorderedlist', 'pre', 'outdent', 'indent'],
        buttonLabels: 'fontawesome',
        anchorTarget: true,
        anchorInputPlaceholder: '${ _("Paste or type a link") }',
        anchorInputCheckboxLabel: '${ _("Open in new window") }',
        firstHeader: 'h2',
        secondHeader: 'h3'
      });
      $(element).on('blur', function () {
        allBindings().value($(element).html())
      });
    }
  };

  ko.bindingHandlers.verticalSlide = {
    init: function(element, valueAccessor) {
      if (ko.utils.unwrapObservable(valueAccessor())) {
        $(element).show();
      } else {
        $(element).hide();
      }
    },
    update: function(element, valueAccessor) {
      if (ko.utils.unwrapObservable(valueAccessor())) {
        $(element).slideDown('fast');
      } else {
        $(element).slideUp('fast');
      }
    }
  };

  ko.bindingHandlers.dblclick = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var fn = valueAccessor();
      $(element).dblclick(function () {
        var data = ko.dataFor(this);
        fn.call(viewModel, data);
      });
    }
  };

  ko.bindingHandlers.hueChecked = {
    after: ['value', 'attr'],
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var selectedValues = valueAccessor();

      var updateCheckedState = function () {
        ko.utils.toggleDomNodeCssClass(element, 'fa-check', selectedValues.indexOf(viewModel) > -1);
      };

      ko.utils.registerEventHandler(element, 'click', function () {
        var currentIndex = selectedValues.indexOf(viewModel);
        if (currentIndex === -1) {
          selectedValues.push(viewModel);
        } else if (currentIndex > -1) {
          selectedValues.splice(currentIndex, 1);
        }
      });

      selectedValues.subscribe(updateCheckedState);
      updateCheckedState();
    }
  };

  ko.bindingHandlers.hueCheckbox = {
    after: ['value', 'attr'],
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var value = valueAccessor();
      $(element).addClass('hueCheckbox fa');

      var updateCheckedState = function () {
        ko.utils.toggleDomNodeCssClass(element, 'fa-check', value());
      };

      ko.utils.registerEventHandler(element, 'click', function () {
        value(!value());
      });

      value.subscribe(updateCheckedState);
      updateCheckedState();
    }
  };

  ko.bindingHandlers.hueCheckAll = {
    init: function (element, valueAccessor, allBindings) {
      var allValues = ko.utils.unwrapObservable(valueAccessor()).allValues;
      var selectedValues = ko.utils.unwrapObservable(valueAccessor()).selectedValues;

      var updateCheckedState = function () {
        ko.utils.toggleDomNodeCssClass(element, 'fa-check', selectedValues().length === allValues().length);
        ko.utils.toggleDomNodeCssClass(element, 'fa-minus hue-uncheck', selectedValues().length > 0 && selectedValues().length !== allValues().length);
      };

      ko.utils.registerEventHandler(element, 'click', function () {
        if (selectedValues().length == 0) {
          selectedValues(allValues().slice(0));
        } else {
          selectedValues([]);
        }
      });

      selectedValues.subscribe(updateCheckedState);
      allValues.subscribe(updateCheckedState);
      updateCheckedState();
    }
  };

  /**
   * This binding limits the rendered items based on what is visible within a scrollable container. It supports
   * multiple any amount of nested children with foreachVisible bindings
   *
   * The minHeight parameter is the initial expected rendered height of each entry, once rendered the real
   * height is used. It keeps a number of elements above and below the visible elements to make slow scrolling
   * smooth.
   *
   * The height of the container element has to be less than or equal to the inner height of the window.
   *
   * Example:
   *
   * <div class="container" style="overflow-y: scroll; height: 100px">
   *  <ul data-bind="foreachVisible: { data: items, minHeight: 20, container: '.container' }">
   *    <li>...</li>
   *  </ul>
   * </div>
   *
   * For tables the binding has to be attached to the tbody element:
   *
   * <div class="container" style="overflow-y: scroll; height: 100px">
   *  <table>
   *    <thead>...</thead>
   *    <tbody data-bind="foreachVisible: { data: items, minHeight: 20, container: '.container' }>
   *      <tr>...</tr>
   *    </tbody>
   *  </ul>
   * </div>
   *
   * Currently the binding only supports one element inside the bound element otherwise the height
   * calculations will be off. In other words this will make it go bonkers:
   *
   * <div class="container" style="overflow-y: scroll; height: 100px">
   *  <ul data-bind="foreachVisible: { data: items, minHeight: 20, container: '.container' }">
   *    <li>...</li>
   *    <li style="display: none;">...</li>
   *  </ul>
   * </div>
   *
   */
  ko.bindingHandlers.foreachVisible = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      return ko.bindingHandlers.template.init(element, function () {
        return {
          'foreach': [],
          'templateEngine': ko.nativeTemplateEngine.instance
        };
      }, allBindings, viewModel, bindingContext);
    },

    update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var options = valueAccessor();
      var $element = $(element);
      var isTable = false;

      if ($element.parent().is('table')) {
        $element = $element.parent();
        isTable = true;
      }

      var $container = $element.closest(options.container);

      var id = Math.random();

      // This is possibly a parent element that has the foreachVisible binding
      var $parentFVElement = bindingContext.$parentForeachVisible || null;
      var parentId = bindingContext.$parentForeachVisibleId || -1;
      // This is the element from the parent foreachVisible rendered element that contains
      // this one or container for root
      var $parentFVOwnerElement = $container;
      $element.data('parentForeachVisible', $parentFVElement);

      var depth = bindingContext.$depth || 0;

      // Locate the owning element if within another foreach visible binding
      if ($parentFVElement) {
        var myOffset = $element.offset().top;
        $parentFVElement.children().each(function (idx, child) {
          var $child = $(child);
          if (myOffset > $child.offset().top) {
            $parentFVOwnerElement = $child;
          } else {
            return false;
          }
        });
      }

      if ($parentFVOwnerElement.data('disposalFunction')) {
        $parentFVOwnerElement.data('disposalFunction')();
        $parentFVOwnerElement.data('lastKnownHeights', null);
      }

      var entryMinHeight = options.minHeight;
      var allEntries = ko.utils.unwrapObservable(options.data);

      var visibleEntryCount = 0;
      var incrementLimit = 0; // The diff required to re-render, set to visibleCount below
      var elementIncrement = 0; // Elements to add on either side of the visible elements, set to 3x visibleCount

      var updateVisibleEntryCount = function () {
        // TODO: Drop the window innerHeight limitation.
        // Sometimes after resizeWrapper() is called the reported innerHeight of the $container is the same as
        // the wrapper causing the binding to render all the items. This limits the visibleEntryCount to the
        // window height.
        var newEntryCount = Math.ceil(Math.min($(window).innerHeight(), $container.innerHeight()) / entryMinHeight);
        if (newEntryCount !== visibleEntryCount) {
          var diff = newEntryCount - visibleEntryCount;
          elementIncrement = options.elementIncrement || 25;
          incrementLimit = options.incrementLimit || 5;
          visibleEntryCount = newEntryCount;
          endIndex += diff;
          huePubSub.publish('foreach.visible.update', id);
        }
      };

      // TODO: Move intervals to webworker
      var updateCountInterval = setInterval(updateVisibleEntryCount, 300);
      updateVisibleEntryCount();

      // In case this element was rendered before use the last known indices
      var startIndex = Math.max($parentFVOwnerElement.data('startIndex') || 0, 0);
      var endIndex = Math.min($parentFVOwnerElement.data('endIndex') || (visibleEntryCount + elementIncrement), allEntries.length - 1);

      var huePubSubs = [];

      var scrollToIndex = function (idx, offset, entry) {
        var lastKnownHeights = $parentFVOwnerElement.data('lastKnownHeights');
        if (! lastKnownHeights) {
          return;
        }
        var top = 0;
        for (var i = 0; i < idx; i++) {
          top += lastKnownHeights[i];
        }
        window.setTimeout(function () {
          $('.assist-db-scrollable').stop().animate({ scrollTop: top + offset }, '500', 'swing', function () {
            huePubSub.publish('assist.db.scrollToComplete', entry);
          });
        }, 0);

      };

      huePubSubs.push(huePubSub.subscribe('assist.db.scrollTo', function (targetEntry) {
        var foundIndex = -1;
        $.each(allEntries, function (idx, entry) {
          if (targetEntry === entry) {
            foundIndex = idx;
            return false;
          }
        });
        if (foundIndex !== -1) {
          var offset = depth > 0 ? $parentFVOwnerElement.position().top : 0;
          scrollToIndex(foundIndex, offset, targetEntry);
        }
      }));

      var childBindingContext = bindingContext.createChildContext(
          bindingContext.$rawData,
          null,
          function(context) {
            ko.utils.extend(context, {
              $parentForeachVisible: $element,
              $parentForeachVisibleId: id,
              $depth: depth + 1,
              $indexOffset: function() {
                return startIndex;
              }
            });
          });

      var withNiceScroll = !options.disableNiceScroll;
      var $wrapper = $element.parent();
      if (!$wrapper.hasClass('foreach-wrapper')) {
        $wrapper = $('<div>').css({
          'position': 'relative',
          'width': '100%'
        }).addClass('foreach-wrapper').insertBefore($element);
        $element.css({
          'position': 'absolute',
          'top': 0,
          'width': '100%'
        }).appendTo($wrapper);

        if ($.fn.niceScroll && withNiceScroll) {
          hueUtils.initNiceScroll($container, {
            horizrailenabled: false
          });
        }
      } else {
        window.setTimeout(function(){
          if ($.fn.niceScroll && withNiceScroll) {
            $container.getNiceScroll().resize();
          }
        }, 200);
      }

      // This is kept up to date with the currently rendered elements, it's used to keep track of any
      // height changes of the elements.
      var renderedElements = [];

      if (! $parentFVOwnerElement.data('lastKnownHeights') || $parentFVOwnerElement.data('lastKnownHeights').length !== allEntries.length) {
        var lastKnownHeights = [];
        $.each(allEntries, function () {
          lastKnownHeights.push(entryMinHeight);
        });
        $parentFVOwnerElement.data('lastKnownHeights', lastKnownHeights);
      }

      var resizeWrapper = function () {
        var totalHeight = 0;
        var lastKnownHeights = $parentFVOwnerElement.data('lastKnownHeights');
        $.each(lastKnownHeights, function(idx, height) {
          totalHeight += height;
        });
        $wrapper.height(totalHeight + 'px');
        if ($.fn.niceScroll) {
          $container.getNiceScroll().resize();
        }
      };
      resizeWrapper();

      var updateLastKnownHeights = function () {
        if ($container.data('busyRendering')) {
          return;
        }
        var lastKnownHeights = $parentFVOwnerElement.data('lastKnownHeights');
        // Happens when closing first level and the third level is open, disposal tells the parents
        // to update their heights...
        if (!lastKnownHeights) {
          return;
        }
        var diff = false;
        $.each(renderedElements, function (idx, renderedElement) {
          // TODO: Figure out why it goes over index at the end scroll position
          if (startIndex + idx < lastKnownHeights.length) {
            var renderedHeight = $(renderedElement).outerHeight(true);
            if (renderedHeight > 5 && lastKnownHeights[startIndex + idx] !== renderedHeight) {
              lastKnownHeights[startIndex + idx] = renderedHeight;
              diff = true;
            }
          }
        });
        // Only resize if a difference in height was noticed.
        if (diff) {
          $parentFVOwnerElement.data('lastKnownHeights', lastKnownHeights);
          resizeWrapper();
        }
      };

      var updateHeightsInterval = window.setInterval(updateLastKnownHeights, 600);

      huePubSubs.push(huePubSub.subscribe('foreach.visible.update.heights', function (targetId) {
        if (targetId === id) {
          clearInterval(updateHeightsInterval);
          updateLastKnownHeights();
          huePubSub.publish('foreach.visible.update.heights', parentId);
          updateHeightsInterval = window.setInterval(updateLastKnownHeights, 600);
        }
      }));

      updateLastKnownHeights();

      var positionList = function () {
        var lastKnownHeights = $parentFVOwnerElement.data('lastKnownHeights');
        if (! lastKnownHeights) {
          return;
        }
        var top = 0;
        for (var i = 0; i < startIndex; i++) {
          top += lastKnownHeights[i];
        }
        $element.css('top', top + 'px');
      };

      var afterRender = function () {
        renderedElements = isTable ? $element.children('tbody').children() : $element.children();
        $container.data('busyRendering', false);
        huePubSub.publish('foreach.visible.update.heights', id);
      };

      var render = function () {
        if (endIndex === 0 && allEntries.length > 1 || endIndex < 0) {
          ko.bindingHandlers.template.update(element, function () {
            return {
              'foreach': [],
              'templateEngine': ko.nativeTemplateEngine.instance,
              'afterRender': function () {
                // This is called once for each added element (not when elements are removed)
                clearTimeout(throttle);
                throttle = setTimeout(afterRender, 0);
              }
            };
          }, allBindings, viewModel, childBindingContext);
          return;
        }
        $container.data('busyRendering', true);
        // Save the start and end index for when the list is removed and is shown again.
        $parentFVOwnerElement.data('startIndex', startIndex);
        $parentFVOwnerElement.data('endIndex', endIndex);
        positionList();


        // This is to ensure that our afterRender is called (the afterRender of KO below isn't called
        // when only elements are removed)
        var throttle = setTimeout(afterRender, 0);

        ko.bindingHandlers.template.update(element, function () {
          return {
            'foreach': allEntries.slice(startIndex, endIndex + 1),
            'templateEngine': ko.nativeTemplateEngine.instance,
            'afterRender': function () {
              // This is called once for each added element (not when elements are removed)
              clearTimeout(throttle);
              throttle = setTimeout(afterRender, 0);
            }
          };
        }, allBindings, viewModel, childBindingContext);
      };

      var setStartAndEndFromScrollTop = function () {
        var lastKnownHeights = $parentFVOwnerElement.data('lastKnownHeights');

        var parentSpace = 0;

        var $lastParent = $parentFVElement;
        var $lastRef = $element;
        var $parentOwner;

        while ($lastParent) {
          // Include the header, parent() is .foreach-wrapper, parent().parent() is the container (ul or div)
          var lastRefOffset = $lastRef.parent().parent().offset().top;
          var lastAddedSpace = 0;
          $lastParent.children().each(function (idx, child) {
            var $child = $(child);
            if (lastRefOffset > $child.offset().top) {
              lastAddedSpace = $child.outerHeight(true);
              parentSpace += lastAddedSpace;
              if ($lastParent === $parentFVElement) {
                $parentOwner = $child;
              }
            } else {
              // Remove the height of the child which is the parent of this
              parentSpace -= lastAddedSpace;
              return false;
            }
          });
          parentSpace += $lastParent.position().top;
          $lastRef = $lastParent;
          $lastParent = $lastParent.data('parentForeachVisible');
        }
        var position = Math.min($container.scrollTop() - parentSpace, $wrapper.height());

        for (var i = 0; i < lastKnownHeights.length; i++) {
          position -= lastKnownHeights[i];
          if (position <= 0) {
            startIndex = Math.max(i - elementIncrement, 0);
            endIndex = Math.min(allEntries.length - 1, i + elementIncrement + visibleEntryCount);
            break;
          }
        }
      };

      var renderThrottle = -1;
      var lastScrollTop = -1;
      var onScroll = function () {
        if (startIndex > incrementLimit && Math.abs(lastScrollTop - $container.scrollTop()) < (incrementLimit * options.minHeight)) {
          return;
        }
        lastScrollTop = $container.scrollTop();

        setStartAndEndFromScrollTop();
        if (typeof options.fetchMore !== 'undefined' && endIndex === allEntries.length - 1) {
          options.fetchMore();
        }

        clearTimeout(renderThrottle);
        if (Math.abs($parentFVOwnerElement.data('startIndex') - startIndex) > incrementLimit ||
            Math.abs($parentFVOwnerElement.data('endIndex') - endIndex) > incrementLimit) {
          renderThrottle = setTimeout(render, 0);
        }
      };

      huePubSubs.push(huePubSub.subscribe('foreach.visible.update', function (callerId) {
        if (callerId === id && endIndex > 0) {
          setStartAndEndFromScrollTop();
          clearTimeout(renderThrottle);
          renderThrottle = setTimeout(render, 0);
        }
      }));

      $container.bind('scroll', onScroll);

      $parentFVOwnerElement.data('disposalFunction', function () {
        setTimeout(function () {
          huePubSub.publish('foreach.visible.update.heights', parentId);
        }, 0);
        huePubSubs.forEach(function (pubSub) {
          pubSub.remove();
        });
        $container.unbind('scroll', onScroll);
        clearInterval(updateCountInterval);
        clearInterval(updateHeightsInterval);
        $parentFVOwnerElement.data('disposalFunction', null);
      });

      if (typeof options.pubSubDispose !== 'undefined') {
        huePubSubs.push(huePubSub.subscribe(options.pubSubDispose, $parentFVOwnerElement.data('disposalFunction')));
      }

      ko.utils.domNodeDisposal.addDisposeCallback($wrapper[0], $parentFVOwnerElement.data('disposalFunction'));

      setStartAndEndFromScrollTop();
      render();
    }
  };
  ko.expressionRewriting.bindingRewriteValidators['foreachVisible'] = false;
  ko.virtualElements.allowedBindings['foreachVisible'] = true;

  ko.bindingHandlers.hueach = {
    init: function (element, valueAccessor, allBindings) {
      var valueAccessorBuilder = function () {
        return {
          data: ko.observableArray([])
        }
      };
      ko.bindingHandlers.foreach.init(element, valueAccessorBuilder, allBindings);
    },
    update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var $element = $(element),
        $parent = $element.parent(),
        data = typeof valueAccessor().data === 'function' ? valueAccessor().data() : valueAccessor().data,
        considerStretching = valueAccessor().considerStretching || false,
        itemHeight = valueAccessor().itemHeight || 22,
        scrollable = valueAccessor().scrollable || 'body',
        scrollUp = valueAccessor().scrollUp || false,
        scrollableOffset = valueAccessor().scrollableOffset || 0,
        disableHueEachRowCount = valueAccessor().disableHueEachRowCount || 0,
        forceRenderSub = valueAccessor().forceRenderSub || null,
        renderTimeout = -1,
        dataHasChanged = true;

      var wrappable = $(element);
      if (data.length > disableHueEachRowCount) {
        if ($parent.is('table')) {
          wrappable = $parent;
          $parent = wrappable.parent();
        }

        if (!wrappable.parent().hasClass('hueach')) {
          wrappable.wrap('<div class="hueach"></div>');
          $parent = wrappable.parent();
          wrappable.css({
            position: 'absolute',
            width: '100%'
          });
        }

        $parent.height(data.length * itemHeight);
        if (wrappable.is('table')) {
          $parent.height($parent.height() + (data.length > 0 ? itemHeight : 0));
        }
      }

      try {
        if (ko.utils.domData.get(element, 'originalData') && JSON.stringify(ko.utils.domData.get(element, 'originalData')) === JSON.stringify(data)) {
          dataHasChanged = false;
        }
      }
      catch (e) {
      }

      if (dataHasChanged) {
        ko.utils.domData.set(element, 'originalData', data);
      }

      var startItem = 0, endItem = 0;
      var valueAccessorBuilder = function () {
        return {
          data: ko.utils.domData.get(element, 'originalData') ? ko.observableArray(ko.utils.domData.get(element, 'originalData').slice(startItem, endItem)) : []
        }
      }

      var render = function () {
        if ($parent.parents('.hueach').length === 0) {
          var heightCorrection = 0, fluidCorrection = 0;
          var scrollTop = $parent.parents(scrollable).scrollTop();
          if (wrappable.is('table')) {
            if (scrollTop < scrollableOffset + itemHeight) {
              wrappable.find('thead').css('opacity', '1');
            }
            else {
              wrappable.find('thead').css('opacity', '0');
            }
          }
          else {
            wrappable.children(':visible').each(function (cnt, child) {
              if ($(child).height() >= itemHeight) {
                heightCorrection += $(child).height();
              }
            });
            if (heightCorrection > 0) {
              ko.utils.domData.set(element, 'heightCorrection', heightCorrection);
            }
            if (heightCorrection == 0 && ko.utils.domData.get(element, 'heightCorrection')) {
              fluidCorrection = ko.utils.domData.get(element, 'heightCorrection') - 20;
            }
          }
          startItem = Math.max(0, Math.floor(Math.max(1, (scrollTop - heightCorrection - fluidCorrection - scrollableOffset)) / itemHeight) - 10);
          if (wrappable.is('table') && startItem % 2 == 1) {
            startItem--;
          }
          endItem = Math.min(startItem + Math.ceil($parent.parents(scrollable).height() / itemHeight) + 20, data.length);
          wrappable.css('top', ((startItem * itemHeight) + fluidCorrection) + 'px');
        }
        else {
          startItem = 0, endItem = data.length;
        }
        bindingContext.$indexOffset = function () {
          return startItem
        }
        ko.bindingHandlers.foreach.update(element, valueAccessorBuilder, allBindings, viewModel, bindingContext);
      }


      $parent.parents(scrollable).off('scroll');
      huePubSub.publish('scrollable.scroll.off', scrollable);

      $parent.parents(scrollable).on('scroll', render);
      if (scrollUp){
        $parent.parents(scrollable).jHueScrollUp();
      }

      if ($parent.parents('.hueach').length > 0) {
        window.setTimeout(render, 100);
      }

      if (considerStretching) {
        huePubSub.subscribe('assist.stretchDown', function () {
          window.clearTimeout(renderTimeout);
          renderTimeout = window.setTimeout(function () {
            ko.utils.domData.set(element, 'hasStretched', true);
            render();
          }, 300);
        });
      }

      if (forceRenderSub) {
        huePubSub.subscribe(forceRenderSub, function () {
          window.setTimeout(render, 300);
        });
      }

      window.clearTimeout(renderTimeout);
      renderTimeout = window.setTimeout(function () {
        ko.utils.domData.set(element, 'hasStretched', true);
        render();
      }, 300);

    }
  };

  ko.bindingHandlers.niceScroll = {
    init: function (element, valueAccessor, allBindings) {
      var options = valueAccessor() || {};
      if ((typeof options.enable === 'undefined' || options.enable) && $.fn.niceScroll) {
        hueUtils.initNiceScroll($(element), options);
        $(element).addClass('nicescrollified');
        huePubSub.subscribe('nicescroll.resize', function () {
          $(element).getNiceScroll().resize();
        });
        ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
          $(element).getNiceScroll().remove();
        });
      }
    }
  };


  ko.bindingHandlers.plotly = {
    init: function (element, valueAccessor, allBindings) {
      var options = valueAccessor() || {};
      if (Plotly){
        Plotly.plot(element, options.data || [], options.layout || {}, {displaylogo: false});
      }
    }
  };

  ko.bindingHandlers.dockable = {
    init: function (element, valueAccessor, allBindings) {
      var options = valueAccessor() || {};
      var scrollable = options.scrollable ? options.scrollable : window;

      $(element).addClass('dockable');

      var initialTopPosition = -1;
      var initialSize = {
        w: $(element).width(),
        h: $(element).outerHeight() + (options.jumpCorrection || 0)
      };

      var ghost = $('<div>').css({'display': 'none', 'height': initialSize.h}).insertBefore($(element));

      function dock() {
        if (initialTopPosition == -1) {
          initialTopPosition = $(element).position().top;
        }
        if ($(scrollable).scrollTop() > initialTopPosition) {
          $(element).css({
            'position': 'fixed',
            'top': '82px',
            'width': initialSize.w + 'px'
          });
          ghost.show();
        }
        else {
          $(element).removeAttr('style');
          ghost.hide();
        }
      }

      if (options.nicescroll) {
        var checkForNicescrollInit = -1;
        checkForNicescrollInit = window.setInterval(function () {
          if ($(scrollable).hasClass('nicescrollified')) {
            window.clearTimeout(checkForNicescrollInit);
            $(scrollable).on('scroll', dock);
          }
        }, 200);
      }
      else {
        $(scrollable).on('scroll', dock);
      }

      huePubSub.subscribe('scrollable.scroll.off', function (scrollElement) {
        if (scrollElement === scrollable) {
          $(scrollable).on('scroll', dock);
        }
      });

    }
  };

  ko.bindingHandlers.autogrowInput = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var o = $.extend({
        minWidth: 0,
        maxWidth: 1000,
        comfortZone: 70
      }, valueAccessor());
      var minWidth = o.minWidth || $(element).width(),
        val = '',
        input = $(element),
        testSubject = $('<tester/>').css({
          position: 'absolute',
          top: -9999,
          left: -9999,
          width: 'auto',
          fontSize: input.css('fontSize'),
          fontFamily: input.css('fontFamily'),
          fontWeight: input.css('fontWeight'),
          letterSpacing: input.css('letterSpacing'),
          whiteSpace: 'nowrap'
        }),
        check = function () {
          if (val === (val = input.val())) {
            return;
          }
          var escaped = val.replace(/&/g, '&amp;').replace(/\s/g, ' ').replace(/</g, '&lt;').replace(/>/g, '&gt;');
          testSubject.html(escaped);
          var testerWidth = testSubject.width(),
            newWidth = (testerWidth + o.comfortZone) >= minWidth ? testerWidth + o.comfortZone : minWidth,
            currentWidth = input.width(),
            isValidWidthChange = (newWidth < currentWidth && newWidth >= minWidth) || (newWidth > minWidth && newWidth < o.maxWidth);
          if (isValidWidthChange) {
            input.width(newWidth);
          }
        };
      testSubject.insertAfter(element);
      ko.utils.registerEventHandler(element, 'keyup keydown blur update', check);
    }
  };

  ko.bindingHandlers.readonlyXML = {
    init: function (element, valueAccessor, allBindingsAccessor) {
      $(element).css({
        'min-height': '250px'
      });
      var editor = ace.edit(element);
      editor.setOptions({
        readOnly: true,
        maxLines: Infinity
      });
      editor.setTheme($.totalStorage("hue.ace.theme") || "ace/theme/hue");
      editor.getSession().setMode("ace/mode/xml");
      $(element).data('aceEditor', editor);
    },
    update: function (element, valueAccessor, allBindingsAccessor) {
      var value = ko.unwrap(valueAccessor());
      var options = ko.unwrap(allBindingsAccessor());
      if (typeof value !== 'undefined' && value !== '') { // allows highlighting static code
        if (options.path) {
          value = value[options.path];
        }
        $(element).data('aceEditor').setValue(value, -1)
      }
    }
  };

  ko.bindingHandlers.highlight = {
    init: function (element) {
      $(element).addClass('ace-highlight');
    },
    update: function (element, valueAccessor) {
      var options = $.extend({
        dialect: 'hive',
        value: '',
        formatted: false
      }, valueAccessor());

      var value = ko.unwrap(options.value);

      if (typeof value !== 'undefined' && value !== '') { // allows highlighting static code
        if (options.path) {
          value = value[options.path];
        }
        ace.require([
          'ace/mode/impala_highlight_rules',
          'ace/mode/hive_highlight_rules',
          'ace/mode/xml_highlight_rules',
          'ace/tokenizer',
          'ace/layer/text'
        ], function (impalaRules, hiveRules, xmlRules, tokenizer, text) {
          var res = [];

          var Tokenizer = tokenizer.Tokenizer;
          var Rules = hiveRules.HiveHighlightRules;
          if (options.dialect && ko.unwrap(options.dialect) == 'impala') {
            Rules = impalaRules.ImpalaHighlightRules;
          }

          var Text = text.Text;

          var tok = new Tokenizer(new Rules().getRules());
          var lines = value.split('\n');

          var renderSimpleLine = function(txt, stringBuilder, tokens) {
            var screenColumn = 0;
            var token = tokens[0];
            var value = token.value;
            if (value) {
              screenColumn = txt.$renderToken(stringBuilder, screenColumn, token, value);
            }
            for (var i = 1; i < tokens.length; i++) {
              token = tokens[i];
              value = token.value;
              try {
                screenColumn = txt.$renderToken(stringBuilder, screenColumn, token, value);
              }
              catch (e) {
                if (console && console.warn) {
                  console.warn(value, 'This token has some parsing errors and it has been rendered without highlighting.');
                }
                stringBuilder.push(value);
                screenColumn = screenColumn + value.length;
              }
            }
          };

          var additionalClass = '';
          if (!options.splitLines && !options.formatted) {
            additionalClass = 'pull-left';
          } else if (options.formatted) {
            additionalClass = 'ace-highlight-pre';
          }

          lines.forEach(function (line) {
            var renderedTokens = [];
            var tokens = tok.getLineTokens(line);

            if (tokens && tokens.tokens.length) {
              renderSimpleLine(new Text(document.createElement('div')), renderedTokens, tokens.tokens);
            }

            res.push('<div class="ace_line ' + additionalClass + '">' + renderedTokens.join('') + '&nbsp;</div>');
          });

          element.innerHTML = '<div class="ace_editor ace-hue"><div class="ace_layer" style="position: static;">' + res.join('') + '</div></div>';
        });
      }


    }
  };

  ko.bindingHandlers.ellipsis = {
    update: function (element, valueAccessor, allBindingsAccessor) {
      var value = ko.unwrap(valueAccessor());
      var $element = $(element);
      var chopLength = value.length ? value.length : 30;
      var text = typeof value === 'object' ? value.data : value;
      if (text.length > chopLength) {
        $element.attr('title', text);
        $element.text(text.substr(0, chopLength) + '...');
      }
      else {
        $element.text(text);
      }
    }
  };

  ko.bindingHandlers.select2Version4 = {
    init: function (el, valueAccessor, allBindingsAccessor, viewModel) {
      ko.utils.domNodeDisposal.addDisposeCallback(el, function () {
        $(el).select2('destroy');
      });

      var allBindings = allBindingsAccessor(),
        select2 = ko.utils.unwrapObservable(allBindings.select2Version4);

      $(el).select2(select2);
    },
    update: function (el, valueAccessor, allBindingsAccessor, viewModel) {
      var allBindings = allBindingsAccessor();

      if ("value" in allBindings) {
        if ((allBindings.select2Version4.multiple || el.multiple) && allBindings.value().constructor != Array) {
          $(el).val(allBindings.value().split(',')).trigger('change');
        }
        else {
          $(el).val(allBindings.value()).trigger('change');
        }
      } else if ("selectedOptions" in allBindings) {
        var converted = [];
        var textAccessor = function (value) {
          return value;
        };
        if ("optionsText" in allBindings) {
          textAccessor = function (value) {
            var valueAccessor = function (item) {
              return item;
            }
            if ("optionsValue" in allBindings) {
              valueAccessor = function (item) {
                return item[allBindings.optionsValue];
              }
            }
            var items = $.grep(allBindings.options(), function (e) {
              return valueAccessor(e) == value
            });
            if (items.length == 0 || items.length > 1) {
              return "UNKNOWN";
            }
            return items[0][allBindings.optionsText];
          }
        }
        $.each(allBindings.selectedOptions(), function (key, value) {
          converted.push({id: value, text: textAccessor(value)});
        });
        $(el).select2("data", converted);
      }
    }
  };


  ko.bindingHandlers.momentFromNow = {
    update: function (element, valueAccessor) {
      var options = ko.unwrap(valueAccessor());
      var $element = $(element);

      var value = typeof options.data === 'function' ? options.data() : options.data;

      function render() {
        $element.text(moment(value).fromNow());
        if (options.titleFormat) {
          $element.attr('title', moment(value).format(options.titleFormat));
        }
      }

      render();

      if (options.interval) {
        window.clearInterval($element.data('momentInterval'));
        $element.data('momentInterval', window.setInterval(render, options.interval));
      }
    }
  };

  ko.bindingHandlers.moment = {
    update: function (element, valueAccessor) {
      var options = ko.unwrap(valueAccessor());
      var $element = $(element);

      var value = typeof options.data === 'function' ? options.data() : options.data;

      function render() {
        if (options.format) {
          $element.text(moment(value).format(options.format));
        }
        else {
          $element.text(moment(value));
        }
      }
      render();
    }
  };


  ko.bindingHandlers.attachViewModelToElementData = {
    init: function (el, valueAccessor, allBindingsAccessor, viewModel) {
      $(el).data('__ko_vm', viewModel);
    }
  };

  ko.bindingHandlers.hdfsTree = {
    update: function (element, valueAccessor) {
      var options = ko.unwrap(valueAccessor());
      var $element = $(element);

      $element.empty();

      var value = typeof options.data === 'function' ? options.data() : options.data;
      $element.jHueHdfsTree({
        home: '',
        isS3: false,
        initialPath: options.path,
        withTopPadding: false,
        onPathChange: function (path) {
          options.selectedPath(path);
        }
      });

    }
  };

  ko.bindingHandlers.documentChooser = {
    init: function (element, valueAccessor) {
      var options = valueAccessor();
      var TYPE_MAP = {
        'hive': 'query-hive',
        'impala': 'query-impala',
        'java': 'query-java',
        'spark': 'query-spark2',
        'pig': 'query-pig',
        'sqoop': 'query-sqoop1',
        'distcp-doc': 'query-distcp',
        'mapreduce-doc': 'query-mapreduce',
        'hive-document-widget': 'query-hive',
        'impala-document-widget': 'query-impala',
        'java-document-widget': 'query-java',
        'spark-document-widget': 'query-spark2',
        'pig-document-widget': 'query-pig',
        'sqoop-document-widget': 'query-sqoop1',
        'distcp-document-widget': 'query-distcp',
        'shell-document-widget': 'query-shell',
        'mapreduce-document-widget': 'query-mapreduce',
      }
      var type = 'query-hive';
      if (options.type) {
        var tempType = options.type();
        if (tempType === 'function') {
          tempType = tempType();
        }
        type = TYPE_MAP[tempType] ? TYPE_MAP[tempType] : tempType;
      }
      var firstLoad = false;
      $(element).selectize({
        valueField: 'uuid',
        labelField: 'name',
        searchField: 'name',
        options: [],
        create: false,
        preload: true,
        dropdownParent: 'body',
        render: {
          option: function (item, escape) {
            return '<div>' +
              '<strong>' + escape(item.name) + '</strong><br>' +
              '<span class="muted">' + escape(item.description) + '</span>' +
              '</div>';
          }
        },
        load: function (query, callback) {
          if (query === '' && options.value && !firstLoad){
            firstLoad = true;
          }
          $.ajax({
            url: '/desktop/api2/docs/',
            data: {
              type: type,
              text: query,
              include_trashed: false,
              limit: 100
            },
            type: 'GET',
            error: function () {
              callback();
            },
            success: function (res) {
              callback(res.documents);
            }
          });
        },
        onChange: function (val) {
          if (options.value) {
            options.value(val);
          }
          if (options.document) {
            options.document(this.options[val]);
          }
          if (options.mappedDocument) {
            options.mappedDocument(ko.mapping.fromJS(this.options[val]));
          }
        },
        onLoad: function () {
          if (options.value) {
            this.setValue(options.value());
          }
          if (options.loading) {
            options.loading(false);
          }
        },
      });
    },

    update: function (element, valueAccessor) {
      var options = valueAccessor();
      if (options.value) {
        element.selectize.setValue(options.value());
      }
      if (options.dependentValue && options.dependentValue() !== '') {
        element.selectize.setValue(options.dependentValue());
        options.dependentValue('');
      }
    }
  };

  ko.bindingHandlers.tagsNotAllowed = {
    update: function (element, valueAccessor, allBindingsAccessor) {
      var $element = $(element);
      var params = allBindingsAccessor();
      var valueObservable = ko.isObservable(params) ? params : (params.textInput ? params.textInput : params.value);
      var value = valueObservable();
      var escaped = value.replace(/<|>/g, '');
      if (escaped !== value){
        $element.val(escaped);
      }
    }
  };

  ko.bindingHandlers.truncatedText = {
    update: function (element, valueAccessor, allBindingsAccessor) {
      var text = ko.isObservable(valueAccessor()) ? ko.utils.unwrapObservable(valueAccessor()) : valueAccessor();
      var length = ko.utils.unwrapObservable(allBindingsAccessor().maxLength) || 20;
      var truncated = '';
      if (typeof text !== 'undefined' && text !== null){
        truncated = text.length > length ? text.substring(0, length) + '...' : text;
      }
      ko.bindingHandlers.text.update(element, function () {
        return truncated;
      });
    }
  };

  ko.bindingHandlers.parseArguments = {
    init: function (element, valueAccessor, allBindingsAccessor) {
      $el = $(element);

      function splitStrings(str) {
        var bits = [];
        var isInQuotes = false;
        var tempStr = '';
        str.split('').forEach(function (char) {
          if (char == '"' || char == "'") {
            isInQuotes = !isInQuotes;
          }
          else if ((char == ' ' || char == '\n') && !isInQuotes && tempStr != '') {
            bits.push(tempStr);
            tempStr = '';
          }
          else {
            tempStr += char;
          }
        });
        if (tempStr != '') {
          bits.push(tempStr);
        }
        return bits;
      }

      $el.bind('paste', function (e) {
        var pasted = e.originalEvent.clipboardData.getData('text');
        var args = splitStrings(pasted);
        if (args.length > 1) {
          var newList = [];
          args.forEach(function (arg) {
            var obj = {};
            obj[valueAccessor().objectKey] = arg;
            newList.push(obj);
          });
          valueAccessor().list(ko.mapping.fromJS(newList)());
          valueAccessor().callback();
        }
      });

    }
  };


  var aceInstancesById = {},
    aceInitId = 0;

  ko.bindingHandlers.ace = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {

      var options = allBindingsAccessor().aceOptions || {};
      var value = ko.utils.unwrapObservable(valueAccessor());

      if (!element.id) {
        element.id = 'knockoutAce' + aceInitId;
        aceInitId = aceInitId + 1;
      }

      var editor = ace.edit(element.id);

      editor.setOptions(options);

      if (options.theme) {
        editor.setTheme('ace/theme/' + options.theme);
      }
      else {
        editor.setTheme('ace/theme/hue');
      }
      if (options.mode) {
        editor.getSession().setMode('ace/mode/' + options.mode);
      }
      if (options.readOnly) {
        editor.setReadOnly(true);
      }

      editor.setValue(value);
      editor.gotoLine(0);

      editor.getSession().on('change', function (delta) {
        if (ko.isWriteableObservable(valueAccessor())) {
          valueAccessor()(editor.getValue());
        }
      });

      aceInstancesById[element.id] = editor;

      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        editor.destroy();
        delete aceInstancesById[element.id];
      });
    },
    update: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
      var value = ko.utils.unwrapObservable(valueAccessor());
      var id = element.id;

      if (typeof id !== 'undefined' && id !== '' && aceInstancesById.hasOwnProperty(id)) {
        var editor = aceInstancesById[id];
        var content = editor.getValue();
        if (content !== value) {
          editor.setValue(value);
          editor.gotoLine(0);
        }
      }
    }
  };

  ko.aceEditors = {
    resizeAll: function () {
      for (var id in aceInstancesById) {
        if (!aceInstancesById.hasOwnProperty(id)) continue;
        var editor = aceInstancesById[id];
        editor.resize();
      }
    },
    get: function (id) {
      return aceInstancesById[id];
    }
  };

  ko.bindingHandlers.dropzone = {
    init: function (element, valueAccessor) {
      var value = ko.unwrap(valueAccessor());

      var options = {
        autoDiscover: false,
        maxFilesize: 5000000,
        previewsContainer: '#progressStatusContent',
        previewTemplate: '<div class="progress-row">' +
        '<span class="break-word" data-dz-name></span>' +
        '<div class="pull-right">' +
        '<span class="muted" data-dz-size></span>&nbsp;&nbsp;' +
        '<span data-dz-remove><a href="javascript:undefined;" title="' + DropzoneGlobals.i18n.cancelUpload + '"><i class="fa fa-fw fa-times"></i></a></span>' +
          '<span style="display: none" data-dz-uploaded><i class="fa fa-fw fa-check muted"></i></span>' +
        '</div>' +
        '<div class="progress-row-bar" data-dz-uploadprogress></div>' +
        '</div>',
        drop: function (e) {
          $('.hoverMsg').addClass('hide');
          if (e.dataTransfer.files.length > 0) {
            $('#progressStatus').removeClass('hide');
            $('#progressStatusBar').removeClass('hide');
            $('#progressStatusBar div').css('width', '0');
          }
        },
        uploadprogress: function (file, progress) {
          $('[data-dz-name]').each(function (cnt, item) {
            if ($(item).text() === file.name) {
              $(item).parents('.progress-row').find('[data-dz-uploadprogress]').width(progress.toFixed() + '%');
              if (progress.toFixed() === '100') {
                $(item).parents('.progress-row').find('[data-dz-remove]').hide();
                $(item).parents('.progress-row').find('[data-dz-uploaded]').show();
              }
            }
          });
        },
        totaluploadprogress: function (progress) {
          $('#progressStatusBar div').width(progress.toFixed() + "%");
        },
        canceled: function () {
          $.jHueNotify.info(DropzoneGlobals.i18n.uploadCanceled);
        },
        complete: function (file) {
          if (file.xhr.response != '') {
            var response = JSON.parse(file.xhr.response);
            if (response && response.status != null) {
              if (response.status != 0) {
                $(document).trigger('error', response.data);
                if (value.onError) {
                  value.onError(file.name);
                }
              }
              else {
                $(document).trigger('info', response.path + ' ' + DropzoneGlobals.i18n.uploadSucceeded);
                if (value.onComplete) {
                  value.onComplete(response.path);
                }
              }
            }
          }
        },
        queuecomplete: function () {
          window.setTimeout(function () {
            $('#progressStatus').addClass('hide');
            $('#progressStatusBar').addClass('hide');
            $('#progressStatusBar div').css('width', '0');
          }, 2500);
        },
        createImageThumbnails: false
      };

      $.extend(options, value);

      $(element).addClass('dropzone');
      new Dropzone(element, options);
    }
  };

  ko.bindingHandlers.jHueRowSelector = {
    init: function (element, valueAccessor) {
      $(element).jHueRowSelector();
    }
  }

})();
