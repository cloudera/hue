/*-----------------------------------------------------------------------------
 * SetupSamples.sql
 *   Creates users and populates their schemas with the tables and packages
 * necessary for the cx_Oracle HOL samples.
 *
 * Run this like:
 *   sqlplus / as sysdba @SetupSamples
 *
 * Note that the script SampleEnv.sql should be modified if you would like to
 * use something other than the default configuration.
 *---------------------------------------------------------------------------*/

/*-----------------------------------------------------------------------------
 * Copyright (c) 2017, Oracle and/or its affiliates. All rights reserved.
 *---------------------------------------------------------------------------*/

whenever sqlerror exit failure

-- drop existing user
@@DropSamples.sql

alter session set nls_date_format = 'YYYY-MM-DD HH24:MI:SS';
alter session set nls_numeric_characters='.,';

create user &main_user identified by &main_password
quota unlimited on users
default tablespace users;

grant
    create session,
    create table,
    create procedure,
    create type,
    select any dictionary,
    change notification
to &main_user;

grant execute on dbms_aqadm to &main_user;
grant execute on dbms_lock to &main_user;

create table &main_user..testclobs (
    id     number not null,
    myclob clob not null
);

-- Sequence for connect_pool.py

create sequence &main_user..myseq;

-- EMP/DEPT tables

CREATE TABLE &main_user..EMP
       (EMPNO NUMBER(4) NOT NULL,
        ENAME VARCHAR2(10),
        JOB VARCHAR2(9),
        MGR NUMBER(4),
        HIREDATE DATE,
        SAL NUMBER(7, 2),
        COMM NUMBER(7, 2),
        DEPTNO NUMBER(2));

INSERT INTO &main_user..EMP VALUES
        (7369, 'SMITH',  'CLERK',     7902,
        TO_DATE('17-DEC-1980', 'DD-MON-YYYY'),  800, NULL, 20);
INSERT INTO &main_user..EMP VALUES
        (7499, 'ALLEN',  'SALESMAN',  7698,
        TO_DATE('20-FEB-1981', 'DD-MON-YYYY'), 1600,  300, 30);
INSERT INTO &main_user..EMP VALUES
        (7521, 'WARD',   'SALESMAN',  7698,
        TO_DATE('22-FEB-1981', 'DD-MON-YYYY'), 1250,  500, 30);
INSERT INTO &main_user..EMP VALUES
        (7566, 'JONES',  'MANAGER',   7839,
        TO_DATE('2-APR-1981', 'DD-MON-YYYY'),  2975, NULL, 20);
INSERT INTO &main_user..EMP VALUES
        (7654, 'MARTIN', 'SALESMAN',  7698,
        TO_DATE('28-SEP-1981', 'DD-MON-YYYY'), 1250, 1400, 30);
INSERT INTO &main_user..EMP VALUES
        (7698, 'BLAKE',  'MANAGER',   7839,
        TO_DATE('1-MAY-1981', 'DD-MON-YYYY'),  2850, NULL, 30);
INSERT INTO &main_user..EMP VALUES
        (7782, 'CLARK',  'MANAGER',   7839,
        TO_DATE('9-JUN-1981', 'DD-MON-YYYY'),  2450, NULL, 10);
INSERT INTO &main_user..EMP VALUES
        (7788, 'SCOTT',  'ANALYST',   7566,
        TO_DATE('09-DEC-1982', 'DD-MON-YYYY'), 3000, NULL, 20);
INSERT INTO &main_user..EMP VALUES
        (7839, 'KING',   'PRESIDENT', NULL,
        TO_DATE('17-NOV-1981', 'DD-MON-YYYY'), 5000, NULL, 10);
INSERT INTO &main_user..EMP VALUES
        (7844, 'TURNER', 'SALESMAN',  7698,
        TO_DATE('8-SEP-1981', 'DD-MON-YYYY'),  1500,    0, 30);
INSERT INTO &main_user..EMP VALUES
        (7876, 'ADAMS',  'CLERK',     7788,
        TO_DATE('12-JAN-1983', 'DD-MON-YYYY'), 1100, NULL, 20);
INSERT INTO &main_user..EMP VALUES
        (7900, 'JAMES',  'CLERK',     7698,
        TO_DATE('3-DEC-1981', 'DD-MON-YYYY'),   950, NULL, 30);
INSERT INTO &main_user..EMP VALUES
        (7902, 'FORD',   'ANALYST',   7566,
        TO_DATE('3-DEC-1981', 'DD-MON-YYYY'),  3000, NULL, 20);
INSERT INTO &main_user..EMP VALUES
        (7934, 'MILLER', 'CLERK',     7782,
        TO_DATE('23-JAN-1982', 'DD-MON-YYYY'), 1300, NULL, 10);

CREATE TABLE &main_user..DEPT
       (DEPTNO NUMBER(2),
        DNAME VARCHAR2(14),
        LOC VARCHAR2(13) );

INSERT INTO &main_user..DEPT VALUES (10, 'ACCOUNTING', 'NEW YORK');
INSERT INTO &main_user..DEPT VALUES (20, 'RESEARCH',   'DALLAS');
INSERT INTO &main_user..DEPT VALUES (30, 'SALES',      'CHICAGO');
INSERT INTO &main_user..DEPT VALUES (40, 'OPERATIONS', 'BOSTON');

CREATE TABLE &main_user..BONUS
        (ENAME VARCHAR2(10),
         JOB   VARCHAR2(9),
         SAL   NUMBER,
         COMM  NUMBER);

CREATE TABLE &main_user..SALGRADE
        (GRADE NUMBER,
         LOSAL NUMBER,
         HISAL NUMBER);

INSERT INTO &main_user..SALGRADE VALUES (1,  700, 1200);
INSERT INTO &main_user..SALGRADE VALUES (2, 1201, 1400);
INSERT INTO &main_user..SALGRADE VALUES (3, 1401, 2000);
INSERT INTO &main_user..SALGRADE VALUES (4, 2001, 3000);
INSERT INTO &main_user..SALGRADE VALUES (5, 3001, 9999);

COMMIT;

exit
