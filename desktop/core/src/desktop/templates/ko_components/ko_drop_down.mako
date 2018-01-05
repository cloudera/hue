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
      <span data-bind="text: typeof value().label !== 'undefined' ? value().label : value(), visible: ! dropDownVisible() || !searchable, attr: { 'title': linkTitle }" ></span>
      <!-- /ko -->
      <i class="fa fa-caret-down"></i>
    </a>
    <!-- /ko -->
    <!-- ko if: !menuOnly && (dropDownVisible() && searchable) -->
    <input class="hue-drop-down-input" type="text" data-bind="textInput: filter, attr: { 'placeHolder': inputPlaceHolder }, visible: dropDownVisible, style: { color: filterEdited() ? '#000' : '#AAA', 'min-height': '22px', 'margin-left': '10px' }"/>
    <i class="fa fa-caret-down"></i>
    <!-- /ko -->
    <div class="hue-drop-down-container" data-bind="css: { 'open' : dropDownVisible, 'hue-drop-down-fixed': fixedPosition }">
      <div class="dropdown-menu" data-bind="visible: filteredEntries().length > 0" style="min-width: 190px; max-width: 250px; min-height: 34px; max-height: 200px;">
        <!-- ko if: foreachVisible -->
        <ul class="hue-inner-drop-down" style="overflow-x: hidden;" data-bind="foreachVisible: { data: filteredEntries, minHeight: 34, container: '.dropdown-menu' }">
          <!-- ko if: typeof $data.divider !== 'undefined' && $data.divider -->
          <li class="divider"></li>
          <!-- /ko -->
          <!-- ko if: typeof $data.divider === 'undefined' || !$data.divider -->
          <li><a href="javascript:void(0)" data-bind="text: typeof $data.label !== 'undefined' ? $data.label : $data, click: function () { $parent.value($data); }"></a></li>
          <!-- /ko -->
        </ul>
        <!-- /ko -->
        <!-- ko ifnot: foreachVisible -->
        <ul class="hue-inner-drop-down" style="overflow-x: hidden;" data-bind="foreach: filteredEntries">
          <!-- ko if: typeof $data.divider !== 'undefined' && $data.divider -->
          <li class="divider"></li>
          <!-- /ko -->
          <!-- ko if: typeof $data.divider === 'undefined' || !$data.divider -->
          <li><a href="javascript:void(0)" data-bind="text: typeof $data.label !== 'undefined' ? $data.label : $data, click: function () { $parent.value($data); }"></a></li>
          <!-- /ko -->
        </ul>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      var HueDropDown = function (params, element) {
        var self = this;
        self.dropDownVisible = ko.observable(!!params.showOnInit);
        self.menuOnly = !!params.menuOnly;
        self.noLabel = !!params.noLabel;
        self.icon = params.icon;
        self.value = params.value;
        self.entries = params.entries;
        self.searchable = params.searchable || false;
        self.foreachVisible = params.foreachVisible || false;
        self.linkTitle = params.linkTitle || '${ _('Selected entry') }';
        self.fixedPosition = !!params.fixedPosition;

        self.inputPlaceHolder = ko.pureComputed(function () {
          return typeof self.value() === 'object' ? self.value().label : self.value();
        });

        var closeOnOutsideClick = function (e) {
          var $input = $(element).find('.hue-drop-down-input');
          if (!$input.is($(e.target))) {
            self.dropDownVisible(false);
          }
        };

        var inputKeyup = function (e) {
          var $currentActive = $(element).find('.hue-inner-drop-down > .active');
          var activeTop = $currentActive.length !== 0 ? $currentActive.position().top : 0;
          var activeHeight = $currentActive.length !== 0 ? $currentActive.outerHeight(true) : $(element).find('.hue-inner-drop-down li:first-child').outerHeight(true);
          var containerHeight = $(element).find('.dropdown-menu').innerHeight();
          var containerScrollTop = $(element).find('.dropdown-menu').scrollTop();

          $currentActive.removeClass('active');
          if (e.keyCode === 27) {
            // esc
            self.dropDownVisible(false);
          } else if (e.keyCode === 38) {
            // up
            if ($currentActive.length !== 0 && $currentActive.prev().length !== 0) {
              if (activeTop < containerScrollTop + activeHeight) {
                $(element).find('.dropdown-menu').scrollTop(activeTop - containerHeight/2);
              }
              $currentActive.prev().addClass('active');
            }
          } else if (e.keyCode === 40) {
            // down
            if ($currentActive.length === 0) {
              $(element).find('.hue-inner-drop-down li:first-child').addClass('active');
            } else if ($currentActive.next().length !== 0) {
              if ((activeTop + activeHeight *3) > containerHeight - containerScrollTop) {
                $(element).find('.dropdown-menu').scrollTop(activeTop - containerHeight/2);
              }
              $currentActive.next().addClass('active');
            } else {
              $currentActive.addClass('active');
            }
          } else if (e.keyCode === 13) {
            // enter
            if ($currentActive.length > 0) {
              self.value(ko.dataFor($currentActive[0]));
              self.dropDownVisible(false);
              $(element).find('.dropdown-menu').scrollTop(0)
            }
          } else {
            $(element).find('.dropdown-menu').scrollTop(0)
          }
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
              $(element).find('.hue-drop-down-input').on('keyup', inputKeyup);
              $(element).find('.hue-drop-down-input').focus();
            }, 0);
          } else {
            $(element).find('.hue-inner-drop-down > .active').removeClass('.active');
            $(window).off('click', closeOnOutsideClick);
            $(element).find('.hue-drop-down-input').off('keyup', inputKeyup);
          }
        });
        self.filteredEntries = ko.pureComputed(function () {
          if (self.filter() === '' || ! self.filterEdited()) {
            return ko.unwrap(self.entries);
          } else {
            var lowerFilter = self.filter().toLowerCase();
            return ko.unwrap(self.entries).filter(function (entry) {
              if (typeof entry === 'object') {
                return entry.label.toLowerCase().indexOf(lowerFilter) !== -1;
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