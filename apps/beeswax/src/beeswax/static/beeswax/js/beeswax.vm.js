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

function BeeswaxViewModel(server, apiHelper) {
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
      'expired': false,
      'explanation': null,
      'url': null,
      'errors': [],
      'save': {
        'errors': null,
        'type': 'hdfs-file',
        'path': null,
        'overwrite': true
      }
    },
    'watch': {
      'logs': [],
      'jobUrls': [],
      'url': null,
      'errors': []
    },
    'isRunning': false,
    'statement': '',
    'isFinished': true,
    'isRedacted': false
  };

  self.database = ko.observable(null);

  var type = server === "beeswax" ? "hive" : "impala";
  huePubSub.subscribe("assist.db.panel.ready", function () {
    // Defer to let the db be set
    window.setTimeout(function () {
      huePubSub.publish('assist.set.database', {
        source: type,
        name: self.database()
      });
    }, 0);
  });

  huePubSub.subscribe("assist.database.selected", function (database) {
    if (database.sourceType === type && self.database() !== database.name) {
      self.database(database.name);
    }
  });

  huePubSub.subscribe("assist.database.set", function (database) {
    if (database.sourceType === type && self.database() !== database.name) {
      self.database(database.name);
    }
  });

  self.design = ko.mapping.fromJS(DESIGN_DEFAULTS);

  self.design.inlineErrors = ko.computed(function() {
    return ko.utils.arrayFilter(self.design.errors(), function(err) {
        return err && err.toLowerCase().indexOf("line") > -1;
    });
  });

  self.design.watch.inlineErrors = ko.computed(function() {
    return ko.utils.arrayFilter(self.design.watch.errors(), function(err) {
        return err && err.toLowerCase().indexOf("line") > -1;
    });
  });

  self.impalaSessionLink = ko.observable("");

  self.isEditor = ko.observable(true);

  self.chartType = ko.observable("bars");
  self.chartSorting = ko.observable("none");
  self.chartData = ko.observableArray();

  self.server = ko.observable(server);
  self.isReady = ko.observable(false);
  // Use a view model attribute so that we don't have to override KO.
  // This allows Hue to disable the execute button until the query placeholder dies.
  self.queryEditorBlank = ko.observable(false);
  self.scrollNotWorking = ko.observable(true);

  self.canExecute = ko.computed(function() {
    return !self.design.isRunning() && self.design.isFinished();
  });

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

  self.design.results.save.targetFileError = ko.computed(function() {
    return (self.design.results.save.errors() && 'target_file' in self.design.results.save.errors()) ? self.design.results.save.errors()['target_file'] : null;
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

  self.hasResults = ko.computed(function() {
    return !self.design.results.empty() && !self.design.results.expired();
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
    if (message) {
      self.design.errors.push(message);
    }
    if (errors) {
      self.design.query.errors.push.apply(self.design.query.errors, errors.query);
      self.design.settings.errors.push.apply(self.design.settings.errors, errors.settings);
      self.design.fileResources.errors.push.apply(self.design.fileResources.errors, errors.file_resources);
      self.design.functions.errors.push.apply(self.design.functions.errors, errors.functions);
    }
  };

  self.updateDesign = function(design) {
    self.design.query.value(design.query);
    self.design.id(design.id);
    self.design.name(design.name);
    self.design.description(design.desc);
    self.database(design.database);
    if (typeof design.database !== 'undefined' && design.database !== null) {
      huePubSub.publish('assist.set.database', {
        source: type,
        name: design.database
      });
    }

    self.design.isParameterized(design.is_parameterized);
    self.design.email(design.email_notify);
    self.design.isRedacted(design.is_redacted);

    self.design.settings.values.removeAll();
    self.design.fileResources.values.removeAll();
    self.design.functions.values.removeAll();

    $.each(design.settings, function(index, setting) {
      self.addSetting(setting.key, setting.value);
    });
    $.each(design.file_resources, function(index, file_resource) {
      self.addFileResource(file_resource.type, file_resource.path);
    });
    $.each(design.functions, function(index, _function) {
      self.addFunction(_function.name, _function.class_name);
    });
  };

  self.updateHistory = function(history) {
    self.design.history.id(history.id);
    self.design.results.url('/' + self.server() + '/results/' + history.id + '/0?format=json');
    self.design.watch.url('/' + self.server() + '/api/watch/json/' + history.id);
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

  var advancedErrorHandling = function(advanced_parameter, key) {
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

  self.getQueryErrors = advancedErrorHandling('query', 'query');

  self.getSettingKeyErrors = advancedErrorHandling('settings', 'key');
  self.getSettingValueErrors = advancedErrorHandling('settings', 'value');

  self.getFileResourceTypeErrors = advancedErrorHandling('fileResources', 'type');
  self.getFileResourcePathErrors = advancedErrorHandling('fileResources', 'path');

  self.getFunctionNameErrors = advancedErrorHandling('functions', 'name');
  self.getFunctionClassNameErrors = advancedErrorHandling('functions', 'class_name');

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
      $(document).trigger('server.error', JSON.parse(jqXHR.responseText));
    } catch(e) {
      $(document).trigger('server.unmanageable_error', jqXHR.responseText);
    }
  };

  self.fetchingImpalaSession = ko.observable(false);
  self.fetchImpalaSession = function () {
    self.fetchingImpalaSession(true);
    var request = {
      url: '/impala/api/session/',
      dataType: 'json',
      type: 'GET',
      success: function (data) {
        if (data && data.properties && data.properties.http_addr) {
          if (!data.properties.http_addr.match(/^(https?):\/\//)) {
            data.properties.http_addr = window.location.protocol + "//" + data.properties.http_addr;
          }
          self.impalaSessionLink(data.properties.http_addr);
        }
        else {
          self.impalaSessionLink("");
        }
        self.fetchingImpalaSession(false);
      },
      error: error_fn,
      cache: false
    };
    $.ajax(request);
  }

  self.fetchDesign = function() {
    $(document).trigger('fetch.design');

    var request = {
      url: '/' + self.server() + '/api/design/' + self.design.id() + '/get',
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        self.updateDesign(data.design);
        self.database(data.design.database);
        $(document).trigger('fetched.design', [data]);
      },
      error: error_fn,
      cache: false
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
        if (data.query_history.database) {
          self.database(data.query_history.database);
        }
        $(document).trigger('fetched.query', [data]);
      },
      error: error_fn,
      cache: false
    };
    $.ajax(request);
  };

  self.clearQueryHistory = function() {
    var request = {
      url: '/' + self.server() + '/api/query/clear_history/',
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        $(document).trigger('clear.history', [data]);
      },
      error: error_fn,
      cache: false
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
      data: data,
      cache: false
    };
    $.ajax(request);
  };

  self.explainQuery = function() {
    $(document).trigger('explain.query', data);
    self.design.explain(true);
    self.design.isRunning(true);
    self.design.isFinished(true);
    self.design.results.expired(false);
    self.design.results.empty(false);
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
          self.design.watch.jobUrls.removeAll();
          self.design.statement(data.statement);
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
      data: data,
      cache: false
    };
    $.ajax(request);
  };

  self.executeQuery = function() {
    $(document).trigger('execute.query', data);
    self.design.explain(false);
    self.design.isRunning(true);
    self.design.isFinished(true);
    self.design.results.expired(false);
    self.design.results.empty(false);
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
        self.design.watch.errors.removeAll();
        if (data.status == 0) {
          hueUtils.changeURL('/' + self.server() + '/execute/query/' + data.id + '#query/logs');
          self.design.results.url('/' + self.server() + '/results/' + data.id + '/0?format=json');
          self.design.watch.url(data.watch_url);
          self.design.statement(data.statement);
          self.design.history.id(data.id);
          self.design.isRedacted(data.is_redacted);
          self.watchQueryLoop();
          $(document).trigger('executed.query', data);
        } else {
          self.setErrors(data.message, data.errors);
          self.design.isRunning(false);
          $(document).trigger('error.query');
        }
      },
      error: error_fn,
      data: data,
      cache: false
    };
    $.ajax(request);
  };

  self.executeNextStatement = function() {
    $(document).trigger('execute.query', data);
    self.design.explain(false);
    self.design.isRunning(true);
    self.design.isFinished(true);
    self.resetErrors();

    var data = {
      'next': true,
      'query-query': self.design.query.value(),
    };
    var request = {
      url: self.design.watch.url(),
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        if (data.status == 0) {
          self.design.watch.logs.removeAll();
          self.design.watch.jobUrls.removeAll();
          self.design.statement(data.statement);
          self.design.watch.url(data.watch_url);
          self.design.results.url('/' + self.server() + '/results/' + data.id + '/0?format=json');
          self.watchQueryLoop();
          $(document).trigger('executed.query', data);
        } else {
          self.setErrors(data.message, data.errors);
          self.design.isRunning(false);
          self.design.isFinished(false); // We propose to skip the failed statement
          $(document).trigger('error.query');
        }
      },
      error: error_fn,
      data: data,
      cache: false
    };
    $.ajax(request);
  };

  self.watchQuery = function() {
    var data = {
      'query-query': self.design.query.value(),
      'query-database': self.database(),
      'log-start-over': self.design.watch.logs().length == 0
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
        if (data.status != 0) {
          self.setErrors(data.message, data.errors);
          self.design.isRunning(false);
          $(document).trigger('error.query');
          $(document).trigger("error", data.message);
          if (typeof window.console !== 'undefined') {
            console.error(data.message);
          }
          if (data.log) {
            self.applyLogs(data.log);
          }
        } else {
          $(document).trigger('watched.query', data);
        }
      },
      error: function(jqXHR, status, errorThrown) {
        self.design.isRunning(false);
        try {
          var data = JSON.parse(jqXHR.responseText);
          self.design.watch.errors.push(data.error);
        } catch(e) {
          $(document).trigger('server.unmanageable_error', jqXHR.responseText);
        }
      },
      data: data,
      cache: false
    };
    $.ajax(request);
  };

  self.shouldAppendLogs = false;

  self.applyLogs = function(log) {
    var lines = log.split("\n")

    if (self.shouldAppendLogs) {
      lines = self.design.watch.logs().concat(lines);
    }
    self.design.watch.logs(lines);
  };

  self.watchQueryLoop = function(fn) {
    var TIMEOUT = 100;
    var timer = null;

    self.design.isRunning(true);
    self.design.watch.logs.removeAll();
    self.design.watch.jobUrls.removeAll();
    self.design.results.rows.removeAll();
    self.design.results.columns.removeAll();
    self.resetErrors();

    var _fn = function() {
      $(document).one('watched.query', function(e, data) {
        var failed = data.isFailure  || data.status != 0;
        if (data.isSuccess || failed) {
          clearTimeout(timer);
          self.design.isRunning(false);
          if (data.log) {
            self.applyLogs(data.log)
            // scroll logs
            if (data.oldLogsApi) {
              self.design.watch.jobUrls(data.jobUrls);
            } else {
              $.each(data.jobUrls, function (i, url) {
                self.design.watch.jobUrls.push(url);
              });
            }
          }
          if (! failed) {
            $(document).trigger('stop_watch.query');
            if (fn) {
              fn(data);
            } else {
              self.fetchResults();
            }
          }
          else {
            self.design.watch.errors.push(data.message);
            $(document).trigger('stop_watch.query');
          }
        } else {
          self.design.statement(data.statement); // In case new no result statement executed
          if (data.log) {
            self.applyLogs(data.log)
            // scroll logs
            if (data.oldLogsApi) {
              self.design.watch.jobUrls(data.jobUrls);
            } else {
              $.each(data.jobUrls, function (i, url) {
                self.design.watch.jobUrls.push(url);
              });
            }
          }

          TIMEOUT = Math.min(TIMEOUT + 100, 2000);
          timer = setTimeout(_fn, TIMEOUT);
        }
      });
      self.watchQuery();
    };
    $(document).trigger('start_watch.query');
    timer = setTimeout(_fn, TIMEOUT);
  };

  self.isFetchingResults = ko.observable(false);
  self.fetchResults = function () {
    if (!self.isFetchingResults()) {
      self.isFetchingResults(true);
      $(document).trigger('fetch.results');
      self.design.errors.removeAll();
      self.design.results.errors.removeAll();
      var request = {
        url: self.design.results.url(),
        dataType: 'text',
        type: 'GET',
        success: function (data) {
          data = JSON.bigdataParse(data);
          if (data.traceback) {
            self.design.isRunning(false);
            $(document).trigger('server.unmanageable_error', data.traceback.length > 0 ? data.traceback[data.traceback.length - 1].join("\n") : "");
          }
          else if (data.error) {
            self.design.results.errors.push(data.message);
            self.design.isRunning(false);
            self.design.results.empty(true);
          }
          else {
            self.design.isRunning(false);
            self.design.isFinished(data.is_finished);
            if (self.design.results.columns().length == 0) {
              if (data.columns != null) {
                data.columns.unshift({ type: "INT_TYPE", name: "", comment: null});
              }
              self.design.results.columns(data.columns ? data.columns : []); // Some querysets have empty or null for columns
            }
            self.design.results.rows.push.apply(self.design.results.rows, data.results);
            self.design.results.empty(self.design.results.rows().length == 0);
            if (data.has_more) {
              self.design.results.url(data.next_json_set);
            } else {
              self.design.results.url(null);
            }
          }
          self.isFetchingResults(false);
          if (!data.traceback) {
            $(document).trigger('fetched.results', [data]);
          }
        },
        error: function (jqXHR, status, errorThrown) {
          self.isFetchingResults(false);
          error_fn(jqXHR, status, errorThrown);
        },
        cache: false
      };
      $.ajax(request);
    }
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
          if (data.status == 0) {
            self.design.id(data.design_id);
            $(document).trigger('saved.design', [data.design_id]);
          } else {
            self.setErrors("", data.errors);
            $(document).trigger('error_save.design', [data.message ? data.message : data.errors]);
          }
        },
        error: function() {
          $(document).trigger('error_save.design');
        },
        data: data,
        cache: false
      };
      $.ajax(request);
    }
  };

  self.cancelQuery = function() {
    if (self.design.history.id() > 0) {
      $(document).trigger('cancel.query');
      var url = '/' + self.server() + '/api/query/' + self.design.history.id() + '/cancel';
      $.post(url,
        function(response) {
          if (response['status'] != 0) {
            $(document).trigger('error_cancel.query', response['message']);
          } else {
            $(document).trigger('cancelled.query');
          }
        }
      );
    }
  };

  self.closeQuery = function() {
    var self = this;
    if (self.design.history.id() > 0 && !self.design.isRunning()) {
      var data = {};
      var url = '/' + self.server() + '/api/query/' + self.design.history.id() + '/close';
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
        async: false, // for multi query
        cache: false
      };
      $.ajax(request);
    }
  };

  self.saveResults = function() {
    var self = this;

    self.design.isRunning(true);
    self.resetErrors();
    if (self.design.id()) {
      var data, url;

      switch(self.design.results.save.type()) {
        case 'hdfs-directory':
        data = {
          'server': self.server(),
          'path': self.design.results.save.path()
        };
        url = '/' + self.server() + '/api/query/' + self.design.history.id() + '/results/save/hdfs/directory';
        break;

        case 'hdfs-file':
        data = {
          'server': self.server(),
          'path': self.design.results.save.path(),
          'overwrite': self.design.results.save.overwrite()
        };
        url = '/' + self.server() + '/api/query/' + self.design.history.id() + '/results/save/hdfs/file';
        break;

        // case 'hive-table':
        default:
        data = {
          'database': self.database(),
          'server': self.server(),
          'table': self.design.results.save.path()
        };
        url = '/' + self.server() + '/api/query/' + self.design.history.id() + '/results/save/hive/table';
        break;
      }
      var request = {
        url: url,
        dataType: 'json',
        type: 'POST',
        success: function(data) {
          if (data.status == 0) {
            self.design.results.save.errors(null);

            var redirect_fn = function() {
              huePubSub.publish('open.link', data.success_url + (data.success_url.indexOf("?") > -1 ? "&" : "?") + "refresh=true");
              self.design.isRunning(false);
            };
            if (data.id) {
              // watch this ID.
              self.design.watch.url(data.watch_url);
              self.design.watch.logs.removeAll();
              self.design.watch.jobUrls.removeAll();
              self.watchQueryLoop(redirect_fn);
            } else {
              // redirect to metastore app.
              redirect_fn();
            }
            $(document).trigger('saved.results', data);
          } else {
            self.design.isRunning(false);
            self.design.results.save.errors(data.errors);
            $(document).trigger('error_save.results', [data.message]);
          }
        },
        error: function(data) {
          self.design.isRunning(false);
          self.design.results.save.errors(data);
          $(document).trigger('error_save.results', [data]);
        },
        data: data,
        cache: false
      };
      return $.ajax(request);
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


function folderChooser(inputElement) {
  $("#folderchooser").jHueFileChooser({
    initialPath: inputElement.val(),
    onFolderChoose:function (folderPath) {
      inputElement.val(folderPath);
      inputElement.trigger("change");
      $("#chooseFolder").modal("hide");
    },
    selectFolder: true,
    createFolder: true,
    selectFile: false,
    uploadFile: false
  });
  $("#chooseFolder").modal("show");
}

function getFolderBrowseButton(inputElement) {
  return $("<button>").addClass("btn").addClass("fileChooserBtn").text("..").click(function (e) {
    e.preventDefault();
    folderChooser(inputElement);
  });
}

function pathChooser(inputElement) {
  $("#pathchooser").jHueFileChooser({
    initialPath: inputElement.val(),
    onFolderChoose:function (folderPath) {
      if (folderPath[folderPath.length - 1] != '/') {
        folderPath += '/';
      }
      inputElement.val(folderPath + 'results.csv');
      inputElement.trigger("change");
      $("#choosePath").modal("hide");
    },
    onFileChoose: function (filePath) {
      inputElement.val(filePath);
      inputElement.trigger("change");
      $("#choosePath").modal("hide");
    },
    selectFolder: true,
    createFolder: true,
    selectFile: true,
    uploadFile: false
  });
  $("#choosePath").modal("show");
}

function getPathBrowseButton(inputElement) {
  return $("<button>").addClass("btn").addClass("fileChooserBtn").text("..").click(function (e) {
    e.preventDefault();
    pathChooser(inputElement);
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
