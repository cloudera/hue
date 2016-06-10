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

    self.fnSetColumnVis = function(index, visible) {
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

    self.fnDraw = function () {};

    self.fnAddData = function (mData, bRedraw) {
      var aoColumns = this.$table.data('aoColumns');

      var $t = self.$table;
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


      var appendable = $t.children('tbody').length > 0 ? $t.children('tbody') : $t;
      var html = '';
      mData.forEach(function (row) {
        html += '<tr>';
        var index = 0;
        row.forEach(function (cell) {
          if (aoColumns[index].bVisible) {
            html += '<td>' + cell + '</td>';
          } else {
            html += '<td style="display: none;">' + cell + '</td>';
          }
          index++;
        });
        html += '</tr>';
      });
      appendable.append(html);
      if (oInit['fnDrawCallback']){
        oInit['fnDrawCallback']();
      }
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
    };

    self.fnDestroy = function () {
      self.$table.unwrap();
      self.$table.removeClass('table-huedatatable');
    };

    return self.each(function () {
      self.$table = $(this);
      var parent = self.$table.parent();
      if (parent.hasClass('dataTables_wrapper')) {
        return;
      }
      self.$table.data('aoRows', []);
      self.$table.data('aoColumns', []);
      self.$table.wrap('<div class="dataTables_wrapper"></div>');
      self.$table.addClass('table-huedatatable');
    });
  };
})(jQuery, window, document);