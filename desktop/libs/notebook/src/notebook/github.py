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


LOG = logging.getLogger(__name__)


class GithubClientException(Exception):
  pass


class GithubClient(object):
  """
  https://developer.github.com/v3/
  """

  BASE_URL = 'https://api.github.com'

  REPO_URL_RE = re.compile("http[s]?://(www.)?github.com/([a-z0-9](?:-?[a-z0-9]){0,38}).([\w\.@\:\-~]+)/blob/([\w\.@\:\-~_]+)/(.+)?")


  def __init__(self, **options):
    # TODO: Add support for access token and authenticated API access
    self._client = HttpClient(self.BASE_URL, logger=LOG)
    self._root = resource.Resource(self._client)


  @classmethod
  def parse_github_url(cls, url):
    """
    Given a base URL to a Github repository, return a tuple of the owner, repo, branch, and filepath
    :param url: base URL to repo (e.g. - https://github.com/cloudera/hue/blob/master/README.rst)
    :return: tuple of strings (e.g. - ('cloudera', 'hue', 'master', 'README.rst'))
    """
    match = cls.REPO_URL_RE.search(url)
    if match:
      return match.group(2), match.group(3), match.group(4), match.group(5)
    else:
      raise ValueError('Github URL is not formatted correctly: %s' % url)


  def _get_headers(self):
    return {}


  def _get_params(self):
    return ()


  def _get_json(self, response):
    if type(response) != dict:
      # Got 'plain/text' mimetype instead of 'application/json'
      try:
        response = json.loads(response)
      except ValueError, e:
        # Got some null bytes in the response
        LOG.error('%s: %s' % (unicode(e), repr(response)))
        response = json.loads(response.replace('\x00', ''))
    return response


  def _clean_path(self, filepath):
    cleaned_path = filepath.strip('/')
    cleaned_path = urllib.unquote(cleaned_path)
    return cleaned_path


  def get_file_contents(self, owner, repo, filepath, branch='master'):
    filepath = self._clean_path(filepath)
    try:
      sha = self.get_sha(owner, repo, filepath, branch)
      blob = self.get_blob(owner, repo, sha)
      content = blob['content'].decode('base64')
      return content
    except binascii.Error:
      raise GithubClientException('Failed to decode file contents, check if file content is properly base64-encoded.')
    except GithubClientException, e:
      raise e
    except Exception, e:
      raise GithubClientException('Failed to get file contents: %s' % str(e))


  def get_sha(self, owner, repo, filepath, branch='master'):
    filepath = self._clean_path(filepath)
    try:
      sha = branch
      path_tokens = filepath.split('/')
      for token in path_tokens:
        tree = self.get_tree(owner, repo, sha, recursive=False)
        sha = next(elem['sha'] for elem in tree['tree'] if elem['path'] == token)
      return sha
    except StopIteration, e:
      raise GithubClientException('Could not find sha for: %s/%s/%s/%s' % (owner, repo, branch, filepath))
    except RestException, e:
      raise e


  def get_tree(self, owner, repo, sha='master', recursive=True):
    """
    GET /repos/:owner/:repo/git/trees/:sha
    https://developer.github.com/v3/git/trees/#get-a-tree
    """
    try:
      params = self._get_params()
      if recursive:
        params += (
            ('recursive', 1),
        )
      response = self._root.get('repos/%s/%s/git/trees/%s' % (owner, repo, sha), headers=self._get_headers(), params=params)
      return self._get_json(response)
    except RestException, e:
      raise GithubClientException('Could not find Github object, check owner, repo and filepath or permissions: %s' % str(e))


  def get_blob(self, owner, repo, sha):
    """
    GET /repos/:owner/:repo/git/blobs/:sha
    https://developer.github.com/v3/git/blobs/#get-a-blob
    """
    try:
      response = self._root.get('repos/%s/%s/git/blobs/%s' % (owner, repo, sha), headers=self._get_headers(), params=self._get_params())
      return self._get_json(response)
    except RestException, e:
      raise GithubClientException('Could not find Github object, check owner, repo and sha or permissions: %s' % str(e))
