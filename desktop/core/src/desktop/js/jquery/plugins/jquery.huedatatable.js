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
import hueUtils from 'utils/hueUtils';

/*
 * Extension to datatable to programmatically switch off datatable in case of huge tables
 *
 */

$.fn.hueDataTable = function(oInit) {
  const self = this;
  self.$table = null;

  self.fnSetColumnVis = function(index, visible) {
    const aoColumns = self.$table.data('aoColumns');
    const change = aoColumns[index].bVisible !== visible;
    aoColumns[index].bVisible = visible;
    if (!change) {
      return;
    }
    if (!visible) {
      self.$table
        .find('tr')
        .find('td:eq(' + index + '),th:eq(' + index + ')')
        .hide();
    } else {
      self.$table
        .find('tr')
        .find('td:eq(' + index + '),th:eq(' + index + ')')
        .show();
    }
    if (self.$table.data('plugin_jHueTableExtender')) {
      self.$table.data('plugin_jHueTableExtender').drawLockedRows(true);
    } else if (self.$table.data('plugin_jHueTableExtender2')) {
      self.$table.data('plugin_jHueTableExtender2').redraw();
    }
  };

  self.fnToggleAllCols = function(visible) {
    const aoColumns = self.$table.data('aoColumns');
    aoColumns.forEach((col, idx) => {
      if (idx > 0) {
        col.bVisible = visible;
      }
    });
    if (!visible) {
      self.$table.find('th, td').hide();
      self.$table
        .find('tr')
        .find('td:eq(0),th:eq(0)')
        .show();
    } else {
      self.$table.find('th, td').show();
    }
    if (self.$table.data('plugin_jHueTableExtender')) {
      self.$table.data('plugin_jHueTableExtender').drawLockedRows(true);
    } else if (self.$table.data('plugin_jHueTableExtender2')) {
      self.$table.data('plugin_jHueTableExtender2').redraw();
    }
  };

  self.fnSortColumn = function(obj, way) {
    const data = self.$table.data('data');

    let idx = obj.originalIndex;
    if (way === 0) {
      idx = 0;
    }

    let sortType = 'alpha';
    if (obj.cssClass) {
      if (obj.cssClass === 'sort-numeric') {
        sortType = 'numeric';
      }
      if (obj.cssClass === 'sort-date') {
        sortType = 'date';
      }
    }

    if (way === -1 || way === 0) {
      data.sort((a, b) => {
        if (sortType === 'date') {
          if (a[idx] === 'NULL') {
            return -1;
          }
          if (b[idx] === 'NULL') {
            return 1;
          }
          if (
            moment(a[idx].replace(/\&nbsp;/, ' ')).valueOf() >
            moment(b[idx].replace(/\&nbsp;/, ' ')).valueOf()
          ) {
            return 1;
          }
          if (
            moment(a[idx].replace(/\&nbsp;/, ' ')).valueOf() <
            moment(b[idx].replace(/\&nbsp;/, ' ')).valueOf()
          ) {
            return -1;
          }
          return 0;
        } else if (sortType === 'numeric') {
          if (a[idx] === 'NULL') {
            return -1;
          }
          if (b[idx] === 'NULL') {
            return 1;
          }
          if (a[idx] * 1 > b[idx] * 1) {
            return 1;
          }
          if (a[idx] * 1 < b[idx] * 1) {
            return -1;
          }
          return 0;
        } else {
          if (a[idx] > b[idx]) {
            return 1;
          }
          if (a[idx] < b[idx]) {
            return -1;
          }
          return 0;
        }
      });
    } else {
      data.sort((a, b) => {
        if (sortType === 'date') {
          if (a[idx] === 'NULL') {
            return 1;
          }
          if (b[idx] === 'NULL') {
            return -1;
          }
          if (
            moment(a[idx].replace(/\&nbsp;/, ' ')).valueOf() >
            moment(b[idx].replace(/\&nbsp;/, ' ')).valueOf()
          ) {
            return -1;
          }
          if (
            moment(a[idx].replace(/\&nbsp;/, ' ')).valueOf() <
            moment(b[idx].replace(/\&nbsp;/, ' ')).valueOf()
          ) {
            return 1;
          }
          return 0;
        } else if (sortType === 'numeric') {
          if (a[idx] === 'NULL') {
            return 1;
          }
          if (b[idx] === 'NULL') {
            return -1;
          }
          if (a[idx] * 1 > b[idx] * 1) {
            return -1;
          }
          if (a[idx] * 1 < b[idx] * 1) {
            return 1;
          }
          return 0;
        } else {
          if (a[idx] > b[idx]) {
            return -1;
          }
          if (a[idx] < b[idx]) {
            return 1;
          }
          return 0;
        }
      });
    }

    self.fnDraw(true);
  };

  self.fnShowSearch = function() {
    if ($('.hue-datatable-search').length == 0) {
      const search = $('<div>')
        .css({
          position: 'fixed',
          bottom: '20px',
          opacity: 0.85
        })
        .addClass('hueAnchor hue-datatable-search')
        .appendTo(HUE_CONTAINER);
      search.html(
        '<input type="text"> <i class="fa fa-chevron-up pointer muted"></i> <i class="fa fa-chevron-down pointer muted"></i> &nbsp; <span></span> &nbsp; <i class="fa fa-times pointer inactive-action"></i>'
      );

      search.find('.fa-times').on('click', () => {
        search.hide();
        const $t = self.$table;
        if ($t.data('scrollToRow') != null) {
          $t.data('scrollToCol', null);
          $t.data('scrollToRow', null);
          $t.find('.columnSelected').removeClass('columnSelected');
        }
      });

      search.find('.fa-chevron-down').on('click', () => {
        if (!self.isScrolling) {
          self.fnScrollToNextResult();
        }
      });

      search.find('.fa-chevron-up').on('click', () => {
        if (!self.isScrolling) {
          self.fnScrollToPreviousResult();
        }
      });

      search.find('input').jHueDelayedInput(
        () => {
          self.fnSearch(search.find('input').val());
        },
        600,
        true
      );

      search.find('input').keydown(e => {
        if ([13, 37, 38, 39, 40].indexOf(e.keyCode) > -1) {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          if ([13, 39, 40].indexOf(e.keyCode) > -1) {
            search.find('.fa-chevron-down').trigger('click');
          } else {
            search.find('.fa-chevron-up').trigger('click');
          }
        }
      });

      search.find('input').focus();

      huePubSub.subscribe('hue.datatable.search.hide', () => {
        $('.hue-datatable-search').hide();
      });
    } else {
      $('.hue-datatable-search').show();
      $('.hue-datatable-search')
        .find('input')
        .focus();
    }
    let right = -30;
    const adjustRight =
      $(window).width() - ($('.page-content').width() + $('.page-content').offset().left);
    if (adjustRight > 0) {
      right = adjustRight;
    }
    $('.hueAnchorScroller:visible').each(function() {
      const visibleRight =
        $(this)
          .css('right')
          .replace(/px/gi, '') * 1;
      if (!isNaN(visibleRight) && visibleRight > right) {
        right = visibleRight;
      }
    });
    $('.hue-datatable-search').css('right', right + 50 + 'px');
  };

  self.fnSearch = function(what, avoidScroll) {
    const $t = self.$table;
    if ($t) {
      if (typeof avoidScroll === 'undefined' || !avoidScroll) {
        $t.find('.columnSelected').removeClass('columnSelected');
        $t.data('scrollToCol', null);
        $t.data('scrollToRow', null);
      }

      if (what !== '') {
        $('.hue-datatable-search')
          .find('span')
          .text('');
        $('.hue-datatable-search')
          .find('.fa-chevron-down')
          .addClass('muted')
          .removeClass('inactive-action');
        $('.hue-datatable-search')
          .find('.fa-chevron-up')
          .addClass('muted')
          .removeClass('inactive-action');
        const coords = [];
        $t.data('searchCoords', []);
        $t.data('searchCoordHighlighted', 0);
        const data = self.$table.data('data');
        data.forEach((row, rowIdx) => {
          row.forEach((fld, fldIdx) => {
            if (
              (fld + '')
                .replace(/\&nbsp;/, ' ')
                .toLowerCase()
                .indexOf(what.toLowerCase()) > -1
            ) {
              coords.push({
                row: rowIdx,
                col: fldIdx
              });
            }
          });
        });
        $t.data('searchCoords', coords);
        if (coords.length > 0) {
          if (
            $('.hue-datatable-search')
              .find('input')
              .val() !== ''
          ) {
            $('.hue-datatable-search')
              .find('.fa-chevron-down')
              .removeClass('muted')
              .addClass('inactive-action');
            $('.hue-datatable-search')
              .find('.fa-chevron-up')
              .removeClass('muted')
              .addClass('inactive-action');
          }
          if (typeof avoidScroll === 'undefined' || !avoidScroll) {
            self.fnScrollTo(coords[0].row, coords[0].col);
          } else {
            $('.hue-datatable-search')
              .find('span')
              .text(
                $t.data('searchCoordHighlighted') +
                  1 +
                  ' ' +
                  $t.data('oInit')['i18n'].OF +
                  ' ' +
                  $t.data('searchCoords').length
              );
          }
        } else {
          $('.hue-datatable-search')
            .find('span')
            .text($t.data('oInit')['i18n'].NO_RESULTS);
        }
      }
    }
  };

  self.fnScrollToPreviousResult = function() {
    const $t = self.$table;
    if ($t && $t.data('searchCoords') && $t.data('searchCoords').length > 0) {
      let high = $t.data('searchCoordHighlighted');
      high = high == 0 ? $t.data('searchCoords').length - 1 : high - 1;
      $t.data('searchCoordHighlighted', high);
      self.fnScrollTo($t.data('searchCoords')[high].row, $t.data('searchCoords')[high].col);
    }
  };

  self.fnScrollToNextResult = function() {
    const $t = self.$table;
    if ($t && $t.data('searchCoords') && $t.data('searchCoords').length > 0) {
      let high = $t.data('searchCoordHighlighted');
      high = high == $t.data('searchCoords').length - 1 ? 0 : high + 1;
      $t.data('searchCoordHighlighted', high);
      self.fnScrollTo($t.data('searchCoords')[high].row, $t.data('searchCoords')[high].col);
    }
  };

  self.isScrolling = false;
  self.fnScrollTo = function(row, col) {
    const $t = self.$table;
    if ($t) {
      self.isScrolling = true;
      $('.hue-datatable-search')
        .find('span')
        .text(
          $t.data('searchCoordHighlighted') +
            1 +
            ' ' +
            $t.data('oInit')['i18n'].OF +
            ' ' +
            $t.data('searchCoords').length
        );
      const colSel = $t.find('tr th:nth-child(' + (col + 1) + ')');
      $t.parent().animate(
        {
          scrollLeft:
            colSel.position().left + $t.parent().scrollLeft() - $t.parent().offset().left - 30
        },
        300,
        () => {
          self.isScrolling = false;
        }
      );
      $t.parents($t.data('oInit')['scrollable']).animate(
        {
          scrollTop:
            $t
              .find('tbody tr')
              .find('td:eq(0)')
              .filter(function() {
                return $(this).text() - 1 == row;
              })
              .position().top + 73
        },
        100,
        () => {
          $t.data('scrollToCol', col);
          $t.data('scrollToRow', row);
          $t.data('scrollAnimate', true);
          $t.parent().trigger('scroll');
        }
      );
    }
  };

  self.isDrawing = false;

  self.fnDraw = function(force) {
    const aoColumns = self.$table.data('aoColumns');
    if (!self.isDrawing && aoColumns) {
      const $t = self.$table;
      if ($t) {
        self.isDrawing = true;
        const data = self.$table.data('data');
        const appendable = $t.children('tbody').length > 0 ? $t.children('tbody') : $t;
        let startCol = -1;
        let endCol = -1;
        $t.find('thead>tr th').each(function(i) {
          if ($(this).position().left > 0 && startCol == -1) {
            startCol = i;
          }
          if ($(this).position().left < $t.parent().width() + $t.parent().position().left) {
            endCol = i;
          }
        });
        startCol = Math.max(1, startCol - 1);
        endCol = Math.min(aoColumns.length, endCol + 3); // avoid loading just after the col
        // for tables under the 30 columns, display them all at once
        if (aoColumns.length <= 30) {
          endCol = aoColumns.length;
        }

        const rowHeight = 32;
        const invisibleOffset = $t.data('oInit')['forceInvisible']
          ? $t.data('oInit')['forceInvisible']
          : aoColumns.length < 100
          ? 10
          : 1;
        const scrollable = $t.parents($t.data('oInit')['scrollable']);
        let visibleRows = Math.ceil(
          (scrollable.height() - Math.max($t.offset().top, 0)) / rowHeight
        );
        if ($t.data('oInit')['contained']) {
          visibleRows = Math.ceil(scrollable.height() / rowHeight);
        }
        visibleRows += invisibleOffset;
        visibleRows = Math.max(visibleRows, 11);

        let startRow =
          $t.offset().top - 73 < 0
            ? Math.max(Math.floor(Math.abs($t.offset().top - 73) / rowHeight) - invisibleOffset, 0)
            : 0;
        if ($t.data('oInit')['contained']) {
          startRow = Math.max(
            0,
            Math.floor(Math.abs($t.position().top) / rowHeight) - invisibleOffset
          );
        }
        const endRow = startRow + visibleRows + invisibleOffset;

        if (
          endRow != $t.data('endRow') ||
          (endRow == $t.data('endRow') && endCol > $t.data('endCol')) ||
          force
        ) {
          $t.data('endCol', endCol);
          $t.data('endRow', endRow);

          if ($t.data('fnDraws') === 0) {
            let html = '';
            for (let i = 0; i < data.length; i++) {
              html +=
                '<tr class="ht-visible-row ht-visible-row-' +
                i +
                '"><td>' +
                hueUtils.deXSS(data[i][0]) +
                '</td><td colspan="' +
                (aoColumns.length - 1) +
                '" class="stripe"></td></tr>';
            }
            appendable.html(html);
            if ($t.data('plugin_jHueTableExtender')) {
              $t.data('plugin_jHueTableExtender').drawFirstColumn();
            }
            if ($t.data('plugin_jHueTableExtender2')) {
              $t.data('plugin_jHueTableExtender2').drawFirstColumn(true);
            }
          } else if (force) {
            let html = '';
            for (let i = $t.find('.ht-visible-row').length; i < data.length; i++) {
              html +=
                '<tr class="ht-visible-row ht-visible-row-' +
                i +
                '"><td>' +
                hueUtils.deXSS(data[i][0]) +
                '</td><td colspan="' +
                (aoColumns.length - 1) +
                '" class="stripe"></td></tr>';
            }
            appendable.html(appendable.html() + html);
          }

          for (let i = 0; i < data.length; i++) {
            let html = '';
            if (i >= startRow && i <= endRow) {
              const row = data[i];
              if (row) {
                for (let j = 0; j < endCol; j++) {
                  html +=
                    '<td ' +
                    (!aoColumns[j].bVisible ? 'style="display: none"' : '') +
                    '>' +
                    hueUtils.deXSS(row[j]) +
                    '</td>';
                }

                if (endCol < aoColumns.length) {
                  html += '<td colspan="' + (aoColumns.length - endCol) + '" class="stripe"></td>';
                }
              }
            } else {
              html =
                '<td>' +
                hueUtils.deXSS(data[i][0]) +
                '</td><td colspan="' +
                (aoColumns.length - 1) +
                '" class="stripe"></td>';
            }
            appendable
              .children()
              .eq(i)
              .html(html);
          }

          if (force) {
            if ($t.data('plugin_jHueTableExtender')) {
              $t.data('plugin_jHueTableExtender').drawFirstColumn();
            }
            if ($t.data('plugin_jHueTableExtender2')) {
              $t.data('plugin_jHueTableExtender2').drawFirstColumn(true);
            }
          }
        }
        if ($t.data('scrollToCol')) {
          $t.find('.columnSelected').removeClass('columnSelected');
          let colSel = $t.find('tr th:nth-child(' + ($t.data('scrollToCol') + 1) + ')');
          if ($t.find('tr td:nth-child(' + ($t.data('scrollToCol') + 1) + ')').length > 0) {
            colSel = $t.find('tr td:nth-child(' + ($t.data('scrollToCol') + 1) + ')');
          }
          if ($t.data('scrollAnimate')) {
            if ($t.data('scrollAnimateDirect')) {
              $t.parent().scrollLeft(
                colSel.position().left +
                  $t.parent().scrollLeft() -
                  ($t.data('scrollInPopover') ? 0 : $t.parent().offset().left) -
                  30
              );
              $t.parent().trigger('scroll');
            } else {
              $t.parent().animate(
                {
                  scrollLeft:
                    colSel.position().left +
                    $t.parent().scrollLeft() -
                    ($t.data('scrollInPopover') ? 0 : $t.parent().offset().left) -
                    30
                },
                300,
                () => {
                  $t.parent().trigger('scroll');
                }
              );
            }
            if (
              $t.data('scrollLastColPosLeft') == null ||
              $t.data('scrollLastColPosLeft') != colSel.position().left
            ) {
              $t.data('scrollLastColPosLeft', colSel.position().left);
              $t.data('scrollLastParentLeft', $t.parent().scrollLeft());
            } else {
              $t.data('scrollAnimate', null);
              $t.data('scrollAnimateDirect', null);
              $t.data('scrollLastColPosLeft', null);
              $t.data('scrollLastParentLeft', null);
            }
          }
          if ($t.data('scrollToRow') == null) {
            colSel.addClass('columnSelected');
          } else {
            $t.find(
              'tr:nth-child(' +
                ($t.data('scrollToRow') + 1) +
                ') td:nth-child(' +
                ($t.data('scrollToCol') + 1) +
                ')'
            ).addClass('columnSelected');
          }

          if ($t.data('plugin_jHueTableExtender')) {
            $t.data('plugin_jHueTableExtender').drawHeader(typeof force === 'undefined');
            $t.data('plugin_jHueTableExtender').drawLockedRows();
          }
          if ($t.data('plugin_jHueTableExtender2')) {
            $t.data('plugin_jHueTableExtender2').drawLockedRows();
          }
        }
        $t.data('fnDraws', $t.data('fnDraws') + 1);
        if ($t.data('oInit')['fnDrawCallback']) {
          $t.data('oInit')['fnDrawCallback']();
        }

        $t.trigger('headerpadding');

        self.isDrawing = false;
      }
    }
  };

  self.fnAddData = function(mData, bRedraw) {
    const $t = self.$table;

    if ($t) {
      const aoColumns = $t.data('aoColumns') || [];
      $t.data('data', $t.data('data').concat(mData));

      if (mData.length === 0) {
        return;
      }

      if (aoColumns.length === 0) {
        mData[0].forEach(() => {
          aoColumns.push({
            bVisible: true
          });
        });
      }
      self.fnDraw(true);

      if ($('.hue-datatable-search').is(':visible')) {
        self.fnSearch(
          $('.hue-datatable-search')
            .find('input')
            .val(),
          true
        );
      }
    }
  };

  self.fnSettings = function() {
    const aoColumns = self.$table.data('aoColumns');
    return {
      aoColumns: aoColumns
    };
  };

  self.fnClearTable = function(bRedraw) {
    const $t = self.$table;
    if ($t) {
      if ($t.children('tbody').length > 0) {
        $t.children('tbody').empty();
      } else {
        $t.children('tr').remove();
      }
      $t.data('data', []);
      $t.data('aoRows', []);
      $t.data('aoColumns', []);
      $t.data('fnDraws', 0);
    }
  };

  self.fnDestroy = function() {
    self.fnClearTable();
    self.$table.unwrap();
    self.$table.data('isScrollAttached', null);
    self.$table.removeClass('table-huedatatable');
    if (self.$table.data('oInit')) {
      self.$table
        .parents(self.$table.data('oInit')['scrollable'])
        .off(
          'scroll',
          self.$table.parents(self.$table.data('oInit')['scrollable']).data('scrollFnDt')
        );
    }
  };

  return self.each(function() {
    self.$table = $(this);
    const parent = self.$table.parent();
    if (parent.hasClass('dataTables_wrapper')) {
      return;
    }
    $('.hue-datatable-search').remove();
    self.$table.data('data', []);
    self.$table.data('aoRows', []);
    self.$table.data('aoColumns', []);
    self.$table.data('fnDraws', 0);
    self.$table.wrap('<div class="dataTables_wrapper"></div>');

    self.$table.unbind('sort');
    self.$table.bind('sort', (e, obj) => {
      self.$table
        .find('thead tr th:not(:eq(' + obj.originalIndex + '))')
        .removeClass('sorting_desc')
        .removeClass('sorting_asc');
      self.$table.data('scrollAnimate', true);
      self.$table.data('scrollAnimateDirect', true);
      const $cell = self.$table.find('thead tr th:eq(' + obj.originalIndex + ')');
      if ($cell.hasClass('sorting_desc')) {
        $cell.removeClass('sorting_desc');
        self.fnSortColumn(obj, 0);
      } else if ($cell.hasClass('sorting_asc')) {
        $cell.removeClass('sorting_asc').addClass('sorting_desc');
        self.fnSortColumn(obj, 1);
      } else {
        $cell.addClass('sorting_asc');
        self.fnSortColumn(obj, -1);
      }
      if (self.$table.data('plugin_jHueTableExtender2')) {
        self.$table.data('plugin_jHueTableExtender2').drawHeader();
        self.$table.data('plugin_jHueTableExtender2').drawLockedRows();
      }
    });

    if (typeof oInit !== 'undefined') {
      self.$table.data('oInit', oInit);
      let drawTimeout = -1;
      if (self.$table.data('oInit')['scrollable'] && !self.$table.data('isScrollAttached')) {
        self.$table.data('isScrollAttached', true);
        const scrollFn = function() {
          window.clearTimeout(drawTimeout);
          drawTimeout = window.setTimeout(
            self.fnDraw,
            Math.max(
              100,
              Math.min(
                self.$table.data('aoColumns') ? self.$table.data('aoColumns').length : 500,
                500
              )
            )
          );
        };
        window.setTimeout(() => {
          self.$table.parents(oInit['scrollable']).data('scrollFnDt', scrollFn);
          self.$table.parents(oInit['scrollable']).on('scroll', scrollFn);
        }, 1000);
      }
    }
    self.$table.addClass('table-huedatatable');
  });
};
