from django.db import connection
from django.db.models.fields import *
from south.db import generic

class DatabaseOperations(generic.DatabaseOperations):
    """
    django-pyodbc (sql_server.pyodbc) implementation of database operations.
    """
    
    backend_name = "pyodbc"
    
    add_column_string = 'ALTER TABLE %s ADD %s;'
    alter_string_set_type = 'ALTER COLUMN %(column)s %(type)s'
    alter_string_drop_null = 'ALTER COLUMN %(column)s %(type)s NOT NULL'
    allows_combined_alters = False

    drop_index_string = 'DROP INDEX %(index_name)s ON %(table_name)s'
    drop_constraint_string = 'ALTER TABLE %(table_name)s DROP CONSTRAINT %(constraint_name)s'
    delete_column_string = 'ALTER TABLE %s DROP COLUMN %s'


    def delete_column(self, table_name, name):
        q_table_name, q_name = (self.quote_name(table_name), self.quote_name(name))

        # Zap the indexes
        for ind in self._find_indexes_for_column(table_name,name):
            params = {'table_name':q_table_name, 'index_name': ind}
            sql = self.drop_index_string % params
            self.execute(sql, [])

        # Zap the constraints
        for const in self._find_constraints_for_column(table_name,name):
            params = {'table_name':q_table_name, 'constraint_name': const}
            sql = self.drop_constraint_string % params
            self.execute(sql, [])

        # Finally zap the column itself
        self.execute(self.delete_column_string % (q_table_name, q_name), [])

    def _find_indexes_for_column(self, table_name, name):
        "Find the indexes that apply to a column, needed when deleting"
        q_table_name, q_name = (self.quote_name(table_name), self.quote_name(name))

        sql = """
        SELECT si.name, si.id, sik.colid, sc.name
        FROM dbo.sysindexes SI WITH (NOLOCK)
        INNER JOIN dbo.sysindexkeys SIK WITH (NOLOCK)
            ON  SIK.id = Si.id
            AND SIK.indid = SI.indid
        INNER JOIN dbo.syscolumns SC WITH (NOLOCK)
            ON  SI.id = SC.id
            AND SIK.colid = SC.colid
        WHERE SI.indid !=0
            AND Si.id = OBJECT_ID('%s')
            AND SC.name = '%s'
        """
        idx = self.execute(sql % (table_name, name), [])
        return [i[0] for i in idx]

    def _find_constraints_for_column(self, table_name, name):
        "Find the constraints that apply to a column, needed when deleting"
        q_table_name, q_name = (self.quote_name(table_name), self.quote_name(name))

        sql = """
        SELECT  
            Cons.xtype, 
            Cons.id, 
            Cons.[name]
        FROM dbo.sysobjects AS Cons WITH(NOLOCK)
        INNER JOIN (
            SELECT [id], colid, name
            FROM dbo.syscolumns WITH(NOLOCK)
            WHERE id = OBJECT_ID('%s')
            AND name = '%s'
        ) AS Cols
            ON  Cons.parent_obj = Cols.id
        WHERE Cons.parent_obj = OBJECT_ID('%s')
        AND (
            (OBJECTPROPERTY(Cons.[id],'IsConstraint') = 1
                 AND Cons.info = Cols.colid)
             OR (OBJECTPROPERTY(Cons.[id],'IsForeignKey') = 1
                 AND LEFT(Cons.name,%d) = '%s')
        )
        """
        cons = self.execute(sql % (table_name, name, table_name, len(name), name), [])
        return [c[2] for c in cons]


    def drop_column_default_sql(self, table_name, name, q_name):
        "MSSQL specific drop default, which is a pain"

        sql = """
        SELECT object_name(cdefault)
        FROM syscolumns
        WHERE id = object_id('%s')
        AND name = '%s'
        """
        cons = self.execute(sql % (table_name, name), [])
        if cons and cons[0] and cons[0][0]:
            return "DROP CONSTRAINT %s" % cons[0][0]
        return None

    def _fix_field_definition(self, field):
        if isinstance(field, BooleanField):
            if field.default == True:
                field.default = 1
            if field.default == False:
                field.default = 0

    def add_column(self, table_name, name, field, keep_default=True):
        self._fix_field_definition(field)
        generic.DatabaseOperations.add_column(self, table_name, name, field, keep_default)

    def create_table(self, table_name, fields):
        # Tweak stuff as needed
        for name,f in fields:
            self._fix_field_definition(f)

        # Run
        generic.DatabaseOperations.create_table(self, table_name, fields)

    def rename_column(self, table_name, old, new):
        """
        Renames the column of 'table_name' from 'old' to 'new'.
        WARNING - This isn't transactional on MSSQL!
        """
        if old == new:
            # No Operation
            return
        # Examples on the MS site show the table name not being quoted...
        params = (table_name, self.quote_name(old), self.quote_name(new))
        self.execute("EXEC sp_rename '%s.%s', %s, 'COLUMN'" % params)

    def rename_table(self, old_table_name, table_name):
        """
        Renames the table 'old_table_name' to 'table_name'.
        WARNING - This isn't transactional on MSSQL!
        """
        if old_table_name == table_name:
            # No Operation
            return
        params = (self.quote_name(old_table_name), self.quote_name(table_name))
        self.execute('EXEC sp_rename %s, %s' % params)
