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

function s4() {
  return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
}

function UUID() {
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
}

var Column = function (size, rows) {
  var self = this;

  self.rowPrototype = Row;
  self.id = ko.observable(UUID());
  self.size = ko.observable(size);
  self.rows = ko.observableArray(rows);

  self.drops = ko.observableArray(["temp"]);
  self.klass = ko.computed(function () {
    return "card card-home card-column span" + self.size();
  });
  self.percWidth = ko.observable();
  self.addEmptyRow = function (atBeginning, atIndex) {
    return self.addRow(null, atBeginning, atIndex);
  };
  self.addRow = function (row, atBeginning, atIndex) {
    if (typeof row == "undefined" || row == null) {
      row = new self.rowPrototype([], viewModel); // Hacky but needed when a new row is deleted
    }

    if (typeof atIndex != "undefined" && atIndex != null) {
      self.rows.splice(atIndex, 0, row);
    }
    else {
      if (typeof atBeginning == "undefined" || atBeginning == null || !atBeginning) {
        self.rows.push(row);
      }
      else {
        self.rows.unshift(row);
      }
    }
    return row;
  };
}

var Row = function (widgets, vm, columns) {
  var self = this;

  self.columnPrototype = Column;
  self.id = ko.observable(UUID());
  self.widgets = ko.observableArray(widgets);
  self.columns = ko.observableArray(columns ? columns : []);
  self.columns.subscribe(function (val) {
    self.columns().forEach(function (col) {
      col.percWidth((100 - self.columns().length * 0.5) / self.columns().length);
    });
  });

  self.addWidget = function (widget) {
    self.widgets.push(widget);
  };

  self.addEmptyColumn = function (atBeginning) {
    if (self.columns().length == 0) {
      var _col = self.addColumn(null, atBeginning);
      if (self.widgets().length > 0) {
        var _row = _col.addEmptyRow();
        self.widgets().forEach(function (widget) {
          _row.addWidget(widget);
        });
        self.widgets([]);
      }
    }
    return self.addColumn(null, atBeginning);
  };

  self.addColumn = function (column, atBeginning) {
    if (typeof column == "undefined" || column == null) {
      var _size = Math.max(1, Math.floor(12 / (self.columns().length + 1)));
      column = new self.columnPrototype(_size, []); // Hacky but needed when a new row is deleted
      self.columns().forEach(function (col) {
        col.size(_size);
      });
    }
    if (typeof atBeginning == "undefined" || atBeginning == null || !atBeginning) {
      self.columns.push(column);
    }
    else {
      self.columns.unshift(column);
    }
    return column;
  };

  self.move = function (from, to) {
    try {
      vm.columns()[to].addRow(self);
      vm.columns()[from].rows.remove(self);
    }
    catch (exception) {
    }
  }

  self.moveDown = function (col, row) {
    var _i = col.rows().indexOf(row);
    if (_i < col.rows().length - 1) {
      var _arr = col.rows();
      col.rows.splice(_i, 2, _arr[_i + 1], _arr[_i]);
    }
  }

  self.moveUp = function (col, row) {
    var _i = col.rows().indexOf(row);
    if (_i >= 1) {
      var _arr = col.rows();
      col.rows.splice(_i - 1, 2, _arr[_i], _arr[_i - 1]);
    }
  }

  self.remove = function (col, row) {
    $.each(self.columns(), function (i, column) {
      $.each(column.rows(), function (j, row) {
        $.each(row.widgets(), function (k, widget) {
          vm.removeWidget(widget);
        });
      });
    });

    $.each(self.widgets(), function (i, widget) {
      vm.removeWidget(widget);
    });
    col.rows.remove(row);
  }

  self.autosizeWidgets = function () {
    $.each(self.widgets(), function (i, widget) {
      widget.size(Math.floor(12 / self.widgets().length));
    });
  }
}


// A widget is generic. It has an id that refer to another object (e.g. facet) with the same id.
var Widget = function (params) {
  var self = this;

  self.extend = function () {
    return self;
  }

  self.size = ko.observable(params.size).extend({ numeric: 0 });

  self.name = ko.observable(params.name);
  self.id = ko.observable(params.id);
  self.widgetType = ko.observable(typeof params.widgetType != "undefined" && params.widgetType != null ? params.widgetType : "empty-widget");
  self.properties = ko.observable(typeof params.properties != "undefined" && params.properties != null ? params.properties : {});
  self.offset = ko.observable(typeof params.offset != "undefined" && params.offset != null ? params.offset : 0).extend({ numeric: 0 });
  self.isLoading = ko.observable(typeof params.loading != "undefined" && params.loading != null ? params.loading : false);

  self.klass = ko.computed(function () {
    return "card card-widget span" + self.size() + (self.offset() * 1 > 0 ? " offset" + self.offset() : "");
  });

  self.expand = function () {
    self.size(self.size() + 1);
    $("#wdg_" + self.id()).trigger("resize");
  }

  self.compress = function () {
    self.size(self.size() - 1);
    $("#wdg_" + self.id()).trigger("resize");
  }

  self.moveLeft = function () {
    self.offset(self.offset() - 1);
  }

  self.moveRight = function () {
    self.offset(self.offset() + 1);
  }

  self.remove = function (row, widget) {
    if (params.vm != null) {
      params.vm.removeWidget(widget);
    }
    row.widgets.remove(widget);
  }
};

Widget.prototype.clone = function () {
  return new Widget({
    size: this.size(),
    id: UUID(),
    name: this.name(),
    widgetType: this.widgetType()
  });
};

function fullLayout(vm) {
  setLayout([12], vm);
}

function oneSixthLeftLayout(vm) {
  setLayout([2, 10], vm);
}

function oneFourthLeftLayout(vm) {
  setLayout([3, 9], vm);
}

function oneThirdLeftLayout(vm) {
  setLayout([4, 8], vm);
}

function halfHalfLayout(vm) {
  setLayout([6, 6], vm);
}

function oneThirdRightLayout(vm) {
  setLayout([8, 4], vm);
}

function oneFourthRightLayout(vm) {
  setLayout([9, 3], vm);
}

function oneSixthRightLayout(vm) {
  setLayout([10, 2], vm);
}


function setLayout(colSizes, vm) {
  // Save previous widgets
  var _allRows = [];
  $(vm.columns()).each(function (cnt, col) {
    var _tRows = [];
    $(col.rows()).each(function (icnt, row) {
      if (row.widgets().length > 0 || (typeof vm.isNested != "undefined" && vm.isNested())) {
        _tRows.push(row);
      }
    });
    _allRows = _allRows.concat(_tRows);
  });

  var _cols = [];
  var _highestCol = {
    idx: -1,
    size: -1
  };
  $(colSizes).each(function (cnt, size) {
    _cols.push(new Column(size, []));
    if (size > _highestCol.size) {
      _highestCol.idx = cnt;
      _highestCol.size = size;
    }
  });
  if (_allRows.length > 0 && _highestCol.idx > -1) {
    _cols[_highestCol.idx].rows(_allRows);
  }

  $(_cols).each(function (cnt, col) {
    if (col.rows().length == 0) {
      col.rows([new Row([], vm)]);
    }
  });

  vm.columns(_cols);

  $(document).trigger("setLayout");
}

function ChangeTracker(objectToTrack, hashFunction) {
  hashFunction = hashFunction || ko.toJSON;
  var lastCleanState = ko.observable(hashFunction(objectToTrack));

  var result = {
    somethingHasChanged: ko.dependentObservable(function () {
      $(document).trigger("viewmodelHasChanged");
      return hashFunction(objectToTrack) != lastCleanState()
    }),
    markCurrentStateAsClean: function () {
      lastCleanState(hashFunction(objectToTrack));
    }
  };

  return function () {
    return result
  }
}
