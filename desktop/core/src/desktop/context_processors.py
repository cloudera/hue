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

import re


def app_name(request):
  """
  Add the name of the app to the template context.
  """
  context = {}

  name = get_app_name(request)

  if name is not None:
    context.update({'app_name': name})

  return context


NAME = re.compile('/([^/]+)')

def get_app_name(request):
  # No other cleaner way found
  match = NAME.search(request.path)

  if match is not None:
    return match.group(1)


def nonce(request):
    """ Pass the nonce cases to their respective template calls.

    Args:
        request (:obj:) Django request object

    Returns:
        dict:
            script_nonce (str): Cryptographic nonce for use in <script> tags or empty string.
            style_nonce (str): Cryptographic nonce for use in <style> tags or empty string.

    """
    script = getattr(request, 'script_nonce', False)
    style = getattr(request, 'style_nonce', False)

    # Only include nonce in the dictionary if a value is set
    nonce_dict = {}
    if script:
        nonce_dict['script_nonce'] = 'nonce={}'.format(script)
    else:
        nonce_dict['script_nonce'] = ''
    
    if style:
        nonce_dict['style_nonce'] = 'nonce={}'.format(style)
    else:
        nonce_dict['style_nonce'] = ''

    return nonce_dict