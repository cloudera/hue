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
    this.$table = null;

    this.fnAddData = function (mData, bRedraw) {
      var $t = self.$table;
      if (mData.length === 0) {
        return;
      }
      var appendable = $t.children('tbody').length > 0 ? $t.children('tbody') : $t;
      var html = '';
      mData.forEach(function (row) {
        html += '<tr>';
        row.forEach(function (cell) {
          html += '<td>' + cell + '</td>';
        });
        html += '</tr>';
      });
      appendable.append(html);
      if (oInit['fnDrawCallback']){
        oInit['fnDrawCallback']();
      }
    };

    this.fnClearTable = function (bRedraw) {
      var $t = self.$table;
      if ($t.children('tbody').length > 0) {
        $t.children('tbody').empty();
      }
      else {
        $t.children('tr').remove();
      }
    };

    this.fnDestroy = function () {
      self.$table.unwrap();
      self.$table.removeClass('table-huedatatable');
    };

    return this.each(function () {
      self.$table = $(this);
      self.$table.wrap('<div class="dataTables_wrapper"></div>');
      self.$table.addClass('table-huedatatable');
    });
  };
})(jQuery, window, document);