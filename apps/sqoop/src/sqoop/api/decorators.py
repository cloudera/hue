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

import json
import logging

from django.utils.translation import ugettext as _
from django.utils.functional import wraps

from desktop.lib.django_util import render
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.rest.http_client import RestException
from exception import handle_rest_exception
from sqoop import client, conf


__all__ = ['get_job_or_exception']

LOG = logging.getLogger(__name__)


def get_connector_or_exception(exception_class=PopupException):
  def inner(view_func):
    def decorate(request, connector_id, *args, **kwargs):
      try:
        c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE, ssl_cert_ca_verify=conf.SSL_CERT_CA_VERIFY.get())
        connector = c.get_connector(int(connector_id))
      except RestException, e:
        handle_rest_exception(e, _('Could not get connector.'))
      return view_func(request, connector=connector, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner


def get_link_or_exception(exception_class=PopupException):
  def inner(view_func):
    def decorate(request, link_id, *args, **kwargs):
      try:
        c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE, ssl_cert_ca_verify=conf.SSL_CERT_CA_VERIFY.get())
        link = c.get_link(int(link_id))
      except RestException, e:
        handle_rest_exception(e, _('Could not get link.'))
      return view_func(request, link=link, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner


def get_job_or_exception(exception_class=PopupException):
  def inner(view_func):
    def decorate(request, job_id, *args, **kwargs):
      try:
        c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE, ssl_cert_ca_verify=conf.SSL_CERT_CA_VERIFY.get())
        job = c.get_job(int(job_id))
      except RestException, e:
        handle_rest_exception(e, _('Could not get job.'))
      return view_func(request, job=job, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner


def get_submission_or_exception(exception_class=PopupException):
  def inner(view_func):
    def decorate(request, submission_id, *args, **kwargs):
      try:
        c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE, ssl_cert_ca_verify=conf.SSL_CERT_CA_VERIFY.get())
        submission = c.get_submission(int(submission_id))
      except RestException, e:
        handle_rest_exception(e, _('Could not get submission.'))
      return view_func(request, submission=submission, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner
