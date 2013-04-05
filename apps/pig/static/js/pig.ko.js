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

var PigScript = function (pigScript) {
  var self = this;

  self.id = ko.observable(pigScript.id);
  self.isDesign = ko.observable(pigScript.isDesign);
  self.name = ko.observable(pigScript.name);
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
  self.parameters = ko.observableArray(pigScript.parameters);
  self.addParameter = function () {
    self.parameters.push({name: '', value: ''});
  };
  self.removeParameter = function () {
    self.parameters.remove(this);
  };
  self.getParameters = function () {
    var params = {};
    var variables = this.script().match(/\$(\w)+/g);
    if (variables) {
      $.each(variables, function(index, param) {
        var p = param.substring(1);
        params[p] = '';
        $.each(self.parameters(), function(index, param) {
          if (param['name'] == p) {
            params[p] = param['value'];
          }
        });
      });
    }
    return params;
  };
  self.resources = ko.observableArray([]);
  ko.utils.arrayForEach(pigScript.resources, function (resource) {
    self.resources.push(new Resource({type: resource.type, value: resource.value}));
  });
  self.addResource = function () {
    self.resources.push(new Resource({type: 'file', value: ''}));
  };
  self.removeResource = function () {
    self.resources.remove(this);
  };
}

var Workflow = function (wf) {
  return {
    id: wf.id,
    scriptId: wf.scriptId,
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
  self.COPY_URL = props.copyUrl;
  self.DELETE_URL = props.deleteUrl;

  self.isLoading = ko.observable(false);
  self.allSelected = ko.observable(false);
  self.submissionVariables = ko.observableArray([]);

  self.scripts = ko.observableArray([]);

  self.filteredScripts = ko.observableArray(self.scripts());

  self.runningScripts = ko.observableArray([]);
  self.completedScripts = ko.observableArray([]);

  var _defaultScript = {
    id: -1,
    name: self.LABELS.NEW_SCRIPT_NAME,
    script: self.LABELS.NEW_SCRIPT_CONTENT,
    parameters: self.LABELS.NEW_SCRIPT_PARAMETERS,
    resources: self.LABELS.NEW_SCRIPT_RESOURCES
  };

  self.currentScript = ko.observable(new PigScript(_defaultScript));
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
    self.allSelected(!self.allSelected());
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

  self.newScript = function () {
    self.currentScript(new PigScript(_defaultScript));
    $(document).trigger("loadEditor");
    $(document).trigger("showEditor");
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

  self.viewScript = function (script) {
    self.currentScript(script);
    $(document).trigger("loadEditor");
    $(document).trigger("showEditor");
  };

  self.saveScript = function () {
    callSave(self.currentScript());
  };

  self.runScript = function () {
    callRun(self.currentScript());
  };

  self.copyScript = function () {
    callCopy(self.currentScript());
  };

  self.confirmDeleteScript = function () {
    self.currentDeleteType("single");
    showDeleteModal();
  };

  self.listRunScript = function () {
    callRun(self.selectedScript());
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
        return new PigScript(script);
      }));
      self.filteredScripts(self.scripts());
      $(document).trigger("scriptsRefreshed");
    });
  };

  self.updateDashboard = function (workflows) {
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

  self.showSubmissionModal = function showSubmissionModal() {
    var script = self.currentScript();
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
  };

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

  function callSave(script) {
    $(document).trigger("saving");
    $.post(self.SAVE_URL,
        {
          id: script.id(),
          name: script.name(),
          script: script.script(),
          parameters: ko.utils.stringifyJson(script.parameters()),
          resources: ko.toJSON(script.resources())
        },
        function (data) {
          self.currentScript().id(data.id);
          $(document).trigger("saved");
          self.updateScripts();
        }, "json");
  }

  function callRun(script) {
    $(document).trigger("running");
    $.post(self.RUN_URL,
        {
          id: script.id(),
          name: script.name(),
          script: script.script(),
          parameters: ko.utils.stringifyJson(self.submissionVariables()),
          resources: ko.toJSON(script.resources())
        },
        function (data) {
          if (data.id && self.currentScript().id() != data.id){
            self.currentScript(script);
            $(document).trigger("loadEditor");
          }
          script.isRunning(true);
          script.watchUrl(data.watchUrl);
          $(document).trigger("startLogsRefresh");
          $(document).trigger("refreshDashboard");
          $(document).trigger("showLogs");
          self.updateScripts();
          $("#submitModal").modal("hide");
        }, "json");
  }

  function callCopy(script) {
    $.post(self.COPY_URL,
        {
          id: script.id()
        },
        function (data) {
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
    $.post(self.DELETE_URL,
        {
          ids: ids.join(",")
        },
        function (data) {
          self.updateScripts();
          $("#deleteModal").modal("hide");
        }, "json");
  }

  self.viewSubmittedScript = function (workflow) {
    self.loadScript(workflow.scriptId);
    self.currentScript().isRunning(true);
    self.currentScript().watchUrl(workflow.watchUrl);
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
      $("#logsModal img").removeClass("hide");
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
            $("#logsModal img").addClass("hide");
            $("#logsModal pre").removeClass("hide");
            var _logsEl = $("#logsModal pre");
            var newLines = data.logs.pig.split("\n").slice(_logsEl.text().split("\n").length);
            _logsEl.text(_logsEl.text() + newLines.join("\n"));
            if (self.showLogsAtEnd) {
              _logsEl.scrollTop(_logsEl[0].scrollHeight - _logsEl.height());
            }
          }
        });
      }, 1000);
    }
  };
};
