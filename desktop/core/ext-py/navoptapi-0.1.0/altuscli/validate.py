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

import datetime
import decimal

from altuscli.compat import six
from altuscli.exceptions import ParamValidationError
from altuscli.utils import parse_to_aware_datetime


def validate_parameters(params, shape):
    """Validates input parameters against a schema.

    This is a convenience function that validates parameters against a schema.
    You can also instantiate and use the ParamValidator class directly if you
    want more control.

    If there are any validation errors then a ParamValidationError
    will be raised.  If there are no validation errors than no exception
    is raised and a value of None is returned.
    """
    validator = ParamValidator()
    report = validator.validate(params, shape)
    if report.has_errors():
        raise ParamValidationError(report=report.generate_report())


def type_check(valid_types):
    def _create_type_check_guard(func):
        def _on_passes_type_check(self, param, shape, errors, name):
            if _type_check(param, errors, name):
                return func(self, param, shape, errors, name)

        def _type_check(param, errors, name):
            if not isinstance(param, valid_types):
                valid_type_names = [six.text_type(t) for t in valid_types]
                errors.report(name, 'invalid type', param=param,
                              valid_types=valid_type_names)
                return False
            return True

        return _on_passes_type_check
    return _create_type_check_guard


def range_check(name, value, shape, error_type, errors):
    failed = False
    min_allowed = float('-inf')
    max_allowed = float('inf')
    if shape.minimum is not None:
        min_allowed = shape.minimum
        if value < min_allowed:
            failed = True
    if shape.maximum is not None:
        max_allowed = shape.maximum
        if value > max_allowed:
            failed = True
    if failed:
        errors.report(name, error_type, param=value,
                      valid_range=[min_allowed, max_allowed])


def length_check(name, value, shape, error_type, errors):
    failed = False
    min_allowed = float('-inf')
    max_allowed = float('inf')
    if shape.min_length is not None:
        min_allowed = shape.min_length
        if value < min_allowed:
            failed = True
    if shape.max_length is not None:
        max_allowed = shape.max_length
        if value > max_allowed:
            failed = True
    if failed:
        errors.report(name, error_type, param=value,
                      valid_range=[min_allowed, max_allowed])


class ValidationErrors(object):
    def __init__(self):
        self._errors = []

    def has_errors(self):
        if self._errors:
            return True
        return False

    def generate_report(self):
        error_messages = []
        for error in self._errors:
            error_messages.append(self._format_error(error))
        return '\n'.join(error_messages)

    def _format_error(self, error):
        error_type, name, additional = error
        name = self._get_name(name)
        if error_type == 'missing required field':
            return 'Missing required parameter in %s: "%s"' % (
                name, additional['required_name'])
        elif error_type == 'unknown field':
            return 'Unknown parameter in %s: "%s", must be one of: %s' % (
                name, additional['unknown_param'], ', '.join(additional['valid_names']))
        elif error_type == 'invalid type':
            return 'Invalid type for parameter %s, value: %s, type: %s, valid types: %s' \
                % (name, additional['param'],
                   str(type(additional['param'])),
                   ', '.join(additional['valid_types']))
        elif error_type == 'invalid enum':
            return ('Invalid value for parameter %s, value: %s, type: %s, valid '
                    'values: %s') \
                % (name, additional['param'],
                   str(type(additional['param'])),
                   ', '.join(additional['valid_values']))
        elif error_type == 'invalid range':
            min_allowed = additional['valid_range'][0]
            max_allowed = additional['valid_range'][1]
            return ('Invalid range for parameter %s, value: %s, valid range: '
                    '%s-%s' % (name, additional['param'],
                               min_allowed, max_allowed))
        elif error_type == 'invalid length':
            min_allowed = additional['valid_range'][0]
            max_allowed = additional['valid_range'][1]
            return ('Invalid length for parameter %s, value: %s, valid range: '
                    '%s-%s' % (name, additional['param'],
                               min_allowed, max_allowed))

    def _get_name(self, name):
        if not name:
            return 'input'
        elif name.startswith('.'):
            return name[1:]
        else:
            return name

    def report(self, name, reason, **kwargs):
        self._errors.append((reason, name, kwargs))


class ParamValidator(object):

    def validate(self, params, shape):
        errors = ValidationErrors()
        self._validate(params, shape, errors, name='')
        return errors

    def _validate(self, params, shape, errors, name):
        getattr(self, '_validate_%s' % shape.type_name)(params, shape, errors, name)

    @type_check(valid_types=(dict,))
    def _validate_object(self, params, shape, errors, name):
        # Validate required fields.
        for required_member in shape.required_members:
            if required_member not in params:
                errors.report(name, 'missing required field',
                              required_name=required_member, user_params=params)
        members = shape.members
        known_params = []
        # Validate known params.
        for param in params:
            if param not in members:
                errors.report(name, 'unknown field', unknown_param=param,
                              valid_names=list(members))
            else:
                known_params.append(param)
        # Validate structure members.
        for param in known_params:
            self._validate(params[param], shape.members[param],
                           errors, '%s.%s' % (name, param))

    @type_check(valid_types=(bool,))
    def _validate_boolean(self, param, shape, errors, name):
        pass

    @type_check(valid_types=six.integer_types)
    def _validate_integer(self, param, shape, errors, name):
        range_check(name, param, shape, 'invalid range', errors)

    @type_check(valid_types=(float, decimal.Decimal) + six.integer_types)
    def _validate_number(self, param, shape, errors, name):
        range_check(name, param, shape, 'invalid range', errors)

    @type_check(valid_types=six.string_types)
    def _validate_string(self, param, shape, errors, name):
        if len(shape.enum) > 0 and param not in shape.enum:
            errors.report(name, 'invalid enum', param=param,
                          valid_values=shape.enum)
        length_check(name, len(param), shape, 'invalid length', errors)

    @type_check(valid_types=(list, tuple))
    def _validate_array(self, param, shape, errors, name):
        member_shape = shape.member
        length_check(name, len(param), shape, 'invalid length', errors)
        for i, item in enumerate(param):
            self._validate(item, member_shape, errors, '%s[%s]' % (name, i))

    def _validate_datetime(self, param, shape, errors, name):
        # We don't use @type_check because datetimes are a bit more flexible.
        # You can either provide a datetime object, or a string that parses
        # to a datetime.
        is_valid_type = self._type_check_datetime(param)
        if not is_valid_type:
            valid_type_names = [six.text_type(datetime), 'timestamp-string']
            errors.report(name, 'invalid type', param=param,
                          valid_types=valid_type_names)

    def _type_check_datetime(self, value):
        try:
            parse_to_aware_datetime(value)
            return True
        except (TypeError, ValueError, AttributeError):
            # Yes, dateutil can sometimes raise an AttributeError when parsing
            # timestamps.
            return False


class ParamValidationDecorator(object):
    def __init__(self, param_validator, serializer):
        self._param_validator = param_validator
        self._serializer = serializer

    def serialize_to_request(self, parameters, operation_model):
        input_shape = operation_model.input_shape
        if input_shape is not None:
            report = self._param_validator.validate(parameters,
                                                    operation_model.input_shape)
            if report.has_errors():
                raise ParamValidationError(report=report.generate_report())
        return self._serializer.serialize_to_request(parameters, operation_model)
