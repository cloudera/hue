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

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_GET

from desktop.lib.django_util import JsonResponse

from desktop.lib.vcs.github_client import GithubClient
from desktop.lib.vcs.apis.base_api import Api


class GithubApi(Api):

  def __init__(self):
    self.request = None

  @require_GET
  def contents(self, request):
    response = {'status': -1}

    api = GithubClient(access_token=request.session.get('github_access_token'))

    response['url'] = url = request.GET.get('url')

    if url:
      owner, repo, branch, filepath = api.parse_github_url(url)
      content = api.get_file_contents(owner, repo, filepath, branch)
      try:
        response['content'] = json.loads(content)
      except ValueError:
        # Content is not JSON-encoded so return plain-text
        response['content'] = content
      response['status'] = 0
    else:
      return HttpResponseBadRequest(_('url param is required'))

    return JsonResponse(response)

  def authorize(self, request):
    access_token = request.session.get('github_access_token')
    if access_token and GithubClient.is_authenticated(access_token):
      response = {
        'status': 0,
        'message': _('User is already authenticated to GitHub.')
      }
      return JsonResponse(response)
    else:
      auth_url = GithubClient.get_authorization_url()
      request.session['github_callback_redirect'] = request.GET.get('currentURL')
      request.session['github_callback_fetch'] = request.GET.get('fetchURL')
      response = {
        'status': -1,
        'auth_url':auth_url
      }
      if (request.is_ajax()):
        return JsonResponse(response)

      return HttpResponseRedirect(auth_url)

  def callback(self, request):
    redirect_base = request.session['github_callback_redirect'] + "&github_status="
    if 'code' in request.GET:
      session_code = request.GET.get('code')
      request.session['github_access_token'] = GithubClient.get_access_token(session_code)
      return HttpResponseRedirect(redirect_base + "0&github_fetch=" + request.session['github_callback_fetch'])
    else:
      return HttpResponseRedirect(redirect_base + "-1&github_fetch=" + request.session['github_callback_fetch'])