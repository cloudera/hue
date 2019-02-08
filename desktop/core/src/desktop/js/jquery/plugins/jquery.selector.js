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

/*
 * jHue selector plugin
 * it tranforms a select multiple into a searchable/selectable alphabetical list
 */

const pluginName = 'jHueSelector',
  defaults = {
    selectAllLabel: 'Select all',
    showSelectAll: true,
    searchPlaceholder: 'Search',
    noChoicesFound: 'No choices found for this element',
    width: 300,
    height: 200,
    onChange: function() {}
  };

function Plugin(element, options) {
  this.element = element;
  this.options = $.extend({}, defaults, options);
  this._defaults = defaults;
  this._name = pluginName;
  this.init();
}

Plugin.prototype.setOptions = function(options) {
  this.options = $.extend({}, defaults, options);
};

Plugin.prototype.init = function() {
  const _this = this;
  const addressBook = [];
  const selectorContainer = $('<div>');
  if (this.options.width != 300) {
    selectorContainer.width(this.options.width);
  }
  $(_this.element).hide();
  $(_this.element)
    .find('option')
    .each((cnt, opt) => {
      const initial = $(opt)
        .text()
        .substr(0, 1)
        .toLowerCase();
      if (addressBook[initial] == null) {
        addressBook[initial] = [];
      }
      addressBook[initial].push($(opt));
    });
  const sortedKeys = [];
  for (const key in addressBook) {
    if (addressBook.hasOwnProperty(key)) {
      sortedKeys.push(key);
    }
  }
  sortedKeys.sort();

  if (sortedKeys.length == 0) {
    $(_this.element).after(
      $('<div>')
        .addClass('alert')
        .css('margin-top', '-2px')
        .css('float', 'left')
        .html(this.options.noChoicesFound)
    );
  } else {
    selectorContainer.addClass('jHueSelector');
    const body = $('<div>').addClass('jHueSelectorBody');
    body.appendTo(selectorContainer);

    for (let i = 0; i < sortedKeys.length; i++) {
      const key = sortedKeys[i];
      const ul = $('<ul>');
      const dividerLi = $('<li>').addClass('selectorDivider');
      dividerLi.html('<strong>' + key.toUpperCase() + '</strong>');
      dividerLi.appendTo(ul);
      $.each(addressBook[key], (cnt, opt) => {
        const li = $('<li>');
        const lbl = $('<label>').text(opt.text());
        const chk = $('<input>')
          .attr('type', 'checkbox')
          .addClass('selector')
          .change(function() {
            if ($(this).is(':checked')) {
              $(this)
                .data('opt')
                .attr('selected', 'selected');
            } else {
              $(this)
                .data('opt')
                .removeAttr('selected');
            }
            _this.options.onChange();
          })
          .data('opt', opt)
          .prependTo(lbl);
        if (opt.is(':selected')) {
          chk.attr('checked', 'checked');
        }
        lbl.appendTo(li);
        li.appendTo(ul);
      });
      ul.appendTo(body);
    }

    const header = $('<div>').addClass('jHueSelectorHeader');
    header.prependTo(selectorContainer);

    const selectAll = $('<label>').html('&nbsp;');

    if (this.options.showSelectAll) {
      selectAll.text(this.options.selectAllLabel);
      $('<input>')
        .attr('type', 'checkbox')
        .change(function() {
          const isChecked = $(this).is(':checked');
          selectorContainer.find('input.selector:visible').each(function() {
            if (isChecked) {
              $(this).prop('checked', true);
              $(this)
                .data('opt')
                .attr('selected', 'selected');
            } else {
              $(this).prop('checked', false);
              $(this)
                .data('opt')
                .removeAttr('selected');
            }
          });
          if (searchBox.val() != '') {
            $(this).prop('checked', false);
          }
          _this.options.onChange();
        })
        .prependTo(selectAll);
    }

    selectAll.appendTo(header);

    const searchBox = $('<input>')
      .attr('type', 'text')
      .attr('placeholder', this.options.searchPlaceholder)
      .keyup(function() {
        body
          .find('ul')
          .attr('show', true)
          .show();
        const q = $.trim($(this).val());
        if (q != '') {
          body.find('li.selectorDivider').hide();
          body.find('label').each(function() {
            if (
              $(this)
                .text()
                .toLowerCase()
                .indexOf(q.toLowerCase()) > -1
            ) {
              $(this)
                .parent()
                .show();
            } else {
              $(this)
                .parent()
                .hide();
            }
          });
          body.find('ul').attr('show', false);
          body
            .find('ul > *:visible')
            .parent()
            .attr('show', true)
            .find('li.selectorDivider')
            .show();
        } else {
          body.find('li.selectorDivider').show();
          body
            .find('label')
            .parent()
            .show();
        }
        body.find('ul[show=false]').hide();
        body.find('ul[show=true]').show();
      });
    if (this.options.width != 300) {
      searchBox.css('margin-left', this.options.width - 120 + 'px');
    }
    searchBox.prependTo(header);

    body.height(this.options.height - header.outerHeight());

    $(_this.element).after(selectorContainer);
  }
};

$.fn[pluginName] = function(options) {
  return this.each(function() {
    if (!$.data(this, 'plugin_' + pluginName)) {
      $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
    } else {
      $.data(this, 'plugin_' + pluginName).setOptions(options);
    }
  });
};
