"""
Oracle database backend for Django.

Requires cx_Oracle: http://cx-oracle.sourceforge.net/
"""
from __future__ import unicode_literals

import decimal
import re
import sys
import warnings

def _setup_environment(environ):
    import platform
    # Cygwin requires some special voodoo to set the environment variables
    # properly so that Oracle will see them.
    if platform.system().upper().startswith('CYGWIN'):
        try:
            import ctypes
        except ImportError as e:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured("Error loading ctypes: %s; "
                                       "the Oracle backend requires ctypes to "
                                       "operate correctly under Cygwin." % e)
        kernel32 = ctypes.CDLL('kernel32')
        for name, value in environ:
            kernel32.SetEnvironmentVariableA(name, value)
    else:
        import os
        os.environ.update(environ)

_setup_environment([
    # Oracle takes client-side character set encoding from the environment.
    ('NLS_LANG', '.UTF8'),
    # This prevents unicode from getting mangled by getting encoded into the
    # potentially non-unicode database character set.
    ('ORA_NCHAR_LITERAL_REPLACE', 'TRUE'),
])


try:
    import cx_Oracle as Database
except ImportError as e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Error loading cx_Oracle module: %s" % e)

try:
    import pytz
except ImportError:
    pytz = None

from django.db import utils
from django.db.backends import *
from django.db.backends.oracle.client import DatabaseClient
from django.db.backends.oracle.creation import DatabaseCreation
from django.db.backends.oracle.introspection import DatabaseIntrospection
from django.utils.encoding import force_bytes, force_text


DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError

# Check whether cx_Oracle was compiled with the WITH_UNICODE option if cx_Oracle is pre-5.1. This will
# also be True for cx_Oracle 5.1 and in Python 3.0. See #19606
if int(Database.version.split('.', 1)[0]) >= 5 and \
        (int(Database.version.split('.', 2)[1]) >= 1 or
         not hasattr(Database, 'UNICODE')):
    convert_unicode = force_text
else:
    convert_unicode = force_bytes


class Oracle_datetime(datetime.datetime):
    """
    A datetime object, with an additional class attribute
    to tell cx_Oracle to save the microseconds too.
    """
    input_size = Database.TIMESTAMP

    @classmethod
    def from_datetime(cls, dt):
        return Oracle_datetime(dt.year, dt.month, dt.day,
                               dt.hour, dt.minute, dt.second, dt.microsecond)


class DatabaseFeatures(BaseDatabaseFeatures):
    empty_fetchmany_value = ()
    needs_datetime_string_cast = False
    interprets_empty_strings_as_nulls = True
    uses_savepoints = True
    has_select_for_update = True
    has_select_for_update_nowait = True
    can_return_id_from_insert = True
    allow_sliced_subqueries = False
    supports_subqueries_in_group_by = False
    supports_transactions = True
    supports_timezones = False
    has_zoneinfo_database = pytz is not None
    supports_bitwise_or = False
    can_defer_constraint_checks = True
    ignores_nulls_in_unique_constraints = False
    has_bulk_insert = True
    supports_tablespaces = True
    supports_sequence_reset = False
    atomic_transactions = False

class DatabaseOperations(BaseDatabaseOperations):
    compiler_module = "django.db.backends.oracle.compiler"

    def autoinc_sql(self, table, column):
        # To simulate auto-incrementing primary keys in Oracle, we have to
        # create a sequence and a trigger.
        sq_name = self._get_sequence_name(table)
        tr_name = self._get_trigger_name(table)
        tbl_name = self.quote_name(table)
        col_name = self.quote_name(column)
        sequence_sql = """
DECLARE
    i INTEGER;
BEGIN
    SELECT COUNT(*) INTO i FROM USER_CATALOG
        WHERE TABLE_NAME = '%(sq_name)s' AND TABLE_TYPE = 'SEQUENCE';
    IF i = 0 THEN
        EXECUTE IMMEDIATE 'CREATE SEQUENCE "%(sq_name)s"';
    END IF;
END;
/""" % locals()
        trigger_sql = """
CREATE OR REPLACE TRIGGER "%(tr_name)s"
BEFORE INSERT ON %(tbl_name)s
FOR EACH ROW
WHEN (new.%(col_name)s IS NULL)
    BEGIN
        SELECT "%(sq_name)s".nextval
        INTO :new.%(col_name)s FROM dual;
    END;
/""" % locals()
        return sequence_sql, trigger_sql

    def cache_key_culling_sql(self):
        return """
            SELECT cache_key
              FROM (SELECT cache_key, rank() OVER (ORDER BY cache_key) AS rank FROM %s)
             WHERE rank = %%s + 1
        """

    def date_extract_sql(self, lookup_type, field_name):
        if lookup_type == 'week_day':
            # TO_CHAR(field, 'D') returns an integer from 1-7, where 1=Sunday.
            return "TO_CHAR(%s, 'D')" % field_name
        else:
            # http://docs.oracle.com/cd/B19306_01/server.102/b14200/functions050.htm
            return "EXTRACT(%s FROM %s)" % (lookup_type.upper(), field_name)

    def date_interval_sql(self, sql, connector, timedelta):
        """
        Implements the interval functionality for expressions
        format for Oracle:
        (datefield + INTERVAL '3 00:03:20.000000' DAY(1) TO SECOND(6))
        """
        minutes, seconds = divmod(timedelta.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days = str(timedelta.days)
        day_precision = len(days)
        fmt = "(%s %s INTERVAL '%s %02d:%02d:%02d.%06d' DAY(%d) TO SECOND(6))"
        return fmt % (sql, connector, days, hours, minutes, seconds,
                timedelta.microseconds, day_precision)

    def date_trunc_sql(self, lookup_type, field_name):
        # http://docs.oracle.com/cd/B19306_01/server.102/b14200/functions230.htm#i1002084
        if lookup_type in ('year', 'month'):
            return "TRUNC(%s, '%s')" % (field_name, lookup_type.upper())
        else:
            return "TRUNC(%s)" % field_name

    # Oracle crashes with "ORA-03113: end-of-file on communication channel"
    # if the time zone name is passed in parameter. Use interpolation instead.
    # https://groups.google.com/forum/#!msg/django-developers/zwQju7hbG78/9l934yelwfsJ
    # This regexp matches all time zone names from the zoneinfo database.
    _tzname_re = re.compile(r'^[\w/:+-]+$')

    def _convert_field_to_tz(self, field_name, tzname):
        if not self._tzname_re.match(tzname):
            raise ValueError("Invalid time zone name: %s" % tzname)
        # Convert from UTC to local time, returning TIMESTAMP WITH TIME ZONE.
        result = "(FROM_TZ(%s, '0:00') AT TIME ZONE '%s')" % (field_name, tzname)
        # Extracting from a TIMESTAMP WITH TIME ZONE ignore the time zone.
        # Convert to a DATETIME, which is called DATE by Oracle. There's no
        # built-in function to do that; the easiest is to go through a string.
        result = "TO_CHAR(%s, 'YYYY-MM-DD HH24:MI:SS')" % result
        result = "TO_DATE(%s, 'YYYY-MM-DD HH24:MI:SS')" % result
        # Re-convert to a TIMESTAMP because EXTRACT only handles the date part
        # on DATE values, even though they actually store the time part.
        return "CAST(%s AS TIMESTAMP)" % result

    def datetime_extract_sql(self, lookup_type, field_name, tzname):
        if settings.USE_TZ:
            field_name = self._convert_field_to_tz(field_name, tzname)
        if lookup_type == 'week_day':
            # TO_CHAR(field, 'D') returns an integer from 1-7, where 1=Sunday.
            sql = "TO_CHAR(%s, 'D')" % field_name
        else:
            # http://docs.oracle.com/cd/B19306_01/server.102/b14200/functions050.htm
            sql = "EXTRACT(%s FROM %s)" % (lookup_type.upper(), field_name)
        return sql, []

    def datetime_trunc_sql(self, lookup_type, field_name, tzname):
        if settings.USE_TZ:
            field_name = self._convert_field_to_tz(field_name, tzname)
        # http://docs.oracle.com/cd/B19306_01/server.102/b14200/functions230.htm#i1002084
        if lookup_type in ('year', 'month'):
            sql = "TRUNC(%s, '%s')" % (field_name, lookup_type.upper())
        elif lookup_type == 'day':
            sql = "TRUNC(%s)" % field_name
        elif lookup_type == 'hour':
            sql = "TRUNC(%s, 'HH24')" % field_name
        elif lookup_type == 'minute':
            sql = "TRUNC(%s, 'MI')" % field_name
        else:
            sql = field_name    # Cast to DATE removes sub-second precision.
        return sql, []

    def convert_values(self, value, field):
        if isinstance(value, Database.LOB):
            value = value.read()
            if field and field.get_internal_type() == 'TextField':
                value = force_text(value)

        # Oracle stores empty strings as null. We need to undo this in
        # order to adhere to the Django convention of using the empty
        # string instead of null, but only if the field accepts the
        # empty string.
        if value is None and field and field.empty_strings_allowed:
            value = ''
        # Convert 1 or 0 to True or False
        elif value in (1, 0) and field and field.get_internal_type() in ('BooleanField', 'NullBooleanField'):
            value = bool(value)
        # Force floats to the correct type
        elif value is not None and field and field.get_internal_type() == 'FloatField':
            value = float(value)
        # Convert floats to decimals
        elif value is not None and field and field.get_internal_type() == 'DecimalField':
            value = util.typecast_decimal(field.format_number(value))
        # cx_Oracle always returns datetime.datetime objects for
        # DATE and TIMESTAMP columns, but Django wants to see a
        # python datetime.date, .time, or .datetime.  We use the type
        # of the Field to determine which to cast to, but it's not
        # always available.
        # As a workaround, we cast to date if all the time-related
        # values are 0, or to time if the date is 1/1/1900.
        # This could be cleaned a bit by adding a method to the Field
        # classes to normalize values from the database (the to_python
        # method is used for validation and isn't what we want here).
        elif isinstance(value, Database.Timestamp):
            if field and field.get_internal_type() == 'DateTimeField':
                pass
            elif field and field.get_internal_type() == 'DateField':
                value = value.date()
            elif field and field.get_internal_type() == 'TimeField' or (value.year == 1900 and value.month == value.day == 1):
                value = value.time()
            elif value.hour == value.minute == value.second == value.microsecond == 0:
                value = value.date()
        return value

    def deferrable_sql(self):
        return " DEFERRABLE INITIALLY DEFERRED"

    def drop_sequence_sql(self, table):
        return "DROP SEQUENCE %s;" % self.quote_name(self._get_sequence_name(table))

    def fetch_returned_insert_id(self, cursor):
        return int(cursor._insert_id_var.getvalue())

    def field_cast_sql(self, db_type, internal_type):
        if db_type and db_type.endswith('LOB'):
            return "DBMS_LOB.SUBSTR(%s, 4000)"
        else:
            return "%s"

    def last_executed_query(self, cursor, sql, params):
        # http://cx-oracle.sourceforge.net/html/cursor.html#Cursor.statement
        # The DB API definition does not define this attribute.
        statement = cursor.statement
        if statement and six.PY2 and not isinstance(statement, unicode):
            statement = statement.decode('utf-8')
        # Unlike Psycopg's `query` and MySQLdb`'s `_last_executed`, CxOracle's
        # `statement` doesn't contain the query parameters. refs #20010.
        return super(DatabaseOperations, self).last_executed_query(cursor, statement, params)

    def last_insert_id(self, cursor, table_name, pk_name):
        sq_name = self._get_sequence_name(table_name)
        cursor.execute('SELECT "%s".currval FROM dual' % sq_name)
        return cursor.fetchone()[0]

    def lookup_cast(self, lookup_type):
        if lookup_type in ('iexact', 'icontains', 'istartswith', 'iendswith'):
            return "UPPER(%s)"
        return "%s"

    def max_in_list_size(self):
        return 1000

    def max_name_length(self):
        return 30

    def prep_for_iexact_query(self, x):
        return x

    def process_clob(self, value):
        if value is None:
            return ''
        return force_text(value.read())

    def quote_name(self, name):
        # SQL92 requires delimited (quoted) names to be case-sensitive.  When
        # not quoted, Oracle has case-insensitive behavior for identifiers, but
        # always defaults to uppercase.
        # We simplify things by making Oracle identifiers always uppercase.
        if not name.startswith('"') and not name.endswith('"'):
            name = '"%s"' % util.truncate_name(name.upper(),
                                               self.max_name_length())
        # Oracle puts the query text into a (query % args) construct, so % signs
        # in names need to be escaped. The '%%' will be collapsed back to '%' at
        # that stage so we aren't really making the name longer here.
        name = name.replace('%','%%')
        return name.upper()

    def random_function_sql(self):
        return "DBMS_RANDOM.RANDOM"

    def regex_lookup_9(self, lookup_type):
        raise NotImplementedError("Regexes are not supported in Oracle before version 10g.")

    def regex_lookup_10(self, lookup_type):
        if lookup_type == 'regex':
            match_option = "'c'"
        else:
            match_option = "'i'"
        return 'REGEXP_LIKE(%%s, %%s, %s)' % match_option

    def regex_lookup(self, lookup_type):
        # If regex_lookup is called before it's been initialized, then create
        # a cursor to initialize it and recur.
        self.connection.cursor()
        return self.connection.ops.regex_lookup(lookup_type)

    def return_insert_id(self):
        return "RETURNING %s INTO %%s", (InsertIdVar(),)

    def savepoint_create_sql(self, sid):
        return convert_unicode("SAVEPOINT " + self.quote_name(sid))

    def savepoint_rollback_sql(self, sid):
        return convert_unicode("ROLLBACK TO SAVEPOINT " + self.quote_name(sid))

    def sql_flush(self, style, tables, sequences, allow_cascade=False):
        # Return a list of 'TRUNCATE x;', 'TRUNCATE y;',
        # 'TRUNCATE z;'... style SQL statements
        if tables:
            # Oracle does support TRUNCATE, but it seems to get us into
            # FK referential trouble, whereas DELETE FROM table works.
            sql = ['%s %s %s;' % (
                style.SQL_KEYWORD('DELETE'),
                style.SQL_KEYWORD('FROM'),
                style.SQL_FIELD(self.quote_name(table))
            ) for table in tables]
            # Since we've just deleted all the rows, running our sequence
            # ALTER code will reset the sequence to 0.
            sql.extend(self.sequence_reset_by_name_sql(style, sequences))
            return sql
        else:
            return []

    def sequence_reset_by_name_sql(self, style, sequences):
        sql = []
        for sequence_info in sequences:
            sequence_name = self._get_sequence_name(sequence_info['table'])
            table_name = self.quote_name(sequence_info['table'])
            column_name = self.quote_name(sequence_info['column'] or 'id')
            query = _get_sequence_reset_sql() % {'sequence': sequence_name,
                                                    'table': table_name,
                                                    'column': column_name}
            sql.append(query)
        return sql

    def sequence_reset_sql(self, style, model_list):
        from django.db import models
        output = []
        query = _get_sequence_reset_sql()
        for model in model_list:
            for f in model._meta.local_fields:
                if isinstance(f, models.AutoField):
                    table_name = self.quote_name(model._meta.db_table)
                    sequence_name = self._get_sequence_name(model._meta.db_table)
                    column_name = self.quote_name(f.column)
                    output.append(query % {'sequence': sequence_name,
                                           'table': table_name,
                                           'column': column_name})
                    # Only one AutoField is allowed per model, so don't
                    # continue to loop
                    break
            for f in model._meta.many_to_many:
                if not f.rel.through:
                    table_name = self.quote_name(f.m2m_db_table())
                    sequence_name = self._get_sequence_name(f.m2m_db_table())
                    column_name = self.quote_name('id')
                    output.append(query % {'sequence': sequence_name,
                                           'table': table_name,
                                           'column': column_name})
        return output

    def start_transaction_sql(self):
        return ''

    def tablespace_sql(self, tablespace, inline=False):
        if inline:
            return "USING INDEX TABLESPACE %s" % self.quote_name(tablespace)
        else:
            return "TABLESPACE %s" % self.quote_name(tablespace)

    def value_to_db_date(self, value):
        """
        Transform a date value to an object compatible with what is expected
        by the backend driver for date columns.
        The default implementation transforms the date to text, but that is not
        necessary for Oracle.
        """
        return value

    def value_to_db_datetime(self, value):
        """
        Transform a datetime value to an object compatible with what is expected
        by the backend driver for datetime columns.

        If naive datetime is passed assumes that is in UTC. Normally Django
        models.DateTimeField makes sure that if USE_TZ is True passed datetime
        is timezone aware.
        """

        if value is None:
            return None

        # cx_Oracle doesn't support tz-aware datetimes
        if timezone.is_aware(value):
            if settings.USE_TZ:
                value = value.astimezone(timezone.utc).replace(tzinfo=None)
            else:
                raise ValueError("Oracle backend does not support timezone-aware datetimes when USE_TZ is False.")

        return Oracle_datetime.from_datetime(value)

    def value_to_db_time(self, value):
        if value is None:
            return None

        if isinstance(value, six.string_types):
            return datetime.datetime.strptime(value, '%H:%M:%S')

        # Oracle doesn't support tz-aware times
        if timezone.is_aware(value):
            raise ValueError("Oracle backend does not support timezone-aware times.")

        return Oracle_datetime(1900, 1, 1, value.hour, value.minute,
                               value.second, value.microsecond)

    def year_lookup_bounds_for_date_field(self, value):
        # Create bounds as real date values
        first = datetime.date(value, 1, 1)
        last = datetime.date(value, 12, 31)
        return [first, last]

    def year_lookup_bounds_for_datetime_field(self, value):
        # cx_Oracle doesn't support tz-aware datetimes
        bounds = super(DatabaseOperations, self).year_lookup_bounds_for_datetime_field(value)
        if settings.USE_TZ:
            bounds = [b.astimezone(timezone.utc) for b in bounds]
        return [Oracle_datetime.from_datetime(b) for b in bounds]

    def combine_expression(self, connector, sub_expressions):
        "Oracle requires special cases for %% and & operators in query expressions"
        if connector == '%%':
            return 'MOD(%s)' % ','.join(sub_expressions)
        elif connector == '&':
            return 'BITAND(%s)' % ','.join(sub_expressions)
        elif connector == '|':
            raise NotImplementedError("Bit-wise or is not supported in Oracle.")
        return super(DatabaseOperations, self).combine_expression(connector, sub_expressions)

    def _get_sequence_name(self, table):
        name_length = self.max_name_length() - 3
        return '%s_SQ' % util.truncate_name(table, name_length).upper()

    def _get_trigger_name(self, table):
        name_length = self.max_name_length() - 3
        return '%s_TR' % util.truncate_name(table, name_length).upper()

    def bulk_insert_sql(self, fields, num_values):
        items_sql = "SELECT %s FROM DUAL" % ", ".join(["%s"] * len(fields))
        return " UNION ALL ".join([items_sql] * num_values)


class _UninitializedOperatorsDescriptor(object):

    def __get__(self, instance, owner):
        # If connection.operators is looked up before a connection has been
        # created, transparently initialize connection.operators to avert an
        # AttributeError.
        if instance is None:
            raise AttributeError("operators not available as class attribute")
        # Creating a cursor will initialize the operators.
        instance.cursor().close()
        return instance.__dict__['operators']


class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = 'oracle'
    operators = _UninitializedOperatorsDescriptor()

    _standard_operators = {
        'exact': '= %s',
        'iexact': '= UPPER(%s)',
        'contains': "LIKE TRANSLATE(%s USING NCHAR_CS) ESCAPE TRANSLATE('\\' USING NCHAR_CS)",
        'icontains': "LIKE UPPER(TRANSLATE(%s USING NCHAR_CS)) ESCAPE TRANSLATE('\\' USING NCHAR_CS)",
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': "LIKE TRANSLATE(%s USING NCHAR_CS) ESCAPE TRANSLATE('\\' USING NCHAR_CS)",
        'endswith': "LIKE TRANSLATE(%s USING NCHAR_CS) ESCAPE TRANSLATE('\\' USING NCHAR_CS)",
        'istartswith': "LIKE UPPER(TRANSLATE(%s USING NCHAR_CS)) ESCAPE TRANSLATE('\\' USING NCHAR_CS)",
        'iendswith': "LIKE UPPER(TRANSLATE(%s USING NCHAR_CS)) ESCAPE TRANSLATE('\\' USING NCHAR_CS)",
    }

    _likec_operators = _standard_operators.copy()
    _likec_operators.update({
        'contains': "LIKEC %s ESCAPE '\\'",
        'icontains': "LIKEC UPPER(%s) ESCAPE '\\'",
        'startswith': "LIKEC %s ESCAPE '\\'",
        'endswith': "LIKEC %s ESCAPE '\\'",
        'istartswith': "LIKEC UPPER(%s) ESCAPE '\\'",
        'iendswith': "LIKEC UPPER(%s) ESCAPE '\\'",
    })

    Database = Database

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

        self.features = DatabaseFeatures(self)
        use_returning_into = self.settings_dict["OPTIONS"].get('use_returning_into', True)
        self.features.can_return_id_from_insert = use_returning_into
        self.ops = DatabaseOperations(self)
        self.client = DatabaseClient(self)
        self.creation = DatabaseCreation(self)
        self.introspection = DatabaseIntrospection(self)
        self.validation = BaseDatabaseValidation(self)

    def _connect_string(self):
        settings_dict = self.settings_dict
        if not settings_dict['HOST'].strip():
            settings_dict['HOST'] = 'localhost'
        if settings_dict['PORT'].strip():
            dsn = Database.makedsn(settings_dict['HOST'],
                                   int(settings_dict['PORT']),
                                   settings_dict['NAME'])
        else:
            dsn = settings_dict['NAME']
        return "%s/%s@%s" % (settings_dict['USER'],
                             settings_dict['PASSWORD'], dsn)

    def get_connection_params(self):
        conn_params = self.settings_dict['OPTIONS'].copy()
        if 'use_returning_into' in conn_params:
            del conn_params['use_returning_into']
        return conn_params

    def get_new_connection(self, conn_params):
        conn_string = convert_unicode(self._connect_string())
        return Database.connect(conn_string, **conn_params)

    def init_connection_state(self):
        cursor = self.create_cursor()
        # Set the territory first. The territory overrides NLS_DATE_FORMAT
        # and NLS_TIMESTAMP_FORMAT to the territory default. When all of
        # these are set in single statement it isn't clear what is supposed
        # to happen.
        cursor.execute("ALTER SESSION SET NLS_TERRITORY = 'AMERICA'")
        # Set oracle date to ansi date format.  This only needs to execute
        # once when we create a new connection. We also set the Territory
        # to 'AMERICA' which forces Sunday to evaluate to a '1' in
        # TO_CHAR().
        cursor.execute(
            "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'"
            " NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF'"
            + (" TIME_ZONE = 'UTC'" if settings.USE_TZ else ''))
        cursor.close()
        if 'operators' not in self.__dict__:
            # Ticket #14149: Check whether our LIKE implementation will
            # work for this connection or we need to fall back on LIKEC.
            # This check is performed only once per DatabaseWrapper
            # instance per thread, since subsequent connections will use
            # the same settings.
            cursor = self.create_cursor()
            try:
                cursor.execute("SELECT 1 FROM DUAL WHERE DUMMY %s"
                               % self._standard_operators['contains'],
                               ['X'])
            except DatabaseError:
                self.operators = self._likec_operators
            else:
                self.operators = self._standard_operators
            cursor.close()

        # There's no way for the DatabaseOperations class to know the
        # currently active Oracle version, so we do some setups here.
        # TODO: Multi-db support will need a better solution (a way to
        # communicate the current version).
        if self.oracle_version is not None and self.oracle_version <= 9:
            self.ops.regex_lookup = self.ops.regex_lookup_9
        else:
            self.ops.regex_lookup = self.ops.regex_lookup_10

        try:
            self.connection.stmtcachesize = 20
        except:
            # Django docs specify cx_Oracle version 4.3.1 or higher, but
            # stmtcachesize is available only in 4.3.2 and up.
            pass

    def create_cursor(self):
        return FormatStylePlaceholderCursor(self.connection)

    def _commit(self):
        if self.connection is not None:
            try:
                return self.connection.commit()
            except Database.DatabaseError as e:
                # cx_Oracle 5.0.4 raises a cx_Oracle.DatabaseError exception
                # with the following attributes and values:
                #  code = 2091
                #  message = 'ORA-02091: transaction rolled back
                #            'ORA-02291: integrity constraint (TEST_DJANGOTEST.SYS
                #               _C00102056) violated - parent key not found'
                # We convert that particular case to our IntegrityError exception
                x = e.args[0]
                if hasattr(x, 'code') and hasattr(x, 'message') \
                   and x.code == 2091 and 'ORA-02291' in x.message:
                    six.reraise(utils.IntegrityError, utils.IntegrityError(*tuple(e.args)), sys.exc_info()[2])
                raise

    # Oracle doesn't support savepoint commits.  Ignore them.
    def _savepoint_commit(self, sid):
        pass

    def _set_autocommit(self, autocommit):
        with self.wrap_database_errors:
            self.connection.autocommit = autocommit

    def check_constraints(self, table_names=None):
        """
        To check constraints, we set constraints to immediate. Then, when, we're done we must ensure they
        are returned to deferred.
        """
        self.cursor().execute('SET CONSTRAINTS ALL IMMEDIATE')
        self.cursor().execute('SET CONSTRAINTS ALL DEFERRED')

    def is_usable(self):
        try:
            if hasattr(self.connection, 'ping'):    # Oracle 10g R2 and higher
                self.connection.ping()
            else:
                # Use a cx_Oracle cursor directly, bypassing Django's utilities.
                self.connection.cursor().execute("SELECT 1 FROM DUAL")
        except Database.Error:
            return False
        else:
            return True

    @cached_property
    def oracle_version(self):
        with self.temporary_connection():
            version = self.connection.version
        try:
            return int(version.split('.')[0])
        except ValueError:
            return None


class OracleParam(object):
    """
    Wrapper object for formatting parameters for Oracle. If the string
    representation of the value is large enough (greater than 4000 characters)
    the input size needs to be set as CLOB. Alternatively, if the parameter
    has an `input_size` attribute, then the value of the `input_size` attribute
    will be used instead. Otherwise, no input size will be set for the
    parameter when executing the query.
    """

    def __init__(self, param, cursor, strings_only=False):
        # With raw SQL queries, datetimes can reach this function
        # without being converted by DateTimeField.get_db_prep_value.
        if settings.USE_TZ and (isinstance(param, datetime.datetime) and
                                not isinstance(param, Oracle_datetime)):
            if timezone.is_naive(param):
                warnings.warn("Oracle received a naive datetime (%s)"
                              " while time zone support is active." % param,
                              RuntimeWarning)
                default_timezone = timezone.get_default_timezone()
                param = timezone.make_aware(param, default_timezone)
            param = Oracle_datetime.from_datetime(param.astimezone(timezone.utc))

        # Oracle doesn't recognize True and False correctly in Python 3.
        # The conversion done below works both in 2 and 3.
        if param is True:
            param = "1"
        elif param is False:
            param = "0"
        if hasattr(param, 'bind_parameter'):
            self.force_bytes = param.bind_parameter(cursor)
        elif isinstance(param, six.memoryview):
            self.force_bytes = param
        else:
            self.force_bytes = convert_unicode(param, cursor.charset,
                                             strings_only)
        if hasattr(param, 'input_size'):
            # If parameter has `input_size` attribute, use that.
            self.input_size = param.input_size
        elif isinstance(param, six.string_types) and len(param) > 1000:
            # Mark any string param greater than 1000 characters as a CLOB.
            # loaddata does not convert long strings < 4000 to required CLOB type, so reduce to 1000
            self.input_size = Database.CLOB
        else:
            self.input_size = None


class VariableWrapper(object):
    """
    An adapter class for cursor variables that prevents the wrapped object
    from being converted into a string when used to instanciate an OracleParam.
    This can be used generally for any other object that should be passed into
    Cursor.execute as-is.
    """

    def __init__(self, var):
        self.var = var

    def bind_parameter(self, cursor):
        return self.var

    def __getattr__(self, key):
        return getattr(self.var, key)

    def __setattr__(self, key, value):
        if key == 'var':
            self.__dict__[key] = value
        else:
            setattr(self.var, key, value)


class InsertIdVar(object):
    """
    A late-binding cursor variable that can be passed to Cursor.execute
    as a parameter, in order to receive the id of the row created by an
    insert statement.
    """

    def bind_parameter(self, cursor):
        param = cursor.cursor.var(Database.NUMBER)
        cursor._insert_id_var = param
        return param


class FormatStylePlaceholderCursor(object):
    """
    Django uses "format" (e.g. '%s') style placeholders, but Oracle uses ":var"
    style. This fixes it -- but note that if you want to use a literal "%s" in
    a query, you'll need to use "%%s".

    We also do automatic conversion between Unicode on the Python side and
    UTF-8 -- for talking to Oracle -- in here.
    """
    charset = 'utf-8'

    def __init__(self, connection):
        self.cursor = connection.cursor()
        # Necessary to retrieve decimal values without rounding error.
        self.cursor.numbersAsStrings = True
        # Default arraysize of 1 is highly sub-optimal.
        self.cursor.arraysize = 100

    def _format_params(self, params):
        try:
            return dict((k,OracleParam(v, self, True)) for k,v in params.items())
        except AttributeError:
            return tuple([OracleParam(p, self, True) for p in params])

    def _guess_input_sizes(self, params_list):
        # Try dict handling; if that fails, treat as sequence
        if hasattr(params_list[0], 'keys'):
            sizes = {}
            for params in params_list:
                for k, value in params.items():
                    if value.input_size:
                        sizes[k] = value.input_size
            self.setinputsizes(**sizes)
        else:
            # It's not a list of dicts; it's a list of sequences
            sizes = [None] * len(params_list[0])
            for params in params_list:
                for i, value in enumerate(params):
                    if value.input_size:
                        sizes[i] = value.input_size
            self.setinputsizes(*sizes)

    def _param_generator(self, params):
        # Try dict handling; if that fails, treat as sequence
        if hasattr(params, 'items'):
            return dict((k, v.force_bytes) for k,v in params.items())
        else:
            return [p.force_bytes for p in params]

    def _fix_for_params(self, query, params):
        # cx_Oracle wants no trailing ';' for SQL statements.  For PL/SQL, it
        # it does want a trailing ';' but not a trailing '/'.  However, these
        # characters must be included in the original query in case the query
        # is being passed to SQL*Plus.
        if query.endswith(';') or query.endswith('/'):
            query = query[:-1]
        if params is None:
            params = []
            query = convert_unicode(query, self.charset)
        elif hasattr(params, 'keys'):
            # Handle params as dict
            args = dict((k, ":%s"%k) for k in params.keys())
            query = convert_unicode(query % args, self.charset)
        else:
            # Handle params as sequence
            args = [(':arg%d' % i) for i in range(len(params))]
            query = convert_unicode(query % tuple(args), self.charset)
        return query, self._format_params(params)

    def execute(self, query, params=None):
        query, params = self._fix_for_params(query, params)
        self._guess_input_sizes([params])
        try:
            return self.cursor.execute(query, self._param_generator(params))
        except Database.DatabaseError as e:
            # cx_Oracle <= 4.4.0 wrongly raises a DatabaseError for ORA-01400.
            if hasattr(e.args[0], 'code') and e.args[0].code == 1400 and not isinstance(e, IntegrityError):
                six.reraise(utils.IntegrityError, utils.IntegrityError(*tuple(e.args)), sys.exc_info()[2])
            raise

    def executemany(self, query, params=None):
        if not params:
            # No params given, nothing to do
            return None
        # uniform treatment for sequences and iterables
        params_iter = iter(params)
        query, firstparams = self._fix_for_params(query, next(params_iter))
        # we build a list of formatted params; as we're going to traverse it
        # more than once, we can't make it lazy by using a generator
        formatted = [firstparams]+[self._format_params(p) for p in params_iter]
        self._guess_input_sizes(formatted)
        try:
            return self.cursor.executemany(query,
                                [self._param_generator(p) for p in formatted])
        except Database.DatabaseError as e:
            # cx_Oracle <= 4.4.0 wrongly raises a DatabaseError for ORA-01400.
            if hasattr(e.args[0], 'code') and e.args[0].code == 1400 and not isinstance(e, IntegrityError):
                six.reraise(utils.IntegrityError, utils.IntegrityError(*tuple(e.args)), sys.exc_info()[2])
            raise

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return row
        return _rowfactory(row, self.cursor)

    def fetchmany(self, size=None):
        if size is None:
            size = self.arraysize
        return tuple([_rowfactory(r, self.cursor)
                      for r in self.cursor.fetchmany(size)])

    def fetchall(self):
        return tuple([_rowfactory(r, self.cursor)
                      for r in self.cursor.fetchall()])

    def var(self, *args):
        return VariableWrapper(self.cursor.var(*args))

    def arrayvar(self, *args):
        return VariableWrapper(self.cursor.arrayvar(*args))

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)

    def __iter__(self):
        return CursorIterator(self.cursor)


class CursorIterator(six.Iterator):

    """Cursor iterator wrapper that invokes our custom row factory."""

    def __init__(self, cursor):
        self.cursor = cursor
        self.iter = iter(cursor)

    def __iter__(self):
        return self

    def __next__(self):
        return _rowfactory(next(self.iter), self.cursor)


def _rowfactory(row, cursor):
    # Cast numeric values as the appropriate Python type based upon the
    # cursor description, and convert strings to unicode.
    casted = []
    for value, desc in zip(row, cursor.description):
        if value is not None and desc[1] is Database.NUMBER:
            precision, scale = desc[4:6]
            if scale == -127:
                if precision == 0:
                    # NUMBER column: decimal-precision floating point
                    # This will normally be an integer from a sequence,
                    # but it could be a decimal value.
                    if '.' in value:
                        value = decimal.Decimal(value)
                    else:
                        value = int(value)
                else:
                    # FLOAT column: binary-precision floating point.
                    # This comes from FloatField columns.
                    value = float(value)
            elif precision > 0:
                # NUMBER(p,s) column: decimal-precision fixed point.
                # This comes from IntField and DecimalField columns.
                if scale == 0:
                    value = int(value)
                else:
                    value = decimal.Decimal(value)
            elif '.' in value:
                # No type information. This normally comes from a
                # mathematical expression in the SELECT list. Guess int
                # or Decimal based on whether it has a decimal point.
                value = decimal.Decimal(value)
            else:
                value = int(value)
        # datetimes are returned as TIMESTAMP, except the results
        # of "dates" queries, which are returned as DATETIME.
        elif desc[1] in (Database.TIMESTAMP, Database.DATETIME):
            # Confirm that dt is naive before overwriting its tzinfo.
            if settings.USE_TZ and value is not None and timezone.is_naive(value):
                value = value.replace(tzinfo=timezone.utc)
        elif desc[1] in (Database.STRING, Database.FIXED_CHAR,
                         Database.LONG_STRING):
            value = to_unicode(value)
        casted.append(value)
    return tuple(casted)


def to_unicode(s):
    """
    Convert strings to Unicode objects (and return all other data types
    unchanged).
    """
    if isinstance(s, six.string_types):
        return force_text(s)
    return s


def _get_sequence_reset_sql():
    # TODO: colorize this SQL code with style.SQL_KEYWORD(), etc.
    return """
DECLARE
    table_value integer;
    seq_value integer;
BEGIN
    SELECT NVL(MAX(%(column)s), 0) INTO table_value FROM %(table)s;
    SELECT NVL(last_number - cache_size, 0) INTO seq_value FROM user_sequences
           WHERE sequence_name = '%(sequence)s';
    WHILE table_value > seq_value LOOP
        SELECT "%(sequence)s".nextval INTO seq_value FROM dual;
    END LOOP;
END;
/"""
