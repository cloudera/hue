"""Unload fixtures by truncating tables rather than rebuilding.

A copy of Django 1.3.0's stock loaddata.py, adapted so that, instead of
loading any data, it returns the tables referenced by a set of fixtures so we
can truncate them (and no others) quickly after we're finished with them.
"""

import os
import gzip
import zipfile
from itertools import product

from django.conf import settings
from django.core import serializers
from django.db import router, DEFAULT_DB_ALIAS

try:
    from django.db.models import get_apps
except ImportError:
    from django.apps import apps

    def get_apps():
        """Emulate get_apps in Django 1.9 and later."""
        return [a.models_module for a in apps.get_app_configs()]

try:
    import bz2
    has_bz2 = True
except ImportError:
    has_bz2 = False


def tables_used_by_fixtures(fixture_labels, using=DEFAULT_DB_ALIAS):
    """Get tables used by a fixture.

    Acts like Django's stock loaddata command, but, instead of loading data,
    return an iterable of the names of the tables into which data would be
    loaded.
    """
    # Keep a count of the installed objects and fixtures
    fixture_count = 0
    loaded_object_count = 0
    fixture_object_count = 0
    tables = set()

    class SingleZipReader(zipfile.ZipFile):
        def __init__(self, *args, **kwargs):
            zipfile.ZipFile.__init__(self, *args, **kwargs)
            if settings.DEBUG:
                assert len(self.namelist()) == 1, \
                    "Zip-compressed fixtures must contain only one file."

        def read(self):
            return zipfile.ZipFile.read(self, self.namelist()[0])

    compression_types = {
        None:   open,
        'gz':   gzip.GzipFile,
        'zip':  SingleZipReader
    }
    if has_bz2:
        compression_types['bz2'] = bz2.BZ2File

    app_module_paths = []
    for app in get_apps():
        if hasattr(app, '__path__'):
            # It's a 'models/' subpackage
            for path in app.__path__:
                app_module_paths.append(path)
        else:
            # It's a models.py module
            app_module_paths.append(app.__file__)

    app_fixtures = [
        os.path.join(os.path.dirname(path), 'fixtures')
        for path in app_module_paths]
    for fixture_label in fixture_labels:
        parts = fixture_label.split('.')

        if len(parts) > 1 and parts[-1] in compression_types:
            compression_formats = [parts[-1]]
            parts = parts[:-1]
        else:
            compression_formats = list(compression_types.keys())

        if len(parts) == 1:
            fixture_name = parts[0]
            formats = serializers.get_public_serializer_formats()
        else:
            fixture_name, format = '.'.join(parts[:-1]), parts[-1]
            if format in serializers.get_public_serializer_formats():
                formats = [format]
            else:
                formats = []

        if not formats:
            # stderr.write(style.ERROR("Problem installing fixture '%s': %s is
            # not a known serialization format.\n" % (fixture_name, format)))
            return set()

        if os.path.isabs(fixture_name):
            fixture_dirs = [fixture_name]
        else:
            fixture_dirs = app_fixtures + list(settings.FIXTURE_DIRS) + ['']

        for fixture_dir in fixture_dirs:
            # stdout.write("Checking %s for fixtures...\n" %
            # humanize(fixture_dir))

            label_found = False
            for combo in product([using, None], formats, compression_formats):
                database, format, compression_format = combo
                file_name = '.'.join(
                    p for p in [
                        fixture_name, database, format, compression_format
                    ]
                    if p
                )

                # stdout.write("Trying %s for %s fixture '%s'...\n" % \
                # (humanize(fixture_dir), file_name, fixture_name))
                full_path = os.path.join(fixture_dir, file_name)
                open_method = compression_types[compression_format]
                try:
                    fixture = open_method(full_path, 'r')
                    if label_found:
                        fixture.close()
                        # stderr.write(style.ERROR("Multiple fixtures named
                        # '%s' in %s. Aborting.\n" % (fixture_name,
                        # humanize(fixture_dir))))
                        return set()
                    else:
                        fixture_count += 1
                        objects_in_fixture = 0
                        loaded_objects_in_fixture = 0
                        # stdout.write("Installing %s fixture '%s' from %s.\n"
                        # % (format, fixture_name, humanize(fixture_dir)))
                        try:
                            objects = serializers.deserialize(
                                format, fixture, using=using)
                            for obj in objects:
                                objects_in_fixture += 1
                                cls = obj.object.__class__
                                if router.allow_syncdb(using, cls):
                                    loaded_objects_in_fixture += 1
                                    tables.add(cls._meta.db_table)
                            loaded_object_count += loaded_objects_in_fixture
                            fixture_object_count += objects_in_fixture
                            label_found = True
                        except (SystemExit, KeyboardInterrupt):
                            raise
                        except Exception:
                            fixture.close()
                            # stderr.write( style.ERROR("Problem installing
                            # fixture '%s': %s\n" % (full_path, ''.join(tra
                            # ceback.format_exception(sys.exc_type,
                            # sys.exc_value, sys.exc_traceback)))))
                            return set()
                        fixture.close()

                        # If the fixture we loaded contains 0 objects, assume
                        # that an error was encountered during fixture loading.
                        if objects_in_fixture == 0:
                            # stderr.write( style.ERROR("No fixture data found
                            # for '%s'. (File format may be invalid.)\n" %
                            # (fixture_name)))
                            return set()

                except Exception:
                    # stdout.write("No %s fixture '%s' in %s.\n" % \ (format,
                    # fixture_name, humanize(fixture_dir)))
                    pass

    return tables
