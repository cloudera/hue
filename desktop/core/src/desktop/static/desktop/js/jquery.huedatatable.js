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
    self.fnDraw = function () {
      if (!self.isDrawing) {
        self.isDrawing = true;
        var rowHeight = 29;
        var $t = self.$table;

        var aoColumns = self.$table.data('aoColumns');
        var appendable = $t.children('tbody').length > 0 ? $t.children('tbody') : $t;

        var invisibleOffset = 1;
        var scrollable = $t.parents($t.data('oInit')['scrollable']);
        var visibleRows = Math.ceil((scrollable.height() - Math.max($t.offset().top, 0)) / rowHeight) + invisibleOffset;

        var startRow = $t.offset().top - 73 < 0 ? Math.max(Math.floor(Math.abs($t.offset().top - 73) / rowHeight) - invisibleOffset, 0) : 0;
        var endRow = startRow + visibleRows;

        var northSpace = rowHeight * startRow;
        if ($t.find('.ht-north-spacer').length === 0) {
          $('<tr>').addClass('ht-north-spacer').hide().html('<td colspan="' + (aoColumns.length) + '"></td>').appendTo(appendable);
        }
        else {
          if (northSpace > 0) {
            $t.find('.ht-north-spacer').show().html('<td colspan="' + (aoColumns.length) + '" style="height: ' + northSpace + 'px"></td>');
          }
          else {
            $t.find('.ht-north-spacer').hide();
          }
        }

        $t.find('.ht-visible-row').empty();

        for (var i=0; i<visibleRows; i++) {
          if ($t.find('.ht-visible-row-' + i).length === 0) {
            $t.find('.ht-north-spacer').after('<tr class="ht-visible-row ht-visible-row-' + i + '"></tr>');
          }
        }

        $t.find('.ht-visible-row').each(function(idx, el){
          var row = $t.data('data')[startRow + idx];
          var html = '';
          if (row){
            for (var j = 0; j < aoColumns.length; j++) {
              html += '<td>' + row[j] + '</td>';
            }
          }
          $(el).html(html);
        });


        var southSpace = rowHeight * ($t.data('data').length - endRow);
        if ($t.find('.ht-south-spacer').length === 0) {
          $('<tr>').addClass('ht-south-spacer').html('<td colspan="' + (aoColumns.length) + '" style="height: ' + southSpace + 'px"></td>').appendTo(appendable);
        }
        else {
          $t.find('.ht-south-spacer').html('<td colspan="' + (aoColumns.length) + '" style="height: ' + southSpace + 'px"></td>');
        }

        if ($t.data('oInit')['fnDrawCallback']) {
          window.setTimeout(function(){
            $t.data('oInit')['fnDrawCallback']();
          }, 0);
        }
        self.isDrawing = false;
      }
    };

    self.fnAddData = function (mData, bRedraw) {
      var aoColumns = self.$table.data('aoColumns') || [];

      var $t = self.$table;

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

      self.fnDraw();

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
      self.$table.wrap('<div class="dataTables_wrapper"></div>');

      if (typeof oInit !== 'undefined') {
        self.$table.data('oInit', oInit);
        var drawTimeout = -1;
        if (self.$table.data('oInit')['scrollable'] && !self.$table.data('isScrollAttached')) {
          self.$table.data('isScrollAttached', true);
          self.$table.parents(oInit['scrollable']).on('scroll', function () {
            window.clearTimeout(drawTimeout);
            drawTimeout = window.setTimeout(self.fnDraw, 50);
          });
        }
      }
      self.$table.addClass('table-huedatatable');
    });
  };
})(jQuery, window, document);