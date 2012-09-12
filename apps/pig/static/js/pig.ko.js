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


var App = function (app) {
  return {
    id:app.id,
    name:app.name,
    archive:app.archive,
    submitUrl:app.submitUrl,
    watchUrl:app.watchUrl,
    saveUrl:app.saveUrl,
    killUrl:"",
    rerunUrl:"",
    description:app.description,
    isRunning:ko.observable(false),
    status:ko.observable(""),
    progress:ko.observable(""),
    progressCss:ko.observable("width: 0%"),
    intervalId:-1,
    actions:ko.observableArray(),
    output:ko.observable(""),
    tooltip:ko.observable("")
  }
}

var pigModel = function (serviceUrl, labels) {
  var self = this;

  self.serviceUrl = ko.observable(serviceUrl);
  self.LABELS = labels;
  self.apps = ko.observableArray();
  self.history = ko.observableArray();
  self.isLoading = ko.observable(true);

  self.retrieveData = function () {
    self.isLoading(true);

    $.getJSON(self.serviceUrl() + self.getDocId(), function (data) {
      self.apps(ko.utils.arrayMap(data.apps, function (app) {
        return getInitApp(app);
      }));
      self.isLoading(false);
      if ($){
        $(document).trigger("updateTooltips");
      }
    });

    function getInitApp(app) {
      var a = new App(app);
      a.tooltip(self.LABELS.TOOLTIP_PLAY);
      return a;
    }
  };
  
  self.getDocId = function() {
    var hash = window.location.hash;
    var jobId = ""
    if (hash != null && hash.indexOf("/") > -1) {
      jobId = hash.substring(hash.indexOf("/") + 1);
    }
    return jobId;
  }

  self.manageApp = function (app) {
    if (app.status() == "" || app.status() == "FAILED" || app.status() == "STOPPED") {
      self.submitApp(app);
    }
    if (app.isRunning()) {
      self.killApp(app);
    }
    if (app.status() == "SUCCEEDED") {
      self.rerunApp(app);
    }
  };

  self.submitApp = function (app) {
    $.post(app.submitUrl, $("#queryForm").serialize(), function (data) {
      window.location.hash = "#/" + data.jobId;
      app.watchUrl = data.watchUrl;
      self.updateAppStatus(app);
      app.intervalId = window.setInterval(function () {
        self.updateAppStatus(app);
      }, 1000);
    }, "json");
  };

  self.save = function (app) {
    $.post(app.submitUrl, $("#queryForm").serialize(), function (data) {
      if (self.getDocId() == "") {
    	  window.location.hash += "/" + data.doc_id;  
      }
      $.jHueNotify.info(self.LABELS.SAVED);
    }, "json");
  };
  
  self.killApp = function (app) {
    app.isRunning(false);
    app.status("STOPPED");
    app.tooltip(self.LABELS.TOOLTIP_PLAY);
    if (app.intervalId > -1) {
      window.clearInterval(app.intervalId);
      self.appendToHistory(app);
    }
    if ($) {
      $(document).trigger("updateTooltips");
    }
    if (app.killUrl) {
      $.post(app.killUrl,function (data) {
        if (data.status != 0) {
          $.jHueNotify.error(data.data);
        }
      }, "json").error(function () {
        $.jHueNotify.error(self.LABELS.KILL_ERROR);
      });
    }

  };

  self.rerunApp = function (app) {
    if (app.intervalId > -1) {
      window.clearInterval(app.intervalId);
    }
    self.submitApp(app);
  };

  self.updateAppStatus = function (app) {
    $.getJSON(app.watchUrl, function (watch) {
      var previousTooltip = app.tooltip();
      app.tooltip(self.LABELS.TOOLTIP_STOP);
      app.isRunning(watch.workflow.isRunning);
      app.status(watch.workflow.status);
      app.progress(watch.workflow.progress);
      app.progressCss("width: " + app.progress() + "%");
      app.actions(watch.workflow.actions);
      app.killUrl = watch.workflow.killUrl;
      app.rerunUrl = watch.workflow.rerunUrl;
      app.output(watch.output);
      if (!watch.workflow.isRunning) {
        window.clearInterval(app.intervalId);
        app.tooltip(self.LABELS.TOOLTIP_PLAY);
        self.appendToHistory(app);
      }
      if (app.tooltip() != previousTooltip) {
        if ($) {
          $(document).trigger("updateTooltips");
        }
      }
    });
  };

  self.resetAppStatus = function (app) {
    app.isRunning(false);
    app.status("");
  };

  self.appendToHistory = function (app) {
    var newApp = {
      id:app.id,
      name:app.name,
      when:moment().format('MM/DD/YYYY, h:mm:ss a'),
      archive:app.archive,
      submitUrl:app.submitUrl,
      watchUrl:app.watchUrl,
      killUrl:app.killUrl,
      rerunUrl:app.rerunUrl,
      description:app.description,
      isRunning:ko.observable(app.isRunning()),
      status:ko.observable(app.status()),
      progress:ko.observable(app.progress()),
      progressCss:ko.observable(app.progressCss()),
      intervalId:app.intervalId,
      actions:ko.observableArray(app.actions()),
      output:ko.observable(app.output())
    };
    var history = self.history();
    history.push(newApp);
    self.history(history);
  };

};
