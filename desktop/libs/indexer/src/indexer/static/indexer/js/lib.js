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

// Start Models

var Collection = function(name) {
  var self = this;

  self.name = ko.observable(name).extend({'errors': null});
  self.fields = ko.observableArray();

  // Metadata
  self.uniqueKeyField = ko.observable().extend({'errors': null});
  self.df = ko.observable().extend({'errors': null});
  self.hasHueCollection = ko.observable(true).extend({'errors': null});
  self.hasSolrCollection = ko.observable(true).extend({'errors': null});
  self.isCoreOnly = ko.observable(false);
  self.isAlias = ko.observable(false);
  self.collections = ko.observable([]);

  self.removeField = function(field) {
    if (field.name() != self.uniqueKeyField()) {
      self.fields.remove(field);
    }
  };

  self.addField = function(name, type) {
    self.fields.push(new Field(self, name, type));
  };

  self.newField = function() {
    self.addField('', 'text_general');
  };

  self.newIdField = function() {
    self.fields.push(new Field(self, 'id', 'string', true, true, true));
    self.uniqueKeyField('id');
  };

  self.setData = function(data_json) {
    self.data(data_json);
  };
};

var Field = function(collection, name, type, required, indexed, stored, mockId) {
  var self = this;

  indexed = (indexed == undefined) ? true : !!indexed;
  required = (required == undefined) ? true : !!required;
  stored = (stored == undefined) ? true : !!stored;
  mockId = (mockId == undefined) ? false: !!mockId;

  self.name = ko.observable(name).extend({'errors': null});
  self.type = ko.observable(type).extend({'errors': null});
  self.required = ko.observable(required).extend({'errors': null});
  self.indexed = ko.observable(indexed).extend({'errors': null});
  self.stored = ko.observable(stored).extend({'errors': null});
  self.mockId = ko.observable(mockId).extend({'errors': null});

  // Metadata
  self.saved = ko.observable(false);

  self.uniqueKeyField = ko.computed({
    'read': function() {
      return collection.uniqueKeyField() == self.name();
    },
    'write': function(value) {
      collection.uniqueKeyField(self.name());
      self.indexed(true);
    }
  });
  self.df = ko.computed({
    'read': function() {
      return collection.df() == self.name();
    },
    'write': function(value) {
      collection.df(self.name());
      self.indexed(true);
    }
  });
  self.editable = ko.computed(function() {
    return !self.uniqueKeyField() && self.name() != '_version_';
  });

  self.remove = function() {
    collection.removeField(self);
  };
};

var HiveDatabase = function(name) {
  var self = this;

  self.name = ko.observable(name).extend({'errors': null});
  self.tables = ko.observableArray();
};

var HiveTable = function(name) {
  var self = this;

  self.name = ko.observable(name).extend({'errors': null});
  self.columns = ko.observableArray();
};

var HBaseCluster = function(name) {
  var self = this;

  self.name = ko.observable(name).extend({'errors': null});
  self.tables = ko.observableArray();
};

var HBaseTable = function(name) {
  var self = this;

  self.name = ko.observable(name).extend({'errors': null});
};

// End Models


// Start Wizard

var Page = function(url, name, next, validate_fn) {
  var self = this;

  self.name = ko.observable(name);
  self.url = ko.observable(url);
  self.next = ko.observable(next);

  self.validate = validate_fn || function() { return true; };
};

var Wizard = function() {
  var self = this;

  self.rootPage = ko.observable();
  self.currentPage = ko.observable(self.rootPage());
  // Stack of previous pages.
  self.previousPages = ko.observableArray();
  self.pages = {};

  self.hasPrevious = ko.computed(function() {
    return self.previousPages().length > 0;
  });

  self.hasNext = ko.computed(function() {
    return !!(self.currentPage() && self.currentPage().next());
  });

  self.pageList = ko.computed(function() {
    var page = self.rootPage();
    var pages = [];
    while(page) {
      pages.push(page);
      page = self.pages[page.next()];
    }
    return pages;
  });

  self.previousUrl = ko.computed(function() {
    if (self.previousPages().length > 0) {
      return self.previousPages()[self.previousPages().length - 1].url();
    } else {
      return null;
    }
  });

  self.nextUrl = ko.computed(function() {
    if (self.currentPage() && self.currentPage().next()) {
      return self.currentPage().next();
    } else {
      return null;
    }
  });

  self.next = function() {
    if (self.hasNext() && self.currentPage().validate()) {
      self.previousPages.push(self.currentPage());
      self.currentPage(self.pages[self.currentPage().next()]);
    }
  };

  self.previous = function() {
    if (self.hasPrevious()) {
      self.currentPage(self.previousPages.pop());
    }
  };

  self.setPageByUrl = function(url) {
    var urls = ko.utils.arrayMap(self.pageList(), function(page) {
      return page.url();
    });
    var previousUrls = ko.utils.arrayMap(self.previousPages(), function(page) {
      return page.url();
    });
    if ($.inArray(url, previousUrls) != -1) {
      var previousPageURL = null;
      self.previous();
      while(self.hasPrevious() && self.currentPage().url() != url && self.currentPage().url() != previousPageURL) {
        previousPageURL = self.currentPage().url();
        self.previous();
      }
    } else if ($.inArray(url, urls) != -1) {
      var previousPageURL = null;
      while(self.hasNext() && self.currentPage().url() != url && self.currentPage().url() != previousPageURL) {
        previousPageURL = self.currentPage().url();
        self.next();
      }
    }
  };

  self.getPage = function(url, name, next, validate_fn) {
    self.pages;
    if (!self.pages[url]) {
      self.pages[url] = new Page(url, name, next, validate_fn);
    }
    return self.pages[url];
  };
};

// End Wizard


// Start utils

ko.bindingHandlers.routie = {
  init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    $(element).click(function() {
      var obj = ko.utils.unwrapObservable(valueAccessor());
      var url = null;
      var bubble = false;
      if ($.isPlainObject(obj)) {
        url = obj.url;
        bubble = !!obj.bubble;
      } else {
        url = obj;
      }
      routie(url);
      return bubble;
    });
  }
};

ko.bindingHandlers.filter = {
  init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    var obj = ko.utils.unwrapObservable(valueAccessor());
    var test_fn = obj.test;
    var list = obj.list;
    var filteredList = obj.filteredList;
    filteredList(list());
    $(element).keyup(function(e) {
      if (e.target.value) {
        filteredList(ko.utils.arrayFilter(list(), function(obj) {
          return test_fn(obj, e.target.value);
        }));
      } else {
        filteredList(list());
      }
      return (obj.bubble == undefined) ? false : obj.bubble;
    });
  }
};

ko.extenders.errors = function(target, options) {
  target.errors = ko.observableArray();
  target.errors.remove = function(obj) {
    var index = target.errors().indexOf(obj);
    if (index > -1) {
      target.errors.splice(index, 1);
    }
  };
  return target;
};

ko.extenders.selectable = function(target, options) {
  target.selected = ko.observable(false);
  target.toggleSelect = function() {
    target.selected(!target.selected());
  };
  return target;
};

ko.bindingHandlers.chosen = {
  init: function(element, options) {
    $(element).chosen(options);
  },
  update: function(element) {
    $(element).trigger('chosen:updated');
  }
};

ko.bindingHandlers.editableText = {
  init: function(element, valueAccessor) {
    $(element).attr('contenteditable', true);
    $(element).on('click', function() {
      $(element).focus();
    });
    $(element).on('blur', function() {
      var observable = valueAccessor();
      observable( $(this).text() );
    });
  },
  update: function(element, valueAccessor) {
    var value = ko.utils.unwrapObservable(valueAccessor());
    $(element).text(value);
  }
};

function chooseUniqueKey(collection) {
  function fieldChooser(fields) {
    if (fields.length > 0) {
      fields[0].uniqueKeyField(true);
      return true;
    }
    return false;
  }

  // Find a field named "ID"
  if (fieldChooser(ko.utils.arrayFilter(collection.fields(), function(field) {
    return field.name().toLowerCase() == 'id';
  }))) return;

  // Find a long
  if (fieldChooser(ko.utils.arrayFilter(collection.fields(), function(field) {
    return $.inArray(field.type().toLowerCase(), ['long', 'tlong', 'plong']) != -1;
  }))) return;

  // Find an integer
  if (fieldChooser(ko.utils.arrayFilter(collection.fields(), function(field) {
    return $.inArray(field.type().toLowerCase(), ['int', 'tint', 'pint']) != -1;
  }))) return;

  // Find first indexed field
  if (fieldChooser(ko.utils.arrayFilter(collection.fields(), function(field) {
    return field.indexed();
  }))) return;

  // Choose a field
  fieldChooser(collection.fields());
}

function chooseDefaultField(collection) {
  function fieldChooser(fields) {
    if (fields.length > 0) {
      fields[0].df(true);
      return true;
    }
    return false;
  }

  // Find a field named "text"
  if (fieldChooser(ko.utils.arrayFilter(collection.fields(), function(field) {
    return field.name().toLowerCase() == 'text';
  }))) return;

  // Find a text field
  if (fieldChooser(ko.utils.arrayFilter(collection.fields(), function(field) {
    return field.type().toLowerCase().substring(0, 4) == 'text';
  }))) return;

  // Find a string field
  if (fieldChooser(ko.utils.arrayFilter(collection.fields(), function(field) {
    return field.type().toLowerCase() == 'string';
  }))) return;

  // Find first indexed field
  if (fieldChooser(ko.utils.arrayFilter(collection.fields(), function(field) {
    return field.indexed();
  }))) return;

  // Choose a field
  fieldChooser(collection.fields());
}

function getCharacterLabel(character) {
  var LABELS = {
    '\t': '\\t'
  };
  if (LABELS[character]) {
    return LABELS[character];
  } else {
    return character;
  }
}

function validateNotNull(obs, message) {
  var ret = true;
  if (!obs()) {
    obs.errors.push(message);
    ret = false;
  } else {
    obs.errors.remove(message);
  }
  return ret;
}

// End utils
