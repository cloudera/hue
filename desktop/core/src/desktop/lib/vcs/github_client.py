#!/usr/bin/env python
# -- coding: utf-8 --
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
import json
import logging
import re
import urllib

from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest import resource

from desktop.conf import VCS
from desktop.lib.vcs.apis.base_api import GITHUB_OFFICIAL


LOG = logging.getLogger(__name__)


class GithubClientException(Exception):
  pass


class GithubClient(object):
  """
  https://developer.github.com/v3/
  """

  OWNER_RE = "(?P<owner>[A-Za-z0-9](?:-?[A-Za-z0-9]){0,38})"
  REPO_RE = "(?P<repo>[\w\.@\:\-~]+)"
  BRANCH_RE = "(?P<branch>[\w\.@\:\-~]+)"
  FILEPATH_RE = "(?P<filepath>.+)"

  DEFAULT_SCOPES = ['repo', 'user']


  def __init__(self, **options):
    self._github_base_url = options.get('remote_url', VCS[GITHUB_OFFICIAL].REMOTE_URL.get()).strip('/')
    self._api_url = options.get('api_url', VCS[GITHUB_OFFICIAL].API_URL.get()).strip('/')

    self._client = HttpClient(self._api_url, logger=LOG)
    self._root = resource.Resource(self._client)

    self.__headers = {}
    access_token = options.get('access_token')
    if access_token:
      self.__headers['Authorization'] = 'token %s' % access_token
      # TODO: Redact access_token from logs
    self.__params = ()


  @classmethod
  def get_authorization_url(cls, **options):
    """
    https://developer.github.com/guides/basics-of-authentication/
    """
    remote_url = options.get('remote_url', VCS[GITHUB_OFFICIAL].REMOTE_URL.get()).strip('/')
    client_id = options.get('client_id', VCS[GITHUB_OFFICIAL].CLIENT_ID.get())
    scopes_list = options.get('scopes_list', cls.DEFAULT_SCOPES)
    scopes = ','.join(scopes_list)
    return '%s/login/oauth/authorize?scope=%s&client_id=%s' % (remote_url, scopes, client_id)


  @classmethod
  def get_access_token(cls, session_code, **options):
    remote_url = options.get('remote_url', VCS[GITHUB_OFFICIAL].REMOTE_URL.get()).strip('/')
    client_id = options.get('client_id', VCS[GITHUB_OFFICIAL].CLIENT_ID.get())
    client_secret = options.get('client_secret', VCS[GITHUB_OFFICIAL].CLIENT_SECRET.get())

    try:
      client = HttpClient(remote_url, logger=LOG)
      root = resource.Resource(client)
      data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': session_code
      }
      headers = {
        'content-type':'application/json',
        'Accept': 'application/json'
      }
      response = root.post('login/oauth/access_token', headers=headers, data=json.dumps(data))
      result = cls._get_json(response)
      return result['access_token']
    except RestException, e:
      raise GithubClientException('Failed to request access token from GitHub: %s' % e)
    except KeyError:
      raise GithubClientException('Failed to find access_token in GitHub oAuth response')


  @classmethod
  def is_authenticated(cls, access_token, **options):
    api_url = options.get('api_url', VCS[GITHUB_OFFICIAL].API_URL.get()).strip('/')

    try:
      client = HttpClient(api_url, logger=LOG)
      root = resource.Resource(client)
      params = (
        ('access_token', access_token),
      )
      root.get('user', params=params)
      return True
    except RestException:
      return False


  @classmethod
  def _get_json(cls, response):
    if type(response) != dict:
      try:
        response = json.loads(response)
      except ValueError:
        raise GithubClientException('GitHub API did not return JSON response')
    return response


  @property
  def github_url_regex(self):
    return re.compile('%s/%s/%s/blob/%s/%s' % (self._github_base_url, self.OWNER_RE, self.REPO_RE, self.BRANCH_RE, self.FILEPATH_RE))


  def _clean_path(self, filepath):
    cleaned_path = filepath.strip('/')
    cleaned_path = urllib.unquote(cleaned_path)
    return cleaned_path


  def parse_github_url(self, url):
    """
    Given a base URL to a Github repository, return a tuple of the owner, repo, branch, and filepath
    :param url: base URL to repo (e.g. - https://github.com/cloudera/hue/blob/master/README.rst)
    :return: tuple of strings (e.g. - ('cloudera', 'hue', 'master', 'README.rst'))
    """
    match = self.github_url_regex.search(url)
    if match:
      return match.group('owner'), match.group('repo'), match.group('branch'), match.group('filepath')
    else:
      raise ValueError('GitHub URL is not formatted correctly: %s' % url)


  def get_file_contents(self, owner, repo, filepath, branch='master'):
    filepath = self._clean_path(filepath)
    try:
      sha = self.get_sha(owner, repo, filepath, branch)
      blob = self.get_blob(owner, repo, sha)
      content = blob['content'].decode('base64')
      return content
    except binascii.Error, e:
      raise GithubClientException('Failed to decode file contents, check if file content is properly base64-encoded: %s' % e)
    except KeyError, e:
      raise GithubClientException('Failed to find expected content object in blob object: %s' % e)


  def get_sha(self, owner, repo, filepath, branch='master'):
    """
    Return the sha for a given filepath by recursively calling Trees API for each level of the path
    """
    filepath = self._clean_path(filepath)
    sha = branch
    path_tokens = filepath.split('/')

    for token in path_tokens:
      tree = self.get_tree(owner, repo, sha, recursive=False)
      for elem in tree['tree']:
        if elem['path'] == token:
          sha = elem['sha']
          break
      else:
        raise GithubClientException('Could not find sha for: %s/%s/%s/%s' % (owner, repo, branch, filepath))

    return sha


  def get_tree(self, owner, repo, sha='master', recursive=True):
    """
    GET /repos/:owner/:repo/git/trees/:sha
    https://developer.github.com/v3/git/trees/#get-a-tree
    """
    try:
      params = self.__params
      if recursive:
        params += (
            ('recursive', 1),
        )
      response = self._root.get('repos/%s/%s/git/trees/%s' % (owner, repo, sha), headers=self.__headers, params=self.__params)
      return self._get_json(response)
    except RestException, e:
      raise GithubClientException('Could not find GitHub object, check owner, repo and filepath or permissions: %s' % e)


  def get_blob(self, owner, repo, sha):
    """
    GET /repos/:owner/:repo/git/blobs/:sha
    https://developer.github.com/v3/git/blobs/#get-a-blob
    """
    try:
      response = self._root.get('repos/%s/%s/git/blobs/%s' % (owner, repo, sha), headers=self.__headers, params=self.__params)
      return self._get_json(response)
    except RestException, e:
      raise GithubClientException('Could not find GitHub object, check owner, repo and sha or permissions: %s' % e)
