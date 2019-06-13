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
import I18n from 'utils/i18n';

const PLUGIN_NAME = 'jHueTableExtender2';

const DEFAULT_OPTIONS = {
  fixedHeader: true,
  fixedFirstColumn: true,
  fixedFirstColumnTopMargin: 0,
  headerSorting: true,
  lockSelectedRow: true,
  firstColumnTooltip: false,
  classToRemove: 'resultTable',
  hintElement: null,
  mainScrollable: window,
  app: null,
  stickToTopPosition: -1,
  labels: {
    GO_TO_COLUMN: 'Go to column:',
    PLACEHOLDER: 'column name...',
    LOCK: 'Lock row',
    UNLOCK: 'Unlock row',
    ROW_DETAILS: 'Show row details'
  }
};

function Plugin(element, options) {
  const self = this;
  self.disposeFunctions = [];

  self.lockedRows = {};
  self.setOptions(options); // Sets self.options

  self.$element = $(element);
  self.$parent = self.$element.parent();
  self.$mainScrollable = $(self.options.mainScrollable);
  self.lastHeaderWidth = 0;

  self.drawHeader(); // Sets self.headerRowContainer, self.thMapping
  self.drawFirstColumn(); // Sets self.firstColumnInner, self.firstColumnTopCell and self.firstColumn
  self.drawLockedRows();

  const manyColumns = self.thMapping.length > 20;

  const sortAdjustment = self.options.noSort ? 10 : 20; // 20 is the sorting css width

  let firstCellWidth, leftPosition, th, thi, leftPadding;
  const throttledHeaderPadding = function() {
    firstCellWidth = self.options.fixedFirstColumn ? self.firstColumnTopCell.outerWidth() : 0;
    for (thi = 0; thi < self.thMapping.length; thi++) {
      th = self.thMapping[thi];
      if (!th.original.is(':visible')) {
        continue;
      }
      leftPosition = th.clone.position().left - firstCellWidth;
      if (leftPosition + th.clone.outerWidth() > 0 && leftPosition < 0) {
        if (th.cloneSpan.width() - leftPosition < th.clone.outerWidth() - sortAdjustment) {
          leftPadding = -leftPosition;
        } else {
          leftPadding = th.clone.outerWidth() - sortAdjustment - th.cloneSpan.width();
        }
        th.cloneSpan.css('paddingLeft', leftPadding);
      } else {
        th.cloneSpan.css('paddingLeft', 0);
      }
    }
  };

  let scrollTimeout = -1;
  const headerScroll = function() {
    self.headerRowContainer.scrollLeft(self.$parent.scrollLeft());
    if (manyColumns) {
      window.clearTimeout(scrollTimeout);
      scrollTimeout = window.setTimeout(throttledHeaderPadding, 200);
    } else {
      throttledHeaderPadding();
    }
  };
  self.$parent.on('scroll', headerScroll);
  self.disposeFunctions.push(() => {
    self.$parent.off('scroll', headerScroll);
  });

  self.$element.bind('headerpadding', () => {
    window.clearTimeout(scrollTimeout);
    scrollTimeout = window.setTimeout(throttledHeaderPadding, 200);
  });
  self.disposeFunctions.push(() => {
    self.$element.unbind('headerpadding');
  });

  const redrawSubscription = huePubSub.subscribe('table.extender.redraw', parentId => {
    if (parentId == self.options.parentId) {
      self.redraw();
    }
  });
  self.disposeFunctions.push(() => {
    redrawSubscription.remove();
  });

  const hideSubscription = huePubSub.subscribe('table.extender.hide', parentId => {
    if (parentId == self.options.parentId) {
      self.headerRowContainer.hide();
      self.firstColumnInner.hide();
      self.firstColumnTopCell.hide();
      self.firstColumn.hide();
    }
  });
  self.disposeFunctions.push(() => {
    hideSubscription.remove();
  });

  const adjustSizes = function() {
    if (self.lastHeaderWidth !== self.$parent.width()) {
      self.lastHeaderWidth = self.$parent.width();
      self.headerRowContainer.width(self.lastHeaderWidth);
    }
    for (thi = 0; thi < self.thMapping.length; thi++) {
      th = self.thMapping[thi];
      if (!th.original.is(':visible')) {
        continue;
      }
      if (th.clone.lastWidth !== th.original.width()) {
        th.clone.lastWidth = th.original.width();
        th.clone.width(th.clone.lastWidth);
      }
    }

    if (self.headerRowContainer.scrollLeft() !== self.$parent.scrollLeft()) {
      self.headerRowContainer.scrollLeft(self.$parent.scrollLeft());
      throttledHeaderPadding();
    }
  };
  adjustSizes();
  const sizeInterval = window.setInterval(adjustSizes, 300, self.options.app);
  self.disposeFunctions.push(() => {
    window.clearInterval(sizeInterval);
  });

  const clickHandler = function() {
    if ($(this).hasClass('selected')) {
      self.$parent.find('.selected').removeClass('selected');
    } else {
      self.$parent.find('.selected').removeClass('selected');
      $(this).addClass('selected');
      self.$parent
        .find('.fixed-first-column table tbody tr:eq(' + $(this).index() + ')')
        .addClass('selected');
    }
  };

  const overHandler = function() {
    self.$parent
      .find('.fixed-first-column table tbody tr:eq(' + $(this).index() + ') td')
      .addClass('fixed-first-col-hover');
  };

  const outHandler = function() {
    self.$parent.find('.fixed-first-column table tbody tr td').removeClass('fixed-first-col-hover');
  };

  self.$parent.children('table').on('click dblclick', 'tbody tr', clickHandler);
  self.$parent.children('table').on('mouseover', 'tbody tr', overHandler);
  self.$parent.children('table').on('mouseout', 'tbody tr', outHandler);
  self.disposeFunctions.push(() => {
    self.$parent.children('table').off('click dblclick', 'tbody tr', clickHandler);
    self.$parent.children('table').on('mouseover', 'tbody tr', overHandler);
    self.$parent.children('table').on('mouseout', 'tbody tr', outHandler);
  });

  if (!self.options.disableTopPosition) {
    self.repositionHeader();
    const scrollFunction = self.repositionHeader.bind(self);
    self.$mainScrollable.on('scroll', scrollFunction);
    self.disposeFunctions.push(() => {
      self.$mainScrollable.off('scroll', scrollFunction);
    });
  }
}

Plugin.prototype.redraw = function() {
  const self = this;
  self.drawHeader();
  self.drawFirstColumn();
  self.drawLockedRows(true);
  self.repositionHeader();
  window.setTimeout(() => {
    self.headerRowContainer.scrollLeft(self.$parent.scrollLeft());
    self.$element.trigger('headerpadding');
  }, 300);
};

Plugin.prototype.destroy = function() {
  const self = this;
  self.disposeFunctions.forEach(disposeFunction => {
    disposeFunction();
  });
};

Plugin.prototype.setOptions = function(options) {
  this.options = $.extend({}, DEFAULT_OPTIONS, options);
  this.options.labels = $.extend(
    {},
    DEFAULT_OPTIONS.labels,
    {
      GO_TO_COLUMN: I18n('Go to column:'),
      PLACEHOLDER: I18n('column name...'),
      LOCK: I18n('Lock this row'),
      UNLOCK: I18n('Unlock this row'),
      ROW_DETAILS: I18n('Show row details')
    },
    options ? options.labels : {}
  );
};

Plugin.prototype.repositionHeader = function() {
  const self = this;
  if (self.options.disableTopPosition) {
    return;
  }
  let pos = self.options.stickToTopPosition;
  let topPos = 0;
  let firstColTopPos = 0;
  if (typeof pos === 'function') {
    pos = pos();
  }
  if (window.IS_EMBEDDED) {
    pos = $('.hue-embedded-container').offset().top;
  }
  let isFixed = false;
  if (pos > -1) {
    if (self.$element.offset().top < pos) {
      topPos = pos;
      isFixed = true;
    } else {
      topPos = self.$element.offset().top;
      isFixed = false;
    }
    firstColTopPos = self.$element.offset().top;
  } else if (self.options.clonedContainerPosition == 'absolute') {
    topPos = self.$parent.position().top;
    firstColTopPos = topPos;
  } else {
    topPos = self.$parent.offset().top;
    firstColTopPos = topPos;
  }

  if (pos > -1) {
    let fixCSS = {
      top: '',
      left: self.$parent.position().left + 'px',
      position: 'absolute'
    };
    self.firstColumn.css(fixCSS);
    if (isFixed) {
      fixCSS = {
        top: topPos + 'px',
        left: '',
        position: 'fixed'
      };
    }
    self.firstColumnTopCell.css(fixCSS);
    self.headerRowContainer.css(fixCSS);
  } else {
    self.firstColumn.scrollTop(self.$mainScrollable.scrollTop());
    self.firstColumn.css('top', firstColTopPos + 'px');
    self.headerRowContainer.css('top', topPos + 'px');
    self.firstColumnTopCell.css('top', topPos + 'px');
  }
};

Plugin.prototype.drawHeader = function() {
  const self = this;
  if (!self.$element.attr('id') && self.options.parentId) {
    self.$element.attr('id', 'eT' + self.options.parentId);
  }

  $('#' + self.$element.attr('id') + 'jHueTableExtenderClonedContainer').remove();
  const clonedTable = $('<table>').attr('class', self.$element.attr('class'));
  clonedTable.removeClass(self.options.classToRemove);
  clonedTable.css('margin-bottom', '0').css('table-layout', 'fixed');
  const clonedTableTHead = $('<thead>');
  clonedTableTHead.appendTo(clonedTable);
  const clonedTableTR = self.$element.find('thead>tr').clone();
  clonedTableTR.appendTo(clonedTableTHead);
  $('<tbody>').appendTo(clonedTable);

  const clonedThs = clonedTable.find('thead>tr th');
  clonedThs.wrapInner('<span></span>');

  if (typeof self.$element.data('updateThWidthsInterval') !== 'undefined') {
    window.clearInterval(self.$element.data('updateThWidthsInterval'));
  }

  self.thMapping = [];
  let totalThWidth = 0;
  self.$element.find('thead>tr th').each(function(i) {
    const originalTh = $(this);
    originalTh.removeAttr('data-bind');
    const clonedTh = $(clonedThs[i]).css('background-color', '#FFFFFF');
    clonedTh.click(function() {
      originalTh.click();
      if (self.options.headerSorting) {
        clonedThs.attr('class', 'sorting');
      }
      $(this).attr('class', originalTh.attr('class'));
    });
    clonedTh.width(originalTh.width());
    totalThWidth += originalTh.width();
    self.thMapping.push({
      original: originalTh,
      clone: clonedTh,
      cloneSpan: clonedTh.children().first()
    });
  });

  const headerRowDiv = $('<div>');
  clonedTable.appendTo(headerRowDiv);

  let topPosition;
  if (self.options.clonedContainerPosition == 'absolute') {
    topPosition = self.$parent.position().top - self.$mainScrollable.scrollTop();
  } else {
    topPosition = self.$parent.offset().top - self.$mainScrollable.scrollTop();
  }
  const headerRowContainer = $('<div>')
    .attr('id', self.$element.attr('id') + 'jHueTableExtenderClonedContainer')
    .addClass('fixed-header-row')
    .width(totalThWidth)
    .css('overflow-x', 'hidden');
  if (!self.options.disableTopPosition) {
    headerRowContainer.css('top', topPosition + 'px');
  }
  headerRowContainer.css('position', self.options.clonedContainerPosition || 'fixed');
  self.lastHeaderWidth = self.$parent.width();
  headerRowContainer.width(self.lastHeaderWidth);

  headerRowDiv.appendTo(headerRowContainer);
  headerRowContainer.prependTo(self.$parent);

  headerRowContainer.scrollLeft(self.$parent.scrollLeft());

  self.headerRowContainer = headerRowContainer;
  self.$mainScrollable.trigger('scroll');
};

Plugin.prototype.drawFirstColumn = function(repositionHeader) {
  const self = this;
  if (!self.options.fixedFirstColumn) {
    self.firstColumnInner = $();
    self.firstColumnTopCell = $();
    self.firstColumn = $();
    return;
  }
  if (!self.$element.attr('id') && self.options.parentId) {
    self.$element.attr('id', 'eT' + self.options.parentId);
  }

  const originalTh = self.$element.find('thead>tr th:eq(0)');
  let topPosition;
  if (self.options.clonedContainerPosition == 'absolute') {
    topPosition = self.$parent.position().top - self.$mainScrollable.scrollTop();
  } else {
    topPosition = self.$parent.offset().top - self.$mainScrollable.scrollTop();
  }

  $('#' + self.$element.attr('id') + 'jHueTableExtenderClonedContainerCell').remove();
  const clonedCell = $('<table>').attr('class', self.$element.attr('class'));
  clonedCell.removeClass(self.options.classToRemove);
  clonedCell.css('margin-bottom', '0').css('table-layout', 'fixed');
  const clonedCellTHead = $('<thead><tr></tr></thead>');
  clonedCellTHead.appendTo(clonedCell);
  const clonedCellTH = originalTh.clone();
  clonedCellTH.appendTo(clonedCellTHead.find('tr'));
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

  const firstColumnTopCell = $('<div>')
    .attr('id', self.$element.attr('id') + 'jHueTableExtenderClonedContainerCell')
    .addClass('fixed-first-cell')
    .width(originalTh.outerWidth())
    .css('overflow', 'hidden')
    .css('top', topPosition + 'px');
  firstColumnTopCell.css('position', self.options.clonedContainerPosition || 'fixed');

  clonedCellContainer.appendTo(firstColumnTopCell);

  $('#' + self.$element.attr('id') + 'jHueTableExtenderClonedContainerColumn').remove();
  const clonedTable = $('<table>')
    .attr('class', self.$element.attr('class'))
    .html('<thead><tr></tr></thead><tbody></tbody>');
  clonedTable.removeClass(self.options.classToRemove);
  clonedTable.css('margin-bottom', '0').css('table-layout', 'fixed');
  self.$element
    .find('thead>tr th:eq(0)')
    .clone()
    .appendTo(clonedTable.find('thead tr'));
  const clonedTBody = clonedTable.find('tbody');
  const clones = self.$element.find('tbody>tr td:nth-child(1)').clone();
  let h = '';
  let foundEmptyTh = false;
  clones.each(function() {
    if ($(this).html() === '') {
      foundEmptyTh = true;
    }
    h += '<tr><td>' + $(this).html() + '</td></tr>';
  });
  if (foundEmptyTh) {
    // In IE it's sometimes empty so we'll redraw in a bit
    window.setTimeout(self.drawFirstColumn.bind(self), 200);
    self.firstColumnInner = $();
    self.firstColumnTopCell = $();
    self.firstColumn = $();
    return;
  }
  clonedTBody.html(h);
  if (self.options.lockSelectedRow) {
    clonedTBody.find('td').each(function(idx) {
      const cell = $(this);
      cell.addClass('lockable');
      $('<i>')
        .addClass('fa fa-lock pointer muted')
        .prependTo(cell)
        .on('click', function() {
          self.drawLockedRow(
            $(this)
              .parent()
              .text() * 1
          );
        })
        .attr('title', self.options.labels.LOCK);
      $('<i>')
        .addClass('fa fa-expand pointer muted')
        .prependTo(cell)
        .on('click', () => {
          huePubSub.publish('table.row.show.details', { idx: idx, table: self.$element });
        })
        .attr('title', self.options.labels.ROW_DETAILS);
    });
  }
  clonedTable
    .find('thead>tr th:eq(0)')
    .width(originalTh.width())
    .css('background-color', '#FFFFFF');

  const firstColumnInner = $('<div>')
    .css('background-color', '#FFFFFF')
    .width(originalTh.outerWidth())
    .height(self.$parent.get(0).scrollHeight);
  clonedTable.appendTo(firstColumnInner);

  const firstColumn = $('<div>')
    .attr('id', self.$element.attr('id') + 'jHueTableExtenderClonedContainerColumn')
    .addClass('fixed-first-column')
    .width(originalTh.outerWidth())
    .height(self.$parent.height())
    .css('overflow', 'hidden')
    .css('top', topPosition + 'px');
  firstColumn.css('position', self.options.clonedContainerPosition || 'fixed');

  firstColumnInner.appendTo(firstColumn);
  firstColumn.insertAfter(self.$element.prev());

  firstColumnTopCell.insertAfter(firstColumn);

  self.firstColumnInner = firstColumnInner;
  self.firstColumnTopCell = firstColumnTopCell;
  self.firstColumn = firstColumn;

  if (repositionHeader) {
    self.repositionHeader();
  }
};

Plugin.prototype.drawLockedRows = function(force) {
  const self = this;
  if (Object.keys(self.lockedRows).length === 0) {
    self.headerRowContainer.find('tbody').empty();
    self.headerRowContainer.removeClass('locked');
    self.firstColumnTopCell.removeClass('locked');
  } else {
    self.headerRowContainer.addClass('locked');
    self.firstColumnTopCell.addClass('locked');
    Object.keys(self.lockedRows).forEach(idx => {
      self.drawLockedRow(idx.substr(1), force);
    });
  }
};

Plugin.prototype.drawLockedRow = function(rowNo, force) {
  const self = this;

  function unlock($el) {
    self.headerRowContainer
      .find('tr td:first-child')
      .filter(function() {
        return $(this).text() === rowNo + '';
      })
      .closest('tr')
      .remove();
    delete self.lockedRows['r' + $el.text()];
    $el.parent().remove();
    if (self.headerRowContainer.find('tbody tr').length == 0) {
      self.headerRowContainer.removeClass('locked');
      self.firstColumnTopCell.removeClass('locked');
    }
  }

  if (Object.keys(self.lockedRows).indexOf('r' + rowNo) === -1 || force) {
    if (force) {
      unlock(self.lockedRows['r' + rowNo].cell.find('td'));
    }
    const $clone = $('<tr>').addClass('locked');
    let tHtml = '';
    const aoColumns = self.$element.data('aoColumns');
    self.$element.data('data')[rowNo - 1].forEach((col, idx) => {
      tHtml +=
        '<td ' +
        (aoColumns && !aoColumns[idx].bVisible ? 'style="display: none"' : '') +
        '>' +
        hueUtils.deXSS(col) +
        '</td>';
    });
    $clone.html(tHtml);
    $clone.appendTo(self.headerRowContainer.find('tbody'));
    const $newTr = $('<tr>');
    $newTr
      .addClass('locked')
      .html(
        '<td class="pointer unlockable" title="' +
          self.options.labels.UNLOCK +
          '"><i class="fa fa-unlock muted"></i>' +
          rowNo +
          '</td>'
      )
      .appendTo(self.firstColumnTopCell.find('tbody'));
    $newTr.find('td').on('click', function() {
      unlock($(this));
    });
    self.lockedRows['r' + rowNo] = {
      row: $clone,
      cell: $newTr
    };
  } else {
    self.lockedRows['r' + rowNo].row.appendTo(self.headerRowContainer.find('tbody'));
    self.lockedRows['r' + rowNo].cell.appendTo(self.firstColumnTopCell.find('tbody'));
    self.lockedRows['r' + rowNo].cell.find('td').on('click', function() {
      unlock($(this));
    });
  }
};

$.fn[PLUGIN_NAME] = function(options) {
  return this.each(function() {
    if ($.data(this, 'plugin_' + PLUGIN_NAME)) {
      $.data(this, 'plugin_' + PLUGIN_NAME).destroy();
    }
    $.data(this, 'plugin_' + PLUGIN_NAME, new Plugin(this, options));
  });
};
