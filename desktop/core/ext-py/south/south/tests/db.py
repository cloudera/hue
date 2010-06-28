import unittest

from south.db import db
from django.db import connection, models

# Create a list of error classes from the various database libraries
errors = []
try:
    from psycopg2 import ProgrammingError
    errors.append(ProgrammingError)
except ImportError:
    pass
errors = tuple(errors)

class TestOperations(unittest.TestCase):

    """
    Tests if the various DB abstraction calls work.
    Can only test a limited amount due to DB differences.
    """

    def setUp(self):
        db.debug = False
        db.clear_deferred_sql()
        db.start_transaction()
    
    def tearDown(self):
        db.rollback_transaction()

    def test_create(self):
        """
        Test creation of tables.
        """
        cursor = connection.cursor()
        # It needs to take at least 2 args
        self.assertRaises(TypeError, db.create_table)
        self.assertRaises(TypeError, db.create_table, "test1")
        # Empty tables (i.e. no columns) are not fine, so make at least 1
        db.create_table("test1", [('email_confirmed', models.BooleanField(default=False))])
        # And should exist
        cursor.execute("SELECT * FROM test1")
        # Make sure we can't do the same query on an empty table
        try:
            cursor.execute("SELECT * FROM nottheretest1")
            self.fail("Non-existent table could be selected!")
        except:
            pass
    
    def test_delete(self):
        """
        Test deletion of tables.
        """
        db.create_table("test_deltable", [('email_confirmed', models.BooleanField(default=False))])
        db.delete_table("test_deltable")
        # Make sure it went
        try:
            cursor.execute("SELECT * FROM test1")
            self.fail("Just-deleted table could be selected!")
        except:
            pass
    
    def test_nonexistent_delete(self):
        """
        Test deletion of nonexistent tables.
        """
        try:
            db.delete_table("test_nonexistdeltable")
            self.fail("Non-existent table could be deleted!")
        except:
            pass
    
    def test_foreign_keys(self):
        """
        Tests foreign key creation, especially uppercase (see #61)
        """
        Test = db.mock_model(model_name='Test', db_table='test5a',
                             db_tablespace='', pk_field_name='ID',
                             pk_field_type=models.AutoField, pk_field_args=[])
        db.create_table("test5a", [('ID', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True))])
        db.create_table("test5b", [
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('UNIQUE', models.ForeignKey(Test)),
        ])
        db.execute_deferred_sql()
    
    def test_rename(self):
        """
        Test column renaming
        """
        cursor = connection.cursor()
        db.create_table("test_rn", [('spam', models.BooleanField(default=False))])
        # Make sure we can select the column
        cursor.execute("SELECT spam FROM test_rn")
        # Rename it
        db.rename_column("test_rn", "spam", "eggs")
        cursor.execute("SELECT eggs FROM test_rn")
        db.commit_transaction()
        db.start_transaction()
        try:
            cursor.execute("SELECT spam FROM test_rn")
            self.fail("Just-renamed column could be selected!")
        except:
            pass
        db.rollback_transaction()
        db.delete_table("test_rn")
        db.start_transaction()
    
    def test_dry_rename(self):
        """
        Test column renaming while --dry-run is turned on (should do nothing)
        See ticket #65
        """
        cursor = connection.cursor()
        db.create_table("test_drn", [('spam', models.BooleanField(default=False))])
        # Make sure we can select the column
        cursor.execute("SELECT spam FROM test_drn")
        # Rename it
        db.dry_run = True
        db.rename_column("test_drn", "spam", "eggs")
        db.dry_run = False
        cursor.execute("SELECT spam FROM test_drn")
        db.commit_transaction()
        db.start_transaction()
        try:
            cursor.execute("SELECT eggs FROM test_drn")
            self.fail("Dry-renamed new column could be selected!")
        except:
            pass
        db.rollback_transaction()
        db.delete_table("test_drn")
        db.start_transaction()
    
    def test_table_rename(self):
        """
        Test column renaming
        """
        cursor = connection.cursor()
        db.create_table("testtr", [('spam', models.BooleanField(default=False))])
        # Make sure we can select the column
        cursor.execute("SELECT spam FROM testtr")
        # Rename it
        db.rename_table("testtr", "testtr2")
        cursor.execute("SELECT spam FROM testtr2")
        db.commit_transaction()
        db.start_transaction()
        try:
            cursor.execute("SELECT spam FROM testtr")
            self.fail("Just-renamed column could be selected!")
        except:
            pass
        db.rollback_transaction()
        db.delete_table("testtr2")
        db.start_transaction()
    
    def test_percents_in_defaults(self):
        """
        Test that % in a default gets escaped to %%.
        """
        cursor = connection.cursor()
        try:
            db.create_table("testpind", [('cf', models.CharField(max_length=255, default="It should be 2%!"))])
        except IndexError:
            self.fail("% was not properly escaped in column SQL.")
        db.delete_table("testpind")
    
    def test_index(self):
        """
        Test the index operations
        """
        db.create_table("test3", [
            ('SELECT', models.BooleanField(default=False)),
            ('eggs', models.IntegerField(unique=True)),
        ])
        db.execute_deferred_sql()
        # Add an index on that column
        db.create_index("test3", ["SELECT"])
        # Add another index on two columns
        db.create_index("test3", ["SELECT", "eggs"])
        # Delete them both
        db.delete_index("test3", ["SELECT"])
        db.delete_index("test3", ["SELECT", "eggs"])
        # Delete the unique index/constraint
        if db.backend_name != "sqlite3":
            db.delete_unique("test3", ["eggs"])
        db.delete_table("test3")
    
    def test_primary_key(self):
        """
        Test the primary key operations
        """
        
        # SQLite backend doesn't support this yet.
        if db.backend_name == "sqlite3":
            return
        
        db.create_table("test_pk", [
            ('id', models.IntegerField(primary_key=True)),
            ('new_pkey', models.IntegerField()),
            ('eggs', models.IntegerField(unique=True)),
        ])
        db.execute_deferred_sql()
        # Remove the default primary key, and make eggs it
        db.drop_primary_key("test_pk")
        db.create_primary_key("test_pk", "new_pkey")
        # Try inserting a now-valid row pair
        db.execute("INSERT INTO test_pk (id, new_pkey, eggs) VALUES (1, 2, 3)")
        db.execute("INSERT INTO test_pk (id, new_pkey, eggs) VALUES (1, 3, 4)")
        db.delete_table("test_pk")
    
    def test_add_columns(self):
        """
        Test adding columns
        """
        db.create_table("test_addc", [
            ('spam', models.BooleanField(default=False)),
            ('eggs', models.IntegerField()),
        ])
        # Add a column
        db.add_column("test_addc", "add1", models.IntegerField(default=3), keep_default=False)
        # Add a FK with keep_default=False (#69)
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        db.add_column("test_addc", "user", models.ForeignKey(User, null=True), keep_default=False)
        db.delete_column("test_addc", "add1")
        db.delete_table("test_addc")
    
    def test_alter_columns(self):
        """
        Test altering columns
        """
        db.create_table("test_alterc", [
            ('spam', models.BooleanField(default=False)),
            ('eggs', models.IntegerField()),
        ])
        # Change eggs to be a FloatField
        db.alter_column("test_alterc", "eggs", models.FloatField())
        db.delete_table("test_alterc")
        
    def test_alter_column_postgres_multiword(self):
        """
        Tests altering columns with multiple words in Postgres types (issue #125)
        e.g. 'datetime with time zone', look at django/db/backends/postgresql/creation.py
        """
        db.create_table("test_multiword", [
            ('col_datetime', models.DateTimeField(null=True)),
            ('col_integer', models.PositiveIntegerField(null=True)),
            ('col_smallint', models.PositiveSmallIntegerField(null=True)),
            ('col_float', models.FloatField(null=True)),
        ])
        
        # test if 'double precision' is preserved
        db.alter_column('test_multiword', 'col_float', models.FloatField('float', null=True))

        # test if 'CHECK ("%(column)s" >= 0)' is stripped
        db.alter_column('test_multiword', 'col_integer', models.PositiveIntegerField(null=True))
        db.alter_column('test_multiword', 'col_smallint', models.PositiveSmallIntegerField(null=True))

        # test if 'with timezone' is preserved
        if db.backend_name == "postgres":
            db.execute("INSERT INTO test_multiword (col_datetime) VALUES ('2009-04-24 14:20:55+02')")
            db.alter_column('test_multiword', 'col_datetime', models.DateTimeField(auto_now=True))
            assert db.execute("SELECT col_datetime = '2009-04-24 14:20:55+02' FROM test_multiword")[0][0]

        db.delete_table("test_multiword")
    
    def test_alter_constraints(self):
        """
        Tests that going from a PostiveIntegerField to an IntegerField drops
        the constraint on the database.
        """
        # Only applies to databases that support CHECK constraints
        if not db.has_check_constraints:
            return
        # Make the test table
        db.create_table("test_alterc", [
            ('num', models.PositiveIntegerField()),
        ])
        # Add in some test values
        db.execute("INSERT INTO test_alterc (num) VALUES (1)")
        db.execute("INSERT INTO test_alterc (num) VALUES (2)")
        # Ensure that adding a negative number is bad
        db.commit_transaction()
        db.start_transaction()
        try:
            db.execute("INSERT INTO test_alterc (num) VALUES (-3)")
        except:
            db.rollback_transaction()
        else:
            self.fail("Could insert a negative integer into a PositiveIntegerField.")
        # Alter it to a normal IntegerField
        db.alter_column("test_alterc", "num", models.IntegerField())
        # It should now work
        db.execute("INSERT INTO test_alterc (num) VALUES (-3)")
        db.delete_table("test_alterc")
        # We need to match up for tearDown
        db.start_transaction()
    
    def test_unique(self):
        """
        Tests creating/deleting unique constraints.
        """
        
        # SQLite backend doesn't support this yet.
        if db.backend_name == "sqlite3":
            return
        
        db.create_table("test_unique2", [
            ('id', models.AutoField(primary_key=True)),
        ])
        db.create_table("test_unique", [
            ('spam', models.BooleanField(default=False)),
            ('eggs', models.IntegerField()),
            ('ham', models.ForeignKey(db.mock_model('Unique2', 'test_unique2'))),
        ])
        # Add a constraint
        db.create_unique("test_unique", ["spam"])
        # Shouldn't do anything during dry-run
        db.dry_run = True
        db.delete_unique("test_unique", ["spam"])
        db.dry_run = False
        db.delete_unique("test_unique", ["spam"])
        db.create_unique("test_unique", ["spam"])
        db.commit_transaction()
        db.start_transaction()
        
        # Test it works
        db.execute("INSERT INTO test_unique2 (id) VALUES (1)")
        db.execute("INSERT INTO test_unique2 (id) VALUES (2)")
        db.execute("INSERT INTO test_unique (spam, eggs, ham_id) VALUES (true, 0, 1)")
        db.execute("INSERT INTO test_unique (spam, eggs, ham_id) VALUES (false, 1, 2)")
        try:
            db.execute("INSERT INTO test_unique (spam, eggs, ham_id) VALUES (true, 2, 1)")
        except:
            db.rollback_transaction()
        else:
            self.fail("Could insert non-unique item.")
        
        # Drop that, add one only on eggs
        db.delete_unique("test_unique", ["spam"])
        db.execute("DELETE FROM test_unique")
        db.create_unique("test_unique", ["eggs"])
        db.start_transaction()
        
        # Test similarly
        db.execute("INSERT INTO test_unique (spam, eggs, ham_id) VALUES (true, 0, 1)")
        db.execute("INSERT INTO test_unique (spam, eggs, ham_id) VALUES (false, 1, 2)")
        try:
            db.execute("INSERT INTO test_unique (spam, eggs, ham_id) VALUES (true, 1, 1)")
        except:
            db.rollback_transaction()
        else:
            self.fail("Could insert non-unique item.")
        
        # Drop those, test combined constraints
        db.delete_unique("test_unique", ["eggs"])
        db.execute("DELETE FROM test_unique")
        db.create_unique("test_unique", ["spam", "eggs", "ham_id"])
        db.start_transaction()
        # Test similarly
        db.execute("INSERT INTO test_unique (spam, eggs, ham_id) VALUES (true, 0, 1)")
        db.execute("INSERT INTO test_unique (spam, eggs, ham_id) VALUES (false, 1, 1)")
        try:
            db.execute("INSERT INTO test_unique (spam, eggs, ham_id) VALUES (true, 0, 1)")
        except:
            db.rollback_transaction()
        else:
            self.fail("Could insert non-unique pair.")
        db.delete_unique("test_unique", ["spam", "eggs", "ham_id"])
        db.start_transaction()
    
    def test_capitalised_constraints(self):
        """
        Under PostgreSQL at least, capitalised constrains must be quoted.
        """
        db.create_table("test_capconst", [
            ('SOMECOL', models.PositiveIntegerField(primary_key=True)),
        ])
        # Alter it so it's not got the check constraint
        db.alter_column("test_capconst", "SOMECOL", models.IntegerField())
    
    def test_text_default(self):
        """
        MySQL cannot have blank defaults on TEXT columns.
        """
        db.create_table("test_textdef", [
            ('textcol', models.TextField(blank=True)),
        ])
    
    def test_add_unique_fk(self):
        """
        Test adding a ForeignKey with unique=True or a OneToOneField
        """
        db.create_table("test_add_unique_fk", [
            ('spam', models.BooleanField(default=False))
        ])
        
        db.add_column("test_add_unique_fk", "mock1", models.ForeignKey(db.mock_model('Mock', 'mock'), null=True, unique=True))
        db.add_column("test_add_unique_fk", "mock2", models.OneToOneField(db.mock_model('Mock', 'mock'), null=True))
        
        db.delete_table("test_add_unique_fk")
