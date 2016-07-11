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

(function (factory) {
  if(typeof define === "function") {
    define("ko.hue-bindings", ["knockout"], factory);
  } else {
    factory(ko);
  }
}(function (ko) {

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
   * <!-- ko hueSpinner: loading --><!-- /ko -->
   *
   * Or with options:
   *
   * <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
   *
   */
  ko.bindingHandlers.hueSpinner = {
    update: function (element, valueAccessor) {
      var value = ko.unwrap(valueAccessor);

      var options = {
        size: 'default',
        center: false
      };

      var spin = false;
      if (ko.isObservable(valueAccessor())) {
        spin = value();
      } else {
        var value = valueAccessor();
        $.extend(options, value);
        spin = ko.isObservable(value.spin) ? value.spin() : value.spin;
      }

      ko.virtualElements.emptyNode(element);

      if (spin) {
        var container = document.createElement('DIV');
        container.className = 'hue-spinner';
        var spinner = document.createElement('I');
        spinner.className = 'fa fa-spinner fa-spin';
        if (options.size === 'large') {
          spinner.className += ' hue-spinner-large';
        }
        if (options.center) {
          spinner.className += ' hue-spinner-center';
        }
        container.appendChild(spinner);
        ko.virtualElements.prepend(element, container);
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
      ko.utils.domData.set(element, 'visibleOnHover.override', ko.utils.unwrapObservable(options.override) || false)
      var inside = false;

      var show = function () {
        $element.find(selector).fadeTo("fast", 1);
        window.clearTimeout(hideTimeout);
      };

      var hide = function () {
        if (! inside) {
          window.clearTimeout(showTimeout);
          hideTimeout = window.setTimeout(function () {
            $element.find(selector).fadeTo("fast", 0);
          }, 10);
        }
      };

      ko.utils.domData.set(element, 'visibleOnHover.show', show)
      ko.utils.domData.set(element, 'visibleOnHover.hide', hide)

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
        };
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
              }, 275);
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
      }

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
              '<div class="facet-field-cnt picker">' +
              '<div class="facet-field-label facet-field-label-fixed-width"></div>' +
              '<div class="facet-field-switch"><a href="javascript:void(0)"><i class="fa fa-calendar-o"></i> ' + KO_DATERANGEPICKER_LABELS.CUSTOM_FORMAT + '</a></div>' +
              '</div>' +
              '<div class="facet-field-cnt custom">' +
              '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.START + '</div>' +
              '<div class="input-prepend input-group">' +
              '<span class="add-on input-group-addon"><i class="fa fa-calendar"></i></span>' +
              '<input type="text" class="input-large form-control start-date-custom" />' +
              '</div>' +
              '<a class="custom-popover" href="javascript:void(0)" data-trigger="focus" data-toggle="popover" data-placement="right" rel="popover" data-html="true"' +
              '       title="' + KO_DATERANGEPICKER_LABELS.CUSTOM_POPOVER_TITLE + '"' +
              '       data-content="' + KO_DATERANGEPICKER_LABELS.CUSTOM_POPOVER_CONTENT + '">' +
              '&nbsp;&nbsp;<i class="fa fa-question-circle"></i>' +
              ' </a>' +
              '</div>' +
              '<div class="facet-field-cnt custom">' +
              '<div class="facet-field-label facet-field-label-fixed-width">' + KO_DATERANGEPICKER_LABELS.END + '</div>' +
              '<div class="input-prepend input-group">' +
              '<span class="add-on input-group-addon"><i class="fa fa-calendar"></i></span>' +
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
              '<div class="facet-field-cnt custom">' +
              '<div class="facet-field-label facet-field-label-fixed-width"></div>' +
              '<div class="facet-field-switch"><a href="javascript:void(0)"><i class="fa fa-calendar"></i> ' + KO_DATERANGEPICKER_LABELS.DATE_PICKERS + '</a></div>' +
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
        $('.assist-flex-fill').getNiceScroll().resize();
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
            $('.assist-flex-fill').getNiceScroll().resize();
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
      var $rightPanel = $(".right-panel");
      var $execStatus = $resizer.prev('.snippet-execution-status');

      var lastEditorSize = $.totalStorage('hue.editor.editor.size') || 128;
      var editorHeight = Math.floor(lastEditorSize / 16);
      $target.height(lastEditorSize);
      var autoExpand = true;

      ace().on('change', function () {
        if (autoExpand) {
          var maxAutoLines = Math.floor((($(window).height() - 80) / 2) / 16);
          var resized = false;
          if (ace().session.getLength() > editorHeight) {
            if (ace().session.getLength() < maxAutoLines) {
              $target.height((ace().session.getLength() + 1) * 16);
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
          if (resized) {
            ace().resize();
            editorHeight = ace().session.getLength();
            huePubSub.publish('redraw.fixed.headers');
          }
        }
      });

      $resizer.draggable({
        axis: "y",
        start: options.onStart ? options.onStart : function(){},
        drag: function (event, ui) {
          autoExpand = false;
          var currentHeight = ui.offset.top + $rightPanel.scrollTop() - (125 + $execStatus.outerHeight(true));
          $target.css("height", currentHeight + "px");
          ace().resize();
          ui.offset.top = 0;
          ui.position.top = 0;
        },
        stop: function (event, ui) {
          ui.offset.top = 0;
          ui.position.top = 0;
          $.totalStorage('hue.editor.editor.size', $target.height());
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
      $target.css("height", initialHeight + "px");

      var initialOffset = null;
      $resizer.draggable({
        axis: "y",
        start: function (event, ui) {
          if (onStart) {
            onStart();
          }
          if (!initialOffset) {
            initialOffset = $resizer.offset().top;
          }
        },
        drag: function (event, ui) {
          var currentHeight = (ui.offset.top - initialOffset) + initialHeight;
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

  ko.bindingHandlers.splitDraggable = {
    init: function (element, valueAccessor) {
      var options = ko.unwrap(valueAccessor());
      var leftPanelWidth = $.totalStorage(options.appName + "_left_panel_width") != null ? $.totalStorage(options.appName + "_left_panel_width") : 250;

      var containerSelector = options.containerSelector || ".panel-container";
      var leftPanelSelector = options.leftPanelSelector || ".left-panel";
      var rightPanelSelector = options.rightPanelSelector || ".right-panel";

      var onPosition = options.onPosition || function() {};

      var $resizer = $(element);
      var $leftPanel = $(leftPanelSelector);
      var $rightPanel = $(rightPanelSelector);
      var $container = $(containerSelector);

      var positionPanels = function () {
        if (ko.isObservable(options.leftPanelVisible) && ! options.leftPanelVisible()) {
          $rightPanel.css("width", "100%");
          $rightPanel.css("left", "0");
          $resizer.hide();
        } else {
          $resizer.show();
          var totalWidth = $container.width();
          leftPanelWidth = Math.min(leftPanelWidth, totalWidth - 100);
          var rightPanelWidth = totalWidth - leftPanelWidth - $resizer.width();
          $leftPanel.css("width", leftPanelWidth + "px");
          $rightPanel.css("width", rightPanelWidth + "px");
          $resizer.css("left", leftPanelWidth + "px");
          $rightPanel.css("left", leftPanelWidth + $resizer.width() + "px");
        }
        onPosition();
      };

      if (ko.isObservable(options.leftPanelVisible)) {
        options.leftPanelVisible.subscribe(positionPanels);
      }

      var dragTimeout = -1;
      $resizer.draggable({
        axis: "x",
        containment: $container,
        drag: function (event, ui) {
          ui.position.left = Math.min($container.width() - $container.position().left - 200, Math.max(150, ui.position.left));

          dragTimeout = window.setTimeout(function () {
            $leftPanel.css("width", ui.position.left + "px");
            leftPanelWidth = ui.position.left;
            $rightPanel.css("width", $container.width() - ui.position.left - $resizer.width() + "px");
            $rightPanel.css("left", ui.position.left + $resizer.width());
            onPosition();
          }, 10);

        },
        stop: function () {
          $.totalStorage(options.appName + "_left_panel_width", leftPanelWidth);
          window.setTimeout(positionPanels, 100);
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
    update: function (element, valueAccessor, allBindingsAccessor) {
      ko.bindingHandlers.augmenthtml.render(element, valueAccessor, allBindingsAccessor, viewModel);
    }
  }

  ko.bindingHandlers.clearable = {
    init: function (element, valueAccessor, allBindingsAccessor, viewModel) {
      var _el = $(element);

      function tog(v) {
        return v ? "addClass" : "removeClass";
      }

      _el.addClass("clearable");
      _el[tog(valueAccessor()())]("x");
      _el
          .on("input", function () {
            _el[tog(this.value)]("x");
          })
          .on("change", function () {
            valueAccessor()(_el.val());
          })
          .on("blur", function () {
            valueAccessor()(_el.val());
          })
          .on("mousemove", function (e) {
            _el[tog(this.offsetWidth - 18 < e.clientX - this.getBoundingClientRect().left)]("onX");
          })
          .on("click", function (e) {
            if (this.offsetWidth - 18 < e.clientX - this.getBoundingClientRect().left) {
              _el.removeClass("x onX").val("");
              valueAccessor()("");
            }
          });

      if (allBindingsAccessor().valueUpdate != null && allBindingsAccessor().valueUpdate == "afterkeydown") {
        _el.on("keyup", function () {
          valueAccessor()(_el.val());
        });
      }
    },
    update: function (element, valueAccessor, allBindingsAccessor) {
      $(element).val(ko.unwrap(valueAccessor()));
    }
  }

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
    init: function (element, valueAccessor) {
      var local = ko.utils.unwrapObservable(valueAccessor()),
          options = {};

      ko.utils.extend(options, local);

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
      if (typeof valueAccessor.target == "function") {
        elem.val(valueAccessor.target());
      }
      else {
        elem.val(valueAccessor.target);
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
        if (options.data){
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
          skipColumns: options.skipColumns,
          startingPath: options.database + '.',
          rewriteVal: true,
          onPathChange: options.onChange,
          searchEverywhere : options.searchEverywhere || false
        });
      }
      else {
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
      var self = $(element);
      var options = ko.unwrap(allBindingsAccessor());
      self.attr("autocomplete", "off");
      if (typeof valueAccessor() == "function" || typeof valueAccessor().value == "function") {
        self.val(valueAccessor().value ? valueAccessor().value(): valueAccessor()());
        self.data("fullPath", self.val());
        self.attr("data-original-title", self.val());
        if (valueAccessor().displayJustLastBit){
          var _val = self.val();
          self.val(_val.split("/")[_val.split("/").length - 1]);
        }
        self.on("blur", function () {
          if (valueAccessor().value){
            if (valueAccessor().displayJustLastBit){
              var _val = self.data("fullPath");
              valueAccessor().value(_val.substr(0, _val.lastIndexOf("/")) + "/" + self.val());
            }
            else {
              valueAccessor().value(self.val());
            }
            self.data("fullPath", valueAccessor().value());
          }
          else {
            valueAccessor()(self.val());
            self.data("fullPath", valueAccessor()());
          }
          self.attr("data-original-title", self.data("fullPath"));
        });

        if (options.valueUpdate && options.valueUpdate === 'afterkeydown') {
          self.on('keyup', function () {
            if (valueAccessor().value){
              valueAccessor().value(self.val());
            }
            else {
              valueAccessor()(self.val());
            }
          });
        }
      }
      else {
        self.val(valueAccessor());
        self.on("blur", function () {
          valueAccessor(self.val());
        });
        if (options.valueUpdate && options.valueUpdate === 'afterkeydown') {
          self.on('keyup', function () {
            valueAccessor(self.val());
          });
        }
      }

      self.after(getFileBrowseButton(self, true, valueAccessor, true, allBindingsAccessor, valueAccessor().isAddon, valueAccessor().isNestedModal));
    }
  };


  function getFileBrowseButton(inputElement, selectFolder, valueAccessor, stripHdfsPrefix, allBindingsAccessor, isAddon, isNestedModal) {
    var _btn;
    if (isAddon) {
      _btn = $("<span>").addClass("add-on muted pointer").text("..");
    } else {
      _btn = $("<button>").addClass("btn").addClass("fileChooserBtn").text("..");
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
        $("#filechooser").jHueFileChooser({
          suppressErrors: true,
          selectFolder: (selectFolder) ? true : false,
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
          filterExtensions: allBindingsAccessor && allBindingsAccessor().filechooserFilter ? allBindingsAccessor().filechooserFilter : ""
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

      $el.text(snippet.statement_raw());

      var editor = ace.edit($el.attr("id"));
      editor.session.setMode(snippet.getAceMode());
      if (navigator.platform && navigator.platform.toLowerCase().indexOf("linux") > -1) {
        editor.setOptions({ fontSize: "14px" });
      }

      snippet.errors.subscribe(function(newErrors) {
        editor.clearErrors();
        var offset = 0;
        if (snippet.isSqlDialect()) {
          if (editor.getSelectedText()){
            var selectionRange = editor.getSelectionRange();
            offset = Math.min(selectionRange.start.row, selectionRange.end.row);
          }
          if (snippet.result && snippet.result.statements_count() > 1){
            offset = snippet.result.statement_range().start.row;
          }
        }
        if (newErrors.length > 0) {
          newErrors.forEach(function (err, cnt) {
            if (err.line !== null) {
              editor.addError(err.message, err.line + offset);
              if (cnt == 0) {
                editor.scrollToLine(err.line + offset, true, true, function () {});
              }
            }
          });
        }
      });

      editor.setTheme($.totalStorage("hue.ace.theme") || "ace/theme/hue");

      var editorOptions = {
        enableBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: true,
        showGutter: false,
        showLineNumbers: false,
        showPrintMargin: false,
        minLines: 1,
        maxLines: 25
      };

      $.extend(editorOptions, aceOptions);

      editor.setOptions(editorOptions);

      var AceAutocomplete = ace.require("ace/autocomplete").Autocomplete;

      if (!editor.completer) {
        editor.completer = new AceAutocomplete();
      }
      editor.completer.exactMatch = ! snippet.isSqlDialect();

      var initAutocompleters = function () {
        editor.completers.length = 0;
        if(! options.useNewAutocompleter) {
          editor.completers.push(langTools.snippetCompleter);
          editor.completers.push(langTools.textCompleter);
          editor.completers.push(langTools.keyWordCompleter);
        }
        editor.completers.push(snippet.autocompleter);
      }

      var langTools = ace.require("ace/ext/language_tools");
      langTools.textCompleter.setSqlMode(snippet.isSqlDialect());

      editor.on("focus", initAutocompleters);
      initAutocompleters();

      var removeUnicodes = function (value) {
        var UNICODES_TO_REMOVE = /[\u1680\u180E\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u200B\u202F\u205F\u3000\uFEFF]/ig;  //taken from https://www.cs.tut.fi/~jkorpela/chars/spaces.html
        return value.replace(UNICODES_TO_REMOVE, ' ');
      }

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

      editor.on("input", function() {
        if (editor.getValue().length == 0 && !placeHolderVisible) {
          placeHolderElement.appendTo(editor.renderer.scroller);
          placeHolderVisible = true;
        } else if (placeHolderVisible) {
          placeHolderElement.remove();
          placeHolderVisible = false;
        }
        if (options.updateOnInput){

          snippet.statement_raw(removeUnicodes(editor.getValue()));
        }
        if (editor.session.$backMarkers) {
          for (var marker in editor.session.$backMarkers) {
            if (editor.session.$backMarkers[marker].clazz === 'highlighted') {
              editor.session.removeMarker(editor.session.$backMarkers[marker].id);
            }
          }
        }
      });

      editor.on("focus", function () {
        snippet.inFocus(true);
        $(".ace-editor").data("last-active-editor", false);
        $el.data("last-active-editor", true);
      });

      editor.selection.on("changeSelection", function () {
        snippet.selectedStatement(editor.getSelectedText());
      });

      editor.on("blur", function () {
        snippet.inFocus(false);
        snippet.statement_raw(removeUnicodes(editor.getValue()));
        if (options.onBlur) {
          options.onBlur($el, removeUnicodes(editor.getValue()));
        }
      });

      var currentAssistTables = {};

      var refreshTables = function() {
        currentAssistTables = {};
        if (snippet.database()) {
          apiHelper.fetchTables({
            sourceType: snippet.type(),
            databaseName: snippet.database(),
            successCallback: function(data) {
              $.each(data.tables_meta, function(index, tableMeta) {
                currentAssistTables[tableMeta.name] = true;
              });
            },
            silenceErrors: true
          });
        }
      };
      snippet.database.subscribe(refreshTables);
      refreshTables();

      ace.define("huelink", [], function (require, exports, module) {
        "use strict";

        var Oop = ace.require("ace/lib/oop");
        var Event = ace.require("ace/lib/event");
        var Range = ace.require("ace/range").Range;
        var EventEmitter = ace.require("ace/lib/event_emitter").EventEmitter;
        var Tooltip = ace.require("ace/tooltip").Tooltip;

        var HueLink = function (editor) {
          if (editor.hueLink)
            return;
          editor.hueLink = this;
          this.editor = editor;
          Tooltip.call(this, editor.container);

          this.update = this.update.bind(this);
          this.onMouseMove = this.onMouseMove.bind(this);
          this.onMouseOut = this.onMouseOut.bind(this);
          this.onClick = this.onClick.bind(this);
          Event.addListener(editor.renderer.scroller, "mousemove", this.onMouseMove);
          Event.addListener(editor.renderer.content, "mouseout", this.onMouseOut);
          Event.addListener(editor.renderer.content, "click", this.onClick);
        };

        Oop.inherits(HueLink, Tooltip);

        (function () {
          Oop.implement(this, EventEmitter);

          this.token = {};
          this.marker = null;

          this.update = function () {
            this.$timer = null;
            var editor = this.editor;
            var renderer = editor.renderer;

            var canvasPos = renderer.scroller.getBoundingClientRect();
            var offset = (this.x + renderer.scrollLeft - canvasPos.left - renderer.$padding) / renderer.characterWidth;
            var row = Math.floor((this.y + renderer.scrollTop - canvasPos.top) / renderer.lineHeight);
            var col = Math.round(offset);

            var screenPos = {row: row, column: col, side: offset - col > 0 ? 1 : -1};
            var session = editor.session;
            var docPos = session.screenToDocumentPosition(screenPos.row, screenPos.column);

            var selectionRange = editor.selection.getRange();
            if (!selectionRange.isEmpty()) {
              if (selectionRange.start.row <= row && selectionRange.end.row >= row)
                return this.clear();
            }

            var line = editor.session.getLine(docPos.row);
            if (docPos.column == line.length) {
              var clippedPos = editor.session.documentToScreenPosition(docPos.row, docPos.column);
              if (clippedPos.column != screenPos.column) {
                return this.clear();
              }
            }

            var token = editor.session.getTokenAt(docPos.row, docPos.column);

            if (token) {
              var self = this;
              if (token.value === " * ") {
                snippet.autocompleter.autocomplete(editor.getValue().substring(0, token.start + 1), editor.getValue().substring(token.start + 2), function (suggestions) {
                  var cols = [];
                  $.each(suggestions, function (idx, suggestion) {
                    if (suggestion.meta === "column" && suggestion.value !== "*") {
                      cols.push(suggestion.value);
                    }
                  });
                  if (cols.length > 0) {
                    // add highlight for the clicked token
                    var start = token.value == " * " ? token.start + 1 : token.start;
                    var end = token.value == " * " ? token.start + 2 : token.start + token.value.length;
                    var range = new AceRange(docPos.row, start, docPos.row, end);
                    token.range = range;
                    token.columns = cols;
                    editor.session.removeMarker(self.marker);
                    self.marker = editor.session.addMarker(range, 'ace_bracket red');
                    editor.renderer.setCursorStyle("pointer");
                    self.setText(options.expandStar);
                    if ($.totalStorage("hue.ace.showLinkTooltips") == null || $.totalStorage("hue.ace.showLinkTooltips")) {
                      self.show(null, self.x + 10, self.y + 10);
                    }
                    self.link = token;
                    self.isClearable = true
                  }
                });
              }
              else if (token.value.indexOf("'/") == 0 && token.value.lastIndexOf("'") == token.value.length - 1 ||
                  token.value.indexOf("\"/") == 0 && token.value.lastIndexOf("\"") == token.value.length - 1 ||
                  currentAssistTables[token.value]) {
                // add highlight for the clicked token
                var range = new AceRange(docPos.row, token.start, docPos.row, token.start + token.value.length);
                editor.session.removeMarker(this.marker);
                this.marker = editor.session.addMarker(range, 'ace_bracket red');
                editor.renderer.setCursorStyle("pointer");
                this.setText(options.openIt);
                if ($.totalStorage("hue.ace.showLinkTooltips") == null || $.totalStorage("hue.ace.showLinkTooltips")) {
                  this.show(null, this.x + 10, this.y + 10);
                }
                this.link = token;
                this.isClearable = true
              }
              else {
                this.clear();
              }
            }
            else {
              this.clear();
            }
          };

          this.clear = function () {
            if (this.isClearable) {
              this.hide(); // hides the tooltip
              this.editor.session.removeMarker(this.marker);
              this.editor.renderer.setCursorStyle("");
              this.isClearable = false;
              this.link = null;
            }
          };

          this.onClick = function (e) {
            if (this.link && e.shiftKey) {
              this.link.editor = this.editor;
              this.editor.session.selection.clearSelection();
              this._signal("open", this.link);
              this.clear();
            }
          };

          this.onMouseMove = function (e) {
            if (this.editor.$mouseHandler.isMousePressed) {
              if (!this.editor.selection.isEmpty())
                this.clear();
              return;
            }
            this.x = e.clientX;
            this.y = e.clientY;
            this.update();
          };

          this.onMouseOut = function (e) {
            Tooltip.prototype.hide();
            this.clear();
          };

          this.destroy = function () {
            this.onMouseOut();
            Event.removeListener(this.editor.renderer.scroller, "mousemove", this.onMouseMove);
            Event.removeListener(this.editor.renderer.content, "mouseout", this.onMouseOut);
            delete this.editor.hueLink;
          };

        }).call(HueLink.prototype);

        exports.HueLink = HueLink;
      });

      HueLink = ace.require("huelink").HueLink;
      editor.hueLink = new HueLink(editor);
      editor.hueLink.on("open", function (token) {
        if (token.value === " * " && token.columns.length > 0) {
          editor.session.replace(token.range, token.columns.join(", "))
        } else if (token.value.indexOf("'/") == 0 && token.value.lastIndexOf("'") == token.value.length - 1) {
          window.open("/filebrowser/#" + token.value.replace(/'/gi, ""), '_blank');
        } else if (token.value.indexOf("\"/") == 0 && token.value.lastIndexOf("\"") == token.value.length - 1) {
          window.open("/filebrowser/#" + token.value.replace(/\"/gi, ""), '_blank');
        } else {
          window.open("/metastore/table/" + snippet.database() + "/" + token.value, '_blank');
        }
      });

      editor.previousSize = 0;

      // TODO: Get rid of this
      window.setInterval(function(){
        editor.session.getMode().$id = snippet.getAceMode(); // forces the id again because of Ace command internals
      }, 100);

      editor.middleClick = false;
      editor.on("mousedown", function (e) {
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

      editor.on("change", function (e) {
        snippet.statement_raw(removeUnicodes(editor.getValue()));
        editor.clearErrors();
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
        bindKey: {win: "Ctrl-e", mac: "Command-e|Ctrl-e"},
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
        bindKey: {win: "Ctrl-i", mac: "Command-i|Ctrl-i"},
        exec: function () {
          if (['ace/mode/hive', 'ace/mode/impala', 'ace/mode/sql', 'ace/mode/mysql', 'ace/mode/pgsql', 'ace/mode/sqlite', 'ace/mode/oracle'].indexOf(snippet.getAceMode()) > -1) {
            if (vkbeautify) {
              if (editor.getSelectedText() != '') {
                editor.session.replace(editor.session.selection.getRange(), vkbeautify.sql(editor.getSelectedText(), 2));
              }
              else {
                editor.setValue(vkbeautify.sql(editor.getValue(), 2), 1);
                snippet.statement_raw(removeUnicodes(editor.getValue()));
              }
            }
          }
        }
      });

      huePubSub.subscribe("assist.dblClickDbItem", function(assistDbEntry) {
        if ($el.data("last-active-editor")) {
          var text = assistDbEntry.editorText();
          if (editor.getValue() == "") {
            if (assistDbEntry.definition.isTable) {
              text = "SELECT * FROM " + assistDbEntry.editorText() + " LIMIT 100";
            }
            else if (assistDbEntry.definition.isColumn) {
              text = "SELECT " + assistDbEntry.editorText().split(",")[0] + " FROM " + assistDbEntry.parent.editorText() + " LIMIT 100";
            }
          }
          editor.session.insert(editor.getCursorPosition(), text);
        }
      });

      huePubSub.subscribe("assist.dblClickHdfsItem", function(assistHdfsEntry) {
        if ($el.data("last-active-editor")) {
          editor.session.insert(editor.getCursorPosition(), "'" + assistHdfsEntry.path + "'");
        }
      });

      var $tableDropMenu = $el.next('.table-drop-menu');
      var $identifierDropMenu = $tableDropMenu.find('.editor-drop-identifier')


      var hideDropMenu = function () {
        $tableDropMenu.css('opacity', 0);
        window.setTimeout(function () {
          $tableDropMenu.hide();
        }, 300);
      };

      $(document).click(function (event) {
        if ($tableDropMenu.find($(event.target)).length === 0) {
          hideDropMenu();
        };
      });

      var lastMeta = {};
      huePubSub.subscribe('draggable.text.meta', function (meta) {
        lastMeta = meta;
        if (typeof meta !== 'undefined' && typeof meta.table !== 'undefined') {
          $identifierDropMenu.text(meta.table)
        }
      });

      var menu = ko.bindingHandlers.contextMenu.initContextMenu($tableDropMenu, $('.right-panel'));

      var setFromDropMenu = function (text) {
        var before = editor.getTextBeforeCursor();
        if (/\S+$/.test(before)) {
          text = " " + text;
        }
        editor.session.insert(editor.getCursorPosition(), text);
        menu.hide();
        editor.focus();
      }

      $tableDropMenu.find('.editor-drop-value').click(function () {
        setFromDropMenu(lastMeta.table);
      });

      $tableDropMenu.find('.editor-drop-select').click(function () {
        setFromDropMenu('SELECT * FROM ' + lastMeta.table + ';');
        $tableDropMenu.hide();
      });

      $tableDropMenu.find('.editor-drop-insert').click(function () {
        setFromDropMenu('INSERT INTO ' + lastMeta.table + ' VALUES ();');
      });

      $tableDropMenu.find('.editor-drop-update').click(function () {
        setFromDropMenu('UPDATE ' + lastMeta.table + ' SET ');
      });

      $tableDropMenu.find('.editor-drop-delete').click(function () {
        setFromDropMenu('DELETE FROM ' + lastMeta.table + ' WHERE ');
      });

      var draggableMeta = {};
      huePubSub.subscribe('draggable.text.meta', function (meta) {
        draggableMeta = meta;
      });

      $el.droppable({
        accept: ".draggableText",
        drop: function (e, ui) {
          var position = editor.renderer.screenToTextCoordinates(e.clientX, e.clientY);
          var text = ui.helper.text();
          editor.moveCursorToPosition(position);
          var before = editor.getTextBeforeCursor();
          if (draggableMeta.table && ! draggableMeta.column && /.*;|^\s*$/.test(before)) {
            menu.show(event);
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

      editor.commands.on("afterExec", function (e) {
        if (e.command.name === "insertstring") {
          var triggerAutocomplete = ((editor.session.getMode().$id == "ace/mode/hive" || editor.session.getMode().$id == "ace/mode/impala") && (e.args == "." || e.args == " ")) || /["']\/[^\/]*/.test(editor.getTextBeforeCursor());
          if(e.args.toLowerCase().indexOf("? from ") == 0) {
            if (e.args[e.args.length - 1] !== '.') {
              editor.moveCursorTo(editor.getCursorPosition().row, editor.getCursorPosition().column - e.args.length + 1);
              editor.removeTextBeforeCursor(1);
            }
            triggerAutocomplete = true;
          }

          if (triggerAutocomplete) {
            window.setTimeout(function () {
              editor.execCommand("startAutocomplete");
            }, 1);
          }
        }
        editor.session.getMode().$id = snippet.getAceMode(); // forces the id again because of Ace command internals
        // if it's pig and before it's LOAD ' we disable the autocomplete and show a filechooser btn
        if (editor.session.getMode().$id = "ace/mode/pig" && e.args) {
          var textBefore = editor.getTextBeforeCursor();
          if ((e.args == "'" && textBefore.toUpperCase().indexOf("LOAD ") > -1 && textBefore.toUpperCase().indexOf("LOAD ") == textBefore.toUpperCase().length - 5)
              || textBefore.toUpperCase().indexOf("LOAD '") > -1 && textBefore.toUpperCase().indexOf("LOAD '") == textBefore.toUpperCase().length - 6) {
            editor.disableAutocomplete();
            var btn = editor.showFileButton();
            btn.on("click", function (ie) {
              ie.preventDefault();
              if ($(".ace-filechooser-content").data("spinner") == null) {
                $(".ace-filechooser-content").data("spinner", $(".ace-filechooser-content").html());
              }
              else {
                $(".ace-filechooser-content").html($(".ace-filechooser-content").data("spinner"));
              }
              $(".ace-filechooser-content").jHueFileChooser({
                onFileChoose: function (filePath) {
                  editor.session.insert(editor.getCursorPosition(), filePath + "'");
                  editor.hideFileButton();
                  editor.enableAutocomplete();
                  $(".ace-filechooser").hide();
                },
                selectFolder: false,
                createFolder: false
              });
              $(".ace-filechooser").css({ "top": $(ie.currentTarget).position().top, "left": $(ie.currentTarget).position().left}).show();
            });
          }
          else {
            editor.hideFileButton();
            editor.enableAutocomplete();
          }
          if (e.args != "'" && textBefore.toUpperCase().indexOf("LOAD '") > -1 && textBefore.toUpperCase().indexOf("LOAD '") == textBefore.toUpperCase().length - 6) {
            editor.hideFileButton();
            editor.enableAutocomplete();
          }
        }
      });

      editor.$blockScrolling = Infinity;
      snippet.ace(editor);
    },

    update: function (element, valueAccessor) {
      var options = ko.unwrap(valueAccessor());
      var snippet = options.snippet;
      if (snippet.ace()) {
        var editor = snippet.ace();
        var range = options.highlightedRange ? options.highlightedRange() : null;
        editor.session.setMode(snippet.getAceMode());
        if (range) {
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
   * <div class=".container" style="overflow-y: scroll; height: 100px">
   *  <ul data-bind="foreachVisible: { data: items, minHeight: 20, container: '.container' }">
   *    <li>...</li>
   *  </ul>
   * </div>
   *
   * Currently the binding only supports one element inside the bound element otherwise the height
   * calculations will be off. In other words this will make it go bonkers:
   *
   * <div class=".container" style="overflow-y: scroll; height: 100px">
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
      var updateCountInterval = setInterval(updateVisibleEntryCount, 300);
      updateVisibleEntryCount();

      // In case this element was rendered before use the last known indices
      var startIndex = $parentFVOwnerElement.data('startIndex') || 0;
      var endIndex = $parentFVOwnerElement.data('endIndex') || (visibleEntryCount + elementIncrement);
      if (startIndex > (allEntries.length-1)) {
        startIndex = 0
      }
      if (endIndex > (allEntries.length - 1)) {
        endIndex = allEntries.length - 1;
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
        $element.css({
          'position': 'absolute',
          'top': 0,
          'width': '100%'
        }).appendTo($wrapper);

        $container.niceScroll({
          cursorcolor: "#CCC",
          cursorborder: "1px solid #CCC",
          cursoropacitymin: 0,
          cursoropacitymax: 0.75,
          scrollspeed: 100,
          mousescrollstep: 60,
          cursorminheight: options.cursorminheight || 20,
          horizrailenabled: options.horizrailenabled || false
        });
      }
      else {
        window.setTimeout(function(){
          $container.getNiceScroll().resize();
        }, 200);
      }

      // This is kept up to date with the currently rendered elements, it's used to keep track of any
      // height changes of the elements.
      var renderedElements = [];

      if (! $parentFVOwnerElement.data('lastKnownHeights')) {
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
        $container.getNiceScroll().resize();
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

      huePubSub.subscribe('foreach.visible.update.heights', function (targetId) {
        if (targetId === id) {
          clearInterval(updateHeightsInterval);
          updateLastKnownHeights();
          huePubSub.publish('foreach.visible.update.heights', parentId);
          updateHeightsInterval = window.setInterval(updateLastKnownHeights, 600);
        }
      });

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
        renderedElements = $element.children();
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
          var lastRefOffset = $lastRef.offset().top;
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
        lastScrollTop = $container.scrollTop();;
        setStartAndEndFromScrollTop();
        clearTimeout(renderThrottle);
        if (Math.abs($parentFVOwnerElement.data('startIndex') - startIndex) > incrementLimit ||
            Math.abs($parentFVOwnerElement.data('endIndex') - endIndex) > incrementLimit) {
          renderThrottle = setTimeout(render, 0);
        }
      };

      huePubSub.subscribe('foreach.visible.update', function (callerId) {
        if (callerId === id && endIndex > 0) {
          setStartAndEndFromScrollTop();
          clearTimeout(renderThrottle);
          renderThrottle = setTimeout(render, 0);
        }
      });

      $container.bind('scroll', onScroll);

      $parentFVOwnerElement.data('disposalFunction', function () {
        setTimeout(function () {
          huePubSub.publish('foreach.visible.update.heights', parentId);
        }, 0);
        $container.unbind('scroll', onScroll);
        clearInterval(updateCountInterval);
        clearInterval(updateHeightsInterval);
        $parentFVOwnerElement.data('disposalFunction', null);
      });

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
      }
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
      if (typeof options.enable === 'undefined' || options.enable) {
        $(element).niceScroll({
          cursorcolor: "#CCC",
          cursorborder: "1px solid #CCC",
          cursoropacitymin: 0,
          cursoropacitymax: 0.75,
          scrollspeed: 100,
          mousescrollstep: 60,
          cursorminheight: options.cursorminheight || 20,
          horizrailenabled: options.horizrailenabled || true
        });
        $(element).addClass('nicescrollified');
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

  ko.bindingHandlers.highlight = {
    update: function (element, valueAccessor, allBindingsAccessor) {
      var value = ko.unwrap(valueAccessor());
      var options = ko.unwrap(allBindingsAccessor());

      if (typeof value !== 'undefined') { // allows highlighting static code
        ace.require([
          'ace/mode/impala_highlight_rules',
          'ace/mode/hive_highlight_rules',
          'ace/tokenizer',
          'ace/layer/text'
        ], function (impalaRules, hiveRules, tokenizer, text) {
          var res = [];

          var Tokenizer = tokenizer.Tokenizer;
          var Rules;
          if (options.flavor() == 'impala') {
            Rules = impalaRules.ImpalaHighlightRules;
          } else {
            Rules = hiveRules.HiveHighlightRules;
          }
          var Text = text.Text;

          var tok = new Tokenizer(new Rules().getRules());
          var lines = value.split('\n');

          lines.forEach(function (line) {
            var renderedTokens = [];
            var tokens = tok.getLineTokens(line);

            if (tokens && tokens.tokens.length) {
              try {
                new Text(document.createElement('div')).$renderSimpleLine(renderedTokens, tokens.tokens);
              }
              catch (e) {
                if (console && console.warn) {
                  console.warn(line, 'This line has some parsing errors and it has been skipped.');
                }
              }
            }

            res.push('<div class="ace_line pull-left">' + renderedTokens.join('') + '&nbsp;</div>');
          })

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


  ko.bindingHandlers.attachViewModelToElementData = {
    init: function (el, valueAccessor, allBindingsAccessor, viewModel) {
      $(el).data('__ko_vm', viewModel);
    }
  }

}));