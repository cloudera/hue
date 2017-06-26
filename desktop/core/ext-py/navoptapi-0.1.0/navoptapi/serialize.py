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

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict  # Python 2.6
import json


class Serializer(object):
    DEFAULT_ENCODING = 'utf-8'

    def serialize_to_request(self, parameters, operation_model):
        # Don't serialize any parameter with a None value.
        filtered_parameters = OrderedDict(
            (k, v) for k, v in parameters.items() if v is not None)

        serialized = {}
        serialized_body = OrderedDict()
        if len(filtered_parameters) != 0:
            self._serialize(serialized_body, filtered_parameters, None)

        serialized['body'] = json.dumps(serialized_body).encode(self.DEFAULT_ENCODING)

        return serialized

    def _serialize(self, serialized, value, shape, key=None):
        self._default_serialize(serialized, value, shape, key)

    def _serialize_type_object(self, serialized, value, shape, key):
        if key is not None:
            # If a key is provided, this is a result of a recursive call, so we
            # need to add a new child dict as the value of the passed in dict.
            # Below we will add all the structure members to the new serialized
            # dictionary we just created.
            serialized[key] = OrderedDict()
            serialized = serialized[key]

        for member_key, member_value in value.items():
            member_shape = shape.members[member_key]
            self._serialize(serialized, member_value, member_shape, member_key)

    def _serialize_type_array(self, serialized, value, shape, key):
        array_obj = []
        serialized[key] = array_obj
        for array_item in value:
            wrapper = {}
            # JSON list serialization is the only case where we aren't setting
            # a key on a dict.  We handle this by using a __current__ key on a
            # wrapper dict to serialize each list item before appending it to
            # the serialized list.
            self._serialize(wrapper, array_item, shape.member, "__current__")
            array_obj.append(wrapper["__current__"])

    def _default_serialize(self, serialized, value, shape, key):
        if key:
            serialized[key] = value
        else:
            for member_key, member_value in value.items():
                serialized[member_key] = member_value
