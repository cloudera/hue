import os.path
import re
import cx_Oracle

from django.db import connection, models
from django.db.backends.util import truncate_name
from django.core.management.color import no_style
from django.db.backends.oracle.base import get_sequence_name
from django.db.models.fields import NOT_PROVIDED
from south.db import generic

print " ! WARNING: South's Oracle support is still alpha."
print " !          Be wary of posible bugs."

class DatabaseOperations(generic.DatabaseOperations):    
    """
    Oracle implementation of database operations.    
    """
    backend_name = 'oracle'

    alter_string_set_type =     'ALTER TABLE %(table_name)s MODIFY "%(column)s" %(type)s %(nullity)s;'
    alter_string_set_default =  'ALTER TABLE %(table_name)s MODIFY "%(column)s" DEFAULT %(default)s;'
    add_column_string =         'ALTER TABLE %s ADD %s;'
    delete_column_string =      'ALTER TABLE %s DROP COLUMN %s;'

    allows_combined_alters = False
    
    constraits_dict = {
        'PRIMARY KEY': 'P',
        'UNIQUE': 'U',
        'CHECK': 'C',
        'REFERENCES': 'R'
    }
    table_names_cache = set()

    def adj_column_sql(self, col):
        col = re.sub('(?P<constr>CHECK \(.*\))(?P<any>.*)(?P<default>DEFAULT [0|1])', 
                     lambda mo: '%s %s%s'%(mo.group('default'), mo.group('constr'), mo.group('any')), col) #syntax fix for boolean field only
        col = re.sub('(?P<not_null>NOT NULL) (?P<default>DEFAULT.+)',
                     lambda mo: '%s %s'%(mo.group('default'), mo.group('not_null')), col) #fix order  of DEFAULT and NOT NULL
        return col

    def check_m2m(self, table_name):
        m2m_table_name = table_name
        existing_tables = []

        if not self.table_names_cache:
            self.check_meta(table_name)
            self.table_names_cache = set(connection.introspection.table_names())
        tn = table_name.rsplit('_', 1)

        while len(tn) == 2:
            tn2qn = self.quote_name(tn[0], upper = False, check_m2m = False) 
            if tn2qn in self.table_names_cache:
                m2m_table_name = table_name.replace(tn[0], tn2qn)
                break
            else:
                if not existing_tables:
                    existing_tables = connection.introspection.table_names()
                if tn2qn in existing_tables:
                    m2m_table_name = table_name.replace(tn[0], tn2qn)
                    break
            tn = tn[0].rsplit('_', 1)

        self.table_names_cache.add(m2m_table_name)
        return m2m_table_name

    def check_meta(self, table_name):
        return table_name in [ m._meta.db_table for m in models.get_models() ] #caching provided by Django

    def quote_name(self, name, upper=True, column = False, check_m2m = True):
        if not column:
            if check_m2m:
                name = self.check_m2m(name)
            if self.check_meta(name): #replication of Django flow for models where Meta.db_table is set by user
                name = name.upper()
        tn = truncate_name(name, connection.ops.max_name_length())

        return upper and tn.upper() or tn.lower()

    def create_table(self, table_name, fields): 
        qn = self.quote_name(table_name, upper = False)
        qn_upper = qn.upper()
        columns = []
        autoinc_sql = ''

        for field_name, field in fields:
            col = self.column_sql(qn_upper, field_name, field)
            if not col:
                continue
            col = self.adj_column_sql(col)

            columns.append(col)
            if isinstance(field, models.AutoField):
                autoinc_sql = connection.ops.autoinc_sql(self.check_meta(table_name) and table_name or qn, field_name)

        sql = 'CREATE TABLE %s (%s);' % (qn_upper, ', '.join([col for col in columns]))
        self.execute(sql)
        if autoinc_sql:
            self.execute(autoinc_sql[0])
            self.execute(autoinc_sql[1])

    def delete_table(self, table_name, cascade=True):
        qn = self.quote_name(table_name, upper = False)

        if cascade:
            self.execute('DROP TABLE %s CASCADE CONSTRAINTS PURGE;' % qn.upper())
        else:
            self.execute('DROP TABLE %s;' % qn.upper())
        self.execute('DROP SEQUENCE %s;'%get_sequence_name(qn))

    def alter_column(self, table_name, name, field, explicit_name=True):
        qn = self.quote_name(table_name)

        # hook for the field to do any resolution prior to it's attributes being queried
        if hasattr(field, 'south_init'):
            field.south_init()
        field = self._field_sanity(field)

        # Add _id or whatever if we need to
        field.set_attributes_from_name(name)
        if not explicit_name:
            name = field.column
        qn_col = self.quote_name(name, column = True)

        # First, change the type
        params = {
            'table_name':qn,
            'column': qn_col,
            'type': self._db_type_for_alter_column(field),
            'nullity': 'NOT NULL',
            'default': 'NULL'
        }
        if field.null:
            params['nullity'] = ''
        sqls = [self.alter_string_set_type % params]

        if not field.null and field.has_default():
            params['default'] = field.get_default()

        sqls.append(self.alter_string_set_default % params)

        #UNIQUE constraint
        unique_constraint = list(self._constraints_affecting_columns(qn, [qn_col]))

        if field.unique and not unique_constraint:
            self.create_unique(qn, [qn_col])
        elif not field.unique and unique_constraint:
            self.delete_unique(qn, [qn_col])

        #CHECK constraint is not handled

        for sql in sqls:
            try:
                self.execute(sql)
            except cx_Oracle.DatabaseError, exc:
                if str(exc).find('ORA-01442') == -1:
                    raise

    def add_column(self, table_name, name, field, keep_default=True):
        qn = self.quote_name(table_name, upper = False)
        sql = self.column_sql(qn, name, field)
        sql = self.adj_column_sql(sql)

        if sql:
            params = (
                qn.upper(),
                sql
            )
            sql = self.add_column_string % params
            self.execute(sql)

            # Now, drop the default if we need to
            if not keep_default and field.default is not None:
                field.default = NOT_PROVIDED
                self.alter_column(table_name, name, field, explicit_name=False)

    def delete_column(self, table_name, name):
        return super(DatabaseOperations, self).delete_column(self.quote_name(table_name), name)

    def _field_sanity(self, field):
        """
        This particular override stops us sending DEFAULTs for BooleanField.
        """
        if isinstance(field, models.BooleanField) and field.has_default():
            field.default = int(field.to_python(field.get_default()))
        return field

    def _constraints_affecting_columns(self, table_name, columns, type='UNIQUE'):
        """
        Gets the names of the constraints affecting the given columns.
        """
        qn = self.quote_name

        if self.dry_run:
            raise ValueError("Cannot get constraints for columns during a dry run.")
        columns = set(columns)
        rows = self.execute("""
            SELECT user_cons_columns.constraint_name, user_cons_columns.column_name
            FROM user_constraints
            JOIN user_cons_columns ON
                 user_constraints.table_name = user_cons_columns.table_name AND 
                 user_constraints.constraint_name = user_cons_columns.constraint_name
            WHERE user_constraints.table_name = '%s' AND
                  user_constraints.constraint_type = '%s'
        """ % (qn(table_name), self.constraits_dict[type]))
        # Load into a dict
        mapping = {}
        for constraint, column in rows:
            mapping.setdefault(constraint, set())
            mapping[constraint].add(column)
        # Find ones affecting these columns
        for constraint, itscols in mapping.items():
            if itscols == columns:
                yield constraint