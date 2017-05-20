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

import os
import re

from ._version import get_versions


__version__ = get_versions()['version']
del get_versions

VERSION = __version__

ALTUSCLI_ROOT = os.path.dirname(os.path.abspath(__file__))


# Used to specify anonymous (unsigned) request signature
UNSIGNED = object()


SCALAR_TYPES = set(['string',
                    'float',
                    'integer',
                    'long',
                    'boolean',
                    'double',
                    'blob',
                    'datetime'])

LIST_TYPE = 'array'
OBJECT_TYPE = 'object'
REF_KEY = '$ref'
REF_NAME_PREFIX = '#/definitions/'

COMPLEX_TYPES = set([OBJECT_TYPE,
                     LIST_TYPE])

DEFAULT_PROFILE_NAME = 'default'
ALTUS_ACCESS_KEY_ID_KEY_NAME = 'altus_access_key_id'
ALTUS_PRIVATE_KEY_KEY_NAME = 'altus_private_key'
# Python argparse has a bug in which '-' are not parsed correctly if they appear
# as values for other arguments, see: http://bugs.python.org/issue9334 for more
# details. This defines special encoding for dash that we will "decode" and
# replace with a dash. The reason we are using \\ is that there is a non zero
# chance that customers can discover this themselves.
ARGPARSE_DASH_ENCODING = '\\-'

# Prepopulate the cache with special cases that don't match our regular
# transformation.
_xform_cache = {
    ('s3GuardConfiguration', '-'): 's3-guard-configuration',
}
_first_cap_regex = re.compile('(.)([A-Z][a-z]+)')
_number_cap_regex = re.compile('([a-z])([0-9]+)')
_end_cap_regex = re.compile('([a-z0-9])([A-Z])')
# The regex below handles the special case where some acryonym
# name is pluralized, e.g GatewayARNs, ListWebACLs, SomeCNAMEs.
_special_case_transform = re.compile('[A-Z]{3,}s$')


def xform_name(name, sep='_', _xform_cache=_xform_cache):
    if sep in name:
        # If the sep is in the name, assume that it's already
        # transformed and return the string unchanged.
        return name
    key = (name, sep)
    if key not in _xform_cache:
        if _special_case_transform.search(name) is not None:
            is_special = _special_case_transform.search(name)
            matched = is_special.group()
            # Replace something like CRNs, ACLs with _crns, _acls.
            name = name[:-len(matched)] + sep + matched.lower()
        s1 = _first_cap_regex.sub(r'\1' + sep + r'\2', name)
        s2 = _number_cap_regex.sub(r'\1' + sep + r'\2', s1)
        transformed = _end_cap_regex.sub(r'\1' + sep + r'\2', s2).lower()
        _xform_cache[key] = transformed
    return _xform_cache[key]
