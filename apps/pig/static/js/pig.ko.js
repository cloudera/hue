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


var PigScript = function (pigScript) {
  return {
    id: ko.observable(pigScript.id),
    name: ko.observable(pigScript.name),
    script: ko.observable(pigScript.script),
    isRunning: ko.observable(false),
    selected: ko.observable(false),
    watchUrl: ko.observable(""),
    actions: ko.observableArray([]),
    handleSelect: function (row, e) {
      this.selected(!this.selected());
    },
    hovered: ko.observable(false),
    toggleHover: function (row, e) {
      this.hovered(!this.hovered());
    }
  }
}

var Workflow = function (wf) {
  return {
    id: wf.id,
    lastModTime: wf.lastModTime,
    endTime: wf.endTime,
    status: wf.status,
    statusClass: "label " + getStatusClass(wf.status),
    isRunning: wf.isRunning,
    duration: wf.duration,
    appName: wf.appName,
    progress: wf.progress,
    progressClass: "bar " + getStatusClass(wf.status, "bar-"),
    user: wf.user,
    absoluteUrl: wf.absoluteUrl,
    canEdit: wf.canEdit,
    killUrl: wf.killUrl,
    created: wf.created,
    run: wf.run
  }
}


var PigViewModel = function (scripts, props) {
  var self = this;

  self.LABELS = props.labels;

  self.LIST_SCRIPTS = props.listScripts;
  self.SAVE_URL = props.saveUrl;
  self.RUN_URL = props.runUrl;
  self.COPY_URL = props.copyUrl;
  self.DELETE_URL = props.deleteUrl;

  self.isLoading = ko.observable(false);
  self.allSelected = ko.observable(false);

  self.scripts = ko.observableArray(ko.utils.arrayMap(scripts, function (pigScript) {
    return new PigScript(pigScript);
  }));

  self.filteredScripts = ko.observableArray(self.scripts());

  self.runningScripts = ko.observableArray([]);
  self.completedScripts = ko.observableArray([]);

  var _defaultScript = {
    id: -1,
    name: self.LABELS.NEW_SCRIPT_NAME,
    script: self.LABELS.NEW_SCRIPT_CONTENT
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
      return script.name().toLowerCase().indexOf(filter.toLowerCase()) > -1
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
          script: script.script()
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
          script: script.script()
        },
        function (data) {
          if (data.id && self.currentScript().id() != data.id){
            self.currentScript(script);
            $(document).trigger("loadEditor");
          }
          script.isRunning(true);
          script.watchUrl(data.watchUrl);
          $(document).trigger("startLogsRefresh");
          $(document).trigger("showLogs");
          self.updateScripts();
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
};
