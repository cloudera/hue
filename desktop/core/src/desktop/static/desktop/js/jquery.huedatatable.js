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
/*
 * Extension to datatable to programmatically switch off datatable in case of huge tables
 *
 */
(function ($, window, document) {

  $.fn.hueDataTable = function (oInit) {

    var self = this;
    self.$table = null;

    self.fnSetColumnVis = function (index, visible) {
      var aoColumns = this.$table.data('aoColumns');
      var change = aoColumns[index].bVisible !== visible;
      aoColumns[index].bVisible = visible;
      if (!change) {
        return;
      }
      if (!visible) {
        self.$table.find('tr').find('td:eq(' + index + '),th:eq(' + index + ')').hide();
      } else {
        self.$table.find('tr').find('td:eq(' + index + '),th:eq(' + index + ')').show();
      }
    }

    self.isDrawing = false;

    self.fnDraw = function (force) {
      if (!self.isDrawing) {

        self.isDrawing = true;
        var $t = self.$table;
        var aoColumns = self.$table.data('aoColumns');
        var data = self.$table.data('data');
        var appendable = $t.children('tbody').length > 0 ? $t.children('tbody') : $t;
        var startCol = -1;
        var endCol = -1;
        $t.find("thead>tr th").each(function(i){
          if ($(this).position().left > 0 && startCol == -1){
            startCol = i;
          }
          if ($(this).position().left < $t.parent().width() + $t.parent().position().left){
            endCol = i;
          }
        });
        startCol = Math.max(1, startCol - 1);
        endCol = Math.min(aoColumns.length, endCol + 1);

        var rowHeight = 29;
        var invisibleOffset = aoColumns.length < 100 ? 10 : 1;
        var scrollable = $t.parents($t.data('oInit')['scrollable']);
        var visibleRows = Math.ceil((scrollable.height() - Math.max($t.offset().top, 0)) / rowHeight);

        visibleRows += invisibleOffset;

        var startRow = $t.offset().top - 73 < 0 ? Math.max(Math.floor(Math.abs($t.offset().top - 73) / rowHeight) - invisibleOffset, 0) : 0;
        var endRow = startRow + visibleRows + invisibleOffset;

        if (endRow != $t.data('endRow') || (endRow == $t.data('endRow') && endCol > $t.data('endCol')) || force) {
            $t.data('endCol', endCol);
            $t.data('endRow', endRow);

            if ($t.data('fnDraws') == 0) {
              var html = '';
              for (var i = 0; i < data.length; i++) {
                html += '<tr class="ht-visible-row ht-visible-row-' + i + '"><td>' + data[i][0] + '</td><td colspan="' + (aoColumns.length - 1) + '" class="stripe"></td></tr>';
              }
              appendable.html(html);
              if ($t.data('plugin_jHueTableExtender')) {
                $t.data('plugin_jHueTableExtender').drawFirstColumn();
              }
            }
            else {
              if (force) {
                var html = '';
                for (var i = $t.find('.ht-visible-row').length; i < data.length; i++) {
                  html += '<tr class="ht-visible-row ht-visible-row-' + i + '"><td>' + data[i][0] + '</td><td colspan="' + (aoColumns.length - 1) + '" class="stripe"></td></tr>';
                }
                appendable.html(appendable.html() + html);
                if ($t.data('plugin_jHueTableExtender')) {
                  $t.data('plugin_jHueTableExtender').drawFirstColumn();
                }
              }
            }

            for (var i = 0; i < data.length; i++) {
              var html = '';
              if (i >= startRow && i <= endRow) {
                var row = data[i];
                if (row) {

                  for (var j = 0; j < endCol; j++) {
                    html += '<td>' + row[j] + '</td>';
                  }

                  if (endCol < aoColumns.length) {
                    html += '<td colspan="' + (aoColumns.length - endCol) + '" class="stripe"></td>';
                  }
                }
              }
              else {
                html = '<td>' + data[i][0] + '</td><td colspan="' + (aoColumns.length - 1) + '" class="stripe"></td>';
              }
              appendable.children().eq(i).html(html);
            }

            if ($t.data('scrollToCol')){
              var colSel = $t.find("tr th:nth-child(" + ($t.data('scrollToCol') + 1) + ")");
              $t.parent().animate({
                scrollLeft: colSel.position().left + $t.parent().scrollLeft() - $t.parent().offset().left - 30
              }, 300);
              colSel = $t.find("tr td:nth-child(" + ($t.data('scrollToCol') + 1) + ")");
              colSel.addClass("columnSelected");
              $t.data('scrollToCol', null);
            }

            if ($t.data('plugin_jHueTableExtender')) {
              $t.data('plugin_jHueTableExtender').drawHeader(typeof force === 'undefined');
              $t.data('plugin_jHueTableExtender').drawLockedRows();
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

    self.fnAddData = function (mData, bRedraw) {
      var $t = self.$table;

      var aoColumns = $t.data('aoColumns') || [];
      $t.data('data', $t.data('data').concat(mData));

      if (mData.length === 0) {
        return;
      }

      if (aoColumns.length === 0) {
        mData[0].forEach(function () {
          aoColumns.push({
            bVisible: true
          })
        })
      }

      self.fnDraw(true);

    };

    self.fnSettings = function () {
      var aoColumns = self.$table.data('aoColumns');
      return {
        aoColumns: aoColumns
      }
    }

    self.fnClearTable = function (bRedraw) {
      var $t = self.$table;
      if ($t.children('tbody').length > 0) {
        $t.children('tbody').empty();
      }
      else {
        $t.children('tr').remove();
      }
      $t.data('data', []);
      $t.data('aoRows', []);
      $t.data('aoColumns', []);
      $t.data('fnDraws', 0);
    };

    self.fnDestroy = function () {
      self.fnClearTable();
      self.$table.unwrap();
      self.$table.removeClass('table-huedatatable');
    };

    return self.each(function () {
      self.$table = $(this);
      var parent = self.$table.parent();
      if (parent.hasClass('dataTables_wrapper')) {
        return;
      }
      self.$table.data('data', []);
      self.$table.data('aoRows', []);
      self.$table.data('aoColumns', []);
      self.$table.data('fnDraws', 0);
      self.$table.wrap('<div class="dataTables_wrapper"></div>');

      if (typeof oInit !== 'undefined') {
        self.$table.data('oInit', oInit);
        var drawTimeout = -1;
        if (self.$table.data('oInit')['scrollable'] && !self.$table.data('isScrollAttached')) {
          self.$table.data('isScrollAttached', true);
          self.$table.parents(oInit['scrollable']).on('scroll', function () {
            window.clearTimeout(drawTimeout);
            drawTimeout = window.setTimeout(self.fnDraw, Math.max(100, Math.min(self.$table.data('aoColumns').length, 500)));
          });
        }
      }
      self.$table.addClass('table-huedatatable');
    });
  };
})(jQuery, window, document);