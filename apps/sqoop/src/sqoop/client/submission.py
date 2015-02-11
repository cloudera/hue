# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from desktop.lib.python_util import force_dict_to_strings

from exception import SqoopException
from config import Config


class Submission(object):
  """
  Sqoop submission object.

  Example of sqoop submission dictionary received by server: {
    "progress": 0.0,
    "last-update-date": 1371775331096,
    "external-id": "job_201306201740_0001",
    "status": "RUNNING",
    "job": 1,
    "creation-date": 1371775311721,
    "external-link": "http://solaris:50030/jobdetails.jsp?jobid=job_201306201740_0001"
  }
  """
  def __init__(self, job_id, status, progress, created, updated, enabled=True, **kwargs):
    self.job_id = job_id
    self.status = status
    self.progress = progress
    self.created = created
    self.updated = updated
    self.external_id = kwargs.get('external_id', None)
    self.external_link = kwargs.get('external_link', None)
    self.enabled = enabled

  @staticmethod
  def from_dict(submission_dict):
    submission_dict['job_id'] = submission_dict['job']
    submission_dict['created'] = submission_dict['creation-date']
    submission_dict['updated'] = submission_dict['last-update-date']
    submission_dict['external_id'] = submission_dict.get('external-id', None)
    submission_dict['external_link'] = submission_dict.get('external-link', None)
    return Submission(**force_dict_to_strings(submission_dict))

  def to_dict(self):
    d = {
      'job': self.job_id,
      'status': self.status,
      'progress': self.progress,
      'creation-date': self.created,
      'last-update-date': self.updated,
      'enabled': self.enabled
    }

    if self.external_id:
      d['external-id'] = self.external_id

    if self.external_id:
      d['external-link'] = self.external_link

    return d


class SqoopSubmissionException(Exception):

  def __init__(self, job_id, status, progress, created, updated, **kwargs):
    self.job_id = job_id
    self.status = status
    self.progress = progress
    self.created = created
    self.updated = updated
    self.exception = kwargs.get('exception', None)
    self.exception_trace = kwargs.get('exception_trace', None)

  @staticmethod
  def from_dict(submission_dict):
    submission_dict['job_id'] = submission_dict['job']
    submission_dict['created'] = submission_dict['creation-date']
    submission_dict['updated'] = submission_dict['last-update-date']
    submission_dict['exception'] = submission_dict.get('exception', None)
    submission_dict['exception_trace'] = submission_dict.get('exception-trace', None)
    submission = SqoopSubmissionException(**force_dict_to_strings(submission_dict))
    return submission

  def to_dict(self):
    d = {
      'job': self.job_id,
      'status': self.status,
      'progress': self.progress,
      'creation-date': self.created,
      'last-update-date': self.updated
    }

    if self.exception:
      d['exception'] = self.exception

    if self.exception_trace:
      d['exception-trace'] = self.exception_trace

    return d