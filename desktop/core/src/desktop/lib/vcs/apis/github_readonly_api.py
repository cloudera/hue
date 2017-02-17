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


import binascii
import logging
import re
import urllib
import urlparse

from django.http import HttpResponseBadRequest
from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse
from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest import resource

from desktop.conf import VCS
from desktop.lib.vcs.apis.base_api import Api, GIT_READ_ONLY
from desktop.lib.vcs.github_client import GithubClientException

LOG = logging.getLogger(__name__)


class GithubReadOnlyApi(Api):
  """
  https://developer.github.com/v3/
  """

  OWNER_RE = "(?P<owner>[A-Za-z0-9](?:-?[A-Za-z0-9]){0,38})"
  REPO_RE = "(?P<repo>[\w\.@\:\-~]+)"
  BRANCH_RE = "(?P<branch>[\w\.@\:\-~]+)"

  DEFAULT_SCOPES = ['repo', 'user']

  def __init__(self):
    self._remote_url = VCS[GIT_READ_ONLY].REMOTE_URL.get().strip('/')
    self._api_url = VCS[GIT_READ_ONLY].API_URL.get().strip('/')

    self._client = HttpClient(self._api_url, logger=LOG)
    self._root = resource.Resource(self._client)

  def contents(self, request):
    """
    GET /repos/:owner/:repo/contents/:path
    https://developer.github.com/v3/repos/contents/#get-contents
    """
    response = {'status': -1}
    response['fileType'] = filetype = request.GET.get('fileType', 'dir')
    filepath = request.GET.get('path', '/')
    filepath = self._clean_path(filepath)

    if self._remote_url:
      owner, repo, branch = self.parse_github_url(self._remote_url)
      blob = self._get_contents(owner, repo, filepath)
      if filetype == 'dir':
        response['files'] = _massage_content(blob)
        response['status'] = 0
      elif filetype == 'file':
        try:
          response['content'] = blob['content'].decode('base64')
          response['status'] = 0
        except binascii.Error, e:
          raise GithubClientException('Failed to decode file contents, check if file content is properly base64-encoded: %s' % e)
        except KeyError, e:
          raise GithubClientException('Failed to find expected content object in blob object: %s' % e)
    else:
      return HttpResponseBadRequest(_('url param is required'))
    return JsonResponse(response)

  def authorize(self, request):
    pass

  def parse_github_url(self, url):
    """
    Given a base URL to a Github repository, return a tuple of the owner, repo, branch
    :param url: base URL to repo (e.g. - https://github.com/cloudera/hue/tree/master)
    :return: tuple of strings (e.g. - ('cloudera', 'hue', 'master'))
    """
    match = self.github_url_regex.search(url)
    if match:
      return match.group('owner'), match.group('repo'), match.group('branch')
    else:
      raise ValueError('GitHub URL is not formatted correctly: %s' % url)

  @property
  def github_url_regex(self):
    return re.compile('%s/%s/%s/tree/%s' % (self._get_base_url(), self.OWNER_RE, self.REPO_RE, self.BRANCH_RE))

  def _get_base_url(self):
    split_url = urlparse.urlsplit(self._remote_url)
    return urlparse.urlunsplit((split_url.scheme, split_url.netloc, '', "", ""))

  def _clean_path(self, filepath):
    cleaned_path = filepath.strip('/')
    cleaned_path = urllib.unquote(cleaned_path)
    return cleaned_path

  def _get_contents(self, owner, repo, path):
    try:
      return self._root.get('repos/%s/%s/contents/%s' % (owner, repo, path))
    except RestException, e:
      raise GithubClientException('Could not find GitHub object, check owner, repo or path: %s' % e)


def _massage_content(blob):
  response = []
  for file in blob:
    file['stats'] = {
      'size': file.get('size', 0),
      'path': file.get('path', '')
    }
    response.append(file)
  return response