# Copyright 2012-2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Modifications made by Cloudera are:
#     Copyright (c) 2016 Cloudera, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from collections import namedtuple

import six

ReadOnlyCredentials = namedtuple('ReadOnlyCredentials',
                                 ['access_key_id', 'private_key', 'method'])


class Credentials(object):
    """
    Holds the credentials needed to authenticate requests.
    """

    def __init__(self, access_key_id, private_key, method):
        self.access_key_id = access_key_id
        self.private_key = private_key
        self.method = method
        self._normalize()

    def ensure_unicode(self, s, encoding='utf-8', errors='strict'):
        if isinstance(s, six.text_type):
            return s
        return unicode(s, encoding, errors)

    def _normalize(self):
        self.access_key_id = self.ensure_unicode(self.access_key_id)
        self.private_key = self.ensure_unicode(self.private_key)

    def get_frozen_credentials(self):
        return ReadOnlyCredentials(self.access_key_id,
                                   self.private_key,
                                   self.method)
