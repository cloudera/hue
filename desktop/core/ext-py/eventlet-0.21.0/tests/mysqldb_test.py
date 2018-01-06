from __future__ import print_function

import os
import time
import traceback

import eventlet
from eventlet import event
try:
    from eventlet.green import MySQLdb
except ImportError:
    MySQLdb = False
import tests
from tests import skip_unless, using_pyevent, get_database_auth


def mysql_requirement(_f):
    """We want to skip tests if using pyevent, MySQLdb is not installed, or if
    there is no database running on the localhost that the auth file grants
    us access to.

    This errs on the side of skipping tests if everything is not right, but
    it's better than a million tests failing when you don't care about mysql
    support."""
    if using_pyevent(_f):
        return False
    if MySQLdb is False:
        print("Skipping mysql tests, MySQLdb not importable")
        return False
    try:
        auth = get_database_auth()['MySQLdb'].copy()
        MySQLdb.connect(**auth)
        return True
    except MySQLdb.OperationalError:
        print("Skipping mysql tests, error when connecting:")
        traceback.print_exc()
        return False


class TestMySQLdb(tests.LimitedTestCase):
    def setUp(self):
        self._auth = get_database_auth()['MySQLdb']
        self.create_db()
        self.connection = None
        self.connection = MySQLdb.connect(**self._auth)
        cursor = self.connection.cursor()
        cursor.execute("""CREATE TABLE gargleblatz
        (
        a INTEGER
        );""")
        self.connection.commit()
        cursor.close()

        super(TestMySQLdb, self).setUp()

    def tearDown(self):
        if self.connection:
            self.connection.close()
        self.drop_db()

        super(TestMySQLdb, self).tearDown()

    @skip_unless(mysql_requirement)
    def create_db(self):
        auth = self._auth.copy()
        try:
            self.drop_db()
        except Exception:
            pass
        dbname = 'test_%d_%d' % (os.getpid(), int(time.time() * 1000))
        db = MySQLdb.connect(**auth).cursor()
        db.execute("create database " + dbname)
        db.close()
        self._auth['db'] = dbname
        del db

    def drop_db(self):
        db = MySQLdb.connect(**self._auth).cursor()
        db.execute("drop database " + self._auth['db'])
        db.close()
        del db

    def set_up_dummy_table(self, connection=None):
        close_connection = False
        if connection is None:
            close_connection = True
            if self.connection is None:
                connection = MySQLdb.connect(**self._auth)
            else:
                connection = self.connection

        cursor = connection.cursor()
        cursor.execute(self.dummy_table_sql)
        connection.commit()
        cursor.close()
        if close_connection:
            connection.close()

    dummy_table_sql = """CREATE TEMPORARY TABLE test_table
        (
        row_id INTEGER PRIMARY KEY AUTO_INCREMENT,
        value_int INTEGER,
        value_float FLOAT,
        value_string VARCHAR(200),
        value_uuid CHAR(36),
        value_binary BLOB,
        value_binary_string VARCHAR(200) BINARY,
        value_enum ENUM('Y','N'),
        created TIMESTAMP
        ) ENGINE=InnoDB;"""

    def assert_cursor_yields(self, curs):
        counter = [0]

        def tick():
            while True:
                counter[0] += 1
                eventlet.sleep()
        gt = eventlet.spawn(tick)
        curs.execute("select 1")
        rows = curs.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(rows[0]), 1)
        self.assertEqual(rows[0][0], 1)
        assert counter[0] > 0, counter[0]
        gt.kill()

    def assert_cursor_works(self, cursor):
        cursor.execute("select 1")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(rows[0]), 1)
        self.assertEqual(rows[0][0], 1)
        self.assert_cursor_yields(cursor)

    def assert_connection_works(self, conn):
        curs = conn.cursor()
        self.assert_cursor_works(curs)

    def test_module_attributes(self):
        import MySQLdb as orig
        for key in dir(orig):
            if key not in ('__author__', '__path__', '__revision__',
                           '__version__', '__loader__'):
                assert hasattr(MySQLdb, key), "%s %s" % (key, getattr(orig, key))

    def test_connecting(self):
        assert self.connection is not None

    def test_connecting_annoyingly(self):
        self.assert_connection_works(MySQLdb.Connect(**self._auth))
        self.assert_connection_works(MySQLdb.Connection(**self._auth))
        self.assert_connection_works(MySQLdb.connections.Connection(**self._auth))

    def test_create_cursor(self):
        cursor = self.connection.cursor()
        cursor.close()

    def test_run_query(self):
        cursor = self.connection.cursor()
        self.assert_cursor_works(cursor)
        cursor.close()

    def test_run_bad_query(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute("garbage blah blah")
            assert False
        except AssertionError:
            raise
        except Exception:
            pass
        cursor.close()

    def fill_up_table(self, conn):
        curs = conn.cursor()
        for i in range(1000):
            curs.execute('insert into test_table (value_int) values (%s)' % i)
        conn.commit()

    def test_yields(self):
        conn = self.connection
        self.set_up_dummy_table(conn)
        self.fill_up_table(conn)
        curs = conn.cursor()
        results = []
        SHORT_QUERY = "select * from test_table"
        evt = event.Event()

        def a_query():
            self.assert_cursor_works(curs)
            curs.execute(SHORT_QUERY)
            results.append(2)
            evt.send()
        eventlet.spawn(a_query)
        results.append(1)
        self.assertEqual([1], results)
        evt.wait()
        self.assertEqual([1, 2], results)

    def test_visibility_from_other_connections(self):
        conn = MySQLdb.connect(**self._auth)
        conn2 = MySQLdb.connect(**self._auth)
        curs = conn.cursor()
        try:
            curs2 = conn2.cursor()
            curs2.execute("insert into gargleblatz (a) values (%s)" % (314159))
            self.assertEqual(curs2.rowcount, 1)
            conn2.commit()
            selection_query = "select * from gargleblatz"
            curs2.execute(selection_query)
            self.assertEqual(curs2.rowcount, 1)
            del curs2, conn2
            # create a new connection, it should see the addition
            conn3 = MySQLdb.connect(**self._auth)
            curs3 = conn3.cursor()
            curs3.execute(selection_query)
            self.assertEqual(curs3.rowcount, 1)
            # now, does the already-open connection see it?
            curs.execute(selection_query)
            self.assertEqual(curs.rowcount, 1)
            del curs3, conn3
        finally:
            # clean up my litter
            curs.execute("delete from gargleblatz where a=314159")
            conn.commit()


class TestMonkeyPatch(tests.LimitedTestCase):
    @skip_unless(mysql_requirement)
    def test_monkey_patching(self):
        tests.run_isolated('mysqldb_monkey_patch.py')
