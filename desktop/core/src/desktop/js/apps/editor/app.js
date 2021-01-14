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

import * as ko from 'knockout';
import $ from 'jquery';
import Clipboard from 'clipboard';
import 'jquery-mousewheel';
import 'ext/bootstrap-datepicker.min';
import 'ext/jquery.hotkeys';
import 'jquery/plugins/jquery.hdfstree';

import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import I18n from 'utils/i18n';
import sqlWorkerHandler from 'sql/sqlWorkerHandler';

import {
  HIDE_FIXED_HEADERS_EVENT,
  REDRAW_FIXED_HEADERS_EVENT,
  SHOW_GRID_SEARCH_EVENT,
  SHOW_NORMAL_RESULT_EVENT,
  REDRAW_CHART_EVENT,
  IGNORE_NEXT_UNLOAD_EVENT
} from './events';
import EditorViewModel from './EditorViewModel';
import { DIALECT } from './snippet';
import { SHOW_LEFT_ASSIST_EVENT } from 'ko/components/assist/events';

window.Clipboard = Clipboard;

const HUE_PUB_SUB_EDITOR_ID = 'editor';

huePubSub.subscribe('app.dom.loaded', app => {
  if (app === 'editor') {
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
        $(window.EDITOR_BINDABLE_ELEMENT).find('.hoverMsg').removeClass('hide');
      }
    };

    const hideHoverMsg = vm => {
      if (vm.editorMode()) {
        $(window.EDITOR_BINDABLE_ELEMENT).find('.hoverText').html(I18n('Drop a SQL file here'));
      } else {
        $(window.EDITOR_BINDABLE_ELEMENT)
          .find('.hoverText')
          .html(I18n('Drop iPython/Zeppelin notebooks here'));
      }
      $(window.EDITOR_BINDABLE_ELEMENT).find('.hoverMsg').addClass('hide');
    };

    if (ko.options) {
      ko.options.deferUpdates = true;
    }

    let viewModel;

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
      huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT);
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
              huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT);
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

      const handleFileSelect = evt => {
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
          reader.onload = (function (file) {
            return function (e) {
              $('.hoverText').html("<i class='fa fa-spinner fa-spin'></i>");
              parseExternalJSON(e.target.result);
            };
          })(f);
          reader.readAsText(f);
        }
      };

      const handleDragOver = function (evt) {
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
      viewModel = new EditorViewModel(
        window.EDITOR_ID,
        window.NOTEBOOKS_JSON,
        window.EDITOR_VIEW_MODEL_OPTIONS,
        window.CoordinatorEditorViewModel,
        window.RunningCoordinatorModel
      );
    } else {
      viewModel = new EditorViewModel(
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
      huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT);
    });

    let ignoreNextUnload = false;

    huePubSub.subscribe(IGNORE_NEXT_UNLOAD_EVENT, () => {
      ignoreNextUnload = true;
    });

    // Close the notebook snippets when leaving the page
    window.onbeforeunload = function (e) {
      if (ignoreNextUnload) {
        ignoreNextUnload = false;
        return;
      }
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
        $('#editorSaveAsModal').modal('show');
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
            ? viewModel.selectedNotebook().snippets()[0].currentQueryTab()
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
          viewModel.selectedNotebook().snippets()[0].currentQueryTab() === 'queryResults'
        ) {
          e.preventDefault();
          huePubSub.publish(SHOW_GRID_SEARCH_EVENT);
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
        start: function (e, ui) {
          initialResizePosition = ui.offset.top;
          huePubSub.publish(HIDE_FIXED_HEADERS_EVENT);
        },
        drag: function (e, ui) {
          draggableHelper($(this), e, ui);
        },
        stop: function (e, ui) {
          draggableHelper($(this), e, ui, true);
          huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT);
          ui.helper.first().removeAttr('style');
        },
        containment: [0, minY, 4000, minY + 400]
      };
    };

    $('.resize-panel a').each(function () {
      $(this).draggable(getDraggableOptions($(this).parents('.snippet').offset().top + 128));
    });

    // ======== PubSub ========

    let splitDraggableTimeout = -1;
    huePubSub.subscribe(
      'split.draggable.position',
      () => {
        window.clearTimeout(splitDraggableTimeout);
        splitDraggableTimeout = window.setTimeout(() => {
          huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT);
        }, 200);
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'app.gained.focus',
      app => {
        if (app === 'editor') {
          huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT);
          huePubSub.publish('hue.scrollleft.show');
          viewModel.notifyDialectChange(
            viewModel.editorType(),
            viewModel.getSnippetViewSettings(viewModel.editorType()).sqlDialect
          );
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
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe('editor.create.new', newKeyHandler, HUE_PUB_SUB_EDITOR_ID);

    if (viewModel.isOptimizerEnabled()) {
      if (window.OPTIMIZER_AUTO_UPLOAD_QUERIES) {
        huePubSub.subscribe(
          'editor.upload.query',
          query_id => {
            viewModel.selectedNotebook().snippets()[0].uploadQuery(query_id);
          },
          HUE_PUB_SUB_EDITOR_ID
        );
      }

      if (window.OPTIMIZER_AUTO_UPLOAD_DDL) {
        huePubSub.subscribe(
          'editor.upload.table.stats',
          options => {
            viewModel.selectedNotebook().snippets()[0].uploadTableStats(options);
          },
          HUE_PUB_SUB_EDITOR_ID
        );
      }

      if (window.OPTIMIZER_QUERY_HISTORY_UPLOAD_LIMIT !== 0) {
        huePubSub.subscribe(
          'editor.upload.history',
          () => {
            viewModel.selectedNotebook().snippets()[0].uploadQueryHistory(5);
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
      SHOW_LEFT_ASSIST_EVENT,
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

          // if (window.BANNER_TOP_HTML) {
          //   $('.main-content').attr('style', 'top: 31px !important');
          // } else {
          //   $('.main-content').css('top', '1px');
          // }
          window.setTimeout(() => {
            huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT);
          }, 200);
          $(window).bind('keydown', 'esc', exitPlayerMode);
        } else {
          huePubSub.publish(HIDE_FIXED_HEADERS_EVENT);
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
          // if (window.BANNER_TOP_HTML) {
          //   $('.main-content').css('top', '112px');
          // } else {
          //   $('.main-content').css('top', '74px');
          // }
          window.setTimeout(() => {
            huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT);
          }, 200);
          $(window).unbind('keydown', exitPlayerMode);
        }
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'show.retry.modal',
      data => {
        $('#editorRetryModal').modal('show');
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'hide.retry.modal',
      data => {
        $('#editorRetryModal' + window.EDITOR_SUFFIX).modal('hide');
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
        huePubSub.publish('show.jobs.panel', { id: data.job_id, interface: data.type });
      },
      HUE_PUB_SUB_EDITOR_ID
    );

    huePubSub.subscribe(
      'jobbrowser.data',
      jobs => {
        viewModel.withActiveSnippet(snippet => {
          if (!snippet || snippet.dialect() === DIALECT.impala) {
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
        });
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
            result.editor = viewModel.selectedNotebook().snippets()[0].ace();
            result.risks = viewModel.selectedNotebook().snippets()[0].complexity() || {};
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
              function () {
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
      huePubSub.publish(HIDE_FIXED_HEADERS_EVENT);
      window.setTimeout(() => {
        huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT);
      }, 200);
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

    $(document).on('editorSizeChanged', () => {
      window.setTimeout(() => {
        huePubSub.publish(REDRAW_CHART_EVENT);
      }, 50);
    });

    $(document).on('redrawResults', () => {
      window.setTimeout(() => {
        huePubSub.publish(REDRAW_CHART_EVENT);
      }, 50);
    });

    $(document).on('renderDataError', (e, options) => {
      huePubSub.publish(SHOW_NORMAL_RESULT_EVENT);
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

    $(window).on('resize', () => {
      huePubSub.publish('recalculate.name.description.width');
    });
  }
});
