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


function BeeswaxViewModel(server) {
  var self = this;

  var DESIGN_DEFAULTS = {
    'id': -1,
    'query': {
      'value': '',
      'errors': []
    },
    'name': null,
    'description': null,
    'settings': {
      'values': [],
      'errors': []
    },
    'fileResources': {
      'values': [],
      'errors': []
    },
    'functions': {
      'values': [],
      'errors': []
    },
    'parameters': [],
    'isParameterized': true,
    'email': false,
    'errors': [],
    'explain': false,
    'history': {
      'id': -1
    },
    'results': {
      'rows': [],
      'columns': [],
      'empty': true,
      'explanation': null,
      'url': null,
      'errors': [],
      'save': {
        'errors': null,
        'type': 'hive-table',
        'path': null
      }
    },
    'watch': {
      'logs': [],
      'url': null,
      'errors': []
    },
    'isRunning': false,
    'statement': '',
    'isFinished': true
  };

  self.server = ko.observable(server);
  self.databases = ko.observableArray();
  self.selectedDatabase = ko.observable(0);
  self.isReady = ko.observable(false);
  self.design = ko.mapping.fromJS(DESIGN_DEFAULTS);

  self.hasMoreResults = ko.computed(function() {
    return self.design.results.url() != null;
  });

  self.design.results.save.saveTargetError = ko.computed(function() {
    return (self.design.results.save.errors() && 'save_target' in self.design.results.save.errors()) ? self.design.results.save.errors()['save_target'] : null;
  });

  self.design.results.save.targetTableError = ko.computed(function() {
    return (self.design.results.save.errors() && 'target_table' in self.design.results.save.errors()) ? self.design.results.save.errors()['target_table'] : null;
  });

  self.design.results.save.targetDirectoryError = ko.computed(function() {
    return (self.design.results.save.errors() && 'target_dir' in self.design.results.save.errors()) ? self.design.results.save.errors()['target_dir'] : null;
  });

  self.database = ko.computed({
    'read': function() {
      if (self.databases()) {
        return self.databases()[self.selectedDatabase()];
      } else{
        return "";
      }
    },
    'write': function(value) {
      if (value) {
        self.selectedDatabase(self.databases.indexOf(value));
      }
    },
    'deferEvaluation': true
  });

  self.hasParametersFilled = ko.computed(function() {
    var hasBlank = false;
    $.each(self.design.parameters(), function(index, element) {
      if (element.value() == '') {
        hasBlank = true;
      }
    });
    return ! hasBlank;
  });

  self.resetQuery = function() {
    ko.mapping.fromJS(QUERY_DEFAULTS, self.design);
  };

  self.resetErrors = function() {
    self.design.errors.removeAll();
    self.design.query.errors.removeAll();
    self.design.settings.errors.removeAll();
    self.design.fileResources.errors.removeAll();
    self.design.functions.errors.removeAll();
  };

  self.setErrors = function(message, errors) {
    self.resetErrors();
    self.design.errors.push(message);
    if (errors) {
      self.design.query.errors.push.apply(self.design.query.errors, errors.query);
      self.design.settings.errors.push.apply(self.design.settings.errors, errors.settings);
      self.design.fileResources.errors.push.apply(self.design.fileResources.errors, errors.file_resources);
      self.design.functions.errors.push.apply(self.design.functions.errors, errors.functions);
    }
  };

  self.updateDatabases = function(databases) {
    self.databases(databases);
  };

  self.updateDesign = function(design) {
    self.design.query.value(design.query);
    self.design.id(design.id);
    self.design.name(design.name);
    self.design.description(design.desc);
    self.database(design.database);
    self.design.isParameterized(design.is_parameterized);
    self.design.email(design.email_notify);

    self.design.settings.values.removeAll();
    self.design.fileResources.values.removeAll();
    self.design.functions.values.removeAll();

    $.each(design.settings, function(index, setting) {
      self.addSetting(setting.key, setting.value);
    });
    $.each(design.file_resources, function(index, file_resource) {
      self.addFileResources(file_resource.type, file_resource.path);
    });
    $.each(design.functions, function(index, _function) {
      self.addFunction(_function.name, _function.class_name);
    });
  };

  self.updateHistory = function(history) {
    self.design.history.id(history.id);
    viewModel.design.results.url('/' + viewModel.server() + '/results/' + history.id + '/0?format=json');
    viewModel.design.watch.url('/' + viewModel.server() + '/api/watch/json/' + history.id);
    if (history.design) {
      self.updateDesign(history.design);
    }
  };

  self.updateParameters = function(parameters) {
    self.design.parameters.removeAll();
    $.each(parameters, function(index, parameter) {
      self.addParameter(parameter.parameter, parameter.name, '');
    });
  };

  self.addParameter = function(parameter, name, value) {
    var obj = {
      'parameter': ko.observable(parameter),
      'name': ko.observable(name),
      'value': ko.observable(value)
    };
    obj.parameter.subscribe(function() {
      self.design.parameters.valueHasMutated();
    });
    obj.name.subscribe(function() {
      self.design.parameters.valueHasMutated();
    });
    obj.value.subscribe(function() {
      self.design.parameters.valueHasMutated();
    });
    self.design.parameters.push(obj);
  };

  self.addSetting = function(key, value) {
    var obj = {
      'key': ko.observable(key),
      'value': ko.observable(value)
    };
    obj.key.subscribe(function() {
      self.design.settings.values.valueHasMutated();
    });
    obj.value.subscribe(function() {
      self.design.settings.values.valueHasMutated();
    });
    self.design.settings.values.push(obj);
  };

  self.removeSetting = function(index) {
    self.design.settings.values.splice(index, 1);
  };

  self.addFileResource = function(type, path) {
    var obj = {
      'type': ko.observable(type),
      'path': ko.observable(path)
    };
    obj.type.subscribe(function() {
      self.design.fileResources.values.valueHasMutated();
    });
    obj.path.subscribe(function() {
      self.design.fileResources.values.valueHasMutated();
    });
    self.design.fileResources.values.push(obj);
  };

  self.removeFileResource = function(index) {
    self.design.fileResources.values.splice(index, 1);
  };

  self.getFileResourceTypeErrors = function(index) {
    if (self.design.settings.errors() && self.design.settings.errors()[index]) {
      return self.design.settings.errors()[index];
    } else {
      return {};
    }
  };

  self.getFileResourcePathErrors = function(index) {
    
  };

  self.addFunction = function(name, class_name) {
    var obj = {
      'name': ko.observable(name),
      'class_name': ko.observable(class_name)
    };
    obj.name.subscribe(function() {
      self.design.functions.values.valueHasMutated();
    });
    obj.class_name.subscribe(function() {
      self.design.functions.values.valueHasMutated();
    });
    self.design.functions.values.push(obj);
  };

  self.removeFunction = function(index) {
    self.design.functions.values.splice(index, 1);
  };

  self.getFunctionErrors = function(index) {
    if (self.design.settings.errors() && self.design.settings.errors()[index]) {
      return self.design.settings.errors()[index];
    } else {
      return {};
    }
  };

  var advancedParameterErrorHandling = function(advanced_parameter, key) {
    return function(index) {
      var errors = self.design[advanced_parameter].errors();
      if (errors && errors[index]) {
        if (key in errors[index]) {
          return errors[index][key];
        } else {
          return [];
        }
      } else {
        return [];
      }
    };
  };

  self.getSettingKeyErrors = advancedParameterErrorHandling('settings', 'key');
  self.getSettingValueErrors = advancedParameterErrorHandling('settings', 'value');

  self.getFileResourceTypeErrors = advancedParameterErrorHandling('fileResources', 'type');
  self.getFileResourcePathErrors = advancedParameterErrorHandling('fileResources', 'path');

  self.getFunctionNameErrors = advancedParameterErrorHandling('functions', 'name');
  self.getFunctionClassNameErrors = advancedParameterErrorHandling('functions', 'class_name');

  function getMultiFormData(prefix, arr, members) {
    var data = {};
    var index = 0;
    data[prefix + '-next_form_id'] = arr.length;
    ko.utils.arrayForEach(arr, function(obj) {
      $.each(members, function(i, member) {
        data[prefix + '-' + index + '-' + member] = obj[member]();
      });
      data[prefix + '-' + index + '-_exists'] = true;
      data[prefix + '-' + index++ + '-_deleted'] = false;
    });
    return data;
  }

  self.getSettingsFormData = function() {
    return getMultiFormData('settings', self.design.settings.values(), ['key', 'value']);
  };

  self.getFileResourcesFormData = function() {
    return getMultiFormData('file_resources', self.design.fileResources.values(), ['type', 'path']);
  };

  self.getFunctionsFormData = function() {
    return getMultiFormData('functions', self.design.functions.values(), ['name', 'class_name']);
  };

  self.getParametersFormData = function() {
    var data = {};
    $.each(self.design.parameters(), function(index, parameter) {
      data[parameter.parameter()] = parameter.value();
    });
    return data;
  };

  self.getOtherData = function() {
    var data = {
      'query-email_notify': self.design.email(),
      'query-is_parameterized': self.design.isParameterized()
    };
    return data;
  };

  var error_fn = function(jqXHR, status, errorThrown) {
    self.design.isRunning(false);
    try {
      $(document).trigger('server.error', $.parseJSON(jqXHR.responseText));
    } catch(e) {
      $(document).trigger('server.unmanageable_error', jqXHR.responseText);
    }
  };

  self.fetchDatabases = function() {
    var request = {
      url: '/' + self.server() + '/api/autocomplete',
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        self.updateDatabases(data.databases);
      },
      error: error_fn
    };
    $.ajax(request);
  };

  self.fetchDesign = function() {
    $(document).trigger('fetch.design');

    var request = {
      url: '/' + self.server() + '/api/design/' + self.design.id() + '/get',
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        self.updateDesign(data.design);
        $(document).trigger('fetched.design', data);
      },
      error: error_fn
    };
    $.ajax(request);
  };

  self.fetchQueryHistory = function() {
    $(document).trigger('fetch.query');

    var request = {
      url: '/' + self.server() + '/api/query/' + self.design.history.id() + '/get',
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        self.updateHistory(data.query_history);
        $(document).trigger('fetched.query', data);
      },
      error: error_fn
    };
    $.ajax(request);
  };


  self.fetchParameters = function() {
    $(document).trigger('fetch.parameters');

    var data = {
      'query-query': self.design.query.value(),
      'query-database': self.database()
    };
    $.extend(data, self.getSettingsFormData());
    $.extend(data, self.getFileResourcesFormData());
    $.extend(data, self.getFunctionsFormData());
    $.extend(data, self.getParametersFormData());
    $.extend(data, self.getOtherData());
    var request = {
      url: '/' + self.server() + '/api/query/parameters',
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        self.updateParameters(data.parameters);
        $(document).trigger('fetched.parameters');
      },
      error: error_fn,
      data: data
    };
    $.ajax(request);
  };

  self.explainQuery = function() {
    $(document).trigger('explain.query', data);
    self.design.explain(true);
    self.design.isRunning(true);
    self.design.isFinished(true);
    self.resetErrors();

    var data = {
      'query-query': self.design.query.value(),
      'query-database': self.database()
    };
    $.extend(data, self.getSettingsFormData());
    $.extend(data, self.getFileResourcesFormData());
    $.extend(data, self.getFunctionsFormData());
    $.extend(data, self.getParametersFormData());
    $.extend(data, self.getOtherData());
    var request = {
      url: '/' + self.server() + '/api/query/execute/?explain=true',
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        if (data.status == 0) {
          self.design.watch.logs.removeAll();
          self.design.results.rows.removeAll();
          self.design.results.columns.removeAll();
          self.design.results.explanation(data.explanation);
        } else {
          self.setErrors(data.message);
          $(document).trigger('error.query');
        }
        $(document).trigger('explained.query', data);
        self.design.isRunning(false);
      },
      error: error_fn,
      data: data
    };
    $.ajax(request);
  };

  self.executeQuery = function() {
    $(document).trigger('execute.query', data);
    self.design.explain(false);
    self.design.isRunning(true);
    self.design.isFinished(true);
    self.resetErrors();

    var data = {
      'query-query': self.design.query.value(),
      'query-database': self.database()
    };
    $.extend(data, self.getSettingsFormData());
    $.extend(data, self.getFileResourcesFormData());
    $.extend(data, self.getFunctionsFormData());
    $.extend(data, self.getParametersFormData());
    $.extend(data, self.getOtherData());
    var url = '/' + self.server() + '/api/query/execute/';
    if (self.design.id() > -1) {
      url += self.design.id();
    }
    var request = {
      url: url,
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        self.design.errors.removeAll();
        if (data.status == 0) {
          self.design.results.url('/' + self.server() + '/results/' + data.id + '/0?format=json');
          self.design.watch.url(data.watch_url);
          self.design.statement(data.statement);
          self.design.history.id(data.id);
          self.watchQueryLoop();
        } else {
          self.setErrors(data.message, data.errors);
          self.design.isRunning(false);
          $(document).trigger('error.query');
        }
        $(document).trigger('executed.query', data);
      },
      error: error_fn,
      data: data
    };
    $.ajax(request);
  };

  self.executeNextStatement = function() {
    $(document).trigger('execute.query', data);
    self.design.explain(false);
    self.design.isRunning(true);
    self.design.isFinished(true);
    self.design.errors.removeAll();

    var data = {
      'next': true
    };
    var request = {
      url: self.design.watch.url(),
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        self.design.errors.removeAll();
        self.design.watch.logs.removeAll();
        self.design.statement(data.statement);
        self.design.watch.url(data.watch_url);
        self.design.results.url('/' + self.server() + '/results/' + data.id + '/0?format=json');
        self.watchQueryLoop();
        $(document).trigger('executed.query', data);
      },
      error: error_fn,
      data: data
    };
    $.ajax(request);
  };

  self.watchQuery = function() {
    var data = {
      'query-query': self.design.query.value(),
      'query-database': self.database()
    };
    $.extend(data, self.getSettingsFormData());
    $.extend(data, self.getFileResourcesFormData());
    $.extend(data, self.getFunctionsFormData());
    $.extend(data, self.getParametersFormData());
    $.extend(data, self.getOtherData());
    var request = {
      url: self.design.watch.url(),
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        $(document).trigger('watched.query', data);
      },
      error: function(jqXHR, status, errorThrown) {
        self.design.isRunning(false);
        try {
          var data = $.parseJSON(jqXHR.responseText);
          self.design.errors.push(data.error);
        } catch(e) {
          $(document).trigger('server.unmanageable_error', jqXHR.responseText);
        }
      },
      data: data
    };
    $.ajax(request);
  };

  self.watchQueryLoop = function(fn) {
    var TIMEOUT = 1000;
    var timer = null;

    self.design.watch.logs.removeAll();
    self.design.watch.errors.removeAll();
    self.design.results.rows.removeAll();
    self.design.results.columns.removeAll();

    var _fn = function() {
      $(document).one('watched.query', function(e, data) {
        if (data.isSuccess || data.isFailure) {
          clearTimeout(timer);
          self.design.isRunning(false);

          if (data.log) {
            self.design.watch.logs.push(data.log);
            // scroll logs
          }
          if (!data.isFailure) {
            $(document).trigger('stop_watch.query');

            if (fn) {
              fn(data);
            } else {
              self.fetchResults();
            }
          }
        } else {
          self.design.statement(data.statement); // In case new no result statement executed
          if (data.log) {
            self.design.watch.logs.push(data.log);
            // scroll logs
          }

          timer = setTimeout(_fn, TIMEOUT);
        }
      });
      self.watchQuery();
    };
    $(document).trigger('start_watch.query');
    timer = setTimeout(_fn, TIMEOUT);
  };

  self.fetchResults = function() {
    $(document).trigger('fetch.results');
    self.design.results.errors.removeAll();
    var request = {
      url: self.design.results.url(),
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        if (data.error) {
          self.design.results.errors.push(data.message);
          self.design.isRunning(false);
          self.design.results.empty(true);
        } else {
          self.design.isRunning(false);
          self.design.isFinished(data.is_finished);
          if (self.design.results.columns().length == 0){
            self.design.results.columns(data.columns);
          }
          self.design.results.rows.push.apply(self.design.results.rows, data.results);
          self.design.results.empty(self.design.results.rows().length == 0);
          if (data.has_more) {
            self.design.results.url(data.next_json_set);
          } else {
            self.design.results.url(null);
          }
        }
        $(document).trigger('fetched.results', [data]);
      },
      error: error_fn
    };
    $.ajax(request);
  };

  self.saveDesign = function() {
    var self = this;
    if (self.design.query.value() && self.design.name()) {
      var data = {
        'query-query': self.design.query.value(),
        'query-database': self.database()
      };
      $.extend(data, self.getSettingsFormData());
      $.extend(data, self.getFileResourcesFormData());
      $.extend(data, self.getFunctionsFormData());
      $.extend(data, self.getParametersFormData());
      $.extend(data, self.getOtherData());
      data['saveform-name'] = self.design.name();
      data['saveform-desc'] = self.design.description();
      if (self.design.id() > 0) {
        data['query-id'] = self.design.id();
      }
      var url = '/' + self.server() + '/api/design/';
      if (self.design.id() && self.design.id() != -1) {
        url += self.design.id();
      }
      var request = {
        url: url,
        dataType: 'json',
        type: 'POST',
        success: function(data) {
          self.design.id(data.design_id);
          $(document).trigger('saved.design', [data.design_id]);
        },
        error: function() {
          $(document).trigger('error_save.design');
        },
        data: data
      };
      $.ajax(request);
    }
  };

  self.cancelQuery = function() {
    $(document).trigger('cancel.query');
    var url = '/' + self.server() + '/api/query/' + self.design.id() + '/cancel';
    $.post(url,
      function(response) {
        if (response['status'] != 0) {
          $(document).trigger('error_cancel.query', response['message']);
        } else {
          $(document).trigger('cancelled.query');
        }
      }
    );
  };

  self.closeQuery = function() {
    var self = this;
    if (self.design.id()) {
      var data = {};
      var url = '/' + self.server() + '/api/query/' + self.design.id() + '/close';
      var request = {
        url: url,
        dataType: 'json',
        type: 'POST',
        success: function(data) {
          if (data.status == 0) {
            $(document).trigger('closed.query', data);
            //self.resetQuery(); // Would fail multiqueries
          } else {
            $(document).trigger('error_close.query');
          }
        },
        error: function(data) {
          $(document).trigger('error_close.results');
        },
        data: data,
        async: false // for multi query
      };
      $.ajax(request);
    }
  };

  self.saveResults = function() {
    var self = this;
    if (self.design.id()) {
      var data = {
        'database': self.database(),
        'server': self.server(),
        'type': self.design.results.save.type(),
        'path': self.design.results.save.path()
      };
      var url = '/' + self.server() + '/api/query/' + self.design.history.id() + '/results/save';
      var request = {
        url: url,
        dataType: 'json',
        type: 'POST',
        success: function(data) {
          if (data.status == 0) {
            self.design.results.save.errors(null);
            if (data.id) {
              // watch this ID.
              self.design.watch.url(data.watch_url);
              self.design.watch.logs.removeAll();
              self.watchQueryLoop(function() {
                window.location.href = data.success_url;
              });
            } else {
              // redirect to metastore app.
              window.location.href = data.success_url;
            }
            $(document).trigger('saved.results', data);
          } else {
            self.design.results.save.errors(data.errors);
            $(document).trigger('error_save.results');
          }
        },
        error: function(data) {
          self.design.results.save.errors(data);
          $(document).trigger('error_save.results');
        },
        data: data
      };
      $.ajax(request);
    }
  };

  // Events
  // Remove watched query event that watchQueryLoop may be bound to.
  $(document).on('server.unmanageable_error', function() {
    $(document).off('watched.query');
  });
}


// For routie
function showSection(section) {
  $('.section').hide();
  $('#' + section).show();
}


// File browser button
function getFileBrowseButton(inputElement) {
  return $("<button>").addClass("btn").addClass("fileChooserBtn").text("..").click(function (e) {
    e.preventDefault();
    $("#filechooser").jHueFileChooser({
      initialPath: inputElement.val(),
      onFileChoose: function (filePath) {
        inputElement.val(filePath);
        inputElement.trigger("change");
        $("#chooseFile").modal("hide");
      },
      createFolder: false
    });
    $("#chooseFile").modal("show");
  });
}


// utils
function clickHard(el) {
  var timer = setInterval(function () {
    if ($(el).length > 0) {
      $(el).click();
      clearInterval(timer);
    }
  }, 100);
}
