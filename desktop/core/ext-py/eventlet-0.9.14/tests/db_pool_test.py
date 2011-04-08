"Test cases for db_pool"
import sys
import os
import traceback
from unittest import TestCase, main

from tests import skipped, skip_unless, skip_with_pyevent, get_database_auth
from eventlet import event
from eventlet import db_pool
import eventlet


class DBTester(object):
    __test__ = False  # so that nose doesn't try to execute this directly
    def setUp(self):
        self.create_db()
        self.connection = None
        connection = self._dbmodule.connect(**self._auth)
        cursor = connection.cursor()
        cursor.execute("""CREATE  TABLE gargleblatz
        (
        a INTEGER
        );""")
        connection.commit()
        cursor.close()

    def tearDown(self):
        if self.connection:
            self.connection.close()
        self.drop_db()

    def set_up_dummy_table(self, connection=None):
        close_connection = False
        if connection is None:
            close_connection = True
            if self.connection is None:
                connection = self._dbmodule.connect(**self._auth)
            else:
                connection = self.connection

        cursor = connection.cursor()
        cursor.execute(self.dummy_table_sql)
        connection.commit()
        cursor.close()
        if close_connection:
            connection.close()

# silly mock class
class Mock(object):
    pass


class DBConnectionPool(DBTester):
    __test__ = False  # so that nose doesn't try to execute this directly
    def setUp(self):
        super(DBConnectionPool, self).setUp()
        self.pool = self.create_pool()
        self.connection = self.pool.get()

    def tearDown(self):
        if self.connection:
            self.pool.put(self.connection)
        self.pool.clear()
        super(DBConnectionPool, self).tearDown()

    def assert_cursor_works(self, cursor):
        cursor.execute("select 1")
        rows = cursor.fetchall()
        self.assert_(rows)

    def test_connecting(self):
        self.assert_(self.connection is not None)

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
            self.assert_(False)
        except AssertionError:
            raise
        except Exception:
            pass
        cursor.close()

    def test_put_none(self):
        # the pool is of size 1, and its only connection is out
        self.assert_(self.pool.free() == 0)
        self.pool.put(None)
        # ha ha we fooled it into thinking that we had a dead process
        self.assert_(self.pool.free() == 1)
        conn2 = self.pool.get()
        self.assert_(conn2 is not None)
        self.assert_(conn2.cursor)
        self.pool.put(conn2)

    def test_close_does_a_put(self):
        self.assert_(self.pool.free() == 0)
        self.connection.close()
        self.assert_(self.pool.free() == 1)
        self.assertRaises(AttributeError, self.connection.cursor)

    @skipped
    def test_deletion_does_a_put(self):
        # doing a put on del causes some issues if __del__ is called in the
        # main coroutine, so, not doing that for now
        self.assert_(self.pool.free() == 0)
        self.connection = None
        self.assert_(self.pool.free() == 1)

    def test_put_doesnt_double_wrap(self):
        self.pool.put(self.connection)
        conn = self.pool.get()
        self.assert_(not isinstance(conn._base, db_pool.PooledConnectionWrapper))
        self.pool.put(conn)

    def test_bool(self):
        self.assert_(self.connection)
        self.connection.close()
        self.assert_(not self.connection)

    def fill_up_table(self, conn):
        curs = conn.cursor()
        for i in range(1000):
            curs.execute('insert into test_table (value_int) values (%s)' % i)
        conn.commit()

    def test_returns_immediately(self):
        self.pool = self.create_pool()
        conn = self.pool.get()
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
        self.pool.put(conn)

    def test_connection_is_clean_after_put(self):
        self.pool = self.create_pool()
        conn = self.pool.get()
        self.set_up_dummy_table(conn)
        curs = conn.cursor()
        for i in range(10):
            curs.execute('insert into test_table (value_int) values (%s)' % i)
        # do not commit  :-)
        self.pool.put(conn)
        del conn
        conn2 = self.pool.get()
        curs2 = conn2.cursor()
        for i in range(10):
            curs2.execute('insert into test_table (value_int) values (%s)' % i)
        conn2.commit()
        curs2.execute("select * from test_table")
        # we should have only inserted them once
        self.assertEqual(10, curs2.rowcount)
        self.pool.put(conn2)

    def test_visibility_from_other_connections(self):
        self.pool = self.create_pool(3)
        conn = self.pool.get()
        conn2 = self.pool.get()
        curs = conn.cursor()
        try:
            curs2 = conn2.cursor()
            curs2.execute("insert into gargleblatz (a) values (%s)" % (314159))
            self.assertEqual(curs2.rowcount, 1)
            conn2.commit()
            selection_query = "select * from gargleblatz"
            curs2.execute(selection_query)
            self.assertEqual(curs2.rowcount, 1)
            del curs2
            self.pool.put(conn2)
            # create a new connection, it should see the addition
            conn3 = self.pool.get()
            curs3 = conn3.cursor()
            curs3.execute(selection_query)
            self.assertEqual(curs3.rowcount, 1)
            # now, does the already-open connection see it?
            curs.execute(selection_query)
            self.assertEqual(curs.rowcount, 1)
            self.pool.put(conn3)
        finally:
            # clean up my litter
            curs.execute("delete from gargleblatz where a=314159")
            conn.commit()
            self.pool.put(conn)

    @skipped
    def test_two_simultaneous_connections(self):
        # timing-sensitive test, disabled until we come up with a better
        # way to do this
        self.pool = self.create_pool(2)
        conn = self.pool.get()
        self.set_up_dummy_table(conn)
        self.fill_up_table(conn)
        curs = conn.cursor()
        conn2 = self.pool.get()
        self.set_up_dummy_table(conn2)
        self.fill_up_table(conn2)
        curs2 = conn2.cursor()
        results = []
        LONG_QUERY = "select * from test_table"
        SHORT_QUERY = "select * from test_table where row_id <= 20"

        evt = event.Event()
        def long_running_query():
            self.assert_cursor_works(curs)
            curs.execute(LONG_QUERY)
            results.append(1)
            evt.send()
        evt2 = event.Event()
        def short_running_query():
            self.assert_cursor_works(curs2)
            curs2.execute(SHORT_QUERY)
            results.append(2)
            evt2.send()

        eventlet.spawn(long_running_query)
        eventlet.spawn(short_running_query)
        evt.wait()
        evt2.wait()
        results.sort()
        self.assertEqual([1, 2], results)

    def test_clear(self):
        self.pool = self.create_pool()
        self.pool.put(self.connection)
        self.pool.clear()
        self.assertEqual(len(self.pool.free_items), 0)

    def test_unwrap_connection(self):
        self.assert_(isinstance(self.connection,
                                db_pool.GenericConnectionWrapper))
        conn = self.pool._unwrap_connection(self.connection)
        self.assert_(not isinstance(conn, db_pool.GenericConnectionWrapper))

        self.assertEquals(None, self.pool._unwrap_connection(None))
        self.assertEquals(None, self.pool._unwrap_connection(1))

        # testing duck typing here -- as long as the connection has a
        # _base attribute, it should be unwrappable
        x = Mock()
        x._base = 'hi'
        self.assertEquals('hi', self.pool._unwrap_connection(x))
        conn.close()

    def test_safe_close(self):
        self.pool._safe_close(self.connection, quiet=True)
        self.assertEquals(len(self.pool.free_items), 1)

        self.pool._safe_close(None)
        self.pool._safe_close(1)

        # now we're really going for 100% coverage
        x = Mock()
        def fail():
            raise KeyboardInterrupt()
        x.close = fail
        self.assertRaises(KeyboardInterrupt, self.pool._safe_close, x)

        x = Mock()
        def fail2():
            raise RuntimeError("if this line has been printed, the test succeeded")
        x.close = fail2
        self.pool._safe_close(x, quiet=False)

    def test_zero_max_idle(self):
        self.pool.put(self.connection)
        self.pool.clear()
        self.pool = self.create_pool(max_size=2, max_idle=0)
        self.connection = self.pool.get()
        self.connection.close()
        self.assertEquals(len(self.pool.free_items), 0)

    def test_zero_max_age(self):
        self.pool.put(self.connection)
        self.pool.clear()
        self.pool = self.create_pool(max_size=2, max_age=0)
        self.connection = self.pool.get()
        self.connection.close()
        self.assertEquals(len(self.pool.free_items), 0)

    @skipped
    def test_max_idle(self):
        # This test is timing-sensitive.  Rename the function without
        # the "dont" to run it, but beware that it could fail or take
        # a while.

        self.pool = self.create_pool(max_size=2, max_idle=0.02)
        self.connection = self.pool.get()
        self.connection.close()
        self.assertEquals(len(self.pool.free_items), 1)
        eventlet.sleep(0.01)  # not long enough to trigger the idle timeout
        self.assertEquals(len(self.pool.free_items), 1)
        self.connection = self.pool.get()
        self.connection.close()
        self.assertEquals(len(self.pool.free_items), 1)
        eventlet.sleep(0.01)  # idle timeout should have fired but done nothing
        self.assertEquals(len(self.pool.free_items), 1)
        self.connection = self.pool.get()
        self.connection.close()
        self.assertEquals(len(self.pool.free_items), 1)
        eventlet.sleep(0.03) # long enough to trigger idle timeout for real
        self.assertEquals(len(self.pool.free_items), 0)

    @skipped
    def test_max_idle_many(self):
        # This test is timing-sensitive.  Rename the function without
        # the "dont" to run it, but beware that it could fail or take
        # a while.

        self.pool = self.create_pool(max_size=2, max_idle=0.02)
        self.connection, conn2 = self.pool.get(), self.pool.get()
        self.connection.close()
        eventlet.sleep(0.01)
        self.assertEquals(len(self.pool.free_items), 1)
        conn2.close()
        self.assertEquals(len(self.pool.free_items), 2)
        eventlet.sleep(0.02)  # trigger cleanup of conn1 but not conn2
        self.assertEquals(len(self.pool.free_items), 1)

    @skipped
    def test_max_age(self):
        # This test is timing-sensitive.  Rename the function without
        # the "dont" to run it, but beware that it could fail or take
        # a while.

        self.pool = self.create_pool(max_size=2, max_age=0.05)
        self.connection = self.pool.get()
        self.connection.close()
        self.assertEquals(len(self.pool.free_items), 1)
        eventlet.sleep(0.01)  # not long enough to trigger the age timeout
        self.assertEquals(len(self.pool.free_items), 1)
        self.connection = self.pool.get()
        self.connection.close()
        self.assertEquals(len(self.pool.free_items), 1)
        eventlet.sleep(0.05) # long enough to trigger age timeout
        self.assertEquals(len(self.pool.free_items), 0)

    @skipped
    def test_max_age_many(self):
        # This test is timing-sensitive.  Rename the function without
        # the "dont" to run it, but beware that it could fail or take
        # a while.

        self.pool = self.create_pool(max_size=2, max_age=0.15)
        self.connection, conn2 = self.pool.get(), self.pool.get()
        self.connection.close()
        self.assertEquals(len(self.pool.free_items), 1)
        eventlet.sleep(0)  # not long enough to trigger the age timeout
        self.assertEquals(len(self.pool.free_items), 1)
        eventlet.sleep(0.2) # long enough to trigger age timeout
        self.assertEquals(len(self.pool.free_items), 0)
        conn2.close()  # should not be added to the free items
        self.assertEquals(len(self.pool.free_items), 0)

    def test_waiters_get_woken(self):
        # verify that when there's someone waiting on an empty pool
        # and someone puts an immediately-closed connection back in
        # the pool that the waiter gets woken
        self.pool.put(self.connection)
        self.pool.clear()
        self.pool = self.create_pool(max_size=1, max_age=0)

        self.connection = self.pool.get()
        self.assertEquals(self.pool.free(), 0)
        self.assertEquals(self.pool.waiting(), 0)
        e = event.Event()
        def retrieve(pool, ev):
            c = pool.get()
            ev.send(c)
        eventlet.spawn(retrieve, self.pool, e)
        eventlet.sleep(0) # these two sleeps should advance the retrieve
        eventlet.sleep(0) # coroutine until it's waiting in get()
        self.assertEquals(self.pool.free(), 0)
        self.assertEquals(self.pool.waiting(), 1)
        self.pool.put(self.connection)
        timer = eventlet.Timeout(1)
        conn = e.wait()
        timer.cancel()
        self.assertEquals(self.pool.free(), 0)
        self.assertEquals(self.pool.waiting(), 0)
        self.pool.put(conn)

    @skipped
    def test_0_straight_benchmark(self):
        """ Benchmark; don't run unless you want to wait a while."""
        import time
        iterations = 20000
        c = self.connection.cursor()
        self.connection.commit()
        def bench(c):
            for i in xrange(iterations):
                c.execute('select 1')

        bench(c)  # warm-up
        results = []
        for i in xrange(3):
            start = time.time()
            bench(c)
            end = time.time()
            results.append(end-start)

        print "\n%u iterations took an average of %f seconds, (%s) in %s\n" % (
            iterations, sum(results)/len(results), results, type(self))

    def test_raising_create(self):
        # if the create() method raises an exception the pool should
        # not lose any connections
        self.pool = self.create_pool(max_size=1, module=RaisingDBModule())
        self.assertRaises(RuntimeError, self.pool.get)
        self.assertEquals(self.pool.free(), 1)


class RaisingDBModule(object):
    def connect(self, *args, **kw):
        raise RuntimeError()


class TpoolConnectionPool(DBConnectionPool):
    __test__ = False  # so that nose doesn't try to execute this directly
    def create_pool(self, max_size=1, max_idle=10, max_age=10,
                    connect_timeout=0.5, module=None):
        if module is None:
            module = self._dbmodule
        return db_pool.TpooledConnectionPool(module,
            min_size=0, max_size=max_size,
            max_idle=max_idle, max_age=max_age,
            connect_timeout = connect_timeout,
            **self._auth)


    @skip_with_pyevent
    def setUp(self):
        super(TpoolConnectionPool, self).setUp()

    def tearDown(self):
        super(TpoolConnectionPool, self).tearDown()
        from eventlet import tpool
        tpool.killall()



class RawConnectionPool(DBConnectionPool):
    __test__ = False  # so that nose doesn't try to execute this directly
    def create_pool(self, max_size=1, max_idle=10, max_age=10,
                    connect_timeout=0.5, module=None):
        if module is None:
            module = self._dbmodule
        return db_pool.RawConnectionPool(module,
            min_size=0, max_size=max_size,
            max_idle=max_idle, max_age=max_age,
            connect_timeout=connect_timeout,
            **self._auth)

get_auth = get_database_auth

def mysql_requirement(_f):
    verbose = os.environ.get('eventlet_test_mysql_verbose')
    try:
        import MySQLdb
        try:
            auth = get_auth()['MySQLdb'].copy()
            MySQLdb.connect(**auth)
            return True
        except MySQLdb.OperationalError:
            if verbose:
                print >> sys.stderr, ">> Skipping mysql tests, error when connecting:"
                traceback.print_exc()
            return False
    except ImportError:
        if verbose:
            print >> sys.stderr, ">> Skipping mysql tests, MySQLdb not importable"
        return False

class MysqlConnectionPool(object):
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

    @skip_unless(mysql_requirement)
    def setUp(self):
        import MySQLdb
        self._dbmodule = MySQLdb
        self._auth = get_auth()['MySQLdb']
        super(MysqlConnectionPool, self).setUp()

    def tearDown(self):
        super(MysqlConnectionPool, self).tearDown()

    def create_db(self):
        auth = self._auth.copy()
        try:
            self.drop_db()
        except Exception:
            pass
        dbname = 'test%s' % os.getpid()
        db = self._dbmodule.connect(**auth).cursor()
        db.execute("create database "+dbname)
        db.close()
        self._auth['db'] = dbname
        del db

    def drop_db(self):
        db = self._dbmodule.connect(**self._auth).cursor()
        db.execute("drop database "+self._auth['db'])
        db.close()
        del db


class Test01MysqlTpool(MysqlConnectionPool, TpoolConnectionPool, TestCase):
    __test__ = True

class Test02MysqlRaw(MysqlConnectionPool, RawConnectionPool, TestCase):
    __test__ = True

def postgres_requirement(_f):
    try:
        import psycopg2
        try:
            auth = get_auth()['psycopg2'].copy()
            psycopg2.connect(**auth)
            return True
        except psycopg2.OperationalError:
            print "Skipping postgres tests, error when connecting"
            return False
    except ImportError:
        print "Skipping postgres tests, psycopg2 not importable"
        return False


class Psycopg2ConnectionPool(object):
    dummy_table_sql = """CREATE TEMPORARY TABLE test_table
        (
        row_id SERIAL PRIMARY KEY,
        value_int INTEGER,
        value_float FLOAT,
        value_string VARCHAR(200),
        value_uuid CHAR(36),
        value_binary BYTEA,
        value_binary_string BYTEA,
        created TIMESTAMP
        );"""

    @skip_unless(postgres_requirement)
    def setUp(self):
        import psycopg2
        self._dbmodule = psycopg2
        self._auth = get_auth()['psycopg2']
        super(Psycopg2ConnectionPool, self).setUp()

    def tearDown(self):
        super(Psycopg2ConnectionPool, self).tearDown()

    def create_db(self):
        dbname = 'test%s' % os.getpid()
        self._auth['database'] = dbname
        try:
            self.drop_db()
        except Exception:
            pass
        auth = self._auth.copy()
        auth.pop('database')  # can't create if you're connecting to it
        conn = self._dbmodule.connect(**auth)
        conn.set_isolation_level(0)
        db = conn.cursor()
        db.execute("create database "+dbname)
        db.close()
        del db

    def drop_db(self):
        auth = self._auth.copy()
        auth.pop('database')  # can't drop database we connected to
        conn = self._dbmodule.connect(**auth)
        conn.set_isolation_level(0)
        db = conn.cursor()
        db.execute("drop database "+self._auth['database'])
        db.close()
        del db

class Test01Psycopg2Tpool(Psycopg2ConnectionPool, TpoolConnectionPool, TestCase):
    __test__ = True

class Test02Psycopg2Raw(Psycopg2ConnectionPool, RawConnectionPool, TestCase):
    __test__ = True

if __name__ == '__main__':
    main()
