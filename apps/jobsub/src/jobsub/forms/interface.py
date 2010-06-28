#!/usr/bin/env python
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
"""
Interface and registry for jobsub "forms".
"""
import logging

LOG = logging.getLogger(__name__)

class UnimplementedException(Exception):
  pass

registry = {}

class JobSubForm(object):
  """
  JobSubForms should inherit from this class so that
  they can be registered.  This follows the pattern from
  http://effbot.org/zone/metaclass-plugins.htm
  """
  class __metaclass__(type):
    def __init__(cls, clsname, bases, dict):
      global registry
      type.__init__(cls, clsname, bases, dict)
      if clsname == "JobSubForm":
        return
      name = dict["name"]
      if name in registry:
        raise Exception("Multiply defined form type %s: %s." % (clsname, name))
      LOG.info("Registered jobsub plugin: %s->%s" % (name, clsname))
      registry[name] = cls

class JobSubFormInterface(object):
  """
  A JobSubForm allows developers to create UIs for their
  Hadoop applications.  It is responsible for
  rendering an HTML form, and preparing a submission
  to the jobsubd daemon.

  The general flow for editing and saving is:

  1) Present the form
     (new) __init__() -> render_edit()
     (edit) __init__(string_repr=...) -> render_edit()
  2) Handle the POST
     __init__() -> is_valid_edit(post_data) -> serialize_to_string()
                                          \_-> render_edit()
  
  And the flow for submission is

  1) Present the parameterization
     __init__(string_repr) -> render_parameterization()
  2) Handle the POST
     __init__(string_repr) -> is_valid_parameterization(post_data) -> submit()
                                                                 \_-> render_parameterization()

  Note that both flows may be implemented by mixing in with
  DjangoFormBasedEditForm and BasicParameterizationForm,
  in which case all you need to implement is render() and 
  to_job_submission_plan().
  """
  def render(self):
    """
    Renders an HTML snippet corresponding to the form.
    This does not include the <form> tag, nor the submit
    buttons.
    """
    raise UnimplementedException()

  def post(data):
    """
    Updates its state according to form data.

    Returns True if the form is valid, False otherwise.
    """
    raise UnimplementedException()

  def serialize_to_string(self):
    """
    Saves its internal state to a string.
    """
    raise UnimplementedException()

  def deserialize_from_string(self):
    """
    Restores its internal state from a string.
    """
    raise UnimplementedException()

  def parameterization_form(self):
    """
    Returns an HTML snippet corresponding to
    the parameterization necessary for job submission.
    """
    raise UnimplementedException()

  def to_job_submission_steps(self, job_design_name):
    """
    Creates a JobSubmission from itself.

    Data is the post data from parameterization_form.
    """
    raise UnimplementedException()
