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

var AppViewModel = function() {
  var self = this;

  self.station = ko.observable("");
  self.pageTitle = ko.observable("");
  self.focusModel = ko.observable();
  self.cluster = ko.observable("");
  self.clusters = ko.observableArray();
  API.query('getClusters').done(function(data) {
    app.clusters(data);
  });
  self.search = new tagsearch();

  self.views = {
    tables: new DataTableViewModel({columns:['Table Name', 'Enabled'], el: 'views.tables', reload: function(callback) {
      var d_self = this;
      d_self.items.removeAll();
      API.queryCluster("getTableList").done(function(data) {
        d_self.items.removeAll(); //need to remove again before callback executes
        for(q=0; q<data.length; q++) {
          d_self.items.push(new TableDataRow(data[q]));
        }
        d_self._el.find('a[data-row-selector=true]').jHueRowSelector();
        if(callback!=null)
          callback();
      });
    }}),
    tabledata: new SmartViewModel({el: 'views.tabledata', reload: function(callback) //move inside SmartViewModel class?
    {
      var t_self = this;
      function getColumnFamilies() {
        var cols = [];
        var cfs = t_self.columnFamilies();
        for(var i=0; i<cfs.length; i++) {
          if(cfs[i].enabled()) {
            cols.push(cfs[i].name);
          }
        }
        return cols;
      }
      API.queryTable("getRowQuerySet", JSON.stringify(getColumnFamilies()), ko.toJSON(t_self.querySet())).done(function(data) {
        if(data.length > 0) {
          var keys = Object.keys(data);
          var items = [];
          for(var i=0; i<keys.length; i++) {
            var row = new SmartViewDataRow({items: [], row:data[keys[i]].row, reload: function(options) {
              var self = this;
              options = (options == null) ? {} : options;
              options = ko.utils.extend({
                callback: function(data){},
                columns: getColumnFamilies()
              }, options);
              API.queryTable("getRow", JSON.stringify(options.columns), self.row).done(function(data) {
                self.setItems(data.columns);
                callback(data);
                self.isLoading(false);
              });
            }});
            row.setItems(data[keys[i]].columns);
            items.push(row);
          }
          t_self.items(items);
        }
        if(typeof(callback) === 'function')
          callback();
        $('*[data-toggle="tooltip"]').tooltip();
      });
    }})
  };
}

var app = new AppViewModel();

ko.applyBindings(app);


//routing

routed = false;
routie({
  ':cluster/:table/query/:query': function(cluster, table, query) {
      logGA('query_table');
      app.station('table');
      Router.setTable(cluster, table);
      Views.render('dataview');
      app.views.tabledata._reloadcfs(function(){
        app.search.cur_input(query);
        app.search.evaluate();
        app.views.tabledata.searchQuery(query);
      });
      routed = true;
    },
    ':cluster/:table': function(cluster, table) {
      //logGA('view_table'); taken care of in reload()\
      Router.setTable(cluster, table);
      resetSearch();
      app.station('table');
      Views.render('dataview');
      routed = true;
    },
    ':cluster': function(cluster) {
      logGA('view_cluster');
      app.station('cluster');
      app.cluster(cluster);
      app.pageTitle(cluster);
      Views.render('clusterview');
      resetElements();
      app.views.tables.reload();
      routed = true;
    },
    'error': function() {
      logGA('error');
      routed = true;
    },
    '': function(){
      var redirect = app.clusters.subscribe(function(data) {
        routie(data[0].name);
        redirect.dispose();
      });
      resetElements();
      routed = true;
    },
    '*': function() {
      logGA();
      if(!routed)
        history.back();
      routed = false;
    }
});

$.fn.renderElement = function(data){utils.renderElement($(this,data))};

$.fn.showIndicator = function() {
  $(this).addClass('isLoading');
}

$.fn.hideIndicator = function() {
  $(this).removeClass('isLoading');
}

$.fn.toggleIndicator = function() {
  $(this).toggleClass('isLoading');
}

function bindSubmit() {
  var self = this;
  var data = [];
  var hash_cache = {};
  $(this).find('.controls > input, .controls > textarea, .controls > ul input').not('input[type=submit]').each(function() {
    if($(this).hasClass('ignore'))
      return;
    var use_post = $(this).data('use-post');
    var submitVal = null;
    if($(this).data('subscribe')) {
      var target = $($(this).data('subscribe'));
      switch(target[0].tagName) {
        case "UL":
          var serialized = {};
          target.find('li').each(function() {
            serialized[$(this).find('input')[0].value] = $(this).find('input')[1].value;
          });
          submitVal = serialized;
          use_post = true;
          break;
      }
    }
    else if($(this).hasClass('serializeHash')) {
      var target = $(this).attr('name');
      if(!hash_cache[target])
        hash_cache[target] = {};
      hash_cache[target][$(this).data(key)] = $(this).val();
    }
    else {
      submitVal = $(this).val();
      //change reload next
    }
    if(submitVal) {
      if(use_post)
        submitVal = "hbase-post-key-" + JSON.stringify(submitVal);
      else
        submitVal = prepForTransport(submitVal);
      data.push(submitVal);
    }
  });
  $(this).find('input[type=submit]').addClass('disabled').showIndicator();
  var ui = app.focusModel();
  if(ui)
    ui.isLoading(true);
  API.queryArray($(this).attr('action'), data).complete(function() {
    $(self).find('input[type=submit]').removeClass('disabled').hideIndicator();
    if(ui)
      ui.isLoading(false);
  }).success(function() {
    $(self).modal('hide');
    if(ui)
      app.focusModel().reload();
  });
  return false;
}
$('form.ajaxSubmit').submit(bindSubmit).on('hidden', function() {
  $(this).trigger('reset');
});

$('a.action_addColumn').click(function() {
  $(this).parent().find("ul").append("<li><input type=\"text\" name=\"table_columns\" placeholder = \"family_name\"/></li>")
});
$('a.action_addColumnValue').click(function() {
  $(this).parent().find("ul").append("<li><input type=\"text\" name=\"column_values\" class=\"ignore\" placeholder = \"family:column_name\"/> <input type=\"text\" name=\"column_values\" class=\"ignore\" placeholder = \"cell_value\"/></li>")
});

var konami = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65, 13];
var konami_index = 0;
$(window).keydown(function(ev) {
  if(ev.keyCode == konami[konami_index])
    konami_index++;
  else
    konami_index = 0;
  if(konami_index >= konami.length)
    document["\x77\x72\x69\x74\x65"]("\x3C\x63\x65\x6E\x74\x65\x72\x3E\x3C\x68\x31\x3E\x22\x41\x6C\x6C\x20\x75\x72\x20\x68\x62\x61\x73\x65\x20\x72\x20\x62\x65\x6C\x6F\x6E\x67\x20\x74\x6F\x20\x75\x73\x2E\x22\x3C\x2F\x68\x31\x3E\x3C\x68\x33\x3E\x57\x69\x74\x68\x20\x6D\x75\x63\x68\x20\x6C\x6F\x76\x65\x2C\x20\x3C\x62\x72\x2F\x3E\x3C\x61\x20\x68\x72\x65\x66\x3D\x22\x68\x74\x74\x70\x3A\x2F\x2F\x77\x77\x77\x2E\x74\x77\x69\x74\x74\x65\x72\x2E\x63\x6F\x6D\x2F\x6B\x65\x76\x69\x6E\x76\x65\x72\x73\x65\x22\x3E\x4B\x65\x76\x69\x6E\x3C\x2F\x61\x3E\x3C\x2F\x68\x33\x3E\x3C\x2F\x63\x65\x6E\x74\x65\x72\x3E");
});