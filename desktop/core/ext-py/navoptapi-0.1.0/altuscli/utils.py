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

import contextlib
import datetime
import functools
import re
import signal

from altuscli import LIST_TYPE
from altuscli import OBJECT_TYPE
from altuscli.compat import OrderedDict
import dateutil.parser
from dateutil.tz import tzlocal
from dateutil.tz import tzutc

# These are chars that do not need to be urlencoded based on rfc2986, section 2.3.
SAFE_CHARS = '-._~'


def get_service_module_name(service_model):
    name = service_model.service_name
    name = name.replace('Cloudera', '')
    name = name.replace('Altus', '')
    name = re.sub('\W+', '', name)
    return name


def json_encoder(obj):
    """JSON encoder that formats datetimes as ISO8601 format."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        return obj


class CachedProperty(object):
    def __init__(self, fget):
        self._fget = fget

    def __get__(self, obj, cls):
        if obj is None:
            return self
        else:
            computed_value = self._fget(obj)
            obj.__dict__[self._fget.__name__] = computed_value
            return computed_value


def instance_cache(func):
    """Method decorator for caching method calls to a single instance.

    **This is not a general purpose caching decorator.**

    In order to use this, you *must* provide an ``_instance_cache``
    attribute on the instance.

    This decorator is used to cache method calls.  The cache is only
    scoped to a single instance though such that multiple instances
    will maintain their own cache.  In order to keep things simple,
    this decorator requires that you provide an ``_instance_cache``
    attribute on your instance.

    """
    func_name = func.__name__

    @functools.wraps(func)
    def _cache_guard(self, *args, **kwargs):
        cache_key = (func_name, args)
        if kwargs:
            kwarg_items = tuple(sorted(kwargs.items()))
            cache_key = (func_name, args, kwarg_items)
        result = self._instance_cache.get(cache_key)
        if result is not None:
            return result
        result = func(self, *args, **kwargs)
        self._instance_cache[cache_key] = result
        return result
    return _cache_guard


def parse_timestamp(value):
    """Parse a timestamp into a datetime object.

    Supported formats:

        * iso8601
        * rfc822
        * epoch (value is an integer)

    This will return a ``datetime.datetime`` object.

    """
    if isinstance(value, (int, float)):
        # Possibly an epoch time.
        return datetime.datetime.fromtimestamp(value, tzlocal())
    else:
        try:
            return datetime.datetime.fromtimestamp(float(value), tzlocal())
        except (TypeError, ValueError):
            pass
    try:
        return dateutil.parser.parse(value)
    except (TypeError, ValueError) as e:
        raise ValueError('Invalid timestamp "%s": %s' % (value, e))


def parse_to_aware_datetime(value):
    """Converted the passed in value to a datetime object with tzinfo.

    This function can be used to normalize all timestamp inputs.  This
    function accepts a number of different types of inputs, but
    will always return a datetime.datetime object with time zone
    information.

    The input param ``value`` can be one of several types:

        * A datetime object (both naive and aware)
        * An integer representing the epoch time (can also be a string
          of the integer, i.e '0', instead of 0).  The epoch time is
          considered to be UTC.
        * An iso8601 formatted timestamp.  This does not need to be
          a complete timestamp, it can contain just the date portion
          without the time component.

    The returned value will be a datetime object that will have tzinfo.
    If no timezone info was provided in the input value, then UTC is
    assumed, not local time.

    """
    # This is a general purpose method that handles several cases of
    # converting the provided value to a string timestamp suitable to be
    # serialized to an http request. It can handle:
    # 1) A datetime.datetime object.
    if isinstance(value, datetime.datetime):
        datetime_obj = value
    else:
        # 2) A string object that's formatted as a timestamp.
        #    We document this as being an iso8601 timestamp, although
        #    parse_timestamp is a bit more flexible.
        datetime_obj = parse_timestamp(value)
    if datetime_obj.tzinfo is None:
        # I think a case would be made that if no time zone is provided,
        # we should use the local time.  However, to restore backwards
        # compat, the previous behavior was to assume UTC, which is
        # what we're going to do here.
        datetime_obj = datetime_obj.replace(tzinfo=tzutc())
    else:
        datetime_obj = datetime_obj.astimezone(tzutc())
    return datetime_obj


@contextlib.contextmanager
def ignore_ctrl_c():
    original = signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, original)


def datetime2timestamp(dt, default_timezone=None):
    """Calculate the timestamp based on the given datetime instance.

    :type dt: datetime
    :param dt: A datetime object to be converted into timestamp
    :type default_timezone: tzinfo
    :param default_timezone: If it is provided as None, we treat it as tzutc().
                             But it is only used when dt is a naive datetime.
    :returns: The timestamp
    """
    epoch = datetime.datetime(1970, 1, 1)
    if dt.tzinfo is None:
        if default_timezone is None:
            default_timezone = tzutc()
        dt = dt.replace(tzinfo=default_timezone)
    d = dt.replace(tzinfo=None) - dt.utcoffset() - epoch
    if hasattr(d, "total_seconds"):
        return d.total_seconds()  # Works in Python 2.7+
    return (d.microseconds + (d.seconds + d.days * 24 * 3600) * 10**6) / 10**6


class ArgumentGenerator(object):
    """Generate sample input based on a shape model.

    This class contains a ``generate_skeleton`` method that will take
    an input shape (created from ``altuscli.model``) and generate
    a sample dictionary corresponding to the input shape.

    The specific values used are place holder values. For strings an
    empty string is used, for numbers 0 or 0.0 is used. For datetime a date in
    RFC822 is used. The intended usage of this class is to generate the *shape*
    of the input object. In the future we might take the defaults from the
    model.

    This can be useful for operations that have complex input shapes.
    This allows a user to just fill in the necessary data instead of
    worrying about the specific object of the input arguments.

    Example usage::

        clidriver = CLIDriver
        ddb = clidriver.get_service_model('dataeng')
        arg_gen = ArgumentGenerator()
        sample_input = arg_gen.generate_skeleton(
            ddb.operation_model('createCluster').input_shape)
        print("Sample input for dataeng.createCluster: %s" % sample_input)

    """
    def __init__(self):
        pass

    def generate_skeleton(self, shape):
        if shape.type_name == OBJECT_TYPE:
            return self._generate_type_object(shape)
        elif shape.type_name == LIST_TYPE:
            return self._generate_type_array(shape)
        elif shape.type_name == 'string':
            return ''
        elif shape.type_name in ['integer']:
            return 0
        elif shape.type_name == 'number':
            return 0.0
        elif shape.type_name == 'boolean':
            return True
        elif shape.type_name == 'datetime':
            return 'Wed, 02 Oct 2002 13:00:00 GMT'
        else:
            raise Exception("Unknown shape type: %s" % shape.type_name)

    def _generate_type_object(self, shape):
        skeleton = OrderedDict()
        for member_name, member_shape in shape.members.items():
            skeleton[member_name] = self.generate_skeleton(member_shape)
        return skeleton

    def _generate_type_array(self, shape):
        # For list elements we've arbitrarily decided to return the first
        # element for the skeleton list.
        return [
            self.generate_skeleton(shape.member),
        ]
