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

(function ($, window, document, undefined) {

  var PLUGIN_NAME = "jHueTableExtender2";

  var DEFAULT_OPTIONS = {
    stickyHeader: true,
    stickyFirstColumn: true,
    headerSorting: true,
    mainScrollable: window,
    labels: {
      GO_TO_COLUMN: "Go to column:",
      PLACEHOLDER: "column name...",
      LOCK: "Lock row",
      UNLOCK: "Unlock row",
      ROW_DETAILS: "Show row details"
    }
  };

  function Plugin(sourceTable, options) {
    var self = this;
    self.setOptions(options);
    self.disposeFunctions = [];

    if (!self.options.stickyHeader && !self.options.stickyFirstColumn) {
      return;
    }

    self.$sourceTable = $(sourceTable);
    self.$parent = self.$sourceTable.parent();
    self.$mainScrollable = $(self.options.mainScrollable);

    self.$firstCellTable = null;
    self.$firstColumnTable = null;
    self.$headerTable = null;

    self.initParent();
    self.redraw();

    if (self.options.stickyFirstColumn) {
      self.$parent.on('scroll.tableExtender', self.repositionLeftColumn.bind(self));
    }

    self.disposeFunctions.push(huePubSub.subscribe('table.extender.redraw', function (parentId) {
      if (parentId === self.options.parentId) {
        self.redraw();
      }
    }).remove);
  }

  Plugin.prototype.destroy = function () {
    var self = this;
    self.$parent.off('.tableExtender');
    self.disposeFunctions.forEach(function (dispose) {
      dispose();
    })
  };

  Plugin.prototype.setOptions = function (options) {
    var self = this;
    self.options = $.extend({}, DEFAULT_OPTIONS, options);
    self.options.labels = $.extend({}, DEFAULT_OPTIONS.labels, HUE_I18n.jHueTableExtender, options ? options.labels : {})
  };

  Plugin.prototype.initParent = function () {
    var self = this;
    var parentPosition = self.$parent.css('position');
    self.$parent.css('position', (!parentPosition || parentPosition === 'static') ? 'relative' : parentPosition);
  };

  Plugin.prototype.createEmptyTableClone = function () {
    var self = this;
    var $result = $('<table>');
    $result.attr('class', self.$sourceTable.attr('class'));
    $result.attr('style', self.$sourceTable.attr('style'));
    $result.css({ 'position': 'absolute', 'top': 0, 'left': 0 });
    return $result;
  };

  Plugin.prototype.redraw = function () {
    var self = this;
    if (self.options.stickyHeader) {
      self.drawHeader();
    }
    if (self.options.stickyFirstColumn) {
      self.drawFirstColumn();
    }
  };

  Plugin.prototype.drawHeader = function () {
    var self = this;
  };

  Plugin.prototype.drawFirstColumn = function () {
    var self = this;

    var $firstColumnTable = self.createEmptyTableClone().css('z-index', 2);

    // Clone the header for the first cell
    var $sourceFirstHeader = self.$sourceTable.find('thead>tr th:eq(0)');

    var $clonedFirstHeader = $sourceFirstHeader.clone();
    $clonedFirstHeader.wrap('<tr></tr>').parent().wrap('<thead>').parent().appendTo($firstColumnTable);
    $firstColumnTable.width($sourceFirstHeader.outerWidth(true));

    // Create a separate table for the upper left header cell only
    var $firstCellTable = $firstColumnTable.clone().css('z-index', 3);

    $firstCellTable.find('th').click(function () {
      $sourceFirstHeader.click();
      window.setTimeout(self.drawFirstColumn.bind(self), 0);
    });

    // Clone the cells under the header for the first column
    var $clonedFirstCells = self.$sourceTable.find("tbody>tr td:nth-child(1)").clone();
    $clonedFirstCells.wrapAll('<tbody>').parent().appendTo($firstColumnTable);
    $clonedFirstCells.wrap('<tr>');

    var foundEmptyCell = false;
    $clonedFirstCells.each(function (index, cell) {
      var $cell = $(cell);

      if ($cell.html() === '') {
        foundEmptyCell = true;
        return false;
      }
      if (self.options.lockSelectedRow) {
        $cell.addClass('lockable');
        $('<i>').addClass('fa fa-lock pointer muted').attr('title', self.options.labels.LOCK).on('click', function() {
          self.drawLockedRow(index);
        }).prependTo($cell);
        $('<i>').addClass('fa fa-expand pointer muted').attr('title', self.options.labels.ROW_DETAILS).on('click', function(){
          huePubSub.publish('table.row.dblclick', { idx: index, table: self.$sourceTable });
        }).prependTo($cell);
      }
    });

    if (foundEmptyCell) {
      // In IE the cell can be empty at initial render, if so we defer the rendering
      window.setTimeout(self.drawFirstColumn.bind(self), 100);
      return;
    }

    // Append the table for the first columns
    if (self.$firstColumnTable) {
      self.$firstColumnTable.remove();
    }
    self.$firstColumnTable = $firstColumnTable;
    self.$firstColumnTable.css('left', self.$parent.scrollLeft() + 'px');
    self.$firstColumnTable.appendTo(self.$parent);

    // Append the table for the first cell (header of first column)
    if (self.$firstCellTable) {
      self.$firstCellTable.remove();
    }
    self.$firstCellTable = $firstCellTable;
    self.$firstCellTable.width(self.$firstColumnTable.outerWidth(true)); // Width is only known after the first col render
    self.$firstCellTable.css('left', self.$parent.scrollLeft() + 'px');
    self.$firstCellTable.appendTo(self.$parent);
  };

  Plugin.prototype.lockRow = function (index) {

  };

  Plugin.prototype.repositionLeftColumn = function () {
    var self = this;
    if (self.$firstColumnTable) {
      self.$firstColumnTable.css('left', self.$parent.scrollLeft() + 'px');
      self.$firstCellTable.css('left', self.$parent.scrollLeft() + 'px');
    }
  };

  Plugin.prototype.repositionHeader = function () {

  };

  Plugin.prototype.drawLockedRows = function () {

  };


  $.fn[PLUGIN_NAME] = function (options) {
    return this.each(function () {
      if ($.data(this, 'plugin_' + PLUGIN_NAME)) {
        $.data(this, 'plugin_' + PLUGIN_NAME).destroy();
      }
      $.data(this, 'plugin_' + PLUGIN_NAME, new Plugin(this, options));
    });
  }
})(jQuery, window, document);
