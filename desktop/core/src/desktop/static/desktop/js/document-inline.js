
(function () {
  ko.bindingHandlers.trashDroppable = {
    init: function (element, valueAccessor, allBindings, boundEntry) {
      var dragData;
      huePubSub.subscribe('doc.browser.dragging', function (data) {
        dragData = data;
      });
      var $element = $(element);
      $element.droppable({
        drop: function () {
          if (dragData && !dragData.dragToSelect) {
            boundEntry.moveToTrash();
            $element.removeClass('blue');
          }
        },
        over: function () {
          if (dragData && !dragData.dragToSelect) {
            $element.addClass('blue');
          }
        },
        out: function () {
          $element.removeClass('blue');
        }
      })
    }
  };

  ko.bindingHandlers.docDroppable = {
    init: function (element, valueAccessor, allBindings, boundEntry, bindingContext) {
      var $element = $(element);
      var dragToSelect = false;
      var selectSub = huePubSub.subscribe('doc.drag.to.select', function (value) {
        dragToSelect = value;
      });

      var dragData;
      var dragSub = huePubSub.subscribe('doc.browser.dragging', function (data) {
        dragData = data;
      });

      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        dragSub.remove();
        selectSub.remove();
      });

      $element.droppable({
        drop: function (ev, ui) {
          if (!dragToSelect && dragData && !dragData.dragToSelect && boundEntry.isDirectory && boundEntry.isDirectory()) {
            boundEntry.moveHere(dragData.selectedEntries);
          }
          $element.removeClass('doc-browser-drop-hover');
        },
        over: function () {
          if (!dragToSelect && boundEntry.isDirectory && boundEntry.isDirectory()) {
            var movableCount = dragData.selectedEntries.filter(function (entry) {
              return entry.selected() && !entry.isSharedWithMe();
            }).length;
            if (movableCount > 0) {
              $element.addClass('doc-browser-drop-hover');
            }
          }
        },
        out: function (event, ui) {
          if (!dragToSelect && boundEntry.isDirectory && boundEntry.isDirectory()) {
            $element.removeClass('doc-browser-drop-hover');
          }
        }
      })
    }
  };

  ko.bindingHandlers.docSelect = {
    init: function (element, valueAccessor, allBindings, boundEntry, bindingContext) {
      var $element = $(element);
      $element.attr('unselectable', 'on').css('user-select', 'none').on('selectstart', false);
      var allEntries = valueAccessor();

      var dragStartY = -1;
      var dragStartX = -1;
      var dragToSelect = false;
      var allRows;
      $element.draggable({
        start: function (event, ui) {
          allRows = $('.doc-browser-row');
          var $container = $('.doc-browser-drag-container');

          var selectedEntries = allEntries ? $.grep(allEntries(), function (entry) {
            return entry.selected();
          }) : [];

          dragToSelect = boundEntry && boundEntry.selected ? !boundEntry.selected() : true;

          huePubSub.publish('doc.browser.dragging', {
            selectedEntries: selectedEntries,
            originEntry: boundEntry ? boundEntry.parent : null,
            dragToSelect: dragToSelect
          });

          dragStartX = event.clientX;
          dragStartY = event.clientY;

          huePubSub.publish('doc.drag.to.select', dragToSelect);

          if (dragToSelect && selectedEntries.length > 0 && !(event.metaKey || event.ctrlKey)) {
            $.each(selectedEntries, function (idx, selectedEntry) {
              if (selectedEntry !== boundEntry) {
                selectedEntry.selected(false);
              }
            });
            selectedEntries = [];
          }

          if (boundEntry && boundEntry.selected) {
            boundEntry.selected(true);
          }
          if (dragToSelect && allEntries) {
            allEntries().forEach(function (entry) {
              entry.alreadySelected = entry.selected();
            })
          }

          if (!dragToSelect) {
            var $helper = $('.doc-browser-drag-helper').clone().appendTo($container).show();
            var sharedCount = selectedEntries.filter(function (entry) {
              return entry.isSharedWithMe();
            }).length;
            if (sharedCount === selectedEntries.length) {
              $helper.hide();
            } else if (selectedEntries.length > 1 && sharedCount > 0) {
              $helper.find('.drag-text').text(selectedEntries.length + ' selected (' + sharedCount + ' shared ignored)');
              $helper.find('i').removeClass().addClass('fa fa-fw fa-clone');
            } else if (selectedEntries.length > 1) {
              $helper.find('.drag-text').text(selectedEntries.length + ' selected');
              $helper.find('i').removeClass().addClass('fa fa-fw fa-clone');
            } else {
              $helper.find('.drag-text').text(boundEntry.definition().name);
              $helper.find('i').removeClass().addClass($element.find('.doc-browser-primary-col i').attr('class'));
            }

          } else {
            $('<div>').addClass('doc-browser-drag-select').appendTo('body');
          }
        },
        drag: function (event) {
          var startX = Math.min(event.clientX, dragStartX);
          var startY = Math.min(event.clientY, dragStartY);
          if (dragToSelect) {
            allRows.each(function (idx, row) {
              var boundingRect = row.getBoundingClientRect();
              var boundObject = ko.dataFor(row);
              if (boundObject) {
                if ((dragStartY <= boundingRect.top && event.clientY >= boundingRect.top) ||
                  (event.clientY <= boundingRect.bottom && dragStartY >= boundingRect.bottom)) {
                  boundObject.selected(true);
                } else if (!boundObject.alreadySelected) {
                  boundObject.selected(false);
                }
              }
            });
            $('.doc-browser-drag-select').css({
              top: startY + 'px',
              left: startX + 'px',
              height: Math.max(event.clientY, dragStartY) - startY + 'px',
              width: Math.max(event.clientX, dragStartX) - startX + 'px'
            })
          }
        },
        stop: function (event) {
          $('.doc-browser-drag-select').remove();
          var elementAtStart = document.elementFromPoint(dragStartX, dragStartY);
          var elementAtStop = document.elementFromPoint(event.clientX, event.clientY);
          if (elementAtStart.nodeName === "A" && elementAtStop.nodeName === "A" && Math.sqrt((dragStartX - event.clientX) * (dragStartX - event.clientX) + (dragStartY - event.clientY) * (dragStartY - event.clientY)) < 8) {
            $(elementAtStop).trigger('click');
          }
        },
        helper: function (event) {
          if (typeof boundEntry !== 'undefined' && boundEntry.selected && boundEntry.selected()) {
            return $('<div>').addClass('doc-browser-drag-container');
          }
          return $('<div>');
        },
        appendTo: "body",
        cursorAt: {
          top: 0,
          left: 0
        }
      });

      var clickHandler = function (clickedEntry, event) {
        if (allEntries) {
          var clickedIndex = $.inArray(clickedEntry, allEntries());

          if (event.metaKey || event.ctrlKey) {
            clickedEntry.selected(!clickedEntry.selected());
          } else if (event.shiftKey) {
            var lastClickedIndex = ko.utils.domData.get(document, 'last-clicked-entry-index') || 0;
            var lower = Math.min(lastClickedIndex, clickedIndex);
            var upper = Math.max(lastClickedIndex, clickedIndex);
            for (var i = lower; i <= upper; i++) {
              allEntries()[i].selected(true);
            }
          } else {
            $.each(allEntries(), function (idx, entry) {
              if (entry !== clickedEntry) {
                entry.selected(false);
              }
            });
            clickedEntry.selected(true);
          }
          var selectedEntries = $.grep(allEntries(), function (entry) {
            return entry.selected();
          });
          ko.utils.domData.set(document, 'last-clicked-entry-index', selectedEntries.length > 0 ? clickedIndex : 0);
        }
      };

      ko.bindingHandlers.multiClick.init(element, function () {
        return {
          click: clickHandler,
          dblClick: boundEntry.open
        }
      }, allBindings, boundEntry, bindingContext);
    }
  };

  /**
   * @param {Object} params
   * @param {HueFileEntry} params.activeEntry - Observable holding the current directory
   * @constructor
   */
  function DocBrowser(params) {
    var self = this;
    self.activeEntry = params.activeEntry;

    self.searchQuery = ko.observable().extend({ throttle: 500 });
    self.searchQuery.subscribe(function (query) {
      self.activeEntry().search(query);
    });

    self.searchVisible = ko.observable(false);
    self.searchFocus = ko.observable(false);

    huePubSub.subscribe('file.browser.directory.opened', function () {
      self.searchQuery('');
      self.searchVisible(false);
      $('.tooltip').hide();
    });

    var keepSelectionSelector = '.doc-browser-entries, .doc-browser-folder-actions, .doc-browser-header, .doc-browser-search-container, .modal';
    $(document).click(function (event) {
      var $target = $(event.target);
      if (!$target.is(keepSelectionSelector) && $target.parents(keepSelectionSelector).length === 0 && self.activeEntry()) {
        self.activeEntry().selectedEntries().forEach(function (entry) {
          entry.selected(false);
        });
      }
    });
    $(window).bind('keydown', 'ctrl+a alt+a meta+a', function (e) {
      self.activeEntry().entries().forEach(function (entry) {
        entry.selected(true);
      });
      e.preventDefault();
      return false;
    });
  }

  ko.components.register('doc-browser', {
    viewModel: DocBrowser,
    template: { element: 'doc-browser-template' }
  });
})();




(function () {
  if (ko.options) {
    ko.options.deferUpdates = true;
  }

  $(document).ready(function () {
    var options = {
      user: window.LOGGED_USERNAME,
      superuser: window.USER_IS_ADMIN,
      i18n: {
        errorFetchingTableDetails: 'An error occurred fetching the table details. Please try again.',
        errorFetchingTableFields: 'An error occurred fetching the table fields. Please try again.',
        errorFetchingTableSample: 'An error occurred fetching the table sample. Please try again.',
        errorRefreshingTableStats: 'An error occurred refreshing the table stats. Please try again.',
        errorLoadingDatabases: 'There was a problem loading the databases. Please try again.',
        errorLoadingTablePreview: 'There was a problem loading the table preview. Please try again.'
      }
    };

    var viewModel = new HomeViewModel(options);

    var loadUrlParam = function () {
      if (window.location.pathname.indexOf('/home') > -1) {
        if (hueUtils.getParameter('uuid')) {
          viewModel.openUuid(hueUtils.getParameter('uuid'));
        } else if (hueUtils.getParameter('path')) {
          viewModel.openPath(hueUtils.getParameter('path'));
        } else if (viewModel.activeEntry() && viewModel.activeEntry().loaded()) {
          var rootEntry = viewModel.activeEntry();
          while (rootEntry && !rootEntry.isRoot()) {
            rootEntry = rootEntry.parent;
          }
          viewModel.activeEntry(rootEntry);
        } else {
          viewModel.activeEntry().load(function () {
            if (viewModel.activeEntry().entries().length === 1 && viewModel.activeEntry().entries()[0].definition().type === 'directory') {
              viewModel.activeEntry(viewModel.activeEntry().entries()[0]);
              viewModel.activeEntry().load();
            }
          });
        }
      }
    };
    window.onpopstate = loadUrlParam;
    loadUrlParam();

    viewModel.activeEntry.subscribe(function (newEntry) {
      var filterType = window.location.pathname.indexOf('/home') > -1 && hueUtils.getParameter('type') != '' ? 'type=' + hueUtils.getParameter('type') : '';
      if (typeof newEntry !== 'undefined' && newEntry.definition().uuid && !newEntry.isRoot()) {
        if (hueUtils.getParameter('uuid') === '' || hueUtils.getParameter('uuid') !== newEntry.definition().uuid){
          hueUtils.changeURL('/hue/home/?uuid=' + newEntry.definition().uuid + '&' + filterType);
        }
      } else if (typeof newEntry === 'undefined' || newEntry.isRoot()) {
        var url = '/hue/home/' + (filterType ? '?' + filterType : '');
        if (window.location.pathname + window.location.search !== url) {
          hueUtils.changeURL(url);
        }
      }
    });

    ko.applyBindings(viewModel, $('#homeComponents')[0]);
  });
})();


