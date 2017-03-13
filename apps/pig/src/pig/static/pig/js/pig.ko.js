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

var Resource = function (resource) {
  var self = this;

  self.type = ko.observable(resource.type);
  self.value = ko.observable(resource.value);
};

var HadoopProperty = function (property) {
  var self = this;

  self.name = ko.observable(property.name);
  self.value = ko.observable(property.value);
};

var PigParameter = HadoopProperty;


var PigScript = function (pigScript) {
  var self = this;

  self.id = ko.observable(pigScript.id);
  self.docId = ko.observable(pigScript.docId);
  self.isDesign = ko.observable(pigScript.isDesign);
  self.name = ko.observable(pigScript.name);
  self.can_write = ko.observable(pigScript.can_write);
  self.script = ko.observable(pigScript.script);
  self.scriptSumup = ko.observable(pigScript.script.replace(/\W+/g, ' ').substring(0, 100));
  self.isRunning = ko.observable(false);
  self.selected = ko.observable(false);
  self.watchUrl = ko.observable("");
  self.actions = ko.observableArray([]);

  self.handleSelect = function (row, e) {
    this.selected(!this.selected());
  };
  self.hovered = ko.observable(false);
  self.toggleHover = function (row, e) {
    this.hovered(!this.hovered());
  };

  self.parameters = ko.observableArray([]);
  ko.utils.arrayForEach(pigScript.parameters, function (parameter) {
    self.parameters.push(new PigParameter({name: parameter.name, value: parameter.value}));
  });
  self.addParameter = function () {
    self.parameters.push(new PigParameter({name: '', value: ''}));
    self.updateParentModel();
  };
  self.removeParameter = function () {
    self.parameters.remove(this);
    self.updateParentModel();
  };
  self.scriptContent = ko.computed(function() {
    return self.script().replace(/\/\* .+? \*\//g, ''); // Trim comments, no multiline
  });
  self.getParameters = function () {
    var params = {};
    var variables = self.scriptContent().match(/([^\\]|^)\$[^\d'"](\w*)/g);
    var declares = self.scriptContent().match(/%declare +([^ ])+/gi);
    var defaults = self.scriptContent().match(/%default +([^;])+/gi);
    var macro_defines = self.scriptContent().match(/define [^ ]+ *\(([^\)]*)\)/gi); // no multiline
    var macro_returns = self.scriptContent().match(/returns +([^\{]*)/gi); // no multiline

    if (variables) {
      $.each(variables, function(index, param) {
        var p = param.substring(param.indexOf('$') + 1);
        params[p] = '';
      });
    }
    if (declares) {
      $.each(declares, function(index, param) {
        param = param.match(/(\w+)/g);
        if (param && param.length >= 2) {
          delete params[param[1]];
        }
      });
    }
    if (defaults) {
      $.each(defaults, function(index, param) {
        var line = param.match(/(\w+)/g);
        if (line && line.length >= 2) {
          var name = line[1];
          params[name] = param.substring(param.indexOf(name) + name.length + 1);
        }
      });
    }
    if (macro_defines) {
      $.each(macro_defines, function(index, params_line) {
        var param_line = params_line.match(/(\w+)/g);
        if (param_line && param_line.length > 2) {
          $.each(param_line, function(index, param) {
            if (index >= 2) { // Skips define NAME
              delete params[param];
            }
          });
        }
      });
    }
    if (macro_returns) {
      $.each(macro_returns, function(index, params_line) {
        var param_line = params_line.match(/(\w+)/g);
        if (param_line) {
          $.each(param_line, function(index, param) {
            if (index >= 1) { // Skip returns
              delete params[param];
            }
          });
        }
      });
    }

    $.each(self.parameters(), function(index, param) {
      params[param.name()] = param.value();
    });

    return params;
  };

  self.hadoopProperties = ko.observableArray([]);
  ko.utils.arrayForEach(pigScript.hadoopProperties, function (property) {
    self.hadoopProperties.push(new HadoopProperty({name: property.name, value: property.value}));
  });
  self.addHadoopProperties = function () {
    self.hadoopProperties.push(new HadoopProperty({name: '', value: ''}));
    self.updateParentModel();
  };
  self.removeHadoopProperties = function () {
    self.hadoopProperties.remove(this);
    self.updateParentModel();
  };

  self.resources = ko.observableArray([]);
  ko.utils.arrayForEach(pigScript.resources, function (resource) {
    self.resources.push(new Resource({type: resource.type, value: resource.value}));
  });
  self.addResource = function () {
    self.resources.push(new Resource({type: 'file', value: ''}));
    self.updateParentModel();
  };
  self.removeResource = function () {
    self.resources.remove(this);
    self.updateParentModel();
  };

  self.parentModel = pigScript.parentModel;
  self.updateParentModel = function () {
    if (typeof self.parentModel != "undefined" && self.parentModel != null) {
      self.parentModel.isDirty(true);
    }
  }

  self.name.subscribe(function (name) {
    self.updateParentModel();
  });
}

var Workflow = function (wf) {
  return {
    id: wf.id,
    scriptId: wf.scriptId,
    scriptContent: wf.scriptContent,
    lastModTime: wf.lastModTime,
    endTime: wf.endTime,
    status: wf.status,
    statusClass: "label " + getStatusClass(wf.status),
    isRunning: wf.isRunning,
    duration: wf.duration,
    appName: wf.appName,
    progress: wf.progress,
    progressPercent: wf.progressPercent,
    progressClass: "bar " + getStatusClass(wf.status, "bar-"),
    user: wf.user,
    absoluteUrl: wf.absoluteUrl,
    watchUrl: wf.watchUrl,
    canEdit: wf.canEdit,
    killUrl: wf.killUrl,
    created: wf.created,
    run: wf.run
  }
}


var PigViewModel = function (props) {
  var self = this;

  self.LABELS = props.labels;

  self.LIST_SCRIPTS = props.listScripts;
  self.SAVE_URL = props.saveUrl;
  self.RUN_URL = props.runUrl;
  self.STOP_URL = props.stopUrl;
  self.COPY_URL = props.copyUrl;
  self.DELETE_URL = props.deleteUrl;

  self.isLoading = ko.observable(false);
  self.allSelected = ko.observable(false);
  self.submissionVariables = ko.observableArray([]);

  self.scripts = ko.observableArray([]);

  self.filteredScripts = ko.observableArray(self.scripts());

  self.runningScripts = ko.observableArray([]);
  self.completedScripts = ko.observableArray([]);

  self.isDashboardLoaded = false;
  self.isDirty = ko.observable(false);

  var _defaultScript = {
    id: -1,
    docId: -1,
    name: self.LABELS.NEW_SCRIPT_NAME,
    script: self.LABELS.NEW_SCRIPT_CONTENT,
    parameters: self.LABELS.NEW_SCRIPT_PARAMETERS,
    resources: self.LABELS.NEW_SCRIPT_RESOURCES,
    hadoopProperties: self.LABELS.NEW_SCRIPT_HADOOP_PROPERTIES,
    parentModel: self,
    can_write: true
  };

  self.currentScript = ko.observable(new PigScript(_defaultScript));
  self.loadingScript = null;
  self.currentDeleteType = ko.observable("");

  self.selectedScripts = ko.computed(function () {
    return ko.utils.arrayFilter(self.scripts(), function (script) {
      return script.selected();
    });
  }, self);

  self.selectedScript = ko.computed(function () {
    return self.selectedScripts()[0];
  }, self);

  self.selectAll = function () {
    self.allSelected(! self.allSelected());
    ko.utils.arrayForEach(self.scripts(), function (script) {
      script.selected(self.allSelected());
    });
    return true;
  };

  self.getScriptById = function (id) {
    var _s = null;
    ko.utils.arrayForEach(self.scripts(), function (script) {
      if (script.id() == id) {
        _s = script;
      }
    });
    return _s;
  }

  self.filterScripts = function (filter) {
    self.filteredScripts(ko.utils.arrayFilter(self.scripts(), function (script) {
      return script.isDesign() && script.name().toLowerCase().indexOf(filter.toLowerCase()) > -1
    }));
  };

  self.loadScript = function (id) {
    var _s = self.getScriptById(id);
    if (_s != null) {
      self.currentScript(_s);
    }
    else {
      self.currentScript(new PigScript(_defaultScript));
    }
  }

  self.confirmNewScript = function () {
    if (self.isDirty()) {
      showConfirmModal();
    }
    else {
      self.newScript();
    }
  };

  self.confirmScript = function () {
    if (self.loadingScript != null){
      self.viewScript(self.loadingScript);
    }
    else {
      self.newScript();
    }
  };

  self.newScript = function () {
    self.loadingScript = null;
    self.currentScript(new PigScript(_defaultScript));
    self.isDirty(false);
    $("#confirmModal").modal("hide");
    $(document).trigger("loadEditor");
    $(document).trigger("showEditor");
    $(document).trigger("clearLogs");
  };

  self.editScript = function (script) {
    $(document).trigger("showEditor");
  };

  self.editScriptProperties = function (script) {
    $(document).trigger("showProperties");
  };

  self.showScriptLogs = function (script) {
    $(document).trigger("showLogs");
  };

  self.confirmViewScript = function (script) {
    if (self.isDirty()) {
      self.loadingScript = script;
      showConfirmModal();
    }
    else {
      self.viewScript(script);
    }
  };

  self.viewScript = function (script) {
    self.loadingScript = null;
    self.currentScript(script);
    self.isDirty(false);
    $("#confirmModal").modal("hide");
    $(document).trigger("loadEditor");
    $(document).trigger("showEditor");
  };

  self.saveScript = function () {
    if (self.LABELS.NEW_SCRIPT_NAME == self.currentScript().name()){
      showNameModal();
    }
    else {
      $("#nameModal").modal("hide");
      callSave(self.currentScript());
      self.isDirty(false);
    }
  };

  self.runScript = function () {
    $("#withLogs").empty();
    callRun(self.currentScript());
  };

  self.copyScript = function () {
    callCopy(self.currentScript());
    viewModel.isDirty(true);
  };

  self.confirmDeleteScript = function () {
    self.currentDeleteType("single");
    showDeleteModal();
  };

  self.stopScript = function () {
    callStop(self.currentScript());
  };

  self.listRunScript = function () {
    self.currentScript(self.selectedScript());
    self.runOrShowSubmissionModal();
  };

  self.listCopyScript = function () {
    callCopy(self.selectedScript());
  };

  self.listConfirmDeleteScripts = function () {
    self.currentDeleteType("multiple");
    showDeleteModal();
  };

  self.deleteScripts = function () {
    var ids = [];
    if (self.currentDeleteType() == "single") {
      ids.push(self.currentScript().id());
    }
    if (self.currentDeleteType() == "multiple") {
      $(self.selectedScripts()).each(function (index, script) {
        ids.push(script.id());
      });
    }
    callDelete(ids);
  };

  self.updateScripts = function () {
    $.getJSON(self.LIST_SCRIPTS, function (data) {
      self.scripts(ko.utils.arrayMap(data, function (script) {
        script.parentModel = self;
        return new PigScript(script);
      }));
      self.filteredScripts(self.scripts());
      $(document).trigger("scriptsRefreshed");
    });
  };

  self.updateDashboard = function (workflows) {
    self.isDashboardLoaded = true;
    var koWorkflows = ko.utils.arrayMap(workflows, function (wf) {
      return new Workflow(wf);
    });
    self.runningScripts(ko.utils.arrayFilter(koWorkflows, function (wf) {
      return wf.isRunning
    }));
    self.completedScripts(ko.utils.arrayFilter(koWorkflows, function (wf) {
      return !wf.isRunning
    }));
  }

  self.runOrShowSubmissionModal = function runOrShowSubmissionModal() {
    var script = self.currentScript();
    if (! $.isEmptyObject(script.getParameters())) {
      self.submissionVariables.removeAll();
      $.each(script.getParameters(), function (key, value) {
        self.submissionVariables.push({'name': key, 'value': value});
      });
      $("#runScriptBtn").button("reset");
      $("#runScriptBtn").attr("data-loading-text", $("#runScriptBtn").text() + " ...");
      $("#submitModal").modal({
        keyboard: true,
        show: true
      });
    } else {
      self.runScript();
    }
  };

  self.showStopModal = function showStopModal() {
    $("#stopScriptBtn").button("reset");
    $("#stopScriptBtn").attr("data-loading-text", $("#stopScriptBtn").text() + " ...");
    $("#stopModal").modal({
      keyboard: true,
      show: true
    });
  }

  self.showFileChooser = function showFileChooser() {
    var inputPath = this;
    var path = inputPath.value().substr(0, inputPath.value().lastIndexOf("/"));
    $("#filechooser").jHueFileChooser({
      initialPath: path,
      onFileChoose: function (filePath) {
        inputPath.value(filePath);
        $("#chooseFile").modal("hide");
      },
      createFolder: false
    });
    $("#chooseFile").modal("show");
  };

  function showDeleteModal() {
    $(".deleteMsg").addClass("hide");
    if (self.currentDeleteType() == "single") {
      $(".deleteMsg.single").removeClass("hide");
    }
    if (self.currentDeleteType() == "multiple") {
      if (self.selectedScripts().length > 1) {
        $(".deleteMsg.multiple").removeClass("hide");
      }
      else {
        $(".deleteMsg.single").removeClass("hide");
      }
    }
    $("#deleteModal").modal({
      keyboard: true,
      show: true
    });
  }

  function showStopModal() {
    $(".stopMsg").addClass("hide");
    if (self.currentStopType() == "single") {
      $(".stopMsg.single").removeClass("hide");
    }
    if (self.currentStopType() == "multiple") {
      if (self.selectedScripts().length > 1) {
        $(".stopMsg.multiple").removeClass("hide");
      } else {
        $(".stopMsg.single").removeClass("hide");
      }
    }
    $("#stopModal").modal({
      keyboard: true,
      show: true
    });
  }

  function showConfirmModal() {
    $("#confirmModal").modal({
      keyboard: true,
      show: true
    });
  }

  function showNameModal() {
    $("#nameModal").modal({
      keyboard: true,
      show: true
    });
  }

  function updateScript(script, data) {
    script.id(data.id);
    script.docId(data.docId);
  }

  function callSave(script) {
    $(document).trigger("saving");
    $.post(self.SAVE_URL,
        {
          id: script.id(),
          name: script.name(),
          script: script.script(),
          parameters: ko.toJSON(script.parameters()),
          resources: ko.toJSON(script.resources()),
          hadoopProperties: ko.toJSON(script.hadoopProperties()),
        },
        function (data) {
          updateScript(self.currentScript(), data);
          self.updateScripts();
          $(document).trigger("saved");
        }, "json").fail( function(xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        });
  }

  function callRun(script) {
    self.currentScript(script);
    $(document).trigger("clearLogs");
    script.isRunning(true);
    script.actions([]);
    $(document).trigger("showLogs");
    $(document).trigger("running");
    $("#submitModal").modal("hide");
    $.post(self.RUN_URL,
        {
          id: script.id(),
          name: script.name(),
          script: script.script(),
          parameters: ko.toJSON(script.parameters()),
          submissionVariables: ko.utils.stringifyJson(self.submissionVariables()),
          resources: ko.toJSON(script.resources()),
          hadoopProperties: ko.toJSON(script.hadoopProperties())
        },
        function (data) {
          if (data.id && self.currentScript().id() != data.id){
            updateScript(self.currentScript(), data);
            $(document).trigger("loadEditor");
          }
          script.isRunning(true);
          script.watchUrl(data.watchUrl);
          $(document).trigger("startLogsRefresh");
          self.updateScripts();
        }, "json").fail( function(xhr, textStatus, errorThrown) {
          $(document).trigger("error", xhr.responseText);
        });
  }

  function callStop(script) {
    $(document).trigger("stopping");
    $.post(self.STOP_URL, {
          id: script.id()
        },
        function (data) {
          $(document).trigger("stopped");
          $("#stopModal").modal("hide");
        }, "json"
    ).fail(function () {
      self.currentScript().isRunning(false);
      $(document).trigger("stopError");
      $(document).trigger("stopped");
      $("#stopModal").modal("hide");
    });
  }

  function callCopy(script) {
    $.post(self.COPY_URL,
        {
          id: script.id()
        },
        function (data) {
          data.parentModel = self;
          self.currentScript(new PigScript(data));
          $(document).trigger("loadEditor");
          self.updateScripts();
        }, "json");
  }

  function callDelete(ids) {
    if (ids.indexOf(self.currentScript().id()) > -1) {
      self.currentScript(new PigScript(_defaultScript));
      $(document).trigger("loadEditor");
    }
    $.post(self.DELETE_URL, {
      ids: ids.join(",")
    },
    function (data) {
      self.updateScripts();
      $("#deleteModal").modal("hide");
      viewModel.isDirty(false);
    }, "json");
  }

  self.viewSubmittedScript = function (workflow) {
    self.loadScript(workflow.scriptId);
    self.currentScript().script(workflow.scriptContent);
    self.currentScript().isRunning(true);
    self.currentScript().watchUrl(workflow.watchUrl);
    $(document).trigger("loadEditor");
    $(document).trigger("clearLogs");
    $(document).trigger("startLogsRefresh");
    $(document).trigger("showLogs");
  };

  self.showLogsInterval = -1;
  self.showLogsAtEnd = true;
  self.showLogs = function (workflow) {
    window.clearInterval(self.showLogsInterval);
    $("#logsModal pre").scroll(function () {
      self.showLogsAtEnd = $(this).scrollTop() + $(this).height() + 20 >= $(this)[0].scrollHeight;
    });
    if (workflow.isRunning) {
      $("#logsModal i").removeClass("hide");
      $("#logsModal pre").addClass("hide");
      $("#logsModal").modal({
        keyboard: true,
        show: true
      });
      $("#logsModal").on("hide", function () {
        window.clearInterval(self.showLogsInterval);
      });
      self.showLogsInterval = window.setInterval(function () {
        $.getJSON(workflow.watchUrl, function (data) {
          if (data.workflow && !data.workflow.isRunning) {
            window.clearInterval(self.showLogsInterval);
          }
          if (data.logs.pig) {
            $("#logsModal i").addClass("hide");
            $("#logsModal pre").removeClass("hide");
            var _logsEl = $("#logsModal pre");
            var newLines = data.logs.pig.split("\n").slice(_logsEl.html().split("<br>").length);
            if (newLines.length > 0){
              _logsEl.html(_logsEl.html() + newLines.join("<br>") + "<br>");
            }
            if (self.showLogsAtEnd) {
              _logsEl.scrollTop(_logsEl[0].scrollHeight - _logsEl.height());
            }
          }
        });
      }, 1000);
    }
  };
};
