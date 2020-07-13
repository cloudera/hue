# coding: utf-8

import re

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import DDL
from sqlalchemy import DefaultClause
from sqlalchemy import event
from sqlalchemy import exc
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import inspect
from sqlalchemy import Integer
from sqlalchemy import LargeBinary
from sqlalchemy import MetaData
from sqlalchemy import NCHAR
from sqlalchemy import select
from sqlalchemy import SmallInteger
from sqlalchemy import sql
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import testing
from sqlalchemy import Text
from sqlalchemy import TIMESTAMP
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import UniqueConstraint
from sqlalchemy import util
from sqlalchemy.dialects.mysql import base as mysql
from sqlalchemy.dialects.mysql import reflection as _reflection
from sqlalchemy.schema import CreateIndex
from sqlalchemy.testing import assert_raises_message
from sqlalchemy.testing import AssertsCompiledSQL
from sqlalchemy.testing import eq_
from sqlalchemy.testing import expect_warnings
from sqlalchemy.testing import fixtures
from sqlalchemy.testing import is_
from sqlalchemy.testing import mock


class TypeReflectionTest(fixtures.TestBase):
    __only_on__ = "mysql"
    __backend__ = True

    @testing.provide_metadata
    def _run_test(self, specs, attributes):
        columns = [Column("c%i" % (i + 1), t[0]) for i, t in enumerate(specs)]

        # Early 5.0 releases seem to report more "general" for columns
        # in a view, e.g. char -> varchar, tinyblob -> mediumblob
        use_views = testing.db.dialect.server_version_info > (5, 0, 10)

        m = self.metadata
        Table("mysql_types", m, *columns)

        if use_views:
            event.listen(
                m,
                "after_create",
                DDL(
                    "CREATE OR REPLACE VIEW mysql_types_v "
                    "AS SELECT * from mysql_types"
                ),
            )
            event.listen(
                m, "before_drop", DDL("DROP VIEW IF EXISTS mysql_types_v")
            )
        m.create_all()

        m2 = MetaData(testing.db)
        tables = [Table("mysql_types", m2, autoload=True)]
        if use_views:
            tables.append(Table("mysql_types_v", m2, autoload=True))

        for table in tables:
            for i, (reflected_col, spec) in enumerate(zip(table.c, specs)):
                expected_spec = spec[1]
                reflected_type = reflected_col.type
                is_(type(reflected_type), type(expected_spec))

                for attr in attributes:
                    eq_(
                        getattr(reflected_type, attr),
                        getattr(expected_spec, attr),
                        "Column %s: Attribute %s value of %s does not "
                        "match %s for type %s"
                        % (
                            "c%i" % (i + 1),
                            attr,
                            getattr(reflected_type, attr),
                            getattr(expected_spec, attr),
                            spec[0],
                        ),
                    )

    def test_time_types(self):
        specs = []

        if testing.requires.mysql_fsp.enabled:
            fsps = [None, 0, 5]
        else:
            fsps = [None]

        for type_ in (mysql.TIMESTAMP, mysql.DATETIME, mysql.TIME):
            # MySQL defaults fsp to 0, and if 0 does not report it.
            # we don't actually render 0 right now in DDL but even if we do,
            # it comes back blank
            for fsp in fsps:
                if fsp:
                    specs.append((type_(fsp=fsp), type_(fsp=fsp)))
                else:
                    specs.append((type_(), type_()))

        specs.extend(
            [(TIMESTAMP(), mysql.TIMESTAMP()), (DateTime(), mysql.DATETIME())]
        )

        # note 'timezone' should always be None on both
        self._run_test(specs, ["fsp", "timezone"])

    def test_year_types(self):
        specs = [
            (mysql.YEAR(), mysql.YEAR(display_width=4)),
            (mysql.YEAR(display_width=4), mysql.YEAR(display_width=4)),
        ]

        self._run_test(specs, ["display_width"])

    def test_string_types(self):
        specs = [
            (String(1), mysql.MSString(1)),
            (String(3), mysql.MSString(3)),
            (Text(), mysql.MSText()),
            (Unicode(1), mysql.MSString(1)),
            (Unicode(3), mysql.MSString(3)),
            (UnicodeText(), mysql.MSText()),
            (mysql.MSChar(1), mysql.MSChar(1)),
            (mysql.MSChar(3), mysql.MSChar(3)),
            (NCHAR(2), mysql.MSChar(2)),
            (mysql.MSNChar(2), mysql.MSChar(2)),
            (mysql.MSNVarChar(22), mysql.MSString(22)),
        ]
        self._run_test(specs, ["length"])

    def test_integer_types(self):
        specs = []
        for type_ in [
            mysql.TINYINT,
            mysql.SMALLINT,
            mysql.MEDIUMINT,
            mysql.INTEGER,
            mysql.BIGINT,
        ]:
            for display_width in [None, 4, 7]:
                for unsigned in [False, True]:
                    for zerofill in [None, True]:
                        kw = {}
                        if display_width:
                            kw["display_width"] = display_width
                        if unsigned is not None:
                            kw["unsigned"] = unsigned
                        if zerofill is not None:
                            kw["zerofill"] = zerofill

                        zerofill = bool(zerofill)
                        source_type = type_(**kw)

                        if display_width is None:
                            display_width = {
                                mysql.MEDIUMINT: 9,
                                mysql.SMALLINT: 6,
                                mysql.TINYINT: 4,
                                mysql.INTEGER: 11,
                                mysql.BIGINT: 20,
                            }[type_]

                        if zerofill:
                            unsigned = True

                        expected_type = type_(
                            display_width=display_width,
                            unsigned=unsigned,
                            zerofill=zerofill,
                        )
                        specs.append((source_type, expected_type))

        specs.extend(
            [
                (SmallInteger(), mysql.SMALLINT(display_width=6)),
                (Integer(), mysql.INTEGER(display_width=11)),
                (BigInteger, mysql.BIGINT(display_width=20)),
            ]
        )
        self._run_test(specs, ["display_width", "unsigned", "zerofill"])

    def test_binary_types(self):
        specs = [
            (LargeBinary(3), mysql.TINYBLOB()),
            (LargeBinary(), mysql.BLOB()),
            (mysql.MSBinary(3), mysql.MSBinary(3)),
            (mysql.MSVarBinary(3), mysql.MSVarBinary(3)),
            (mysql.MSTinyBlob(), mysql.MSTinyBlob()),
            (mysql.MSBlob(), mysql.MSBlob()),
            (mysql.MSBlob(1234), mysql.MSBlob()),
            (mysql.MSMediumBlob(), mysql.MSMediumBlob()),
            (mysql.MSLongBlob(), mysql.MSLongBlob()),
        ]
        self._run_test(specs, [])

    @testing.uses_deprecated("Manually quoting ENUM value literals")
    def test_legacy_enum_types(self):

        specs = [(mysql.ENUM("''", "'fleem'"), mysql.ENUM("''", "'fleem'"))]

        self._run_test(specs, ["enums"])


class ReflectionTest(fixtures.TestBase, AssertsCompiledSQL):

    __only_on__ = "mysql"
    __backend__ = True

    def test_default_reflection(self):
        """Test reflection of column defaults."""

        from sqlalchemy.dialects.mysql import VARCHAR

        def_table = Table(
            "mysql_def",
            MetaData(testing.db),
            Column(
                "c1",
                VARCHAR(10, collation="utf8_unicode_ci"),
                DefaultClause(""),
                nullable=False,
            ),
            Column("c2", String(10), DefaultClause("0")),
            Column("c3", String(10), DefaultClause("abc")),
            Column("c4", TIMESTAMP, DefaultClause("2009-04-05 12:00:00")),
            Column("c5", TIMESTAMP),
            Column(
                "c6",
                TIMESTAMP,
                DefaultClause(
                    sql.text(
                        "CURRENT_TIMESTAMP " "ON UPDATE CURRENT_TIMESTAMP"
                    )
                ),
            ),
        )
        def_table.create()
        try:
            reflected = Table("mysql_def", MetaData(testing.db), autoload=True)
        finally:
            def_table.drop()
        assert def_table.c.c1.server_default.arg == ""
        assert def_table.c.c2.server_default.arg == "0"
        assert def_table.c.c3.server_default.arg == "abc"
        assert def_table.c.c4.server_default.arg == "2009-04-05 12:00:00"
        assert str(reflected.c.c1.server_default.arg) == "''"
        assert str(reflected.c.c2.server_default.arg) == "'0'"
        assert str(reflected.c.c3.server_default.arg) == "'abc'"
        assert (
            str(reflected.c.c4.server_default.arg) == "'2009-04-05 12:00:00'"
        )
        assert reflected.c.c5.default is None
        assert reflected.c.c5.server_default is None
        assert reflected.c.c6.default is None
        assert re.match(
            r"CURRENT_TIMESTAMP(\(\))? ON UPDATE CURRENT_TIMESTAMP(\(\))?",
            str(reflected.c.c6.server_default.arg).upper(),
        )
        reflected.create()
        try:
            reflected2 = Table(
                "mysql_def", MetaData(testing.db), autoload=True
            )
        finally:
            reflected.drop()
        assert str(reflected2.c.c1.server_default.arg) == "''"
        assert str(reflected2.c.c2.server_default.arg) == "'0'"
        assert str(reflected2.c.c3.server_default.arg) == "'abc'"
        assert (
            str(reflected2.c.c4.server_default.arg) == "'2009-04-05 12:00:00'"
        )
        assert reflected.c.c5.default is None
        assert reflected.c.c5.server_default is None
        assert reflected.c.c6.default is None
        assert re.match(
            r"CURRENT_TIMESTAMP(\(\))? ON UPDATE CURRENT_TIMESTAMP(\(\))?",
            str(reflected.c.c6.server_default.arg).upper(),
        )

    def test_reflection_with_table_options(self):
        comment = r"""Comment types type speedily ' " \ '' Fun!"""

        def_table = Table(
            "mysql_def",
            MetaData(testing.db),
            Column("c1", Integer()),
            mysql_engine="MEMORY",
            comment=comment,
            mysql_default_charset="utf8",
            mysql_auto_increment="5",
            mysql_avg_row_length="3",
            mysql_password="secret",
            mysql_connection="fish",
        )

        def_table.create()
        try:
            reflected = Table("mysql_def", MetaData(testing.db), autoload=True)
        finally:
            def_table.drop()

        assert def_table.kwargs["mysql_engine"] == "MEMORY"
        assert def_table.comment == comment
        assert def_table.kwargs["mysql_default_charset"] == "utf8"
        assert def_table.kwargs["mysql_auto_increment"] == "5"
        assert def_table.kwargs["mysql_avg_row_length"] == "3"
        assert def_table.kwargs["mysql_password"] == "secret"
        assert def_table.kwargs["mysql_connection"] == "fish"

        assert reflected.kwargs["mysql_engine"] == "MEMORY"

        assert reflected.comment == comment
        assert reflected.kwargs["mysql_comment"] == comment
        assert reflected.kwargs["mysql_default charset"] == "utf8"
        assert reflected.kwargs["mysql_avg_row_length"] == "3"
        assert reflected.kwargs["mysql_connection"] == "fish"

        # This field doesn't seem to be returned by mysql itself.
        # assert reflected.kwargs['mysql_password'] == 'secret'

        # This is explicitly ignored when reflecting schema.
        # assert reflected.kwargs['mysql_auto_increment'] == '5'

    def test_reflection_on_include_columns(self):
        """Test reflection of include_columns to be sure they respect case."""

        case_table = Table(
            "mysql_case",
            MetaData(testing.db),
            Column("c1", String(10)),
            Column("C2", String(10)),
            Column("C3", String(10)),
        )

        try:
            case_table.create()
            reflected = Table(
                "mysql_case",
                MetaData(testing.db),
                autoload=True,
                include_columns=["c1", "C2"],
            )
            for t in case_table, reflected:
                assert "c1" in t.c.keys()
                assert "C2" in t.c.keys()
            reflected2 = Table(
                "mysql_case",
                MetaData(testing.db),
                autoload=True,
                include_columns=["c1", "c2"],
            )
            assert "c1" in reflected2.c.keys()
            for c in ["c2", "C2", "C3"]:
                assert c not in reflected2.c.keys()
        finally:
            case_table.drop()

    def test_autoincrement(self):
        meta = MetaData(testing.db)
        try:
            Table(
                "ai_1",
                meta,
                Column("int_y", Integer, primary_key=True, autoincrement=True),
                Column("int_n", Integer, DefaultClause("0"), primary_key=True),
                mysql_engine="MyISAM",
            )
            Table(
                "ai_2",
                meta,
                Column("int_y", Integer, primary_key=True, autoincrement=True),
                Column("int_n", Integer, DefaultClause("0"), primary_key=True),
                mysql_engine="MyISAM",
            )
            Table(
                "ai_3",
                meta,
                Column(
                    "int_n",
                    Integer,
                    DefaultClause("0"),
                    primary_key=True,
                    autoincrement=False,
                ),
                Column("int_y", Integer, primary_key=True, autoincrement=True),
                mysql_engine="MyISAM",
            )
            Table(
                "ai_4",
                meta,
                Column(
                    "int_n",
                    Integer,
                    DefaultClause("0"),
                    primary_key=True,
                    autoincrement=False,
                ),
                Column(
                    "int_n2",
                    Integer,
                    DefaultClause("0"),
                    primary_key=True,
                    autoincrement=False,
                ),
                mysql_engine="MyISAM",
            )
            Table(
                "ai_5",
                meta,
                Column("int_y", Integer, primary_key=True, autoincrement=True),
                Column(
                    "int_n",
                    Integer,
                    DefaultClause("0"),
                    primary_key=True,
                    autoincrement=False,
                ),
                mysql_engine="MyISAM",
            )
            Table(
                "ai_6",
                meta,
                Column("o1", String(1), DefaultClause("x"), primary_key=True),
                Column("int_y", Integer, primary_key=True, autoincrement=True),
                mysql_engine="MyISAM",
            )
            Table(
                "ai_7",
                meta,
                Column("o1", String(1), DefaultClause("x"), primary_key=True),
                Column("o2", String(1), DefaultClause("x"), primary_key=True),
                Column("int_y", Integer, primary_key=True, autoincrement=True),
                mysql_engine="MyISAM",
            )
            Table(
                "ai_8",
                meta,
                Column("o1", String(1), DefaultClause("x"), primary_key=True),
                Column("o2", String(1), DefaultClause("x"), primary_key=True),
                mysql_engine="MyISAM",
            )
            meta.create_all()

            table_names = [
                "ai_1",
                "ai_2",
                "ai_3",
                "ai_4",
                "ai_5",
                "ai_6",
                "ai_7",
                "ai_8",
            ]
            mr = MetaData(testing.db)
            mr.reflect(only=table_names)

            for tbl in [mr.tables[name] for name in table_names]:
                for c in tbl.c:
                    if c.name.startswith("int_y"):
                        assert c.autoincrement
                    elif c.name.startswith("int_n"):
                        assert not c.autoincrement
                tbl.insert().execute()
                if "int_y" in tbl.c:
                    assert select([tbl.c.int_y]).scalar() == 1
                    assert list(tbl.select().execute().first()).count(1) == 1
                else:
                    assert 1 not in list(tbl.select().execute().first())
        finally:
            meta.drop_all()

    @testing.provide_metadata
    def test_view_reflection(self):
        Table(
            "x", self.metadata, Column("a", Integer), Column("b", String(50))
        )
        self.metadata.create_all()

        with testing.db.connect() as conn:
            conn.execute("CREATE VIEW v1 AS SELECT * FROM x")
            conn.execute("CREATE ALGORITHM=MERGE VIEW v2 AS SELECT * FROM x")
            conn.execute(
                "CREATE ALGORITHM=UNDEFINED VIEW v3 AS SELECT * FROM x"
            )
            conn.execute(
                "CREATE DEFINER=CURRENT_USER VIEW v4 AS SELECT * FROM x"
            )

        @event.listens_for(self.metadata, "before_drop")
        def cleanup(*arg, **kw):
            with testing.db.connect() as conn:
                for v in ["v1", "v2", "v3", "v4"]:
                    conn.execute("DROP VIEW %s" % v)

        insp = inspect(testing.db)
        for v in ["v1", "v2", "v3", "v4"]:
            eq_(
                [
                    (col["name"], col["type"].__class__)
                    for col in insp.get_columns(v)
                ],
                [("a", mysql.INTEGER), ("b", mysql.VARCHAR)],
            )

    @testing.provide_metadata
    def test_skip_not_describable(self):
        @event.listens_for(self.metadata, "before_drop")
        def cleanup(*arg, **kw):
            with testing.db.connect() as conn:
                conn.execute("DROP TABLE IF EXISTS test_t1")
                conn.execute("DROP TABLE IF EXISTS test_t2")
                conn.execute("DROP VIEW IF EXISTS test_v")

        with testing.db.connect() as conn:
            conn.execute("CREATE TABLE test_t1 (id INTEGER)")
            conn.execute("CREATE TABLE test_t2 (id INTEGER)")
            conn.execute("CREATE VIEW test_v AS SELECT id FROM test_t1")
            conn.execute("DROP TABLE test_t1")

            m = MetaData()
            with expect_warnings(
                "Skipping .* Table or view named .?test_v.? could not be "
                "reflected: .* references invalid table"
            ):
                m.reflect(views=True, bind=conn)
            eq_(m.tables["test_t2"].name, "test_t2")

            assert_raises_message(
                exc.UnreflectableTableError,
                "references invalid table",
                Table,
                "test_v",
                MetaData(),
                autoload_with=conn,
            )

    @testing.exclude("mysql", "<", (5, 0, 0), "no information_schema support")
    def test_system_views(self):
        dialect = testing.db.dialect
        connection = testing.db.connect()
        view_names = dialect.get_view_names(connection, "information_schema")
        self.assert_("TABLES" in view_names)

    @testing.provide_metadata
    def test_nullable_reflection(self):
        """test reflection of NULL/NOT NULL, in particular with TIMESTAMP
        defaults where MySQL is inconsistent in how it reports CREATE TABLE.

        """
        meta = self.metadata

        # this is ideally one table, but older MySQL versions choke
        # on the multiple TIMESTAMP columns

        row = testing.db.execute(
            "show variables like '%%explicit_defaults_for_timestamp%%'"
        ).first()
        explicit_defaults_for_timestamp = row[1].lower() in ("on", "1", "true")

        reflected = []
        for idx, cols in enumerate(
            [
                [
                    "x INTEGER NULL",
                    "y INTEGER NOT NULL",
                    "z INTEGER",
                    "q TIMESTAMP NULL",
                ],
                ["p TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP"],
                ["r TIMESTAMP NOT NULL"],
                ["s TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"],
                ["t TIMESTAMP"],
                ["u TIMESTAMP DEFAULT CURRENT_TIMESTAMP"],
            ]
        ):
            Table("nn_t%d" % idx, meta)  # to allow DROP

            testing.db.execute(
                """
                CREATE TABLE nn_t%d (
                    %s
                )
            """
                % (idx, ", \n".join(cols))
            )

            reflected.extend(
                {
                    "name": d["name"],
                    "nullable": d["nullable"],
                    "default": d["default"],
                }
                for d in inspect(testing.db).get_columns("nn_t%d" % idx)
            )

        if testing.db.dialect._is_mariadb_102:
            current_timestamp = "current_timestamp()"
        else:
            current_timestamp = "CURRENT_TIMESTAMP"

        eq_(
            reflected,
            [
                {"name": "x", "nullable": True, "default": None},
                {"name": "y", "nullable": False, "default": None},
                {"name": "z", "nullable": True, "default": None},
                {"name": "q", "nullable": True, "default": None},
                {"name": "p", "nullable": True, "default": current_timestamp},
                {
                    "name": "r",
                    "nullable": False,
                    "default": None
                    if explicit_defaults_for_timestamp
                    else (
                        "%(current_timestamp)s "
                        "ON UPDATE %(current_timestamp)s"
                    )
                    % {"current_timestamp": current_timestamp},
                },
                {"name": "s", "nullable": False, "default": current_timestamp},
                {
                    "name": "t",
                    "nullable": True
                    if explicit_defaults_for_timestamp
                    else False,
                    "default": None
                    if explicit_defaults_for_timestamp
                    else (
                        "%(current_timestamp)s "
                        "ON UPDATE %(current_timestamp)s"
                    )
                    % {"current_timestamp": current_timestamp},
                },
                {
                    "name": "u",
                    "nullable": True
                    if explicit_defaults_for_timestamp
                    else False,
                    "default": current_timestamp,
                },
            ],
        )

    @testing.provide_metadata
    def test_reflection_with_unique_constraint(self):
        insp = inspect(testing.db)

        meta = self.metadata
        uc_table = Table(
            "mysql_uc",
            meta,
            Column("a", String(10)),
            UniqueConstraint("a", name="uc_a"),
        )

        uc_table.create()

        # MySQL converts unique constraints into unique indexes.
        # separately we get both
        indexes = dict((i["name"], i) for i in insp.get_indexes("mysql_uc"))
        constraints = set(
            i["name"] for i in insp.get_unique_constraints("mysql_uc")
        )

        self.assert_("uc_a" in indexes)
        self.assert_(indexes["uc_a"]["unique"])
        self.assert_("uc_a" in constraints)

        # reflection here favors the unique index, as that's the
        # more "official" MySQL construct
        reflected = Table("mysql_uc", MetaData(testing.db), autoload=True)

        indexes = dict((i.name, i) for i in reflected.indexes)
        constraints = set(uc.name for uc in reflected.constraints)

        self.assert_("uc_a" in indexes)
        self.assert_(indexes["uc_a"].unique)
        self.assert_("uc_a" not in constraints)

    @testing.provide_metadata
    def test_reflect_fulltext(self):
        mt = Table(
            "mytable",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("textdata", String(50)),
            mysql_engine="InnoDB",
        )
        Index("textdata_ix", mt.c.textdata, mysql_prefix="FULLTEXT")
        self.metadata.create_all(testing.db)

        mt = Table("mytable", MetaData(), autoload_with=testing.db)
        idx = list(mt.indexes)[0]
        eq_(idx.name, "textdata_ix")
        eq_(idx.dialect_options["mysql"]["prefix"], "FULLTEXT")
        self.assert_compile(
            CreateIndex(idx),
            "CREATE FULLTEXT INDEX textdata_ix ON mytable (textdata)",
        )

    @testing.requires.mysql_ngram_fulltext
    @testing.provide_metadata
    def test_reflect_fulltext_comment(self):
        mt = Table(
            "mytable",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("textdata", String(50)),
            mysql_engine="InnoDB",
        )
        Index(
            "textdata_ix",
            mt.c.textdata,
            mysql_prefix="FULLTEXT",
            mysql_with_parser="ngram",
        )

        self.metadata.create_all(testing.db)

        mt = Table("mytable", MetaData(), autoload_with=testing.db)
        idx = list(mt.indexes)[0]
        eq_(idx.name, "textdata_ix")
        eq_(idx.dialect_options["mysql"]["prefix"], "FULLTEXT")
        eq_(idx.dialect_options["mysql"]["with_parser"], "ngram")
        self.assert_compile(
            CreateIndex(idx),
            "CREATE FULLTEXT INDEX textdata_ix ON mytable "
            "(textdata) WITH PARSER ngram",
        )

    @testing.provide_metadata
    def test_non_column_index(self):
        m1 = self.metadata
        t1 = Table(
            "add_ix", m1, Column("x", String(50)), mysql_engine="InnoDB"
        )
        Index("foo_idx", t1.c.x.desc())
        m1.create_all()

        insp = inspect(testing.db)
        eq_(
            insp.get_indexes("add_ix"),
            [{"name": "foo_idx", "column_names": ["x"], "unique": False}],
        )

    def _bug_88718_96365_casing_0(self):
        fkeys_casing_0 = [
            {
                "name": "FK_PlaylistTTrackId",
                "constrained_columns": ["TTrackID"],
                "referred_schema": "Test_Schema",
                "referred_table": "Track",
                "referred_columns": ["trackid"],
                "options": {},
            },
            {
                "name": "FK_PlaylistTrackId",
                "constrained_columns": ["TrackID"],
                "referred_schema": None,
                "referred_table": "Track",
                "referred_columns": ["trackid"],
                "options": {},
            },
        ]
        ischema_casing_0 = [
            ("Test", "Track", "TrackID"),
            ("Test_Schema", "Track", "TrackID"),
        ]
        return fkeys_casing_0, ischema_casing_0

    def _bug_88718_96365_casing_1(self):
        fkeys_casing_1 = [
            {
                "name": "FK_PlaylistTTrackId",
                "constrained_columns": ["TTrackID"],
                "referred_schema": "Test_Schema",
                "referred_table": "Track",
                "referred_columns": ["trackid"],
                "options": {},
            },
            {
                "name": "FK_PlaylistTrackId",
                "constrained_columns": ["TrackID"],
                "referred_schema": None,
                "referred_table": "Track",
                "referred_columns": ["trackid"],
                "options": {},
            },
        ]
        ischema_casing_1 = [
            (util.u("Test"), util.u("Track"), "TrackID"),
            (util.u("Test_Schema"), util.u("Track"), "TrackID"),
        ]
        return fkeys_casing_1, ischema_casing_1

    def _bug_88718_96365_casing_2(self):
        fkeys_casing_2 = [
            {
                "name": "FK_PlaylistTTrackId",
                "constrained_columns": ["TTrackID"],
                # I haven't tested schema name but since col/table both
                # do it, assume schema name also comes back wrong
                "referred_schema": "test_schema",
                "referred_table": "track",
                "referred_columns": ["trackid"],
                "options": {},
            },
            {
                "name": "FK_PlaylistTrackId",
                "constrained_columns": ["TrackID"],
                "referred_schema": None,
                # table name also comes back wrong (probably schema also)
                # with casing=2, see https://bugs.mysql.com/bug.php?id=96365
                "referred_table": "track",
                "referred_columns": ["trackid"],
                "options": {},
            },
        ]
        ischema_casing_2 = [
            ("Test", "Track", "TrackID"),
            ("Test_Schema", "Track", "TrackID"),
        ]
        return fkeys_casing_2, ischema_casing_2

    def test_correct_for_mysql_bugs_88718_96365(self):
        dialect = mysql.dialect()

        for casing, (fkeys, ischema) in [
            (0, self._bug_88718_96365_casing_0()),
            (1, self._bug_88718_96365_casing_1()),
            (2, self._bug_88718_96365_casing_2()),
        ]:
            dialect._casing = casing
            dialect.default_schema_name = "Test"
            connection = mock.Mock(
                dialect=dialect, execute=lambda stmt, **params: ischema
            )
            dialect._correct_for_mysql_bugs_88718_96365(fkeys, connection)
            eq_(
                fkeys,
                [
                    {
                        "name": "FK_PlaylistTTrackId",
                        "constrained_columns": ["TTrackID"],
                        "referred_schema": "Test_Schema",
                        "referred_table": "Track",
                        "referred_columns": ["TrackID"],
                        "options": {},
                    },
                    {
                        "name": "FK_PlaylistTrackId",
                        "constrained_columns": ["TrackID"],
                        "referred_schema": None,
                        "referred_table": "Track",
                        "referred_columns": ["TrackID"],
                        "options": {},
                    },
                ],
            )

    @testing.provide_metadata
    def test_case_sensitive_column_constraint_reflection(self):
        # test for issue #4344 which works around
        # MySQL 8.0 bug https://bugs.mysql.com/bug.php?id=88718

        m1 = self.metadata

        Table(
            "Track",
            m1,
            Column("TrackID", Integer, primary_key=True),
            mysql_engine="InnoDB",
        )
        Table(
            "Track",
            m1,
            Column("TrackID", Integer, primary_key=True),
            schema=testing.config.test_schema,
            mysql_engine="InnoDB",
        )
        Table(
            "PlaylistTrack",
            m1,
            Column("id", Integer, primary_key=True),
            Column(
                "TrackID",
                ForeignKey("Track.TrackID", name="FK_PlaylistTrackId"),
            ),
            Column(
                "TTrackID",
                ForeignKey(
                    "%s.Track.TrackID" % (testing.config.test_schema,),
                    name="FK_PlaylistTTrackId",
                ),
            ),
            mysql_engine="InnoDB",
        )
        m1.create_all()

        if testing.db.dialect._casing in (1, 2):
            # the original test for the 88718 fix here in [ticket:4344]
            # actually set  referred_table='track', with the wrong casing!
            # this test was never run. with [ticket:4751], I've gone through
            # the trouble to create docker containers with true
            # lower_case_table_names=2 and per
            # https://bugs.mysql.com/bug.php?id=96365 the table name being
            # lower case is also an 8.0 regression.

            eq_(
                inspect(testing.db).get_foreign_keys("PlaylistTrack"),
                [
                    {
                        "name": "FK_PlaylistTTrackId",
                        "constrained_columns": ["TTrackID"],
                        "referred_schema": testing.config.test_schema,
                        "referred_table": "Track",
                        "referred_columns": ["TrackID"],
                        "options": {},
                    },
                    {
                        "name": "FK_PlaylistTrackId",
                        "constrained_columns": ["TrackID"],
                        "referred_schema": None,
                        "referred_table": "Track",
                        "referred_columns": ["TrackID"],
                        "options": {},
                    },
                ],
            )
        else:
            eq_(
                inspect(testing.db).get_foreign_keys("PlaylistTrack"),
                [
                    {
                        "name": "FK_PlaylistTTrackId",
                        "constrained_columns": ["TTrackID"],
                        "referred_schema": testing.config.test_schema,
                        "referred_table": "Track",
                        "referred_columns": ["TrackID"],
                        "options": {},
                    },
                    {
                        "name": "FK_PlaylistTrackId",
                        "constrained_columns": ["TrackID"],
                        "referred_schema": None,
                        "referred_table": "Track",
                        "referred_columns": ["TrackID"],
                        "options": {},
                    },
                ],
            )

    @testing.requires.mysql_fully_case_sensitive
    @testing.provide_metadata
    def test_case_sensitive_reflection_dual_case_references(self):
        # this tests that within the fix we do for MySQL bug
        # 88718, we don't do case-insensitive logic if the backend
        # is case sensitive
        m = self.metadata
        Table(
            "t1",
            m,
            Column("some_id", Integer, primary_key=True),
            mysql_engine="InnoDB",
        )

        Table(
            "T1",
            m,
            Column("Some_Id", Integer, primary_key=True),
            mysql_engine="InnoDB",
        )

        Table(
            "t2",
            m,
            Column("id", Integer, primary_key=True),
            Column("t1id", ForeignKey("t1.some_id", name="t1id_fk")),
            Column("cap_t1id", ForeignKey("T1.Some_Id", name="cap_t1id_fk")),
            mysql_engine="InnoDB",
        )
        m.create_all(testing.db)

        eq_(
            dict(
                (rec["name"], rec)
                for rec in inspect(testing.db).get_foreign_keys("t2")
            ),
            {
                "cap_t1id_fk": {
                    "name": "cap_t1id_fk",
                    "constrained_columns": ["cap_t1id"],
                    "referred_schema": None,
                    "referred_table": "T1",
                    "referred_columns": ["Some_Id"],
                    "options": {},
                },
                "t1id_fk": {
                    "name": "t1id_fk",
                    "constrained_columns": ["t1id"],
                    "referred_schema": None,
                    "referred_table": "t1",
                    "referred_columns": ["some_id"],
                    "options": {},
                },
            },
        )


class RawReflectionTest(fixtures.TestBase):
    __backend__ = True

    def setup(self):
        dialect = mysql.dialect()
        self.parser = _reflection.MySQLTableDefinitionParser(
            dialect, dialect.identifier_preparer
        )

    def test_key_reflection(self):
        regex = self.parser._re_key

        assert regex.match("  PRIMARY KEY (`id`),")
        assert regex.match("  PRIMARY KEY USING BTREE (`id`),")
        assert regex.match("  PRIMARY KEY (`id`) USING BTREE,")
        assert regex.match("  PRIMARY KEY (`id`)")
        assert regex.match("  PRIMARY KEY USING BTREE (`id`)")
        assert regex.match("  PRIMARY KEY (`id`) USING BTREE")
        assert regex.match(
            "  PRIMARY KEY (`id`) USING BTREE KEY_BLOCK_SIZE 16"
        )
        assert regex.match(
            "  PRIMARY KEY (`id`) USING BTREE KEY_BLOCK_SIZE=16"
        )
        assert regex.match(
            "  PRIMARY KEY (`id`) USING BTREE KEY_BLOCK_SIZE  = 16"
        )
        assert not regex.match(
            "  PRIMARY KEY (`id`) USING BTREE KEY_BLOCK_SIZE = = 16"
        )
        assert regex.match("  KEY (`id`) USING BTREE COMMENT 'comment'")
        # `SHOW CREATE TABLE` returns COMMENT '''comment'
        # after creating table with COMMENT '\'comment'
        assert regex.match("  KEY (`id`) USING BTREE COMMENT '''comment'")
        assert regex.match("  KEY (`id`) USING BTREE COMMENT 'comment'''")
        assert regex.match("  KEY (`id`) USING BTREE COMMENT 'prefix''suffix'")
        assert regex.match(
            "  KEY (`id`) USING BTREE COMMENT 'prefix''text''suffix'"
        )
        # https://forums.mysql.com/read.php?20,567102,567111#msg-567111
        # "It means if the MySQL version >= 501, execute what's in the comment"
        assert regex.match(
            "  FULLTEXT KEY `ix_fulltext_oi_g_name` (`oi_g_name`) "
            "/*!50100 WITH PARSER `ngram` */ "
        )

    def test_key_reflection_columns(self):
        regex = self.parser._re_key
        exprs = self.parser._re_keyexprs
        m = regex.match("  KEY (`id`) USING BTREE COMMENT '''comment'")
        eq_(m.group("columns"), "`id`")

        m = regex.match("  KEY (`x`, `y`) USING BTREE")
        eq_(m.group("columns"), "`x`, `y`")

        eq_(exprs.findall(m.group("columns")), [("x", "", ""), ("y", "", "")])

        m = regex.match("  KEY (`x`(25), `y`(15)) USING BTREE")
        eq_(m.group("columns"), "`x`(25), `y`(15)")
        eq_(
            exprs.findall(m.group("columns")),
            [("x", "25", ""), ("y", "15", "")],
        )

        m = regex.match("  KEY (`x`(25) DESC, `y`(15) ASC) USING BTREE")
        eq_(m.group("columns"), "`x`(25) DESC, `y`(15) ASC")
        eq_(
            exprs.findall(m.group("columns")),
            [("x", "25", "DESC"), ("y", "15", "ASC")],
        )

        m = regex.match("  KEY `foo_idx` (`x` DESC)")
        eq_(m.group("columns"), "`x` DESC")
        eq_(exprs.findall(m.group("columns")), [("x", "", "DESC")])

        eq_(exprs.findall(m.group("columns")), [("x", "", "DESC")])

        m = regex.match("  KEY `foo_idx` (`x` DESC, `y` ASC)")
        eq_(m.group("columns"), "`x` DESC, `y` ASC")

    def test_fk_reflection(self):
        regex = self.parser._re_fk_constraint

        m = regex.match(
            "  CONSTRAINT `addresses_user_id_fkey` "
            "FOREIGN KEY (`user_id`) "
            "REFERENCES `users` (`id`) "
            "ON DELETE CASCADE ON UPDATE CASCADE"
        )
        eq_(
            m.groups(),
            (
                "addresses_user_id_fkey",
                "`user_id`",
                "`users`",
                "`id`",
                None,
                "CASCADE",
                "CASCADE",
            ),
        )

        m = regex.match(
            "  CONSTRAINT `addresses_user_id_fkey` "
            "FOREIGN KEY (`user_id`) "
            "REFERENCES `users` (`id`) "
            "ON DELETE CASCADE ON UPDATE SET NULL"
        )
        eq_(
            m.groups(),
            (
                "addresses_user_id_fkey",
                "`user_id`",
                "`users`",
                "`id`",
                None,
                "CASCADE",
                "SET NULL",
            ),
        )
