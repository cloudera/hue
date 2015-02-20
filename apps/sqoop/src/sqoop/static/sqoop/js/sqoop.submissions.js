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


var submissions = (function($) {
  var submission_registry = {};

  var SubmissionModel = koify.Model.extend({
    'job': -1,
    'progress': 0.0,
    'status': 'NEVER_EXECUTED',
    'creation_date': 0,
    'last_update_date': 0,
    'external_id': null,
    'external_link': null,
    'initialize': function(attrs) {
      var self = this;
      var _attrs = $.extend(true, {}, attrs || {});
      _attrs = transform_keys(_attrs, {
        'creation-date': 'creation_date',
        'last-update-date': 'last_update_date',
        'external-id': 'external_id',
        'external-link': 'external_link'
      });
      return _attrs;
    }
  });


  var Submission = koify.Node.extend({
    'identifier': 'submission',
    'persists': false,
    'model_class': SubmissionModel,
    'base_url': '/sqoop/api/submissions/',
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
        if (self.last_update_date()) {
          return moment(self.last_update_date()).format('MM/DD/YYYY hh:mm A');
        } else {
          return 0;
        }
      });
      self.progressFormatted = ko.computed(function() {
        return (self.progress() * 2 * 100) + "%";
      });
      self.selected = ko.observable();
    }
  });

  function fetch_submissions(options) {
    $(document).trigger('load.submissions', [options]);
    var request = $.extend({
      url: '/sqoop/api/submissions/',
      dataType: 'json',
      type: 'GET',
      success: fetcher_success('submissions', Submission, options),
      error: fetcher_error('submissions', Submission, options)
    }, options || {});
    $.ajax(request);
  }

  function put_submission(submission) {
    if (submission_registry[submission.job()]) {
      if (submission_registry[submission.job()].creation_date() < submission.creation_date() ||
          (submission_registry[submission.job()].creation_date() == submission.creation_date() && submission_registry[submission.job()].last_update_date() < submission.last_update_date())) {
        submission_registry[submission.job()] = submission;
      }
    } else {
      submission_registry[submission.job()] = submission;
    }
  }

  function get_submission(job_id) {
    return submission_registry[job_id];
  }

  function set_default_submission(job_id) {
    var submission = get_submission(job_id);
    if (!submission) {
      put_submission(new Submission({modelDict: {job: job_id}}));
    }
    return get_submission(job_id);
  }

  $(document).on('loaded.submissions', function(e, nodes, options) {
    $.each(nodes, function(index, submission) {
      put_submission(submission);
    });
  });

  return {
    'SubmissionModel': SubmissionModel,
    'Submission': Submission,
    'fetchSubmissions': fetch_submissions,
    'putSubmission': put_submission,
    'getSubmission': get_submission,
    'setDefaultSubmission': set_default_submission
  }
})($);
