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

import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

/*
 * jHue table extender plugin
 *
 */

const pluginName = 'jHueTableExtender',
  defaults = {
    fixedHeader: false,
    fixedFirstColumn: false,
    fixedFirstColumnTopMargin: 0,
    headerSorting: true,
    lockSelectedRow: false,
    firstColumnTooltip: false,
    classToRemove: 'resultTable',
    hintElement: null,
    includeNavigator: true,
    mainScrollable: window,
    stickToTopPosition: -1,
    app: null,
    labels: {
      GO_TO_COLUMN: 'Go to column:',
      PLACEHOLDER: 'column name...',
      LOCK: 'Click to lock row',
      UNLOCK: 'Click to unlock row'
    }
  };

function Plugin(element, options) {
  this.element = element;
  this.setOptions(options);
  this._name = pluginName;
  this.init();
}

Plugin.prototype.setOptions = function(options) {
  this.options = $.extend({}, defaults, options);
  this.options.labels = $.extend(
    {},
    defaults.labels,
    {
      GO_TO_COLUMN: I18n('Go to column:'),
      PLACEHOLDER: I18n('column name...'),
      LOCK: I18n('Lock this row'),
      UNLOCK: I18n('Unlock this row'),
      ROW_DETAILS: I18n('Show row details')
    },
    options ? options.labels : {}
  );
  this._defaults = defaults;

  if (this.options.fixedHeader) {
    drawHeader(this);
  }
  if (this.options.fixedFirstColumn) {
    drawFirstColumn(this);
  }
};

Plugin.prototype.resetSource = function() {
  const _this = this;
  if (_this.options.includeNavigator) {
    const source = [];
    $(this.element)
      .find('th')
      .each(function() {
        source.push($(this).text());
      });

    $('#jHueTableExtenderNavigator')
      .find('input')
      .data('typeahead').source = source;
  }
};

Plugin.prototype.drawHeader = function(skipCreation) {
  drawHeader(this, skipCreation);
};

Plugin.prototype.drawFirstColumn = function() {
  drawFirstColumn(this);
};

Plugin.prototype.drawLockedRows = function(force) {
  const _this = this;
  const $pluginElement = $(_this.element);
  if ($pluginElement.data('lockedRows')) {
    const locks = $pluginElement.data('lockedRows');
    Object.keys(locks).forEach(idx => {
      drawLockedRow(_this, idx.substr(1), force);
    });
  }
};

Plugin.prototype.init = function() {
  $.expr[':'].econtains = function(obj, index, meta, stack) {
    return (
      (obj.textContent || obj.innerText || $(obj).text() || '').toLowerCase() ==
      meta[3].toLowerCase()
    );
  };

  const _this = this;
  if (_this.options.includeNavigator) {
    const jHueTableExtenderNavigator = $('<div>').attr('id', 'jHueTableExtenderNavigator');
    $('<a>')
      .attr('href', '#')
      .addClass('pull-right')
      .html('&times;')
      .click(function(e) {
        e.preventDefault();
        $(this)
          .parent()
          .hide();
      })
      .appendTo(jHueTableExtenderNavigator);
    $('<label>')
      .html(
        _this.options.labels.GO_TO_COLUMN +
          ' <input type="text" placeholder="' +
          _this.options.labels.PLACEHOLDER +
          '" />'
      )
      .appendTo(jHueTableExtenderNavigator);

    jHueTableExtenderNavigator.appendTo(HUE_CONTAINER);

    $(_this.element)
      .find('tbody')
      .click(event => {
        if ($.trim(getSelection()) == '') {
          window.setTimeout(() => {
            $('.rowSelected').removeClass('rowSelected');
            $('.columnSelected').removeClass('columnSelected');
            $('.cellSelected').removeClass('cellSelected');
            $(event.target.parentNode).addClass('rowSelected');
            $(event.target.parentNode)
              .find('td')
              .addClass('rowSelected');
            jHueTableExtenderNavigator
              .css(
                'left',
                (event.pageX + jHueTableExtenderNavigator.width() > $(window).width() - 10
                  ? event.pageX - jHueTableExtenderNavigator.width() - 10
                  : event.pageX) + 'px'
              )
              .css('top', event.pageY + 10 + 'px')
              .show();
            jHueTableExtenderNavigator.find('input').focus();
          }, 100);
        }
      });

    const source = [];
    $(_this.element)
      .find('th')
      .each(function() {
        source.push($(this).text());
      });

    jHueTableExtenderNavigator.find('input').typeahead({
      source: source,
      updater: function(item) {
        jHueTableExtenderNavigator.hide();
        $(_this.element)
          .find(
            'tr td:nth-child(' +
              ($(_this.element)
                .find('th:econtains(' + item + ')')
                .index() +
                1) +
              ')'
          )
          .addClass('columnSelected');
        if (_this.options.firstColumnTooltip) {
          $(_this.element)
            .find(
              'tr td:nth-child(' +
                ($(_this.element)
                  .find('th:econtains(' + item + ')')
                  .index() +
                  1) +
                ')'
            )
            .each(function() {
              $(this)
                .attr('rel', 'tooltip')
                .attr(
                  'title',
                  '#' +
                    $(this)
                      .parent()
                      .find('td:first-child')
                      .text()
                )
                .tooltip({
                  placement: 'left'
                });
            });
        }
        $(_this.element)
          .parent()
          .animate(
            {
              scrollLeft:
                $(_this.element)
                  .find('th:econtains(' + item + ')')
                  .position().left +
                $(_this.element)
                  .parent()
                  .scrollLeft() -
                $(_this.element)
                  .parent()
                  .offset().left -
                30
            },
            300
          );
        $(_this.element)
          .find(
            'tr.rowSelected td:nth-child(' +
              ($(_this.element)
                .find('th:econtains(' + item + ')')
                .index() +
                1) +
              ')'
          )
          .addClass('cellSelected');
      }
    });

    $(_this.element)
      .parent()
      .bind('mouseleave', () => {
        jHueTableExtenderNavigator.hide();
      });

    jHueTableExtenderNavigator.bind('mouseenter', e => {
      jHueTableExtenderNavigator.show();
    });
  }

  if (_this.options.hintElement != null) {
    let showAlertTimeout = -1;
    $(_this.element)
      .find('tbody')
      .mousemove(() => {
        window.clearTimeout(showAlertTimeout);
        if (
          $(_this.options.hintElement).data('show') == null ||
          $(_this.options.hintElement).data('show')
        ) {
          showAlertTimeout = window.setTimeout(() => {
            $(_this.options.hintElement).fadeIn();
          }, 1300);
        }
      });

    $(_this.options.hintElement)
      .find('.close')
      .click(() => {
        $(_this.options.hintElement).data('show', false);
      });
  }

  if (_this.options.fixedHeader) {
    drawHeader(_this);
  }
  if (_this.options.fixedFirstColumn) {
    drawFirstColumn(_this);
  }

  $(document).on('click dblclick', '.dataTables_wrapper > table tbody tr', function() {
    $(
      '.dataTables_wrapper > .jHueTableExtenderClonedContainerColumn table tbody tr.selected'
    ).removeClass('selected');
    if ($(this).hasClass('selected')) {
      $(this).removeClass('selected');
    } else {
      $('.dataTables_wrapper > table tbody tr.selected').removeClass('selected');
      $(this).addClass('selected');
      $(
        '.dataTables_wrapper > .jHueTableExtenderClonedContainerColumn table tbody tr:eq(' +
          $(this).index() +
          ')'
      ).addClass('selected');
    }
  });
  $(document).on('dblclick', '.dataTables_wrapper > table tbody tr', function() {
    if (huePubSub) {
      huePubSub.publish('table.row.show.details', {
        idx: $(this).index(),
        table: $(this).parents('table')
      });
    }
  });
};

function drawLockedRow(plugin, rowNo, force) {
  const $pluginElement = $(plugin.element);
  const lockedRows = $pluginElement.data('lockedRows') || {};
  const $header = $('#' + $pluginElement.attr('id') + 'jHueTableExtenderClonedContainer');
  const $headerCounter = $(
    '#' + $pluginElement.attr('id') + 'jHueTableExtenderClonedContainerCell'
  );
  $header.addClass('locked');
  $headerCounter.addClass('locked');

  function unlock($el) {
    $header
      .find('tr td:first-child')
      .filter(function() {
        return $(this).text() === rowNo + '';
      })
      .closest('tr')
      .remove();
    delete lockedRows['r' + $el.text()];
    $el.parent().remove();
    if ($header.find('tbody tr').length == 0) {
      $header.removeClass('locked');
      $headerCounter.removeClass('locked');
    }
  }

  if (Object.keys(lockedRows).indexOf('r' + rowNo) === -1 || force) {
    if (force) {
      unlock(lockedRows['r' + rowNo].cell.find('td'));
    }
    const $clone = $('<tr>');
    let tHtml = '';
    const aoColumns = $pluginElement.data('aoColumns');
    $pluginElement.data('data')[rowNo - 1].forEach((col, idx) => {
      tHtml +=
        '<td ' +
        (aoColumns && !aoColumns[idx].bVisible ? 'style="display: none"' : '') +
        '>' +
        col +
        '</td>';
    });
    $clone.html(tHtml);
    $clone.addClass('locked');
    $clone.appendTo($header.find('tbody'));
    $pluginElement.data('lockedRows', lockedRows);
    const $newTr = $('<tr>');
    $newTr
      .addClass('locked')
      .html(
        '<td class="pointer unlockable" title="' +
          plugin.options.labels.UNLOCK +
          '"><i class="fa fa-unlock muted"></i>' +
          rowNo +
          '</td>'
      )
      .appendTo($headerCounter.find('tbody'));
    $newTr.find('td').on('click', function() {
      unlock($(this));
    });
    lockedRows['r' + rowNo] = {
      row: $clone,
      cell: $newTr
    };
  } else {
    lockedRows['r' + rowNo].row.appendTo($header.find('tbody'));
    lockedRows['r' + rowNo].cell.appendTo($headerCounter.find('tbody'));
    lockedRows['r' + rowNo].cell.find('td').on('click', function() {
      unlock($(this));
    });
  }
}

function drawFirstColumn(plugin) {
  const $pluginElement = $(plugin.element);
  if (!$pluginElement.attr('id') && plugin.options.parentId) {
    $pluginElement.attr('id', 'eT' + plugin.options.parentId);
  }

  const mainScrollable = plugin.options.mainScrollable;
  const originalTh = $(plugin.element).find('thead>tr th:eq(0)');
  let topPosition;
  if (plugin.options.clonedContainerPosition == 'absolute') {
    topPosition = $pluginElement.parent().position().top - $(mainScrollable).scrollTop();
  } else {
    topPosition = $pluginElement.parent().offset().top - $(mainScrollable).scrollTop();
  }

  $('#' + $pluginElement.attr('id') + 'jHueTableExtenderClonedContainerCell').remove();
  const clonedCell = $('<table>').attr('class', $(plugin.element).attr('class'));
  clonedCell.removeClass(plugin.options.classToRemove);
  clonedCell.css('margin-bottom', '0').css('table-layout', 'fixed');
  const clonedCellTHead = $('<thead>');
  clonedCellTHead.appendTo(clonedCell);
  const clonedCellTH = originalTh.clone();
  clonedCellTH.appendTo(clonedCellTHead);
  clonedCellTH.width(originalTh.width()).css({
    'background-color': '#FFFFFF',
    'border-color': 'transparent'
  });
  clonedCellTH.click(() => {
    originalTh.click();
  });
  $('<tbody>').appendTo(clonedCell);

  const clonedCellContainer = $('<div>')
    .css('background-color', '#FFFFFF')
    .width(originalTh.outerWidth());

  clonedCell.appendTo(clonedCellContainer);

  const clonedCellVisibleContainer = $('<div>')
    .attr('id', $(plugin.element).attr('id') + 'jHueTableExtenderClonedContainerCell')
    .addClass('jHueTableExtenderClonedContainerCell')
    .width(originalTh.outerWidth())
    .css('overflow', 'hidden')
    .css('top', topPosition + 'px');
  clonedCellVisibleContainer.css('position', plugin.options.clonedContainerPosition || 'fixed');

  clonedCellContainer.appendTo(clonedCellVisibleContainer);

  $('#' + $pluginElement.attr('id') + 'jHueTableExtenderClonedContainerColumn').remove();
  const clonedTable = $('<table>')
    .attr('class', $(plugin.element).attr('class'))
    .html('<thead></thead><tbody></tbody>');
  clonedTable.removeClass(plugin.options.classToRemove);
  clonedTable.css('margin-bottom', '0').css('table-layout', 'fixed');
  $(plugin.element)
    .find('thead>tr th:eq(0)')
    .clone()
    .appendTo(clonedTable.find('thead'));
  const clonedTBody = clonedTable.find('tbody');
  const clones = $(plugin.element)
    .find('tbody>tr td:nth-child(1)')
    .clone();
  let h = '';
  clones.each(function() {
    h += '<tr><td>' + $(this).html() + '</td></tr>';
  });
  clonedTBody.html(h);
  if (plugin.options.lockSelectedRow) {
    clonedTBody.find('td').each(function() {
      const cell = $(this);
      cell
        .attr('title', plugin.options.labels.LOCK)
        .addClass('lockable pointer')
        .on('click', function() {
          drawLockedRow(plugin, $(this).text() * 1);
        });
      $('<i>')
        .addClass('fa fa-lock muted')
        .prependTo(cell);
    });
  }
  clonedTable
    .find('thead>tr th:eq(0)')
    .width(originalTh.width())
    .css('background-color', '#FFFFFF');

  const clonedTableContainer = $('<div>')
    .css('background-color', '#FFFFFF')
    .width(originalTh.outerWidth())
    .height($pluginElement.parent().get(0).scrollHeight);
  clonedTable.appendTo(clonedTableContainer);

  const clonedTableVisibleContainer = $('<div>')
    .attr('id', $pluginElement.attr('id') + 'jHueTableExtenderClonedContainerColumn')
    .addClass('jHueTableExtenderClonedContainerColumn')
    .width(originalTh.outerWidth())
    .height($pluginElement.parent().height())
    .css('overflow', 'hidden')
    .css('top', topPosition + 'px');
  clonedTableVisibleContainer.css('position', plugin.options.clonedContainerPosition || 'fixed');

  clonedTableContainer.appendTo(clonedTableVisibleContainer);
  clonedTableVisibleContainer.appendTo($pluginElement.parent());

  clonedCellVisibleContainer.appendTo($pluginElement.parent());

  window.clearInterval($pluginElement.data('firstcol_interval'));
  const firstColInt = window.setInterval(
    () => {
      if ($pluginElement.parent().height() != $pluginElement.parent().data('h')) {
        clonedTableContainer.height($pluginElement.parent().get(0).scrollHeight);
        clonedTableVisibleContainer.height($pluginElement.parent().height());
        $pluginElement.parent().data('h', clonedTableVisibleContainer.height());
      }
    },
    250,
    plugin.options.app
  );
  $pluginElement.data('firstcol_interval', firstColInt);

  $pluginElement.parent().resize(() => {
    clonedTableContainer.height($pluginElement.parent().get(0).scrollHeight);
    clonedTableVisibleContainer.height($pluginElement.parent().height());
  });

  $pluginElement.parent().scroll(() => {
    clonedTableContainer.css(
      'marginTop',
      -$pluginElement.parent().scrollTop() + plugin.options.fixedFirstColumnTopMargin + 'px'
    );
  });

  clonedTableContainer.css(
    'marginTop',
    -$pluginElement.parent().scrollTop() + plugin.options.fixedFirstColumnTopMargin + 'px'
  );

  function positionClones() {
    let pos = plugin.options.stickToTopPosition;
    if (typeof pos === 'function') {
      pos = pos();
    }
    if (pos > -1) {
      if ($pluginElement.offset().top < pos) {
        clonedCellVisibleContainer.css('top', pos + 'px');
      } else {
        clonedCellVisibleContainer.css('top', $pluginElement.offset().top + 'px');
      }
      clonedTableVisibleContainer.css('top', $pluginElement.offset().top + 'px');
    } else if (plugin.options.clonedContainerPosition == 'absolute') {
      clonedTableVisibleContainer.css('top', $pluginElement.parent().position().top + 'px');
      clonedCellVisibleContainer.css('top', $pluginElement.parent().position().top + 'px');
    } else {
      clonedTableVisibleContainer.css('top', $pluginElement.parent().offset().top + 'px');
      clonedCellVisibleContainer.css('top', $pluginElement.parent().offset().top + 'px');
    }
  }

  positionClones();

  $(mainScrollable).on('scroll', positionClones);
}

function drawHeader(plugin, skipCreation) {
  const $pluginElement = $(plugin.element);
  if (!$pluginElement.attr('id') && plugin.options.parentId) {
    $pluginElement.attr('id', 'eT' + plugin.options.parentId);
  }

  if (typeof skipCreation === 'undefined') {
    const mainScrollable = plugin.options.mainScrollable;

    $('#' + $pluginElement.attr('id') + 'jHueTableExtenderClonedContainer').remove();
    const clonedTable = $('<table>').attr('class', $(plugin.element).attr('class'));
    clonedTable.removeClass(plugin.options.classToRemove);
    clonedTable.css('margin-bottom', '0').css('table-layout', 'fixed');
    const clonedTableTHead = $('<thead>');
    clonedTableTHead.appendTo(clonedTable);
    const clonedTableTR = $pluginElement.find('thead>tr').clone();
    clonedTableTR.appendTo(clonedTableTHead);
    $('<tbody>').appendTo(clonedTable);

    clonedTable.find('thead>tr th').wrapInner('<span></span>');

    $pluginElement.find('thead>tr th').each(function(i) {
      const originalTh = $(this);
      originalTh.removeAttr('data-bind');
      clonedTable
        .find('thead>tr th:eq(' + i + ')')
        .width(originalTh.width())
        .css('background-color', '#FFFFFF')
        .click(function() {
          originalTh.click();
          if (plugin.options.headerSorting) {
            clonedTable.find('thead>tr th').attr('class', 'sorting');
          }
          $(this).attr('class', originalTh.attr('class'));
        });
    });

    const clonedTableContainer = $('<div>').width($pluginElement.outerWidth());
    clonedTable.appendTo(clonedTableContainer);

    let topPosition;
    if (plugin.options.clonedContainerPosition == 'absolute') {
      topPosition = $pluginElement.parent().position().top - $(mainScrollable).scrollTop();
    } else {
      topPosition = $pluginElement.parent().offset().top - $(mainScrollable).scrollTop();
    }
    const clonedTableVisibleContainer = $('<div>')
      .attr('id', $pluginElement.attr('id') + 'jHueTableExtenderClonedContainer')
      .addClass('jHueTableExtenderClonedContainer')
      .width($pluginElement.parent().width())
      .css('overflow-x', 'hidden')
      .css('top', topPosition + 'px');
    clonedTableVisibleContainer.css('position', plugin.options.clonedContainerPosition || 'fixed');

    clonedTableContainer.appendTo(clonedTableVisibleContainer);
    clonedTableVisibleContainer.prependTo($pluginElement.parent());

    const throttledHeaderPadding = () => {
      const firstCellWidth = clonedTable.find('thead>tr th:eq(0)').outerWidth();
      clonedTable.find('thead>tr th').each(function() {
        const leftPosition = $(this).position().left - firstCellWidth;
        if (leftPosition + $(this).outerWidth() > 0 && leftPosition < 0) {
          if (
            $(this)
              .find('span')
              .width() +
              -leftPosition <
            $(this).outerWidth() - 20
          ) {
            // 20 is the sorting css width
            $(this)
              .find('span')
              .css('paddingLeft', -leftPosition);
          }
        } else {
          $(this)
            .find('span')
            .css('paddingLeft', 0);
        }
      });
    };

    let scrollTimeout = -1;
    $pluginElement.parent().scroll(function() {
      const scrollLeft = $(this).scrollLeft();
      clonedTableVisibleContainer.scrollLeft(scrollLeft);
      window.clearTimeout(scrollTimeout);
      scrollTimeout = window.setTimeout(throttledHeaderPadding, 200);
    });

    $pluginElement.bind('headerpadding', () => {
      scrollTimeout = window.setTimeout(throttledHeaderPadding, 200);
    });

    clonedTableVisibleContainer.scrollLeft($pluginElement.parent().scrollLeft());

    $pluginElement.parent().data('w', clonedTableVisibleContainer.width());

    window.clearInterval($pluginElement.data('header_interval'));
    const headerInt = window.setInterval(
      () => {
        if ($pluginElement.parent().width() != $pluginElement.parent().data('w')) {
          clonedTableVisibleContainer.width($pluginElement.parent().width());
          $pluginElement.parent().data('w', clonedTableVisibleContainer.width());
          $pluginElement.find('thead>tr th').each(function(i) {
            clonedTable
              .find('thead>tr th:eq(' + i + ')')
              .width($(this).width())
              .css('background-color', '#FFFFFF');
          });
        }
      },
      250,
      plugin.options.app
    );
    $pluginElement.data('header_interval', headerInt);

    $pluginElement.parent().resize(function() {
      clonedTableVisibleContainer.width($(this).width());
    });

    const positionClones = () => {
      let pos = plugin.options.stickToTopPosition;
      if (typeof pos === 'function') {
        pos = pos();
      }
      if (pos > -1) {
        if ($pluginElement.offset().top < pos) {
          clonedTableVisibleContainer.css('top', pos + 'px');
        } else {
          clonedTableVisibleContainer.css('top', $pluginElement.offset().top + 'px');
        }
      } else if (plugin.options.clonedContainerPosition == 'absolute') {
        clonedTableVisibleContainer.css('top', $pluginElement.parent().position().top + 'px');
      } else {
        clonedTableVisibleContainer.css('top', $pluginElement.parent().offset().top + 'px');
      }
    };

    positionClones();

    $(mainScrollable).on('scroll', positionClones);
  } else {
    $('#' + $pluginElement.attr('id') + 'jHueTableExtenderClonedContainer')
      .children('div')
      .width($pluginElement.outerWidth());
    $pluginElement.find('thead>tr th').each(function(i) {
      const originalTh = $(this);
      $('#' + $pluginElement.attr('id') + 'jHueTableExtenderClonedContainer')
        .find('thead>tr th:eq(' + i + ')')
        .width(originalTh.width())
        .attr('class', originalTh.attr('class'));
    });
  }
}

function getSelection() {
  let t = '';
  if (window.getSelection) {
    t = window.getSelection();
  } else if (document.getSelection) {
    t = document.getSelection();
  } else if (document.selection) {
    t = document.selection.createRange().text;
  }
  return t.toString();
}

$.fn[pluginName] = function(options) {
  return this.each(function() {
    if (!$.data(this, 'plugin_' + pluginName)) {
      $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
    } else {
      $.data(this, 'plugin_' + pluginName).resetSource();
      $.data(this, 'plugin_' + pluginName).setOptions(options);
    }
  });
};
