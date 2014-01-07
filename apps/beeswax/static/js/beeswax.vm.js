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


function BeeswaxViewModel(server, query_id) {
  var self = this;

  var QUERY_DEFAULTS = {
    'id': query_id,
    'query': '',
    'name': null,
    'description': null,
    'settings': [],
    'fileResources': [],
    'functions': [],
    'parameters': [],
    'isParameterized': true,
    'email': false,
    'errors': [],
    'explain': false,
    'results': {
      'rows': [],
      'columns': [],
      'empty': true,
      'explanation': null,
      'url': null,
      'save': {
        'errors': null,
        'type': 'table',
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
  self.query = ko.mapping.fromJS(QUERY_DEFAULTS);

  self.hasMoreResults = ko.computed(function() {
    return self.query.results.url() != null;
  });

  self.query.results.save.saveTargetError = ko.computed(function() {
    return (self.query.results.save.errors() && 'save_target' in self.query.results.save.errors()) ? self.query.results.save.errors()['save_target'] : null;
  });

  self.query.results.save.targetTableError = ko.computed(function() {
    return (self.query.results.save.errors() && 'target_table' in self.query.results.save.errors()) ? self.query.results.save.errors()['target_table'] : null;
  });

  self.query.results.save.targetDirectoryError = ko.computed(function() {
    return (self.query.results.save.errors() && 'target_dir' in self.query.results.save.errors()) ? self.query.results.save.errors()['target_dir'] : null;
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
    $.each(self.query.parameters(), function(index, element) {
      if (element.value() == '') {
        hasBlank = true;
      }
    });
    return ! hasBlank;
  });

  self.resetQuery = function() {
    ko.mapping.fromJS(QUERY_DEFAULTS, self.query);
  };

  self.updateDatabases = function(databases) {
    self.databases(databases);
  };

  self.updateQuery = function(design) {
    self.query.query(design.query);
    self.query.id(design.id);
    self.query.name(design.name);
    self.query.description(design.desc);
    self.database(design.database);
    self.query.isParameterized(design.is_parameterized);
    self.query.email(design.email_notify);

    self.query.settings.removeAll();
    self.query.fileResources.removeAll();
    self.query.functions.removeAll();

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

  self.updateParameters = function(parameters) {
    self.query.parameters.removeAll();
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
      self.query.parameters.valueHasMutated();
    });
    obj.name.subscribe(function() {
      self.query.parameters.valueHasMutated();
    });
    obj.value.subscribe(function() {
      self.query.parameters.valueHasMutated();
    });
    self.query.parameters.push(obj);
  };

  self.addSetting = function(key, value) {
    var obj = {
      'key': ko.observable(key),
      'value': ko.observable(value)
    };
    obj.key.subscribe(function() {
      self.query.settings.valueHasMutated();
    });
    obj.value.subscribe(function() {
      self.query.settings.valueHasMutated();
    });
    self.query.settings.push(obj);
  };

  self.removeSetting = function(index) {
    self.query.settings.splice(index, 1);
  };

  self.addFileResources = function(type, path) {
    var obj = {
      'type': ko.observable(type),
      'path': ko.observable(path)
    };
    obj.type.subscribe(function() {
      self.query.fileResources.valueHasMutated();
    });
    obj.path.subscribe(function() {
      self.query.fileResources.valueHasMutated();
    });
    self.query.fileResources.push(obj);
  };

  self.removeFileResources = function(index) {
    self.query.fileResources.splice(index, 1);
  };

  self.addFunction = function(name, class_name) {
    var obj = {
      'name': ko.observable(name),
      'class_name': ko.observable(class_name)
    };
    obj.name.subscribe(function() {
      self.query.functions.valueHasMutated();
    });
    obj.class_name.subscribe(function() {
      self.query.functions.valueHasMutated();
    });
    self.query.functions.push(obj);
  };

  self.removeFunction = function(index) {
    self.query.functions.splice(index, 1);
  };

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
    return getMultiFormData('settings', self.query.settings(), ['key', 'value']);
  };

  self.getFileResourcesFormData = function() {
    return getMultiFormData('file_resources', self.query.fileResources(), ['type', 'path']);
  };

  self.getFunctionsFormData = function() {
    return getMultiFormData('functions', self.query.functions(), ['name', 'class_name']);
  };

  self.getParametersFormData = function() {
    var data = {};
    $.each(self.query.parameters(), function(index, parameter) {
      data[parameter.parameter()] = parameter.value();
    });
    return data;
  };

  self.getOtherData = function() {
    var data = {
      'query-email_notify': self.query.email(),
      'query-is_parameterized': self.query.isParameterized()
    };
    return data;
  };

  var error_fn = function(jqXHR, status, errorThrown) {
    self.query.isRunning(false);
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

  self.fetchQuery = function() {
    $(document).trigger('fetch.query');

    var request = {
      url: '/' + self.server() + '/api/query/' + self.query.id() + '/get',
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        self.updateQuery(data.design);
        $(document).trigger('fetched.query', data);
      },
      error: error_fn
    };
    $.ajax(request);
  };

  self.fetchParameters = function() {
    $(document).trigger('fetch.parameters');

    var data = {
      'query-query': self.query.query(),
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
    self.query.explain(true);
    self.query.isRunning(true);

    var data = {
      'query-query': self.query.query(),
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
        self.query.errors.removeAll();
        if (data.status == 0) {
          self.query.watch.logs.removeAll();
          self.query.results.rows.removeAll();
          self.query.results.columns.removeAll();
          self.query.results.explanation(data.explanation);
        } else {
          self.query.errors.push(data.message);
          $(document).trigger('error.query');
        }
        $(document).trigger('explained.query', data);
        self.query.isRunning(false);
      },
      error: error_fn,
      data: data
    };
    $.ajax(request);
  };

  self.executeQuery = function() {
    $(document).trigger('execute.query', data);
    self.query.explain(false);
    self.query.isRunning(true);
    self.query.isFinished(true);
    self.query.errors.removeAll();

    var data = {
      'query-query': self.query.query(),
      'query-database': self.database()
    };
    $.extend(data, self.getSettingsFormData());
    $.extend(data, self.getFileResourcesFormData());
    $.extend(data, self.getFunctionsFormData());
    $.extend(data, self.getParametersFormData());
    $.extend(data, self.getOtherData());
    var request = {
      url: '/' + self.server() + '/api/query/execute/',
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        self.query.errors.removeAll();
        if (data.status == 0) {
          self.query.id(data.id);
          self.query.results.url('/' + self.server() + '/results/' + self.query.id() + '/0?format=json');
          self.query.watch.url(data.watch_url);
          self.query.statement(data.statement);
          self.watchQueryLoop();
        } else {
          self.query.errors.push(data.message);
          self.query.isRunning(false);
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
    self.query.explain(false);
    self.query.isRunning(true);
    self.query.isFinished(true);
    self.query.errors.removeAll();

    var data = {
      'next': true
    };
    var request = {
      url: self.query.watch.url(),
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        self.query.errors.removeAll();
        self.query.statement(data.statement);
        self.query.watch.url(data.watch_url);
        self.query.results.url('/' + self.server() + '/results/' + self.query.id() + '/0?format=json');
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
      'query-query': self.query.query(),
      'query-database': self.database()
    };
    $.extend(data, self.getSettingsFormData());
    $.extend(data, self.getFileResourcesFormData());
    $.extend(data, self.getFunctionsFormData());
    $.extend(data, self.getParametersFormData());
    $.extend(data, self.getOtherData());
    var request = {
      url: self.query.watch.url(),
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        $(document).trigger('watched.query', data);
      },
      error: function(jqXHR, status, errorThrown) {
        self.query.isRunning(false);
        try {
          var data = $.parseJSON(jqXHR.responseText);
          self.query.errors.push(data.error);
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

    self.query.watch.logs.removeAll();
    self.query.watch.errors.removeAll();
    self.query.results.rows.removeAll();
    self.query.results.columns.removeAll();

    var _fn = function() {
      $(document).one('watched.query', function(e, data) {
        if (data.isSuccess || data.isFailure) {
          clearTimeout(timer);
          self.query.isRunning(false);

          if (data.log) {
            self.query.watch.logs.push(data.log);
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
          self.query.statement(data.statement); // In case new no result statement executed
          if (data.log) {
            self.query.watch.logs.push(data.log);
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
    var request = {
      url: self.query.results.url(),
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        self.query.isRunning(false);
        self.query.isFinished(data.is_finished);
        if (self.query.results.columns().length == 0){
          self.query.results.columns(data.columns);
        }
        self.query.results.rows.push.apply(self.query.results.rows, data.results);
        self.query.results.empty(self.query.results.rows().length == 0);
        if (data.has_more) {
          self.query.results.url(data.next_json_set);
        } else {
          self.query.results.url(null);
        }
        $(document).trigger('fetched.results', [data]);
      },
      error: error_fn
    };
    $.ajax(request);
  };

  self.saveQuery = function() {
    var self = this;
    if (self.query.query() && self.query.name()) {
      var data = {
        'query-query': self.query.query(),
        'query-database': self.database()
      };
      $.extend(data, self.getSettingsFormData());
      $.extend(data, self.getFileResourcesFormData());
      $.extend(data, self.getFunctionsFormData());
      $.extend(data, self.getParametersFormData());
      $.extend(data, self.getOtherData());
      data['saveform-name'] = self.query.name();
      data['saveform-desc'] = self.query.description();
      if (self.query.id() > 0) {
        data['query-id'] = self.query.id();
      }
      var url = '/' + self.server() + '/api/query/';
      if (self.query.id() && self.query.id() != -1) {
        url += self.query.id();
      }
      var request = {
        url: url,
        dataType: 'json',
        type: 'POST',
        success: function(data) {
          self.query.id(data.design_id);
          $(document).trigger('saved.query', [data.design_id]);
        },
        error: function() {
          $(document).trigger('error_save.query');
        },
        data: data
      };
      $.ajax(request);
    }
  };

  self.cancelQuery = function() {
    $(document).trigger('cancel.query');
    var url = '/' + self.server() + '/api/query/' + self.query.id() + '/cancel';
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
    if (self.query.id()) {
      var data = {};
      var url = '/' + self.server() + '/api/query/' + self.query.id() + '/close';
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
    if (self.query.id()) {
      var data = {
        'type': self.query.results.save.type(),
        'path': self.query.results.save.path()
      };
      var url = '/' + self.server() + '/api/query/' + self.query.id() + '/results/save';
      var request = {
        url: url,
        dataType: 'json',
        type: 'POST',
        success: function(data) {
          if (data.status == 0) {
            self.query.results.save.errors(null);
            if (data.id) {
              // watch this ID.
              self.query.watch.url(data.watch_url);
              self.query.watch.logs.removeAll();
              self.watchQueryLoop(function() {
                window.location.href = "/filebrowser/view" + data.path;
              });
            } else {
              // redirect to metastore app.
              window.location.href = "/metastore";
            }
            $(document).trigger('saved.results', data);
          } else {
            self.query.results.save.errors(data.errors);
            $(document).trigger('error_save.results');
          }
        },
        error: function(data) {
          self.query.results.save.errors(data);
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
  $(window).scrollTop(0);
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
