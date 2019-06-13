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

import contextCatalog from 'catalog/contextCatalog';
import dataCatalog from 'catalog/dataCatalog';

/*
 * jHue generic autocomplete plugin
 * augment a textbox into an generic hive/solr autocomplete
 */

const pluginName = 'jHueGenericAutocomplete',
  defaults = {
    serverType: 'HIVE',
    home: '/',
    skipColumns: false,
    skipTables: false,
    onEnter: function() {},
    onBlur: function() {},
    onPathChange: function() {},
    pathChangeLevel: '',
    smartTooltip: '',
    smartTooltipThreshold: 10, // needs 10 up/down or click actions and no tab to activate the smart tooltip
    showOnFocus: false,
    startingPath: '',
    rewriteVal: false,
    searchEverywhere: false,
    apiHelperUser: '',
    apiHelperType: '',
    mainScrollable: $(window)
  };

function Plugin(element, options) {
  const self = this;
  self.element = element;
  self.options = $.extend({}, defaults, options);
  self._defaults = defaults;
  self._name = pluginName;

  self.namespaceDeferred = $.Deferred();
  self.computeDeferred = $.Deferred();

  if (self.options.namespace) {
    self.namespaceDeferred.resolve(self.options.namespace);
  } else {
    contextCatalog.getNamespaces({ sourceType: options.apiHelperType }).done(context => {
      if (context.namespaces && context.namespaces.length) {
        self.namespaceDeferred.resolve(context.namespaces[0]);
      } else {
        self.namespaceDeferred.reject();
      }
    });
  }
  self.namespaceDeferred.done(namespace => {
    if (
      !self.options.compute ||
      !namespace.computes.some(compute => {
        if (compute.id === self.options.compute.id) {
          self.computeDeferred.resolve(compute);
          return true;
        }
      })
    ) {
      self.computeDeferred.resolve(namespace.computes[0]);
    }
  });

  this.init();
}

Plugin.prototype.init = function() {
  const self = this;
  const $el = $(self.element);

  // creates autocomplete popover
  if ($('#jHueGenericAutocomplete').length === 0) {
    $('<div>')
      .attr('id', 'jHueGenericAutocomplete')
      .addClass('jHueAutocomplete popover')
      .attr('style', 'position:absolute;display:none;max-width:1000px;z-index:33000')
      .html(
        '<div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><ul class="unstyled"></ul></div></div>'
      )
      .appendTo(window.HUE_CONTAINER);
  }

  $el.wrap('<div class="inline">');
  $el
    .parent()
    .append(
      '<i class="fa fa-spinner fa-spin muted" style="margin-top: 8px; margin-left: -24px; margin-right: 11px; display:none"></i>'
    );

  function setHueBreadcrumbCaretAtEnd(element) {
    const elemLength = element.value.length;
    if (document.selection) {
      element.focus();
      const _oSel = document.selection.createRange();
      _oSel.moveStart('character', -elemLength);
      _oSel.moveStart('character', elemLength);
      _oSel.moveEnd('character', 0);
      _oSel.select();
    } else if (element.selectionStart || element.selectionStart === '0') {
      element.selectionStart = elemLength;
      element.selectionEnd = elemLength;
      element.focus();
    }
  }

  $el.focus(() => {
    $(document.body).on('contextmenu', e => {
      e.preventDefault(); // prevents native menu on FF for Mac from being shown
    });
    setHueBreadcrumbCaretAtEnd(self.element);
    _pauseBlur = false;
  });

  $el.keydown(e => {
    if (e.keyCode === 9) {
      e.preventDefault();
      showAutocomplete(() => {
        let path = $el.val();
        if (path.indexOf('.') > -1) {
          path = path.substr(path.lastIndexOf('.') + 1);
        }
        guessHivePath(path);
      });
    }
  });

  function smartTooltipMaker() {
    if (
      self.options.smartTooltip !== '' &&
      typeof $.totalStorage !== 'undefined' &&
      $.totalStorage('jHueGenericAutocompleteTooltip') !== -1
    ) {
      let cnt = 0;
      if ($.totalStorage('jHueGenericAutocompleteTooltip')) {
        cnt = $.totalStorage('jHueGenericAutocompleteTooltip') + 1;
      }
      $.totalStorage('jHueGenericAutocompleteTooltip', cnt);
      if (cnt >= self.options.smartTooltipThreshold) {
        $el
          .tooltip({
            animation: true,
            title: self.options.smartTooltip,
            trigger: 'manual',
            placement: 'top'
          })
          .tooltip('show');
        window.setTimeout(() => {
          $el.tooltip('hide');
        }, 10000);
        $.totalStorage('jHueGenericAutocompleteTooltip', -1);
      }
    }
  }

  self.options.mainScrollable.on('scroll', () => {
    $('#jHueGenericAutocomplete')
      .css('top', $el.offset().top + $el.outerHeight() - 1)
      .css('left', $el.offset().left)
      .width($el.outerWidth() - 4);
  });

  let validateTimeout = -1;
  const onPathChange = function(path) {
    window.clearTimeout(validateTimeout);
    self.options.onPathChange(path);
  };

  const validateAndSet = function() {
    const path = $el.val().split('.');
    if (path.length > 1) {
      window.clearTimeout(validateTimeout);
      validateTimeout = window.setTimeout(() => {
        $.when(self.namespaceDeferred, self.computeDeferred).done((namespace, compute) => {
          const target = path.pop();
          dataCatalog
            .getChildren({
              sourceType: self.options.apiHelperType,
              namespace: namespace,
              compute: compute,
              path: path
            })
            .done(childEntries => {
              if (
                childEntries.some(childEntry => {
                  return childEntry.name === target;
                })
              ) {
                onPathChange($el.val());
              }
            });
        });
      }, 500);
    }
  };

  let _hiveAutocompleteSelectedIndex = -1;
  let _filterTimeout = -1;
  $el.keyup(function(e) {
    window.clearTimeout(_filterTimeout);
    validateAndSet();
    if ($.inArray(e.keyCode, [17, 38, 40, 13, 32, 191]) === -1) {
      _hiveAutocompleteSelectedIndex = -1;
      _filterTimeout = window.setTimeout(() => {
        let path = $el.val();
        if (path.indexOf('.') > -1) {
          path = path.substr(path.lastIndexOf('.') + 1);
        }
        const $jHueGenericAutocomplete = $('#jHueGenericAutocomplete');
        $jHueGenericAutocomplete.show();
        const $jHueGenericAutocompleteLi = $('#jHueGenericAutocomplete ul li');
        $jHueGenericAutocompleteLi.show();
        if (path !== '') {
          $jHueGenericAutocompleteLi.each(function() {
            if (self.options.searchEverywhere) {
              if (
                $(this)
                  .text()
                  .trim()
                  .toLowerCase()
                  .indexOf(path.toLowerCase()) === -1
              ) {
                $(this).hide();
              }
            } else if (
              $(this)
                .text()
                .trim()
                .indexOf(path) !== 0
            ) {
              $(this).hide();
            }
          });
          if ($('#jHueGenericAutocomplete ul li:visible').length === 0) {
            $jHueGenericAutocomplete.hide();
          }
        }
      }, 500);
    }
    const $jHueGenericAutocompleteLiVisible = $('#jHueGenericAutocomplete ul li:visible');
    if (e.keyCode === 38) {
      if (_hiveAutocompleteSelectedIndex <= 0) {
        _hiveAutocompleteSelectedIndex = $jHueGenericAutocompleteLiVisible.length - 1;
      } else {
        _hiveAutocompleteSelectedIndex--;
      }
    }
    if (e.keyCode === 40) {
      if (_hiveAutocompleteSelectedIndex === $jHueGenericAutocompleteLiVisible.length - 1) {
        _hiveAutocompleteSelectedIndex = 0;
      } else {
        _hiveAutocompleteSelectedIndex++;
      }
    }
    if (e.keyCode === 38 || e.keyCode === 40) {
      smartTooltipMaker();
      $('#jHueGenericAutocomplete ul li').removeClass('active');
      $jHueGenericAutocompleteLiVisible.eq(_hiveAutocompleteSelectedIndex).addClass('active');
      $('#jHueGenericAutocomplete .popover-content').scrollTop(
        $jHueGenericAutocompleteLiVisible.eq(_hiveAutocompleteSelectedIndex).prevAll().length *
          $jHueGenericAutocompleteLiVisible.eq(_hiveAutocompleteSelectedIndex).outerHeight()
      );
    }
    if ((e.keyCode === 32 && e.ctrlKey) || e.keyCode === 191) {
      smartTooltipMaker();
      showAutocomplete();
    }
    if (e.keyCode === 13) {
      _pauseBlur = true;
      if (_hiveAutocompleteSelectedIndex > -1) {
        $jHueGenericAutocompleteLiVisible.eq(_hiveAutocompleteSelectedIndex).click();
      } else {
        self.options.onEnter($(this));
      }
      $('#jHueGenericAutocomplete').hide();
      _hiveAutocompleteSelectedIndex = -1;
    }
  });

  if (self.options.showOnFocus) {
    $el.on('focus', () => {
      showAutocomplete();
    });
  }

  let _pauseBlur = false;

  $el.blur(() => {
    if (!_pauseBlur) {
      $(document.body).off('contextmenu');
      $('#jHueGenericAutocomplete').hide();
      self.options.onBlur();
    }
  });

  let BASE_PATH = '/beeswax/api/autocomplete/';
  if (self.options.serverType === 'IMPALA') {
    BASE_PATH = '/impala/api/autocomplete/';
  }
  if (self.options.serverType === 'SOLR') {
    BASE_PATH = '/indexer/api/autocomplete/';
  }
  let _currentFiles = [];

  self.getDatabases = function(callback) {
    const self = this;
    $.when(self.namespaceDeferred, self.computeDeferred).done((namespace, compute) => {
      dataCatalog
        .getChildren({
          sourceType: self.options.apiHelperType,
          namespace: namespace,
          compute: compute,
          path: []
        })
        .done(dbEntries => {
          callback(
            $.map(dbEntries, entry => {
              return entry.name;
            })
          );
        });
    });
  };

  self.getTables = function(database, callback) {
    const self = this;
    $.when(self.namespaceDeferred, self.computeDeferred).done((namespace, compute) => {
      dataCatalog
        .getEntry({
          sourceType: self.options.apiHelperType,
          namespace: namespace,
          compute: compute,
          path: [database]
        })
        .done(entry => {
          entry.getSourceMeta().done(callback);
        });
    });
  };

  self.getColumns = function(database, table, callback) {
    const self = this;
    $.when(self.namespaceDeferred, self.computeDeferred).done((namespace, compute) => {
      dataCatalog
        .getEntry({
          sourceType: self.options.apiHelperType,
          namespace: namespace,
          compute: compute,
          path: [database, table]
        })
        .done(entry => {
          entry.getSourceMeta().done(callback);
        });
    });
  };

  function autocompleteLogic(autocompleteUrl, data) {
    if (!data.error) {
      _currentFiles = [];

      let _ico = '';
      let _iterable = [];
      let _isSkipColumns = false;
      let _isSkipTables = false;

      if (self.options.serverType === 'SOLR') {
        _iterable = data.collections;
        _ico = 'fa-search';
      } else if (data.databases) {
        // it's a db
        _iterable = data.databases;
        _ico = 'fa-database';
      } else if (data.tables_meta) {
        // it's a table
        if (!self.options.skipTables) {
          _iterable = $.map(data.tables_meta, tablesMeta => {
            return tablesMeta.name;
          });
          _ico = 'fa-table';
        } else {
          _isSkipTables = true;
        }
      } else if (!self.options.skipColumns) {
        _iterable = data.columns;
        _ico = 'fa-columns';
      } else {
        _isSkipColumns = true;
      }

      let firstSolrCollection = false;
      let firstSolrConfig = false;
      if (!_isSkipColumns && !_isSkipTables) {
        $(_iterable).each((cnt, item) => {
          if (self.options.serverType === 'SOLR') {
            if (item.isCollection && !firstSolrCollection) {
              _currentFiles.push(
                '<li class="hiveAutocompleteItem" data-value="collections.*" title="collections.*"><i class="fa fa-search-plus"></i> collections.*</li>'
              );
              _currentFiles.push(
                '<li class="hiveAutocompleteItem" data-value="admin.collections" title="admin.collections"><i class="fa fa-database"></i> admin.collections</li>'
              );
              _currentFiles.push(
                '<li class="hiveAutocompleteItem" data-value="admin.cores" title="admin.collections"><i class="fa fa-database"></i> admin.cores</li>'
              );
              firstSolrCollection = true;
            }
            if (item.isConfig) {
              _ico = 'fa-cog';
              if (!firstSolrConfig) {
                _currentFiles.push(
                  '<li class="hiveAutocompleteItem" data-value="configs.*" title="configs.*"><i class="fa fa-cogs"></i> configs.*</li>'
                );
                firstSolrConfig = true;
              }
            }
            _currentFiles.push(
              '<li class="hiveAutocompleteItem" data-value="' +
                item.name +
                '" title="' +
                item.name +
                '"><i class="fa ' +
                _ico +
                '"></i> ' +
                item.name +
                '</li>'
            );
          } else {
            _currentFiles.push(
              '<li class="hiveAutocompleteItem" data-value="' +
                item +
                '" title="' +
                item +
                '"><i class="fa ' +
                _ico +
                '"></i> ' +
                item +
                '</li>'
            );
          }
        });

        const $jHueGenericAutocomplete = $('#jHueGenericAutocomplete');
        $jHueGenericAutocomplete
          .css('top', $el.offset().top + $el.outerHeight() - 1)
          .css('left', $el.offset().left)
          .width($el.outerWidth() - 4);
        $jHueGenericAutocomplete
          .find('ul')
          .empty()
          .html(_currentFiles.join(''));
        $jHueGenericAutocomplete.find('li').on('click', function(e) {
          smartTooltipMaker();
          e.preventDefault();
          const item = $(this)
            .text()
            .trim();

          if (
            $(this)
              .html()
              .indexOf('search') > -1 ||
            $(this)
              .html()
              .indexOf('cog') > -1 ||
            $(this)
              .html()
              .indexOf('database') > -1
          ) {
            if (
              $(this)
                .html()
                .indexOf('search') > -1 &&
              $(this)
                .html()
                .indexOf('search-plus') === -1
            ) {
              $el.val('collections.' + item);
            } else if (
              $(this)
                .html()
                .indexOf('cog') > -1 &&
              $(this)
                .html()
                .indexOf('cogs') === -1
            ) {
              $el.val('configs.' + item);
            } else {
              $el.val(item);
            }
            if (
              self.options.pathChangeLevel === '' ||
              self.options.pathChangeLevel === 'database'
            ) {
              onPathChange($el.val());
            }
            $('#jHueGenericAutocomplete').hide();
            _hiveAutocompleteSelectedIndex = -1;
            self.options.onEnter($el);
          }

          if (
            $(this)
              .html()
              .indexOf('database') > -1
          ) {
            if (self.options.skipTables) {
              $el.val(item);
              $('#jHueGenericAutocomplete').hide();
            } else {
              $el.val(item + '.');
            }
            if (
              self.options.pathChangeLevel === '' ||
              self.options.pathChangeLevel === 'database'
            ) {
              onPathChange($el.val());
            }
            if (!self.options.skipTables) {
              showAutocomplete();
            }
          }

          if (
            $(this)
              .html()
              .indexOf('table') > -1
          ) {
            if ($el.val().indexOf('.') > -1) {
              if ($el.val().match(/\./gi).length === 1) {
                $el.val($el.val().substring(0, $el.val().lastIndexOf('.') + 1) + item);
              } else {
                $el.val($el.val().substring(0, $el.val().indexOf('.') + 1) + item);
              }
            } else if (self.options.rewriteVal) {
              $el.val(item);
            } else {
              $el.val($el.val() + item);
            }
            if (!self.options.skipColumns) {
              $el.val($el.val() + '.');
            }
            if (self.options.pathChangeLevel === '' || self.options.pathChangeLevel === 'table') {
              onPathChange($el.val());
            }
            if (!self.options.skipColumns) {
              showAutocomplete();
            } else {
              self.options.onEnter($el);
              $('#jHueGenericAutocomplete').hide();
              _hiveAutocompleteSelectedIndex = -1;
            }
          }

          if (
            $(this)
              .html()
              .indexOf('columns') > -1
          ) {
            if ($el.val().match(/\./gi).length > 1) {
              $el.val($el.val().substring(0, $el.val().lastIndexOf('.') + 1) + item);
            } else {
              $el.val($el.val() + '.' + item);
            }
            $('#jHueGenericAutocomplete').hide();
            _hiveAutocompleteSelectedIndex = -1;
            self.options.onEnter($el);
          }
        });
        $jHueGenericAutocomplete.show();
        window.setTimeout(() => {
          setHueBreadcrumbCaretAtEnd(self.element);
        }, 100);
      }
    }
    $el
      .parent()
      .find('.fa-spinner')
      .hide();
  }

  function showAutocomplete() {
    $el
      .parent()
      .find('.fa-spinner')
      .show();
    let path = $el.val();
    if (self.options.startingPath !== '') {
      path = self.options.startingPath + path;
    }
    let autocompleteUrl = BASE_PATH;

    if (path !== '' && path.indexOf('.') === -1) {
      path = '';
    }

    if (path !== '' && path.lastIndexOf('.') !== path.length - 1) {
      path = path.substring(0, (self.options.startingPath + $el.val()).lastIndexOf('.'));
    }

    if (self.options.serverType !== 'SOLR') {
      autocompleteUrl += path.replace(/\./g, '/');
    }

    if (self.options.serverType !== 'SOLR' && self.options.apiHelperUser !== '') {
      const suffix = autocompleteUrl.substr(BASE_PATH.length);
      if (suffix === '') {
        self.getDatabases(data => {
          autocompleteLogic(autocompleteUrl, {
            databases: data
          });
        });
      } else {
        const details = suffix.split('/');
        if (details.length > 1 && details[1] !== '') {
          self.getColumns(details[0], details[1], data => {
            let columns = [];
            if (data.cols || data.extended_columns) {
              columns = $.map(data.cols ? data.cols : data.extended_columns, item => {
                return item.name;
              });
            } else if (data.columns) {
              columns = data.columns;
            }
            autocompleteLogic(autocompleteUrl, {
              columns: columns
            });
          });
        } else {
          self.getTables(details[0], data => {
            autocompleteLogic(autocompleteUrl, data);
          });
        }
      }
    } else {
      $.getJSON(autocompleteUrl, data => {
        autocompleteLogic(autocompleteUrl, data);
      });
    }
  }

  $(document).on('mouseenter', '.hiveAutocompleteItem', () => {
    _pauseBlur = true;
  });

  $(document).on('mouseout', '.hiveAutocompleteItem', () => {
    _pauseBlur = false;
  });

  function guessHivePath(lastChars) {
    const possibleMatches = [];
    for (let i = 0; i < _currentFiles.length; i++) {
      if (
        ($(_currentFiles[i])
          .text()
          .trim()
          .indexOf(lastChars) === 0 ||
          lastChars === '') &&
        $(_currentFiles[i])
          .text()
          .trim() !== '..'
      ) {
        possibleMatches.push(_currentFiles[i]);
      }
    }
    if (possibleMatches.length === 1) {
      $el.val(
        $el.val() +
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
        $el.val($el.val() + '/');
        showAutocomplete();
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
      while (word1.charAt(j) === word2.charAt(j)) {
        ++j;
      }
      const match = word1.substring(0, j);
      $el.val($el.val() + match.substr(lastChars.length));
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
  if (typeof console !== 'undefined') {
    console.warn('$(elem).jHueGenericAutocomplete() is a preferred call method.');
  }
  $(options.element).jHueGenericAutocomplete(options);
};
