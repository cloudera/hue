"""Utils for working with the parquet thrift models."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import thriftpy


THRIFT_FILE = os.path.join(os.path.dirname(__file__), "parquet.thrift")
parquet_thrift = thriftpy.load(THRIFT_FILE, module_name=str("parquet_thrift"))  # pylint: disable=invalid-name


class SchemaHelper(object):
    """Utility providing convenience methods for schema_elements."""

    def __init__(self, schema_elements):
        """Initialize with the specified schema_elements."""
        self.schema_elements = schema_elements
        self.schema_elements_by_name = dict(
            [(se.name, se) for se in schema_elements])
        assert len(self.schema_elements) == len(self.schema_elements_by_name)

    def schema_element(self, name):
        """Get the schema element with the given name."""
        return self.schema_elements_by_name[name]

    def is_required(self, name):
        """Return true iff the schema element with the given name is required."""
        return self.schema_element(name).repetition_type == parquet_thrift.FieldRepetitionType.REQUIRED

    def max_repetition_level(self, path):
        """Get the max repetition level for the given schema path."""
        max_level = 0
        for part in path:
            element = self.schema_element(part)
            if element.repetition_type == parquet_thrift.FieldRepetitionType.REQUIRED:
                max_level += 1
        return max_level

    def max_definition_level(self, path):
        """Get the max definition level for the given schema path."""
        max_level = 0
        for part in path:
            element = self.schema_element(part)
            if element.repetition_type != parquet_thrift.FieldRepetitionType.REQUIRED:
                max_level += 1
        return max_level
