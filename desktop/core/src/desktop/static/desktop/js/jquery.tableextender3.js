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
    classToRemove: 'resultTable',
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
    self.$mainScrollable = self.options.mainScrollable ? $(self.options.mainScrollable) : self.$parent;

    self.$firstCellTable = null;
    self.$firstColumnTable = null;
    self.$headerTable = null;
    self.updateHeaderWidths = $.noop;

    self.initParent();
    self.redraw();

    var widthThrottle = -1;

    if (self.options.stickyFirstColumn) {
      self.$parent.on('scroll.tableExtender', function () {
        self.repositionLeftColumn();
        if (self.options.stickyHeader) {
          window.clearTimeout(widthThrottle);
          widthThrottle = window.setTimeout(self.updateHeaderWidths.bind(self), 50);
        }
      });
    }

    if (self.options.stickyHeader) {
      self.$mainScrollable.on('scroll.tableExtender', self.repositionHeader.bind(self));
      var widthInterval = window.setInterval(self.updateHeaderWidths.bind(self), 100);
      self.disposeFunctions.push(function () {
        window.clearInterval(widthInterval);
      })
    }

    self.disposeFunctions.push(huePubSub.subscribe('table.extender.redraw', function (parentId) {
      if (parentId === self.options.parentId) {
        self.redraw();
      }
    }).remove);
  }

  Plugin.prototype.destroy = function () {
    var self = this;
    $('.table-extender-header_' + self.options.parentId).remove();
    $('.table-extender-first-col-' + self.options.parentId).remove();
    $('.table-extender-first-cell-' + self.options.parentId).remove();
    self.$parent.off('.tableExtender');
    self.$mainScrollable.off('.tableExtender');
    self.disposeFunctions.forEach(function (dispose) {
      dispose();
    });
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
    $result.removeClass(self.options.classToRemove);
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
    var $headerTable = self.createEmptyTableClone().css('z-index', 1);
    $headerTable.addClass('table-extender-header_' + self.options.parentId);

    // Clone the header
    var $sourceHeaders = self.$sourceTable.find('thead>tr th');
    var $clonedHeaders = $sourceHeaders.clone();
    $clonedHeaders.wrapAll('<tr></tr>').parent().wrap('<thead>').parent().appendTo($headerTable);

    $clonedHeaders.each(function (index, clonedTh) {
      var $clonedTh = $(clonedTh);
      var $sourceTh = $sourceHeaders.eq(index);
      $clonedTh.width($sourceTh.width());
      $clonedTh.click(function () {
        $sourceTh.click();
        window.setTimeout(self.drawHeader.bind(self), 0);
      })
    });
    $headerTable.width(self.$sourceTable.width());

    self.updateHeaderWidths = function () {
      var sourceTableWidth = self.$sourceTable.width();
      if (self.$headerTable && sourceTableWidth !== self.$headerTable.width()) {
        self.$headerTable.width(sourceTableWidth);
        $clonedHeaders.each(function (index, clonedTh) {
          var $clonedTh = $(clonedTh);
          var $sourceTh = $sourceHeaders.eq(index);
          $clonedTh.width($sourceTh.width());
        });
      }
    };

    $('.table-extender-header_' + self.options.parentId).remove();

    self.$headerTable = $headerTable;
    self.$headerTable.appendTo(self.$parent);
  };

  Plugin.prototype.lockRow = function (index) {
    var self = this;
  };

  Plugin.prototype.drawLockedRows = function () {
    var self = this;
  };

  Plugin.prototype.drawFirstColumn = function () {
    var self = this;

    var $firstColumnTable = self.createEmptyTableClone().css('z-index', 2);
    $firstColumnTable.addClass('table-extender-first-col-' + self.options.parentId);
    // Clone the header for the first cell
    var $sourceFirstHeader = self.$sourceTable.find('thead>tr th:eq(0)');
    var $clonedFirstHeader = $sourceFirstHeader.clone();
    $clonedFirstHeader.wrap('<tr></tr>').parent().wrap('<thead>').parent().appendTo($firstColumnTable);
    $firstColumnTable.width($sourceFirstHeader.outerWidth(true));

    // Create a separate table for the upper left header cell only
    var $firstCellTable = $firstColumnTable.clone().css('z-index', 3);
    $firstCellTable.addClass('table-extender-first-cell-' + self.options.parentId);

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
        $('<i>').addClass('fa fa-lock pointer muted').attr('title', self.options.labels.LOCK).on('click', function() {
          self.drawLockedRow(index);
        }).prependTo($cell);
      }
      $cell.addClass('lockable');
      $('<i>').addClass('fa fa-expand pointer muted').attr('title', self.options.labels.ROW_DETAILS).on('click', function(){
        huePubSub.publish('table.row.show.details', { idx: index, table: self.$sourceTable });
      }).prependTo($cell);
    });

    if (foundEmptyCell) {
      // In IE the cell can be empty at initial render, if so we defer the rendering
      window.setTimeout(self.drawFirstColumn.bind(self), 100);
      return;
    }

    // Append the table for the first columns
    $('.table-extender-first-col-' + self.options.parentId).remove();
    self.$firstColumnTable = $firstColumnTable;
    self.$firstColumnTable.css('left', self.$parent.scrollLeft() + 'px');
    self.$firstColumnTable.appendTo(self.$parent);

    // Append the table for the first cell (header of first column)
    $('.table-extender-first-cell-' + self.options.parentId).remove();
    self.$firstCellTable = $firstCellTable;
    self.$firstCellTable.width(self.$firstColumnTable.outerWidth(true)); // Width is only known after the first col render
    self.$firstCellTable.css('left', self.$parent.scrollLeft() + 'px');
    self.$firstCellTable.appendTo(self.$parent);
  };

  Plugin.prototype.repositionLeftColumn = function () {
    var self = this;
    if (self.$firstColumnTable) {
      self.$firstColumnTable.css('left', self.$parent.scrollLeft() + 'px');
      self.$firstCellTable.css('left', self.$parent.scrollLeft() + 'px');
    }
  };

  Plugin.prototype.repositionHeader = function () {
    var self = this;
    if (!self.$firstCellTable || !self.$headerTable) {
      return;
    }
    var diff = self.$sourceTable.offset().top - self.$mainScrollable.offset().top;

    if (self.$firstCellTable && diff < 0) {
      self.$firstCellTable.css('padding-top', -diff + 'px');
    } else if (self.$firstCellTable && self.$firstCellTable.position().top !== 0) {
      self.$firstCellTable.css('padding-top', '0');
    }

    if (self.$headerTable && diff < 0) {
      self.$headerTable.css('padding-top', -diff + 'px');
    } else if (self.$headerTable && self.$headerTable.position().top !== 0) {
      self.$headerTable.css('padding-top', '0');
    }
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
