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


//// Menu items
function highlightMainMenu(mainSection) {
  $(".nav-pills li").removeClass("active");
  $("a[href='#" + mainSection + "']").parent().addClass("active");
}

function highlightMenu(section) {
  $(".nav-list li").removeClass("active");
  $("li[data-section='" + section + "']").addClass("active");
}

function showMainSection(mainSection) {
  if ($("#" + mainSection).is(":hidden")) {
    $(".mainSection").hide();
    $("#" + mainSection).show();
    highlightMainMenu(mainSection);
  }
}

function showSection(mainSection, section) {
  showMainSection(mainSection);
  $(document).trigger('show_section', section);
  if ($("#" + section).is(":hidden")) {
    $(".section").hide();
    $("#" + section).show();
    highlightMenu(section);
  }
}

function showSubsection(mainSection, section, subSection) {
  showSection(mainSection, section);
  if ($("#" + subSection).is(":hidden")) {
    $(".subSection").hide();
    $("#" + subSection).show();
  }
}


//// Constructors
function create_connection(attrs, options) {
  var options = options || {};
  options.modelDict = attrs || {};
  var node = new connections.Connection(options);
  // Need a copy of the forms so that when editing
  // we don't re-use forms.
  $.each(viewModel.connector().con_forms(), function(index, form) {
    node.connector.push($.extend(true, {}, form));
  });
  $.each(viewModel.framework().con_forms(), function(index, form) {
    node.framework.push($.extend(true, {}, form));
  });
  return node;
}


function create_job(attrs, options) {
  var options = options || {};
  options.modelDict = attrs || {};
  var node = new jobs.Job(options);
  return node;
}


//// View Models
var viewModel = new (function() {
  var self = this;

  self.jobWizard = new wizard.Wizard();
  self.errors = ko.observable({});
  self.warnings = ko.observable({});
  self.framework = ko.observable();
  self.connectors = ko.observableArray();
  self.connections = ko.observableArray();
  self.jobs = ko.observableArray();
  self.connection = ko.observable();
  self.editConnection = ko.observable();
  self.modal = {
    'name': ko.observable()
  };
  self.filter = ko.observable("");
  self.shownSection = ko.observable("");
  self.isDirty = ko.observable(false);
  self.isLoading = ko.observable(false);
  self.isReady = ko.observable(false);

  self.isReady.subscribe(function(value) {  // fixes problem with too fast rendering engines that display chunks of html before KO bindings
    if (value){
      $(document).trigger('isready');
    }
  });

  // Must always have a value.
  self.connector = ko.computed(function() {
    // Fall back to first connector so that a connector is selected when we are creating a connection.
    if (!self.connection()) {
      return self.connectors()[0];
    }
    var connectorArr = ko.utils.arrayFilter(self.connectors(), function (connector) {
      return connector.id() == self.connection().connector_id();
    });
    return (connectorArr.length > 0) ? connectorArr[0] : self.connectors()[0];
  });
  self.persistedJobs = ko.computed(function() {
    return ko.utils.arrayFilter(self.jobs(), function (job) {
      return job.persisted();
    });
  });
  self.persistedConnections = ko.computed(function() {
    return ko.utils.arrayFilter(self.connections(), function (connection) {
      return connection.persisted();
    });
  });
  self.filteredJobs = ko.computed(function() {
    var filter = self.filter().toLowerCase();
    return ko.utils.arrayFilter(self.persistedJobs(), function (job) {
      if (job.name()) {
        return job.name().toLowerCase().indexOf(filter) > -1 || job.type().toLowerCase().indexOf(filter) > -1;
      } else {
        return false;
      }
    });
  });
  self.selectedJobs = ko.computed(function() {
    return ko.utils.arrayFilter(self.jobs(), function (job) {
      return job.selected();
    });
  });
  self.job = ko.computed(function() {
    if (self.selectedJobs().length > 0) {
      return self.selectedJobs()[0];
    }
    return null;
  });
  self.allJobsSelected = ko.computed(function () {
    return self.selectedJobs().length > 0 && self.selectedJobs().length == self.jobs().length;
  });


  // Update forms for connectors, jobs, and connections.
  // In sqoop, the connector and framework provides
  // attributes that need to be filled in for connections
  // and jobs. The framework and connector will provide
  // different forms for IMPORT and EXPORT jobs.
  self.framework.subscribe(function(value) {
    // We assume that the framework components
    // are not going to change so we do not update connection
    // and job objects unless they lack forms.
    if (value) {
      if (self.editConnection() && self.editConnection().framework().length == 0) {
        self.editConnection().framework(value.con_forms());
      }
      if (self.job() && self.job().framework().length == 0) {
        var type = self.job().type().toUpperCase();
        self.job().framework(value.job_forms[type]());
      }
    }
  });

  self.connector.subscribe(function(value) {
    // We assume that the connectors component
    // are not going to change so we do not update connection
    // and job objects unless they lack forms.
    if (value) {
      if (self.editConnection() && self.editConnection().connector().length == 0) {
        self.editConnection().connector(value.con_forms());
      }
      if (self.job() && self.job().connector().length == 0) {
        var type = self.job().type().toUpperCase();
        self.job().connector(value.job_forms[type]());
      }
    }
  });

  // Forms are swapped between IMPORT and EXPORT types.
  // Use of "beforeChange" subscription event to
  // remove subscriptions and help with swapping.
  var job_type_subscriptions = [];
  var old_connector_forms = {
    'IMPORT': null,
    'EXPORT': null
  };
  var old_framework_forms = {
    'IMPORT': null,
    'EXPORT': null
  };
  self.job.subscribe(function(old_job) {
    if (job_type_subscriptions) {
      $.each(job_type_subscriptions, function(index, subscription) {
        subscription.dispose();
      });
    }
  }, self, "beforeChange");
  self.job.subscribe(function(job) {
    if (job) {
      var type = job.type().toUpperCase();

      if (self.connector() && job.connector().length == 0) {
        job.connector(self.connector().job_forms[type]());
      }

      if (self.framework() && job.framework().length == 0) {
        job.framework(self.framework().job_forms[type]());
      }

      job_type_subscriptions.push(job.type.subscribe(function(new_type) {
        var connector = old_connector_forms[new_type] || self.connector().job_forms[new_type]();
        var framework = old_framework_forms[new_type] || self.framework().job_forms[new_type]();
        old_connector_forms[new_type] = null;
        old_framework_forms[new_type] = null;
        job.connector(connector);
        job.framework(framework);
      }));

      job_type_subscriptions.push(job.type.subscribe(function(old_type) {
        if (job.connector().length > 0) {
          old_connector_forms[old_type] = job.connector();
        }
        if (job.framework().length > 0) {
          old_framework_forms[old_type] = job.framework();
        }
      }, self, "beforeChange"));
    }
  });

  self.editConnection.subscribe(function() {
    if (self.editConnection()) {
      if (self.connector() && self.editConnection().connector().length == 0) {
        self.editConnection().connector(self.connector().con_forms());
      }
      if (self.framework() && !self.editConnection().framework().length == 0) {
        self.editConnection().framework(self.framework().con_forms());
      }
    }
  });

  self.job.subscribe(function() {
    self.errors({});
    self.warnings({});
  });

  self.newConnection = function() {
    var self = this;
    if (!self.connection() || self.connection().persisted()) {
      var conn = create_connection();
      self.editConnection(conn);
    }
  };

  self.saveConnection = function() {
    var connection = self.editConnection();
    if (connection) {
      connection.connector_id(self.connector().id());
      connection.save();
    }
  };

  self.getConnectionById = function(id) {
    var connection = null;
    $.each(self.connections(), function(index, conn) {
      if (conn.id() == id) {
        connection = conn;
      }
    });
    return connection;
  };

  self.chooseConnectionById = function(id) {
    var self = this;
    self.editConnection(self.getConnectionById(id) || self.editConnection());
  };

  self.deselectAllConnections = function() {
    $.each(self.connections(), function(index, value) {
      value.selected(false);
    });
  };

  self.newJob = function(defaultName) {
    var self = this;
    if (!self.job() || self.job().persisted()) {
      var job = create_job();
      job.name(defaultName);
      self.jobs.push(job);
      self.deselectAllJobs();
      job.selected(true);
    }
  };

  self.saveJob = function() {
    var job = self.job();
    if (job) {
      job.connector_id(self.connector().id());
      job.connection_id(self.connection().id());
      job.save();
    }
  };

  self.chooseJobById = function(id) {
    var found_job = false;
    $.each(self.jobs(), function(index, job) {
      if (job.id() == id) {
        found_job = true;
        job.selected(true);
      } else {
        job.selected(false);
      }
    });
    return found_job;
  };

  self.toggleAllJobsSelected = function() {
    if (!self.allJobsSelected()) {
      self.selectAllJobs();
    } else {
      self.deselectAllJobs();
    }
  };

  self.selectAllJobs = function() {
    $.each(self.jobs(), function(index, value) {
      value.selected(true);
    });
  };

  self.deselectAllJobs = function() {
    $.each(self.jobs(), function(index, value) {
      value.selected(false);
    });
  };

  self.label = function(component, name) {
    var self = this;
    return self[component]().resources[name + '.label'];
  };

  self.help = function(component, name) {
    var self = this;
    return self[component]().resources[name + '.help'];
  };

  self.getDatabaseByConnectionId = function(id) {
    var self = this;
    var connection = self.getConnectionById(id);
    if (connection) {
      var connection_string = connection.connectionString();
      if (connection_string) {
        var connection_string_parts = connection.connectionString().split(':');
        if (connection_string_parts.length > 2) {
          return connection_string_parts[1].toUpperCase();
        }
      }
    }
    return null;
  };

  self.showModal = function(name) {
    var self = this;
    self.modal.name(name);
    $('#modal-container').modal();
  };

  self.showDeleteJobModal = function() {
    var self = this;
    var name = 'delete-job-modal';
    self.showModal(name);
  };

  self.showDeleteConnectionModal = function() {
    var self = this;
    var name = 'delete-connection-modal';
    self.showModal(name);
  }

  self.showFileChooser = function showFileChooser() {
    var inputPath = this;
    var path = inputPath.value();
    $("#filechooser").jHueFileChooser({
      initialPath: path,
      onFolderChoose: function (filePath) {
    	inputPath.value(filePath);
        $("#chooseFile").modal("hide");
      },
      onFileChoose:function (filePath) {
    	inputPath.value(filePath);
        $("#chooseFile").modal("hide");
      },
      createFolder: false,
      selectFolder: true,
      uploadFile:true
    });
    $("#chooseFile").modal("show");
  };
})();

//// Event handling
function set_framework(e, framework, options) {
  viewModel.framework(framework);
}

function set_connectors(e, connectors, options) {
  viewModel.connectors(connectors);
}

function set_connections(e, connections, options) {
  viewModel.connections(connections);
  if (viewModel.connections().length > 0) {
    viewModel.connection(viewModel.connections()[0]);
  }
}

function set_jobs(e, jobs, options) {
  viewModel.jobs.removeAll();
  viewModel.jobs(jobs);
}

function update_job_submissions(e, submissions, options) {
  $.each(submissions, function(index, submission) {
    var job = jobs.getJob(submission.job());
    if (job) {
      job.submission(submission);
    }
  });
}

$(document).on('loaded.framework', set_framework);
$(document).on('loaded.connectors', set_connectors);
$(document).on('loaded.connections', set_connections);
$(document).on('loaded.jobs', set_jobs);
$(document).on('loaded.submissions', update_job_submissions);
