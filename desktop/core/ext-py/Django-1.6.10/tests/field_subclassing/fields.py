from __future__ import unicode_literals

import json

from django.db import models
from django.utils.encoding import force_text
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Small(object):
    """
    A simple class to show that non-trivial Python objects can be used as
    attributes.
    """
    def __init__(self, first, second):
        self.first, self.second = first, second

    def __str__(self):
        return '%s%s' % (force_text(self.first), force_text(self.second))

class SmallField(six.with_metaclass(models.SubfieldBase, models.Field)):
    """
    Turns the "Small" class into a Django field. Because of the similarities
    with normal character fields and the fact that Small.__unicode__ does
    something sensible, we don't need to implement a lot here.
    """

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 2
        super(SmallField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

    def to_python(self, value):
        if isinstance(value, Small):
            return value
        return Small(value[0], value[1])

    def get_db_prep_save(self, value, connection):
        return six.text_type(value)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return force_text(value)
        if lookup_type == 'in':
            return [force_text(v) for v in value]
        if lookup_type == 'isnull':
            return []
        raise TypeError('Invalid lookup type: %r' % lookup_type)

class SmallerField(SmallField):
    pass


class JSONField(six.with_metaclass(models.SubfieldBase, models.TextField)):

    description = ("JSONField automatically serializes and desializes values to "
        "and from JSON.")

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, six.string_types):
            value = json.loads(value)
        return value

    def get_db_prep_save(self, value, connection):
        if value is None:
            return None
        return json.dumps(value)
