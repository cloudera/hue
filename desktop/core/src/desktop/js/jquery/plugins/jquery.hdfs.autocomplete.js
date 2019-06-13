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

import hueUtils from '../../utils/hueUtils';

/*
 * jHue HDFS autocomplete plugin
 * augment a textbox into an HDFS autocomplete
 */

const pluginName = 'jHueHdfsAutocomplete',
  defaults = {
    home: '/',
    onEnter: function() {},
    onBlur: function() {},
    onPathChange: function() {},
    smartTooltip: '',
    smartTooltipThreshold: 10, // needs 10 up/down or click actions and no tab to activate the smart tooltip
    showOnFocus: false,
    skipKeydownEvents: false,
    skipEnter: false,
    skipScrollEvent: false,
    zIndex: 33000,
    root: '/',
    isS3: false
  };

function Plugin(element, options) {
  this.element = element;
  this.options = $.extend({}, defaults, options);
  this._defaults = defaults;
  this._name = pluginName;
  this.init();
}

Plugin.prototype.init = function() {
  const _this = this;
  const _el = $(_this.element);
  _el.addClass('jHueAutocompleteElement');
  _el.attr('autocomplete', 'off'); // prevents default browser behavior

  // creates autocomplete popover
  if ($('#jHueHdfsAutocomplete').length == 0) {
    $('<div>')
      .attr('id', 'jHueHdfsAutocomplete')
      .addClass('jHueAutocomplete popover')
      .attr(
        'style',
        'position:absolute;display:none;max-width:1000px;z-index:' + _this.options.zIndex
      )
      .html(
        '<div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><p><ul class="unstyled"></ul></p></div></div>'
      )
      .appendTo($(HUE_CONTAINER));
  }

  function setHueBreadcrumbCaretAtEnd(element) {
    const elemLength = element.value.length;
    if (document.selection) {
      element.focus();
      const _oSel = document.selection.createRange();
      _oSel.moveStart('character', -elemLength);
      _oSel.moveStart('character', elemLength);
      _oSel.moveEnd('character', 0);
      _oSel.select();
    } else if (element.selectionStart || element.selectionStart == '0') {
      element.selectionStart = elemLength;
      element.selectionEnd = elemLength;
      element.focus();
    }
  }

  _el.focus(() => {
    $(document.body).on('contextmenu', e => {
      e.preventDefault(); // prevents native menu on FF for Mac from being shown
    });
    setHueBreadcrumbCaretAtEnd(_this.element);
  });

  _el.keydown(e => {
    if (e.keyCode == 9) {
      e.preventDefault();
      showHdfsAutocomplete(() => {
        let path = _el.val();
        if (path.indexOf('/') > -1) {
          path = path.substr(path.lastIndexOf('/') + 1);
        }
        guessHdfsPath(path);
      });
    }
  });

  function smartTooltipMaker() {
    if (
      _this.options.smartTooltip != '' &&
      typeof $.totalStorage != 'undefined' &&
      $.totalStorage('jHueHdfsAutocompleteTooltip') != -1
    ) {
      let cnt = 0;
      if ($.totalStorage('jHueHdfsAutocompleteTooltip') != null) {
        cnt = $.totalStorage('jHueHdfsAutocompleteTooltip') + 1;
      }
      $.totalStorage('jHueHdfsAutocompleteTooltip', cnt);
      if (cnt >= _this.options.smartTooltipThreshold) {
        _el
          .tooltip({
            animation: true,
            title: _this.options.smartTooltip,
            trigger: 'manual',
            placement: 'top'
          })
          .tooltip('show');
        window.setTimeout(() => {
          _el.tooltip('hide');
        }, 10000);
        $.totalStorage('jHueHdfsAutocompleteTooltip', -1);
      }
    }
  }

  if (!_this.options.skipScrollEvent) {
    $(window).on('scroll', () => {
      $('#jHueHdfsAutocomplete')
        .css('top', _el.offset().top + _el.outerHeight() - 1)
        .css('left', _el.offset().left)
        .width(_el.outerWidth() - 4);
    });
  }

  _el.on('keydown', e => {
    if (!_this.options.skipKeydownEvents && e.keyCode == 191) {
      e.preventDefault();
    }
    if (e.keyCode == 32 && e.ctrlKey) {
      e.preventDefault();
    }
    if (_this.options.skipEnter && e.keyCode === 13) {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
    }
  });

  let _hdfsAutocompleteSelectedIndex = -1;
  let _filterTimeout = -1;
  _el.keyup(function(e) {
    window.clearTimeout(_filterTimeout);
    if ($.inArray(e.keyCode, [38, 40, 13, 32, 191]) == -1) {
      _hdfsAutocompleteSelectedIndex = -1;
      _filterTimeout = window.setTimeout(() => {
        let path = _el.val();
        if (path.indexOf('/') > -1) {
          path = path.substr(path.lastIndexOf('/') + 1);
        }
        $('#jHueHdfsAutocomplete ul li').show();
        $('#jHueHdfsAutocomplete ul li').each(function() {
          if (
            $(this)
              .text()
              .trim()
              .indexOf(path) != 0
          ) {
            $(this).hide();
          }
        });
      }, 500);
    }
    if (e.keyCode == 38) {
      if (_hdfsAutocompleteSelectedIndex <= 0) {
        _hdfsAutocompleteSelectedIndex = $('#jHueHdfsAutocomplete ul li:visible').length - 1;
      } else {
        _hdfsAutocompleteSelectedIndex--;
      }
    }
    if (e.keyCode == 40) {
      if (_hdfsAutocompleteSelectedIndex == $('#jHueHdfsAutocomplete ul li:visible').length - 1) {
        _hdfsAutocompleteSelectedIndex = 0;
      } else {
        _hdfsAutocompleteSelectedIndex++;
      }
    }
    if (e.keyCode == 38 || e.keyCode == 40) {
      smartTooltipMaker();
      $('#jHueHdfsAutocomplete ul li').removeClass('active');
      $('#jHueHdfsAutocomplete ul li:visible')
        .eq(_hdfsAutocompleteSelectedIndex)
        .addClass('active');
      $('#jHueHdfsAutocomplete .popover-content').scrollTop(
        $('#jHueHdfsAutocomplete ul li:visible')
          .eq(_hdfsAutocompleteSelectedIndex)
          .prevAll().length *
          $('#jHueHdfsAutocomplete ul li:visible')
            .eq(_hdfsAutocompleteSelectedIndex)
            .outerHeight()
      );
    }
    if ((e.keyCode == 32 && e.ctrlKey) || e.keyCode == 191) {
      smartTooltipMaker();
      showHdfsAutocomplete();
    }
    if (e.keyCode == 13) {
      if (_hdfsAutocompleteSelectedIndex > -1) {
        $('#jHueHdfsAutocomplete ul li:visible')
          .eq(_hdfsAutocompleteSelectedIndex)
          .click();
      } else {
        _this.options.onEnter($(this));
      }
      $('#jHueHdfsAutocomplete').hide();
      _hdfsAutocompleteSelectedIndex = -1;
    }
  });

  if (_this.options.showOnFocus) {
    _el.on('focus', () => {
      showHdfsAutocomplete();
    });
  }

  let _pauseBlur = false;

  _el.blur(() => {
    if (!_pauseBlur) {
      $(document.body).off('contextmenu');
      $('#jHueHdfsAutocomplete').hide();
      _this.options.onBlur();
    }
  });

  const BASE_PATH = '/filebrowser/view=';
  let _currentFiles = [];

  function showHdfsAutocomplete(callback) {
    let base = '';
    let path = _el.val();
    const hasScheme = path.indexOf(':/') >= 0;
    const isRelative = !hasScheme && path.charAt(0) !== '/';
    if (isRelative && _this.options.root) {
      base += _this.options.root;
    }
    const autocompleteUrl = BASE_PATH + base + path;
    $.getJSON(autocompleteUrl + '?pagesize=1000&format=json', data => {
      _currentFiles = [];
      if (data.error == null) {
        $(data.files).each((cnt, item) => {
          if (item.name != '.') {
            let ico = 'fa-file-o';
            if (item.type == 'dir') {
              ico = 'fa-folder';
            }
            _currentFiles.push(
              '<li class="hdfsAutocompleteItem" data-value="' +
                hueUtils.escapeOutput(item.name) +
                '"><i class="fa ' +
                ico +
                '"></i> ' +
                hueUtils.escapeOutput(item.name) +
                '</li>'
            );
          }
        });
        window.setTimeout(() => {
          $('#jHueHdfsAutocomplete')
            .css('top', _el.offset().top + _el.outerHeight() - 1)
            .css('left', _el.offset().left)
            .width(_el.outerWidth() - 4);
          $('#jHueHdfsAutocomplete')
            .find('ul')
            .empty()
            .html(_currentFiles.join(''));
          $('#jHueHdfsAutocomplete')
            .find('li')
            .on('click', function(e) {
              smartTooltipMaker();
              e.preventDefault();
              const item = $(this)
                .text()
                .trim();
              if (item == '..') {
                // one folder up
                path = path.substring(0, path.lastIndexOf('/'));
              } else {
                path = path + (path.charAt(path.length - 1) == '/' ? '' : '/') + item;
              }
              _el.val(base + path);
              if (
                $(this)
                  .html()
                  .indexOf('folder') > -1
              ) {
                _el.val(_el.val() + '/');
                _this.options.onPathChange(_el.val());
                showHdfsAutocomplete();
              } else {
                _this.options.onEnter(_el);
              }
            });
          $('#jHueHdfsAutocomplete').show();
          setHueBreadcrumbCaretAtEnd(_this.element);
          if ('undefined' != typeof callback) {
            callback();
          }
        }, 100); // timeout for IE8
      }
    });
  }

  $(document).on('mouseenter', '.hdfsAutocompleteItem', () => {
    _pauseBlur = true;
  });

  $(document).on('mouseout', '.hdfsAutocompleteItem', () => {
    _pauseBlur = false;
  });

  function guessHdfsPath(lastChars) {
    const possibleMatches = [];
    for (let i = 0; i < _currentFiles.length; i++) {
      if (
        ($(_currentFiles[i])
          .text()
          .trim()
          .indexOf(lastChars) == 0 ||
          lastChars == '') &&
        $(_currentFiles[i])
          .text()
          .trim() != '..'
      ) {
        possibleMatches.push(_currentFiles[i]);
      }
    }
    if (possibleMatches.length == 1) {
      _el.val(
        _el.val() +
          $(possibleMatches[0])
            .text()
            .trim()
            .substr(lastChars.length)
      );
      if (
        $(possibleMatches[0])
          .html()
          .indexOf('folder') > -1
      ) {
        _el.val(_el.val() + '/');
        showHdfsAutocomplete();
      }
    } else if (possibleMatches.length > 1) {
      // finds the longest common prefix
      const possibleMatchesPlain = [];
      for (let z = 0; z < possibleMatches.length; z++) {
        possibleMatchesPlain.push(
          $(possibleMatches[z])
            .text()
            .trim()
        );
      }
      const arr = possibleMatchesPlain.slice(0).sort();
      const word1 = arr[0];
      const word2 = arr[arr.length - 1];

      let j = 0;
      while (word1.charAt(j) == word2.charAt(j)) {
        ++j;
      }
      const match = word1.substring(0, j);
      _el.val(_el.val() + match.substr(lastChars.length));
    }
  }
};

Plugin.prototype.setOptions = function(options) {
  this.options = $.extend({}, defaults, options);
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

$[pluginName] = function(options) {
  if (typeof console != 'undefined') {
    console.warn('$(elem).jHueHdfsAutocomplete() is a preferred call method.');
  }
  $(options.element).jHueHdfsAutocomplete(options);
};
