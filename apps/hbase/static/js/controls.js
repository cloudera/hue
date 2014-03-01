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

var searchRenderers = {
  'rowkey': { //class to tag selection
     select: /[^\,\{\[]+(([\{\[][^\}\]]+[\}\]])+|)([^\,]+|)/g, //select the substring to process, useful as JS has no lookbehinds old: ([^,]+\[([^,]+(,|)+)+\]|[^,]+)
     tag: /.+/g, //select the matches to wrap with tags
     nested: {
        'scan': { select: /(([^\\]|\b)\+[0-9]+)/g, tag: /\+[0-9]+/g },
        'columns': {
          select: /\[.+\]/g,
          tag: /[^,\[\]]+/g, //forced to do this select due to lack of lookbehinds /[\[\]]/g
          nested: {
            'range': {
              select: /\sto\s/g,
              tag: /.+/g
            }
          }
        },
        'prefix': { select: /[^\*\\]+\*/g, tag: /\*/g},
        'filter': {
          select: /\{[^\{\}]+\}/,
          tag:/[^\{\}]+/g,
          nested: {
            'linker': {
              select: /\ (AND|OR|SKIP|WHILE)\ /g,
              tag: /.+/g
            }/*,
            'compare_op': {
              select: /[\<\=\!\>]{1,2}/g,
              tag: /.+/g
            }*/ //will be added eventually after html bug is figured out
          }
        }
     }
  }
};

var DataTableViewModel = function(options) {
  var self = this, _defaults = {
    name: '',
    columns: [],
    items: [],
    reload: function() {

    },
    el:''
  };
  options = ko.utils.extend(_defaults,options);
  ListViewModel.apply(this, [options]);

  self.name = ko.observable(options.name);
  self.searchQuery.subscribe(function(value) {
    self._table.fnFilter(value);
  });
  self.columns = ko.observableArray(options.columns);
  self._el = $('table[data-datasource="' + options.el + '"]');
  self._table = null;
  self._initTable = function() {
    if(!self._table) {
      self._table = self._el.dataTable({
        "aoColumnDefs": [ { "bSortable": false, "aTargets": [ 0 ] }
        ],
      "sDom": 'tr',//this has to be in, change to sDom so you can call filter()
      'bAutoWidth':false,
      "iDisplayLength": -1});
      return self._table;
    }
  };
  self.sort = function(viewModel, event) {
      var el = $(event.currentTarget);
  };
  var _reload = self.reload;
  self.reload = function(callback) {
    if(self._table) {
      self._table.fnClearTable();
      self._table.fnDestroy();
      self._table = null;
    }
    _reload(function() {
      self._initTable();
      if(callback!=null)
        callback();
    });
  };

  self.canDrop = ko.computed(function() {
    var selected = self.selected();
    if(selected.length <= 0) return false;
    for(var i=0; i<selected.length; i++) {
      if(selected[i].enabled()) return false;
    }
    return true;
  });

  self.canDisable = ko.computed(function() {
    var selected = self.selected();
    if(selected.length <= 0) return false;
    for(var i=0; i<selected.length; i++) {
      if(!selected[i].enabled()) return false;
    }
    return true;
  });

  self.canEnable = ko.computed(function() {
    var selected = self.selected();
    if(selected.length <= 0) return false;
    for(var i=0; i<selected.length; i++) {
      if(selected[i].enabled()) return false;
    }
    return true;
  });
};

//a Listview of Listviews
var SmartViewModel = function(options) {
  var self = this;
  options = ko.utils.extend({
    name: '',
    items: [],
    reload: function() {

    },
    el:'',
    sortFields: {
      'Row Key': function(a, b) {
        return a.row.localeCompare(b.row);
      },
      'Column Count': function(a, b) {
        a = a.items().length;
        b = b.items().length;
        if(a > b)
          return 1;
        if(a < b)
          return -1;
        return 0;
      },
      'Row Key Length': function(a, b) {
        a = a.row.length;
        b = b.row.length;
        if(a > b)
          return 1;
        if(a < b)
          return -1;
        return 0;
      }
    },
    canWrite: false
  }, options);
  ListViewModel.apply(this, [options]); //items: [ListView.items[],ListView.items[]]

  self.columnFamilies = ko.observableArray();
  self.name = ko.observable(options.name);
  self.name.subscribe(function(val){
    if(!val) return;
    self.columnFamilies([]);
    self._reloadcfs();
    if(app.station() == 'table' && app.search.cur_input())
      return;
    self.querySet.removeAll();
    self.evaluateQuery();
  }); //fix and decouple

  self.lastReloadTime = ko.observable(1);

  self.searchQuery.subscribe(function(value) //make this as nice as the render function and split into two, also fire not down on keyup events
  {
    if(app.station() != 'table')
      return;
    if(value.replace(/\s/g, "") == '' || value == null)
      routie(app.cluster() + '/' + app.views.tabledata.name());
    var inputs = value.match(searchRenderers['rowkey']['select']);
    self.querySet.removeAll();
    if(inputs) {
      for(var i=0; i<inputs.length; i++) {
        if(inputs[i].trim() != "" && inputs[i].trim() != ',') {
          //pull out filters
          var filter = inputs[i].match(searchRenderers['rowkey']['nested']['filter']['select']) || "";
          filter = filter != null && filter.length > 0 ? escape(filter[0].trim().slice(1, -1)) : "";

          function filterPostfix(postfix) {
            return (filter != null && filter.length > 0 ? ' AND ' : ' ' ) + postfix;
          }

          //pull out columns
          var extract = inputs[i].match(searchRenderers['rowkey']['nested']['columns']['select']);
          var columns = extract != null ? extract[0].match(searchRenderers['rowkey']['nested']['columns']['tag']) : [];
          inputs[i] = inputs[i].replace(extract, '');

          //pull out scan
          var p = pullFromRenderer(inputs[i], searchRenderers['rowkey']['nested']['scan']);
          inputs[i] = inputs[i].replace(p, '');
          p = p.split('+');
          var scan = p.length > 1 ? parseInt(p[1].trim()) : 0;

          //pull out column filters
          var toRemove = [];
          var cfs = [];
          for(var n = 0; n < columns.length; n++) {
            var o = columns[n];
            if(columns[n].match(searchRenderers['rowkey']['nested']['columns']['nested']['range']['select'])) {
              var partitions = columns[n].split(searchRenderers['rowkey']['nested']['columns']['nested']['range']['select']);
              filter += filterPostfix("ColumnRangeFilter('" + partitions[0] + "', false, '" + partitions[1] + "', true)");
              toRemove.push(n);
            } else {
              if(o.indexOf(':') == -1) {
                toRemove.push(n);
                //for each column family push cf and then column
                $(self.columnFamilies()).each(function(i, item) {
                  columns.push(item.name + o);
                });
                continue;
              } else {
                o = o.slice(o.indexOf(':') + 1);
              }
              var colscan = pullFromRenderer(o, searchRenderers['rowkey']['nested']['scan']);
              if(colscan) {
                colscan = parseInt(colscan.split('+')[1]) + 1;
                filter += filterPostfix("ColumnPaginationFilter(" + colscan + ", 0)");
              }
              var fc = o.replace(pullFromRenderer(o, searchRenderers['rowkey']['nested']['prefix']), '');
              if(fc != o) {
                filter += filterPostfix("ColumnPrefixFilter('" + o.match(/[^:*]+/g)[0] + "')");
                columns[n] = columns[n].split(':')[0] + ':';
              }
            }
          }

          for(var n = toRemove.length - 1; n>=0; n--) {
            columns.splice(toRemove[n], 1);
          };

          self.querySet.push(new QuerySetPiece({
            'row_key': inputs[i].replace(/\\(\+|\*|\,)/g, '$1').replace(/[\[\{].+[\]\}]|\*/g,'').trim(), //clean up with column regex selectors instead
            'scan_length': scan ? scan + 1 : 1,
            'columns': columns,
            'prefix': inputs[i].match(searchRenderers['rowkey']['nested']['prefix']['select']) != null,
            'filter': filter.length > 0 ? filter : null
          }));
        }
      }
    }
    self.evaluateQuery();
  });

  self._reloadcfs = function(callback) {
    return API.queryTable("getColumnDescriptors").done(function(data) {
      self.columnFamilies.removeAll();
      var keys = Object.keys(data);
      for(var i=0;i<keys.length;i++) {
        self.columnFamilies.push(new ColumnFamily({name:keys[i], enabled:false}));
      }
      if(callback!=null)
        callback();
    });
  };

  self.columnQuery = ko.observable("");
  self.columnQuery.subscribe(function(query) {
    var dataRowFilter = function(index, data_row) {
      data_row.searchQuery(query);
    };
    if (self.selected().length > 0) {
      $.each(self.selected(), dataRowFilter);
    } else {
      $.each(self.items(), dataRowFilter);
    }
  });

  self.rows = ko.computed(function() {
    var a = [];
    var items = this.items();
    for(var i=0; i<items.length; i++) {
      a.push(items[i].row);
    }
    return a;
  }, self);

  self.querySet = ko.observableArray();
  self.validateQuery = function() {
    if(self.querySet().length == 0) {
      self.querySet.push(new QuerySetPiece({
        'row_key': 'null',
        'scan_length': 10,
        'prefix': 'false'
      }));
    } else {
      $(self.querySet()).each(function() {
        this.validate();
        this.editing(false);
      });
    }
  };
  self.addQuery = function() {
    self.validateQuery();
    self.querySet.push(new QuerySetPiece({onValidate: function() {
      //self.reload();
    }}))
  };
  self.evaluateQuery = function(callback) {
    self.validateQuery();
    self.reload(callback);
  };
  var _reload = self.reload;
  self.reload = function(callback) {
    var queryStart = new Date();
    _reload(function() {
      self.lastReloadTime((new Date() - queryStart)/1000);
      if(callback!=null)
        callback();
      self.isLoading(false);
    });
  };

  self.showGrid = ko.observable(false);
  self.showGrid.subscribe(function(val) {
    if(val) {
      var rows = self.items();
      var columns = {};
      //build full lookup hash of columns
      for(var i=0; i<rows.length; i++) {
        var cols = rows[i].items();
        for(var q=0; q<cols.length; q++) {
          if(!columns[cols[q].name])
            columns[cols[q].name] = "";
        }
      }

      for(var i=0; i<rows.length; i++) {
        //clone blank template from hash
        var new_row = $.extend({}, columns);
        var cols = rows[i].items();
        var col_list = [];
        //set existing values
        for(var q=0; q<cols.length; q++) {
          new_row[cols[q].name] = cols[q];
        }
        //build actual row from hash
        var keys = Object.keys(new_row);
        for(var r=0; r<keys.length; r++) {
          if(!new_row[keys[r]]) new_row[keys[r]] = new ColumnRow({ name: keys[r], value: '', parent: rows[i] });
          col_list.push(new_row[keys[r]]);
        }
        //set and sort
        rows[i].items(col_list);
        rows[i].sortDropDown.sort();
      }
    } else {
      self.reload();
    }
  });

  self.truncateLimit = ko.observable(1500);

  self.reachedLimit = ko.computed(function() {
    var items = self.items();
    for(var i=0; i<items.length; i++) {
      if(self.truncateLimit() < items[i].items().length) return true;
    }
    return false;
  });
};

var SmartViewDataRow = function(options) {
  var self = this;
  options = ko.utils.extend({
    sortFields: {
      'Column Family': function(a, b) {
        return a.name.localeCompare(b.name);
      },
      'Column Name': function(a, b) {
        return a.name.split(':')[1].localeCompare(b.name.split(':')[1]);
      },
      'Cell Size': function(a, b) {
        a = a.value().length;
        b = b.value().length;
        if(a > b)
          return 1;
        if(a < b)
          return -1;
        return 0;
      },
      'Cell Value': function(a, b) {
        return a.value().localeCompare(b.value());
      },
      'Timestamp': function(a, b) {
        a = parseInt(a.timestamp);
        b = parseInt(b.timestamp);
        if(a > b)
          return 1;
        if(a < b)
          return -1;
        return 0;
      },
      'Column Name Length': function(a, b) {
        a = a.name.split(':')[1].length;
        b = b.name.split(':')[1].length;
        if(a > b)
          return 1;
        if(a < b)
          return -1;
        return 0;
      }
    },
    canWrite: false
  }, options);
  DataRow.apply(self,[options]);
  ListViewModel.apply(self,[options]);

  self.displayedItems = ko.observableArray();

  self.displayRangeStart = 0;
  self.displayRangeLength = 20;
  self.items.subscribe(function() {
    self.displayedItems([]);
    self.updateDisplayedItems();
  });

  self.searchQuery.subscribe(function(searchValue) {
    self.scrollLoadSource = ko.computed(function(){
      return self.items().filter(function(column) {
        return column.name.toLowerCase().indexOf(searchValue.toLowerCase()) != -1;
      });
    });
    self.displayRangeLength = 20;
    self.updateDisplayedItems();
  });

  self.scrollLoadSource = self.items;

  self.updateDisplayedItems = function() {
    var x = self.displayRangeStart;
    self.displayedItems(self.scrollLoadSource().slice(x, x + self.displayRangeLength));
  };

  self.resetScrollLoad = function() {
    self.scrollLoadSource = self.items;
    self.updateDisplayedItems();
  };

  self.isCollapsed = ko.observable(false);

  self.toggleSelectedCollapse = function() {
    if(!self.isCollapsed()) {
      self.displayedItems(self.displayedItems().filter(function(item) {
        return item.isSelected();
      }));
      self.scrollLoadSource = self.displayedItems;
      self.isCollapsed(true);
    }
    else {
      self.isCollapsed(false);
      self.resetScrollLoad();
    }
  };

  self.onScroll = function(target, ev) {
    var displayRangeDelta = 15;
    if($(ev.target).scrollLeft() == ev.target.scrollWidth - ev.target.clientWidth) {
      if(self.displayedItems().length < self.scrollLoadSource().length) {
        self.displayRangeLength += displayRangeDelta;
        self.updateDisplayedItems();
      } else {
        self.displayRangeLength = self.items().length + displayRangeDelta;
        var validate = self.items().length;
        API.queryTable('getRowPartial' , prepForTransport(self.row), self.items().length, 100).done(function(data) {
          if(self.items().length != validate) return false;
          var cols = data[0].columns;
          var keys = Object.keys(cols);
          var temp = [];
          for(var i=0; i<keys.length; i++) {
            var col = cols[keys[i]];
            temp.push(new ColumnRow({name: keys[i],
             timestamp: col.timestamp,
             value: col.value,
             parent: self}));
          }
          self.items(self.items().concat(temp));
        });
      }
    }
  };

  self.drop = function(cont) {
    function doDrop() {
      self.isLoading(true);
      return API.queryTable('deleteAllRow', self.row, "{}").complete(function() {
        app.views.tabledata.items.remove(self); //decouple later
        self.isLoading(false);
      });
    }

    (cont === true) ? doDrop() : confirm(i18n("Confirm Delete"), i18n('Delete row ') + self.row + i18n('? (This cannot be undone)'), doDrop);
  };

  self.setItems = function(cols) {
    var colKeys = Object.keys(cols);
    var items = [];
    for(var q=0; q<colKeys.length; q++) {
      items.push(new ColumnRow({name: colKeys[q],
             timestamp: cols[colKeys[q]].timestamp,
             value: cols[colKeys[q]].value,
             parent: self}));
    }
    self.items(items);
    return self.items();
  };

  self.selectAllVisible = function(){
    for(t=0; t<self.displayedItems().length; t++)
      self.displayedItems()[t].isSelected(true);
    return self;
  };

  self.deselectAllVisible = function(){
    for(t=0; t<self.displayedItems().length; t++)
      self.displayedItems()[t].isSelected(false);
    return self;
  };

  self.toggleSelectAllVisible = function() {
    if(self.selected().length != self.displayedItems().length)
      return self.selectAllVisible();
    return self.deselectAllVisible();
  };

  self.push = function(item) {
    var column = new ColumnRow(item);
    self.items.push(column);
  };

  var _reload = self.reload;
  self.reload = function(callback) {
  	logGA('get_row');
    _reload(function() {
      if(callback!=null)
        callback();
      self.isLoading(false);
    });
  };
};

var ColumnRow = function(options) {
  var self = this;
  ko.utils.extend(self,options);
  DataRow.apply(self,[options]);

  self.value = ko.observable(self.value);
  self.history = new CellHistoryPage({row: self.parent.row, column: self.name, timestamp: self.timestamp, items: []});
  self.drop = function(cont) {
    function doDrop() {
      logGA('filter_columns');
      self.parent.isLoading(true);
      return API.queryTable('deleteColumn', prepForTransport(self.parent.row), prepForTransport(self.name)).done(function(data) {
        self.parent.items.remove(self);
        if(self.parent.items().length > 0)
          self.parent.reload(); //change later
        self.parent.isLoading(false);
      });
    }
    (cont === true) ? doDrop() : confirm(i18n("Confirm Delete"), i18n("Are you sure you want to drop this column?"), doDrop);
  };

  self.reload = function(callback, skipPut) {
    self.isLoading(true);
    API.queryTable('get', prepForTransport(self.parent.row), prepForTransport(self.name), 'null').done(function(data) {
      if(data.length > 0 && !skipPut)
        self.value(data[0].value);
      if(typeof callback !== "undefined" && callback != null)
        callback();
      self.isLoading(false);
    });
  };

  self.value.subscribe(function(value) {
    //change transport prep to object wrapper
    logGA('put_column');
    API.queryTable('putColumn', prepForTransport(self.parent.row), prepForTransport(self.name), "hbase-post-key-" + JSON.stringify(value)).done(function(data) {
      self.reload(function(){}, true);
    });
    self.editing(false);
  });

  self.editing = ko.observable(false);

  self.isLoading = ko.observable(false); //move to baseclass
};

var SortDropDownView = function(options) {
  var self = this;
  options = ko.utils.extend({
    sortFields: {},
    target: null
  }, options);
  BaseModel.apply(self,[options]);

  self.target = options.target;
  self.sortAsc = ko.observable(true);
  self.sortAsc.subscribe(function(){self.sort()});
  self.sortField = ko.observable("");
  self.sortField.subscribe(function(){self.sort()});
  self.sortFields = ko.observableArray(Object.keys(options.sortFields)); // change to ko.computed?
  self.sortFunctionHash = ko.observable(options.sortFields);
  self.toggleSortMode = function() {
    self.sortAsc(!self.sortAsc());
  };
  self.sort = function() {
    if (!self.target || !(self.sortFields().length > 0)) return;
    self.target.sort(function(a, b) {
      return (self.sortAsc() ? 1 : -1) * self.sortFunctionHash()[self.sortField() ? self.sortField() : self.sortFields()[0]](a,b); //all sort functions must sort by ASC for default
    });
  };
};

var TableDataRow = function(options) {
  var self = this;
  options = ko.utils.extend({
    name:"",
    enabled:true
  }, options);
  DataRow.apply(self,[options]);

  self.name = options['name'];
  self.enabled = ko.observable(options['enabled']);
  self.toggle = function(viewModel,event){
    var action = [i18n('enable'), i18n('disable')][self.enabled() << 0], el = $(event.currentTarget);
    confirm(i18n("Confirm") + " " + action, i18n("Are you sure you want to") + " " + action + " " + i18n("this table?"), function()
    {
      el.showIndicator();
      return self[action](el).complete(function() {
        el.hideIndicator();
      });
    });
  };
  self.enable = function(el) {
    return API.queryCluster('enableTable',self.name).complete(function() {
      self.enabled(true);
    });
  };
  self.disable = function(callback) {
    return API.queryCluster('disableTable',self.name).complete(function() {
      self.enabled(false);
      if($.isFunction(callback)) callback();
    });
  };
  self.drop = function(el) {
    return API.queryCluster('deleteTable',self.name);
  };
};

var QuerySetPiece = function(options) {
  var self = this;
  options = ko.utils.extend({
    row_key: "null",
    scan_length: 1,
    prefix: false,
    columns: [],
    filter: null,
    onValidate: function(){}
  }, options);
  BaseModel.apply(self,[options]);

  self.row_key = ko.observable(options.row_key);
  self.scan_length = ko.observable(options.scan_length);
  self.columns = ko.observableArray(options.columns);
  self.prefix = ko.observable(options.prefix);
  self.filter = ko.observable(options.filter);
  self.editing = ko.observable(true);

  self.validate = function() {
    if(self.scan_length() <= 0 || self.row_key() == "")
      return app.views.tabledata.querySet.remove(self); //change later
    return options.onValidate();
  };
  self.row_key.subscribe(self.validate.bind());
  self.scan_length.subscribe(self.validate.bind());
};

var ColumnFamily = function(options) {
  this.name = options.name;
  this.enabled = ko.observable(options.enabled);
  this.toggle = function() {
    this.enabled(!this.enabled());
    app.views.tabledata.reload();
  };
}


//tagsearch
var tagsearch = function() {
  var self = this;
  self.tags = ko.observableArray();
  self.mode = ko.observable('idle');
  self.cur_input = ko.observable('');
  self.submitted = ko.observable(false);
  self.filters = ["KeyOnlyFilter ()", "FirstKeyOnlyFilter ()", "PrefixFilter ('row_prefix')", "ColumnPrefixFilter('column_prefix')", "MultipleColumnPrefixFilter('column_prefix', 'column_prefix', …, 'column_prefix')", "ColumnCountGetFilter (limit)", "PageFilter (page_size)", "ColumnPaginationFilter(limit, offset)", "InclusiveStopFilter('stop_row_key')", "TimeStampsFilter (timestamp, timestamp, ... ,timestamp)", "RowFilter (compareOp, 'row_comparator')", "QualifierFilter (compareOp, 'qualifier_comparator')", "QualifierFilter (compareOp,'qualifier_comparator')", "ValueFilter (compareOp,'value_comparator')", "DependentColumnFilter ('family', 'qualifier', boolean, compare operator, 'value comparator')", "DependentColumnFilter ('family', 'qualifier', boolean)", "DependentColumnFilter ('family', 'qualifier')", "SingleColumnValueFilter('family', 'qualifier', compare operator, 'comparator', filterIfColumnMissing_boolean, latest_version_boolean)", "SingleColumnValueFilter('family', 'qualifier', compare operator, 'comparator')", "SingleColumnValueExcludeFilter('family', 'qualifier', compare operator, 'comparator', latest_version_boolean, filterIfColumnMissing_boolean)", "SingleColumnValueExcludeFilter('family', 'qualifier', compare operator, 'comparator')", "ColumnRangeFilter ('minColumn', minColumnInclusive_bool, 'maxColumn', maxColumnInclusive_bool)"];
  self.hints = ko.observableArray([ {
      hint: i18n('End Query'),
      shortcut: ',',
      mode: ['rowkey', 'prefix', 'scan'],
      selected: false
    }, {
      hint: i18n('Prefix Scan'),
      shortcut: '*',
      mode: ['rowkey', 'columns'],
      selected: false
    }, {
      hint: i18n('Start Scan'),
      shortcut: '+',
      mode: ['rowkey', 'prefix', 'columns'],
      selected: false
    }, {
      hint: i18n('Start Select Columns'),
      shortcut: '[',
      mode: ['rowkey', 'prefix'],
      selected: false
    }, {
      hint: i18n('End Column/Family'),
      shortcut: ',',
      mode: ['columns'],
      selected: false
    }, {
      hint: i18n('End Select Columns'),
      shortcut: ']',
      mode: ['columns'],
      selected: false
    }, {
      hint: i18n('Column Range'),
      shortcut: ' to ',
      mode: ['columns'],
      selected: false
    },
    {
      hint: i18n('Start FilterString'),
      shortcut: '{',
      mode: ['rowkey'],
      selected: false
    },
    {
      hint: i18n('End FilterString'),
      shortcut: '}',
      mode: ['filter'],
      selected: false
    }
  ]);
  self.activeHints = ko.computed(function() {
    var ret = [];
    $(self.hints()).each(function(i, hint) {
      if (hint.mode.indexOf(self.mode()) > -1)
        ret.push(hint);
    });
    return ret;
  });
  self.activeHint = ko.observable(-1);
  self.modes = {
    'rowkey': {
      hint: i18n('Row Key Value'),
      type: i18n('String')
    },
    'scan': {
      hint: i18n('Length of Scan or Row Key'),
      type: i18n('Integer')
    },
    'columns': {
      hint: i18n('Column Family: Column Name'),
      type: i18n('String')
    },
    'prefix': {
      hint: i18n('Rows starting with'),
      type: i18n('String')
    },
    'filter': {
      hint: i18n('Thrift FilterString'),
      type: i18n('String')
    }
  }

  self.modeQueue = ['idle'];
  self.focused = ko.observable(false);
  self.activeSuggestions = ko.observableArray();
  self.activeSuggestion = ko.observable(-1);

  self.insertTag = function(tag) {
    var mode = tag.indexOf('+') != -1 ? 'scan' : 'rowkey';
    var tag = {value: tag, tag: mode} //parse mode
    self.tags.push(tag);
  }

  self.render = function(input, renderers) {
    var keys = Object.keys(renderers);
    for(var i=0; i<keys.length; i++) {
      input = input.replace(renderers[keys[i]].select, function(selected) {
        var hasMatched = false;
        var processed = selected.replace(renderers[keys[i]].tag, function(tagged) {
          hasMatched = true;
          return "<span class='" + keys[i] + " tagsearchTag' title='" + keys[i] + "' data-toggle='tooltip'>" + ('nested' in renderers[keys[i]] ? self.render(tagged, renderers[keys[i]].nested) : tagged) + "</span>";
        });
        if(hasMatched && renderers[keys[i]]['strip'])
          processed = processed.replace(renderers[keys[i]].strip, '');
        return processed;
      });
    }
    return input;
  };

  self.updateMode = function(value) {
    self.submitted(false);
    var selection = value.slice(0, self.selectionEnd());
    var endindex = selection.slice(selection.lastIndexOf(',')).indexOf(',');
    if(endindex == -1) endindex = selection.length;
    var lastbit = value.substring(selection.lastIndexOf(','), endindex).trim();
    if(lastbit == "," || lastbit == "") {
      self.mode('idle');
      return;
    }
    var tokens = "[]+*{}";
    var m = 'rowkey';
    for(var i=selection.length - 1; i>=0; i--) {
      if(tokens.indexOf(selection[i]) != -1) {
        if(selection[i] == '{')
          m = 'filter';
        else if(selection[i] == '[')
          m = 'columns';
        else if(selection[i] == ']' || selection[i] == '}')
          m = 'rowkey';
        else if(selection[i] == '+')
          m = 'scan';
        else if(selection[i] == '-')
          m = 'prefix';
        break;
      }
    }
    self.mode(m.trim());
  };

  self.selectionStart = ko.observable(0);
  self.selectionEnd = ko.observable(0);

  self.hintText = ko.computed(function() {
    var pre, s, e;
    try {
      var r = window.getSelection().getRangeAt(0);
      pre = r.startContainer.nodeValue;
      s = r.startOffset;
      e = r.endOffset;
      return pre.slice(0, s) + "<span class='selection'>" + pre.slice(s, e) + "</span>" + pre.slice(e);
    } catch (e) {
      var value = self.cur_input();
      var selection = value.slice(0, self.selectionEnd());
      var index = selection.lastIndexOf(',') + 1;
      var endindex = value.slice(index).indexOf(',');
      endindex = endindex == -1 ? value.length : endindex;
      pre = value.substring(index, index + endindex);
      s = self.selectionStart() - index;
      e = self.selectionEnd() - index;
      if(s == e)
        e += 1;
      s = s < 0 ? 0 : s;
      e = e > pre.length ? pre.length : e;
    }
    return pre.slice(0, s) + "<span class='selection'>" + pre.slice(s, e) + "</span>" + pre.slice(e);
  });

  self.onKeyDown = function(target, ev) {
    if(ev.keyCode == 13 && self.cur_input().slice(self.cur_input().lastIndexOf(',')).trim() != ",") {
      if(self.activeSuggestion() > -1) {
        self.replaceFocusNode(self.activeSuggestions()[self.activeSuggestion()]);
        self.activeSuggestion(-1);
        setTimeout(function() {
          var s = self.cur_input(), r;
          if(s.lastIndexOf('(') != -1 && s.lastIndexOf(')') != -1) {
            r = setCursor($('#search-tags')[0], s.lastIndexOf('(') + 1);
            r.setEnd(r.endContainer, r.startOffset + (s.lastIndexOf(')') - s.lastIndexOf('(') - 1));
          } else {
            r = setCursor($('#search-tags')[0], s.length);
          }
          var sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(r);
        }, 1);
      } else {
        self.evaluate();
      }
      return false;
    } else if (ev.keyCode == 219) {
      setTimeout(function() {
        var ep = getEditablePosition($('#search-tags')[0], true);
        self.cur_input(self.cur_input().slice(0, ep) + (ev.shiftKey ? '}' : ']') + self.cur_input().slice(ep));
      }, 1);
    } else if (ev.keyCode == 40) {
      if(self.activeSuggestion() < self.activeSuggestions().length - 1)
        self.activeSuggestion(self.activeSuggestion() + 1);
      return false;
    } else if(ev.keyCode == 38) {
      if(self.activeSuggestion() > 0)
        self.activeSuggestion(self.activeSuggestion() - 1);
      return false;
    }
    setTimeout(self.updateMenu, 1);
    return true;
  };

  self.updateMenu = function() {
    self.activeSuggestion(-1);
    try{
      var pos = getEditablePosition(document.getElementById('search-tags'));
      self.selectionStart(pos);
      self.selectionEnd(pos);
    } catch (err) {}
	  self.updateMode(self.cur_input());
    self.updateSuggestions();
  };

  self.replaceFocusNode = function(text) {
    window.getSelection().getRangeAt(0).startContainer.nodeValue = text;
  };

  self.updateSuggestions = function() {
    var val = window.getSelection().getRangeAt(0).startContainer.nodeValue;
    switch(self.mode()) {
      case 'filter':
        var focus = val.replace(/\{|\}|\s|&[^;]+?;/g,"").split(searchRenderers.rowkey.nested.filter.nested.linker.select).slice(-1)[0];
        if(focus != "") {
          self.activeSuggestions(self.filters.filter(function(a) {
            return a.toLowerCase().replace(" ","").indexOf(focus.toLowerCase()) != -1;
          }));
        } else {
          self.activeSuggestions([]);
        }
        return;
      case 'rowkey':
        var validate = window.getSelection().getRangeAt(0).startContainer.nodeValue;
        function cancel() {
          return window.getSelection().getRangeAt(0).startContainer.nodeValue != validate;
        }
        function callback() {
          if(cancel()) return false;
          if(validate.trim() != "") {
            API.queryTable('getAutocompleteRows', 10, prepForTransport(validate.trim())).done(function(data) {
              if(cancel()) return false;
              self.activeSuggestions(data);
            });
          }
        }
        setTimeout(callback, 200);
        return;
      default:
        self.activeSuggestions([]);
        return;
    }
  }

  self.evaluate = function() {
    table_search(self.cur_input());
    self.submitted(true);
    self.mode('idle');
  };

  $('#search-tags').blur(function(){
  	self.focused(false);
  });

  self.doBlur = function() {
  	if(self.cur_input().trim() == "") {
  	  function doClick() {
        if(self.cur_input().trim() != "") return false;
        setTimeout(function() {
        	$('#search-tags').focus();
        }, 1);
      }
      $('#search-tags').html('<small>' + $('#search-tags').data("placeholder") + '</small>').one('click', doClick).find('small').on('mousedown', doClick);
    }
  }

  $('#search-tags').focus(function(){
  	self.focused(true);
  });
};

var CellHistoryPage = function(options) {
  var self = this;

  self.items = ko.observableArray(options.items);
  self.loading = ko.observable(false);

  self.reload = function(timestamp, append) {
    if(!timestamp)
      timestamp = options.timestamp
    API.queryTable("getVerTs", prepForTransport(options.row), prepForTransport(options.column), timestamp, 10, 'null').done(function(res) {
      self.loading = ko.observable(true);
      if(!append)
        self.items(res);
      else
        self.items(self.items() + res);
      self.loading = ko.observable(false);
    });
  };

  self.pickHistory = function(data) {
    data.history = self;
    if(!ko.isObservable(data.value))
      data.value = ko.observable(data.value);
    launchModal('cell_edit_modal',{ content: data, mime: detectMimeType(data.value()), readonly: true })
  };
};