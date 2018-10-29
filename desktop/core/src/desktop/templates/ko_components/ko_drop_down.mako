## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
from desktop import conf
from desktop.lib.i18n import smart_unicode

from django.utils.translation import ugettext as _
from desktop.views import _ko
%>

<%def name="dropDown()">

  <script type="text/html" id="hue-drop-down-template">
    <!-- ko if: !menuOnly && (!dropDownVisible() || !searchable) -->
    <a class="inactive-action hue-drop-down-active" href="javascript:void(0)" data-bind="toggle: dropDownVisible, css: { 'blue': dropDownVisible }">
      <!-- ko if: icon --><i class="fa" data-bind="css: icon"></i><!-- /ko -->
      <!-- ko if: !noLabel && value -->
      <span class="hue-drop-down-selected" data-bind="text: value() && typeof value()[labelAttribute] !== 'undefined' ? value()[labelAttribute] : value(), visible: ! dropDownVisible() || !searchable, attr: { 'title': value() && typeof value()[labelAttribute] !== 'undefined' ? value()[labelAttribute] : value() }" ></span>
      <!-- /ko -->
      <i class="fa fa-caret-down"></i>
    </a>
    <!-- /ko -->
    <!-- ko if: !menuOnly && (dropDownVisible() && searchable) -->
    <input class="hue-drop-down-input" type="text" data-bind="textInput: filter, attr: { 'placeHolder': inputPlaceHolder }, visible: dropDownVisible, style: { color: filterEdited() ? '#000' : '#AAA', 'min-height': '22px', 'margin-left': '10px' }"/>
    <i class="fa fa-caret-down"></i>
    <!-- /ko -->
    <div class="hue-drop-down-container" data-bind="css: { 'open' : dropDownVisible, 'hue-drop-down-fixed': fixedPosition, 'hue-drop-down-container-searchable': searchable }, dropDownKeyUp: { onEsc: onEsc, onEnter: onEnter, dropDownVisible: dropDownVisible }">
      <div class="dropdown-menu" data-bind="visible: filteredEntries().length > 0, style: { 'overflow-y': !foreachVisible ? 'auto' : 'hidden' }">
        <!-- ko if: foreachVisible -->
        <ul class="hue-inner-drop-down" data-bind="foreachVisible: { data: filteredEntries, minHeight: 34, container: '.dropdown-menu' }">
          <!-- ko if: typeof $data.divider !== 'undefined' && $data.divider -->
          <li class="divider"></li>
          <!-- /ko -->
          <!-- ko if: typeof $data.divider === 'undefined' || !$data.divider -->
          <li><a href="javascript:void(0)" data-bind="text: $data && typeof $data[$parent.labelAttribute] !== 'undefined' ? $data[$parent.labelAttribute] : $data, click: function () { var previous = $parent.value(); $parent.value($data); $parent.onSelect($data, previous); }"></a></li>
          <!-- /ko -->
        </ul>
        <!-- /ko -->
        <!-- ko ifnot: foreachVisible -->
        <ul class="hue-inner-drop-down" data-bind="foreach: filteredEntries">
          <!-- ko if: typeof $data.divider !== 'undefined' && $data.divider -->
          <li class="divider"></li>
          <!-- /ko -->
          <!-- ko if: typeof $data.divider === 'undefined' || !$data.divider -->
          <li><a href="javascript:void(0)" data-bind="text: $data && typeof $data[$parent.labelAttribute] !== 'undefined' ? $data[$parent.labelAttribute] : $data, click: function () { var previous = $parent.value(); $parent.value($data); $parent.onSelect($data, previous); }"></a></li>
          <!-- /ko -->
        </ul>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      ko.bindingHandlers.dropDownKeyUp = {
        init: function (element, valueAccessor) {
          var options = valueAccessor();
          var onEsc = options.onEsc;
          var onEnter = options.onEnter;
          var onSelected = options.onSelected;
          var dropDownVisible = options.dropDownVisible;

          var keyUpTarget = options.keyUpTarget || window;

          var keyUp = function (e) {
            var $element = $(element);
            var $dropDownMenu = $element.find('.dropdown-menu');
            var $currentActive = $element.find('.hue-inner-drop-down > .active');
            var activeTop = $currentActive.length !== 0 ? $currentActive.position().top : 0;
            var activeHeight = $currentActive.length !== 0 ? $currentActive.outerHeight(true) : $element.find('.hue-inner-drop-down li:first-child').outerHeight(true);
            var containerHeight = $dropDownMenu.innerHeight();
            var containerScrollTop = $dropDownMenu.scrollTop();

            $currentActive.removeClass('active');
            if (e.keyCode === 27 && onEsc) {
              onEsc();
            } else if (e.keyCode === 38) {
              // up
              var $nextActive;
              if ($currentActive.length !== 0 && $currentActive.prev().length !== 0) {
                if (activeTop < containerScrollTop + activeHeight) {
                  $dropDownMenu.scrollTop(activeTop - containerHeight / 2);
                }
                $nextActive = $currentActive.prev().addClass('active');
              }
              if (onSelected) {
                onSelected($nextActive && $nextActive.length ? ko.dataFor($nextActive[0]) : undefined);
              }
            } else if (e.keyCode === 40) {
              // down
              var $nextActive;
              if ($currentActive.length === 0) {
                $nextActive = $element.find('.hue-inner-drop-down li:first-child').addClass('active');
              } else if ($currentActive.next().length !== 0) {
                if ((activeTop + activeHeight * 3) > containerHeight - containerScrollTop) {
                  $dropDownMenu.scrollTop(activeTop - containerHeight / 2);
                }
                $nextActive = $currentActive.next().addClass('active');
              } else {
                $nextActive = $currentActive.addClass('active');
              }

              if (onSelected) {
                onSelected($nextActive && $nextActive.length ? ko.dataFor($nextActive[0]) : undefined);
              }
            } else if (e.keyCode === 13) {
              // enter
              if ($currentActive.length > 0) {
                $dropDownMenu.scrollTop(0)
              }
              if (onEnter) {
                onEnter($currentActive.length ? ko.dataFor($currentActive[0]) : undefined);
              }
            } else {
              $dropDownMenu.scrollTop(0)
            }
          };

          var visibleSub = dropDownVisible.subscribe(function (newValue) {
            if (newValue) {
              $(keyUpTarget).on('keyup.hueDropDown', keyUp);
              $(keyUpTarget).on('keydown.hueDropDown', function (e) {
                // This prevents the cursor from moving left or right on up and down
                if (e.keyCode === 38 || e.keyCode === 40) {
                  e.preventDefault();
                }
              })
            } else {
              $(keyUpTarget).off('keyup.hueDropDown');
              $(keyUpTarget).off('keydown.hueDropDown');
            }
          });

          ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
            visibleSub.dispose();
            $(keyUpTarget).off('keyup.hueDropDown');
          });
        }
      };

      var HueDropDown = function (params, element) {
        var self = this;
        self.dropDownVisible = ko.observable(!!params.showOnInit);
        self.menuOnly = !!params.menuOnly;
        self.noLabel = !!params.noLabel;
        self.labelAttribute = params.labelAttribute || 'label';
        self.icon = params.icon;
        self.value = params.value;
        self.entries = params.entries;
        self.searchable = params.searchable || false;
        self.foreachVisible = params.foreachVisible || false;
        self.linkTitle = params.linkTitle || '${ _('Selected entry') }';
        self.fixedPosition = !!params.fixedPosition;
        self.onSelect = params.onSelect || function () {};

        self.inputPlaceHolder = ko.pureComputed(function () {
          return self.value() && typeof self.value() === 'object' ? self.value()[self.labelAttribute] : self.value();
        });

        var closeOnOutsideClick = function (e) {
          var $input = $(element).find('.hue-drop-down-input');
          if (!$input.is($(e.target))) {
            self.dropDownVisible(false);
          }
        };

        self.onEsc = function () {
          self.dropDownVisible(false);
        };

        self.onEnter = function (value) {
          var previous = self.value();
          self.value(value);
          self.onSelect(value, previous);
          self.dropDownVisible(false);
        };

        self.filter = ko.observable('');

        self.value.subscribe(function () {
          self.dropDownVisible(false);
        });

        self.filterEdited = ko.observable(false);

        self.filter.subscribe(function () {
          self.filterEdited(true);
          $(element).find('.hue-inner-drop-down > .active').removeClass('.active');
        });

        self.dropDownVisible.subscribe(function (newValue) {
          self.filterEdited(false);
          if (newValue) {
            window.setTimeout(function () {
              self.filter('');
              $(window).on('click', closeOnOutsideClick);
              $(element).find('.hue-drop-down-input').focus();
            }, 0);

            // Right align the dropdown when outside the right edge
            if (!self.fixedPosition) {
              var $element = $(element);
              var $dropDownMenu = $element.find('.dropdown-menu').parent();
              var $offsetParent = $element.offsetParent();

              var rightLimit = $offsetParent.offset().left + $offsetParent.width();

              if ($dropDownMenu.offset().left + 160 > rightLimit) {
                var $caret = $element.find('.fa-caret-down');
                var caretRight = $caret.offset().left + $caret.width();

                var diff = -$dropDownMenu.offset().left - 160 + caretRight;
                $element.find('.hue-drop-down-container').css({ 'margin-left': diff + 'px' });
              }
            }
          } else {
            $(element).find('.hue-inner-drop-down > .active').removeClass('.active');
            $(window).off('click', closeOnOutsideClick);
          }
        });

        self.filteredEntries = ko.pureComputed(function () {
          if (self.filter() === '' || ! self.filterEdited()) {
            return ko.unwrap(self.entries);
          } else {
            var lowerFilter = self.filter().toLowerCase();
            return ko.unwrap(self.entries).filter(function (entry) {
              if (typeof entry === 'object') {
                return entry[self.labelAttribute].toLowerCase().indexOf(lowerFilter) !== -1;
              }
              return entry.toLowerCase().indexOf(lowerFilter) !== -1;
            });
          }
        });
      };

      ko.components.register('hue-drop-down', {
        viewModel: {
          createViewModel: function(params, componentInfo) {
            return new HueDropDown(params, componentInfo.element);
          }
        },
        template: { element: 'hue-drop-down-template' }
      });
    })();
  </script>

</%def>