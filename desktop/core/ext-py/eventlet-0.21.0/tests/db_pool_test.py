from __future__ import print_function
import os
import sys
import traceback

from eventlet import db_pool
from eventlet.support import six
import eventlet
import eventlet.tpool
import tests
import tests.mock

psycopg2 = None
try:
    import psycopg2
    import psycopg2.extensions
except ImportError:
    pass

MySQLdb = None
try:
    import MySQLdb
except ImportError:
    pass


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
        connection.close()

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
        assert rows

    def test_connecting(self):
        assert self.connection is not None

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

    def test_put_none(self):
        # the pool is of size 1, and its only connection is out
        assert self.pool.free() == 0
        self.pool.put(None)
        # ha ha we fooled it into thinking that we had a dead process
        assert self.pool.free() == 1
        conn2 = self.pool.get()
        assert conn2 is not None
        assert conn2.cursor
        self.pool.put(conn2)

    def test_close_does_a_put(self):
        assert self.pool.free() == 0
        self.connection.close()
        assert self.pool.free() == 1
        self.assertRaises(AttributeError, self.connection.cursor)

    def test_put_doesnt_double_wrap(self):
        self.pool.put(self.connection)
        conn = self.pool.get()
        assert not isinstance(conn._base, db_pool.PooledConnectionWrapper)
        self.pool.put(conn)

    def test_bool(self):
        assert self.connection
        self.connection.close()
        assert not self.connection

    def fill_up_table(self, conn):
        curs = conn.cursor()
        for i in six.moves.range(1000):
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
        evt = eventlet.Event()

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
        self.pool = self.create_pool(max_size=3)
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

    def test_clear(self):
        self.pool = self.create_pool()
        self.pool.put(self.connection)
        self.pool.clear()
        self.assertEqual(len(self.pool.free_items), 0)

    def test_clear_warmup(self):
        """Clear implicitly created connections (min_size > 0)"""
        self.pool = self.create_pool(min_size=1)
        self.pool.clear()
        self.assertEqual(len(self.pool.free_items), 0)

    def test_unwrap_connection(self):
        self.assert_(isinstance(self.connection,
                                db_pool.GenericConnectionWrapper))
        conn = self.pool._unwrap_connection(self.connection)
        assert not isinstance(conn, db_pool.GenericConnectionWrapper)

        self.assertEqual(None, self.pool._unwrap_connection(None))
        self.assertEqual(None, self.pool._unwrap_connection(1))

        # testing duck typing here -- as long as the connection has a
        # _base attribute, it should be unwrappable
        x = Mock()
        x._base = 'hi'
        self.assertEqual('hi', self.pool._unwrap_connection(x))
        conn.close()

    def test_safe_close(self):
        self.pool._safe_close(self.connection, quiet=True)
        self.assertEqual(len(self.pool.free_items), 1)

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
        self.assertEqual(len(self.pool.free_items), 0)

    def test_zero_max_age(self):
        self.pool.put(self.connection)
        self.pool.clear()
        self.pool = self.create_pool(max_size=2, max_age=0)
        self.connection = self.pool.get()
        self.connection.close()
        self.assertEqual(len(self.pool.free_items), 0)

    def test_waiters_get_woken(self):
        # verify that when there's someone waiting on an empty pool
        # and someone puts an immediately-closed connection back in
        # the pool that the waiter gets woken
        self.pool.put(self.connection)
        self.pool.clear()
        self.pool = self.create_pool(max_size=1, max_age=0)

        self.connection = self.pool.get()
        self.assertEqual(self.pool.free(), 0)
        self.assertEqual(self.pool.waiting(), 0)
        e = eventlet.Event()

        def retrieve(pool, ev):
            c = pool.get()
            ev.send(c)
        eventlet.spawn(retrieve, self.pool, e)
        eventlet.sleep(0)  # these two sleeps should advance the retrieve
        eventlet.sleep(0)  # coroutine until it's waiting in get()
        self.assertEqual(self.pool.free(), 0)
        self.assertEqual(self.pool.waiting(), 1)
        self.pool.put(self.connection)
        timer = eventlet.Timeout(1)
        conn = e.wait()
        timer.cancel()
        self.assertEqual(self.pool.free(), 0)
        self.assertEqual(self.pool.waiting(), 0)
        self.pool.put(conn)

    def test_raising_create(self):
        # if the create() method raises an exception the pool should
        # not lose any connections
        self.pool = self.create_pool(max_size=1, module=RaisingDBModule())
        self.assertRaises(RuntimeError, self.pool.get)
        self.assertEqual(self.pool.free(), 1)


class DummyConnection(object):
    def rollback(self):
        pass


class DummyDBModule(object):
    def connect(self, *args, **kwargs):
        return DummyConnection()


class RaisingDBModule(object):
    def connect(self, *args, **kw):
        raise RuntimeError()


class TpoolConnectionPool(DBConnectionPool):
    __test__ = False  # so that nose doesn't try to execute this directly

    def create_pool(self, min_size=0, max_size=1, max_idle=10, max_age=10,
                    connect_timeout=0.5, module=None):
        if module is None:
            module = self._dbmodule
        return db_pool.TpooledConnectionPool(
            module,
            min_size=min_size, max_size=max_size,
            max_idle=max_idle, max_age=max_age,
            connect_timeout=connect_timeout,
            **self._auth)

    @tests.skip_with_pyevent
    def setUp(self):
        super(TpoolConnectionPool, self).setUp()

    def tearDown(self):
        super(TpoolConnectionPool, self).tearDown()
        eventlet.tpool.killall()


class RawConnectionPool(DBConnectionPool):
    __test__ = False  # so that nose doesn't try to execute this directly

    def create_pool(self, min_size=0, max_size=1, max_idle=10, max_age=10,
                    connect_timeout=0.5, module=None):
        if module is None:
            module = self._dbmodule
        return db_pool.RawConnectionPool(
            module,
            min_size=min_size, max_size=max_size,
            max_idle=max_idle, max_age=max_age,
            connect_timeout=connect_timeout,
            **self._auth)


def test_raw_pool_issue_125():
    # pool = self.create_pool(min_size=3, max_size=5)
    pool = db_pool.RawConnectionPool(
        DummyDBModule(),
        dsn="dbname=test user=jessica port=5433",
        min_size=3, max_size=5)
    conn = pool.get()
    pool.put(conn)


def test_raw_pool_custom_cleanup_ok():
    cleanup_mock = tests.mock.Mock()
    pool = db_pool.RawConnectionPool(DummyDBModule(), cleanup=cleanup_mock)
    conn = pool.get()
    pool.put(conn)
    assert cleanup_mock.call_count == 1

    with pool.item() as conn:
        pass
    assert cleanup_mock.call_count == 2


def test_raw_pool_custom_cleanup_arg_error():
    cleanup_mock = tests.mock.Mock(side_effect=NotImplementedError)
    pool = db_pool.RawConnectionPool(DummyDBModule())
    conn = pool.get()
    pool.put(conn, cleanup=cleanup_mock)
    assert cleanup_mock.call_count == 1

    with pool.item(cleanup=cleanup_mock):
        pass
    assert cleanup_mock.call_count == 2


def test_raw_pool_custom_cleanup_fatal():
    state = [0]

    def cleanup(conn):
        state[0] += 1
        raise KeyboardInterrupt

    pool = db_pool.RawConnectionPool(DummyDBModule(), cleanup=cleanup)
    conn = pool.get()
    try:
        pool.put(conn)
    except KeyboardInterrupt:
        pass
    else:
        assert False, 'Expected KeyboardInterrupt'
    assert state[0] == 1


def test_raw_pool_clear_update_current_size():
    # https://github.com/eventlet/eventlet/issues/139
    # BaseConnectionPool.clear does not update .current_size.
    # That leads to situation when new connections could not be created.
    pool = db_pool.RawConnectionPool(DummyDBModule())
    pool.get().close()
    assert pool.current_size == 1
    assert len(pool.free_items) == 1
    pool.clear()
    assert pool.current_size == 0
    assert len(pool.free_items) == 0


def mysql_requirement(_f):
    verbose = os.environ.get('eventlet_test_mysql_verbose')
    if MySQLdb is None:
        if verbose:
            print(">> Skipping mysql tests, MySQLdb not importable", file=sys.stderr)
        return False

    try:
        auth = tests.get_database_auth()['MySQLdb'].copy()
        MySQLdb.connect(**auth)
        return True
    except MySQLdb.OperationalError:
        if verbose:
            print(">> Skipping mysql tests, error when connecting:", file=sys.stderr)
            traceback.print_exc()
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

    @tests.skip_unless(mysql_requirement)
    def setUp(self):
        self._dbmodule = MySQLdb
        self._auth = tests.get_database_auth()['MySQLdb']
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
        db.execute("create database " + dbname)
        db.close()
        self._auth['db'] = dbname
        del db

    def drop_db(self):
        db = self._dbmodule.connect(**self._auth).cursor()
        db.execute("drop database " + self._auth['db'])
        db.close()
        del db


class Test01MysqlTpool(MysqlConnectionPool, TpoolConnectionPool, tests.LimitedTestCase):
    __test__ = True


class Test02MysqlRaw(MysqlConnectionPool, RawConnectionPool, tests.LimitedTestCase):
    __test__ = True


def postgres_requirement(_f):
    if psycopg2 is None:
        print("Skipping postgres tests, psycopg2 not importable")
        return False

    try:
        auth = tests.get_database_auth()['psycopg2'].copy()
        psycopg2.connect(**auth)
        return True
    except psycopg2.OperationalError:
        print("Skipping postgres tests, error when connecting")
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

    @tests.skip_unless(postgres_requirement)
    def setUp(self):
        self._dbmodule = psycopg2
        self._auth = tests.get_database_auth()['psycopg2']
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
        db.execute("create database " + dbname)
        db.close()
        conn.close()

    def drop_db(self):
        auth = self._auth.copy()
        auth.pop('database')  # can't drop database we connected to
        conn = self._dbmodule.connect(**auth)
        conn.set_isolation_level(0)
        db = conn.cursor()
        db.execute("drop database " + self._auth['database'])
        db.close()
        conn.close()


class TestPsycopg2Base(tests.LimitedTestCase):
    __test__ = False

    def test_cursor_works_as_context_manager(self):
        with self.connection.cursor() as c:
            c.execute('select 1')
            row = c.fetchone()
            assert row == (1,)

    def test_set_isolation_level(self):
        self.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)


class Test01Psycopg2Tpool(Psycopg2ConnectionPool, TpoolConnectionPool, TestPsycopg2Base):
    __test__ = True


class Test02Psycopg2Raw(Psycopg2ConnectionPool, RawConnectionPool, TestPsycopg2Base):
    __test__ = True
