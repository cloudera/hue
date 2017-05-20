# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Modifications made by Cloudera are:
#     Copyright (c) 2016 Cloudera, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from altuscli import UNSIGNED
import altuscli.auth
from altuscli.exceptions import UnknownSignatureVersionError


class RequestSigner(object):
    """
    An object to sign requests before they go out over the wire using
    one of the authentication mechanisms defined in ``auth.py``.
    """
    def __init__(self, signature_version, credentials):
        self._signature_version = signature_version
        self._credentials = credentials

    @property
    def signature_version(self):
        return self._signature_version

    def sign(self, request):
        """
        Sign a request before it goes out over the wire.
        """
        if self._signature_version != UNSIGNED:
            signer = self.get_auth_instance(self._signature_version)
            signer.add_auth(request)

    def get_auth_instance(self, signature_version, **kwargs):
        """
        Get an auth instance which can be used to sign a request
        using the given signature version.
        """
        cls = altuscli.auth.AUTH_TYPE_MAPS.get(signature_version)
        if cls is None:
            raise UnknownSignatureVersionError(
                signature_version=signature_version)
        # If there's no credentials provided (i.e credentials is None),
        # then we'll pass a value of "None" over to the auth classes,
        # which already handle the cases where no credentials have
        # been provided.
        frozen_credentials = self._credentials.get_frozen_credentials()
        kwargs['credentials'] = frozen_credentials
        auth = cls(**kwargs)
        return auth
