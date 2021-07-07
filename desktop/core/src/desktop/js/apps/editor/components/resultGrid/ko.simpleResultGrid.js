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
import defer from 'utils/timing/defer';
import sleep from 'utils/timing/sleep';
import UUID from 'utils/string/UUID';
import {
  HIDE_FIXED_HEADERS_EVENT,
  REDRAW_FIXED_HEADERS_EVENT,
  SHOW_GRID_SEARCH_EVENT,
  SHOW_NORMAL_RESULT_EVENT
} from 'apps/editor/events';
import { trackResult } from 'apps/editor/components/executableStateHandler';
import { ExecutionStatus } from 'apps/editor/execution/sqlExecutable';

export const SIMPLE_RESULT_GRID_COMPONENT = 'simple-result-grid';

// prettier-ignore
const TEMPLATE = `
<div class="simple-result-grid" data-bind="delayedOverflow: 'slow'">
  <table class="table table-condensed resultTable">
    <thead>
    <tr data-bind="foreach: meta">
      <th class="sorting" data-bind="
          text: $index() === 0 ? '&nbsp;' : name,
          css: typeof cssClass !== 'undefined' ? cssClass : 'sort-string',
          attr: { title: type },
          style: {
            'width': $index() === 0 ? '1%' : '',
            'height': $index() === 0 ? '32px' : ''
          },
          click: function(obj, e) {
            $(e.target).parents('table').trigger('sort', obj);
          }
        "></th>
    </tr>
    </thead>
    <tbody>
    </tbody>
  </table>
  <div style="display:none;" data-bind="visible: isExpired && data() && data().length > 99">
    <pre class="margin-top-10"><i class="fa fa-check muted"></i> ${ I18n('Results have expired, rerun the query if needed.') }</pre>
  </div>
</div>
`;

class SimpleResultGrid extends DisposableComponent {
  constructor(params, element) {
    super();
    this.id = UUID();
    this.$element = $(element);

    this.activeExecutable = params.activeExecutable;

    this.scrollable = params.scrollable || element.parentElement;
    this.contained = typeof params.contained !== 'undefined' ? params.contained : true;
    this.resultGrayedOut = false;

    this.hasMore = ko.observable(false);
    this.status = ko.observable();
    this.meta = ko.observableArray();
    this.data = ko.observableArray();
    this.lastFetchedRows = ko.observableArray();

    // length > 99 comes from legacy code, likely related to data fetched twice.
    this.isExpired = ko.pureComputed(
      () => this.status() === ExecutionStatus.expired && this.data().length > 99
    );

    this.hueDatatable = undefined;

    const trackerHandler = trackResult(this.activeExecutable, result => {
      if (result) {
        this.status(result.executable.status);
        this.hasMore(result.hasMore);
        if (this.meta() !== result.koEnrichedMeta) {
          this.meta(result.koEnrichedMeta);
          this.data(result.lastRows);
        } else if (result.lastRows.length) {
          this.data.push(...result.lastRows);
        }
        this.lastFetchedRows(result.lastRows);
      } else {
        this.meta([]);
        this.data([]);
        this.hasMore(false);
        this.status(undefined);
        this.lastFetchedRows([]);
      }
    });

    this.addDisposalCallback(() => {
      trackerHandler.dispose();
    });

    this.subscribe(this.data, this.render.bind(this));

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

  createHueDatatable() {
    let invisibleRows = 10;
    if (this.data().length) {
      const colCount = this.data()[0].length;
      invisibleRows = colCount > 200 ? 10 : colCount > 30 ? 50 : 100;
    }
    const $datatablesWrapper = this.getWrapperElement();

    const hueDatatable = this.getResultTableElement().hueDataTable({
      i18n: {
        NO_RESULTS: I18n('No results found.'),
        OF: I18n('of')
      },
      fnDrawCallback: () => {
        const $resultTable = this.getResultTableElement();
        $('#queryResults').removeAttr('style');
        $datatablesWrapper.css('overflow-x', 'hidden');
        $resultTable.jHueHorizontalScrollbar();
        $datatablesWrapper.jHueScrollLeft();
      },
      scrollable: this.scrollable,
      contained: this.contained,
      forceInvisible: invisibleRows
    });

    this.disposals.push(() => {
      hueDatatable.fnDestroy();
    });

    defer(() => {
      const tableExtenderOptions = {
        mainScrollable: this.scrollable,
        fixedFirstColumn: true,
        parentId: this.id,
        clonedContainerPosition: 'fixed',
        app: 'editor'
      };
      this.getWrapperElement().css('overflow-x', 'hidden');
      const bannerTopHeight = window.BANNER_TOP_HTML ? 30 : 2;
      tableExtenderOptions.stickToTopPosition = 48 + bannerTopHeight;

      const $resultTable = this.getResultTableElement();

      $resultTable.jHueTableExtender2(tableExtenderOptions);
      this.disposals.push(() => {
        if ($resultTable.data('plugin_jHueTableExtender2')) {
          $resultTable.data('plugin_jHueTableExtender2').destroy();
        }
      });

      $resultTable.jHueHorizontalScrollbar();
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

    //const $dataTablesWrapper = $resultTable.parents('.dataTables_wrapper');

    const $scrollElement = $(this.scrollable);

    let scrollThrottle = -1;

    this.disposals.push(() => {
      window.clearTimeout(scrollThrottle);
    });

    let fetchingRows = false;
    const dataScroll = () => {
      if (!$resultTable.is(':visible')) {
        return;
      }

      let lastScrollPosition =
        $scrollElement.data('scrollPosition') != null ? $scrollElement.data('scrollPosition') : 0;
      window.clearTimeout(scrollThrottle);
      $scrollElement.data('scrollPosition', $scrollElement.scrollTop());
      scrollThrottle = window.setTimeout(async () => {
        lastScrollPosition--; //hack for forcing fetching
        if (
          lastScrollPosition !== $scrollElement.scrollTop() &&
          $scrollElement.scrollTop() + $scrollElement.outerHeight() + 20 >=
            $scrollElement[0].scrollHeight &&
          this.hueDatatable &&
          this.hasMore() &&
          !fetchingRows
        ) {
          this.showGrayedOutResult();
          fetchingRows = true;
          try {
            await this.fetchRows(100, false);
          } finally {
            this.showNormalResult();
            fetchingRows = false;
          }
        }
      }, 100);
    };

    $scrollElement.off('scroll.' + this.id);
    $scrollElement.on('scroll.' + this.id, dataScroll);
    this.disposals.push(() => {
      $scrollElement.off('scroll.' + this.id);
    });

    this.subscribe(REDRAW_FIXED_HEADERS_EVENT, this.redrawFixedHeaders.bind(this));

    this.subscribe(HIDE_FIXED_HEADERS_EVENT, this.hideFixedHeaders.bind(this));

    this.subscribe(SHOW_NORMAL_RESULT_EVENT, this.showNormalResult.bind(this));

    return this.hueDatatable;
  }

  async fetchRows() {
    if (this.activeExecutable() && this.activeExecutable().result) {
      await this.activeExecutable().result.fetchRows({ rows: 100 });
    }
  }

  getResultTableElement() {
    return this.$element.find('.resultTable');
  }

  getWrapperElement() {
    return this.$element.find('.dataTables_wrapper');
  }

  hideFixedHeaders() {
    const $component = this.$element;
    $component.find('.jHueTableExtenderClonedContainer').hide();
    $component.find('.jHueTableExtenderClonedContainerColumn').hide();
    $component.find('.jHueTableExtenderClonedContainerCell').hide();
    $component.find('.fixed-header-row').hide();
    $component.find('.fixed-first-cell').hide();
    $component.find('.fixed-first-column').hide();
  }

  showFixedHeaders() {
    const $component = this.$element;
    $component.find('.jHueTableExtenderClonedContainer').show();
    $component.find('.jHueTableExtenderClonedContainerColumn').show();
    $component.find('.jHueTableExtenderClonedContainerCell').show();
    $component.find('.fixed-header-row').show();
    $component.find('.fixed-first-cell').show();
    $component.find('.fixed-first-column').show();
  }

  redrawFixedHeaders() {
    if (this.meta().length > 0) {
      const tableExtender = this.getResultTableElement().data('plugin_jHueTableExtender2');
      if (tableExtender) {
        tableExtender.repositionHeader();
        tableExtender.drawLockedRows();
      }
      const $scrollable = $(this.scrollable);
      $scrollable.data('lastScroll', $scrollable.scrollTop());
      $scrollable.trigger('scroll');
    }
    this.showFixedHeaders();
  }

  async render() {
    if (this.data().length || this.lastFetchedRows().length) {
      await sleep(300);
      const $resultTable = this.getResultTableElement();
      const initial = !$resultTable.data('rendered');
      let dataTable;
      if (initial) {
        //this.$element.find('select').trigger('chosen:updated'); // TODO: Extract
        dataTable = this.createDatatable();
        $resultTable.data('rendered', true);
      } else {
        dataTable = $resultTable.hueDataTable();
      }
      try {
        dataTable.fnAddData(initial && this.data().length ? this.data() : this.lastFetchedRows());
      } catch (e) {}
      const $dataTablesWrapper = this.getWrapperElement();
      this.showNormalResult();
      $dataTablesWrapper.scrollTop($dataTablesWrapper.data('scrollPosition'));
    } else {
      this.showNormalResult();
    }
  }

  showGrayedOutResult() {
    if (this.resultGrayedOut) {
      return;
    }
    const $wrapper = this.getWrapperElement();
    $wrapper.find('.fixed-first-column').css({ opacity: '0' });
    $wrapper.find('.fixed-header-row').css({ opacity: '0' });
    $wrapper.find('.fixed-first-cell').css({ opacity: '0' });
    $wrapper.find('.resultTable').css({ opacity: '0.55' });
    this.resultGrayedOut = true;
  }

  showNormalResult() {
    if (!this.resultGrayedOut) {
      return;
    }
    const $wrapper = this.getWrapperElement();
    $wrapper.find('.fixed-first-column').css({ opacity: '1' });
    $wrapper.find('.fixed-header-row').css({ opacity: '1' });
    $wrapper.find('.fixed-first-cell').css({ opacity: '1' });
    $wrapper.find('.resultTable').css({ opacity: '1' });
    this.resultGrayedOut = false;
  }
}

componentUtils.registerComponent(
  SIMPLE_RESULT_GRID_COMPONENT,
  {
    createViewModel: (params, componentInfo) => new SimpleResultGrid(params, componentInfo.element)
  },
  TEMPLATE
);
