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

var BaseModel = function() {
}

var ListViewModel = function(options) {
  var self = this, _defaults = {
    items: [],
    reload: function() {

    },
    sortFields: {}
  };
  options = ko.utils.extend(_defaults,options);
  BaseModel.apply(this,[options]);

  self.canWrite = ko.observable(options.canWrite);
  self.items = ko.observableArray(options.items);
  self.sortDropDown = new SortDropDownView({sortFields: options.sortFields, target: self.items});
  self.selectAll = function(){
    for(t=0; t<self.items().length; t++)
      self.items()[t].isSelected(true);
    return self;
  };
  self.deselectAll = function() {
    for(q=0; q<self.items().length; q++)
      self.items()[q].isSelected(false);
    return self;
  };
  self.toggleSelectAll = function() {
    if(self.selected().length != self.items().length)
      return self.selectAll();
    return self.deselectAll();
  };
  self.selected = function(){
    var acc = [];
    var items = self.items();
    for(i=0; i<items.length; i++) {
      if(items[i].isSelected())
        acc.push(items[i]);
    }
    return acc;
  };
  self.batchSelected = function(action) {
    var selected = self.selected();
    var batchCount = 0;

    for(q=0; q<selected.length; q++) {
      self.isLoading(true);
      var call = action.apply(selected[q], arguments);
      var callback = function() {
        batchCount++;
        if(batchCount >= selected.length) {
          self.reload();
          self.isLoading(false);
        }
      };
      if(call === true) {
        callback();
      } else if (call != null && 'complete' in call) {
        call.complete(callback);
      } else {
        self.isLoading(false);
      }
    }
  };
  self.batchSelectedAlias = function(actionAlias) {
    self.batchSelected(function() {
      return this[actionAlias]();
    });
  };
  self.enableSelected = function() {
    self.batchSelected(function() {
      return this.enable();
    });
  };
  self.disableSelected = function() {
    confirm("Confirm Disable", "Disable these tables?", function() {
      self.batchSelected(function() {
        return this.disable();
      });
    });
  };
  self.dropSelected = function() {
    confirm("Confirm Delete", "Are you sure you want to drop the selected items? (WARNING: This cannot be undone!)", function() {
      self.batchSelected(function() {
        var s = this;
        self.droppedTables.push(s);
        if(s.enabled && s.enabled()) {
          self.isLoading(true);
          return s.disable(function() {
            s.drop(true);
          });
        } else {
          return s.drop(true);
        }
      });
    });
  };
  self.reload = function(callback){
    self.items.removeAll();
    self.isLoading(true);
    options.reload.apply(self,[function() {
      if(callback!=null)
        callback();
      self.sortDropDown.sort();
      self.isLoading(false);
    }]);
  };
  self.searchQuery = ko.observable("");
  self.isLoading = ko.observable(false);
  self.isReLoading = ko.observable(false);
  self.droppedTables = [];
};

var DataRow = function(options) {
  var self = this;
  ko.utils.extend(self,options); //applies options on itself
  BaseModel.apply(self,[options]);

  self.isSelected = ko.observable(false);
  self.select = function(){self.isSelected(!self.isSelected());};
};