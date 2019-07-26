from django_prometheus.db.common import (
    DatabaseWrapperMixin, ExportingCursorWrapper)
from django.db.backends.mysql import base


class DatabaseFeatures(base.DatabaseFeatures):
    """Our database has the exact same features as the base one."""
    pass


class DatabaseWrapper(DatabaseWrapperMixin, base.DatabaseWrapper):
    CURSOR_CLASS = base.CursorWrapper

    def create_cursor(self, name=None):
        cursor = self.connection.cursor()
        CursorWrapper = ExportingCursorWrapper(
            self.CURSOR_CLASS, self.alias, self.vendor)
        return CursorWrapper(cursor)
