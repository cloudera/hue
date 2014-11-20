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
    $(document).trigger('shown_section', section);
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
function create_link(attrs, options) {
  var options = options || {};
  options.modelDict = attrs || {};
  var node = new links.Link(options);
  // Need a copy of the configs so that when editing
  // we don't re-use configs.
  $.each(viewModel.link().link_config_values(), function(index, config) {
    node.connector.push($.extend(true, {}, config));
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
  self.sqoop_errors = ko.observableArray([]);
  self.errors = ko.observable({});
  self.warnings = ko.observable({});
  self.driver = ko.observable();
  self.connectors = ko.observableArray();
  self.links = ko.observableArray();
  self.jobs = ko.observableArray();
  self.link = ko.observable();
  self.editLink = ko.observable();
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
    // Fall back to first connector so that a connector is selected when we are creating a link.
    if (!self.link()) {
      return self.connectors()[0];
    }
    var connectorArr = ko.utils.arrayFilter(self.connectors(), function (connector) {
      return connector.id() == self.link().connector_id();
    });
    return (connectorArr.length > 0) ? connectorArr[0] : self.connectors()[0];
  });
  self.persistedJobs = ko.computed(function() {
    return ko.utils.arrayFilter(self.jobs(), function (job) {
      return job.persisted();
    });
  });
  self.persistedLinks = ko.computed(function() {
    return ko.utils.arrayFilter(self.links(), function (link) {
      return link.persisted();
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
  self.filteredLinks = ko.computed(function() {
    var filter = self.filter().toLowerCase();
    return ko.utils.arrayFilter(self.persistedLinks(), function (link) {
      if (link.name()) {
        return link.name().toLowerCase().indexOf(filter) > -1 || link.type().toLowerCase().indexOf(filter) > -1;
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


  // The driver and connector provide configurations for job
  self.driver.subscribe(function(value) {
    // We assume that the driver components
    // are not going to change so w do not update job objects unless they lack configs.
    if (value) {
      if (self.job() && self.job().driver_config_values().length == 0) {
        self.job().driver_config_values(value.job_config());
      }
    }
  });

  self.connector.subscribe(function(value) {
    // We assume that the connectors component
    // are not going to change so we do not update link
    // and job objects unless they lack configs.
    if (value) {
      if (self.editLink() && self.editLink().link_config_values().length == 0) {
        self.editLink().link_config_values(value.link_config());
      }
      if (self.job() && self.job().from_config_values().length == 0) {
        self.job().from_config_values(value.job_config['FROM']());
      }
       if (self.job() && self.job().to_config_values().length == 0) {
        self.job().to_config_values(value.job_config['TO']());
      }
    }
  });

  // Forms are swapped between FROM and TO types.
  // Use of "beforeChange" subscription event to
  // remove subscriptions and help with swapping.
  var job_type_subscriptions = [];
  var old_connector_configs = {
    'FROM': null,
    'TO': null
  };
  var old_driver_configs = {
    'FROM': null,
    'TO': null
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

      if (self.from_config_values() && job.from_config_values().length == 0) {
        job.from_config_values(self.from_config_values());
      }

      if (self.to_config_values() && job.to_config_values().length == 0) {
        job.to_config_values(self.to_config_values());
      }
      if (self.driver_config_values() && job.driver_config_values().length == 0) {
        job.driver_config_values(self.driver_config_values());
      }

      /*job_type_subscriptions.push(job.type.subscribe(function(new_type) {
        var connector = old_connector_configs[new_type] || self.connector().job_configs[new_type]();
        var driver = old_driver_configs[new_type] || self.driver().job_configs[new_type]();
        old_connector_configs[new_type] = null;
        old_driver_configs[new_type] = null;
        job.connector(connector);
        job.driver(driver);
      }));

      job_type_subscriptions.push(job.type.subscribe(function(old_type) {
        if (job.connector().length > 0) {
          old_connector_configs[old_type] = job.connector();
        }
        if (job.driver_config_values().length > 0) {
          old_driver_configs[old_type] = job.driver();
        }
      }, self, "beforeChange"));*/
    }
  });

  self.editLink.subscribe(function() {
    if (self.editLink()) {
      if (self.link_config_values() && self.editLink().link_config_values().length == 0) {
        self.editLink().link_config_values(self.link_config_values());
      }
    }
  });

  self.job.subscribe(function() {
    self.errors({});
    self.warnings({});
  });

  self.newLink = function() {
    var self = this;
    if (!self.link() || self.link().persisted()) {
      var conn = create_link();
      self.editLink(conn);
    }
  };

  self.saveLink = function() {
    var link = self.editLink();
    if (link) {
      link.connector_id(self.connector().id());
      link.save();
    }
  };

  self.getLinkById = function(id) {
    var link = null;
    $.each(self.links(), function(index, conn) {
      if (conn.id() == id) {
        link = conn;
      }
    });
    return link;
  };

  self.chooseLinkById = function(id) {
    var self = this;
    self.editLink(self.getLinkById(id) || self.editLink());
  };

  self.deselectAllLinks = function() {
    $.each(self.links(), function(index, value) {
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
      if (!self.link()) {
        $(document).trigger('link_missing.job', [self, null, {}]);
        return;
      }
      job.connector_id((self.connector()) ? self.connector().id() : null);
      job.link_id((self.link()) ? self.link().id() : null);
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

  self.getDatabaseByLinkId = function(id) {
    var self = this;
    var link = self.getLinkById(id);
    if (link) {
      var link_string = link.linkString();
      if (link_string) {
        var link_string_parts = link.linkString().split(':');
        if (link_string_parts.length > 2) {
          return link_string_parts[1].toUpperCase();
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

  self.showDeleteLinkModal = function() {
    var self = this;
    var name = 'delete-link-modal';
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
function set_driver(e, driver, options) {
  viewModel.driver(driver);
}

function set_connectors(e, connectors, options) {
  viewModel.connectors(connectors);
}

function set_links(e, links, options) {
  viewModel.links(links);
  if (viewModel.links().length > 0) {
    viewModel.link(viewModel.links()[0]);
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

$(document).on('loaded.driver', set_driver);
$(document).on('loaded.connectors', set_connectors);
$(document).on('loaded.links', set_links);
$(document).on('loaded.jobs', set_jobs);
$(document).on('loaded.submissions', update_job_submissions);
