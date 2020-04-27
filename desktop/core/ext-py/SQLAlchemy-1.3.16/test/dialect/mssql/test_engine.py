# -*- encoding: utf-8
from sqlalchemy import Column
from sqlalchemy import engine_from_config
from sqlalchemy import event
from sqlalchemy import exc
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import testing
from sqlalchemy.dialects.mssql import adodbapi
from sqlalchemy.dialects.mssql import base
from sqlalchemy.dialects.mssql import pymssql
from sqlalchemy.dialects.mssql import pyodbc
from sqlalchemy.engine import url
from sqlalchemy.testing import assert_raises_message
from sqlalchemy.testing import assert_warnings
from sqlalchemy.testing import engines
from sqlalchemy.testing import eq_
from sqlalchemy.testing import expect_warnings
from sqlalchemy.testing import fixtures
from sqlalchemy.testing.mock import Mock


class ParseConnectTest(fixtures.TestBase):
    def test_pyodbc_connect_dsn_trusted(self):
        dialect = pyodbc.dialect()
        u = url.make_url("mssql://mydsn")
        connection = dialect.create_connect_args(u)
        eq_([["dsn=mydsn;Trusted_Connection=Yes"], {}], connection)

    def test_pyodbc_connect_old_style_dsn_trusted(self):
        dialect = pyodbc.dialect()
        u = url.make_url("mssql:///?dsn=mydsn")
        connection = dialect.create_connect_args(u)
        eq_([["dsn=mydsn;Trusted_Connection=Yes"], {}], connection)

    def test_pyodbc_connect_dsn_non_trusted(self):
        dialect = pyodbc.dialect()
        u = url.make_url("mssql://username:password@mydsn")
        connection = dialect.create_connect_args(u)
        eq_([["dsn=mydsn;UID=username;PWD=password"], {}], connection)

    def test_pyodbc_connect_dsn_extra(self):
        dialect = pyodbc.dialect()
        u = url.make_url(
            "mssql://username:password@mydsn/?LANGUAGE=us_" "english&foo=bar"
        )
        connection = dialect.create_connect_args(u)
        dsn_string = connection[0][0]
        assert ";LANGUAGE=us_english" in dsn_string
        assert ";foo=bar" in dsn_string

    def test_pyodbc_hostname(self):
        dialect = pyodbc.dialect()
        u = url.make_url(
            "mssql://username:password@hostspec/database?driver=SQL+Server"
        )
        connection = dialect.create_connect_args(u)
        eq_(
            [
                [
                    "DRIVER={SQL Server};Server=hostspec;Database=database;UI"
                    "D=username;PWD=password"
                ],
                {},
            ],
            connection,
        )

    def test_pyodbc_host_no_driver(self):
        dialect = pyodbc.dialect()
        u = url.make_url("mssql://username:password@hostspec/database")

        def go():
            return dialect.create_connect_args(u)

        connection = assert_warnings(
            go,
            [
                "No driver name specified; this is expected by "
                "PyODBC when using DSN-less connections"
            ],
        )

        eq_(
            [
                [
                    "Server=hostspec;Database=database;UI"
                    "D=username;PWD=password"
                ],
                {},
            ],
            connection,
        )

    def test_pyodbc_connect_comma_port(self):
        dialect = pyodbc.dialect()
        u = url.make_url(
            "mssql://username:password@hostspec:12345/data"
            "base?driver=SQL Server"
        )
        connection = dialect.create_connect_args(u)
        eq_(
            [
                [
                    "DRIVER={SQL Server};Server=hostspec,12345;Database=datab"
                    "ase;UID=username;PWD=password"
                ],
                {},
            ],
            connection,
        )

    def test_pyodbc_connect_config_port(self):
        dialect = pyodbc.dialect()
        u = url.make_url(
            "mssql://username:password@hostspec/database?p"
            "ort=12345&driver=SQL+Server"
        )
        connection = dialect.create_connect_args(u)
        eq_(
            [
                [
                    "DRIVER={SQL Server};Server=hostspec;Database=database;UI"
                    "D=username;PWD=password;port=12345"
                ],
                {},
            ],
            connection,
        )

    def test_pyodbc_extra_connect(self):
        dialect = pyodbc.dialect()
        u = url.make_url(
            "mssql://username:password@hostspec/database?L"
            "ANGUAGE=us_english&foo=bar&driver=SQL+Server"
        )
        connection = dialect.create_connect_args(u)
        eq_(connection[1], {})
        eq_(
            connection[0][0]
            in (
                "DRIVER={SQL Server};Server=hostspec;Database=database;"
                "UID=username;PWD=password;foo=bar;LANGUAGE=us_english",
                "DRIVER={SQL Server};Server=hostspec;Database=database;UID="
                "username;PWD=password;LANGUAGE=us_english;foo=bar",
            ),
            True,
        )

    def test_pyodbc_odbc_connect(self):
        dialect = pyodbc.dialect()
        u = url.make_url(
            "mssql:///?odbc_connect=DRIVER%3D%7BSQL+Server"
            "%7D%3BServer%3Dhostspec%3BDatabase%3Ddatabase"
            "%3BUID%3Dusername%3BPWD%3Dpassword"
        )
        connection = dialect.create_connect_args(u)
        eq_(
            [
                [
                    "DRIVER={SQL Server};Server=hostspec;Database=database;UI"
                    "D=username;PWD=password"
                ],
                {},
            ],
            connection,
        )

    def test_pyodbc_odbc_connect_with_dsn(self):
        dialect = pyodbc.dialect()
        u = url.make_url(
            "mssql:///?odbc_connect=dsn%3Dmydsn%3BDatabase"
            "%3Ddatabase%3BUID%3Dusername%3BPWD%3Dpassword"
        )
        connection = dialect.create_connect_args(u)
        eq_(
            [["dsn=mydsn;Database=database;UID=username;PWD=password"], {}],
            connection,
        )

    def test_pyodbc_odbc_connect_ignores_other_values(self):
        dialect = pyodbc.dialect()
        u = url.make_url(
            "mssql://userdiff:passdiff@localhost/dbdiff?od"
            "bc_connect=DRIVER%3D%7BSQL+Server%7D%3BServer"
            "%3Dhostspec%3BDatabase%3Ddatabase%3BUID%3Duse"
            "rname%3BPWD%3Dpassword"
        )
        connection = dialect.create_connect_args(u)
        eq_(
            [
                [
                    "DRIVER={SQL Server};Server=hostspec;Database=database;UI"
                    "D=username;PWD=password"
                ],
                {},
            ],
            connection,
        )

    def test_pyodbc_token_injection(self):
        token1 = "someuser%3BPORT%3D50001"
        token2 = "somepw%3BPORT%3D50001"
        token3 = "somehost%3BPORT%3D50001"
        token4 = "somedb%3BPORT%3D50001"

        u = url.make_url(
            "mssql+pyodbc://%s:%s@%s/%s?driver=foob"
            % (token1, token2, token3, token4)
        )
        dialect = pyodbc.dialect()
        connection = dialect.create_connect_args(u)
        eq_(
            [
                [
                    "DRIVER={foob};Server=somehost%3BPORT%3D50001;"
                    "Database=somedb%3BPORT%3D50001;UID='someuser;PORT=50001';"
                    "PWD='somepw;PORT=50001'"
                ],
                {},
            ],
            connection,
        )

    def test_adodbapi_token_injection(self):
        token1 = "someuser%3BPORT%3D50001"
        token2 = "somepw%3BPORT%3D50001"
        token3 = "somehost%3BPORT%3D50001"
        token4 = "someport%3BPORT%3D50001"

        # this URL format is all wrong
        u = url.make_url(
            "mssql+adodbapi://@/?user=%s&password=%s&host=%s&port=%s"
            % (token1, token2, token3, token4)
        )
        dialect = adodbapi.dialect()
        connection = dialect.create_connect_args(u)
        eq_(
            [
                [
                    "Provider=SQLOLEDB;"
                    "Data Source='somehost;PORT=50001', 'someport;PORT=50001';"
                    "Initial Catalog=None;User Id='someuser;PORT=50001';"
                    "Password='somepw;PORT=50001'"
                ],
                {},
            ],
            connection,
        )

    def test_pymssql_port_setting(self):
        dialect = pymssql.dialect()

        u = url.make_url("mssql+pymssql://scott:tiger@somehost/test")
        connection = dialect.create_connect_args(u)
        eq_(
            [
                [],
                {
                    "host": "somehost",
                    "password": "tiger",
                    "user": "scott",
                    "database": "test",
                },
            ],
            connection,
        )

        u = url.make_url("mssql+pymssql://scott:tiger@somehost:5000/test")
        connection = dialect.create_connect_args(u)
        eq_(
            [
                [],
                {
                    "host": "somehost:5000",
                    "password": "tiger",
                    "user": "scott",
                    "database": "test",
                },
            ],
            connection,
        )

    def test_pymssql_disconnect(self):
        dialect = pymssql.dialect()

        for error in [
            "Adaptive Server connection timed out",
            "Net-Lib error during Connection reset by peer",
            "message 20003",
            "Error 10054",
            "Not connected to any MS SQL server",
            "Connection is closed",
            "message 20006",  # Write to the server failed
            "message 20017",  # Unexpected EOF from the server
            "message 20047",  # DBPROCESS is dead or not enabled
        ]:
            eq_(dialect.is_disconnect(error, None, None), True)

        eq_(dialect.is_disconnect("not an error", None, None), False)

    def test_pyodbc_disconnect(self):
        dialect = pyodbc.dialect()

        class MockDBAPIError(Exception):
            pass

        class MockProgrammingError(MockDBAPIError):
            pass

        dialect.dbapi = Mock(
            Error=MockDBAPIError, ProgrammingError=MockProgrammingError
        )

        for error in [
            MockDBAPIError("[%s] some pyodbc message" % code)
            for code in [
                "08S01",
                "01002",
                "08003",
                "08007",
                "08S02",
                "08001",
                "HYT00",
                "HY010",
            ]
        ] + [
            MockProgrammingError(message)
            for message in [
                "(some pyodbc stuff) The cursor's connection has been closed.",
                "(some pyodbc stuff) Attempt to use a closed connection.",
            ]
        ]:
            eq_(dialect.is_disconnect(error, None, None), True)

        eq_(
            dialect.is_disconnect(
                MockProgrammingError("not an error"), None, None
            ),
            False,
        )

    @testing.requires.mssql_freetds
    def test_bad_freetds_warning(self):
        engine = engines.testing_engine()

        def _bad_version(connection):
            return 95, 10, 255

        engine.dialect._get_server_version_info = _bad_version
        assert_raises_message(
            exc.SAWarning, "Unrecognized server version info", engine.connect
        )


class EngineFromConfigTest(fixtures.TestBase):
    def test_legacy_schema_flag(self):
        cfg = {
            "sqlalchemy.url": "mssql://foodsn",
            "sqlalchemy.legacy_schema_aliasing": "false",
        }
        e = engine_from_config(
            cfg, module=Mock(version="MS SQL Server 11.0.92")
        )
        eq_(e.dialect.legacy_schema_aliasing, False)


class FastExecutemanyTest(fixtures.TestBase):
    __only_on__ = "mssql"
    __backend__ = True
    __requires__ = ("pyodbc_fast_executemany",)

    @testing.provide_metadata
    def test_flag_on(self):
        t = Table(
            "t",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("data", String(50)),
        )
        t.create()

        eng = engines.testing_engine(options={"fast_executemany": True})

        @event.listens_for(eng, "after_cursor_execute")
        def after_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            if executemany:
                assert cursor.fast_executemany

        with eng.connect() as conn:
            conn.execute(
                t.insert(),
                [{"id": i, "data": "data_%d" % i} for i in range(100)],
            )

            conn.execute(t.insert(), {"id": 200, "data": "data_200"})


class VersionDetectionTest(fixtures.TestBase):
    def test_pymssql_version(self):
        dialect = pymssql.MSDialect_pymssql()

        for vers in [
            "Microsoft SQL Server Blah - 11.0.9216.62",
            "Microsoft SQL Server (XYZ) - 11.0.9216.62 \n"
            "Jul 18 2014 22:00:21 \nCopyright (c) Microsoft Corporation",
            "Microsoft SQL Azure (RTM) - 11.0.9216.62 \n"
            "Jul 18 2014 22:00:21 \nCopyright (c) Microsoft Corporation",
        ]:
            conn = Mock(scalar=Mock(return_value=vers))
            eq_(dialect._get_server_version_info(conn), (11, 0, 9216, 62))

    def test_pyodbc_version_productversion(self):
        dialect = pyodbc.MSDialect_pyodbc()

        conn = Mock(scalar=Mock(return_value="11.0.9216.62"))
        eq_(dialect._get_server_version_info(conn), (11, 0, 9216, 62))

    def test_pyodbc_version_fallback(self):
        dialect = pyodbc.MSDialect_pyodbc()
        dialect.dbapi = Mock()

        for vers, expected in [
            ("11.0.9216.62", (11, 0, 9216, 62)),
            ("notsqlserver.11.foo.0.9216.BAR.62", (11, 0, 9216, 62)),
            ("Not SQL Server Version 10.5", (5,)),
        ]:
            conn = Mock(
                scalar=Mock(
                    side_effect=exc.DBAPIError("stmt", "params", None)
                ),
                connection=Mock(getinfo=Mock(return_value=vers)),
            )

            eq_(dialect._get_server_version_info(conn), expected)


class RealIsolationLevelTest(fixtures.TestBase):
    __only_on__ = "mssql"
    __backend__ = True

    @testing.provide_metadata
    def test_isolation_level(self):
        Table("test", self.metadata, Column("id", Integer)).create(
            checkfirst=True
        )

        with testing.db.connect() as c:
            default = testing.db.dialect.get_isolation_level(c.connection)

        values = [
            "READ UNCOMMITTED",
            "READ COMMITTED",
            "REPEATABLE READ",
            "SERIALIZABLE",
            "SNAPSHOT",
        ]
        for value in values:
            with testing.db.connect() as c:
                c.execution_options(isolation_level=value)

                c.execute("SELECT TOP 10 * FROM test")

                eq_(
                    testing.db.dialect.get_isolation_level(c.connection), value
                )

        with testing.db.connect() as c:
            eq_(testing.db.dialect.get_isolation_level(c.connection), default)


class IsolationLevelDetectTest(fixtures.TestBase):
    def _fixture(self, view):
        class Error(Exception):
            pass

        dialect = pyodbc.MSDialect_pyodbc()
        dialect.dbapi = Mock(Error=Error)
        dialect.server_version_info = base.MS_2012_VERSION

        result = []

        def fail_on_exec(stmt,):
            if view is not None and view in stmt:
                result.append(("SERIALIZABLE",))
            else:
                raise Error("that didn't work")

        connection = Mock(
            cursor=Mock(
                return_value=Mock(
                    execute=fail_on_exec, fetchone=lambda: result[0]
                )
            )
        )

        return dialect, connection

    def test_dm_pdw_nodes(self):
        dialect, connection = self._fixture("dm_pdw_nodes_exec_sessions")

        eq_(dialect.get_isolation_level(connection), "SERIALIZABLE")

    def test_exec_sessions(self):
        dialect, connection = self._fixture("exec_sessions")

        eq_(dialect.get_isolation_level(connection), "SERIALIZABLE")

    def test_not_supported(self):
        dialect, connection = self._fixture(None)

        with expect_warnings("Could not fetch transaction isolation level"):
            assert_raises_message(
                NotImplementedError,
                "Can't fetch isolation",
                dialect.get_isolation_level,
                connection,
            )
