// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/pagination
 */

var componentUtils = require('cloudera-ui/ko/components/componentUtils');
var i18n = require('cloudera-ui/utils/i18n');
var urlHash = require('cloudera-ui/utils/urlHash');
var ko = require('knockout');
var _ = require('_');

require('cloudera-ui/ko/bindings/selectpicker');

/**
 * How many pages we should show to the left or right of the selected page
 * if there are not enough pages to show on on side, we show extra pages
 * on other side
 */
var PAGINATION_PADDING = 2;

var ELLIPSIS = '...';

var PAGE_INDEX_HASH_KEY = 'pageIndex';

/**
 * Gets the current page index from the hash.
 * @return {number}
 */
function getCurrentPageHash() {
  return parseInt(urlHash.get(PAGE_INDEX_HASH_KEY));
}

/**
 * @type {number[]}
 */
var DEFAULT_PAGE_LENGTHS = [10, 25, 50, 100];
var ALL_ROWS = 'all';

/**
 * @alias module:ko/components/pagination
 * @description Pagination control
 */
class PaginationComponent {

  /**
   * @param {function} params.onPaginationChange callback, called with page number on click.
   * @param {boolean} params.unknownSize Tells us that this pagination widget is used for a table of unknown length.
   * @param {ko.observable} params.pageLength The observable that corresponds to the page length.
   * @param {ko.observable} [params.tableSize] number records in the table, if known. Should be the current size.
   * @param {number} [params.pageIndex] The current page to select. Defaults to the page hash or 1.
   * @param {boolean} [params.showAll] If we want to allow fetching all rows.
   * @param {number[]} [params.pageLengths] The list of page lengths. Defaults to [10,25,50].
   * Defaults to the first value in the pageLengths array.
   * @param {number} [params.paginationPadding] The number of pages to disply around the current page. Defaults to 2.
   * @param {boolean} [params.updateUrl] Whether to update the url using a hash. Defaults to false.
   */
  constructor(params) {
    this.onPaginationChange = params.onPaginationChange;

    // constant referenced in the component template
    this.ELLIPSIS = ELLIPSIS;

    this.updateUrl = !!params.updateUrl;

    // start on page 1 by default.
    var pageHash = this.updateUrl ? getCurrentPageHash() : undefined;
    var foundPageIndex = params.pageIndex || pageHash || 1;

    /**
     * Read-write observable
     * Internal page index that is determined by the current url hash.
     * @type {number}
     */
    this.pageIndex = ko.observable(foundPageIndex);

    this.pageLengths = params.pageLengths || DEFAULT_PAGE_LENGTHS;

    // todo, figure out user preferences to save the selected rows per page.
    this.pageLength = ko.computed({
      read: function() {
        return ko.unwrap(params.pageLength || this.pageLengths[0]);
      },
      write: function(val) {
        if (ko.isObservable(params.pageLength)) {
          params.pageLength(val);
        }

        if (this.updateUrl) {
          urlHash.set(PAGE_INDEX_HASH_KEY, undefined);
        }
      }
    }, this);

    if (params.showAll) {
      this.pageLengths.push(ALL_ROWS);
    }

    this.unknownSize = ko.pureComputed(function() {
      return ko.unwrap(params.unknownSize);
    });

    /**
     * Read-only observable
     * Store the table size. If size is unknown, then we display pagination differently.
     * @type {number}
     */
    this.tableSize = ko.pureComputed(function() {
      return ko.unwrap(params.tableSize);
    });

    if (ko.isObservable(params.tableSize)) {
      params.tableSize.subscribe(function(size) {
      }, this);
    }

    /**
     * Read-only computed
     * Determines the maxiumum number of pages to show based on the table size
     * and the rows per page.
     */
    this.pageCount = ko.pureComputed(function() {
      var tableSize = this.tableSize();
      var pageLength = this.pageLength();
      if (this.unknownSize()) {
        // if we don't know how many pages to display, then return the current page index.
        return this.pageIndex();
      }

      var count = Math.ceil(tableSize / pageLength);
      return count;
    }, this);

    /**
     * Make sure we always have the max page item selected if our table count changes.
     */
    this.pageCount.subscribe(function(count) {
      var pageIndex = this.pageIndex();
      if (pageIndex > count) {
        this.pageIndex(count);
      }
    }, this);

    /**
     * Read-only observable
     * Shows the current range of rows you are viewing.
     * @type {string}
     */
    this.currentDisplayedRange = ko.pureComputed(function() {
      var current = this.pageIndex();
      var pageLength = this.pageLength();
      var min = ((current - 1) * pageLength) + 1;
      var size = this.tableSize();
      var max = Math.min(current * pageLength, size || Infinity);
      var displaying;
      if (this.unknownSize()) {
        if (min === max) {
          displaying = i18n.t('ko.components.pagination.displayX.unknown', min);
        } else {
          displaying = i18n.t('ko.components.pagination.displayXtoY.unknown', min, max);
        }
      } else {
        if (min === max) {
          displaying = i18n.t('ko.components.pagination.displayX.known', min, size);
        } else {
          displaying = i18n.t('ko.components.pagination.displayXtoY.known', min, max, size);
        }
      }

      return displaying;
    }, this);

    /**
     * Padding that indicates how many items around the current pagination element we want to show.
     * If padding is 1 and you are at item 27, we display:
     * 1 ... 26 27 28 ... N
     * If padding is 2 and you are at item 27, we display:
     * 1 ... 25 26 27 28 29 ... N
     * @type {number}
     */
    var paginationPadding = params.paginationPadding || PAGINATION_PADDING;

    /**
     * Read-only observable
     * Hides the entire component when there is only one page.
     * @type {boolean}
     */
    this.isVisible = ko.pureComputed(function() {
      if (this.unknownSize()) {
        // show the pagination widget if we don't know the max number of rows
        return true;
      }

      return this.pageCount() > 1;
    }, this);

    /**
     * Read-only observable
     * Shows the 'go to first' page arrow (<) when you are not on the first page.
     * @type {boolean}
     */
    this.isPreviousVisible = ko.pureComputed(function() {
      if (this.unknownSize()) {
        // if we don't know how big the table is, then we don't show the previous button.
        return false;
      }

      return this.pageIndex() > 1;
    }, this);

    /**
     * Read-only observable
     * Shows the 'go to last' page arrow (>) when you are not on the last page.
     * @type {boolean}
     */
    this.isNextVisible = ko.pureComputed(function() {
      if (this.unknownSize()) {
        // if we don't know how big the table is, then we always show a next button
        return true;
      }

      return this.pageIndex() < this.pageCount();
    }, this);

    /**
     * Read-only observable
     * Enumerates the pagination values to display.  Including ellipsis.
     * @type {string[]}
     */
    this.paginationValues = ko.pureComputed(function() {

      var index = this.pageIndex();
      var pageCount = this.pageCount();

      if (pageCount === 1 && this.unknownSize()) {
        return [1, ELLIPSIS];
      }

      if (pageCount < 2) {
        return [];
      }

      var values = [], i, padValue;

      // iterate from -padding to + padding, add values that are > 0 and < pageCount
      for (i = -paginationPadding; i < paginationPadding + 1; i++) {
        padValue = index + i;
        if (padValue > 0 && padValue <= pageCount) {
          values.push(padValue);
        }
      }

      // add the first page index if our range doesn't include it
      if (index - paginationPadding > 1) {
        // add an ellipsis if index is far away from the first value
        if (index - paginationPadding > paginationPadding) {
          values.unshift(ELLIPSIS);
        }

        values.unshift(1);
      }

      // add the last page index if our range doesn't include it
      if (index + paginationPadding < pageCount) {
        // add an ellipsis if index is far away from the last value
        if (index + paginationPadding < pageCount - 1) {
          values.push(ELLIPSIS);
        }

        values.push(pageCount);
      }

      // show an ellipsis for unknown sized tables so you know it doesn't have a max size
      if (this.unknownSize()) {
        values.push(ELLIPSIS);
      }

      return values;
    }, this);

  }

  /**
   * Handles the pagination state change on click.
   * @param {string} pageIndex The index you clicked, or the index of the left or right arrow.
   * @private
   */
  _changePage(pageIndex) {
    var _this = this;
    var index = parseInt(pageIndex);

    /**
     * onPaginationChange is called with pageIndex, pageLength, and a done callback.
     * onPagination's job is to invoke an API request, then signal back to the pagination component to refresh on success.
     */
    this.onPaginationChange(index, this.pageLength(), function onDone(itemsSoFar) {
      // don't update the unknown table because the list didn't grow.
      if (_this.unknownSize() && itemsSoFar === _this.tableSize()) {
        return;
      }

      _this.pageIndex(index);
      if (_this.updateUrl) {
        urlHash.set(PAGE_INDEX_HASH_KEY, index);
      }
    });
  }

  /**
   * Goes to a specific page.
   * @param {number} pageNum The clicked page number.
   * @private
   */
  gotoPage(pageNum) {
    if (!isNaN(pageNum)) {
      this._changePage(pageNum);
    }
  }

  /**
   * Invokes the action specified for the right arrow.
   */
  gotoNext() {
    this._changePage(this.pageIndex() + 1);
  }

  /**
   * Invokes the action specified for the left arrow.
   */
  gotoPrevious() {
    this._changePage(this.pageIndex() - 1);
  }

  /**
   * Shows a number, or i18n translated "All Rows"
   * @return {string|number}
   */
  pageCountText(value) {
    var returnValue = value;
    if (value === ALL_ROWS) {
      returnValue = i18n.t('ko.components.pagination.allRows');
    }

    return returnValue;
  }
}

var template = `
<div class="cui-pagination">
  <span class="cui-pagination-current-range" data-bind="text: currentDisplayedRange"></span>

  <ul class="pagination">

    <li data-bind="visible: isPreviousVisible">
      <a href="#" aria-label="${i18n.t('ko.components.pagination.aria.previous')}" data-bind="click: gotoPrevious">
        <span aria-hidden="true">&lt;</span>
      </a>
    </li>
    <!-- ko foreach: {data: paginationValues, as: 'pageValue' } -->
    <li data-bind="css: {active: pageValue === $parent.pageIndex()}">
      <!-- ko if: pageValue === $component.ELLIPSIS -->
      &hellip;
      <!-- /ko -->

      <!-- ko if: pageValue !== $component.ELLIPSIS && pageValue === $parent.pageIndex() -->
      <span data-bind="text: $data"></span>
      <!-- /ko -->

      <!-- ko if: pageValue !== $component.ELLIPSIS && pageValue !== $parent.pageIndex() -->
      <a href="#" data-bind="text: pageValue, click: function() { $component.gotoPage($data); }"></a>
      <!-- /ko -->
    </li>
    <!-- /ko -->

    <li data-bind="visible: isNextVisible">
      <a href="#" aria-label="${i18n.t('ko.components.pagination.aria.next')}" data-bind="click: gotoNext">
        <span aria-hidden="true">&gt;</span>
      </a>
    </li>
  </ul>

  <span class="cui-pagination-range-picker">
    <select data-bind="selectpicker: {width: 'fit'}, options: pageLengths, value: pageLength, optionsText: pageCountText">
    </select>
    <span>${i18n.t('ko.components.pagination.perPage')}</span>
  </span>
</div>
`;

componentUtils.addComponent(PaginationComponent, 'cui-pagination', template);

// expose this for others to use.
PaginationComponent.getCurrentPageHash = getCurrentPageHash;
PaginationComponent.PAGE_INDEX_HASH_KEY = PAGE_INDEX_HASH_KEY;

module.exports = PaginationComponent;
