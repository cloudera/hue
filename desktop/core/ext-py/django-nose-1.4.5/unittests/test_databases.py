"""Test database access without a database."""
from contextlib import contextmanager
from unittest import TestCase

try:
    from django.db.models.loading import cache as apps
except:
    from django.apps import apps

from nose.plugins.attrib import attr
from django_nose.runner import NoseTestSuiteRunner


class GetModelsForConnectionTests(TestCase):
    """Test runner._get_models_for_connection."""

    tables = ['test_table%d' % i for i in range(5)]

    def _connection_mock(self, tables):
        class FakeIntrospection(object):
            def get_table_list(*args, **kwargs):
                return tables

        class FakeConnection(object):
            introspection = FakeIntrospection()

            def cursor(self):
                return None

        return FakeConnection()

    def _model_mock(self, db_table):
        class FakeModel(object):
            _meta = type('meta', (object,), {'db_table': db_table})()

        return FakeModel()

    @contextmanager
    def _cache_mock(self, tables=[]):
        def get_models(*args, **kwargs):
            return [self._model_mock(t) for t in tables]

        old = apps.get_models
        apps.get_models = get_models
        yield
        apps.get_models = old

    def setUp(self):
        """Initialize the runner."""
        self.runner = NoseTestSuiteRunner()

    def test_no_models(self):
        """For a DB with no tables, return nothing."""
        connection = self._connection_mock([])
        with self._cache_mock(['table1', 'table2']):
            self.assertEqual(
                self.runner._get_models_for_connection(connection), [])

    def test_wrong_models(self):
        """If no tables exists for models, return nothing."""
        connection = self._connection_mock(self.tables)
        with self._cache_mock(['table1', 'table2']):
            self.assertEqual(
                self.runner._get_models_for_connection(connection), [])

    @attr("special")
    def test_some_models(self):
        """If some of the models are in the DB, return matching models."""
        connection = self._connection_mock(self.tables)
        with self._cache_mock(self.tables[1:3]):
            result_tables = [
                m._meta.db_table for m in
                self.runner._get_models_for_connection(connection)]
        self.assertEqual(result_tables, self.tables[1:3])

    def test_all_models(self):
        """If all the models have in the DB, return them all."""
        connection = self._connection_mock(self.tables)
        with self._cache_mock(self.tables):
            result_tables = [
                m._meta.db_table for m in
                self.runner._get_models_for_connection(connection)]
        self.assertEqual(result_tables, self.tables)
