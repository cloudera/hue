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
  self.link = ko.observable();
  self.jobs = ko.observableArray();
  self.from_link = ko.observable();
  self.to_link = ko.observable();
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

  self.connector = ko.computed(function() {
    if (self.link() && self.link().connector_id()) {
      for (var index in self.connectors()) {
        if (self.connectors()[index].id() == self.link().connector_id()) {
          return self.connectors()[index];
        }
      }
    }
  });

  // Must always have a value.
  self.from_connector = ko.computed(function() {
    // Fall back to first connector so that a connector is selected when we are creating a link.
    if (!self.from_link()) {
      return self.connectors()[0];
    }
    var connectorArr = ko.utils.arrayFilter(self.connectors(), function (connector) {
      return connector.id() == self.from_link().connector_id();
    });
    return (connectorArr.length > 0) ? connectorArr[0] : self.connectors()[0];
  });
  // Must always have a value.
  self.to_connector = ko.computed(function() {
    // Fall back to first connector so that a connector is selected when we are creating a link.
    if (!self.to_link()) {
      return self.connectors()[0];
    }
    var connectorArr = ko.utils.arrayFilter(self.connectors(), function (connector) {
      return connector.id() == self.to_link().connector_id();
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
        return job.name().toLowerCase().indexOf(filter) > -1 || job.fromLabel().toLowerCase().indexOf(filter) > -1 || job.toLabel().toLowerCase().indexOf(filter) > -1;
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


  // Make sure jobs have connectors and links and links have connectors
  self.connectors.subscribe(function() {
    $.each(self.links(), function(index, link) {
      link.connectors(self.connectors());
    });
    $.each(self.jobs(), function(index, job) {
      job.connectors(self.connectors());
    });
  });

  self.links.subscribe(function() {
    $.each(self.links(), function(index, link) {
      link.connectors(self.connectors());
    });
    $.each(self.jobs(), function(index, job) {
      job.links(self.links());
    });
  });

  self.jobs.subscribe(function() {
    $.each(self.jobs(), function(index, job) {
      job.connectors(self.connectors());
      job.links(self.links());
    });
  });

  self.connector.subscribe(function() {
    if (self.connector() && self.link() && !self.link().persisted()) {
      self.link().link_config_values(self.connector()['link-config']());
    }
  });

  self.links.subscribe(function() {
    if (self.links().length > 0) {
      if (!self.from_link()) {
        self.from_link(self.links()[0]);
      }

      if (!self.to_link()) {
        self.to_link(self.links()[0]);
      }
    }
  });

  self.from_link.subscribe(function() {
    if (self.from_link() && self.from_connector() && self.job()) {
      self.from_link().link_config_values(self.from_connector()['link-config']());
      self.job().from_config_values(self.from_connector()['job-config'].FROM());
    }
  });

  self.to_link.subscribe(function() {
    if (self.to_link() && self.to_connector() && self.job()) {
      self.to_link().link_config_values(self.to_connector()['link-config']());
      self.job().to_config_values(self.to_connector()['job-config'].TO());
    }
  });

  self.job.subscribe(function() {
    self.errors({});
    self.warnings({});

    if (self.job() && !self.job().persisted()) {
      if (self.from_connector()) {
        self.job().from_config_values(self.from_connector()['job-config'].FROM());
      }

      if (self.to_connector()) {
        self.job().to_config_values(self.to_connector()['job-config'].TO());
      }
    }
  });


  self.newLink = function() {
    var self = this;
    self.link(create_link());
  };

  self.saveLink = function() {
    if (self.link()) {
      if (!self.link().persisted()) {
        self.link().connector_id(self.connector().id());
      }
      self.link().save();
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
    self.link(self.getLinkById(id) || self.link());
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
      if (!job.from_link_id()) {
        job.from_connector_id((self.from_connector()) ? self.from_connector().id() : null);
        job.from_link_id((self.from_link()) ? self.from_link().id() : null);
      }

      if (!job.to_link_id()) {
        job.to_connector_id((self.to_connector()) ? self.to_connector().id() : null);
        job.to_link_id((self.to_link()) ? self.to_link().id() : null);
      }

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
    if (component == 'connector') {
      for (var index in self.connectors()) {
        var label = self.connectors()[index]['all-config-resources'][name + '.label'];
        if (label) {
          return label;
        }
      }
    } else {
      return self['driver']()['all-config-resources'][name + '.label'];
    }
  };

  self.help = function(component, name) {
    var self = this;
    if (component == 'connector') {
      for (var index in self.connectors()) {
        var help = self.connectors()[index]['all-config-resources'][name + '.help'];
        if (help) {
          return help;
        }
      }
    } else {
      return self[component]()['all-config-resources'][name + '.help'];
    }
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
  ko.utils.arrayFilter(connectors, function (connector) {
    return $.inArray(connector.name(), connectors.CONNECTOR_NAMES) != -1;
  });
  viewModel.connectors(connectors);
}

function set_links(e, links, options) {
  viewModel.links(links);
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
