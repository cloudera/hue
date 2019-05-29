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
import Clipboard from 'clipboard';
import 'jquery-mousewheel';
import ko from 'knockout';
import 'ext/bootstrap-datepicker.min';
import 'ext/jquery.hotkeys';
import 'jquery/plugins/jquery.hdfstree';

import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import I18n from 'utils/i18n';
import sqlWorkerHandler from 'sql/sqlWorkerHandler';

window.Clipboard = Clipboard;

const HUE_PUB_SUB_EDITOR_ID =
  window.location.pathname.indexOf('notebook') > -1 ? 'notebook' : 'editor';

huePubSub.subscribe('app.dom.loaded', app => {
  if (app === 'editor' || app === 'notebook') {
    window.MAIN_SCROLLABLE = '.page-content';

    let isLeftNavOpen = false;
    huePubSub.subscribe(
      'left.nav.open.toggle',
      val => {
        isLeftNavOpen = val;
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'split.panel.resized',
      () => {
        huePubSub.publish('recalculate.name.description.width');
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    const showHoverMsg = e => {
      let dt = null;
      if (e) {
        dt = e.dataTransfer;
      }
      if (
        !isLeftNavOpen &&
        (!dt ||
          (dt.types &&
            (dt.types.indexOf ? dt.types.indexOf('Files') !== -1 : dt.types.contains('Files'))))
      ) {
        $(window.EDITOR_BINDABLE_ELEMENT)
          .find('.hoverMsg')
          .removeClass('hide');
      }
    };

    const hideHoverMsg = vm => {
      if (vm.editorMode()) {
        $(window.EDITOR_BINDABLE_ELEMENT)
          .find('.hoverText')
          .html(I18n('Drop a SQL file here'));
      } else {
        $(window.EDITOR_BINDABLE_ELEMENT)
          .find('.hoverText')
          .html(I18n('Drop iPython/Zeppelin notebooks here'));
      }
      $(window.EDITOR_BINDABLE_ELEMENT)
        .find('.hoverMsg')
        .addClass('hide');
    };

    const createHueDatatable = (el, snippet, vm) => {
      let DATATABLES_MAX_HEIGHT = 330;
      let invisibleRows = 10;
      if (snippet.result && snippet.result.data() && snippet.result.data().length) {
        const cols = snippet.result.data()[0].length;
        invisibleRows = cols > 200 ? 10 : cols > 30 ? 50 : 100;
      }
      const _dt = $(el).hueDataTable({
        i18n: {
          NO_RESULTS: I18n('No results found.'),
          OF: I18n('of')
        },
        fnDrawCallback: function(oSettings) {
          if (vm.editorMode()) {
            $('#queryResults').removeAttr('style');
            DATATABLES_MAX_HEIGHT =
              $(window).height() -
              $(el)
                .parent()
                .offset().top -
              40;
            $(el)
              .parents('.dataTables_wrapper')
              .css('overflow-x', 'hidden');
            $(el).jHueHorizontalScrollbar();
            $(el)
              .parents('.dataTables_wrapper')
              .jHueScrollLeft();
          } else if ($(el).data('fnDraws') === 1) {
            $(el)
              .parents('.dataTables_wrapper')
              .jHueTableScroller({
                maxHeight: DATATABLES_MAX_HEIGHT,
                heightAfterCorrection: 0
              });
          }
        },
        scrollable:
          vm.editorMode() && !vm.isPresentationMode()
            ? window.MAIN_SCROLLABLE
            : '.dataTables_wrapper',
        contained: !vm.editorMode() || vm.isPresentationMode(),
        forceInvisible: invisibleRows
      });

      window.setTimeout(() => {
        if (vm.editorMode()) {
          $(el)
            .parents('.dataTables_wrapper')
            .css('overflow-x', 'hidden');
          const bannerTopHeight = window.BANNER_TOP_HTML ? 30 : 2;
          $(el).jHueTableExtender2({
            mainScrollable: window.MAIN_SCROLLABLE,
            fixedFirstColumn: vm.editorMode(),
            stickToTopPosition: 48 + bannerTopHeight,
            parentId: 'snippet_' + snippet.id(),
            clonedContainerPosition: 'fixed',
            app: 'editor'
          });
          $(el).jHueHorizontalScrollbar();
        } else {
          $(el).jHueTableExtender2({
            mainScrollable: $(el).parents('.dataTables_wrapper')[0],
            fixedFirstColumn: vm.editorMode(),
            parentId: 'snippet_' + snippet.id(),
            clonedContainerPosition: 'absolute',
            app: 'editor'
          });
        }
      }, 0);

      return _dt;
    };

    const createDatatable = (el, snippet, vm) => {
      const parent = $(el).parent();
      // When executing few columns -> many columns -> few columns we have to clear the style
      $(el).removeAttr('style');
      if ($(el).hasClass('table-huedatatable')) {
        $(el).removeClass('table-huedatatable');
        if (parent.hasClass('dataTables_wrapper')) {
          $(el).unwrap();
        }
      }
      $(el).addClass('dt');

      const _dt = createHueDatatable(el, snippet, vm);

      const dataTableEl = $(el).parents('.dataTables_wrapper');

      if (!vm.editorMode()) {
        dataTableEl.bind('mousewheel DOMMouseScroll wheel', function(e) {
          if (
            $(el)
              .closest('.results')
              .css('overflow') === 'hidden'
          ) {
            return;
          }
          const _e = e.originalEvent,
            _deltaX = _e.wheelDeltaX || -_e.deltaX,
            _deltaY = _e.wheelDeltaY || -_e.deltaY;
          this.scrollTop += -_deltaY / 2;
          this.scrollLeft += -_deltaX / 2;

          if (this.scrollTop === 0) {
            $('body')[0].scrollTop += -_deltaY / 3;
            $('html')[0].scrollTop += -_deltaY / 3; // for firefox
          }
          e.preventDefault();
        });
      }

      let _scrollTimeout = -1;

      let scrollElement = dataTableEl;
      if (vm.editorMode()) {
        scrollElement = $(window.MAIN_SCROLLABLE);
      }

      if (scrollElement.data('scrollFnDtCreation')) {
        scrollElement.off('scroll', scrollElement.data('scrollFnDtCreation'));
      }

      let resultFollowTimeout = -1;
      const dataScroll = function() {
        if (vm.editorMode()) {
          const snippetEl = $('#snippet_' + snippet.id());
          if (snippetEl.find('.dataTables_wrapper').length > 0 && snippet.showGrid()) {
            window.clearTimeout(resultFollowTimeout);
            resultFollowTimeout = window.setTimeout(() => {
              const topCoord = vm.isPresentationMode() || vm.isResultFullScreenMode() ? 50 : 73;
              let offsetTop = 0;
              if (
                snippetEl.find('.dataTables_wrapper').length > 0 &&
                snippetEl.find('.dataTables_wrapper').offset()
              ) {
                offsetTop = (snippetEl.find('.dataTables_wrapper').offset().top - topCoord) * -1;
              }
              let margin = Math.max(offsetTop, 0);
              if (window.BANNER_TOP_HTML) {
                margin += 31;
              }
              if (snippet.isResultSettingsVisible()) {
                snippetEl.find('.snippet-grid-settings').css({
                  height:
                    vm.isPresentationMode() || !vm.editorMode()
                      ? '330px'
                      : Math.max(
                          100,
                          Math.ceil(
                            $(window).height() - Math.max($('#queryResults').offset().top, topCoord)
                          )
                        ) + 'px'
                });
                snippetEl.find('.result-settings').css({
                  marginTop: margin
                });
              }
              snippetEl.find('.snippet-actions').css({
                marginTop: margin + 25
              });
            }, 100);
          }
        }
        if (
          !vm.editorMode() ||
          (vm.editorMode() && snippet.currentQueryTab() === 'queryResults' && snippet.showGrid())
        ) {
          let _lastScrollPosition =
            scrollElement.data('scrollPosition') != null ? scrollElement.data('scrollPosition') : 0;
          window.clearTimeout(_scrollTimeout);
          scrollElement.data('scrollPosition', scrollElement.scrollTop());
          _scrollTimeout = window.setTimeout(() => {
            if (vm.editorMode()) {
              _lastScrollPosition--; //hack for forcing fetching
            }
            if (
              _lastScrollPosition !== scrollElement.scrollTop() &&
              scrollElement.scrollTop() + scrollElement.outerHeight() + 20 >=
                scrollElement[0].scrollHeight &&
              _dt &&
              snippet.result.hasMore()
            ) {
              huePubSub.publish('editor.snippet.result.gray', snippet);
              snippet.fetchResult(100, false);
            }
          }, 100);
        }
      };
      scrollElement.data('scrollFnDtCreation', dataScroll);
      scrollElement.on('scroll', dataScroll);
      snippet.isResultSettingsVisible.subscribe(newValue => {
        if (newValue) {
          dataScroll();
        }
      });

      huePubSub.subscribeOnce('chart.hard.reset', () => {
        // hard reset once the default opened chart
        const oldChartX = snippet.chartX();
        snippet.chartX(null);
        window.setTimeout(() => {
          snippet.chartX(oldChartX);
        }, 0);
      });

      return _dt;
    };

    if (ko.options) {
      ko.options.deferUpdates = true;
    }

    let viewModel;

    const hideFixedHeaders = function() {
      $('.jHueTableExtenderClonedContainer').hide();
      $('.jHueTableExtenderClonedContainerColumn').hide();
      $('.jHueTableExtenderClonedContainerCell').hide();
      $('.fixed-header-row').hide();
      $('.fixed-first-cell').hide();
      $('.fixed-first-column').hide();
    };

    window.hideFixedHeaders = hideFixedHeaders;

    let redrawTimeout = -1;
    const redrawFixedHeaders = function(timeout) {
      const renderer = function() {
        if (!viewModel.selectedNotebook()) {
          return;
        }
        viewModel
          .selectedNotebook()
          .snippets()
          .forEach(snippet => {
            if (snippet.result.meta().length > 0) {
              const tableExtender = $('#snippet_' + snippet.id() + ' .resultTable').data(
                'plugin_jHueTableExtender2'
              );
              if (typeof tableExtender !== 'undefined') {
                tableExtender.repositionHeader();
                tableExtender.drawLockedRows();
              }
              $(window.MAIN_SCROLLABLE).data('lastScroll', $(window.MAIN_SCROLLABLE).scrollTop());
              $(window.MAIN_SCROLLABLE).trigger('scroll');
            }
          });
        $('.jHueTableExtenderClonedContainer').show();
        $('.jHueTableExtenderClonedContainerColumn').show();
        $('.jHueTableExtenderClonedContainerCell').show();
        $('.fixed-header-row').show();
        $('.fixed-first-cell').show();
        $('.fixed-first-column').show();
      };

      if (timeout) {
        window.clearTimeout(redrawTimeout);
        redrawTimeout = window.setTimeout(renderer, timeout);
      } else {
        renderer();
      }
    };
    window.redrawFixedHeaders = redrawFixedHeaders;

    const replaceAce = content => {
      const snip = viewModel.selectedNotebook().snippets()[0];
      if (snip) {
        snip.statement_raw(content);
        snip.result.statements_count(1);
        snip.ace().setValue(content, 1);
        snip.result.statement_range({
          start: {
            row: 0,
            column: 0
          },
          end: {
            row: 0,
            column: 0
          }
        });
        snip.ace()._emit('focus');
      }
      hideHoverMsg(viewModel);
      redrawFixedHeaders(200);
    };
    window.replaceAce = replaceAce;

    // Drag and drop iPython / Zeppelin notebooks
    if (window.FileReader) {
      let aceChecks = 0;

      const addAce = (content, snippetType) => {
        const snip = viewModel
          .selectedNotebook()
          .addSnippet({ type: snippetType, result: {} }, true);
        snip.statement_raw(content);
        aceChecks++;
        snip.checkForAce = window.setInterval(() => {
          if (snip.ace()) {
            window.clearInterval(snip.checkForAce);
            aceChecks--;
            if (aceChecks === 0) {
              hideHoverMsg(viewModel);
              redrawFixedHeaders(200);
            }
          }
        }, 100);
      };

      const addMarkdown = content => {
        const snip = viewModel
          .selectedNotebook()
          .addSnippet({ type: 'markdown', result: {} }, true);
        snip.statement_raw(content);
      };

      const addPySpark = content => {
        addAce(content, 'pyspark');
      };

      const addSql = content => {
        addAce(content, 'hive');
      };

      const addScala = content => {
        addAce(content, 'spark');
      };

      const parseExternalJSON = raw => {
        try {
          if (viewModel.editorMode()) {
            replaceAce(raw);
          } else {
            const loaded = typeof raw == 'string' ? JSON.parse(raw) : raw;
            if (loaded.nbformat) {
              //ipython
              let cells = [];
              if (loaded.nbformat === 3) {
                cells = loaded.worksheets[0].cells;
              } else if (loaded.nbformat === 4) {
                cells = loaded.cells;
              }
              cells.forEach((cell, cellCnt) => {
                window.setTimeout(() => {
                  if (cell.cell_type === 'code') {
                    if (loaded.nbformat === 3) {
                      addPySpark($.isArray(cell.input) ? cell.input.join('') : cell.input);
                    } else {
                      addPySpark($.isArray(cell.source) ? cell.source.join('') : cell.source);
                    }
                  }
                  if (cell.cell_type === 'heading') {
                    let heading = $.isArray(cell.source) ? cell.source.join('') : cell.source;
                    if (cell.level === 1) {
                      heading += '\n====================';
                    } else if (cell.level === 2) {
                      heading += '\n--------------------';
                    } else {
                      heading = '### ' + heading;
                    }
                    addMarkdown(heading);
                  }
                  if (cell.cell_type === 'markdown') {
                    addMarkdown($.isArray(cell.source) ? cell.source.join('') : cell.source);
                  }
                  if (cellCnt === cells.length - 1 && aceChecks === 0) {
                    hideHoverMsg(viewModel);
                  }
                }, 10);
              });
            }

            if (loaded.paragraphs) {
              //zeppelin
              if (loaded.name) {
                viewModel.selectedNotebook().name(loaded.name);
              }
              loaded.paragraphs.forEach(paragraph => {
                if (paragraph.text) {
                  const content = paragraph.text.split('\n');
                  if (content[0].indexOf('%md') > -1) {
                    content.shift();
                    addMarkdown(content.join('\n'));
                  } else if (content[0].indexOf('%sql') > -1 || content[0].indexOf('%hive') > -1) {
                    content.shift();
                    addSql(content.join('\n'));
                  } else if (content[0].indexOf('%pyspark') > -1) {
                    content.shift();
                    addPySpark(content.join('\n'));
                  } else {
                    if (content[0].indexOf('%spark') > -1) {
                      content.shift();
                    }
                    addScala(content.join('\n'));
                  }
                }
              });
            }
          }
        } catch (e) {
          hideHoverMsg(viewModel);
          replaceAce(raw);
        }
      };

      const handleFileSelect = function(evt) {
        evt.stopPropagation();
        evt.preventDefault();
        const dt = evt.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
          showHoverMsg();
        } else {
          hideHoverMsg(viewModel);
        }

        for (let i = 0, f; (f = files[i]); i++) {
          const reader = new FileReader();
          reader.onload = (function(file) {
            return function(e) {
              $('.hoverText').html("<i class='fa fa-spinner fa-spin'></i>");
              parseExternalJSON(e.target.result);
            };
          })(f);
          reader.readAsText(f);
        }
      };

      const handleDragOver = function(evt) {
        evt.stopPropagation();
        evt.preventDefault();
        evt.dataTransfer.dropEffect = 'copy';
      };

      const dropZone = $(window.EDITOR_BINDABLE_ELEMENT)[0];
      dropZone.addEventListener('dragenter', showHoverMsg, false);
      dropZone.addEventListener('dragover', handleDragOver, false);
      dropZone.addEventListener('drop', handleFileSelect, false);

      let isDraggingOverText = false;

      $(window.EDITOR_BINDABLE_ELEMENT)
        .find('.hoverText')
        .on('dragenter', e => {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          isDraggingOverText = true;
        });

      $(window.EDITOR_BINDABLE_ELEMENT)
        .find('.hoverText')
        .on('dragleave', e => {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();
          isDraggingOverText = false;
        });

      $(window.EDITOR_BINDABLE_ELEMENT)
        .find('.hoverMsg')
        .on('dragleave', e => {
          if (!isDraggingOverText) {
            hideHoverMsg(viewModel);
          }
        });
    }

    if (window.EDITOR_ENABLE_QUERY_SCHEDULING) {
      viewModel = new window.EditorViewModel(
        window.EDITOR_ID,
        window.NOTEBOOKS_JSON,
        window.EDITOR_VIEW_MODEL_OPTIONS,
        window.CoordinatorEditorViewModel,
        window.RunningCoordinatorModel
      );
    } else {
      viewModel = new window.EditorViewModel(
        window.EDITOR_ID,
        window.NOTEBOOKS_JSON,
        window.EDITOR_VIEW_MODEL_OPTIONS
      );
    }
    ko.applyBindings(viewModel, $(window.EDITOR_BINDABLE_ELEMENT)[0]);
    viewModel.init();

    sqlWorkerHandler.registerWorkers();

    viewModel.selectedNotebook.subscribe(newVal => {
      huePubSub.publish('selected.notebook.changed', newVal);
    });

    let wasResultFullScreenMode = false;
    let isAssistAvailable = viewModel.assistAvailable();
    let wasLeftPanelVisible = viewModel.isLeftPanelVisible();
    let wasRightPanelVisible = viewModel.isRightPanelVisible();

    const exitPlayerMode = () => {
      if (!wasResultFullScreenMode) {
        viewModel.selectedNotebook().isPresentationMode(false);
      } else {
        viewModel.isResultFullScreenMode(false);
      }
      wasResultFullScreenMode = false;
    };

    viewModel.isResultFullScreenMode.subscribe(newValue => {
      wasResultFullScreenMode = newValue;
      huePubSub.publish('editor.presentation.operate.toggle', newValue);
    });

    viewModel.isLeftPanelVisible.subscribe(value => {
      redrawFixedHeaders(200);
    });

    // Close the notebook snippets when leaving the page
    window.onbeforeunload = function(e) {
      if (!viewModel.selectedNotebook().avoidClosing) {
        viewModel.selectedNotebook().close();
      }
    };
    $(window).data('beforeunload', window.onbeforeunload);

    $('.preview-sample').css('right', 10 + hueUtils.scrollbarWidth() + 'px');

    const saveKeyHandler = () => {
      if (viewModel.canSave()) {
        viewModel.saveNotebook();
      } else {
        $('#saveAsModal' + window.EDITOR_SUFFIX).modal('show');
      }
    };

    const newKeyHandler = () => {
      if (!viewModel.editorMode()) {
        viewModel.selectedNotebook().newSnippet();
      } else {
        viewModel.newNotebook(
          viewModel.editorType(),
          null,
          viewModel.selectedNotebook()
            ? viewModel
                .selectedNotebook()
                .snippets()[0]
                .currentQueryTab()
            : null
        );
      }
    };

    const initKeydownBindings = () => {
      $(window).bind('keydown.editor', 'ctrl+s alt+s meta+s', e => {
        e.preventDefault();
        saveKeyHandler();
        return false;
      });
      $(window).bind('keydown.editor', 'ctrl+shift+p alt+shift+p meta+shift+p', e => {
        e.preventDefault();
        huePubSub.publish('editor.presentation.toggle');
        return false;
      });
      $(window).bind('keydown.editor', 'ctrl+e alt+e meta+e', e => {
        e.preventDefault();
        newKeyHandler();
        return false;
      });
    };

    if (document.location.href.indexOf('editor') >= 0) {
      initKeydownBindings();
    }

    $(document).bind('keyup', e => {
      if (
        e.keyCode === 191 &&
        e.shiftKey &&
        !$(e.target).is('input') &&
        !$(e.target).is('textarea')
      ) {
        $('#helpModal' + window.EDITOR_SUFFIX).modal('show');
      }

      if (
        e.keyCode === 191 &&
        !e.shiftKey &&
        !$(e.target).is('input') &&
        !$(e.target).is('textarea')
      ) {
        if (
          viewModel.editorMode() &&
          viewModel
            .selectedNotebook()
            .snippets()[0]
            .currentQueryTab() === 'queryResults'
        ) {
          e.preventDefault();
          const $t = $(
            '#snippet_' +
              viewModel
                .selectedNotebook()
                .snippets()[0]
                .id()
          ).find('.resultTable');
          $t.hueDataTable().fnShowSearch();
          return false;
        }
      }
    });

    let initialResizePosition = 100;

    const draggableHelper = (el, e, ui, setSize) => {
      const _snippet = ko.dataFor(el.parents('.snippet')[0]);
      const _cm = $('#snippet_' + _snippet.id()).data('editor');
      const _newSize = _snippet.aceSize() + (ui.offset.top - initialResizePosition);
      _cm.setSize('99%', _newSize);
      if (setSize) {
        _snippet.aceSize(_newSize);
      }
    };

    const getDraggableOptions = minY => {
      return {
        axis: 'y',
        start: function(e, ui) {
          initialResizePosition = ui.offset.top;
        },
        drag: function(e, ui) {
          draggableHelper($(this), e, ui);
          $('.jHueTableExtenderClonedContainer').hide();
          $('.jHueTableExtenderClonedContainerColumn').hide();
          $('.jHueTableExtenderClonedContainerCell').hide();
          $('.fixed-header-row').hide();
          $('.fixed-first-cell').hide();
          $('.fixed-first-column').hide();
        },
        stop: function(e, ui) {
          $('.jHueTableExtenderClonedContainer').show();
          $('.jHueTableExtenderClonedContainerColum').show();
          $('.jHueTableExtenderClonedContainerCell').show();
          $('.fixed-header-row').show();
          $('.fixed-first-cell').show();
          $('.fixed-first-column').show();
          draggableHelper($(this), e, ui, true);
          redrawFixedHeaders();
          ui.helper.first().removeAttr('style');
        },
        containment: [0, minY, 4000, minY + 400]
      };
    };

    $('.resize-panel a').each(function() {
      $(this).draggable(
        getDraggableOptions(
          $(this)
            .parents('.snippet')
            .offset().top + 128
        )
      );
    });

    const resetResultsResizer = snippet => {
      const $snippet = $('#snippet_' + snippet.id());
      $snippet
        .find('.table-results .column-side')
        .width(hueUtils.bootstrapRatios.span3() + '%')
        .data('newWidth', hueUtils.bootstrapRatios.span3());
      if (snippet.isResultSettingsVisible()) {
        $snippet
          .find('.table-results .grid-side')
          .data('newWidth', hueUtils.bootstrapRatios.span9())
          .width(hueUtils.bootstrapRatios.span9() + '%');
      } else {
        $snippet
          .find('.table-results .grid-side')
          .data('newWidth', 100)
          .width('100%');
      }
      $snippet.find('.resize-bar').css('left', '');
      try {
        $snippet.find('.resize-bar').draggable('destroy');
      } catch (e) {}

      let initialPosition = 0;

      $snippet.find('.resize-bar').draggable({
        axis: 'x',
        containment: $snippet.find('.table-results'),
        create: function() {
          const $snip = $('#snippet_' + snippet.id());
          initialPosition = $snip.find('.resize-bar').position().left;
          $snip
            .find('.table-results .column-side')
            .data('newWidth', hueUtils.bootstrapRatios.span3());
          $snip.find('.meta-filter').width($snip.find('.table-results .column-side').width() - 28);
        },
        drag: function(event, ui) {
          const $snip = $('#snippet_' + snippet.id());
          if (initialPosition === 0) {
            initialPosition = $snip.find('.resize-bar').position().left;
          }
          ui.position.left = Math.max(150, ui.position.left);
          const newSpan3Width =
            (ui.position.left * hueUtils.bootstrapRatios.span3()) / initialPosition;
          const newSpan9Width = 100 - newSpan3Width - hueUtils.bootstrapRatios.margin();
          $snip
            .find('.table-results .column-side')
            .width(newSpan3Width + '%')
            .data('newWidth', newSpan3Width);
          $snip
            .find('.table-results .grid-side')
            .width(newSpan9Width + '%')
            .data('newWidth', newSpan9Width);
          $snip.find('.meta-filter').width($snip.find('.table-results .column-side').width() - 28);
        },
        stop: function() {
          redrawFixedHeaders();
          huePubSub.publish('resize.leaflet.map');
        }
      });
    };

    const resizeToggleResultSettings = (snippet, initial) => {
      let _dtElement;
      const $snip = $('#snippet_' + snippet.id());
      if (snippet.showGrid()) {
        _dtElement = $snip.find('.dataTables_wrapper');
        const topCoord =
          viewModel.isPresentationMode() || viewModel.isResultFullScreenMode()
            ? window.BANNER_TOP_HTML
              ? 31
              : 1
            : 73;
        $snip.find('.snippet-grid-settings').css({
          height:
            viewModel.isPresentationMode() || !viewModel.editorMode()
              ? '330px'
              : Math.ceil(
                  $(window).height() -
                    Math.max(
                      $('.result-settings').length > 0 ? $('.result-settings').offset().top : 0,
                      topCoord
                    )
                ) + 'px'
        });
      } else {
        _dtElement = $snip.find('.chart:visible');
      }
      if (_dtElement.length === 0) {
        _dtElement = $snip.find('.table-results');
      }
      _dtElement
        .parents('.snippet-body')
        .find('.toggle-result-settings')
        .css({
          height: _dtElement.height() - 30 + 'px',
          'line-height': _dtElement.height() - 30 + 'px'
        });
      if (initial) {
        $snip.find('.result-settings').css({
          marginTop: 0
        });
        $snip.find('.snippet-actions').css({
          marginTop: 0
        });
        huePubSub.publish('resize.leaflet.map');
      }
    };

    const forceChartDraws = initial => {
      if (viewModel.selectedNotebook()) {
        viewModel
          .selectedNotebook()
          .snippets()
          .forEach(snippet => {
            if (snippet.result.data().length > 0) {
              let _elCheckerInterval = -1;
              const _el = $('#snippet_' + snippet.id());
              _elCheckerInterval = window.setInterval(() => {
                if (_el.find('.resultTable').length > 0) {
                  try {
                    resizeToggleResultSettings(snippet, initial);
                    resetResultsResizer(snippet);
                    $(document).trigger('forceChartDraw', snippet);
                  } catch (e) {}
                  window.clearInterval(_elCheckerInterval);
                }
              }, 200);
            }
          });
      }
    };

    forceChartDraws(true);

    // ======== PubSub ========

    let splitDraggableTimeout = -1;
    huePubSub.subscribe(
      'split.draggable.position',
      () => {
        window.clearTimeout(splitDraggableTimeout);
        splitDraggableTimeout = window.setTimeout(() => {
          redrawFixedHeaders(100);
        }, 200);
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'redraw.fixed.headers',
      () => {
        hideFixedHeaders();
        redrawFixedHeaders(200);
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'app.gained.focus',
      app => {
        if (app === 'editor') {
          huePubSub.publish('redraw.fixed.headers');
          huePubSub.publish('hue.scrollleft.show');
          huePubSub.publish('active.snippet.type.changed', {
            type: viewModel.editorType(),
            isSqlDialect: viewModel.getSnippetViewSettings(viewModel.editorType()).sqlDialect
          });
        }
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'current.query.tab.switched',
      tab => {
        if (tab !== 'queryResults') {
          $('.hue-datatable-search').hide();
        }
        if (tab === 'queryHistory') {
          hueUtils.waitForRendered(
            $('#queryHistory .history-table'),
            el => {
              return el.is(':visible');
            },
            () => {
              viewModel.selectedNotebook().forceHistoryInitialHeight(true);
              huePubSub.publish('editor.calculate.history.height');
            }
          );
        }
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'detach.scrolls',
      snippet => {
        let scrollElement = $('#snippet_' + snippet.id()).find('.dataTables_wrapper');
        if (viewModel.editorMode()) {
          scrollElement = $(window.MAIN_SCROLLABLE);
        }
        if (scrollElement.data('scrollFnDt')) {
          scrollElement.off('scroll', scrollElement.data('scrollFnDt'));
        }
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'editor.calculate.history.height',
      () => {
        if (
          viewModel.editorMode() &&
          (viewModel.selectedNotebook().historyInitialHeight() === 0 ||
            viewModel.selectedNotebook().forceHistoryInitialHeight())
        ) {
          let h = $('#queryHistory .history-table').height();
          if (h === 0) {
            h = viewModel.selectedNotebook().history().length * 32;
          }
          viewModel.selectedNotebook().historyInitialHeight(h + 80); // add pagination too
          viewModel.selectedNotebook().forceHistoryInitialHeight(false);
        }
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe('editor.create.new', newKeyHandler, HUE_PUB_SUB_EDITOR_ID);

    if (viewModel.isOptimizerEnabled()) {
      if (window.OPTIMIZER_AUTO_UPLOAD_QUERIES) {
        huePubSub.subscribe(
          'editor.upload.query',
          query_id => {
            viewModel
              .selectedNotebook()
              .snippets()[0]
              .uploadQuery(query_id);
          },
          HUE_PUB_SUB_EDITOR_ID
        );
      }

      if (window.OPTIMIZER_AUTO_UPLOAD_DDL) {
        huePubSub.subscribe(
          'editor.upload.table.stats',
          options => {
            viewModel
              .selectedNotebook()
              .snippets()[0]
              .uploadTableStats(options);
          },
          HUE_PUB_SUB_EDITOR_ID
        );
      }

      if (window.OPTIMIZER_QUERY_HISTORY_UPLOAD_LIMIT !== 0) {
        huePubSub.subscribe(
          'editor.upload.history',
          () => {
            viewModel
              .selectedNotebook()
              .snippets()[0]
              .uploadQueryHistory(5);
          },
          HUE_PUB_SUB_EDITOR_ID
        );
      }
    }

    huePubSub.subscribe(
      'get.selected.notebook',
      () => {
        huePubSub.publish('set.selected.notebook', viewModel.selectedNotebook());
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'left.assist.show',
      () => {
        if (!viewModel.isLeftPanelVisible() && viewModel.assistAvailable()) {
          viewModel.isLeftPanelVisible(true);
        }
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'assist.set.manual.visibility',
      () => {
        wasLeftPanelVisible = viewModel.isLeftPanelVisible();
        wasRightPanelVisible = viewModel.isRightPanelVisible();
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'editor.presentation.operate.toggle',
      value => {
        viewModel.isEditing(!viewModel.isEditing());
        if (value) {
          $('.jHueNotify').remove();
          isAssistAvailable = viewModel.assistAvailable();
          wasLeftPanelVisible = viewModel.isLeftPanelVisible();
          wasRightPanelVisible = viewModel.isRightPanelVisible();

          if (wasResultFullScreenMode) {
            huePubSub.publish('both.assists.hide', true);
          } else {
            huePubSub.publish('right.assist.hide', true);
          }

          viewModel.assistWithoutStorage(true);
          viewModel.assistAvailable(false);
          viewModel.isLeftPanelVisible(true);
          viewModel.isRightPanelVisible(false);
          window.setTimeout(() => {
            viewModel.assistWithoutStorage(false);
          }, 0);
          $('.navigator').hide();
          $('.add-snippet').hide();

          if (window.BANNER_TOP_HTML) {
            $('.main-content').attr('style', 'top: 31px !important');
          } else {
            $('.main-content').css('top', '1px');
          }
          redrawFixedHeaders(200);
          $(window).bind('keydown', 'esc', exitPlayerMode);
        } else {
          hideFixedHeaders();
          huePubSub.publish('both.assists.show', true);
          viewModel.assistWithoutStorage(true);
          viewModel.isLeftPanelVisible(wasLeftPanelVisible);
          viewModel.isRightPanelVisible(wasRightPanelVisible);
          viewModel.assistAvailable(isAssistAvailable);
          window.setTimeout(() => {
            viewModel.assistWithoutStorage(false);
          }, 0);
          $('.navigator').show();
          $('.add-snippet').show();
          if (window.BANNER_TOP_HTML) {
            $('.main-content').css('top', '112px');
          } else {
            $('.main-content').css('top', '74px');
          }
          redrawFixedHeaders(200);
          $(window).unbind('keydown', exitPlayerMode);
        }
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'show.retry.modal',
      data => {
        $('#retryModal' + window.EDITOR_SUFFIX).modal('show');
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'hide.retry.modal',
      data => {
        $('#retryModal' + window.EDITOR_SUFFIX).modal('hide');
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'open.link',
      link => {
        $(window).unbind('keydown.editor');
        if (link.indexOf('editor') >= 0) {
          initKeydownBindings();
        }
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'editor.presentation.toggle',
      () => {
        viewModel.selectedNotebook().isPresentationMode(!viewModel.isPresentationMode());
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe('editor.save', saveKeyHandler, HUE_PUB_SUB_EDITOR_ID);

    huePubSub.subscribe(
      'editor.render.data',
      options => {
        const $snip = $('#snippet_' + options.snippet.id());
        const _el = $snip.find('.resultTable');
        if (options.data.length > 0) {
          window.setTimeout(() => {
            let _dt;
            if (options.initial) {
              options.snippet.result.meta.notifySubscribers();
              $('#snippet_' + options.snippet.id())
                .find('select')
                .trigger('chosen:updated');
              _dt = createDatatable(_el, options.snippet, viewModel);
              resetResultsResizer(options.snippet);
            } else {
              _dt = _el.hueDataTable();
            }
            try {
              _dt.fnAddData(options.data);
            } catch (e) {}
            const _dtElement = $snip.find('.dataTables_wrapper');
            huePubSub.publish('editor.snippet.result.normal', options.snippet);
            _dtElement.scrollTop(_dtElement.data('scrollPosition'));
            redrawFixedHeaders();
            resizeToggleResultSettings(options.snippet, options.initial);
          }, 300);
        } else {
          huePubSub.publish('editor.snippet.result.normal', options.snippet);
        }
        $snip.find('select').trigger('chosen:updated');
        $snip.find('.snippet-grid-settings').scrollLeft(0);
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'editor.redraw.data',
      options => {
        hueUtils.waitForRendered(
          '#snippet_' + options.snippet.id() + ' .resultTable',
          el => {
            return el.is(':visible');
          },
          () => {
            const $el = $('#snippet_' + options.snippet.id()).find('.resultTable');
            const dt = createDatatable($el, options.snippet, viewModel);
            dt.fnAddData(options.snippet.result.data());
          }
        );
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'editor.snippet.result.gray',
      snippet => {
        const $snippet = $('#snippet_' + snippet.id());
        $snippet.find('.dataTables_wrapper .fixed-first-column').css({ opacity: '0' });
        $snippet.find('.dataTables_wrapper .fixed-header-row').css({ opacity: '0' });
        $snippet.find('.dataTables_wrapper .fixed-first-cell').css({ opacity: '0' });
        $snippet.find('.dataTables_wrapper .resultTable').css({ opacity: '0.55' });
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'editor.snippet.result.normal',
      snippet => {
        const $snippet = $('#snippet_' + snippet.id());
        $snippet.find('.dataTables_wrapper .fixed-first-column').css({ opacity: '1' });
        $snippet.find('.dataTables_wrapper .fixed-header-row').css({ opacity: '1' });
        $snippet.find('.dataTables_wrapper .fixed-first-cell').css({ opacity: '1' });
        $snippet.find('.dataTables_wrapper .resultTable').css({ opacity: '1' });
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'render.jqcron',
      () => {
        if (typeof window.renderJqCron !== 'undefined') {
          window.renderJqCron();
        }
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'submit.popup.return',
      data => {
        viewModel.selectedNotebook().viewSchedulerId(data.job_id);
        $('.submit-modal-editor').modal('hide');
        huePubSub.publish('show.jobs.panel', { id: data.job_id, interface: 'workflows' });
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'jobbrowser.data',
      jobs => {
        const snippet = viewModel.selectedNotebook().snippets()[0];
        if (!snippet || snippet.type() === 'impala') {
          return;
        }
        if (jobs.length > 0) {
          let progress = 0;
          let parent;
          jobs.forEach(job => {
            const id = job.shortId || job.id;
            const el = $('.jobs-overlay li:contains(' + id + ')');
            if (!el.length) {
              return;
            }
            const context = ko.contextFor(el[0]);
            parent = context.$parent;
            const _job = context.$data;
            progress = parseInt(job.mapsPercentComplete);
            if (isNaN(progress)) {
              progress = parseInt(job.progress);
            }
            if (!isNaN(progress)) {
              _job.percentJob(progress);
            } else {
              progress = 0;
            }
          });
          if (parent && parent.jobs().length === 1) {
            parent.progress(Math.max(progress, parent.progress()));
          }
        }
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'editor.get.active.risks',
      callback => {
        const result = {
          editor: undefined,
          risks: {}
        };
        if (viewModel.selectedNotebook()) {
          if (viewModel.selectedNotebook().snippets().length === 1) {
            result.editor = viewModel
              .selectedNotebook()
              .snippets()[0]
              .ace();
            result.risks =
              viewModel
                .selectedNotebook()
                .snippets()[0]
                .complexity() || {};
          } else {
            viewModel
              .selectedNotebook()
              .snippets()
              .every(snippet => {
                if (snippet.inFocus()) {
                  result.editor = snippet.ace();
                  result.risks = snippet.complexity() || {};
                  return false;
                }
                return true;
              });
          }
        }
        callback(result);
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'editor.grid.shown',
      snippet => {
        hueUtils.waitForRendered(
          '#snippet_' + snippet.id() + ' .dataTables_wrapper',
          el => {
            return el.is(':visible');
          },
          () => {
            resizeToggleResultSettings(snippet, true);
            forceChartDraws();
            $('#snippet_' + snippet.id())
              .find('.snippet-grid-settings')
              .scrollLeft(0);
          }
        );
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'editor.chart.shown',
      snippet => {
        resizeToggleResultSettings(snippet, true);
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'recalculate.name.description.width',
      () => {
        hueUtils.waitForRendered(
          '.editorComponents .hue-title-bar .query-name',
          el => {
            return el.is(':visible');
          },
          () => {
            let cumulativeWidth = 0;
            $('.editorComponents .hue-title-bar ul li:not(.skip-width-calculation)').each(
              function() {
                cumulativeWidth += $(this).outerWidth();
              }
            );
            $('.notebook-name-desc').css(
              'max-width',
              ($('.editorComponents .hue-title-bar').width() -
                cumulativeWidth -
                $('.editorComponents .hue-title-bar .pull-right').width() -
                120) /
                2 +
                'px'
            );
          }
        );
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    $(document).on('updateResultHeaders', e => {
      hideFixedHeaders();
      redrawFixedHeaders(200);
    });

    $(document).on('showAuthModal', (e, data) => {
      viewModel.authSessionUsername(window.LOGGED_USERNAME);
      viewModel.authSessionMessage(data['message']);
      viewModel.authSessionPassword('');
      viewModel.authSessionType(data['type']);
      viewModel.authSessionCallback(data['callback']);
      $('#authModal' + window.EDITOR_SUFFIX).modal('show');
    });

    $(document).on('hideHistoryModal', e => {
      $('#clearHistoryModal' + window.EDITOR_SUFFIX).modal('hide');
    });

    $(document).on('toggleResultSettings', (e, snippet) => {
      window.setTimeout(() => {
        const $snip = $('#snippet_' + snippet.id());
        $snip.find('.chart').trigger('forceUpdate');
        $snip.find('.snippet-grid-settings').scrollLeft(0);
        if (snippet.isResultSettingsVisible()) {
          $snip
            .find('.table-results .grid-side')
            .width(
              100 -
                $snip.find('.table-results .column-side').data('newWidth') -
                hueUtils.bootstrapRatios.margin() +
                '%'
            );
        } else {
          $snip.find('.table-results .grid-side').width('100%');
        }
        redrawFixedHeaders();
        $(window).trigger('resize');
      }, 10);
    });

    $(document).on('editorSizeChanged', () => {
      window.setTimeout(forceChartDraws, 50);
    });

    $(document).on('redrawResults', () => {
      window.setTimeout(forceChartDraws, 50);
    });

    $(document).on('executeStarted', (e, options) => {
      const $snip = $('#snippet_' + options.snippet.id());
      const $el = $snip.find('.resultTable');
      if (options.vm.editorMode()) {
        $('#queryResults').css({
          height: $el.height() + 'px'
        });
      }
      $el.data('scrollToCol', null);
      $el.data('scrollToRow', null);
      $snip.find('.progress-snippet').animate(
        {
          height: '3px'
        },
        100
      );
      if ($el.hasClass('dt')) {
        $el.removeClass('dt');
        $('#eT' + options.snippet.id() + 'jHueTableExtenderClonedContainer').remove();
        $('#eT' + options.snippet.id() + 'jHueTableExtenderClonedContainerColumn').remove();
        $('#eT' + options.snippet.id() + 'jHueTableExtenderClonedContainerCell').remove();
        if ($el.hueDataTable()) {
          $el.hueDataTable().fnDestroy();
        }
        $el.find('thead tr').empty();
        $el.data('lockedRows', {});
      }
    });

    $(document).on('renderDataError', (e, options) => {
      huePubSub.publish('editor.snippet.result.normal', options.snippet);
    });

    $(document).on('progress', (e, options) => {
      if (options.data === 100) {
        window.setTimeout(() => {
          $('#snippet_' + options.snippet.id())
            .find('.progress-snippet')
            .animate(
              {
                height: '0'
              },
              100,
              () => {
                options.snippet.progress(0);
                redrawFixedHeaders();
              }
            );
        }, 2000);
      }
    });

    $(document).on('forceChartDraw', (e, snippet) => {
      window.setTimeout(() => {
        snippet.chartX.notifySubscribers();
        snippet.chartX.valueHasMutated();
      }, 100);
    });

    let hideTimeout = -1;
    $(document).on('hideAutocomplete', () => {
      window.clearTimeout(hideTimeout);
      hideTimeout = window.setTimeout(() => {
        const $aceAutocomplete = $('.ace_editor.ace_autocomplete');
        if ($aceAutocomplete.is(':visible')) {
          $aceAutocomplete.hide();
        }
      }, 100);
    });

    let _resizeTimeout = -1;
    $(window).on('resize', () => {
      huePubSub.publish('recalculate.name.description.width');
      window.clearTimeout(_resizeTimeout);
      _resizeTimeout = window.setTimeout(() => {
        forceChartDraws();
      }, 200);
    });
  }
});
