"""Utils for working with the parquet thrift models"""

from ttypes import FieldRepetitionType


class SchemaHelper(object):

    def __init__(self, schema_elements):
        self.schema_elements = schema_elements
        self.schema_elements_by_name = dict(
            [(se.name, se) for se in schema_elements])
        assert len(self.schema_elements) == len(self.schema_elements_by_name)

    def schema_element(self, name):
        """Get the schema element with the given name."""
        return self.schema_elements_by_name[name]

    def is_required(self, name):
        """Returns true iff the schema element with the given name is
        required"""
        return self.schema_element(name).repetition_type == FieldRepetitionType.REQUIRED

    def max_repetition_level(self, path):
        """get the max repetition level for the given schema path."""
        max_level = 0
        for part in path:
            se = self.schema_element(part)
            if se.repetition_type == FieldRepetitionType.REQUIRED:
                max_level += 1
        return max_level

    def max_definition_level(self, path):
        """get the max definition level for the given schema path."""
        max_level = 0
        for part in path:
            se = self.schema_element(part)
            if se.repetition_type != FieldRepetitionType.REQUIRED:
                max_level += 1
        return max_level
