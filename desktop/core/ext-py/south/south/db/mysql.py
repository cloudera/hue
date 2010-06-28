
from django.db import connection
from django.conf import settings
from south.db import generic

class DatabaseOperations(generic.DatabaseOperations):

    """
    MySQL implementation of database operations.
    
    MySQL is an 'interesting' database; it has no DDL transaction support,
    among other things. This can confuse people when they ask how they can
    roll back - hence the dry runs, etc., found in the migration code.
    Alex agrees, and Alex is always right.
    [19:06] <Alex_Gaynor> Also, I want to restate once again that MySQL is a special database
    
    (Still, if you want a key-value store with relational tendancies, go MySQL!)
    """
    
    backend_name = "mysql"
    alter_string_set_type = ''
    alter_string_set_null = 'MODIFY %(column)s %(type)s NULL;'
    alter_string_drop_null = 'MODIFY %(column)s %(type)s NOT NULL;'
    drop_index_string = 'DROP INDEX %(index_name)s ON %(table_name)s'
    delete_primary_key_sql = "ALTER TABLE %(table)s DROP PRIMARY KEY"
    delete_foreign_key_sql = "ALTER TABLE %(table)s DROP FOREIGN KEY %(constraint)s"
    allows_combined_alters = False
    has_ddl_transactions = False
    has_check_constraints = False
    delete_unique_sql = "ALTER TABLE %s DROP INDEX %s"
    
    
    def connection_init(self):
        """
        Run before any SQL to let database-specific config be sent as a command,
        e.g. which storage engine (MySQL) or transaction serialisability level.
        """
        cursor = self._get_connection().cursor()
        if self._has_setting('STORAGE_ENGINE') and self._get_setting('STORAGE_ENGINE'):
            cursor.execute("SET storage_engine=%s;" % self._get_setting('STORAGE_ENGINE'))
        # Turn off foreign key checks, and turn them back on at the end
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        self.deferred_sql.append("SET FOREIGN_KEY_CHECKS=1;")

    
    def rename_column(self, table_name, old, new):
        if old == new or self.dry_run:
            return []
        
        rows = [x for x in self.execute('DESCRIBE %s' % (self.quote_name(table_name),)) if x[0] == old]
        
        if not rows:
            raise ValueError("No column '%s' in '%s'." % (old, table_name))
        
        params = (
            self.quote_name(table_name),
            self.quote_name(old),
            self.quote_name(new),
            rows[0][1],
            rows[0][2] == "YES" and "NULL" or "NOT NULL",
            rows[0][4] and "DEFAULT " or "",
            rows[0][4] and "%s" or "",
            rows[0][5] or "",
        )
        
        sql = 'ALTER TABLE %s CHANGE COLUMN %s %s %s %s %s %s %s;' % params
        
        if rows[0][4]:
            self.execute(sql, (rows[0][4],))
        else:
            self.execute(sql)
    
    
    def delete_column(self, table_name, name):
        db_name = self._get_setting('NAME')
        
        # See if there is a foreign key on this column
        cursor = self._get_connection().cursor()
        get_fkeyname_query = "SELECT tc.constraint_name FROM \
                              information_schema.table_constraints tc, \
                              information_schema.key_column_usage kcu \
                              WHERE tc.table_name=kcu.table_name \
                              AND tc.table_schema=kcu.table_schema \
                              AND tc.constraint_name=kcu.constraint_name \
                              AND tc.constraint_type='FOREIGN KEY' \
                              AND tc.table_schema='%s' \
                              AND tc.table_name='%s' \
                              AND kcu.column_name='%s'"

        result = cursor.execute(get_fkeyname_query % (db_name, table_name, name))
        
        # If a foreign key exists, we need to delete it first
        if result > 0:
            assert result == 1 # We should only have one result, otherwise there's Issues
            fkey_name = cursor.fetchone()[0]
            drop_query = "ALTER TABLE %s DROP FOREIGN KEY %s"
            cursor.execute(drop_query % (self.quote_name(table_name), self.quote_name(fkey_name)))

        super(DatabaseOperations, self).delete_column(table_name, name)

    
    def rename_table(self, old_table_name, table_name):
        """
        Renames the table 'old_table_name' to 'table_name'.
        """
        if old_table_name == table_name:
            # No Operation
            return
        params = (self.quote_name(old_table_name), self.quote_name(table_name))
        self.execute('RENAME TABLE %s TO %s;' % params)
    
    
    def _constraints_affecting_columns(self, table_name, columns, type="UNIQUE"):
        """
        Gets the names of the constraints affecting the given columns.
        If columns is None, returns all constraints of the type on the table.
        """
        
        if self.dry_run:
            raise ValueError("Cannot get constraints for columns during a dry run.")
        
        if columns is not None:
            columns = set(columns)
        
        db_name = self._get_setting('NAME')
        
        # First, load all constraint->col mappings for this table.
        rows = self.execute("""
            SELECT kc.constraint_name, kc.column_name
            FROM information_schema.key_column_usage AS kc
            JOIN information_schema.table_constraints AS c ON
                kc.table_schema = c.table_schema AND
                kc.table_name = c.table_name AND
                kc.constraint_name = c.constraint_name
            WHERE
                kc.table_schema = %s AND
                kc.table_catalog IS NULL AND
                kc.table_name = %s AND
                c.constraint_type = %s
        """, [db_name, table_name, type])
        
        # Load into a dict
        mapping = {}
        for constraint, column in rows:
            mapping.setdefault(constraint, set())
            mapping[constraint].add(column)
        
        # Find ones affecting these columns
        for constraint, itscols in mapping.items():
            if itscols == columns or columns is None:
                yield constraint
    
    
    def _field_sanity(self, field):
        """
        This particular override stops us sending DEFAULTs for BLOB/TEXT columns.
        """
        if self._db_type_for_alter_column(field).upper() in ["BLOB", "TEXT", "LONGTEXT"]:
            field._suppress_default = True
        return field
