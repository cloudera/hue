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

  // we override the default html binding to prevent XSS/JS injection
  var originalHtmlBinding = ko.bindingHandlers.html;
  ko.bindingHandlers.html = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var newValueAccessor = function () {
        return hueUtils.deXSS(ko.unwrap(valueAccessor()));
      };
      originalHtmlBinding.init(element, newValueAccessor, allBindings, viewModel, bindingContext);
    },
    update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      var newValueAccessor = function () {
        return hueUtils.deXSS(ko.unwrap(valueAccessor()));
      };
      originalHtmlBinding.update(element, newValueAccessor, allBindings, viewModel, bindingContext);
    },
  };

  ko.bindingHandlers.htmlUnsecure = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      originalHtmlBinding.init(element, valueAccessor, allBindings, viewModel, bindingContext);
    },
    update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      originalHtmlBinding.update(element, valueAccessor, allBindings, viewModel, bindingContext);
    },
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
      ko.bindingHandlers.click.init(element, function () {
        return function (data, event) {
          var url = ko.unwrap(valueAccessor());
          if (url) {
            var prefix = '';
            if (IS_HUE_4) {
              prefix = '/hue' + (url.indexOf('/') === 0 ? '' : '/');
            }
            if ($(element).attr('target')) {
              window.open(prefix + url, $(element).attr('target'));
            } else if (event.ctrlKey || event.metaKey || event.which === 2) {
              window.open(prefix + url, '_blank');
            } else {
              huePubSub.publish('open.link', url);
            }
          }
        }
      }, allBindings, viewModel, bindingContext);

      ko.bindingHandlers.hueLink.update(element, valueAccessor);
    },
    update: function (element, valueAccessor) {
      var url = ko.unwrap(valueAccessor());
      if (url) {
        if (IS_HUE_4) {
          $(element).attr('href', '/hue' + (url.indexOf('/') === 0 ? url : '/' + url));
        } else {
          $(element).attr('href', url);
        }
      } else {
        $(element).attr('href', 'javascript: void(0);');
      }
    }
  };

  ko.bindingHandlers.publish = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      ko.bindingHandlers.click.init(element, function () {
        return function () {
          var topicDetails = ko.unwrap(valueAccessor());
          if (typeof topicDetails === 'string') {
            huePubSub.publish(topicDetails)
          } else if (typeof topicDetails === 'object') {
            var keys = Object.keys(topicDetails);
            if (keys.length === 1) {
              huePubSub.publish(keys[0], topicDetails[keys[0]]);
            }
          }
        }
      }, allBindings, viewModel, bindingContext);
    },
  };

  ko.bindingHandlers.clickToCopy = {
    init: function (element, valueAccessor) {
      $(element).click(function () {
        var $input = $('<textarea>').css({ opacity: 0 }).val(ko.unwrap(valueAccessor())).appendTo(HUE_CONTAINER).select();
        document.execCommand('copy');
        $input.remove()
      });
    }
  };

  ko.bindingHandlers.fetchMore = {
    init: function (element, valueAccessor) {
      var options = valueAccessor();
      var $element = $(element);

      var throttle = -1;
      $element.on('scroll.fetchMore', function () {
        window.clearTimeout(throttle);
        throttle = window.setTimeout(function () {
          if ((element.scrollTop + $element.innerHeight() >= element.scrollHeight - 10) && ko.unwrap(options.hasMore) && !ko.unwrap(options.loadingMore)) {
            options.fetchMore();
          }
        }, 100);
      });

      ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
        $element.off('scroll.fetchMore');
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
          _resizeMenu: function () {
            // This overrides the default behaviour of using dropdown width of the same size as input autocomplete box
            if (options.limitWidthToInput) {
              this.menu.element.outerWidth(options.minWidth);
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
            options.onSelect(ui.item);
          }
          if (oldSelect) {
            oldSelect(event, ui);
          }
        };
      }

      $element.hueAutocomplete(options);

      var enableAutocomplete = function () {
        if ($element.data('custom-hueAutocomplete')) {
          $element.hueAutocomplete("option", "disabled", false);
          $element.off('click', enableAutocomplete)
        } else {
          window.setTimeout(enableAutocomplete, 200);
        }
      };
      // IE 11 trick to prevent it from being shown on page refresh
      $element.on('click', enableAutocomplete)
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

      var sizeCheckInterval = -1;

      ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
        window.clearInterval(sizeCheckInterval);
      });

      var showEdit = function () {
        window.clearInterval(sizeCheckInterval);
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

      var lastKnownOffsetWidth = -1;
      var lastKnownOffsetHeight = -1;

      var addReadOnlyTagsTillOverflow = function ($readOnlyInner) {
        $readOnlyInner.empty();
        var tagElements = [];
        options.setTags().forEach(function (tag) {
          tagElements.push($('<div>').text(tag).appendTo($readOnlyInner));
        });

        if (! options.readOnly && !options.hasErrors()) {
          $('<i>').addClass('fa fa-pencil selectize-edit pointer').attr('title', HUE_I18n.selectize.editTags).appendTo($readOnlyInner);
          $readOnlyInner.click(function () {
            showEdit();
          });
        }

        if (!options.overflowEllipsis) {
          return;
        }

        if ($readOnlyInner[0].offsetHeight < $readOnlyInner[0].scrollHeight || $readOnlyInner[0].offsetWidth < $readOnlyInner[0].scrollWidth && tagElements.length) {
          tagElements[tagElements.length - 1].after($('<div>').addClass('hue-tag-overflow').text('...'));
        }

        while (tagElements.length && ($readOnlyInner[0].offsetHeight < $readOnlyInner[0].scrollHeight || $readOnlyInner[0].offsetWidth < $readOnlyInner[0].scrollWidth)) {
          tagElements.pop().remove();
        }

        lastKnownOffsetWidth = $readOnlyInner[0].offsetWidth;
        lastKnownOffsetHeight = $readOnlyInner[0].offsetHeight;
      };

      var showReadOnly = function () {
        window.clearInterval(sizeCheckInterval);
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
          addReadOnlyTagsTillOverflow($readOnlyInner);
          if (options.overflowEllipsis) {
            sizeCheckInterval = window.setInterval(function () {
              if ($readOnlyInner[0].offsetWidth !== lastKnownOffsetWidth || $readOnlyInner[0].offsetHeight !== lastKnownOffsetHeight) {
                addReadOnlyTagsTillOverflow($readOnlyInner);
              }
            }, 500);
          }
        } else {
          if (options.hasErrors()) {
            $('<span>').addClass('selectize-no-tags').text(options.errorMessage).appendTo($readOnlyInner);
          } else {
            $('<span>').addClass('selectize-no-tags').text(options.emptyPlaceholder).appendTo($readOnlyInner);
          }

          if (! options.readOnly && !options.hasErrors()) {
            $('<i>').addClass('fa fa-pencil selectize-edit pointer').attr('title', HUE_I18n.selectize.editTags).appendTo($readOnlyInner);
            $readOnlyInner.click(function () {
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

  window.MultiLineEllipsisHandler = (function () {

    function MultiLineEllipsisHandler(options) {
      var self = this;

      self.element = options.element;
      self.$element = $(options.element);
      self.overflowHeight = options.overflowHeight;
      self.expandable = options.expandable;
      self.expandClass = options.expandClass;
      self.expandActionClass = options.expandActionClass;
      self.overflowing = options.overflowing;

      self.onActionRender = options.onActionRender;

      self.lastKnownOffsetHeight;
      self.lastKnownOffsetWidth;
      self.isOverflowing;

      self.expanded = options.expanded || ko.observable(false);
      self.updateOverflowHeight();

      self.contents = options.text;
      self.element.innerHTML = self.contents;

      var linkRegex = /(?:(?:[a-z]+:\/\/)|www\.)[^\s\/]+(?:[.\/]\S+)*[^\s`!()\[\]{};:'".,<>?«»“”‘’]/ig;

      self.renderContents = function (contents) {
        if (options.linkify) {
          return hueUtils.deXSS(contents.replace(linkRegex, function (val) {
            return '<a href="' + (val.toLowerCase().indexOf('www') === 0 ? 'http://' + val : val) + '" target="_blank">' + val + '</a>';
          }));
        }
        return hueUtils.deXSS(contents);
      };

      self.delayedResumeTimeout = window.setTimeout(function () {
        self.resume();
      }, 0);
    }

    MultiLineEllipsisHandler.prototype.updateOverflowHeight = function () {
      var self = this;
      if (self.overflowHeight) {
        self.$element.css('max-height', self.expanded() ? '' : self.overflowHeight);
        self.$element.css('overflow', self.expanded() ? '' : 'hidden');
      }
    };

    MultiLineEllipsisHandler.prototype.resume = function () {
      var self = this;
      self.refresh();
      window.clearInterval(self.sizeCheckInterval);
      self.sizeCheckInterval = window.setInterval(function () {
        if (self.element.offsetWidth !== self.lastKnownOffsetWidth || self.element.offsetHeight !== self.lastKnownOffsetHeight) {
          self.refresh();
        }
      }, 500);
    };

    MultiLineEllipsisHandler.prototype.pause = function () {
      var self = this;
      window.clearTimeout(self.delayedResumeTimeout);
      window.clearInterval(self.sizeCheckInterval);
    };

    MultiLineEllipsisHandler.prototype.dispose = function () {
      var self = this;
      self.pause();
    };

    var checkOverflow = function (element) {
      return element.offsetHeight < element.scrollHeight || element.offsetWidth < element.scrollWidth
    };

    MultiLineEllipsisHandler.prototype.refresh = function () {
      var self = this;
      self.$element.empty();
      var textElement = $('<span>').appendTo(self.$element)[0];
      if (self.expandable) {
        textElement.innerHTML = self.renderContents ? self.renderContents(self.contents) : self.contents;
        if (self.expanded() || checkOverflow(self.element)) {
          self.$element.append('&nbsp;');
          var $expandLink = $('<a href="javascript:void(0);"><i class="fa fa-fw ' + (self.expanded() ? 'fa-chevron-up' : 'fa-chevron-down') + '"></i></a>');
          if (self.expandActionClass) {
            $expandLink.addClass(self.expandActionClass);
          }
          $expandLink.appendTo(self.$element);
          $expandLink.add(textElement).click(function (e) {
            self.expanded(!self.expanded());
            self.updateOverflowHeight();
            if (self.expanded()) {
              if (self.expandClass) {
                self.$element.addClass(self.expandClass);
              }
              self.refresh();
              self.pause();
            } else {
              if (self.expandClass) {
                self.$element.removeClass(self.expandClass);
              }
              self.resume();
            }
          })
        }
      } else {
        textElement.innerHTML = self.renderContents ? self.renderContents(self.contents) : self.contents;
      }

      if (self.onActionRender) {
        self.onActionRender(self.$element, checkOverflow(self.element));
      }

      self.isOverflowing = false;

      if (!self.expanded()) {
        while (checkOverflow(self.element)) {
          self.isOverflowing = true;
          var contents = $(textElement).contents();
          var lastContent = contents[contents.length - 1];
          // Check for text node
          if (lastContent.nodeType === 3 ) {
            var lastSpaceIndex = lastContent.textContent.regexLastIndexOf(/\s\S+/);
            if (lastSpaceIndex !== -1) {
              lastContent.replaceWith(document.createTextNode(lastContent.textContent.substring(0, lastSpaceIndex) + '...'));
            } else if (contents.length > 1) {
              textElement.removeChild(lastContent);
            } else {
              break;
            }
          } else if (contents.length > 1) { // Remove any elements like links
            textElement.removeChild(lastContent)
          }
        }
      }

      if (ko.isObservable(self.overflowing) && self.overflowing() !== self.isOverflowing) {
        self.overflowing(self.isOverflowing);
      }
      self.lastKnownOffsetHeight = self.element.offsetHeight;
      self.lastKnownOffsetWidth = self.element.offsetWidth;
    };

    MultiLineEllipsisHandler.prototype.setText = function (text) {
      var self = this;
      self.contents = text;
      self.refresh();
    };

    return MultiLineEllipsisHandler;
  })();

  ko.bindingHandlers.multiLineEllipsis = {
    after: ['text', 'value'],
    init: function (element, valueAccessor) { },
    update: function (element, valueAccessor) {
      var options = {};
      if (valueAccessor && ko.isObservable(valueAccessor())) {
        options.overflowing = valueAccessor();
      } else if (valueAccessor) {
        options = valueAccessor() || {};
      }
      var multiLineEllipsisHandler = new MultiLineEllipsisHandler({
        element: element,
        text: element.textContent,
        overflowing: options.overflowing,
        linkify: true,
        expandable: options.expandable,
        expanded: options.expanded,
        expandActionClass: options.expandActionClass,
        expandClass: options.expandClass
      });

      ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
        multiLineEllipsisHandler.dispose();
      });
    }
  };

  ko.bindingHandlers.toggleOverflow = {
    render: function ($element, options) {
      if (hueUtils.isOverflowing($element.find('.toggle-overflow'))) {
        $('<div>').addClass('toggle-overflow-toggle').html('<i class="fa fa-caret-down muted"></i>').appendTo($element);
        $element.on('click', function () {
          if ($element.find('.toggle-overflow-toggle i').hasClass('fa-caret-down')){
            $element.find('.toggle-overflow').css('height', '');
            $element.css('cursor', 'n-resize');
            $element.find('.toggle-overflow-toggle').removeClass('toggle-hidden').css('cursor', 'n-resize');
            $element.find('.toggle-overflow-toggle i').removeClass('fa-caret-down').addClass('fa-caret-up');
          } else {
            if (options.height) {
              $element.find('.toggle-overflow').height(options.height);
            }
            $element.css('cursor', 's-resize');
            $element.find('.toggle-overflow-toggle').addClass('toggle-hidden').css('cursor', 's-resize');
            $element.find('.toggle-overflow-toggle i').removeClass('fa-caret-up').addClass('fa-caret-down');
          }
        });
      }
    },

    init: function (element, valueAccessor) {
      var $element = $(element);
      var options = valueAccessor() || {};
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
      var options = valueAccessor() || {};
      window.setTimeout(function () {
        ko.bindingHandlers.toggleOverflow.render($element, options);
      }, 100);
    }
  };

  ko.bindingHandlers.draggableText = {
    init: function (element, valueAccessor) {
      var $element = $(element);
      var options = valueAccessor();
      if ((ko.isObservable(options.text) && !options.text()) || !options.text) {
        return;
      }
      $element.addClass("draggableText");

      var $helper = $("<div>").text(ko.isObservable(options.text) ? options.text() : options.text).css("z-index", "99999");
      var dragStartX = -1;
      var dragStartY = -1;
      var notifiedOnDragStarted = false;
      $element.draggable({
        helper: function () { return $helper },
        appendTo: "body",
        start: function (event) {
          dragStartX = event.clientX;
          dragStartY = event.clientY;
          huePubSub.publish('draggable.text.meta', options.meta);
          notifiedOnDragStarted = false;
        },
        drag: function (event) {
          huePubSub.publish('draggable.text.drag', {
            event: event,
            meta: options.meta
          });
          if (!notifiedOnDragStarted && Math.sqrt((dragStartX-event.clientX)*(dragStartX-event.clientX) + (dragStartY-event.clientY)*(dragStartY-event.clientY)) >= 10) {
            huePubSub.publish('draggable.text.started', options.meta);
            notifiedOnDragStarted = true;
          }
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
          notifiedOnDragStarted = false;
          huePubSub.publish('draggable.text.stopped');
        }
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
        overlay: false,
        inline: false,
        blackout: false
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
        $container.addClass(options.overlay ? 'hue-spinner-overlay' : ( options.inline ? 'hue-spinner-inline' : 'hue-spinner'));
        if (options.blackout) {
          $container.addClass('hue-spinner-blackout');
        }
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
            if (options.inline) {
              $container.css('width', '100%');
            }
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

        if (typeof options.beforeOpen === 'function') {
          options.beforeOpen.bind(viewModel)();
        }
        var $menu = $('#hueContextMenu_' + options.template);
        if ($menu.length === 0) {
          $menu = $('<ul id="hueContextMenu_' + options.template  + '" class="hue-context-menu" data-bind="template: { name: \'' + options.template + '\', data: viewModel, afterRender: afterRender }"></ul>').appendTo(HUE_CONTAINER);
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
            if (options.scrollContainer) {
              $(options.scrollContainer).one('scroll', hideMenu);
            }
            window.setTimeout(function () {
              $menu.data('active', false);
              $(document).one('click', hideMenu);
            }, 100);
          },
          viewModel: options.viewModel || viewModel
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

      $element.on("wheel", function () {
        $element.data('hasUserScrolled', true);
      });

      function autoLogScroll () {
        var elementHeight = $element.innerHeight();
        var lastHeight = $element.data('lastHeight') || elementHeight;
        var lastScrollTop = $element.data('lastScrollTop') || 0;
        var hasUserScrolled = $element.data('hasUserScrolled') || false;
        var lastScrollHeight = $element.data('lastScrollHeight') || elementHeight;

        var stickToBottom = !hasUserScrolled || elementHeight !== lastHeight || (lastScrollTop + elementHeight) === lastScrollHeight;

        if (stickToBottom) {
          $element.scrollTop(element.scrollHeight - $element.height());
          $element.data('lastScrollTop', $element.scrollTop());
        }

        $element.data('lastScrollHeight', element.scrollHeight);
        $element.data('lastHeight', elementHeight);
      }

      var logValue = valueAccessor();
      logValue.subscribe(function () {
        window.setTimeout(autoLogScroll, 200);
      });

      if (typeof allBindings().logScrollerVisibilityEvent !== 'undefined'){
        allBindings().logScrollerVisibilityEvent.subscribe(function () {
          window.setTimeout(autoLogScroll, 0);
        });
      } else {
        hueUtils.waitForRendered(element, function(el) { return el.is(':visible') }, autoLogScroll, 300);
        ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
          window.clearTimeout($element.data('waitForRenderTimeout'));
        });
      }
    }
  };

  ko.bindingHandlers.multiCheckForeachVisible = {
    init: function (element, valueAccessor, allBindings, clickedEntry, bindingContext) {
      var $element = $(element);
      var parentContext = bindingContext.$parentContext;

      var selectedAttr = valueAccessor().selectedAttr;
      var entries = valueAccessor().entries;

      $element.attr('unselectable', 'on').css('user-select', 'none').on('selectstart', false);

      $element.on('click', function (e) {
        if (e.shiftKey && parentContext.$multiCheckLastEntry) {
          var lastEntry = parentContext.$multiCheckLastEntry;
          var inside = false;
          entries().every(function (otherEntry) {
            if (otherEntry === lastEntry || otherEntry === clickedEntry) {
              if (inside) {
                return false;
              }
              inside = true;
              return true;
            }
            if (inside && otherEntry[selectedAttr]() !== lastEntry[selectedAttr]()) {
              otherEntry[selectedAttr](lastEntry[selectedAttr]());
            }
            return true;
          });
          if (clickedEntry[selectedAttr]() !== lastEntry[selectedAttr]()) {
            clickedEntry[selectedAttr](lastEntry[selectedAttr]());
          }
        } else {
          clickedEntry[selectedAttr](!clickedEntry[selectedAttr]());
        }

        parentContext.$multiCheckLastEntry = clickedEntry;
        parentContext.$multiCheckLastChecked = clickedEntry[selectedAttr]();
      });

      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        $element.off('click');
      });
    },
    update: function () {}
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
            allCheckboxes = $container.find(".hue-checkbox");
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
        $container = $('<div>').attr('id', 'popover-container').appendTo(HUE_CONTAINER);
        $('<div>').addClass('temp-content').hide().appendTo($container);
        $('<div>').addClass('temp-title').hide().appendTo($container);
      }

      var $content = $container.find('.temp-content');
      var $title = $container.find('.temp-title');

      $.extend(options, { html: true, trigger: 'manual', container: '#popover-container' });

      var $element = $(element);

      var visible = options.visible || ko.observable(false);

      var trackElementInterval = -1;

      var hidePopover = function () {
        if (visible()) {
          window.clearInterval(trackElementInterval);
          $element.popover('hide');
          visible(false);
          $(document).off('click', hideOnClickOutside);
        }
      };

      var closeSub = huePubSub.subscribe('close.popover', hidePopover);

      var hideOnClickOutside = function (event) {
        if (visible() && $element.data('popover') && ! $.contains($element.data('popover').$tip[0], event.target)) {
          hidePopover();
        }
      };

      ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
        if (visible && $element.data('popover')) {
          hidePopover();
        }
        closeSub.remove();
      });

      var afterRender = function () {
        options.content = $content.html();
        options.title = $title.html();
        $element.popover(options);
        $element.popover('show');
        var $tip = $element.data('popover').$tip;
        if (HUE_CONTAINER !== 'body') {
          $tip.css({ 'position': 'fixed', 'z-index': 2000 });
          $tip.appendTo(HUE_CONTAINER);

          $tip.offset({
            left: $element.offset().left + $element.outerWidth(true) + 10,
            top: $element.offset().top + ($element.outerHeight(true) / 2) - ($tip.outerHeight(true) / 2)
          });
        }
        ko.cleanNode($tip.get(0));
        ko.applyBindings(viewModel, $tip.get(0));
        $tip.find(".close-popover").click(function (event) {
          hidePopover();
          event.stopPropagation();
        });
        if (options.minWidth) {
          var heightBefore = $tip.height();
          $tip.css('min-width', options.minWidth);
          // The width might affect the height in which case we need to reposition the popover
          var diff = (heightBefore - $tip.height()) / 2;
          if (diff !== 0) {
            $tip.css('top', ($tip.position().top + diff) + 'px');
          }
        }
        var lastWidth = $element.outerWidth(true);
        var lastOffset = $element.offset();
        var lastHeight = $element.outerHeight(true);
        trackElementInterval = window.setInterval(function () {
          var elementWidth = $element.outerWidth(true);
          var elementHeight = $element.outerHeight(true);
          var elementOffset = $element.offset();
          if (lastHeight !== elementHeight || lastWidth !== $element.outerWidth(true) || lastOffset.top !== elementOffset.top || lastOffset.left !== elementOffset.left) {
            $tip.css({ 'left': elementOffset.left + (elementWidth / 2) - ($tip.outerWidth(true) / 2) , 'top': elementOffset.top + elementHeight + 10 });
            lastWidth = elementWidth;
            lastOffset = elementOffset;
            lastHeight = elementHeight;
          }
        }, 50);
        $content.empty();
        $title.empty();
        $(document).on('click', hideOnClickOutside);
        visible(true);
      };

      var showPopover = function (preventClose) {
        if (!preventClose) {
          huePubSub.publish('close.popover');
        }
        ko.renderTemplate(options.contentTemplate, viewModel, {
          afterRender: function () {
            if (options.titleTemplate) {
              ko.renderTemplate(options.titleTemplate, viewModel, {
                afterRender: function () {
                  afterRender();
                }
              }, $title.get(0), 'replaceChildren');
            } else {
              afterRender();
            }
          }
        }, $content.get(0), 'replaceChildren');
      };

      if (visible()) {
        window.setTimeout(function () {
          showPopover(true);
        }, 0);
      }

      if (clickTrigger) {
        $element.click(function (e) {
          if (visible()) {
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
        searchViewModel.search();
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
          }
        });
      });
    }
  };

  /**
   * Show the Context Popover for files (HDFS, S3, ADLS, ...) when the bound element is clicked.
   *
   * Parameters:
   *
   * {string} path - the path (can include type, i.e. 'hdfs://tmp'
   * {string} [type] - Optional type, 'hdfs', 's3' etc. Default 'hdfs'.
   * {string} [orientation] - 'top', 'right', 'bottom', 'left'. Default 'right';
   * {Object} [offset] - Optional offset from the element
   * {number} [offset.top] - Offset in pixels
   * {number} [offset.left] - Offset in pixels
   *
   * Examples:
   *
   * data-bind="storageContextPopover: { path: '/tmp/banana.csv' }"
   * data-bind="storageContextPopover: { path: 's3:/tmp/banana.csv', orientation: 'bottom', offset: { top: 5 } }"
   *
   * @type {{init: ko.bindingHandlers.storageContextPopover.init}}
   */
  ko.bindingHandlers.storageContextPopover = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      ko.bindingHandlers.click.init(element, function () {
        return function () {
          var options = valueAccessor();
          AssistStorageEntry.getEntry(options.path, options.type).done(function (entry) {
            var $source = $(element);
            var offset = $source.offset();

            if (options.offset) {
              offset.top += options.offset.top || 0;
              offset.left += options.offset.left || 0;
            }

            entry.open(true);
            huePubSub.publish('context.popover.show', {
              data: {
                type: 'storageEntry',
                storageEntry: entry
              },
              orientation: options.orientation || 'right',
              source: {
                element: element,
                left: offset.left,
                top: offset.top,
                right: offset.left + $source.width(),
                bottom: offset.top + $source.height()
              }
            });

          })
        };
      }, allBindings, viewModel, bindingContext);
    }
  };

  /**
   * Show the Context Popover for SQL or Solr entities when the bound element is clicked.
   *
   * Parameters:
   *
   * {string} sourceType - 'impala', 'hive' etc.
   * {ContextNamespace} namespace
   * {ContextCompute} compute
   * {string} path - the path, i.e. 'default.customers' or ['default', 'customers'
   * {string} [orientation] - 'top', 'right', 'bottom', 'left'. Default 'right'
   * {Object} [offset] - Optional offset from the element
   * {number} [offset.top] - Offset in pixels
   * {number} [offset.left] - Offset in pixels
   *
   * Examples:
   *
   * data-bind="sqlContextPopover: { sourceType: 'impala', namespace: { id: 'myNamespace' }, compute: { id: 'myCompute' }, path: 'default.customers' }"
   * data-bind="sqlContextPopover: { sourceType: 'hive', namespace: { id: 'myNamespace' }, compute: { id: 'myCompute' }, path: 'default', orientation: 'bottom', offset: { top: 5 } }"
   *
   * @type {{init: ko.bindingHandlers.sqlContextPopover.init}}
   */
  ko.bindingHandlers.sqlContextPopover = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      ko.bindingHandlers.click.init(element, function () {
        return function () {
          var options = valueAccessor();
          DataCatalog.getEntry(options).done(function (entry) {
            var $source = $(element);
            var offset = $source.offset();
            if (options.offset) {
              offset.top += options.offset.top || 0;
              offset.left += options.offset.left || 0;
            }

            huePubSub.publish('context.popover.show', {
              data: {
                type: 'catalogEntry',
                catalogEntry: entry
              },
              showInAssistEnabled: true,
              orientation: options.orientation || 'right',
              source: {
                element: element,
                left: offset.left,
                top: offset.top,
                right: offset.left + $source.width(),
                bottom: offset.top + $source.height()
              }
            });
          });
        }
      }, allBindings, viewModel, bindingContext);
    }
  };

  /**
   * Show the Context Popover for Documents when the bound element is clicked.
   *
   * Parameters:
   *
   * {string} uuid - the uuid of the document
   * {string} [orientation] - 'top', 'right', 'bottom', 'left'. Default 'right'
   * {Object} [offset] - Optional offset from the element
   * {number} [offset.top] - Offset in pixels
   * {number} [offset.left] - Offset in pixels
   *
   * Examples:
   *
   * data-bind="documentContextPopover: { uuid: 'bana-na12-3456-7890' }"
   * data-bind="documentContextPopover: { uuid: 'bana-na12-3456-7890', orientation: 'bottom', offset: { top: 5 } }"
   *
   * @type {{init: ko.bindingHandlers.documentContextPopover.init}}
   */
  ko.bindingHandlers.documentContextPopover = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
      ko.bindingHandlers.click.init(element, function () {
        return function () {
          var options = valueAccessor();

          ApiHelper.getInstance().fetchDocument({
            uuid: options.uuid,
            fetchContents: true,
            silenceErrors: true
          }).done(function (response) {
            var $source = $(element);
            var offset = $source.offset();
            if (options.offset) {
              offset.top += options.offset.top || 0;
              offset.left += options.offset.left || 0;
            }

            huePubSub.publish('context.popover.show', {
              data: {
                type: 'hue',
                definition: response.document
              },
              showInAssistEnabled: true,
              orientation: options.orientation || 'right',
              source: {
                element: element,
                left: offset.left,
                top: offset.top,
                right: offset.left + $source.width(),
                bottom: offset.top + $source.height()
              }
            });
          });
        }
      }, allBindings, viewModel, bindingContext);
    }
  };

  ko.bindingHandlers.aceResizer = {
    init: function (element, valueAccessor) {
      var options = ko.unwrap(valueAccessor());
      var ace = options.snippet.ace;
      var $target = $(options.target);
      var $resizer = $(element);
      var $contentPanel = $(".content-panel");
      var $execStatus = $resizer.prev('.snippet-execution-status');
      var $variables = $resizer.siblings('.snippet-row').find('.variables');

      var lastEditorSize = $.totalStorage('hue.editor.editor.size') || 131;
      var editorHeight = Math.floor(lastEditorSize / 16);
      $target.height(lastEditorSize);
      var autoExpand = typeof options.snippet.aceAutoExpand !== 'undefined' ? options.snippet.aceAutoExpand : true;
      var draggedOnce = false;

      function throttleChange() {
        if (autoExpand && !draggedOnce) {
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
          else {
            $target.height(Math.max(ace().session.getLength() * 16, $.totalStorage('hue.editor.editor.size') || 131));
            resized = true;
          }
          if (ace().session.getLength() == editorHeight) {
            resized = false;
          }
          if (resized && $target.height() !== lastEditorSize) {
            ace().resize();
            editorHeight = Math.min(maxAutoLines, ace().session.getLength());
            lastEditorSize = $target.height();
            huePubSub.publish('redraw.fixed.headers');
          }
        }
      }

      var changeTimeout = -1;
      ace().on('change', function () {
        window.clearTimeout(changeTimeout);
        changeTimeout = window.setTimeout(throttleChange, 10)
      });

      var setAutoExpandSubscription = huePubSub.subscribe('ace.set.autoexpand', function (options) {
        if (ace().container.id === options.snippet.id()) {
          autoExpand = options.autoExpand;
        }
      });

      $resizer.draggable({
        axis: "y",
        start: options.onStart ? options.onStart : function(){},
        drag: function (event, ui) {
          draggedOnce = true;
          var currentHeight = ui.offset.top + $contentPanel.scrollTop() - (125 + $execStatus.outerHeight(true) + $variables.outerHeight(true));
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

      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        setAutoExpandSubscription.remove();
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
          if (options.minHeight && currentHeight < options.minHeight) {
            currentHeight = options.minHeight;
          }
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
          $sidePanel.css('flex-basis',  Math.max(sidePanelWidth, 200) + 'px');
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
          if (ko.unwrap(options.rightPanelVisible) && ko.unwrap(options.rightPanelAvailable)) {
            $resizer.show();
            rightPanelWidth = Math.min(rightPanelWidth, $container.width() - 100);
            var contentPanelWidth = totalWidth - rightPanelWidth - $resizer.width();
            $rightPanel.css("width", rightPanelWidth + "px");
            $contentPanel.css("width", contentPanelWidth + "px");
            $resizer.css("left", $container.width() - rightPanelWidth - $resizer.width() + "px");
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
          var oppositeWidth = hasRightPanel && ko.unwrap(options.rightPanelVisible) && ko.unwrap(options.rightPanelAvailable) ? $rightPanel.width() + $resizer.width() : 0;
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

      if (ko.isObservable(options.rightPanelAvailable)) {
        options.rightPanelAvailable.subscribe(positionPanels);
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
          var _less = ".result-container {" + $(item).text() + "}";
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

        if (allBindingsAccessor()['valueUpdateDelay'] != null) {
          var _timeout = -1;
          $element.on("keyup", function (e) {
            if (!([13, 37, 38, 39, 40].indexOf(e.keyCode) > -1)) {
              window.clearTimeout(_timeout);
              _timeout = window.setTimeout(function () {
                valueObservable($element.val());
              }, allBindingsAccessor()['valueUpdateDelay']);
            }
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

  ko.bindingHandlers.onClickOutside = {
    update: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var options = valueAccessor();
      var func = (typeof options === 'function') ? options : options.onOutside;

      var onDocumentClick = function (event) {
        if ($.contains(document, event.target) && !$.contains(element, event.target)) {
          var result = func.bind(viewModel)();
          if (typeof result === 'undefined' || result) {
            $(document).off('click', onDocumentClick);
          }
        }
      };

      $(document).off('click', onDocumentClick);
      $(document).on('click', onDocumentClick);

      ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
        $(document).off('click', onDocumentClick);
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

      if (typeof options === 'object') {
        $element.chosen(options);
      } else {
        $element.chosen();
      }

      ['options', 'selectedOptions', 'value'].forEach(function(propName){
        if (allBindings.has(propName)){
          var prop = allBindings.get(propName);
          if (ko.isObservable(prop)) {
            prop.subscribe(function(){
              $element.trigger('chosen:updated');
            });
          }
        }
      });
    }
  };

  ko.bindingHandlers.tooltip = {
    after: ['attr'],
    update: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
      var local = ko.utils.unwrapObservable(valueAccessor());
      var options = {
        container: HUE_CONTAINER
      };

      $(element).tooltip("destroy");

      ko.utils.extend(options, local);

      if (options.title) {
        var title = ko.unwrap(options.title); // Not always an observable
        if (typeof title === 'string' && !options.html) {
          options.title = escapeOutput(title);
        }
      }

      $(element).tooltip(options);

      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        $(element).tooltip("destroy");
      });
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
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
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

      if (typeof valueAccessor().vm != "undefined") {
        viewModel = valueAccessor().vm;
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
      } else {
        if (options && options.data){
          self.val(options.data);
          complexConfiguration = true;
        } else {
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
          namespace: ko.unwrap(options.namespace),
          compute: ko.unwrap(options.compute),
          searchEverywhere : ko.unwrap(options.searchEverywhere) || false,
          apiHelperUser: ko.unwrap(options.apiHelperUser) || '',
          apiHelperType: ko.unwrap(options.apiHelperType) || '',
          mainScrollable: ko.unwrap(options.mainScrollable) || $(window)
        });
      } else {
        options = allBindingsAccessor();
        function setPathFromAutocomplete(path) {
          self.val(path);
          valueAccessor()(path);
          self.blur();
        }
        self.on("blur", function () {
          if (!options.skipInvalids) {
            valueAccessor()(self.val());
          }
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
          namespace: ko.unwrap(options.namespace),
          compute: ko.unwrap(options.compute),
          pathChangeLevel: ko.unwrap(options.pathChangeLevel) || '',
          apiHelperUser: ko.unwrap(options.apiHelperUser) || '',
          apiHelperType: ko.unwrap(options.apiHelperType) || '',
          mainScrollable: ko.unwrap(options.mainScrollable) || $(window),
          onPathChange: function (path) {
            setPathFromAutocomplete(path);
          },
          onEnter: function (el) {
            if (!options.skipInvalids) {
              setPathFromAutocomplete(el.val());
            }
          },
          onBlur: function () {
            if (self.val().lastIndexOf(".") == self.val().length - 1) {
              self.val(self.val().substr(0, self.val().length - 1));
            }
            if (!options.skipInvalids) {
              valueAccessor()(self.val());
            }
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
        skipTables: true, // No notion of DB actually
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
        $(HUE_CONTAINER).addClass("modal-open");
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
        if (allBindingsAccessor && typeof allBindingsAccessor().filechooserOptions !== 'undefined' && typeof allBindingsAccessor().filechooserOptions.selectFolder !== 'undefined') {
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
        if (isIE11) {
          var oldFocus = jQuery().modal.Constructor.prototype.enforceFocus;
          jQuery().modal.Constructor.prototype.enforceFocus = function() {};
          $("#chooseFile").modal("show");
          window.setTimeout(function () {
            jQuery().modal.Constructor.prototype.enforceFocus = oldFocus;
          }, 5000);
        } else {
          $("#chooseFile").modal("show");
        }
        if (!isNestedModal) {
          $("#chooseFile").on("hidden", function () {
            $(HUE_CONTAINER).removeClass("modal-open");
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
          var m = moment.utc(_el.val());
          _el.datepicker("setValue", m.format("YYYY-MM-DD"));
          _el.val(m.format(_options.momentFormat)); // Set value again as datepicker clears the time component
        }
      }).on("changeDate", function (e) {
        setDate(e.date);
      }).on("hide", function (e) {
        setDate(e.date);
      });

      function setDate(d) {
        if (_options.momentFormat) {
          var m = moment(d);
          // Keep time intact
          var previous = moment.utc(allBindings().value());
          previous.date(m.date());
          previous.month(m.month());
          previous.year(m.year());

          _el.val(previous.format(_options.momentFormat));
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
  };


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
  };

  ko.toCleanJSON = function (koObj) {
    return ko.toJSON(koObj, function (key, value) {
      if (key == "__ko_mapping__") {
        return;
      }
      else {
        return value;
      }
    });
  };


  ko.bindingHandlers.delayedOverflow = {
    init: function (element, valueAccessor) {
      var $element = $(element);

      $element.css("overflow", "hidden");

      var isTouch = false;
      $element.on('touchstart', function () {
        isTouch = true;
      });

      var scrollTimeout = -1;
      $element.hover(function () {
        scrollTimeout = window.setTimeout(function () {
          $element.css("overflow", "auto");
        }, valueAccessor && valueAccessor() === 'slow' ? 500 : 30);
      }, function () {
        if (!isTouch) {
          clearTimeout(scrollTimeout);
          $element.css("overflow", "hidden");
        }
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

  var AceLocationHandler = (function () {

    var STATEMENT_COUNT_AROUND_ACTIVE = 10;

    function AceLocationHandler (editor, editorId, snippet) {
      var self = this;
      self.editor = editor;
      self.editorId = editorId;
      self.snippet = snippet;
      self.sqlSyntaxWorkerSub = null;

      self.disposeFunctions = [];

      self.databaseIndex = {};

      self.attachStatementLocator();
      self.attachSqlWorker();
      self.attachGutterHandler();

      var updateDatabaseIndex = function (databaseList) {
        self.databaseIndex = {};
        databaseList.forEach(function (database) {
          self.databaseIndex[database.toLowerCase()] = true;
        })
      };

      var databaseSub = self.snippet.availableDatabases.subscribe(updateDatabaseIndex);

      self.disposeFunctions.push(function () {
        databaseSub.dispose();
      });

      updateDatabaseIndex(self.snippet.availableDatabases());
    }

    AceLocationHandler.prototype.attachGutterHandler = function () {
      var self = this;
      var lastMarkedGutterLines = [];

      var changedSubscription = huePubSub.subscribe('editor.active.statement.changed', function (statementDetails) {
        if (statementDetails.id !== self.editorId || !statementDetails.activeStatement) {
          return;
        }
        var leadingEmptyLineCount = 0;
        var leadingWhiteSpace = statementDetails.activeStatement.statement.match(/^\s+/);
        if (leadingWhiteSpace) {
          var lineBreakMatch = leadingWhiteSpace[0].match(/(\r\n)|(\n)|(\r)/g);
          if (lineBreakMatch) {
            leadingEmptyLineCount = lineBreakMatch.length;
          }
        }

        while(lastMarkedGutterLines.length) {
          self.editor.getSession().removeGutterDecoration(lastMarkedGutterLines.shift(), 'ace-active-gutter-decoration');
        }
        for (var line = statementDetails.activeStatement.location.first_line - 1 + leadingEmptyLineCount; line < statementDetails.activeStatement.location.last_line; line++) {
          lastMarkedGutterLines.push(line);
          self.editor.getSession().addGutterDecoration(line, 'ace-active-gutter-decoration');
        }
      });

      self.disposeFunctions.push(function () {
        changedSubscription.remove();
      });
    };

    AceLocationHandler.prototype.attachStatementLocator = function () {
      var self = this;
      var lastKnownStatements = [];
      var activeStatement;

      var isPointInside = function (parseLocation, editorPosition) {
        var row = editorPosition.row + 1; // ace positioning has 0 based rows while the parser has 1
        var column = editorPosition.column;
        return (parseLocation.first_line < row && row < parseLocation.last_line) ||
          (parseLocation.first_line === row && row === parseLocation.last_line && parseLocation.first_column <= column && column < parseLocation.last_column) ||
          (parseLocation.first_line === row && row < parseLocation.last_line && column >= parseLocation.first_column) ||
          (parseLocation.first_line < row && row === parseLocation.last_line && column < parseLocation.last_column);
      };

      var lastExecutingStatement = null;
      var updateActiveStatement = function (cursorChange) {
        if (!self.snippet.isSqlDialect()) {
          return;
        }
        var selectionRange = self.editor.getSelectionRange();
        var editorLocation = selectionRange.start;
        if (selectionRange.start.row !== selectionRange.end.row || selectionRange.start.column !== selectionRange.end.column) {
          if (!cursorChange && self.snippet.result && self.snippet.result.statement_range()) {
            var executingStatement = self.snippet.result.statement_range();
            // Row and col are 0 for both start and end on execute, so if the selection hasn't changed we'll use last known executed statement
            if (executingStatement.start.row === 0 && executingStatement.start.column === 0 && executingStatement.end.row === 0 && executingStatement.end.column === 0 && lastExecutingStatement) {
              executingStatement = lastExecutingStatement;
            }
            if (executingStatement.start.row === 0) {
              editorLocation.column += executingStatement.start.column;
            } else if (executingStatement.start.row !== 0 || executingStatement.start.column !== 0) {
              editorLocation.row += executingStatement.start.row;
              editorLocation.column = executingStatement.start.column;
            }
            lastExecutingStatement = executingStatement;
          } else  {
            lastExecutingStatement = null;
          }
        }

        if (cursorChange && activeStatement) {
          // Don't update when cursor stays in the same statement
          if (isPointInside(activeStatement.location, editorLocation)) {
            return;
          }
        }
        var precedingStatements = [];
        var followingStatements = [];
        activeStatement = null;

        var found = false;
        var statementIndex = 0;
        if (lastKnownStatements.length === 1) {
          activeStatement = lastKnownStatements[0];
        } else {
          lastKnownStatements.forEach(function (statement) {
            if (isPointInside(statement.location, editorLocation)) {
              statementIndex++;
              found = true;
              activeStatement = statement;
            } else if (!found) {
              statementIndex++;
              if (precedingStatements.length === STATEMENT_COUNT_AROUND_ACTIVE) {
                precedingStatements.shift();
              }
              precedingStatements.push(statement);
            } else if (found && followingStatements.length < STATEMENT_COUNT_AROUND_ACTIVE) {
              followingStatements.push(statement);
            }
          });

          // Can happen if multiple statements and the cursor is after the last one
          if (!found) {
            precedingStatements.pop();
            activeStatement = lastKnownStatements[lastKnownStatements.length - 1];
          }
        }

        huePubSub.publish('editor.active.statement.changed', {
          id: self.editorId,
          editorChangeTime: lastKnownStatements.editorChangeTime,
          activeStatementIndex: statementIndex,
          totalStatementCount: lastKnownStatements.length,
          precedingStatements: precedingStatements,
          activeStatement: activeStatement,
          followingStatements: followingStatements
        });

        if (activeStatement) {
          self.checkForSyntaxErrors(activeStatement.location, editorLocation);
        }
      };

      var parseForStatements = function () {
        if (self.snippet.isSqlDialect()) {
          try {
            var lastChangeTime = self.editor.lastChangeTime;
            lastKnownStatements = sqlStatementsParser.parse(self.editor.getValue());
            lastKnownStatements.editorChangeTime = lastChangeTime;

            if (typeof hueDebug !== 'undefined' && hueDebug.logStatementLocations) {
              console.log(lastKnownStatements);
            }
          } catch (error) {
            console.warn('Could not parse statements!');
            console.warn(error);
          }
        }
      };

      var changeThrottle = window.setTimeout(parseForStatements, 0);
      var updateThrottle = window.setTimeout(updateActiveStatement, 0);
      var cursorChangePaused = false; // On change the cursor is also moved, this limits the calls while typing

      var lastStart;
      var lastCursorPosition;
      var changeSelectionListener = self.editor.on('changeSelection', function () {
        if (cursorChangePaused) {
          return;
        }
        window.clearTimeout(changeThrottle);
        changeThrottle = window.setTimeout(function () {
          var newCursorPosition = self.editor.getCursorPosition();
          if (!lastCursorPosition || lastCursorPosition.row !== newCursorPosition.row || lastCursorPosition.column !== newCursorPosition.column) {
            self.snippet.aceCursorPosition(newCursorPosition);
            lastCursorPosition = newCursorPosition;
          }

          // The active statement is initially the top one in the selection, batch execution updates this.
          var newStart = self.editor.getSelectionRange().start;
          if (self.snippet.isSqlDialect() && (!lastStart || lastStart.row !== newStart.row || lastStart.column !== newStart.column)) {
            window.clearTimeout(updateThrottle);
            updateActiveStatement(true);
            lastStart = newStart;
          }
        }, 100);
      });

      var changeListener = self.editor.on('change', function () {
        if (self.snippet.isSqlDialect()) {
          window.clearTimeout(changeThrottle);
          cursorChangePaused = true;
          changeThrottle = window.setTimeout(function () {
            window.clearTimeout(updateThrottle);
            parseForStatements();
            updateActiveStatement();
            cursorChangePaused = false;
          }, 500);
          self.editor.lastChangeTime = Date.now();
        }
      });

      var locateSubscription = huePubSub.subscribe('editor.refresh.statement.locations', function (snippet) {
        if (snippet === self.snippet) {
          cursorChangePaused = true;
          window.clearTimeout(changeThrottle);
          window.clearTimeout(updateThrottle);
          parseForStatements();
          updateActiveStatement();
          cursorChangePaused = false;
        }
      });

      self.disposeFunctions.push(function () {
        window.clearTimeout(changeThrottle);
        window.clearTimeout(updateThrottle);
        self.editor.off('changeSelection', changeSelectionListener);
        self.editor.off('change', changeListener);
        locateSubscription.remove();
      });
    };

    AceLocationHandler.prototype.clearMarkedErrors = function (type) {
      var self = this;
      for (var marker in self.editor.getSession().$backMarkers) {
        if (self.editor.getSession().$backMarkers[marker].clazz.indexOf('hue-ace-syntax-' + (type || '')) === 0) {
          self.editor.getSession().$backMarkers[marker].dispose()
        }
      }
    };

    AceLocationHandler.prototype.checkForSyntaxErrors = function (statementLocation, cursorPosition) {
      var self = this;
      if (self.sqlSyntaxWorkerSub !== null && (self.snippet.type() === 'impala' || self.snippet.type() === 'hive'))  {
        var AceRange = ace.require('ace/range').Range;
        var editorChangeTime = self.editor.lastChangeTime;
        var beforeCursor = self.editor.getSession().getTextRange(new AceRange(statementLocation.first_line - 1, statementLocation.first_column, cursorPosition.row, cursorPosition.column));
        var afterCursor = self.editor.getSession().getTextRange(new AceRange(cursorPosition.row, cursorPosition.column, statementLocation.last_line - 1, statementLocation.last_column));
        huePubSub.publish('ace.sql.syntax.worker.post', {
          id: self.snippet.id(),
          editorChangeTime: editorChangeTime,
          beforeCursor: beforeCursor,
          afterCursor: afterCursor,
          statementLocation: statementLocation,
          type: self.snippet.type()
        });
      }
    };

    AceLocationHandler.prototype.addAnchoredMarker = function (range, token, clazz) {
      var self = this;
      range.start = self.editor.getSession().doc.createAnchor(range.start);
      range.end = self.editor.getSession().doc.createAnchor(range.end);
      var markerId = self.editor.getSession().addMarker(range, clazz);
      var marker = self.editor.getSession().$backMarkers[markerId];
      marker.token = token;
      marker.dispose = function () {
        range.start.detach();
        range.end.detach();
        delete marker.token.syntaxError;
        delete marker.token.notFound;
        self.editor.getSession().removeMarker(markerId);
      }
    };

    AceLocationHandler.prototype.attachSqlSyntaxWorker = function () {
      var self = this;

      if (self.sqlSyntaxWorkerSub !== null) {
        return;
      }

      self.sqlSyntaxWorkerSub = huePubSub.subscribe('ace.sql.syntax.worker.message', function (e) {
        if (e.data.id !== self.snippet.id() || e.data.editorChangeTime !== self.editor.lastChangeTime) {
          return;
        }
        self.clearMarkedErrors('error');

        if (!e.data.syntaxError || !e.data.syntaxError.expected || e.data.syntaxError.expected.length === 0) {
          // Only show errors that we have suggestions for
          return;
        }

        var suppressedRules = ApiHelper.getInstance().getFromTotalStorage('hue.syntax.checker', 'suppressedRules', {});
        if (e.data.syntaxError && e.data.syntaxError.ruleId && !suppressedRules[e.data.syntaxError.ruleId.toString() + e.data.syntaxError.text.toLowerCase()]) {
          if (self.snippet.positionStatement() && SqlUtils.locationEquals(e.data.statementLocation, self.snippet.positionStatement().location)) {
            self.snippet.positionStatement().syntaxError = true;
          }
          if (hueDebug.showSyntaxParseResult) {
            console.log(e.data.syntaxError);
          }

          var token = self.editor.getSession().getTokenAt(e.data.syntaxError.loc.first_line - 1, e.data.syntaxError.loc.first_column + 1);

          // Don't mark the current edited word as an error if the cursor is at the end of the word
          // For now [a-z] is fine as we only check syntax for keywords
          if (/[a-z]$/i.test(self.editor.getTextBeforeCursor()) && !/^[a-z]/i.test(self.editor.getTextAfterCursor())) {
            var cursorPos = self.editor.getCursorPosition();
            var cursorToken = self.editor.getSession().getTokenAt(cursorPos.row, cursorPos.column);
            if (cursorToken === token) {
              return;
            }
          }

          // If no token is found it likely means that the parser response came back after the text was changed,
          // at which point it will trigger another parse so we can ignore this.
          if (token) {
            token.syntaxError = e.data.syntaxError;
            var AceRange = ace.require('ace/range').Range;
            var range = new AceRange(e.data.syntaxError.loc.first_line - 1, e.data.syntaxError.loc.first_column, e.data.syntaxError.loc.last_line - 1, e.data.syntaxError.loc.first_column + e.data.syntaxError.text.length);
            self.addAnchoredMarker(range,  token, 'hue-ace-syntax-error');
          }
        }
      });

      huePubSub.publish('editor.refresh.statement.locations', self.snippet);
    };

    AceLocationHandler.prototype.detachSqlSyntaxWorker = function () {
      var self = this;
      if (self.sqlSyntaxWorkerSub !== null) {
        self.sqlSyntaxWorkerSub.remove();
        self.sqlSyntaxWorkerSub = null;
      }
      self.clearMarkedErrors();
    };

    AceLocationHandler.prototype.fetchChildren = function (identifierChain) {
      var self = this;
      var deferred = $.Deferred();
      DataCatalog.getChildren({
        sourceType: self.snippet.type(),
        namespace: self.snippet.namespace(),
        compute: self.snippet.compute(),
        path: $.map(identifierChain, function (identifier) { return identifier.name }),
        silenceErrors: true,
        cachedOnly: true
      }).done(deferred.resolve).fail(function () {
        deferred.reject([]);
      });
      return deferred;
    };

    AceLocationHandler.prototype.fetchPossibleValues = function (token) {
      var self = this;
      var promise = $.Deferred();
      if (token.parseLocation.tables && token.parseLocation.tables.length > 0) {
        var tablePromises = [];
        token.parseLocation.tables.forEach(function (table) {
          if (table.identifierChain) {
            tablePromises.push(self.fetchChildren(table.identifierChain));
          }
        });
        $.when.apply($, tablePromises).done(function () {
          var joined = [];
          for (var i = 0; i < arguments.length; i++) {
            joined = joined.concat(arguments[i]);
          }
          promise.resolve(joined);
        }).fail(promise.reject);
      } else if (token.parseLocation.identifierChain && token.parseLocation.identifierChain.length > 0) {
        // fetch the parent
        return self.fetchChildren(token.parseLocation.identifierChain.slice(0, token.parseLocation.identifierChain.length - 1));
      } else {
        promise.reject([]);
      }
      return promise;
    };

    var VERIFY_LIMIT = 50;
    var VERIFY_DELAY = 50;

    var verifyThrottle = -1;

    AceLocationHandler.prototype.verifyExists = function (tokens, allLocations) {
      var self = this;
      window.clearInterval(verifyThrottle);
      self.clearMarkedErrors('warning');

      if (self.sqlSyntaxWorkerSub === null) {
        return;
      }

      var cursorPos = self.editor.getCursorPosition();

      var tokensToVerify = tokens.filter(function (token) {
        return token && token.parseLocation
          && (token.parseLocation.type === 'table' || token.parseLocation.type === 'column')
          && (token.parseLocation.identifierChain || token.parseLocation.tables)
          && !(cursorPos.row + 1 === token.parseLocation.location.last_line && cursorPos.column + 1 === token.parseLocation.location.first_column + token.value.length)
      }).slice(0, VERIFY_LIMIT);

      if (tokensToVerify.length === 0) {
        return;
      }

      var aliasIndex = {};
      var aliases = [];

      allLocations.forEach(function (location) {
        if (location.type === 'alias' && (location.source === 'column' || location.source === 'table' || location.source === 'subquery' || location.source === 'cte')) {
          aliasIndex[location.alias.toLowerCase()] = location;
          aliases.push({ name: location.alias.toLowerCase() })
        }
      });

      var resolvePathFromTables = function (location) {
        var promise = $.Deferred();
        if (location.type === 'column' && typeof location.tables !== 'undefined' && location.identifierChain.length === 1) {
          var findIdentifierChainInTable = function (tablesToGo) {
            var nextTable = tablesToGo.shift();
            if (typeof nextTable.subQuery === 'undefined') {
              DataCatalog.getChildren({
                sourceType: self.snippet.type(),
                namespace: self.snippet.namespace(),
                compute: self.snippet.compute(),
                path: $.map(nextTable.identifierChain, function (identifier) { return identifier.name }),
                cachedOnly: true,
                silenceErrors: true
              }).done(function (entries) {
                var containsColumn = entries.some(function (entry) {
                  return SqlUtils.identifierEquals(entry.name, location.identifierChain[0].name);
                });

                if (containsColumn) {
                  location.identifierChain = nextTable.identifierChain.concat(location.identifierChain);
                  delete location.tables;
                  promise.resolve();
                } else if (tablesToGo.length > 0) {
                  findIdentifierChainInTable(tablesToGo);
                } else {
                  promise.resolve();
                }
              }).fail(promise.resolve);
            } else if (tablesToGo.length > 0) {
              findIdentifierChainInTable(tablesToGo);
            } else {
              promise.resolve();
            }
          };
          if (location.tables.length > 1) {
            findIdentifierChainInTable(location.tables.concat());
          } else if (location.tables.length === 1 && location.tables[0].identifierChain) {
            location.identifierChain = location.tables[0].identifierChain.concat(location.identifierChain);
            delete location.tables;
            promise.resolve();
          }
        } else {
          promise.resolve();
        }
        return promise;
      };

      var verify = function () {
        if (tokensToVerify.length === 0) {
          return;
        }
        var token = tokensToVerify.shift();
        var location = token.parseLocation;

        // TODO: Verify columns in subqueries, i.e. 'code' in 'select code from (select * from web_logs) wl, customers c;'
        if ((location.type === 'column' || location.type === 'complex') && location.tables) {
          var hasSubQueries = location.tables.some(function (table) {
            return typeof table.subQuery !== 'undefined';
          });
          if (hasSubQueries) {
            verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
            return;
          }
        }

        resolvePathFromTables(location).done(function () {
          if (location.type === 'column') {
            var possibleAlias;
            if (!location.tables && location.identifierChain && location.identifierChain.length > 1) {
              possibleAlias = aliasIndex[token.parseLocation.identifierChain[0].name.toLowerCase()];
            } else if (location.tables) {
              location.tables.some(function (table) {
                if (table.identifierChain && table.identifierChain.length === 1 && table.identifierChain[0].name) {
                  possibleAlias = aliasIndex[table.identifierChain[0].name.toLowerCase()];
                  return possibleAlias;
                }
                return false;
              });
            }
            if (possibleAlias && possibleAlias.source === 'cte') {
              // We currently don't discover the columns from a CTE so we can't say if a column exists or not
              verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
              return;
            }
          }

          self.fetchPossibleValues(token).done(function (possibleValues) {
            // Tokens might change while making api calls
            if (!token.parseLocation) {
              verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
              return;
            }

            // Append aliases unless qualified i.e.for 'b' in SELECT a.b we shouldn't suggest aliases
            if ((token.parseLocation.type !== 'column' && token.parseLocation.type !== 'complex') || !token.parseLocation.qualified) {
              possibleValues = possibleValues.concat(aliases);
            }

            var tokenValLower = token.actualValue.toLowerCase();
            var uniqueIndex = {};
            var uniqueValues = [];
            for (var i = 0; i < possibleValues.length; i++) {
              possibleValues[i].name = SqlUtils.backTickIfNeeded(self.snippet.type(), possibleValues[i].name);
              var nameLower = possibleValues[i].name.toLowerCase();
              if ((nameLower === tokenValLower) || (tokenValLower.indexOf('`') === 0 && tokenValLower.replace(/`/g, '') === nameLower)) {
                // Break if found
                verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
                return;
              }
              if (!uniqueIndex[nameLower]) {
                uniqueValues.push(possibleValues[i]);
                uniqueIndex[nameLower] = true;
              }
            }
            possibleValues = uniqueValues;

            var isLowerCase = tokenValLower === token.value;

            var weightedExpected = $.map(possibleValues, function (val) {
              return {
                text: isLowerCase ? val.name.toLowerCase() : val.name,
                distance: SqlParseSupport.stringDistance(token.value, val.name)
              }
            });
            weightedExpected.sort(function (a, b) {
              if (a.distance === b.distance) {
                return a.text.localeCompare(b.text);
              }
              return a.distance - b.distance
            });
            token.syntaxError = {
              expected: weightedExpected.slice(0, 50)
            };
            token.notFound = true;

            if (token.parseLocation && token.parseLocation.type === 'table') {
              var path = $.map(token.parseLocation.identifierChain, function (identifier) { return identifier.name; });
              token.qualifiedIdentifier = path.join('.');
            }

            if (token.parseLocation && weightedExpected.length > 0) {
              var AceRange = ace.require('ace/range').Range;
              var range = new AceRange(token.parseLocation.location.first_line - 1, token.parseLocation.location.first_column - 1, token.parseLocation.location.last_line - 1, token.parseLocation.location.last_column - 1);
              self.addAnchoredMarker(range,  token, 'hue-ace-syntax-warning');
            }
            verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
          }).fail(function () {
            // Can happen when tables aren't cached etc.
            verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
          });
        }).fail(function () {
          // Can happen when tables aren't cached etc.
          verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
        });
      };

      verifyThrottle = window.setTimeout(verify, VERIFY_DELAY);
    };

    AceLocationHandler.prototype.isDatabase = function (databaseIdentifier) {
      var self = this;
      if (!databaseIdentifier) {
        return false;
      }
      var cleanIdentifier = databaseIdentifier.replace(/^\s*`/, '').replace(/`\s*$/, '').toLowerCase();
      return self.databaseIndex[cleanIdentifier];
    };

    AceLocationHandler.prototype.attachSqlWorker = function () {
      var self = this;

      var activeTokens = [];

      var lastKnownLocations = {};

      var getLocationsSub = huePubSub.subscribe('get.active.editor.locations', function (callback, snippet) {
        if (self.snippet === snippet || self.snippet.inFocus() || self.snippet.editorMode()) {
          callback(lastKnownLocations);
        }
      });

      self.disposeFunctions.push(function () {
        getLocationsSub.remove();
      });

      var locationWorkerSub = huePubSub.subscribe('ace.sql.location.worker.message', function (e) {
        if (e.data.id !== self.snippet.id() || e.data.editorChangeTime !== self.editor.lastChangeTime || !self.snippet.isSqlDialect()) {
          return;
        }

        lastKnownLocations = {
          id: self.editorId,
          type: self.snippet.type(),
          namespace: self.snippet.namespace(),
          compute: self.snippet.compute(),
          defaultDatabase: self.snippet.database(),
          locations: e.data.locations,
          editorChangeTime: e.data.editorChangeTime,
          activeStatementLocations: e.data.activeStatementLocations,
          totalStatementCount: e.data.totalStatementCount,
          activeStatementIndex: e.data.activeStatementIndex
        };

        // Clear out old parse locations to prevent them from being shown when there's a syntax error in the statement
        while (activeTokens.length > 0) {
          delete activeTokens.pop().parseLocation;
        }

        var tokensToVerify = [];

        e.data.locations.forEach(function (location) {
          if (['statement', 'selectList', 'whereClause', 'limitClause'].indexOf(location.type) !== -1
            || ((location.type === 'table' || location.type === 'column') && typeof location.identifierChain === 'undefined')) {
            return;
          }

          if (location.identifierChain && location.identifierChain.length && location.identifierChain[0].name) {
            // The parser isn't aware of the DDL so sometimes it marks complex columns as tables
            // I.e. "Impala SELECT a FROM b.c" Is 'b' a database or a table? If table then 'c' is complex
            if (self.snippet.type() === 'impala' &&
              location.identifierChain.length > 2 &&
              (location.type === 'table' || location.type === 'column') &&
              self.isDatabase(location.identifierChain[0].name)) {
              location.type = 'complex';
            }
          }

          var token = self.editor.getSession().getTokenAt(location.location.first_line - 1, location.location.first_column);

          // Find open UDFs and prevent them from being marked as missing columns, i.e. cos in "SELECT * FROM foo where cos(a|"
          var rowTokens = self.editor.getSession().getTokens(location.location.first_line - 1);
          if (location.type === 'column' && token && rowTokens) {
            var tokenFound = false;
            var isFunction = false;
            rowTokens.some(function (rowToken) {
              if (tokenFound && /\s+/.test(rowToken.value)) {
                return false;
              }
              if (tokenFound) {
                isFunction = rowToken.value === '(';
                return true;
              }
              if (rowToken === token) {
                tokenFound = true;
              }
            });
            if (isFunction) {
              location.type = 'function';
              delete location.identifierChain;
              location.function = token.value;
              token = null;
            }
          }

          if (token && token.value && /`$/.test(token.value)) {
            // Ace getTokenAt() thinks the first ` is a token, column +1 will include the first and last.
            token = self.editor.getSession().getTokenAt(location.location.first_line - 1, location.location.first_column + 1);
          }
          if (token && token.value && /^\s*\$\{\s*$/.test(token.value)) {
            token = null;
          }
          if (token && token.value) {
            var AceRange = ace.require('ace/range').Range;
            // The Ace tokenizer also splits on '{', '(' etc. hence the actual value;
            token.actualValue = self.editor.getSession().getTextRange(new AceRange(location.location.first_line - 1, location.location.first_column - 1, location.location.last_line - 1, location.location.last_column - 1));
          }

          if (token !== null) {
            token.parseLocation = location;
            activeTokens.push(token);
            delete token.notFound;
            delete token.syntaxError;
            if (location.active) {
              tokensToVerify.push(token);
            }
          }
        });

        if (self.snippet.type() === 'impala' || self.snippet.type() === 'hive') {
          self.verifyExists(tokensToVerify, e.data.activeStatementLocations);
        }
        huePubSub.publish('editor.active.locations', lastKnownLocations);

      });

      self.disposeFunctions.push(function () {
        locationWorkerSub.remove();
      });

      var statementSubscription = huePubSub.subscribe('editor.active.statement.changed', function (statementDetails) {
        if (statementDetails.id !== self.editorId) {
          return;
        }
        if (self.snippet.type() === 'hive' || self.snippet.type() === 'impala') {
          huePubSub.publish('ace.sql.location.worker.post', {
            id: self.snippet.id(),
            statementDetails: statementDetails,
            type: self.snippet.type(),
            namespace: self.snippet.namespace(),
            compute: self.snippet.compute(),
            defaultDatabase: self.snippet.database()
          });
        }
      });

      self.disposeFunctions.push(function () {
        statementSubscription.remove();
      });
    };

    AceLocationHandler.prototype.dispose = function () {
      var self = this;
      if (self.sqlSyntaxWorkerSub !== null) {
        self.sqlSyntaxWorkerSub.remove();
        self.sqlSyntaxWorkerSub = null;
      }

      self.disposeFunctions.forEach(function (dispose) {
        dispose();
      })
    };

    return AceLocationHandler;
  })();

  ko.bindingHandlers.aceEditor = {
    init: function (element, valueAccessor) {

      var $el = $(element);
      var options = ko.unwrap(valueAccessor());
      var snippet = options.snippet;
      var aceOptions = options.aceOptions || {};

      var disposeFunctions = [];

      var dispose = function () {
        disposeFunctions.forEach(function (dispose) {
          dispose();
        })
      };

      ko.utils.domNodeDisposal.addDisposeCallback(element, dispose);

      $el.text(snippet.statement_raw());

      var editor = ace.edit($el.attr("id"));
      var Tooltip = ace.require("ace/tooltip").Tooltip;
      var AceRange = ace.require('ace/range').Range;

      var resizeAce = function () {
        window.setTimeout(function () {
          try {
            editor.resize(true);
          } catch (e) {
            // Can happen when the editor hasn't been initialized
          }
        }, 0);
      };

      var assistToggleSub = huePubSub.subscribe('assist.set.manual.visibility', resizeAce);
      var resizePubSub = huePubSub.subscribe('split.panel.resized', resizeAce);
      disposeFunctions.push(function () {
        assistToggleSub.remove();
        resizePubSub.remove();
      });

      var aceLocationHandler = new AceLocationHandler(editor, $el.attr("id"), snippet);
      disposeFunctions.push(function () {
        aceLocationHandler.dispose();
      });

      editor.session.setMode(snippet.getAceMode());
      editor.setOptions({ fontSize: snippet.getApiHelper().getFromTotalStorage('hue.ace', 'fontSize', navigator.platform && navigator.platform.toLowerCase().indexOf("linux") > -1 ? '14px' : '12px')});

      function processErrorsAndWarnings(type, list) {
        editor.clearErrorsAndWarnings(type);
        var offset = 0;
        if (snippet.isSqlDialect() && editor.getSelectedText()) {
          var selectionRange = editor.getSelectionRange();
          offset = Math.min(selectionRange.start.row, selectionRange.end.row);
        }
        if (list.length > 0) {
          list.forEach(function (item, cnt) {
            if (item.line !== null) {
              if (type === 'error') {
                editor.addError(item.message, item.line + offset);
              } else {
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

      var darkThemeEnabled = ApiHelper.getInstance().getFromTotalStorage('ace', 'dark.theme.enabled', false);
      editor.setTheme(darkThemeEnabled ? 'ace/theme/hue_dark' : 'ace/theme/hue');

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

      editor.customMenuOptions = {
        setEnableDarkTheme: function (enabled) {
          darkThemeEnabled = enabled;
          ApiHelper.getInstance().setInTotalStorage('ace', 'dark.theme.enabled', darkThemeEnabled);
          editor.setTheme(darkThemeEnabled ? 'ace/theme/hue_dark' : 'ace/theme/hue');
        },
        getEnableDarkTheme: function () {
          return darkThemeEnabled;
        },
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
        },
        setFontSize: function (size) {
          if (size.toLowerCase().indexOf('px') === -1 && size.toLowerCase().indexOf('em') === -1) {
            size += 'px';
          }
          editor.setOption('fontSize', size);
          snippet.getApiHelper().setInTotalStorage('hue.ace', 'fontSize', size);
        },
        getFontSize: function () {
          var size = editor.getOption('fontSize');
          if (size.toLowerCase().indexOf('px') === -1 && size.toLowerCase().indexOf('em') === -1) {
            size += 'px';
          }
          return size;
        }
      };

      if (ENABLE_SQL_SYNTAX_CHECK && window.Worker) {
        var errorHighlightingEnabled = snippet.getApiHelper().getFromTotalStorage('hue.ace', 'errorHighlightingEnabled', true);

        if (errorHighlightingEnabled) {
          aceLocationHandler.attachSqlSyntaxWorker();
        }

        editor.customMenuOptions.setErrorHighlighting = function (enabled) {
          errorHighlightingEnabled = enabled;
          snippet.getApiHelper().setInTotalStorage('hue.ace', 'errorHighlightingEnabled', enabled);
          if (enabled) {
            aceLocationHandler.attachSqlSyntaxWorker();
          } else {
            aceLocationHandler.detachSqlSyntaxWorker();
          }
        };
        editor.customMenuOptions.getErrorHighlighting = function () {
          return errorHighlightingEnabled;
        };
        editor.customMenuOptions.setClearIgnoredSyntaxChecks = function (flag) {
          ApiHelper.getInstance().setInTotalStorage('hue.syntax.checker', 'suppressedRules', {});
          $('#setClearIgnoredSyntaxChecks').hide();
          $('#setClearIgnoredSyntaxChecks').before('<div style="margin-top:5px;float:right;">done</div>');
        };
        editor.customMenuOptions.getClearIgnoredSyntaxChecks = function () {
          return false;
        }
      }

      $.extend(editorOptions, aceOptions);

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

      var UNICODES_TO_REMOVE = /[\u1680\u180E\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u200B\u202F\u205F\u3000\uFEFF]/ig;  //taken from https://www.cs.tut.fi/~jkorpela/chars/spaces.html

      var removeUnicodes = function (value) {
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

      var pasteListener = editor.on('paste', function (e) {
        e.text = removeUnicodes(e.text);
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

      if (snippet.aceCursorPosition()) {
        editor.moveCursorToPosition(snippet.aceCursorPosition());
        window.setTimeout(function () {
          editor.centerSelection();
        }, 0);
      }

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

      var changeSelectionListener = editor.selection.on('changeSelection', function () {
        snippet.selectedStatement(editor.getSelectedText());
      });

      disposeFunctions.push(function () {
        editor.selection.off('changeSelection', changeSelectionListener);
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

        var popoverShownSub = huePubSub.subscribe('context.popover.shown', function () {
          hideContextTooltip();
          keepLastMarker = true;
          disableTooltip = true;
        });

        disposeFunctions.push(function () {
          popoverShownSub.remove();
        });

        var popoverHiddenSub = huePubSub.subscribe('context.popover.hidden', function () {
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
              if (token !== null && !token.notFound && token.parseLocation && !disableTooltip && token.parseLocation.type !== 'alias') {
                tooltipTimeout = window.setTimeout(function () {
                  if (token.parseLocation) {
                    var endCoordinates = editor.renderer.textToScreenCoordinates(pointerPosition.row, token.start);

                    var tooltipText = token.parseLocation.type === 'asterisk' ? options.expandStar : options.contextTooltip;
                    var colType;
                    if (token.parseLocation.type === 'column') {
                      var tableChain = token.parseLocation.identifierChain.concat();
                      var lastIdentifier = tableChain.pop();
                      if (tableChain.length > 0 && lastIdentifier && lastIdentifier.name) {
                        var colName = lastIdentifier.name.toLowerCase();
                        // Note, as cachedOnly is set to true it will call the successCallback right away (or not at all)
                        DataCatalog.getEntry({
                          sourceType: snippet.type(),
                          namespace: snippet.namespace(),
                          compute: snippet.compute(),
                          path: $.map(tableChain, function (identifier) { return identifier.name })
                        }).done(function (entry) {
                          entry.getSourceMeta({ cachedOnly: true, silenceErrors: true }).done(function (sourceMeta) {
                            if (sourceMeta && sourceMeta.extended_columns) {
                              sourceMeta.extended_columns.every(function (col) {
                                if (col.name.toLowerCase() === colName) {
                                  colType = col.type.match(/^[^<]*/g)[0];
                                  return false;
                                }
                                return true;
                              })
                            }
                          });
                        });
                      }
                    }
                    if (token.parseLocation.identifierChain) {
                      var sqlIdentifier = $.map(token.parseLocation.identifierChain, function (identifier) {
                          return identifier.name
                        }).join('.');
                      if (colType) {
                        sqlIdentifier += ' (' + colType + ')';
                      }
                      tooltipText = sqlIdentifier + ' - ' + tooltipText;
                    } else if (token.parseLocation.function) {
                      tooltipText = token.parseLocation.function + ' - ' + tooltipText;
                    }
                    contextTooltip.show(tooltipText, endCoordinates.pageX, endCoordinates.pageY + editor.renderer.lineHeight + 3);
                  }
                }, 500);
              } else if (token !== null && token.notFound) {
                tooltipTimeout = window.setTimeout(function () {
                  // TODO: i18n
                  if (token.notFound && token.syntaxError) {
                    var tooltipText;
                    if (token.syntaxError.expected.length > 0) {
                      tooltipText = HUE_I18n.syntaxChecker.didYouMean + ' "' + token.syntaxError.expected[0].text + '"?';
                    } else {
                      tooltipText = HUE_I18n.syntaxChecker.couldNotFind + ' "' + (token.qualifiedIdentifier || token.value) + '"';
                    }
                    var endCoordinates = editor.renderer.textToScreenCoordinates(pointerPosition.row, token.start);
                    contextTooltip.show(tooltipText, endCoordinates.pageX, endCoordinates.pageY + editor.renderer.lineHeight + 3);
                  }
                }, 500);
              } else if (token !== null && token.syntaxError) {
                tooltipTimeout = window.setTimeout(function () {
                  // TODO: i18n
                  if (token.syntaxError) {
                    var tooltipText;
                    if (token.syntaxError.expected.length > 0) {
                      tooltipText = HUE_I18n.syntaxChecker.didYouMean + ' "' + token.syntaxError.expected[0].text + '"?';
                    } else if (token.syntaxError.expectedStatementEnd) {
                      tooltipText = HUE_I18n.syntaxChecker.expectedStatementEnd;
                    }
                    if (tooltipText) {
                      var endCoordinates = editor.renderer.textToScreenCoordinates(pointerPosition.row, token.start);
                      contextTooltip.show(tooltipText, endCoordinates.pageX, endCoordinates.pageY + editor.renderer.lineHeight + 3);
                    }
                  }
                }, 500);
              } else {
                hideContextTooltip();
              }
              if (lastHoveredToken !== token) {
                clearActiveMarkers();
                if (token !== null && !token.notFound && token.parseLocation && ['alias', 'whereClause', 'limitClause', 'selectList'].indexOf(token.parseLocation.type) === -1) {
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
          editor.off('input', inputListener);
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

        var onContextMenu = function (e) {
          var selectionRange = editor.selection.getRange();
          huePubSub.publish('context.popover.hide');
          huePubSub.publish('sql.syntax.dropdown.hide');
          if (selectionRange.isEmpty()) {
            var pointerPosition = editor.renderer.screenToTextCoordinates(e.clientX + 5, e.clientY);
            var token = editor.session.getTokenAt(pointerPosition.row, pointerPosition.column);
            if (token && ((token.parseLocation && ['alias', 'whereClause', 'limitClause', 'selectList'].indexOf(token.parseLocation.type) === -1) || token.syntaxError)) {
              var range = token.parseLocation ? markLocation(token.parseLocation) : new AceRange(token.syntaxError.loc.first_line - 1, token.syntaxError.loc.first_column, token.syntaxError.loc.last_line - 1, token.syntaxError.loc.first_column + token.syntaxError.text.length);
              var startCoordinates = editor.renderer.textToScreenCoordinates(range.start.row, range.start.column);
              var endCoordinates = editor.renderer.textToScreenCoordinates(range.end.row, range.end.column);
              var source = {
                 // TODO: add element likely in the event
                left: startCoordinates.pageX - 3,
                top: startCoordinates.pageY,
                right: endCoordinates.pageX - 3,
                bottom: endCoordinates.pageY + editor.renderer.lineHeight
              };

              if (token.parseLocation && token.parseLocation.identifierChain && !token.notFound) {
                token.parseLocation.resolveCatalogEntry().done(function (entry) {
                  huePubSub.publish('context.popover.show', {
                    data: {
                      type: 'catalogEntry',
                      catalogEntry: entry
                    },
                    pinEnabled: true,
                    source: source
                  });
                }).fail(function () {
                  token.notFound = true;
                });
              } else if (token.parseLocation && !token.notFound) {
                // Asterisk, function etc.
                if (token.parseLocation.type === 'file') {
                  AssistStorageEntry.getEntry(token.parseLocation.path).done(function (entry) {
                    entry.open(true);
                    huePubSub.publish('context.popover.show', {
                      data: {
                        type: 'storageEntry',
                        storageEntry: entry,
                        editorLocation: token.parseLocation.location
                      },
                      pinEnabled: true,
                      source: source
                    });
                  });
                } else {
                  huePubSub.publish('context.popover.show', {
                    data: token.parseLocation,
                    sourceType: snippet.type(),
                    namespace: snippet.namespace(),
                    compute: snippet.compute(),
                    defaultDatabase: snippet.database(),
                    pinEnabled: true,
                    source: source
                  });
                }
              } else if (token.syntaxError) {
                huePubSub.publish('sql.syntax.dropdown.show', {
                  snippet: snippet,
                  data: token.syntaxError,
                  editor: editor,
                  range: range,
                  sourceType: snippet.type(),
                  defaultDatabase: snippet.database(),
                  source: source
                });
              }
              e.preventDefault();
              return false;
            }
          }
        };

        var contextmenuListener = editor.container.addEventListener('contextmenu', onContextMenu);

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
        name: 'switchTheme',
        bindKey: { win: 'Ctrl-Alt-t', mac: 'Command-Alt-t' },
        exec: function () {
          darkThemeEnabled = !darkThemeEnabled;
          ApiHelper.getInstance().setInTotalStorage('ace', 'dark.theme.enabled', darkThemeEnabled);
          editor.setTheme(darkThemeEnabled ? 'ace/theme/hue_dark' : 'ace/theme/hue');
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
        name: "esc",
        bindKey: {win: "Ctrl-Shift-p", mac: "Ctrl-Shift-p|Command-Shift-p"},
        exec: function () {
          huePubSub.publish('editor.presentation.toggle');
        }
      });

      editor.commands.bindKey("Ctrl-P", "golineup");

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

      var insertSqlAtCursor = function (text, cursorEndAdjust, menu) {
        var before = editor.getTextBeforeCursor();
        if (/\S+$/.test(before)) {
          text = " " + text;
        }
        if (menu) {
          menu.hide();
        }
        editor.session.insert(editor.getCursorPosition(), text);
        if (cursorEndAdjust !== 0) {
          var cursor = editor.getCursorPosition();
          editor.moveCursorToPosition({ row: cursor.row, column: cursor.column + cursorEndAdjust });
        }
        editor.clearSelection();
        editor.focus();
      };

      var insertTableAtCursorSub = huePubSub.subscribe('editor.insert.table.at.cursor', function(details) {
        if ($el.data('last-active-editor')) {
          var qualifiedName = snippet.database() == details.database ? details.name : details.database + '.' + details.name;
          if (isNewStatement()) {
            insertSqlAtCursor('SELECT * FROM ' + qualifiedName + ' LIMIT 100;', -1);
          } else {
            insertSqlAtCursor(qualifiedName + ' ', 0);
          }
        }
      });

      var insertColumnAtCursorSub = huePubSub.subscribe('editor.insert.column.at.cursor', function(details) {
        if ($el.data('last-active-editor')) {
          if (isNewStatement()) {
            var qualifiedFromName = snippet.database() == details.database ? details.table : details.database + '.' + details.table;
            insertSqlAtCursor('SELECT '  + details.name + ' FROM ' + qualifiedFromName + ' LIMIT 100;', -1);
          } else {
            insertSqlAtCursor(details.name + ' ', 0);
          }
        }
      });

      var insertAtCursorSub = huePubSub.subscribe('editor.insert.at.cursor', function(text) {
        if ($el.data('last-active-editor')) {
          insertSqlAtCursor(text + ' ', 0);
        }
      });

      disposeFunctions.push(function () {
        insertTableAtCursorSub.remove();
        insertColumnAtCursorSub.remove();
        insertAtCursorSub.remove();

      });

      var dblClickHdfsItemSub = huePubSub.subscribe("assist.dblClickHdfsItem", function(assistHdfsEntry) {
        if ($el.data("last-active-editor")) {
          editor.session.insert(editor.getCursorPosition(), "'" + assistHdfsEntry.path + "'");
        }
      });

      disposeFunctions.push(function () {
        dblClickHdfsItemSub.remove();
      });

      var dblClickAdlsItemSub = huePubSub.subscribe("assist.dblClickAdlsItem", function(assistHdfsEntry) {
        if ($el.data("last-active-editor")) {
          editor.session.insert(editor.getCursorPosition(), "adl:/" + assistHdfsEntry.path + "'");
        }
      });

      disposeFunctions.push(function () {
        dblClickAdlsItemSub.remove();
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
        var text = "SELECT * FROM " + table + " LIMIT 100;";
        insertSqlAtCursor(text, -1);
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
        if (meta.isView) {
          $tableDropMenu.find('.editor-drop-update').hide();
          $tableDropMenu.find('.editor-drop-insert').hide();
          $tableDropMenu.find('.editor-drop-drop').hide();
          $tableDropMenu.find('.editor-drop-view').show();
        } else {
          $tableDropMenu.find('.editor-drop-update').show();
          $tableDropMenu.find('.editor-drop-insert').show();
          $tableDropMenu.find('.editor-drop-drop').show();
          $tableDropMenu.find('.editor-drop-view').hide();
        }
        if (typeof meta !== 'undefined' && typeof meta.database !== 'undefined' && typeof meta.table !== 'undefined') {
          $identifierDropMenu.text(meta.database + '.' + meta.table)
        }
      });

      disposeFunctions.push(function () {
        draggableTextSub.remove();
      });

      var menu = ko.bindingHandlers.contextMenu.initContextMenu($tableDropMenu, $('.content-panel'));

      $tableDropMenu.find('.editor-drop-value').click(function () {
        insertSqlAtCursor(SqlUtils.backTickIfNeeded(lastMeta.type, lastMeta.database) + '.' + SqlUtils.backTickIfNeeded(lastMeta.type, lastMeta.table) + ' ', 0, menu);
      });

      $tableDropMenu.find('.editor-drop-select').click(function () {
        insertSqlAtCursor('SELECT * FROM ' + SqlUtils.backTickIfNeeded(lastMeta.type, lastMeta.database) + '.' + SqlUtils.backTickIfNeeded(lastMeta.type, lastMeta.table) + ' LIMIT 100;', -1, menu);
        $tableDropMenu.hide();
      });

      $tableDropMenu.find('.editor-drop-insert').click(function () {
        insertSqlAtCursor('INSERT INTO ' + SqlUtils.backTickIfNeeded(lastMeta.type, lastMeta.database) + '.' + SqlUtils.backTickIfNeeded(lastMeta.type, lastMeta.table) + ' VALUES ();', -2, menu);
      });

      $tableDropMenu.find('.editor-drop-update').click(function () {
        insertSqlAtCursor('UPDATE ' + SqlUtils.backTickIfNeeded(lastMeta.type, lastMeta.database) + '.' + SqlUtils.backTickIfNeeded(lastMeta.type, lastMeta.table) + ' SET ', 0, menu);
      });

      $tableDropMenu.find('.editor-drop-view').click(function () {
        insertSqlAtCursor('DROP VIEW ' + SqlUtils.backTickIfNeeded(lastMeta.type, lastMeta.database) + '.' + SqlUtils.backTickIfNeeded(lastMeta.type, lastMeta.table) + ';', -1, menu);
      });

      $tableDropMenu.find('.editor-drop-drop').click(function () {
        insertSqlAtCursor('DROP TABLE ' + SqlUtils.backTickIfNeeded(lastMeta.type, lastMeta.database) + '.' + SqlUtils.backTickIfNeeded(lastMeta.type, lastMeta.table) + ';', -1, menu);
      });

      $el.droppable({
        accept: ".draggableText",
        drop: function (e, ui) {
          var position = editor.renderer.screenToTextCoordinates(e.clientX, e.clientY);
          var text = ui.helper.text();
          if (lastMeta.type === 's3' || lastMeta.type === 'hdfs' || lastMeta.type === 'adls'){
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
            var lineOffset = snippet.lastAceSelectionRowOffset();
            window.setTimeout(function () {
              editor.session.addMarker(new AceRange(range.start.row + lineOffset, range.start.column, range.end.row + lineOffset, range.end.column), 'highlighted', 'line');
              ace.require('ace/lib/dom').importCssString('.highlighted {\
                  background-color: #E3F7FF;\
                  position: absolute;\
              }');
              editor.scrollToLine(range.start.row + lineOffset, true, true, function () {});
            }, 0);
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

      if (allBindings().checkedValue) {
        viewModel = ko.unwrap(allBindings().checkedValue);
      }

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
      $(element).addClass('hue-checkbox fa');

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
        ko.utils.toggleDomNodeCssClass(element, 'fa-check', allValues().length > 0 && selectedValues().length === allValues().length);
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

      var scrollToIndex = function (idx, offset, instant, callback) {
        var lastKnownHeights = $parentFVOwnerElement.data('lastKnownHeights');
        if (! lastKnownHeights || lastKnownHeights.length <= idx) {
          return;
        }
        var top = 0;
        for (var i = 0; i < idx; i++) {
          top += lastKnownHeights[i];
        }
        var bottom = top + lastKnownHeights[idx];
        window.setTimeout(function () {
          var newScrollTop = top + offset;
          if (instant) {
            if (newScrollTop >= $container.height() + $container.scrollTop()) {
              $container.scrollTop(bottom - $container.height());
            } else if (newScrollTop <= $container.scrollTop()) {
              $container.scrollTop(newScrollTop);
            }
          } else {
            $container.stop().animate({ scrollTop: newScrollTop }, '500', 'swing', function () {
              if (callback) {
                callback();
              }
            });
          }
        }, 0);

      };

      if (!options.skipScrollEvent) {
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
            scrollToIndex(foundIndex, offset, false, function () {
              huePubSub.publish('assist.db.scrollToComplete', targetEntry);
            });
          }
        }));
      }

      if (ko.isObservable(viewModel.foreachVisible)) {
        viewModel.foreachVisible({
          scrollToIndex: function (index) {
            var offset = depth > 0 ? $parentFVOwnerElement.position().top : 0;
            scrollToIndex(index, offset, true);
          }
        })
      }

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

      var $wrapper = $element.parent();
      if (!$wrapper.hasClass('foreach-wrapper')) {
        $wrapper = $('<div>').css({
          'position': 'relative',
          'width': '100%'
        }).addClass('foreach-wrapper').insertBefore($element);
        if (options.usePreloadBackground) {
          $wrapper.addClass('assist-preloader-wrapper');
          $element.addClass('assist-preloader');
        }
        $element.css({
          'position': 'absolute',
          'top': 0,
          'width': '100%'
        }).appendTo($wrapper);
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
        if (!lastKnownHeights) {
          return;
        }
        $.each(lastKnownHeights, function(idx, height) {
          totalHeight += height;
        });
        $wrapper.height(totalHeight + 'px');
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
        var updateEntryCount = false;
        $.each(renderedElements, function (idx, renderedElement) {
          // TODO: Figure out why it goes over index at the end scroll position
          if (startIndex + idx < lastKnownHeights.length) {
            var renderedHeight = $(renderedElement).outerHeight(true);
            if (renderedHeight > 5 && lastKnownHeights[startIndex + idx] !== renderedHeight) {
              if (renderedHeight < entryMinHeight) {
                entryMinHeight = renderedHeight;
                updateEntryCount = true;
              }
              lastKnownHeights[startIndex + idx] = renderedHeight;
              diff = true;
            }
          }
        });

        if (updateEntryCount) {
          updateVisibleEntryCount();
        }
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
        if (typeof options.fetchMore !== 'undefined' && endIndex === allEntries.length - 1) {
          options.fetchMore();
        }
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
        if (!lastKnownHeights) {
          return;
        }

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
      var preloadGhostThrottle = -1;
      var lastScrollTop = -1;
      var onScroll = function () {
        if (startIndex > incrementLimit && Math.abs(lastScrollTop - $container.scrollTop()) < (incrementLimit * options.minHeight)) {
          return;
        }
        lastScrollTop = $container.scrollTop();

        setStartAndEndFromScrollTop();

        // adds a preload ghost image just on scroll and removes it 200ms after the scroll stops
        if (options.usePreloadBackground) {
          $wrapper.addClass('assist-preloader-ghost');
          clearTimeout(preloadGhostThrottle);
          preloadGhostThrottle = setTimeout(function () {
            $wrapper.removeClass('assist-preloader-ghost');
          }, 200);
        }

        clearTimeout(renderThrottle);
        var startDiff = Math.abs($parentFVOwnerElement.data('startIndex') - startIndex);
        var endDiff = Math.abs($parentFVOwnerElement.data('endIndex') - endIndex);
        if (startDiff > incrementLimit
          || endDiff > incrementLimit
          || (startDiff !== 0 && startIndex === 0)
          || (endDiff !== 0 && endIndex === allEntries.length - 1))  {
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
      var triggerAdjust = options.triggerAdjust || 0;
      var zIndex = options.zIndex || 1000;
      $(element).addClass('dockable');

      var initialTopPosition = -1;
      var initialSize = {
        w: $(element).width() - hueUtils.scrollbarWidth(),
        h: $(element).outerHeight() + (options.jumpCorrection || 0)
      };

      var ghost = $('<div>').css({'display': 'none', 'height': initialSize.h}).insertBefore($(element));

      function dock() {
        if (initialTopPosition == -1) {
          initialTopPosition = $(element).position().top;
          ghost.height($(element).outerHeight() + (options.jumpCorrection || 0));
        }
        if ($(scrollable).scrollTop() + triggerAdjust > initialTopPosition) {
          $(element).attr('style', 'position: fixed!important; top: ' + options.topSnap + '; width: ' + initialSize.w + 'px!important; z-index: ' + zIndex);
          ghost.show();
        }
        else {
          $(element).removeAttr('style');
          ghost.hide();
        }
      }

      $(scrollable).on('scroll', dock);

      var scrollOffSubscription = huePubSub.subscribe('scrollable.scroll.off', function (scrollElement) {
        if (scrollElement === scrollable) {
          $(scrollable).on('scroll', dock);
        }
      });


      function resetInitialStyle() {
        $(element).removeAttr('style');
        initialSize = {
          w: $(element).width() - hueUtils.scrollbarWidth(),
          h: $(element).outerHeight() + (options.jumpCorrection || 0)
        };
        dock();
      }

      $(window).on('resize', resetInitialStyle);

      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        $(window).off('resize', resetInitialStyle);
        $(scrollable).off('scroll', dock);
        scrollOffSubscription.remove();
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

  ko.bindingHandlers.readOnlyAce = {
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
      $(element).data('aceEditor', editor);
    },
    update: function (element, valueAccessor, allBindingsAccessor) {
      var value = ko.unwrap(valueAccessor());
      var options = ko.unwrap(allBindingsAccessor());
      $(element).data('aceEditor').getSession().setMode("ace/mode/" + options.type || 'xml'); // e.g. xml, json...
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
          'ace/layer/text',
          'ace/config'
        ], function (impalaRules, hiveRules, xmlRules, tokenizer, text, config) {
          var res = [];

          var Tokenizer = tokenizer.Tokenizer;
          var Rules = hiveRules.HiveHighlightRules;
          if (options.dialect && ko.unwrap(options.dialect) == 'impala') {
            Rules = impalaRules.ImpalaHighlightRules;
          }

          config.loadModule(["theme", $.totalStorage("hue.ace.theme") || "ace/theme/hue"]);

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
          $(element).find('.ace_invisible_space').remove();
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
        var fMoment = moment(value);
        var text;
        if (!fMoment.isValid()) {
          text = value;
        } else {
          if (options.format) {
            text = fMoment.format(options.format);
          }
          else {
            text = fMoment.format();
          }
        }
        $element.text(text);
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
        isS3: !!options.isS3,
        root: options.root,
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
        'shell-doc': 'query-shell',
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
        var tempType = ko.unwrap(options.type);
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
          ApiHelper.getInstance().searchDocuments({
            type: type,
            text: query,
            include_trashed: false,
            limit: 100,
            successCallback: function(data){
              callback(data.documents)
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
      var $el = $(element);

      function splitStrings(str) {
        var bits = [];
        var isInQuotes = false;
        var tempStr = '';
        str.replace(/<\/?arg>|<\/?command>/gi, ' ').replace(/\r?\n|\r/g, '').replace(/\s\s+/g, ' ').split('').forEach(function (char) {
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
            obj[valueAccessor().objectKey] = $.trim(arg);
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
      } else {
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
      if (value.disabled) {
        return;
      }
      var options = {
        autoDiscover: false,
        maxFilesize: 5000000,
        previewsContainer: '#progressStatusContent',
        previewTemplate: '<div class="progress-row">' +
        '<span class="break-word" data-dz-name></span>' +
        '<div class="pull-right">' +
        '<span class="muted" data-dz-size></span>&nbsp;&nbsp;' +
        '<span data-dz-remove><a href="javascript:undefined;" title="' + HUE_I18n.dropzone.cancelUpload + '"><i class="fa fa-fw fa-times"></i></a></span>' +
          '<span style="display: none" data-dz-uploaded><i class="fa fa-fw fa-check muted"></i></span>' +
        '</div>' +
        '<div class="progress-row-bar" data-dz-uploadprogress></div>' +
        '</div>',
        sending: function (e) {
          $('.hoverMsg').addClass('hide');
          $('#progressStatus').removeClass('hide');
          $('#progressStatusBar').removeClass('hide');
          $('#progressStatus .progress-row').remove();
          $('#progressStatusBar div').css('width', '0');
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
          $.jHueNotify.info(HUE_I18n.dropzone.uploadCanceled);
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
                $(document).trigger('info', response.path + ' ' + HUE_I18n.dropzone.uploadSucceeded);
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
      
      $(element).on('click', function (e) {
        e.stopPropagation();
      });

      new Dropzone(element, options);
    }
  };

  ko.bindingHandlers.jHueRowSelector = {
    init: function (element, valueAccessor) {
      $(element).jHueRowSelector();
    }
  };

  //https://stackoverflow.com/questions/19865364/knockoutjs-linking-value-from-a-input-to-a-datalist-value
  ko.bindingHandlers.datalist = (function () {
    function getVal(rawItem, prop) {
      var item = ko.unwrap(rawItem);
      return item && prop ? ko.unwrap(item[prop]) : item;
    }

    function findItem(options, prop, ref) {
      return ko.utils.arrayFirst(options, function (item) {
        return ref === getVal(item, prop);
      });
    }
    return {
      init: function (element, valueAccessor, allBindingsAccessor) {
        var setup = valueAccessor(),
          textProperty = ko.unwrap(setup.optionsText),
          valueProperty = ko.unwrap(setup.optionsValue),
          dataItems = ko.unwrap(setup.options),
          myValue = setup.value,
          koValue = allBindingsAccessor().value,
          datalist = document.createElement("DATALIST");

        // create an associated <datalist> element
        datalist.id = element.getAttribute("list");
        document.body.appendChild(datalist);

        // when the value is changed, write to the associated myValue observable
        function onNewValue(newVal) {
          var setup = valueAccessor(),
            dataItems = ko.unwrap(setup.options),
            selectedItem = findItem(dataItems, textProperty, newVal),
            newValue = selectedItem ? getVal(selectedItem, valueProperty) : newVal;

          if (ko.isWriteableObservable(myValue)) {
            myValue(newValue);
          }
        }

        // listen for value changes
        // - either via KO's value binding (preferred) or the change event
        if (ko.isSubscribable(koValue)) {
          var onNewValueSubscription = koValue.subscribe(onNewValue);
          ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
            onNewValueSubscription.remove();
          });
        } else {
          var event = allBindingsAccessor().valueUpdate === "afterkeydown" ? "input" : "change";
          ko.utils.registerEventHandler(element, event, function () {
            onNewValue(this.value);
          });
        }

        // init the element's value
        // - either via the myValue observable (preferred) or KO's value binding
        if (ko.isObservable(myValue) && myValue()) {
          var selectedItem = findItem(dataItems, valueProperty, myValue());
          element.value = selectedItem ? getVal(selectedItem, textProperty) : myValue();
        } else if (ko.isObservable(koValue) && koValue()) {
          onNewValue(koValue());
        }
      },
      update: function (element, valueAccessor) {
        var setup = valueAccessor(),
          datalist = element.list,
          dataItems = ko.unwrap(setup.options),
          textProperty = ko.unwrap(setup.optionsText);

        // rebuild list of options when an underlying observable changes
        datalist.innerHTML = "";
        ko.utils.arrayForEach(dataItems, function (item) {
          var option = document.createElement("OPTION");
          option.value = getVal(item, textProperty);
          datalist.appendChild(option);
        });
        ko.utils.triggerEvent(element, "change");
      }
    };
  })();

  ko.bindingHandlers.impalaDagre = (function () {
    return {
      init: function (element, valueAccessor, allBindingsAccessor) {
        var id = $(element).attr("id");
        this._impalaDagre = impalaDagre(id);
      },
      update: function (element, valueAccessor) {
        var props = ko.unwrap(valueAccessor());
        this._impalaDagre.update(props.value);
        this._impalaDagre.height(props.height);
      }
    };
  })();

  ko.bindingHandlers.dropdown = {
    init: function (element, valueAccessor) {
        $(element).dropdown();
    }
  };

})();
