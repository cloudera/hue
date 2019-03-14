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

import componentUtils from './componentUtils';
import I18n from 'utils/i18n';

const TEMPLATE = `
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
    <div style="overflow-y: auto;" class="dropdown-menu" data-bind="visible: filteredEntries().length > 0">
      <!-- ko if: foreachVisible -->
      <ul class="hue-inner-drop-down" data-bind="foreachVisible: { data: filteredEntries, minHeight: 34, container: '.dropdown-menu' }">
        <!-- ko if: typeof $data.divider !== 'undefined' && $data.divider -->
        <li class="divider"></li>
        <!-- /ko -->
        <!-- ko if: typeof $data.divider === 'undefined' || !$data.divider -->
        <li><a href="javascript:void(0)" data-bind="text: $data && typeof $data[$parent.labelAttribute] !== 'undefined' ? $data[$parent.labelAttribute] : $data, click: function () { let previous = $parent.value(); $parent.value($data); $parent.onSelect($data, previous); }"></a></li>
        <!-- /ko -->
      </ul>
      <!-- /ko -->
      <!-- ko ifnot: foreachVisible -->
      <ul class="hue-inner-drop-down" data-bind="foreach: filteredEntries">
        <!-- ko if: typeof $data.divider !== 'undefined' && $data.divider -->
        <li class="divider"></li>
        <!-- /ko -->
        <!-- ko if: typeof $data.divider === 'undefined' || !$data.divider -->
        <li><a href="javascript:void(0)" data-bind="text: $data && typeof $data[$parent.labelAttribute] !== 'undefined' ? $data[$parent.labelAttribute] : $data, click: function () { let previous = $parent.value(); $parent.value($data); $parent.onSelect($data, previous); }"></a></li>
        <!-- /ko -->
      </ul>
      <!-- /ko -->
    </div>
  </div>
`;

ko.bindingHandlers.dropDownKeyUp = {
  init: function(element, valueAccessor) {
    const options = valueAccessor();
    const onEsc = options.onEsc;
    const onEnter = options.onEnter;
    const onSelected = options.onSelected;
    const dropDownVisible = options.dropDownVisible;

    const keyUpTarget = options.keyUpTarget || window;

    const keyUp = function(e) {
      const $element = $(element);
      const $dropDownMenu = $element.find('.dropdown-menu');
      const $currentActive = $element.find('.hue-inner-drop-down > .active');
      const activeTop = $currentActive.length !== 0 ? $currentActive.position().top : 0;
      const activeHeight =
        $currentActive.length !== 0
          ? $currentActive.outerHeight(true)
          : $element.find('.hue-inner-drop-down li:first-child').outerHeight(true);
      const containerHeight = $dropDownMenu.innerHeight();
      const containerScrollTop = $dropDownMenu.scrollTop();

      $currentActive.removeClass('active');
      if (e.keyCode === 27 && onEsc) {
        onEsc();
      } else if (e.keyCode === 38) {
        // up
        let $nextActive;
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
        let $nextActive;
        if ($currentActive.length === 0) {
          $nextActive = $element.find('.hue-inner-drop-down li:first-child').addClass('active');
        } else if ($currentActive.next().length !== 0) {
          if (activeTop + activeHeight * 3 > containerHeight - containerScrollTop) {
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
          $dropDownMenu.scrollTop(0);
        }
        if (onEnter) {
          onEnter($currentActive.length ? ko.dataFor($currentActive[0]) : undefined);
        }
      } else {
        $dropDownMenu.scrollTop(0);
      }
    };

    const visibleSub = dropDownVisible.subscribe(newValue => {
      if (newValue) {
        $(keyUpTarget).on('keyup.hueDropDown', keyUp);
        $(keyUpTarget).on('keydown.hueDropDown', e => {
          // This prevents the cursor from moving left or right on up and down
          if (e.keyCode === 38 || e.keyCode === 40) {
            e.preventDefault();
          }
        });
      } else {
        $(keyUpTarget).off('keyup.hueDropDown');
        $(keyUpTarget).off('keydown.hueDropDown');
      }
    });

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      visibleSub.dispose();
      $(keyUpTarget).off('keyup.hueDropDown');
    });
  }
};

class HueDropDown {
  constructor(params, element) {
    const self = this;
    self.dropDownVisible = ko.observable(!!params.showOnInit);
    self.menuOnly = !!params.menuOnly;
    self.noLabel = !!params.noLabel;
    self.labelAttribute = params.labelAttribute || 'label';
    self.icon = params.icon;
    self.value = params.value;
    self.entries = params.entries;
    self.searchable = params.searchable || false;
    self.foreachVisible = params.foreachVisible || false;
    self.linkTitle = params.linkTitle || I18n('Selected entry');
    self.fixedPosition = !!params.fixedPosition;
    self.onSelect = params.onSelect || function() {};

    self.inputPlaceHolder = ko.pureComputed(() => {
      return self.value() && typeof self.value() === 'object'
        ? self.value()[self.labelAttribute]
        : self.value();
    });

    const closeOnOutsideClick = function(e) {
      const $input = $(element).find('.hue-drop-down-input');
      if (!$input.is($(e.target))) {
        self.dropDownVisible(false);
      }
    };

    self.onEsc = function() {
      self.dropDownVisible(false);
    };

    self.onEnter = function(value) {
      const previous = self.value();
      self.value(value);
      self.onSelect(value, previous);
      self.dropDownVisible(false);
    };

    self.filter = ko.observable('');

    self.value.subscribe(() => {
      self.dropDownVisible(false);
    });

    self.filterEdited = ko.observable(false);

    self.filter.subscribe(() => {
      self.filterEdited(true);
      $(element)
        .find('.hue-inner-drop-down > .active')
        .removeClass('.active');
    });

    self.dropDownVisible.subscribe(newValue => {
      self.filterEdited(false);
      if (newValue) {
        window.setTimeout(() => {
          self.filter('');
          $(window).on('click', closeOnOutsideClick);
          $(element)
            .find('.hue-drop-down-input')
            .focus();
        }, 0);

        // Right align the dropdown when outside the right edge
        if (!self.fixedPosition) {
          const $element = $(element);
          const $dropDownMenu = $element.find('.dropdown-menu').parent();
          const $offsetParent = $element.offsetParent();

          const rightLimit = $offsetParent.offset().left + $offsetParent.width();

          if ($dropDownMenu.offset().left + 160 > rightLimit) {
            const $caret = $element.find('.fa-caret-down');
            const caretRight = $caret.offset().left + $caret.width();

            const diff = -$dropDownMenu.offset().left - 160 + caretRight;
            $element.find('.hue-drop-down-container').css({ 'margin-left': diff + 'px' });
          }
        }
      } else {
        $(element)
          .find('.hue-inner-drop-down > .active')
          .removeClass('.active');
        $(window).off('click', closeOnOutsideClick);
      }
    });

    self.filteredEntries = ko.pureComputed(() => {
      if (self.filter() === '' || !self.filterEdited()) {
        return ko.unwrap(self.entries);
      } else {
        const lowerFilter = self.filter().toLowerCase();
        return ko.unwrap(self.entries).filter(entry => {
          if (typeof entry === 'object') {
            return entry[self.labelAttribute].toLowerCase().indexOf(lowerFilter) !== -1;
          }
          return entry.toLowerCase().indexOf(lowerFilter) !== -1;
        });
      }
    });
  }
}

componentUtils.registerComponent(
  'hue-drop-down',
  {
    createViewModel: function(params, componentInfo) {
      return new HueDropDown(params, componentInfo.element);
    }
  },
  TEMPLATE
);
