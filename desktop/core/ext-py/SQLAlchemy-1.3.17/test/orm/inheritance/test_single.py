from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import inspect
from sqlalchemy import Integer
from sqlalchemy import literal
from sqlalchemy import literal_column
from sqlalchemy import null
from sqlalchemy import select
from sqlalchemy import String
from sqlalchemy import testing
from sqlalchemy.orm import aliased
from sqlalchemy.orm import Bundle
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import create_session
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import mapper
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import subqueryload
from sqlalchemy.orm import with_polymorphic
from sqlalchemy.testing import AssertsCompiledSQL
from sqlalchemy.testing import eq_
from sqlalchemy.testing import fixtures
from sqlalchemy.testing.schema import Column
from sqlalchemy.testing.schema import Table


class SingleInheritanceTest(testing.AssertsCompiledSQL, fixtures.MappedTest):
    __dialect__ = "default"

    @classmethod
    def define_tables(cls, metadata):
        Table(
            "employees",
            metadata,
            Column(
                "employee_id",
                Integer,
                primary_key=True,
                test_needs_autoincrement=True,
            ),
            Column("name", String(50)),
            Column("manager_data", String(50)),
            Column("engineer_info", String(50)),
            Column("type", String(20)),
        )

        Table(
            "reports",
            metadata,
            Column(
                "report_id",
                Integer,
                primary_key=True,
                test_needs_autoincrement=True,
            ),
            Column("employee_id", ForeignKey("employees.employee_id")),
            Column("name", String(50)),
        )

    @classmethod
    def setup_classes(cls):
        global Employee, Manager, Engineer, JuniorEngineer

        class Employee(cls.Comparable):
            pass

        class Manager(Employee):
            pass

        class Engineer(Employee):
            pass

        class JuniorEngineer(Engineer):
            pass

    @classmethod
    def setup_mappers(cls):
        Employee, Manager, JuniorEngineer, employees, Engineer = (
            cls.classes.Employee,
            cls.classes.Manager,
            cls.classes.JuniorEngineer,
            cls.tables.employees,
            cls.classes.Engineer,
        )

        mapper(Employee, employees, polymorphic_on=employees.c.type)
        mapper(Manager, inherits=Employee, polymorphic_identity="manager")
        mapper(Engineer, inherits=Employee, polymorphic_identity="engineer")
        mapper(
            JuniorEngineer,
            inherits=Engineer,
            polymorphic_identity="juniorengineer",
        )

    def _fixture_one(self):
        JuniorEngineer, Manager, Engineer = (
            self.classes.JuniorEngineer,
            self.classes.Manager,
            self.classes.Engineer,
        )

        session = create_session()

        m1 = Manager(name="Tom", manager_data="knows how to manage things")
        e1 = Engineer(name="Kurt", engineer_info="knows how to hack")
        e2 = JuniorEngineer(name="Ed", engineer_info="oh that ed")
        session.add_all([m1, e1, e2])
        session.flush()
        return session, m1, e1, e2

    def test_single_inheritance(self):
        Employee, JuniorEngineer, Manager, Engineer = (
            self.classes.Employee,
            self.classes.JuniorEngineer,
            self.classes.Manager,
            self.classes.Engineer,
        )

        session, m1, e1, e2 = self._fixture_one()

        assert session.query(Employee).all() == [m1, e1, e2]
        assert session.query(Engineer).all() == [e1, e2]
        assert session.query(Manager).all() == [m1]
        assert session.query(JuniorEngineer).all() == [e2]

        m1 = session.query(Manager).one()
        session.expire(m1, ["manager_data"])
        eq_(m1.manager_data, "knows how to manage things")

        row = (
            session.query(Engineer.name, Engineer.employee_id)
            .filter(Engineer.name == "Kurt")
            .first()
        )
        assert row.name == "Kurt"
        assert row.employee_id == e1.employee_id

    def test_multi_qualification(self):
        Manager, Engineer = (self.classes.Manager, self.classes.Engineer)

        session, m1, e1, e2 = self._fixture_one()

        ealias = aliased(Engineer)
        eq_(session.query(Manager, ealias).all(), [(m1, e1), (m1, e2)])

        eq_(session.query(Manager.name).all(), [("Tom",)])

        eq_(
            session.query(Manager.name, ealias.name).all(),
            [("Tom", "Kurt"), ("Tom", "Ed")],
        )

        eq_(
            session.query(
                func.upper(Manager.name), func.upper(ealias.name)
            ).all(),
            [("TOM", "KURT"), ("TOM", "ED")],
        )

        eq_(
            session.query(Manager).add_entity(ealias).all(),
            [(m1, e1), (m1, e2)],
        )

        eq_(
            session.query(Manager.name).add_column(ealias.name).all(),
            [("Tom", "Kurt"), ("Tom", "Ed")],
        )

        # TODO: I think raise error on this for now
        # self.assertEquals(
        #    session.query(Employee.name, Manager.manager_data,
        #    Engineer.engineer_info).all(),
        #    []
        # )

    def test_column_qualification(self):
        Employee, JuniorEngineer, Manager, Engineer = (
            self.classes.Employee,
            self.classes.JuniorEngineer,
            self.classes.Manager,
            self.classes.Engineer,
        )

        session, m1, e1, e2 = self._fixture_one()

        m1id, e1id, e2id = m1.employee_id, e1.employee_id, e2.employee_id

        def scalar(q):
            return [x for x, in q]

        eq_(scalar(session.query(Employee.employee_id)), [m1id, e1id, e2id])

        eq_(scalar(session.query(Engineer.employee_id)), [e1id, e2id])

        eq_(scalar(session.query(Manager.employee_id)), [m1id])

        # this currently emits "WHERE type IN (?, ?) AND type IN (?, ?)",
        # so no result.
        eq_(session.query(Manager.employee_id, Engineer.employee_id).all(), [])

        eq_(scalar(session.query(JuniorEngineer.employee_id)), [e2id])

    def test_bundle_qualification(self):
        Employee, JuniorEngineer, Manager, Engineer = (
            self.classes.Employee,
            self.classes.JuniorEngineer,
            self.classes.Manager,
            self.classes.Engineer,
        )

        session, m1, e1, e2 = self._fixture_one()

        m1id, e1id, e2id = m1.employee_id, e1.employee_id, e2.employee_id

        def scalar(q):
            return [x[0] for x, in q]

        eq_(
            scalar(session.query(Bundle("name", Employee.employee_id))),
            [m1id, e1id, e2id],
        )

        eq_(
            scalar(session.query(Bundle("name", Engineer.employee_id))),
            [e1id, e2id],
        )

        eq_(scalar(session.query(Bundle("name", Manager.employee_id))), [m1id])

        # this currently emits "WHERE type IN (?, ?) AND type IN (?, ?)",
        # so no result.
        eq_(
            session.query(
                Bundle("name", Manager.employee_id, Engineer.employee_id)
            ).all(),
            [],
        )

        eq_(
            scalar(session.query(Bundle("name", JuniorEngineer.employee_id))),
            [e2id],
        )

    def test_from_self(self):
        Engineer = self.classes.Engineer

        sess = create_session()
        self.assert_compile(
            sess.query(Engineer).from_self(),
            "SELECT anon_1.employees_employee_id AS "
            "anon_1_employees_employee_id, "
            "anon_1.employees_name AS "
            "anon_1_employees_name, "
            "anon_1.employees_manager_data AS "
            "anon_1_employees_manager_data, "
            "anon_1.employees_engineer_info AS "
            "anon_1_employees_engineer_info, "
            "anon_1.employees_type AS "
            "anon_1_employees_type FROM (SELECT "
            "employees.employee_id AS "
            "employees_employee_id, employees.name AS "
            "employees_name, employees.manager_data AS "
            "employees_manager_data, "
            "employees.engineer_info AS "
            "employees_engineer_info, employees.type "
            "AS employees_type FROM employees WHERE "
            "employees.type IN (:type_1, :type_2)) AS "
            "anon_1",
            use_default_dialect=True,
        )

    def test_select_from_aliased_w_subclass(self):
        Engineer = self.classes.Engineer

        sess = create_session()

        a1 = aliased(Engineer)
        self.assert_compile(
            sess.query(a1.employee_id).select_from(a1),
            "SELECT employees_1.employee_id AS employees_1_employee_id "
            "FROM employees AS employees_1 WHERE employees_1.type "
            "IN (:type_1, :type_2)",
        )

        self.assert_compile(
            sess.query(literal("1")).select_from(a1),
            "SELECT :param_1 AS param_1 FROM employees AS employees_1 "
            "WHERE employees_1.type IN (:type_1, :type_2)",
        )

    def test_union_modifiers(self):
        Engineer, Manager = self.classes("Engineer", "Manager")

        sess = create_session()
        q1 = sess.query(Engineer).filter(Engineer.engineer_info == "foo")
        q2 = sess.query(Manager).filter(Manager.manager_data == "bar")

        assert_sql = (
            "SELECT anon_1.employees_employee_id AS "
            "anon_1_employees_employee_id, "
            "anon_1.employees_name AS anon_1_employees_name, "
            "anon_1.employees_manager_data AS anon_1_employees_manager_data, "
            "anon_1.employees_engineer_info AS anon_1_employees_engineer_info, "  # noqa
            "anon_1.employees_type AS anon_1_employees_type "
            "FROM (SELECT employees.employee_id AS employees_employee_id, "
            "employees.name AS employees_name, "
            "employees.manager_data AS employees_manager_data, "
            "employees.engineer_info AS employees_engineer_info, "
            "employees.type AS employees_type FROM employees "
            "WHERE employees.engineer_info = :engineer_info_1 "
            "AND employees.type IN (:type_1, :type_2) "
            "%(token)s "
            "SELECT employees.employee_id AS employees_employee_id, "
            "employees.name AS employees_name, "
            "employees.manager_data AS employees_manager_data, "
            "employees.engineer_info AS employees_engineer_info, "
            "employees.type AS employees_type FROM employees "
            "WHERE employees.manager_data = :manager_data_1 "
            "AND employees.type IN (:type_3)) AS anon_1"
        )

        for meth, token in [
            (q1.union, "UNION"),
            (q1.union_all, "UNION ALL"),
            (q1.except_, "EXCEPT"),
            (q1.except_all, "EXCEPT ALL"),
            (q1.intersect, "INTERSECT"),
            (q1.intersect_all, "INTERSECT ALL"),
        ]:
            self.assert_compile(
                meth(q2),
                assert_sql % {"token": token},
                checkparams={
                    "manager_data_1": "bar",
                    "type_2": "juniorengineer",
                    "type_3": "manager",
                    "engineer_info_1": "foo",
                    "type_1": "engineer",
                },
            )

    def test_from_self_count(self):
        Engineer = self.classes.Engineer

        sess = create_session()
        col = func.count(literal_column("*"))
        self.assert_compile(
            sess.query(Engineer.employee_id).from_self(col),
            "SELECT count(*) AS count_1 "
            "FROM (SELECT employees.employee_id AS employees_employee_id "
            "FROM employees "
            "WHERE employees.type IN (:type_1, :type_2)) AS anon_1",
            use_default_dialect=True,
        )

    def test_select_from_count(self):
        Manager, Engineer = (self.classes.Manager, self.classes.Engineer)

        sess = create_session()
        m1 = Manager(name="Tom", manager_data="data1")
        e1 = Engineer(name="Kurt", engineer_info="knows how to hack")
        sess.add_all([m1, e1])
        sess.flush()

        eq_(sess.query(func.count(1)).select_from(Manager).all(), [(1,)])

    def test_select_from_subquery(self):
        Manager, JuniorEngineer, employees, Engineer = (
            self.classes.Manager,
            self.classes.JuniorEngineer,
            self.tables.employees,
            self.classes.Engineer,
        )

        sess = create_session()
        m1 = Manager(name="Tom", manager_data="data1")
        m2 = Manager(name="Tom2", manager_data="data2")
        e1 = Engineer(name="Kurt", engineer_info="knows how to hack")
        e2 = JuniorEngineer(name="Ed", engineer_info="oh that ed")
        sess.add_all([m1, m2, e1, e2])
        sess.flush()

        eq_(
            sess.query(Manager)
            .select_from(employees.select().limit(10))
            .all(),
            [m1, m2],
        )

    def test_count(self):
        Employee = self.classes.Employee
        JuniorEngineer = self.classes.JuniorEngineer
        Manager = self.classes.Manager
        Engineer = self.classes.Engineer

        sess = create_session()
        m1 = Manager(name="Tom", manager_data="data1")
        m2 = Manager(name="Tom2", manager_data="data2")
        e1 = Engineer(name="Kurt", engineer_info="data3")
        e2 = JuniorEngineer(name="marvin", engineer_info="data4")
        sess.add_all([m1, m2, e1, e2])
        sess.flush()

        eq_(sess.query(Manager).count(), 2)
        eq_(sess.query(Engineer).count(), 2)
        eq_(sess.query(Employee).count(), 4)

        eq_(sess.query(Manager).filter(Manager.name.like("%m%")).count(), 2)
        eq_(sess.query(Employee).filter(Employee.name.like("%m%")).count(), 3)

    def test_exists_standalone(self):
        Engineer = self.classes.Engineer

        sess = create_session()

        self.assert_compile(
            sess.query(
                sess.query(Engineer).filter(Engineer.name == "foo").exists()
            ),
            "SELECT EXISTS (SELECT 1 FROM employees WHERE "
            "employees.name = :name_1 AND employees.type "
            "IN (:type_1, :type_2)) AS anon_1",
        )

    def test_type_filtering(self):
        Employee, Manager, reports, Engineer = (
            self.classes.Employee,
            self.classes.Manager,
            self.tables.reports,
            self.classes.Engineer,
        )

        class Report(fixtures.ComparableEntity):
            pass

        mapper(
            Report,
            reports,
            properties={"employee": relationship(Employee, backref="reports")},
        )
        sess = create_session()

        m1 = Manager(name="Tom", manager_data="data1")
        r1 = Report(employee=m1)
        sess.add_all([m1, r1])
        sess.flush()
        rq = sess.query(Report)

        assert (
            len(rq.filter(Report.employee.of_type(Manager).has()).all()) == 1
        )
        assert (
            len(rq.filter(Report.employee.of_type(Engineer).has()).all()) == 0
        )

    def test_type_joins(self):
        Employee, Manager, reports, Engineer = (
            self.classes.Employee,
            self.classes.Manager,
            self.tables.reports,
            self.classes.Engineer,
        )

        class Report(fixtures.ComparableEntity):
            pass

        mapper(
            Report,
            reports,
            properties={"employee": relationship(Employee, backref="reports")},
        )
        sess = create_session()

        m1 = Manager(name="Tom", manager_data="data1")
        r1 = Report(employee=m1)
        sess.add_all([m1, r1])
        sess.flush()

        rq = sess.query(Report)

        assert len(rq.join(Report.employee.of_type(Manager)).all()) == 1
        assert len(rq.join(Report.employee.of_type(Engineer)).all()) == 0


class RelationshipFromSingleTest(
    testing.AssertsCompiledSQL, fixtures.MappedTest
):
    @classmethod
    def define_tables(cls, metadata):
        Table(
            "employee",
            metadata,
            Column(
                "id", Integer, primary_key=True, test_needs_autoincrement=True
            ),
            Column("name", String(50)),
            Column("type", String(20)),
        )

        Table(
            "employee_stuff",
            metadata,
            Column(
                "id", Integer, primary_key=True, test_needs_autoincrement=True
            ),
            Column("employee_id", Integer, ForeignKey("employee.id")),
            Column("name", String(50)),
        )

    @classmethod
    def setup_classes(cls):
        class Employee(cls.Comparable):
            pass

        class Manager(Employee):
            pass

        class Stuff(cls.Comparable):
            pass

    def test_subquery_load(self):
        employee, employee_stuff, Employee, Stuff, Manager = (
            self.tables.employee,
            self.tables.employee_stuff,
            self.classes.Employee,
            self.classes.Stuff,
            self.classes.Manager,
        )

        mapper(
            Employee,
            employee,
            polymorphic_on=employee.c.type,
            polymorphic_identity="employee",
        )
        mapper(
            Manager,
            inherits=Employee,
            polymorphic_identity="manager",
            properties={"stuff": relationship(Stuff)},
        )
        mapper(Stuff, employee_stuff)

        sess = create_session()
        context = (
            sess.query(Manager)
            .options(subqueryload("stuff"))
            ._compile_context()
        )
        subq = context.attributes[
            (
                "subquery",
                (class_mapper(Manager), class_mapper(Manager).attrs.stuff),
            )
        ]

        self.assert_compile(
            subq,
            "SELECT employee_stuff.id AS "
            "employee_stuff_id, employee_stuff.employee"
            "_id AS employee_stuff_employee_id, "
            "employee_stuff.name AS "
            "employee_stuff_name, anon_1.employee_id "
            "AS anon_1_employee_id FROM (SELECT "
            "employee.id AS employee_id FROM employee "
            "WHERE employee.type IN (:type_1)) AS anon_1 "
            "JOIN employee_stuff ON anon_1.employee_id "
            "= employee_stuff.employee_id",
            use_default_dialect=True,
        )


class RelationshipToSingleTest(
    testing.AssertsCompiledSQL, fixtures.MappedTest
):
    __dialect__ = "default"

    @classmethod
    def define_tables(cls, metadata):
        Table(
            "employees",
            metadata,
            Column(
                "employee_id",
                Integer,
                primary_key=True,
                test_needs_autoincrement=True,
            ),
            Column("name", String(50)),
            Column("manager_data", String(50)),
            Column("engineer_info", String(50)),
            Column("type", String(20)),
            Column("company_id", Integer, ForeignKey("companies.company_id")),
        )

        Table(
            "companies",
            metadata,
            Column(
                "company_id",
                Integer,
                primary_key=True,
                test_needs_autoincrement=True,
            ),
            Column("name", String(50)),
        )

    @classmethod
    def setup_classes(cls):
        class Company(cls.Comparable):
            pass

        class Employee(cls.Comparable):
            pass

        class Manager(Employee):
            pass

        class Engineer(Employee):
            pass

        class JuniorEngineer(Engineer):
            pass

    def test_of_type(self):
        (
            JuniorEngineer,
            Company,
            companies,
            Manager,
            Employee,
            employees,
            Engineer,
        ) = (
            self.classes.JuniorEngineer,
            self.classes.Company,
            self.tables.companies,
            self.classes.Manager,
            self.classes.Employee,
            self.tables.employees,
            self.classes.Engineer,
        )

        mapper(
            Company,
            companies,
            properties={
                "employees": relationship(Employee, backref="company")
            },
        )
        mapper(Employee, employees, polymorphic_on=employees.c.type)
        mapper(Manager, inherits=Employee, polymorphic_identity="manager")
        mapper(Engineer, inherits=Employee, polymorphic_identity="engineer")
        mapper(
            JuniorEngineer,
            inherits=Engineer,
            polymorphic_identity="juniorengineer",
        )
        sess = sessionmaker()()

        c1 = Company(name="c1")
        c2 = Company(name="c2")

        m1 = Manager(name="Tom", manager_data="data1", company=c1)
        m2 = Manager(name="Tom2", manager_data="data2", company=c2)
        e1 = Engineer(
            name="Kurt", engineer_info="knows how to hack", company=c2
        )
        e2 = JuniorEngineer(name="Ed", engineer_info="oh that ed", company=c1)
        sess.add_all([c1, c2, m1, m2, e1, e2])
        sess.commit()
        sess.expunge_all()
        eq_(
            sess.query(Company)
            .filter(Company.employees.of_type(JuniorEngineer).any())
            .all(),
            [Company(name="c1")],
        )

        eq_(
            sess.query(Company)
            .join(Company.employees.of_type(JuniorEngineer))
            .all(),
            [Company(name="c1")],
        )

    def test_of_type_aliased_fromjoinpoint(self):
        Company, Employee, Engineer = (
            self.classes.Company,
            self.classes.Employee,
            self.classes.Engineer,
        )
        companies, employees = self.tables.companies, self.tables.employees

        mapper(
            Company, companies, properties={"employee": relationship(Employee)}
        )
        mapper(Employee, employees, polymorphic_on=employees.c.type)
        mapper(Engineer, inherits=Employee, polymorphic_identity="engineer")

        sess = create_session()
        self.assert_compile(
            sess.query(Company).outerjoin(
                Company.employee.of_type(Engineer),
                aliased=True,
                from_joinpoint=True,
            ),
            "SELECT companies.company_id AS companies_company_id, "
            "companies.name AS companies_name FROM companies "
            "LEFT OUTER JOIN employees AS employees_1 ON "
            "companies.company_id = employees_1.company_id "
            "AND employees_1.type IN (:type_1)",
        )

    def test_join_explicit_onclause_no_discriminator(self):
        # test issue #3462
        Company, Employee, Engineer = (
            self.classes.Company,
            self.classes.Employee,
            self.classes.Engineer,
        )
        companies, employees = self.tables.companies, self.tables.employees

        mapper(
            Company,
            companies,
            properties={"employees": relationship(Employee)},
        )
        mapper(Employee, employees)
        mapper(Engineer, inherits=Employee)

        sess = create_session()
        self.assert_compile(
            sess.query(Company, Engineer.name).join(
                Engineer, Company.company_id == Engineer.company_id
            ),
            "SELECT companies.company_id AS companies_company_id, "
            "companies.name AS companies_name, "
            "employees.name AS employees_name "
            "FROM companies JOIN "
            "employees ON companies.company_id = employees.company_id",
        )

    def test_outer_join_prop(self):
        Company, Employee, Engineer = (
            self.classes.Company,
            self.classes.Employee,
            self.classes.Engineer,
        )
        companies, employees = self.tables.companies, self.tables.employees

        mapper(
            Company,
            companies,
            properties={"engineers": relationship(Engineer)},
        )
        mapper(Employee, employees, polymorphic_on=employees.c.type)
        mapper(Engineer, inherits=Employee, polymorphic_identity="engineer")

        sess = create_session()
        self.assert_compile(
            sess.query(Company, Engineer.name).outerjoin("engineers"),
            "SELECT companies.company_id AS companies_company_id, "
            "companies.name AS companies_name, "
            "employees.name AS employees_name "
            "FROM companies LEFT OUTER JOIN employees ON companies.company_id "
            "= employees.company_id AND employees.type IN (:type_1)",
        )

    def test_outer_join_prop_alias(self):
        Company, Employee, Engineer = (
            self.classes.Company,
            self.classes.Employee,
            self.classes.Engineer,
        )
        companies, employees = self.tables.companies, self.tables.employees

        mapper(
            Company,
            companies,
            properties={"engineers": relationship(Engineer)},
        )
        mapper(Employee, employees, polymorphic_on=employees.c.type)
        mapper(Engineer, inherits=Employee, polymorphic_identity="engineer")

        eng_alias = aliased(Engineer)
        sess = create_session()
        self.assert_compile(
            sess.query(Company, eng_alias.name).outerjoin(
                eng_alias, Company.engineers
            ),
            "SELECT companies.company_id AS companies_company_id, "
            "companies.name AS companies_name, employees_1.name AS "
            "employees_1_name FROM companies LEFT OUTER "
            "JOIN employees AS employees_1 ON companies.company_id "
            "= employees_1.company_id AND employees_1.type IN (:type_1)",
        )

    def test_outer_join_literal_onclause(self):
        Company, Employee, Engineer = (
            self.classes.Company,
            self.classes.Employee,
            self.classes.Engineer,
        )
        companies, employees = self.tables.companies, self.tables.employees

        mapper(
            Company,
            companies,
            properties={"engineers": relationship(Engineer)},
        )
        mapper(Employee, employees, polymorphic_on=employees.c.type)
        mapper(Engineer, inherits=Employee, polymorphic_identity="engineer")

        sess = create_session()
        self.assert_compile(
            sess.query(Company, Engineer).outerjoin(
                Engineer, Company.company_id == Engineer.company_id
            ),
            "SELECT companies.company_id AS companies_company_id, "
            "companies.name AS companies_name, "
            "employees.employee_id AS employees_employee_id, "
            "employees.name AS employees_name, "
            "employees.manager_data AS employees_manager_data, "
            "employees.engineer_info AS employees_engineer_info, "
            "employees.type AS employees_type, "
            "employees.company_id AS employees_company_id FROM companies "
            "LEFT OUTER JOIN employees ON "
            "companies.company_id = employees.company_id "
            "AND employees.type IN (:type_1)",
        )

    def test_outer_join_literal_onclause_alias(self):
        Company, Employee, Engineer = (
            self.classes.Company,
            self.classes.Employee,
            self.classes.Engineer,
        )
        companies, employees = self.tables.companies, self.tables.employees

        mapper(
            Company,
            companies,
            properties={"engineers": relationship(Engineer)},
        )
        mapper(Employee, employees, polymorphic_on=employees.c.type)
        mapper(Engineer, inherits=Employee, polymorphic_identity="engineer")

        eng_alias = aliased(Engineer)
        sess = create_session()
        self.assert_compile(
            sess.query(Company, eng_alias).outerjoin(
                eng_alias, Company.company_id == eng_alias.company_id
            ),
            "SELECT companies.company_id AS companies_company_id, "
            "companies.name AS companies_name, "
            "employees_1.employee_id AS employees_1_employee_id, "
            "employees_1.name AS employees_1_name, "
            "employees_1.manager_data AS employees_1_manager_data, "
            "employees_1.engineer_info AS employees_1_engineer_info, "
            "employees_1.type AS employees_1_type, "
            "employees_1.company_id AS employees_1_company_id "
            "FROM companies LEFT OUTER JOIN employees AS employees_1 ON "
            "companies.company_id = employees_1.company_id "
            "AND employees_1.type IN (:type_1)",
        )

    def test_outer_join_no_onclause(self):
        Company, Employee, Engineer = (
            self.classes.Company,
            self.classes.Employee,
            self.classes.Engineer,
        )
        companies, employees = self.tables.companies, self.tables.employees

        mapper(
            Company,
            companies,
            properties={"engineers": relationship(Engineer)},
        )
        mapper(Employee, employees, polymorphic_on=employees.c.type)
        mapper(Engineer, inherits=Employee, polymorphic_identity="engineer")

        sess = create_session()
        self.assert_compile(
            sess.query(Company, Engineer).outerjoin(Engineer),
            "SELECT companies.company_id AS companies_company_id, "
            "companies.name AS companies_name, "
            "employees.employee_id AS employees_employee_id, "
            "employees.name AS employees_name, "
            "employees.manager_data AS employees_manager_data, "
            "employees.engineer_info AS employees_engineer_info, "
            "employees.type AS employees_type, "
            "employees.company_id AS employees_company_id "
            "FROM companies LEFT OUTER JOIN employees ON "
            "companies.company_id = employees.company_id "
            "AND employees.type IN (:type_1)",
        )

    def test_outer_join_no_onclause_alias(self):
        Company, Employee, Engineer = (
            self.classes.Company,
            self.classes.Employee,
            self.classes.Engineer,
        )
        companies, employees = self.tables.companies, self.tables.employees

        mapper(
            Company,
            companies,
            properties={"engineers": relationship(Engineer)},
        )
        mapper(Employee, employees, polymorphic_on=employees.c.type)
        mapper(Engineer, inherits=Employee, polymorphic_identity="engineer")

        eng_alias = aliased(Engineer)
        sess = create_session()
        self.assert_compile(
            sess.query(Company, eng_alias).outerjoin(eng_alias),
            "SELECT companies.company_id AS companies_company_id, "
            "companies.name AS companies_name, "
            "employees_1.employee_id AS employees_1_employee_id, "
            "employees_1.name AS employees_1_name, "
            "employees_1.manager_data AS employees_1_manager_data, "
            "employees_1.engineer_info AS employees_1_engineer_info, "
            "employees_1.type AS employees_1_type, "
            "employees_1.company_id AS employees_1_company_id "
            "FROM companies LEFT OUTER JOIN employees AS employees_1 ON "
            "companies.company_id = employees_1.company_id "
            "AND employees_1.type IN (:type_1)",
        )

    def test_correlated_column_select(self):
        Company, Employee, Engineer = (
            self.classes.Company,
            self.classes.Employee,
            self.classes.Engineer,
        )
        companies, employees = self.tables.companies, self.tables.employees

        mapper(Company, companies)
        mapper(
            Employee,
            employees,
            polymorphic_on=employees.c.type,
            properties={"company": relationship(Company)},
        )
        mapper(Engineer, inherits=Employee, polymorphic_identity="engineer")

        sess = create_session()
        engineer_count = (
            sess.query(func.count(Engineer.employee_id))
            .select_from(Engineer)
            .filter(Engineer.company_id == Company.company_id)
            .correlate(Company)
            .as_scalar()
        )

        self.assert_compile(
            sess.query(Company.company_id, engineer_count),
            "SELECT companies.company_id AS companies_company_id, "
            "(SELECT count(employees.employee_id) AS count_1 "
            "FROM employees WHERE employees.company_id = "
            "companies.company_id AND employees.type IN (:type_1)) AS anon_1 "
            "FROM companies",
        )

    def test_no_aliasing_from_overlap(self):
        # test [ticket:3233]

        Company, Employee, Engineer, Manager = (
            self.classes.Company,
            self.classes.Employee,
            self.classes.Engineer,
            self.classes.Manager,
        )

        companies, employees = self.tables.companies, self.tables.employees

        mapper(
            Company,
            companies,
            properties={
                "employees": relationship(Employee, backref="company")
            },
        )
        mapper(Employee, employees, polymorphic_on=employees.c.type)
        mapper(Engineer, inherits=Employee, polymorphic_identity="engineer")
        mapper(Manager, inherits=Employee, polymorphic_identity="manager")

        s = create_session()

        q1 = (
            s.query(Engineer)
            .join(Engineer.company)
            .join(Manager, Company.employees)
        )

        q2 = (
            s.query(Engineer)
            .join(Engineer.company)
            .join(Manager, Company.company_id == Manager.company_id)
        )

        q3 = (
            s.query(Engineer)
            .join(Engineer.company)
            .join(Manager, Company.employees.of_type(Manager))
        )

        q4 = (
            s.query(Engineer)
            .join(Company, Company.company_id == Engineer.company_id)
            .join(Manager, Company.employees.of_type(Manager))
        )

        q5 = (
            s.query(Engineer)
            .join(Company, Company.company_id == Engineer.company_id)
            .join(Manager, Company.company_id == Manager.company_id)
        )

        # note that the query is incorrect SQL; we JOIN to
        # employees twice.   However, this is what's expected so we seek
        # to be consistent; previously, aliasing would sneak in due to the
        # nature of the "left" side.
        for q in [q1, q2, q3, q4, q5]:
            self.assert_compile(
                q,
                "SELECT employees.employee_id AS employees_employee_id, "
                "employees.name AS employees_name, "
                "employees.manager_data AS employees_manager_data, "
                "employees.engineer_info AS employees_engineer_info, "
                "employees.type AS employees_type, "
                "employees.company_id AS employees_company_id "
                "FROM employees JOIN companies "
                "ON companies.company_id = employees.company_id "
                "JOIN employees "
                "ON companies.company_id = employees.company_id "
                "AND employees.type IN (:type_1) "
                "WHERE employees.type IN (:type_2)",
            )

    def test_relationship_to_subclass(self):
        (
            JuniorEngineer,
            Company,
            companies,
            Manager,
            Employee,
            employees,
            Engineer,
        ) = (
            self.classes.JuniorEngineer,
            self.classes.Company,
            self.tables.companies,
            self.classes.Manager,
            self.classes.Employee,
            self.tables.employees,
            self.classes.Engineer,
        )

        mapper(
            Company,
            companies,
            properties={"engineers": relationship(Engineer)},
        )
        mapper(
            Employee,
            employees,
            polymorphic_on=employees.c.type,
            properties={"company": relationship(Company)},
        )
        mapper(Manager, inherits=Employee, polymorphic_identity="manager")
        mapper(Engineer, inherits=Employee, polymorphic_identity="engineer")
        mapper(
            JuniorEngineer,
            inherits=Engineer,
            polymorphic_identity="juniorengineer",
        )
        sess = sessionmaker()()

        c1 = Company(name="c1")
        c2 = Company(name="c2")

        m1 = Manager(name="Tom", manager_data="data1", company=c1)
        m2 = Manager(name="Tom2", manager_data="data2", company=c2)
        e1 = Engineer(
            name="Kurt", engineer_info="knows how to hack", company=c2
        )
        e2 = JuniorEngineer(name="Ed", engineer_info="oh that ed", company=c1)
        sess.add_all([c1, c2, m1, m2, e1, e2])
        sess.commit()

        eq_(c1.engineers, [e2])
        eq_(c2.engineers, [e1])

        sess.expunge_all()
        eq_(
            sess.query(Company).order_by(Company.name).all(),
            [
                Company(name="c1", engineers=[JuniorEngineer(name="Ed")]),
                Company(name="c2", engineers=[Engineer(name="Kurt")]),
            ],
        )

        # eager load join should limit to only "Engineer"
        sess.expunge_all()
        eq_(
            sess.query(Company)
            .options(joinedload("engineers"))
            .order_by(Company.name)
            .all(),
            [
                Company(name="c1", engineers=[JuniorEngineer(name="Ed")]),
                Company(name="c2", engineers=[Engineer(name="Kurt")]),
            ],
        )

        # join() to Company.engineers, Employee as the requested entity
        sess.expunge_all()
        eq_(
            sess.query(Company, Employee)
            .join(Company.engineers)
            .order_by(Company.name)
            .all(),
            [
                (Company(name="c1"), JuniorEngineer(name="Ed")),
                (Company(name="c2"), Engineer(name="Kurt")),
            ],
        )

        # join() to Company.engineers, Engineer as the requested entity.
        # this actually applies the IN criterion twice which is less than
        # ideal.
        sess.expunge_all()
        eq_(
            sess.query(Company, Engineer)
            .join(Company.engineers)
            .order_by(Company.name)
            .all(),
            [
                (Company(name="c1"), JuniorEngineer(name="Ed")),
                (Company(name="c2"), Engineer(name="Kurt")),
            ],
        )

        # join() to Company.engineers without any Employee/Engineer entity
        sess.expunge_all()
        eq_(
            sess.query(Company)
            .join(Company.engineers)
            .filter(Engineer.name.in_(["Tom", "Kurt"]))
            .all(),
            [Company(name="c2")],
        )

        # this however fails as it does not limit the subtypes to just
        # "Engineer". with joins constructed by filter(), we seem to be
        # following a policy where we don't try to make decisions on how to
        # join to the target class, whereas when using join() we seem to have
        # a lot more capabilities. we might want to document
        # "advantages of join() vs. straight filtering", or add a large
        # section to "inheritance" laying out all the various behaviors Query
        # has.
        @testing.fails_on_everything_except()
        def go():
            sess.expunge_all()
            eq_(
                sess.query(Company)
                .filter(Company.company_id == Engineer.company_id)
                .filter(Engineer.name.in_(["Tom", "Kurt"]))
                .all(),
                [Company(name="c2")],
            )

        go()


class ManyToManyToSingleTest(fixtures.MappedTest, AssertsCompiledSQL):
    __dialect__ = "default"

    @classmethod
    def define_tables(cls, metadata):
        Table(
            "parent",
            metadata,
            Column(
                "id", Integer, primary_key=True, test_needs_autoincrement=True
            ),
        )
        Table(
            "m2m",
            metadata,
            Column(
                "parent_id", Integer, ForeignKey("parent.id"), primary_key=True
            ),
            Column(
                "child_id", Integer, ForeignKey("child.id"), primary_key=True
            ),
        )
        Table(
            "child",
            metadata,
            Column(
                "id", Integer, primary_key=True, test_needs_autoincrement=True
            ),
            Column("discriminator", String(20)),
            Column("name", String(20)),
        )

    @classmethod
    def setup_classes(cls):
        class Parent(cls.Comparable):
            pass

        class Child(cls.Comparable):
            pass

        class SubChild1(Child):
            pass

        class SubChild2(Child):
            pass

    @classmethod
    def setup_mappers(cls):
        mapper(
            cls.classes.Parent,
            cls.tables.parent,
            properties={
                "s1": relationship(
                    cls.classes.SubChild1,
                    secondary=cls.tables.m2m,
                    uselist=False,
                ),
                "s2": relationship(
                    cls.classes.SubChild2, secondary=cls.tables.m2m
                ),
            },
        )
        mapper(
            cls.classes.Child,
            cls.tables.child,
            polymorphic_on=cls.tables.child.c.discriminator,
        )
        mapper(
            cls.classes.SubChild1,
            inherits=cls.classes.Child,
            polymorphic_identity="sub1",
        )
        mapper(
            cls.classes.SubChild2,
            inherits=cls.classes.Child,
            polymorphic_identity="sub2",
        )

    @classmethod
    def insert_data(cls, connection):
        Parent = cls.classes.Parent
        SubChild1 = cls.classes.SubChild1
        SubChild2 = cls.classes.SubChild2
        s = Session(connection)
        s.add_all(
            [
                Parent(
                    s1=SubChild1(name="sc1_1"),
                    s2=[SubChild2(name="sc2_1"), SubChild2(name="sc2_2")],
                )
            ]
        )
        s.commit()

    def test_eager_join(self):
        Parent = self.classes.Parent
        SubChild1 = self.classes.SubChild1

        s = Session()

        p1 = s.query(Parent).options(joinedload(Parent.s1)).all()[0]
        eq_(p1.__dict__["s1"], SubChild1(name="sc1_1"))

    def test_manual_join(self):
        Parent = self.classes.Parent
        Child = self.classes.Child
        SubChild1 = self.classes.SubChild1

        s = Session()

        p1, c1 = s.query(Parent, Child).outerjoin(Parent.s1).all()[0]
        eq_(c1, SubChild1(name="sc1_1"))

    def test_assert_join_sql(self):
        Parent = self.classes.Parent
        Child = self.classes.Child

        s = Session()

        self.assert_compile(
            s.query(Parent, Child).outerjoin(Parent.s1),
            "SELECT parent.id AS parent_id, child.id AS child_id, "
            "child.discriminator AS child_discriminator, "
            "child.name AS child_name "
            "FROM parent LEFT OUTER JOIN (m2m AS m2m_1 "
            "JOIN child ON child.id = m2m_1.child_id "
            "AND child.discriminator IN (:discriminator_1)) "
            "ON parent.id = m2m_1.parent_id",
        )

    def test_assert_joinedload_sql(self):
        Parent = self.classes.Parent

        s = Session()

        self.assert_compile(
            s.query(Parent).options(joinedload(Parent.s1)),
            "SELECT parent.id AS parent_id, child_1.id AS child_1_id, "
            "child_1.discriminator AS child_1_discriminator, "
            "child_1.name AS child_1_name "
            "FROM parent LEFT OUTER JOIN "
            "(m2m AS m2m_1 JOIN child AS child_1 "
            "ON child_1.id = m2m_1.child_id AND child_1.discriminator "
            "IN (:discriminator_1)) ON parent.id = m2m_1.parent_id",
        )


class SingleOnJoinedTest(fixtures.MappedTest):
    @classmethod
    def define_tables(cls, metadata):
        global persons_table, employees_table

        persons_table = Table(
            "persons",
            metadata,
            Column(
                "person_id",
                Integer,
                primary_key=True,
                test_needs_autoincrement=True,
            ),
            Column("name", String(50)),
            Column("type", String(20), nullable=False),
        )

        employees_table = Table(
            "employees",
            metadata,
            Column(
                "person_id",
                Integer,
                ForeignKey("persons.person_id"),
                primary_key=True,
            ),
            Column("employee_data", String(50)),
            Column("manager_data", String(50)),
        )

    def test_single_on_joined(self):
        class Person(fixtures.ComparableEntity):
            pass

        class Employee(Person):
            pass

        class Manager(Employee):
            pass

        mapper(
            Person,
            persons_table,
            polymorphic_on=persons_table.c.type,
            polymorphic_identity="person",
        )
        mapper(
            Employee,
            employees_table,
            inherits=Person,
            polymorphic_identity="engineer",
        )
        mapper(Manager, inherits=Employee, polymorphic_identity="manager")

        sess = create_session()
        sess.add(Person(name="p1"))
        sess.add(Employee(name="e1", employee_data="ed1"))
        sess.add(Manager(name="m1", employee_data="ed2", manager_data="md1"))
        sess.flush()
        sess.expunge_all()

        eq_(
            sess.query(Person).order_by(Person.person_id).all(),
            [
                Person(name="p1"),
                Employee(name="e1", employee_data="ed1"),
                Manager(name="m1", employee_data="ed2", manager_data="md1"),
            ],
        )
        sess.expunge_all()

        eq_(
            sess.query(Employee).order_by(Person.person_id).all(),
            [
                Employee(name="e1", employee_data="ed1"),
                Manager(name="m1", employee_data="ed2", manager_data="md1"),
            ],
        )
        sess.expunge_all()

        eq_(
            sess.query(Manager).order_by(Person.person_id).all(),
            [Manager(name="m1", employee_data="ed2", manager_data="md1")],
        )
        sess.expunge_all()

        def go():
            eq_(
                sess.query(Person)
                .with_polymorphic("*")
                .order_by(Person.person_id)
                .all(),
                [
                    Person(name="p1"),
                    Employee(name="e1", employee_data="ed1"),
                    Manager(
                        name="m1", employee_data="ed2", manager_data="md1"
                    ),
                ],
            )

        self.assert_sql_count(testing.db, go, 1)


class SingleFromPolySelectableTest(
    fixtures.DeclarativeMappedTest, AssertsCompiledSQL
):
    __dialect__ = "default"

    @classmethod
    def setup_classes(cls, with_polymorphic=None, include_sub_defaults=False):
        Base = cls.DeclarativeBasic

        class Employee(Base):
            __tablename__ = "employee"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
            type = Column(String(50))

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": type,
            }

        class Engineer(Employee):
            __tablename__ = "engineer"
            id = Column(Integer, ForeignKey("employee.id"), primary_key=True)
            engineer_info = Column(String(50))
            manager_id = Column(ForeignKey("manager.id"))
            __mapper_args__ = {"polymorphic_identity": "engineer"}

        class Manager(Employee):
            __tablename__ = "manager"
            id = Column(Integer, ForeignKey("employee.id"), primary_key=True)
            manager_data = Column(String(50))
            __mapper_args__ = {"polymorphic_identity": "manager"}

        class Boss(Manager):
            __mapper_args__ = {"polymorphic_identity": "boss"}

    def _with_poly_fixture(self):
        employee = self.classes.Employee.__table__
        engineer = self.classes.Engineer.__table__
        manager = self.classes.Manager.__table__

        poly = (
            select(
                [
                    employee.c.id,
                    employee.c.type,
                    employee.c.name,
                    manager.c.manager_data,
                    null().label("engineer_info"),
                    null().label("manager_id"),
                ]
            )
            .select_from(employee.join(manager))
            .apply_labels()
            .union_all(
                select(
                    [
                        employee.c.id,
                        employee.c.type,
                        employee.c.name,
                        null().label("manager_data"),
                        engineer.c.engineer_info,
                        engineer.c.manager_id,
                    ]
                )
                .select_from(employee.join(engineer))
                .apply_labels()
            )
            .alias()
        )

        return poly

    def test_wpoly_single_inh_subclass(self):
        poly = with_polymorphic(
            self.classes.Employee,
            [self.classes.Boss, self.classes.Manager, self.classes.Engineer],
            self._with_poly_fixture(),
        )
        s = Session()
        q = s.query(poly.Boss)
        self.assert_compile(
            q,
            "SELECT "
            "anon_1.employee_id AS anon_1_employee_id, "
            "anon_1.employee_name AS anon_1_employee_name, "
            "anon_1.employee_type AS anon_1_employee_type, "
            "anon_1.manager_manager_data AS anon_1_manager_manager_data "
            "FROM "
            "(SELECT "
            "employee.id AS employee_id, employee.type AS employee_type, "
            "employee.name AS employee_name, "
            "manager.manager_data AS manager_manager_data, "
            "NULL AS engineer_info, NULL AS manager_id FROM employee "
            "JOIN manager ON employee.id = manager.id "
            "UNION ALL "
            "SELECT employee.id AS employee_id, "
            "employee.type AS employee_type, "
            "employee.name AS employee_name, NULL AS manager_data, "
            "engineer.engineer_info AS engineer_engineer_info, "
            "engineer.manager_id AS engineer_manager_id "
            "FROM employee JOIN engineer ON employee.id = engineer.id) "
            "AS anon_1 "
            "WHERE anon_1.employee_type IN (:type_1)",
        )

    def test_query_wpoly_single_inh_subclass(self):
        Boss = self.classes.Boss

        poly = self._with_poly_fixture()

        s = Session()
        q = s.query(Boss).with_polymorphic(Boss, poly)
        self.assert_compile(
            q,
            "SELECT anon_1.employee_id AS anon_1_employee_id, "
            "anon_1.employee_name AS anon_1_employee_name, "
            "anon_1.employee_type AS anon_1_employee_type, "
            "anon_1.manager_manager_data AS anon_1_manager_manager_data "
            "FROM (SELECT employee.id AS employee_id, employee.type "
            "AS employee_type, employee.name AS employee_name, "
            "manager.manager_data AS manager_manager_data, "
            "NULL AS engineer_info, NULL AS manager_id FROM employee "
            "JOIN manager ON employee.id = manager.id "
            "UNION ALL SELECT employee.id AS employee_id, "
            "employee.type AS employee_type, employee.name AS employee_name, "
            "NULL AS manager_data, "
            "engineer.engineer_info AS engineer_engineer_info, "
            "engineer.manager_id AS engineer_manager_id "
            "FROM employee JOIN engineer ON employee.id = engineer.id) "
            "AS anon_1 WHERE anon_1.employee_type IN (:type_1)",
        )

    def test_single_inh_subclass_join_joined_inh_subclass(self):
        Boss, Engineer = self.classes("Boss", "Engineer")
        s = Session()

        q = s.query(Boss).join(Engineer, Engineer.manager_id == Boss.id)

        self.assert_compile(
            q,
            "SELECT manager.id AS manager_id, employee.id AS employee_id, "
            "employee.name AS employee_name, "
            "employee.type AS employee_type, "
            "manager.manager_data AS manager_manager_data "
            "FROM employee JOIN manager ON employee.id = manager.id "
            "JOIN (employee AS employee_1 JOIN engineer AS engineer_1 "
            "ON employee_1.id = engineer_1.id) "
            "ON engineer_1.manager_id = manager.id "
            "WHERE employee.type IN (:type_1)",
        )

    def test_single_inh_subclass_join_wpoly_joined_inh_subclass(self):
        Boss = self.classes.Boss
        poly = with_polymorphic(
            self.classes.Employee,
            [self.classes.Boss, self.classes.Manager, self.classes.Engineer],
            self._with_poly_fixture(),
        )

        s = Session()

        q = s.query(Boss).join(
            poly.Engineer, poly.Engineer.manager_id == Boss.id
        )

        self.assert_compile(
            q,
            "SELECT manager.id AS manager_id, employee.id AS employee_id, "
            "employee.name AS employee_name, employee.type AS employee_type, "
            "manager.manager_data AS manager_manager_data "
            "FROM employee JOIN manager ON employee.id = manager.id "
            "JOIN (SELECT employee.id AS employee_id, "
            "employee.type AS employee_type, employee.name AS employee_name, "
            "manager.manager_data AS manager_manager_data, "
            "NULL AS engineer_info, NULL AS manager_id "
            "FROM employee JOIN manager ON employee.id = manager.id "
            "UNION ALL "
            "SELECT employee.id AS employee_id, "
            "employee.type AS employee_type, employee.name AS employee_name, "
            "NULL AS manager_data, "
            "engineer.engineer_info AS engineer_engineer_info, "
            "engineer.manager_id AS engineer_manager_id "
            "FROM employee "
            "JOIN engineer ON employee.id = engineer.id) AS anon_1 "
            "ON anon_1.manager_id = manager.id "
            "WHERE employee.type IN (:type_1)",
        )

    def test_joined_inh_subclass_join_single_inh_subclass(self):
        Engineer = self.classes.Engineer
        Boss = self.classes.Boss
        s = Session()

        q = s.query(Engineer).join(Boss, Engineer.manager_id == Boss.id)

        self.assert_compile(
            q,
            "SELECT engineer.id AS engineer_id, employee.id AS employee_id, "
            "employee.name AS employee_name, employee.type AS employee_type, "
            "engineer.engineer_info AS engineer_engineer_info, "
            "engineer.manager_id AS engineer_manager_id "
            "FROM employee JOIN engineer ON employee.id = engineer.id "
            "JOIN (employee AS employee_1 JOIN manager AS manager_1 "
            "ON employee_1.id = manager_1.id) "
            "ON engineer.manager_id = manager_1.id "
            "AND employee_1.type IN (:type_1)",
        )


class EagerDefaultEvalTest(fixtures.DeclarativeMappedTest):
    @classmethod
    def setup_classes(cls, with_polymorphic=None, include_sub_defaults=False):
        Base = cls.DeclarativeBasic

        class Foo(Base):
            __tablename__ = "foo"
            id = Column(
                Integer, primary_key=True, test_needs_autoincrement=True
            )
            type = Column(String(50))
            created_at = Column(Integer, server_default="5")

            __mapper_args__ = {
                "polymorphic_on": type,
                "polymorphic_identity": "foo",
                "eager_defaults": True,
                "with_polymorphic": with_polymorphic,
            }

        class Bar(Foo):
            bar = Column(String(50))
            if include_sub_defaults:
                bat = Column(Integer, server_default="10")

            __mapper_args__ = {"polymorphic_identity": "bar"}

    def test_persist_foo(self):
        Foo = self.classes.Foo

        foo = Foo()

        session = Session()
        session.add(foo)
        session.flush()

        eq_(foo.__dict__["created_at"], 5)

        assert "bat" not in foo.__dict__

        session.close()

    def test_persist_bar(self):
        Bar = self.classes.Bar
        bar = Bar()
        session = Session()
        session.add(bar)
        session.flush()

        eq_(bar.__dict__["created_at"], 5)

        if "bat" in inspect(Bar).attrs:
            eq_(bar.__dict__["bat"], 10)

        session.close()


class EagerDefaultEvalTestSubDefaults(EagerDefaultEvalTest):
    @classmethod
    def setup_classes(cls):
        super(EagerDefaultEvalTestSubDefaults, cls).setup_classes(
            include_sub_defaults=True
        )


class EagerDefaultEvalTestPolymorphic(EagerDefaultEvalTest):
    @classmethod
    def setup_classes(cls):
        super(EagerDefaultEvalTestPolymorphic, cls).setup_classes(
            with_polymorphic="*"
        )
