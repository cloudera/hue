# coding: utf-8
"""Django test runner that invokes nose.

You can use... ::

    NOSE_ARGS = ['list', 'of', 'args']

in settings.py for arguments that you want always passed to nose.

"""
from __future__ import print_function, unicode_literals

import os
import sys
from importlib import import_module
from optparse import NO_DEFAULT
from types import MethodType

from django import setup
from django.apps import apps
from django.conf import settings
from django.core import exceptions
from django.core.management.color import no_style
from django.core.management.commands.loaddata import Command
from django.db import connections, transaction, DEFAULT_DB_ALIAS
from django.test.runner import DiscoverRunner

from django_nose.plugin import DjangoSetUpPlugin, ResultPlugin, TestReorderer
from django_nose.utils import uses_mysql
import nose.core

__all__ = ('BasicNoseRunner', 'NoseTestSuiteRunner')


# This is a table of Django's "manage.py test" options which
# correspond to nosetests options with a different name:
OPTION_TRANSLATION = {'--failfast': '-x',
                      '--nose-verbosity': '--verbosity'}


def translate_option(opt):
    if '=' in opt:
        long_opt, value = opt.split('=', 1)
        return '%s=%s' % (translate_option(long_opt), value)
    return OPTION_TRANSLATION.get(opt, opt)


def _get_plugins_from_settings():
    plugins = (list(getattr(settings, 'NOSE_PLUGINS', [])) +
               ['django_nose.plugin.TestReorderer'])
    for plug_path in plugins:
        try:
            dot = plug_path.rindex('.')
        except ValueError:
            raise exceptions.ImproperlyConfigured(
                "%s isn't a Nose plugin module" % plug_path)
        p_mod, p_classname = plug_path[:dot], plug_path[dot + 1:]

        try:
            mod = import_module(p_mod)
        except ImportError as e:
            raise exceptions.ImproperlyConfigured(
                'Error importing Nose plugin module %s: "%s"' % (p_mod, e))

        try:
            p_class = getattr(mod, p_classname)
        except AttributeError:
            raise exceptions.ImproperlyConfigured(
                'Nose plugin module "%s" does not define a "%s"' %
                (p_mod, p_classname))

        yield p_class()


class BaseRunner(DiscoverRunner):
    """Runner that translates nose optparse arguments to argparse.

    Django 1.8 and later uses argparse.ArgumentParser. Nose's optparse
    arguments need to be translated to this format, so that the Django
    command line parsing will pass. This parsing is (mostly) thrown out,
    and reassembled into command line arguments for nose to reparse.
    """

    # Don't pass the following options to nosetests
    django_opts = [
        '--noinput', '--liveserver', '-p', '--pattern', '--testrunner',
        '--settings',
        # 1.8 arguments
        '--keepdb', '--reverse', '--debug-sql',
        # 1.9 arguments
        '--parallel',
        # 1.10 arguments
        '--tag', '--exclude-tag',
        # 1.11 arguments
        '--debug-mode',
    ]

    #
    # For optparse -> argparse conversion
    #
    # Option strings to remove from Django options if found
    _argparse_remove_options = (
        '-p',  # Short arg for nose's --plugins, not Django's --patterns
        '-d',  # Short arg for nose's --detailed-errors, not Django's
               #  --debug-sql
    )

    # Convert nose optparse options to argparse options
    _argparse_type = {
        'int': int,
        'float': float,
        'complex': complex,
        'string': str,
        'choice': str,
    }
    # If optparse has a None argument, omit from call to add_argument
    _argparse_omit_if_none = (
        'action', 'nargs', 'const', 'default', 'type', 'choices',
        'required', 'help', 'metavar', 'dest')

    # Always ignore these optparse arguments
    # Django will parse without calling the callback
    # nose will then reparse with the callback
    _argparse_callback_options = (
        'callback', 'callback_args', 'callback_kwargs')

    # Keep track of nose options with nargs=1
    _has_nargs = set(['--verbosity'])

    @classmethod
    def add_arguments(cls, parser):
        """Convert nose's optparse arguments to argparse."""
        super(BaseRunner, cls).add_arguments(parser)

        # Read optparse options for nose and plugins
        cfg_files = nose.core.all_config_files()
        manager = nose.core.DefaultPluginManager()
        config = nose.core.Config(
            env=os.environ, files=cfg_files, plugins=manager)
        config.plugins.addPlugins(list(_get_plugins_from_settings()))
        options = config.getParser()._get_all_options()

        # Gather existing option strings`
        django_options = set()
        for action in parser._actions:
            for override in cls._argparse_remove_options:
                if override in action.option_strings:
                    # Emulate parser.conflict_handler='resolve'
                    parser._handle_conflict_resolve(
                        None, ((override, action),))
            django_options.update(action.option_strings)

        # Process nose optparse options
        for option in options:
            # Gather options
            opt_long = option.get_opt_string()
            if option._short_opts:
                opt_short = option._short_opts[0]
            else:
                opt_short = None

            # Rename nose's --verbosity to --nose-verbosity
            if opt_long == '--verbosity':
                opt_long = '--nose-verbosity'

            # Skip any options also in Django options
            if opt_long in django_options:
                continue
            if opt_short and opt_short in django_options:
                opt_short = None

            # Convert optparse attributes to argparse attributes
            option_attrs = {}
            for attr in option.ATTRS:
                # Ignore callback options
                if attr in cls._argparse_callback_options:
                    continue

                value = getattr(option, attr)

                if attr == 'default' and value == NO_DEFAULT:
                    continue

                # Rename options for nose's --verbosity
                if opt_long == '--nose-verbosity':
                    if attr == 'dest':
                        value = 'nose_verbosity'
                    elif attr == 'metavar':
                        value = 'NOSE_VERBOSITY'

                # Omit arguments that are None, use default
                if attr in cls._argparse_omit_if_none and value is None:
                    continue

                # Convert type from optparse string to argparse type
                if attr == 'type':
                    value = cls._argparse_type[value]

                # Convert action='callback' to action='store'
                if attr == 'action' and value == 'callback':
                    action = 'store'

                # Keep track of nargs=1
                if attr == 'nargs':
                    assert value == 1, (
                        'argparse option nargs=%s is not supported' %
                        value)
                    cls._has_nargs.add(opt_long)
                    if opt_short:
                        cls._has_nargs.add(opt_short)

                # Pass converted attribute to optparse option
                option_attrs[attr] = value

            # Add the optparse argument
            if opt_short:
                parser.add_argument(opt_short, opt_long, **option_attrs)
            else:
                parser.add_argument(opt_long, **option_attrs)


class BasicNoseRunner(BaseRunner):
    """Facade that implements a nose runner in the guise of a Django runner.

    You shouldn't have to use this directly unless the additions made by
    ``NoseTestSuiteRunner`` really bother you. They shouldn't, because they're
    all off by default.
    """

    __test__ = False

    def run_suite(self, nose_argv):
        """Run the test suite."""
        result_plugin = ResultPlugin()
        plugins_to_add = [DjangoSetUpPlugin(self),
                          result_plugin,
                          TestReorderer()]

        for plugin in _get_plugins_from_settings():
            plugins_to_add.append(plugin)

        setup()

        nose.core.TestProgram(argv=nose_argv, exit=False,
                              addplugins=plugins_to_add)
        return result_plugin.result

    def run_tests(self, test_labels, extra_tests=None):
        """
        Run the unit tests for all the test names in the provided list.

        Test names specified may be file or module names, and may optionally
        indicate the test case to run by separating the module or file name
        from the test case name with a colon. Filenames may be relative or
        absolute.

        N.B.: The test_labels argument *MUST* be a sequence of
        strings, *NOT* just a string object.  (Or you will be
        specifying tests for for each character in your string, and
        not the whole string.

        Examples:
        runner.run_tests( ('test.module',) )
        runner.run_tests(['another.test:TestCase.test_method'])
        runner.run_tests(['a.test:TestCase'])
        runner.run_tests(['/path/to/test/file.py:test_function'])
        runner.run_tests( ('test.module', 'a.test:TestCase') )

        Note: the extra_tests argument is currently ignored.  You can
        run old non-nose code that uses it without totally breaking,
        but the extra tests will not be run.  Maybe later.

        Returns the number of tests that failed.

        """
        nose_argv = (['nosetests'] + list(test_labels))
        if hasattr(settings, 'NOSE_ARGS'):
            nose_argv.extend(settings.NOSE_ARGS)

        # Recreate the arguments in a nose-compatible format
        arglist = sys.argv[1:]
        has_nargs = getattr(self, '_has_nargs', set(['--verbosity']))
        while arglist:
            opt = arglist.pop(0)
            if not opt.startswith('-'):
                # Discard test labels
                continue
            if any(opt.startswith(d) for d in self.django_opts):
                # Discard options handled by Djangp
                continue

            trans_opt = translate_option(opt)
            nose_argv.append(trans_opt)

            if opt in has_nargs:
                # Handle arguments without an equals sign
                opt_value = arglist.pop(0)
                nose_argv.append(opt_value)

        # if --nose-verbosity was omitted, pass Django verbosity to nose
        if ('--verbosity' not in nose_argv and
                not any(opt.startswith('--verbosity=') for opt in nose_argv)):
            nose_argv.append('--verbosity=%s' % str(self.verbosity))

        if self.verbosity >= 1:
            print(' '.join(nose_argv))

        result = self.run_suite(nose_argv)
        # suite_result expects the suite as the first argument.  Fake it.
        return self.suite_result({}, result)


_old_handle = Command.handle


def _foreign_key_ignoring_handle(self, *fixture_labels, **options):
    """Wrap the the stock loaddata to ignore foreign key checks.

    This allows loading circular references from fixtures, and is
    monkeypatched into place in setup_databases().
    """
    using = options.get('database', DEFAULT_DB_ALIAS)
    commit = options.get('commit', True)
    connection = connections[using]

    # MySQL stinks at loading circular references:
    if uses_mysql(connection):
        cursor = connection.cursor()
        cursor.execute('SET foreign_key_checks = 0')

    _old_handle(self, *fixture_labels, **options)

    if uses_mysql(connection):
        cursor = connection.cursor()
        cursor.execute('SET foreign_key_checks = 1')

        if commit:
            connection.close()


def _skip_create_test_db(self, verbosity=1, autoclobber=False, serialize=True,
                         keepdb=True):
    """``create_test_db`` implementation that skips both creation and flushing.

    The idea is to re-use the perfectly good test DB already created by an
    earlier test run, cutting the time spent before any tests run from 5-13s
    (depending on your I/O luck) down to 3.
    """
    # Notice that the DB supports transactions. Originally, this was done in
    # the method this overrides. The confirm method was added in Django v1.3
    # (https://code.djangoproject.com/ticket/12991) but removed in Django v1.5
    # (https://code.djangoproject.com/ticket/17760). In Django v1.5
    # supports_transactions is a cached property evaluated on access.
    if callable(getattr(self.connection.features, 'confirm', None)):
        # Django v1.3-4
        self.connection.features.confirm()
    elif hasattr(self, "_rollback_works"):
        # Django v1.2 and lower
        can_rollback = self._rollback_works()
        self.connection.settings_dict['SUPPORTS_TRANSACTIONS'] = can_rollback

    return self._get_test_db_name()


def _reusing_db():
    """Return whether the ``REUSE_DB`` flag was passed."""
    return os.getenv('REUSE_DB', 'false').lower() in ('true', '1')


def _can_support_reuse_db(connection):
    """Return True if REUSE_DB is a sensible option for the backend."""
    # Perhaps this is a SQLite in-memory DB. Those are created implicitly when
    # you try to connect to them, so our usual test doesn't work.
    return not connection.creation._get_test_db_name() == ':memory:'


def _should_create_database(connection):
    """Return whether we should recreate the given DB.

    This is true if the DB doesn't exist or the REUSE_DB env var isn't truthy.
    """
    # TODO: Notice when the Model classes change and return True. Worst case,
    # we can generate sqlall and hash it, though it's a bit slow (2 secs) and
    # hits the DB for no good reason. Until we find a faster way, I'm inclined
    # to keep making people explicitly saying REUSE_DB if they want to reuse
    # the DB.

    if not _can_support_reuse_db(connection):
        return True

    # Notice whether the DB exists, and create it if it doesn't:
    try:
        # Connections are cached by some backends, if other code has connected
        # to the database previously under a different database name the
        # cached connection will be used and no exception will be raised.
        # Avoiding this by closing connections and setting to null
        for connection in connections.all():
            connection.close()
        connection.connection = None
        connection.cursor()
    except Exception:  # TODO: Be more discerning but still DB agnostic.
        return True
    return not _reusing_db()


def _mysql_reset_sequences(style, connection):
    """Return a SQL statements needed to reset Django tables."""
    tables = connection.introspection.django_table_names(only_existing=True)
    flush_statements = connection.ops.sql_flush(
        style, tables, connection.introspection.sequence_list())

    # connection.ops.sequence_reset_sql() is not implemented for MySQL,
    # and the base class just returns []. TODO: Implement it by pulling
    # the relevant bits out of sql_flush().
    return [s for s in flush_statements if s.startswith('ALTER')]
    # Being overzealous and resetting the sequences on non-empty tables
    # like django_content_type seems to be fine in MySQL: adding a row
    # afterward does find the correct sequence number rather than
    # crashing into an existing row.


class NoseTestSuiteRunner(BasicNoseRunner):
    """A runner that optionally skips DB creation.

    Monkeypatches connection.creation to let you skip creating databases if
    they already exist. Your tests will start up much faster.

    To opt into this behavior, set the environment variable ``REUSE_DB`` to
    "1" or "true" (case insensitive).
    """

    def _get_models_for_connection(self, connection):
        """Return a list of models for a connection."""
        tables = connection.introspection.get_table_list(connection.cursor())
        return [m for m in apps.get_models() if
                m._meta.db_table in tables]

    def setup_databases(self):
        """Set up databases. Skip DB creation if requested and possible."""
        for alias in connections:
            connection = connections[alias]
            creation = connection.creation
            test_db_name = creation._get_test_db_name()

            # Mess with the DB name so other things operate on a test DB
            # rather than the real one. This is done in create_test_db when
            # we don't monkeypatch it away with _skip_create_test_db.
            orig_db_name = connection.settings_dict['NAME']
            connection.settings_dict['NAME'] = test_db_name

            if _should_create_database(connection):
                # We're not using _skip_create_test_db, so put the DB name
                # back:
                connection.settings_dict['NAME'] = orig_db_name

                # Since we replaced the connection with the test DB, closing
                # the connection will avoid pooling issues with SQLAlchemy. The
                # issue is trying to CREATE/DROP the test database using a
                # connection to a DB that was established with that test DB.
                # MySQLdb doesn't allow it, and SQLAlchemy attempts to reuse
                # the existing connection from its pool.
                connection.close()
            else:
                # Reset auto-increment sequences. Apparently, SUMO's tests are
                # horrid and coupled to certain numbers.
                cursor = connection.cursor()
                style = no_style()

                if uses_mysql(connection):
                    reset_statements = _mysql_reset_sequences(
                        style, connection)
                else:
                    reset_statements = connection.ops.sequence_reset_sql(
                        style, self._get_models_for_connection(connection))

                if hasattr(transaction, "atomic"):
                    with transaction.atomic(using=connection.alias):
                        for reset_statement in reset_statements:
                            cursor.execute(reset_statement)
                else:
                    # Django < 1.6
                    for reset_statement in reset_statements:
                        cursor.execute(reset_statement)
                    transaction.commit_unless_managed(using=connection.alias)

                # Each connection has its own creation object, so this affects
                # only a single connection:
                creation.create_test_db = MethodType(
                    _skip_create_test_db, creation)

        Command.handle = _foreign_key_ignoring_handle

        # With our class patch, does nothing but return some connection
        # objects:
        return super(NoseTestSuiteRunner, self).setup_databases()

    def teardown_databases(self, *args, **kwargs):
        """Leave those poor, reusable databases alone if REUSE_DB is true."""
        if not _reusing_db():
            return super(NoseTestSuiteRunner, self).teardown_databases(
                *args, **kwargs)
        # else skip tearing down the DB so we can reuse it next time
