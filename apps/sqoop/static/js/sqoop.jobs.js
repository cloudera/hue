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



var jobs = (function($) {
  var job_registry = {};

  var JobModel = koify.Model.extend({
    'id': -1,
    'name': null,
    'type': 'IMPORT',
    'connector_id': 0,
    'connection_id': 0,
    'connector': [],
    'framework': [],
    'creation_date': null,
    'creation_user': null,
    'update_date': null,
    'update_user': null,
    'setImport': function(){
      this.type("IMPORT");
      // Huge hack for now
      $('a').filter(function(index) { return $(this).text() === "Step 2: To"; }).text("Step 2: From");
      $('a').filter(function(index) { return $(this).text() === "Step 3: From"; }).text("Step 3: To");
    },
    'setExport': function(){
      this.type("EXPORT");
      $('a').filter(function(index) { return $(this).text() === "Step 2: From"; }).text("Step 2: To");
      $('a').filter(function(index) { return $(this).text() === "Step 3: To"; }).text("Step 3: From");
    },
    'initialize': function(attrs) {
      var self = this;
      var _attrs = $.extend(true, {}, attrs);
      _attrs = transform_keys(_attrs, {
        'connector-id': 'connector_id',
        'connection-id': 'connection_id'
      });
      _attrs = transform_values(_attrs, {
        'connector': to_forms,
        'framework': to_forms
      });
      return _attrs;
    }
  });

  var Job = koify.Node.extend({
    'identifier': 'job',
    'persists': true,
    'model_class': JobModel,
    'base_url': '/sqoop/api/jobs/',
    'initialize': function() {
      var self = this;
      self.parent.initialize.apply(self, arguments);
      self.createdFormatted = ko.computed(function() {
        if (self.creation_date()) {
          return moment(self.creation_date()).format('MM/DD/YYYY hh:mm A');
        } else {
          return 0;
        }
      });
      self.updatedFormatted = ko.computed(function() {
        if (self.update_date()) {
          return moment(self.update_date()).format('MM/DD/YYYY hh:mm A');
        } else {
          return 0;
        }
      });
      self.selected = ko.observable();
      self.submission = ko.computed({
        owner: self,
        read: function () {
          return submissions.setDefaultSubmission(this.id());
        },
        write: function (submission) {
          submissions.putSubmission(submission);
          self.id.valueHasMutated();

          if (self.runningInterval == 0 && self.isRunning()) {
            self.runningInterval = setInterval(function() {
              if (!self.isRunning()) {
                clearInterval(self.runningInterval);
                self.runningInterval = 0;
              }

              self.getStatus();
            }, 2000);
          }
        }
      });
      self.persisted = ko.computed(function() {
        return self.id() > -1;
      });
      self.isRunning = ko.computed(function() {
        return self.submission() && $.inArray(self.submission().status(), ['BOOTING', 'RUNNING']) > -1;
      });
      self.hasSucceeded = ko.computed(function() {
        return self.submission() && $.inArray(self.submission().status(), ['SUCCEEDED']) > -1;
      });
      self.hasFailed = ko.computed(function() {
        return self.submission() && $.inArray(self.submission().status(), ['FAILURE_ON_SUBMIT', 'FAILED']) > -1;
      });
      self.outputDirectoryFilebrowserURL = ko.computed(function() {
        var output_directory = null;
        $.each(self.framework(), function(index, form) {
          if (form.name() == 'output') {
            $.each(form.inputs(), function(index, input) {
              if (input.name() == 'output.outputDirectory') {
                output_directory = input.value();
              }
            });
          }
        });
        return (output_directory) ? '/filebrowser/view' + output_directory : null;
      });
      self.inputDirectoryFilebrowserURL = ko.computed(function() {
          var input_directory = null;
          $.each(self.framework(), function(index, form) {
            if (form.name() == 'input') {
              $.each(form.inputs(), function(index, input) {
                if (input.name() == 'input.inputDirectory') {
                  input_directory = input.value();
                }
              });
            }
          });
          return (input_directory) ? '/filebrowser/view' + input_directory : null;
        });
      self.storageType = ko.computed(function() {
        var storage_type = null;
        $.each(self.framework(), function(index, form) {
    	  if (form.name() == 'input') {
            storage_type = 'HDFS'; // Hardcoded for now
    	  } else if (form.name() == 'output') {
            $.each(form.inputs(), function(index, input) {
              if (input.name() == 'output.storageType') {
                storage_type = input.value();
              }
            });
          }
        });
        return storage_type;
      });

      self.runningInterval = 0;
    },
    map: function() {
      var self = this;
      var mapping_options = $.extend(true, {
        'ignore': ['parent', 'initialize']
      }, forms.MapProperties);
      if ('__ko_mapping__' in self) {
        ko.mapping.fromJS(self.model, mapping_options, self);
      } else {
        var mapped = ko.mapping.fromJS(self.model, mapping_options);
        $.extend(self, mapped);
      }
    },
    'start': function(options) {
      var self = this;
      $(document).trigger('start.job', [options, self]);
      var options = $.extend({
        type: 'POST',
        success: function(data) {
          switch(data.status) {
            case 0:
              self.submission(new submissions.Submission({modelDict: data.submission}));
              $(document).trigger('started.job', [self, options, data.submission]);
            break;
            default:
            case 1:
              var error = data.errors[0];
              $(document).trigger('start_fail.job', [self, options, error]);
            break;
          }
        }
      }, options);
      self.request('/sqoop/api/jobs/' + self.id() + '/start', options);
    },
    'stop': function(options) {
      var self = this;
      $(document).trigger('start.job', [options, self]);
      var options = $.extend({
        type: 'POST',
        success: function(data) {
          switch(data.status) {
            case 0:
              self.submission(new submissions.Submission({modelDict: data.submission}));
              $(document).trigger('stopped.job', [self, options, data.submission]);
            break;
            default:
            case 1:
              $(document).trigger('stop_fail.job', [self, options, data]);
            break;
          }
        }
      }, options);
      self.request('/sqoop/api/jobs/' + self.id() + '/stop', options);
    },
    'getStatus': function(options) {
      var self = this;
      $(document).trigger('get_status.job', [self, options]);
      var options = $.extend({
        type: 'GET',
        success: function(data) {
          switch(data.status) {
            case 0:
              self.submission(new submissions.Submission({modelDict: data.submission}));
              $(document).trigger('got_status.job', [self, options, data.submission]);
            break;
            default:
            case 1:
              $(document).trigger('get_status_fail.job', [self, options, data]);
            break;
          }
        }
      }, options);
      self.request('/sqoop/api/jobs/' + self.id() + '/status', options);
    }
  });

  function fetch_jobs(options) {
    $(document).trigger('load.jobs', [options]);
    var request = $.extend({
      url: '/sqoop/api/jobs/',
      dataType: 'json',
      type: 'GET',
      success: fetcher_success('jobs', Job, options)
    }, options || {});
    $.ajax(request);
  }

  function put_job(job) {
    job_registry[job.id()] = job;
  }

  function get_job(id) {
    return job_registry[id];
  }

  function sync_jobs(jobs) {
    job_registry = {};
    $.each(jobs, function(index, job) {
      put_job(job);
    });
  }

  $(document).on('loaded.jobs', function(e, nodes, options) {
    sync_jobs(nodes);
  });

  return {
    'JobModel': JobModel,
    'Job': Job,
    'fetchJobs': fetch_jobs,
    'putJob': put_job,
    'getJob': get_job,
  }
})($);
