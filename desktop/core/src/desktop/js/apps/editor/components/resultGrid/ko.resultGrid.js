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
import * as ko from 'knockout';

import './ko.resultDownloadActions';

import componentUtils from 'ko/components/componentUtils';
import DisposableComponent from 'ko/components/DisposableComponent';
import I18n from 'utils/i18n';
import huePubSub from 'utils/huePubSub';
import defer from 'utils/timing/defer';
import sleep from 'utils/timing/sleep';
import {
  HIDE_FIXED_HEADERS_EVENT,
  REDRAW_FIXED_HEADERS_EVENT,
  SHOW_GRID_SEARCH_EVENT,
  SHOW_NORMAL_RESULT_EVENT
} from 'apps/editor/events';

import { attachTracker } from 'apps/editor/components/executableStateHandler';

export const RESULT_GRID_COMPONENT = 'result-grid';

// prettier-ignore
const TEMPLATE = `
<div class="snippet-tab-actions-append">
  <div class="btn-group">
    <button class="btn btn-editor btn-mini disable-feedback" data-bind="toggle: columnsVisible, css: { 'active' : columnsVisible }">
      <i class="fa fa-columns"></i> ${ I18n('Columns') }
    </button>
  </div>

  <!-- ko ifnot: streaming -->
  <div class="btn-group">
    <button class="btn btn-editor btn-mini disable-feedback" data-bind="click: showSearch.bind($data), css: { 'disabled': !data().length }">
      <i class="fa fa-search"></i> ${ I18n('Search') }
    </button>
  </div>
  <!-- /ko -->

  <!-- ko component: {
    name: 'result-download-actions',
    params: {
      activeExecutable: activeExecutable,
      meta: meta,
      data: data
    }
  } --><!-- /ko -->

  <!-- ko if: false && window.ENABLE_DOWNLOAD -->
    <div data-bind="
        component: {
          name: 'downloadSnippetResults',
          params: {
            gridSideBtn: false,
            snippet: $data,
            notebook: $parent
          }
        }
      " style="display:inline-block;"></div>
  <!-- /ko -->

  <!-- ko if: streaming -->
  <form autocomplete="off" class="inline-block">
    <input class="input-small search-input" style="margin-left: 10px;" type="text" ${ window.PREVENT_AUTOFILL_INPUT_ATTRS } placeholder="${ I18n('Live filter') }" data-bind="
        textInput: filter,
        clearable: filter
      "/>
  </form>
  <!-- /ko -->
</div>

<div class="split-result-container">
  <div class="result-settings-panel" style="display: none; height: auto; position:relative" data-bind="visible: columnsVisible">
    <div class="snippet-grid-settings" data-bind="delayedOverflow, stickVertical: { scrollContainer: MAIN_SCROLLABLE }">
      <table class="table table-condensed margin-top-10 no-border">
        <thead>
        <tr>
          <th width="16">
            <input class="all-meta-checked no-margin-top" type="checkbox" data-bind="
                enable: !isMetaFilterVisible() && filteredMeta().length,
                event: {
                  change: function() { toggleAllResultColumns($element); }
                },
                checked: filteredMetaChecked
              "/>
          </th>
          <th colspan="2" class="nav-header-like">
            <span class="meta-title pointer" data-bind="toggle: isMetaFilterVisible, attr: { title: filteredColumnCount }">${ I18n('columns')}</span>
            (<span class="meta-title pointer" data-bind="toggle: isMetaFilterVisible, text: filteredColumnCount"></span>)
            <span class="inactive-action" href="javascript:void(0)" data-bind="toggle: isMetaFilterVisible, css: { 'blue' : isMetaFilterVisible }"><i class="pointer fa fa-search" title="${ I18n('Search') }"></i></span>
          </th>
        </tr>
        <tr data-bind="visible: isMetaFilterVisible">
          <td colspan="3">
            <div class="context-popover-inline-autocomplete" style="display: block;">
              <!-- ko component: {
                name: 'inline-autocomplete',
                params: {
                  placeHolder: '${ I18n('Filter columns...') }',
                  querySpec: metaFilter,
                  facets: Object.keys(SQL_COLUMNS_KNOWN_FACET_VALUES),
                  knownFacetValues: SQL_COLUMNS_KNOWN_FACET_VALUES,
                  autocompleteFromEntries: autocompleteColumns.bind($data)
                }
              } --><!-- /ko -->
            </div>
          </td>
        </tr>
        </thead>
        <tbody class="unstyled filtered-meta" data-bind="foreach: filteredMeta">
        <tr data-bind="visible: name !== ''">
          <td><input class="no-margin-top" type="checkbox" data-bind="
              event: {
                change: function() { $parent.toggleResultColumn($element, originalIndex); }
              },
              checked: checked
            "/></td>
          <td><a class="pointer" data-bind="
              click: function() { $parent.scrollToResultColumn($element); },
              attr: { title: name + ' - ' + type }
            "><span data-bind="text: name"></span></a></td>
          <td><span data-bind="text: type" class="muted margin-left-20"></span></td>
        </tr>
        </tbody>
        <tfoot>
        <tr>
          <td colspan="3">
            <div class="margin-top-10 muted meta-noresults" data-bind="visible: !filteredMeta().length">
              ${ I18n('No columns found') }
            </div>
          </td>
        </tr>
        </tfoot>
      </table>
    </div>
  </div>

  <div class="split-result-resizer" style="display: none;" data-bind="
      visible: columnsVisible,
      splitFlexDraggable : {
        containerSelector: '.split-result-container',
        sidePanelSelector: '.result-settings-panel',
        sidePanelVisible: columnsVisible,
        orientation: 'left',
        appName: 'result_grid',
        onPosition: function() { redrawFixedHeaders(); }
      }
    "><div class="resize-bar"></div></div>

  <div class="split-result-content" data-bind="delayedOverflow: 'slow', css: resultsKlass">
    <table class="table table-condensed resultTable">
      <thead>
      <tr data-bind="foreach: meta">
        <th class="sorting" data-bind="
            text: ($index() == 0 ? '&nbsp;' : $data.name),
            css: typeof cssClass != 'undefined' ? cssClass : 'sort-string',
            attr: { title: $data.type },
            style: {
              'width': $index() == 0 ? '1%' : '',
              'height': $index() == 0 ? '32px' : ''
            },
            click: function(obj, e) { $(e.target).parents('table').trigger('sort', obj); }
          "></th>
      </tr>
      </thead>
      <tbody>
      </tbody>
    </table>
    <div style="display:none;" data-bind="
        visible: status() == 'expired' && data() && data().length > 99,
        css: resultsKlass
      ">
      <pre class="margin-top-10"><i class="fa fa-check muted"></i> ${ I18n("Results have expired, rerun the query if needed.") }</pre>
    </div>
  </div>
</div>
`;

const STREAMING_MAX_ROWS = 1000;

class ResultGrid extends DisposableComponent {
  constructor(params, element) {
    super();
    this.element = element;
    this.activeExecutable = params.activeExecutable;

    this.bottomExpanded = params.bottomExpanded;
    this.notebookMode = params.notebookMode;
    this.hasMore = params.hasMore;
    this.fetchResult = params.fetchResult;
    this.streaming = params.streaming;

    this.filter = ko.observable().extend({ throttle: 100 });

    this.filter.subscribe(filter => {
      if (this.hueDatatable) {
        this.hueDatatable.setFilter(filter);
      }
    });

    const trackedObservables = {
      columnsVisible: false,
      isMetaFilterVisible: false
    };

    this.status = params.status;
    this.columnsVisible = ko.observable(trackedObservables.columnsVisible);
    this.isMetaFilterVisible = ko.observable(trackedObservables.isMetaFilterVisible);
    this.metaFilter = ko.observable();
    this.resultsKlass = params.resultsKlass;
    this.meta = params.meta;
    this.data = params.data;
    this.lastFetchedRows = params.lastFetchedRows;

    const tracker = attachTracker(
      this.activeExecutable,
      RESULT_GRID_COMPONENT,
      this,
      trackedObservables
    );
    super.addDisposalCallback(tracker.dispose.bind(tracker));

    this.hueDatatable = undefined;

    this.subscribe(this.columnsVisible, () => {
      defer(this.redrawFixedHeaders.bind(this));
    });

    this.filteredMeta = ko.pureComputed(() => {
      if (!this.metaFilter() || this.metaFilter().query === '') {
        return this.meta();
      }

      return this.meta().filter(item => {
        const facets = this.metaFilter().facets;
        const isFacetMatch = !facets || Object.keys(facets).length === 0 || !facets['type']; // So far only type facet is used for SQL
        const isTextMatch = !this.metaFilter().text || this.metaFilter().text.length === 0;
        let match = true;

        if (!isFacetMatch) {
          match = !!facets['type'][item.type];
        }

        if (match && !isTextMatch) {
          match = this.metaFilter().text.every(
            text => item.name.toLowerCase().indexOf(text.toLowerCase()) !== -1
          );
        }
        return match;
      });
    });

    this.filteredMetaChecked = ko.pureComputed(() =>
      this.filteredMeta().some(item => typeof item.checked === 'undefined' || item.checked())
    );

    this.filteredColumnCount = ko.pureComputed(() => {
      if (!this.metaFilter() || this.metaFilter().query === '') {
        return this.meta().length - 1;
      }
      return this.filteredMeta().length;
    });

    this.subscribe(this.data, this.render.bind(this));

    this.subscribe(this.hasMore, val => {
      // Hive reports hasMore = true when there's actually no more results, this prevents the grid
      // from being grayed out after scroll as this.data doesn't change but this.hasMore does.
      if (!val) {
        this.showNormalResult();
      }
    });

    this.subscribe(this.meta, meta => {
      if (meta) {
        if (this.hueDatatable) {
          this.hueDatatable.fnDestroy();
          this.hueDatatable = undefined;
        }

        const $resultTable = this.getResultTableElement();
        if ($resultTable.data('plugin_jHueTableExtender2')) {
          $resultTable.data('plugin_jHueTableExtender2').destroy();
        }
        $resultTable.data('scrollToCol', null);
        $resultTable.data('scrollToRow', null);
        $resultTable.data('rendered', false);
        if ($resultTable.hasClass('dt')) {
          $resultTable.removeClass('dt');
          $resultTable.find('thead tr').empty();
          $resultTable.data('lockedRows', {});
        }
      }
    });

    this.disposals.push(() => {
      if (this.hueDatatable) {
        this.hueDatatable.fnDestroy();
      }
    });
  }

  autocompleteColumns(nonPartial, partial) {
    const result = [];
    const partialLower = partial.toLowerCase();
    this.meta().forEach(column => {
      if (column.name.toLowerCase().indexOf(partialLower) === 0) {
        result.push(nonPartial + partial + column.name.substring(partial.length));
      } else if (column.name.toLowerCase().indexOf('.' + partialLower) !== -1) {
        result.push(
          nonPartial +
            partial +
            column.name.substring(
              partial.length + column.name.toLowerCase().indexOf('.' + partialLower) + 1
            )
        );
      }
    });

    return result;
  }

  createHueDatatable() {
    const $resultTable = this.getResultTableElement();
    let datatablesMaxHeight = 330;
    let invisibleRows = 10;
    if (this.data().length) {
      const colCount = this.data()[0].length;
      invisibleRows = colCount > 200 ? 10 : colCount > 30 ? 50 : 100;
    }

    const hueDatatable = $resultTable.hueDataTable({
      i18n: {
        NO_RESULTS: I18n('No results found.'),
        OF: I18n('of')
      },
      fnDrawCallback: () => {
        const $resultTable = this.getResultTableElement();
        const $datatablesWrapper = $resultTable.parents('.dataTables_wrapper');
        if (!this.notebookMode()) {
          $('#queryResults').removeAttr('style');
          datatablesMaxHeight = $(window).height() - $resultTable.parent().offset().top - 40;
          $datatablesWrapper.css('overflow-x', 'hidden');
          $resultTable.jHueHorizontalScrollbar();
          $datatablesWrapper.jHueScrollLeft();
        } else if ($resultTable.data('fnDraws') === 1) {
          $datatablesWrapper.jHueTableScroller({
            maxHeight: datatablesMaxHeight,
            heightAfterCorrection: 0
          });
          this.disposals.push(() => {
            if ($datatablesWrapper.data('plugin_jHueTableScroller')) {
              $datatablesWrapper.data('plugin_jHueTableScroller').destroy();
            }
          });
        }
      },
      scrollable: this.notebookMode() ? '.dataTables_wrapper' : window.MAIN_SCROLLABLE,
      contained: this.notebookMode(),
      forceInvisible: invisibleRows
    });

    this.disposals.push(() => {
      hueDatatable.fnDestroy();
    });

    defer(() => {
      const $resultTable = this.getResultTableElement();

      const tableExtenderOptions = {
        mainScrollable: this.notebookMode() ? '.dataTables_wrapper' : window.MAIN_SCROLLABLE,
        fixedFirstColumn: !this.notebookMode(),
        parentId: $resultTable.parents('.snippet').attr('id'),
        clonedContainerPosition: this.notebookMode() ? 'absolute' : 'fixed',
        app: 'editor'
      };
      if (!this.notebookMode()) {
        $resultTable.parents('.dataTables_wrapper').css('overflow-x', 'hidden');
        const bannerTopHeight = window.BANNER_TOP_HTML ? 30 : 2;
        tableExtenderOptions.stickToTopPosition = 48 + bannerTopHeight;
      }

      $resultTable.jHueTableExtender2(tableExtenderOptions);

      this.disposals.push(() => {
        if ($resultTable.data('plugin_jHueTableExtender2')) {
          $resultTable.data('plugin_jHueTableExtender2').destroy();
        }
      });

      if (!this.notebookMode()) {
        $resultTable.jHueHorizontalScrollbar();
      }
    });

    return hueDatatable;
  }

  createDatatable() {
    const $resultTable = this.getResultTableElement();
    const $resultTableParent = $resultTable.parent();
    // When executing few columns -> many columns -> few columns we have to clear the style
    $resultTable.removeAttr('style');
    if ($resultTable.hasClass('table-huedatatable')) {
      $resultTable.removeClass('table-huedatatable');
      if ($resultTableParent.hasClass('dataTables_wrapper')) {
        $resultTable.unwrap();
      }
    }
    $resultTable.addClass('dt');

    this.hueDatatable = this.createHueDatatable($resultTable);
    if (this.filter()) {
      this.hueDatatable.setFilter(this.filter());
    }

    const $dataTablesWrapper = $resultTable.parents('.dataTables_wrapper');

    if (this.notebookMode()) {
      $dataTablesWrapper.on(
        'mousewheel.resultGrid DOMMouseScroll.resultGrid wheel.resultGrid',
        function (event) {
          if ($resultTable.closest('.results').css('overflow') === 'hidden') {
            return;
          }
          const originalEvent = event.originalEvent,
            _deltaX = originalEvent.wheelDeltaX || -originalEvent.deltaX,
            _deltaY = originalEvent.wheelDeltaY || -originalEvent.deltaY;
          this.scrollTop += -_deltaY / 2;
          this.scrollLeft += -_deltaX / 2;

          if (this.scrollTop === 0) {
            $('body')[0].scrollTop += -_deltaY / 3;
            $('html')[0].scrollTop += -_deltaY / 3; // for firefox
          }
          event.preventDefault();
        }
      );

      this.disposals.push(() => {
        $dataTablesWrapper.off('mousewheel.resultGrid DOMMouseScroll.resultGrid wheel.resultGrid');
      });
    }

    let $scrollElement = $dataTablesWrapper;
    if (!this.notebookMode()) {
      $scrollElement = $(window.MAIN_SCROLLABLE);
    }

    if ($scrollElement.data('scrollFnDtCreation')) {
      $scrollElement.off('scroll', $scrollElement.data('scrollFnDtCreation'));
    }

    let scrollThrottle = -1;

    this.disposals.push(() => {
      window.clearTimeout(scrollThrottle);
    });

    const dataScroll = () => {
      if (
        !$resultTable.is(':visible') ||
        (this.activeExecutable().result && this.activeExecutable().result.streaming)
      ) {
        return;
      }

      let lastScrollPosition =
        $scrollElement.data('scrollPosition') != null ? $scrollElement.data('scrollPosition') : 0;
      window.clearTimeout(scrollThrottle);
      $scrollElement.data('scrollPosition', $scrollElement.scrollTop());
      scrollThrottle = window.setTimeout(() => {
        if (!this.notebookMode()) {
          lastScrollPosition--; //hack for forcing fetching
        }
        if (
          lastScrollPosition !== $scrollElement.scrollTop() &&
          $scrollElement.scrollTop() + $scrollElement.outerHeight() + 20 >=
            $scrollElement[0].scrollHeight &&
          this.hueDatatable &&
          this.hasMore()
        ) {
          this.showGrayedOutResult();
          this.fetchResult(100, false);
        }
      }, 100);
    };

    $scrollElement.off('scroll.resultGrid');
    $scrollElement.on('scroll.resultGrid', dataScroll);
    this.disposals.push(() => {
      $scrollElement.off('scroll.resultGrid');
    });

    this.subscribe(this.columnsVisible, newValue => {
      if (newValue) {
        dataScroll();
      }
    });

    this.subscribe(REDRAW_FIXED_HEADERS_EVENT, this.redrawFixedHeaders.bind(this));

    this.subscribe(SHOW_GRID_SEARCH_EVENT, this.showSearch.bind(this));

    this.subscribe(HIDE_FIXED_HEADERS_EVENT, this.hideFixedHeaders.bind(this));

    this.subscribe(SHOW_NORMAL_RESULT_EVENT, this.showNormalResult.bind(this));

    return this.hueDatatable;
  }

  getSnippetElement() {
    return $(this.element).parents('.snippet');
  }

  getResultTableElement() {
    return this.getSnippetElement().find('.resultTable');
  }

  hideFixedHeaders() {
    const $snippet = this.getSnippetElement();
    $snippet.find('.jHueTableExtenderClonedContainer').hide();
    $snippet.find('.jHueTableExtenderClonedContainerColumn').hide();
    $snippet.find('.jHueTableExtenderClonedContainerCell').hide();
    $snippet.find('.fixed-header-row').hide();
    $snippet.find('.fixed-first-cell').hide();
    $snippet.find('.fixed-first-column').hide();
  }

  showFixedHeaders() {
    const $snippet = this.getSnippetElement();
    $snippet.find('.jHueTableExtenderClonedContainer').show();
    $snippet.find('.jHueTableExtenderClonedContainerColumn').show();
    $snippet.find('.jHueTableExtenderClonedContainerCell').show();
    $snippet.find('.fixed-header-row').show();
    $snippet.find('.fixed-first-cell').show();
    $snippet.find('.fixed-first-column').show();
  }

  redrawFixedHeaders() {
    const $snippet = this.getSnippetElement();
    if (this.meta().length > 0) {
      const tableExtender = $snippet.find('.resultTable').data('plugin_jHueTableExtender2');
      if (tableExtender) {
        tableExtender.repositionHeader();
        tableExtender.drawLockedRows();
      }
      $(window.MAIN_SCROLLABLE).data('lastScroll', $(window.MAIN_SCROLLABLE).scrollTop());
      $(window.MAIN_SCROLLABLE).trigger('scroll');
    }
    this.showFixedHeaders();
  }

  resizeToggleResultSettings(initial) {
    let $datatablesWrapper;
    const $snippet = this.getSnippetElement();
    if ($snippet.find('.resultTable').is(':visible')) {
      $datatablesWrapper = $snippet.find('.dataTables_wrapper');
    } else {
      $datatablesWrapper = $snippet.find('.chart:visible');
    }
    if ($datatablesWrapper.length === 0) {
      $datatablesWrapper = $snippet.find('.table-results');
    }
    $datatablesWrapper
      .parents('.snippet-body')
      .find('.toggle-result-settings')
      .css({
        height: $datatablesWrapper.height() - 30 + 'px',
        'line-height': $datatablesWrapper.height() - 30 + 'px'
      });
    if (initial) {
      $snippet.find('.result-settings').css({
        marginTop: 0
      });
      $snippet.find('.snippet-actions').css({
        marginTop: 0
      });
      huePubSub.publish('resize.leaflet.map');
    }
  }

  async render() {
    const $snippet = this.getSnippetElement();
    if (this.data().length || this.lastFetchedRows().length) {
      await sleep(300);
      const $resultTable = $snippet.find('.resultTable');
      const initial = !$resultTable.data('rendered');
      let dataTable;
      if (initial) {
        $snippet.find('select').trigger('chosen:updated');
        dataTable = this.createDatatable();
        $resultTable.data('rendered', true);
      } else {
        dataTable = this.hueDatatable;
      }
      try {
        dataTable.fnAddData(
          initial && this.data().length ? this.data() : this.lastFetchedRows(),
          undefined,
          ko.unwrap(this.streaming),
          STREAMING_MAX_ROWS
        );
      } catch (e) {}
      const $dataTablesWrapper = $snippet.find('.dataTables_wrapper');
      this.showNormalResult();
      $dataTablesWrapper.scrollTop($dataTablesWrapper.data('scrollPosition'));
      this.resizeToggleResultSettings(initial);
    } else {
      this.showNormalResult();
    }
    $snippet.find('select').trigger('chosen:updated');
    $snippet.find('.snippet-grid-settings').scrollLeft(0);
  }

  // TODO: Fix for multiple clicks
  scrollToResultColumn(linkElement) {
    const $resultTable = this.getResultTableElement();
    const searchText = $.trim($(linkElement).text());
    const foundColumn = $resultTable.find('th').filter(function () {
      return $.trim($(this).text()) === searchText;
    });
    $resultTable.find('.columnSelected').removeClass('columnSelected');
    const selectedColumn = $resultTable.find('tr th:nth-child(' + (foundColumn.index() + 1) + ')');
    if (selectedColumn.length > 0) {
      $resultTable
        .find('tr td:nth-child(' + (foundColumn.index() + 1) + ')')
        .addClass('columnSelected');
      $resultTable
        .parent()
        .scrollLeft(
          selectedColumn.position().left +
            $resultTable.parent().scrollLeft() -
            $resultTable.parent().offset().left -
            30
        );
      $resultTable.data('scrollToCol', foundColumn.index());
      $resultTable.data('scrollToRow', null);
      $resultTable.data('scrollAnimate', true);
      $resultTable.parent().trigger('scroll');
    }
  }

  showGrayedOutResult() {
    const $wrapper = this.getSnippetElement().find('.dataTables_wrapper');
    $wrapper.find('.fixed-first-column').css({ opacity: '0' });
    $wrapper.find('.fixed-header-row').css({ opacity: '0' });
    $wrapper.find('.fixed-first-cell').css({ opacity: '0' });
    $wrapper.find('.resultTable').css({ opacity: '0.55' });
  }

  showNormalResult() {
    const $wrapper = this.getSnippetElement().find('.dataTables_wrapper');
    $wrapper.find('.fixed-first-column').css({ opacity: '1' });
    $wrapper.find('.fixed-header-row').css({ opacity: '1' });
    $wrapper.find('.fixed-first-cell').css({ opacity: '1' });
    $wrapper.find('.resultTable').css({ opacity: '1' });
  }

  showSearch() {
    if (this.hueDatatable) {
      this.hueDatatable.fnShowSearch();
    }
  }

  toggleAllResultColumns(linkElement) {
    this.hueDatatable.fnToggleAllCols(linkElement.checked);
    this.hueDatatable.fnDraw();
    this.filteredMeta().forEach(item => {
      item.checked(linkElement.checked);
    });
  }

  toggleResultColumn(linkElement, index) {
    this.hueDatatable.fnSetColumnVis(index, linkElement.checked);
  }
}

componentUtils.registerComponent(
  RESULT_GRID_COMPONENT,
  {
    createViewModel: (params, componentInfo) => new ResultGrid(params, componentInfo.element)
  },
  TEMPLATE
);
