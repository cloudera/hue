var indexesOptions = document.getElementById('indexOptions');
indexesOptions = JSON.parse(indexesOptions.textContent);

var IndexesViewModel = (function () {

  var Alias = function (vm) {
    var self = this;

    self.name = ko.observable('');
    self.chosenCollections = ko.observableArray();
    self.availableCollections = ko.computed(function () {
      return $.grep(vm.indexes(), function (index) {
        return index.type() == 'collection';
      });
    });

    self.create = function () {
      $.post("/indexer/api/aliases/create", {
        "name": self.name,
        "collections": ko.mapping.toJSON($.map(self.chosenCollections(), function (collection) {
          return collection.name();
        }))
      }, function (data) {
        if (data.status == 0) {
          vm.indexes.push(ko.mapping.fromJS(data.alias));
          huePubSub.publish('assist.collections.refresh');
        } else {
          huePubSub.publish('hue.global.error', {message: data.message});
        }
        $('#createAlias').modal('hide');
      }).fail(function (xhr, textStatus, errorThrown) {
        huePubSub.publish('hue.global.error', {message: xhr.responseText});
      });
      hueAnalytics.log('indexes', 'create_alias');
    }

    self.edit = function (alias) {
      self.name(alias.name());
      self.chosenCollections($.grep(vm.indexes(), function(collection) { return alias.collections().indexOf(collection.name()) != -1; }));
      $('#createAlias').modal('show');
    }
  };


  var Index = function (vm, index) {
    var self = this;

    self.name = ko.observable(index.name);
    self.type = ko.observable(index.type);
    self.uniqueKey = ko.observable(index.schema.uniqueKey);
    self.fields = ko.mapping.fromJS(index.schema.fields);
    self.fieldsPreview = ko.pureComputed(function () {
      return self.fields().slice(0, 5)
    });
    self.filteredFields = ko.computed(function () {
      var returned = self.fields();
      if (vm.fieldFilter() !== '') {
        returned = $.grep(self.fields(), function (field) {
          return field.name().toLowerCase().indexOf(vm.fieldFilter().toLowerCase()) > -1;
        });
      }
      return returned;
    });

    self.dynamicFields = ko.mapping.fromJS(index.schema.dynamicFields);
    self.copyFields = ko.mapping.fromJS(index.schema.copyFields);
    self.config = ko.observable('');

    self.sample = ko.observableArray();
    self.samplePreview = ko.pureComputed(function () {
      return self.sample().slice(0, 5)
    });

    self.loadingSample = ko.observable(false);
    self.loadingConfig = ko.observable(false);

    self.getSample = function () {
      self.loadingSample(true);
      $.post("/indexer/api/indexes/sample", {
        name: self.name(),
        rows: 100
      }, function (data) {
        if (data.status == 0) {
          self.sample(data.sample);
        } else {
          huePubSub.publish('hue.global.error', {message: data.message});
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        huePubSub.publish('hue.global.error', {message: xhr.responseText});
      }).always(function () {
        self.loadingSample(false);
      });
    };

    self.getConfig = function () {
      self.loadingConfig(true);
      $.post("/indexer/api/indexes/config", {
        name: self.name()
      }, function (data) {
        if (data.status == 0) {
          self.config(data.config);
        } else {
          huePubSub.publish('hue.global.error', {message: data.message});
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        huePubSub.publish('hue.global.error', {message: xhr.responseText});
      }).always(function () {
        self.loadingConfig(false);
      });
    };

    self.delete = function () {
      var indexName = self.name();
      $.post("/indexer/api/indexes/delete", {
        "indexes": ko.mapping.toJSON([{'name': indexName, 'type': self.type()}])
      }, function (data) {
        if (data.status == 0) {
          vm.indexes.remove(function(index) { return index.name() == indexName; });
          huePubSub.publish('assist.collections.refresh');
          vm.showIndexes(false);
        } else {
          huePubSub.publish('hue.global.error', {message: data.message});
        }
        $('#deleteIndex').modal('hide');
      }).fail(function (xhr, textStatus, errorThrown) {
        huePubSub.publish('hue.global.error', {message: xhr.responseText});
      });
      hueAnalytics.log('indexes', 'delete_index');
    };
  };

  var IndexesViewModel = function (options) {
    var self = this;

    self.baseURL = '/hue/indexer/indexes/';

    self.activeNamespace = ko.observable();
    self.activeCompute = ko.observable();

    // TODO: Use connectors in indexes
    contextCatalog.getNamespaces({ connector: { id: 'solr' }}).then(function (context) {
      // TODO: Namespace selection
      self.activeNamespace(context.namespaces[0]);
      self.activeCompute(context.namespaces[0].computes[0]);
    }).catch();

    self.assistAvailable = ko.observable(true);
    self.apiHelper = window.apiHelper;
    self.isLeftPanelVisible = ko.observable();
    window.hueUtils.withLocalStorage('assist.assist_panel_visible', self.isLeftPanelVisible, true);
    self.isLeftPanelVisible.subscribe(function () {
      huePubSub.publish('assist.forceRender');
    });

    self.section = ko.observable('list-indexes');
    self.tab = ko.observable('');
    self.tab.subscribe(function(tab){
      if (tab === 'index-sample'){
        var selector = '#index-sample .sample-table';
          var bannerTopHeight = 0;
        if ($(selector).parents('.dataTables_wrapper').length == 0){
          hueUtils.waitForRendered(selector, function(el){ return el.find('td').length > 0 }, function(){
            $(selector).dataTable({
              "bPaginate": false,
              "bLengthChange": false,
              "bInfo": false,
              "bDestroy": true,
              "bFilter": false,
              "bAutoWidth": false,
              "oLanguage": {
                "sEmptyTable": "No data available",
                "sZeroRecords": "No matching records"
              },
              "fnDrawCallback": function (oSettings) {
                $(selector).parents('.dataTables_wrapper').css('overflow-x', 'hidden');
                $(selector).jHueTableExtender2({
                  fixedHeader: true,
                  fixedFirstColumn: true,
                  includeNavigator: false,
                  lockSelectedRow: false,
                  parentId: 'index-sample',
                  classToRemove: 'sample-table',
                  mainScrollable: '.page-content',
                    stickToTopPosition: 51 + bannerTopHeight,
                  clonedContainerPosition: 'fixed',
                  app: 'indexes'
                });
                $(selector).jHueHorizontalScrollbar();
              },
              "aoColumnDefs": [
                {
                  "sType": "numeric",
                  "aTargets": [ "sort-numeric" ]
                },
                {
                  "sType": "string",
                  "aTargets": [ "sort-string" ]
                },
                {
                  "sType": "date",
                  "aTargets": [ "sort-date" ]
                }
              ]
            });
          });
        }
      }
    });

    self.indexes = ko.observableArray([]);
    self.alias = new Alias(self);
    self.index = ko.observable();

    self.indexFilter = ko.observable('');
    self.fieldFilter = ko.observable('');

    self.filteredIndexes = ko.computed(function () {
      var returned = self.indexes();
      if (self.indexFilter() !== '') {
        returned = $.grep(self.indexes(), function (idx) {
          return idx.name().toLowerCase().indexOf(self.indexFilter().toLowerCase()) > -1;
        });
      }
      return returned;
    });

    self.selectedIndexes = ko.computed(function () {
      return $.grep(self.indexes(), function (index) {
        return index.isSelected();
      });
    });
    self.isLoading = ko.observable(false);

    self.oneSelected = ko.computed(function () {
      return self.selectedIndexes().length == 1;
    });
    self.atLeastOneSelected = ko.computed(function () {
      return self.selectedIndexes().length >= 1;
    });
    self.allSelected = ko.observable(false);

    self.handleSelect = function (index) {
      index.isSelected(!index.isSelected());
    }

    self.selectAll = function () {
      self.allSelected(!self.allSelected());
      ko.utils.arrayForEach(self.indexes(), function (index) {
        index.isSelected(self.allSelected());
      });
    }

    self.datatable = null;

    self.showIndexes = function (reload) {
      self.section('list-indexes');
      self.index(null);
      hueUtils.changeURL(self.baseURL);
      if (typeof reload == 'undefined' || reload) {
        self.fetchIndexes();
      }
    }

    self.fetchIndexes = function (callback) {
      self.isLoading(true);
      $.post("/indexer/api/indexes/list", {}, function (data) {
        if (data.status == 0) {
          var indexes = []
          data.collections.forEach(function (index) {
            index.isSelected = false;
            indexes.push(ko.mapping.fromJS(index));
          });
          self.indexes(indexes);
          if (callback) {
            callback();
          }
        } else {
          huePubSub.publish('hue.global.error', {message: data.message})
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        huePubSub.publish('hue.global.error', {message: xhr.responseText});
      }).always(function () {
        self.isLoading(false);
      });
      hueAnalytics.log('indexes', 'list_indexes');
    };

    self.getIndexByName = function (name) {
      var found = null;
      self.indexes().forEach(function (idx) {
        if (idx.name() === name) {
          found = idx;
        }
      });
      return found;
    };

    self.fetchIndex = function (index) {
      $.post("/indexer/api/index/list", {
        name: index.name()
      }, function (data) {
        if (data.status == 0) {
          self.index(new Index(self, data));
          self.index().type(index.type());
          self.index().getSample();
          hueUtils.changeURL(self.baseURL + self.index().name());
          self.section('list-index');
          self.tab('index-overview');
        } else {
          huePubSub.publish('hue.global.error', {message: data.message});
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        huePubSub.publish('hue.global.error', {message: xhr.responseText});
      });
      hueAnalytics.log('indexes', 'list_index');
    };

    self.deleteIndexes = function () {
      $.post("/indexer/api/indexes/delete", {
        "indexes": ko.mapping.toJSON(self.selectedIndexes)
      }, function (data) {
        if (data.status == 0) {
          self.indexes.removeAll(self.selectedIndexes());
          huePubSub.publish('assist.collections.refresh');
        } else {
          huePubSub.publish('hue.global.error', {message: data.message});
        }
        $('#deleteIndexes').modal('hide');
      }).fail(function (xhr, textStatus, errorThrown) {
        huePubSub.publish('hue.global.error', {message: xhr.responseText});
      });
      hueAnalytics.log('indexes', 'delete_indexes');
    };

    self.showContextPopover = function (field, event) {
      var $source = $(event.target);
      var offset = $source.offset();

      huePubSub.publish('context.popover.show', {
        data: {
          type: 'collection',
          identifierChain: [
            {}, // empty, needed by the context popover
            ko.mapping.toJS(self.index),
            ko.mapping.toJS(field)
          ]
        },
        namespace: self.activeNamespace(),
        compute: self.activeCompute(),
        showInAssistEnabled: true,
        orientation: 'right',
        pinEnabled: false,
        source: {
          element: event.target,
          left: offset.left,
          top: offset.top - 3,
          right: offset.left + $source.width() + 1,
          bottom: offset.top + $source.height() - 3
        }
      });
    };

  };
  return IndexesViewModel;
})();


(function () {
  $(document).ready(function () {
    var options = {
      user: LOGGED_USERNAME,
      index: indexesOptions.index
    };
    var viewModel = new IndexesViewModel(options);
    ko.applyBindings(viewModel, $('#indexesComponents')[0]);

    huePubSub.subscribe('open.index', function (index) {
      var foundIndex = viewModel.getIndexByName(index);
      if (foundIndex) {
        viewModel.fetchIndex(foundIndex);
      }
    }, 'indexes');

    viewModel.fetchIndexes(function () {
      if (options.index) {
        var foundIndex = viewModel.getIndexByName(options.index);
        if (foundIndex) {
          viewModel.fetchIndex(foundIndex);
        }
        else {
          huePubSub.publish('hue.global.error', {
            message: "The specified index has not been found"
          });
          viewModel.showIndexes();
        }
      }
    });
  });
})();