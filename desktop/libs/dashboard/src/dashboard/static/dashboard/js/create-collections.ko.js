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

var Collection = function(viewModel) {
  var self = this;

  self.name = ko.observable().extend({'errors': null});
  self.fields = ko.observableArray();

  self.removeField = function(field) {
    self.fields.remove(field);
  };

  self.addField = function(name, type) {
    self.fields.push(new Field(self, name, type));
  };

  self.newField = function() {
    self.addField('', '');
  };

  self.setData = function(data_json) {
    self.data(data_json);
  };
};

var Field = function(collection, name, type) {
  var self = this;

  self.name = ko.observable(name).extend({'errors': null});
  self.type = ko.observable(type).extend({'errors': null});

  self.remove = function() {
    collection.removeField(self);
  };
};

// End Models


// Start Wizard

var Page = function(name, url, validate_fn) {
  var self = this;

  self.name = ko.observable(name);
  self.url = ko.observable(url);

  self.validate = validate_fn || function() {return true;};
};

var Wizard = function(pages) {
  var self = this;

  self.pages = ko.observableArray();

  $.each(pages, function(index, page) {
    self.pages.push(new Page(page.name, page.url, page.validate));
  });

  self.index = ko.observable(0);

  self.hasPrevious = ko.computed(function() {
    return self.index() > 0;
  });

  self.hasNext = ko.computed(function() {
    return self.index() + 1 < self.pages().length;
  });

  self.current = ko.computed(function() {
    return self.pages()[self.index()];
  });

  self.next = function() {
    if (self.hasNext() && self.pages()[self.index()].validate()) {
      return self.pages()[self.index() + 1];
    } else {
      return self.pages()[self.index()];
    }
  };

  self.previous = function() {
    if (self.hasPrevious()) {
      return self.pages()[self.index() - 1];
    }
  };

  self.setIndexByUrl = function(url) {
    $.each(self.pages(), function(index, step) {
      if (step.url() == url) {
        self.index(index);
      }
    });
  };
};

// End Wizard

var CreateCollectionViewModel = function(steps) {
  var self = this;

  var fieldTypes = [
    'string',
    'integer',
    'float',
    'boolean'
  ];
  var fieldSeparators = [
    ',',
    '\t'
  ];

  // Models
  self.fieldTypes = ko.mapping.fromJS(fieldTypes);
  self.fieldSeparators = ko.mapping.fromJS(fieldSeparators);
  self.collection = new Collection(self);
  self.fieldSeparator = ko.observable();

  // UI
  self.wizard = new Wizard(steps);

  self.inferFields = function(data) {
    var fields = [];
    var field_names = data[0];
    var first_row = data[1];
    $.each(first_row, function(index, value) {
      var type = null;
      if ($.isNumeric(value)) {
        if (value.toString().indexOf(".") == -1) {
          type = 'integer';
        } else {
          type = 'float';
        }
      } else {
        if (value.toLowerCase().indexOf("true") > -1 || value.toLowerCase().indexOf("false") > -1) {
          type = 'boolean';
        }
        else {
          type = 'string';
        }
      }
      fields.push(new Field(self.collection, field_names[index], type));
    });

    self.collection.fields(fields);
  };

  self.save = function() {
    if (self.wizard.current().validate()) {
      return $.post("/search/admin/collections/create", {
        collection: ko.toJSON(self.collection),
      })
      .done(function(data) {
        if (data.status == 0) {
          $(document).trigger("info", data.message);
        } else {
          $(document).trigger("error", data.message);
        }
      })
      .fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    }
  };
};


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

ko.extenders.errors = function(target, options) {
  target.errors = ko.observableArray();
  return target;
};

qq.CollectionFileUploader = function(o){
  // call parent constructor
  qq.FileUploader.apply(this, arguments);

  this._handler._upload = function(id, params){
    var file = this._files[id],
        name = this.getName(id),
        size = this.getSize(id);

    this._loaded[id] = 0;

    var xhr = this._xhrs[id] = new XMLHttpRequest();
    var self = this;

    xhr.upload.onprogress = function(e){
      if (e.lengthComputable){
        self._loaded[id] = e.loaded;
        self._options.onProgress(id, name, e.loaded, e.total);
      }
    };

    xhr.onreadystatechange = function(){
      if (xhr.readyState == 4){
        self._onComplete(id, xhr);
      }
    };

    var formData = new FormData();
    formData.append(params.fileFieldLabel, file);
    formData.append('field-separator', params.fieldSeparator);

    var action = this._options.action;
    xhr.open("POST", action, true);
    xhr.send(formData);
  };
};

qq.extend(qq.CollectionFileUploader.prototype, qq.FileUploader.prototype);

qq.extend(qq.CollectionFileUploader.prototype, {
  _finish: [],
  _onInputChange: function(input){
    if (this._handler instanceof qq.UploadHandlerXhr) {
      this._finish.push(this._uploadFileList.bind(this, input.files));
    } else {
      if (this._validateFile(input)) {
        this._finish.push(this._uploadFile.bind(this, input));
      }
    }
    this._button.reset();
  },
  finishUpload: function() {
    $.each(this._finish, function(index, upload) {
      upload();
    });
  }
});

// End utils
