Changelog
---------

1.4.5 (2017-08-22)
~~~~~~~~~~~~~~~~~~
* Add Django 1.11 support

1.4.4 (2016-06-27)
~~~~~~~~~~~~~~~~~~
* Add Django 1.10 support
* Drop Django 1.4 - 1.7, and Python 2.6 support
* Drop South support

1.4.3 (2015-12-28)
~~~~~~~~~~~~~~~~~~
* Add Django 1.9 support
* Support long options without equals signs, such as "--attr selected"
* Support nose plugins using callback options
* Support nose options without default values (jsatt)
* Remove Django from install dependencies, to avoid accidental upgrades
  (jsocol, willkg)
* Setting REUSE_DB to an empty value now disables REUSE_DB, instead of
  enabling it (wdoekes)

1.4.2 (2015-10-07)
~~~~~~~~~~~~~~~~~~
* Warn against using REUSE_DB=1 and FastFixtureTestCase in docs
* REUSE_DB=1 uses new transaction management in Django 1.7, 1.8 (scottsexton)
* Try to avoid accidentally using production database with REUSE_DB=1 (alexjg, eroninjapan)
* Supported Django versions limited to current supported Django version 1.4,
  1.7, and 1.8, as well as relevant Python versions.

1.4.1 (2015-06-29)
~~~~~~~~~~~~~~~~~~
* Fix version number (ezarowny)
* Fix choice options, unbreaking nose-cover (aamirtharaj-rpx, jwhitlock)
* Support 1.8 app loading system (dgladkov)
* Support non-ASCII file names (singingwolfboy)
* Better PEP8'd assertion names (roganov)

1.4 (2015-04-23)
~~~~~~~~~~~~~~~~
* Django 1.8 support (timc3, adepue, jwhitlock)
* Support --testrunner option (st4lk)
* Fix REUSE_DB second run in py3k (edrmp)

1.3 (2014-12-05)
~~~~~~~~~~~~~~~~
* Django 1.6 and 1.7 support (conrado, co3k, Nepherhotep, mbertheau)
* Python 3.3 and 3.4 testing and support (frewsxcv, jsocol)

1.2 (2013-07-23)
~~~~~~~~~~~~~~~~
* Python 3 support (melinath and jonashaag)
* Django 1.5 compat (fabiosantoscode)

1.1 (2012-05-19)
~~~~~~~~~~~~~~~~
* Django TransactionTestCases don't clean up after themselves; they leave
  junk in the DB and clean it up only on ``_pre_setup``. Thus, Django makes
  sure these tests run last. Now django-nose does, too. This means one fewer
  source of failures on existing projects. (Erik Rose)
* Add support for hygienic TransactionTestCases. (Erik Rose)
* Support models that are used only for tests. Just put them in any file
  imported in the course of loading tests. No more crazy hacks necessary.
  (Erik Rose)
* Make the fixture bundler more conservative, fixing some conceivable
  situations in which fixtures would not appear as intended if a
  TransactionTestCase found its way into the middle of a bundle. (Erik Rose)
* Fix an error that would surface when using SQLAlchemy with connection
  pooling. (Roger Hu)
* Gracefully ignore the new ``--liveserver`` option introduced in Django 1.4;
  don't let it through to nose. (Adam DePue)

1.0 (2012-03-12)
~~~~~~~~~~~~~~~~
* New fixture-bundling plugin for avoiding needless fixture setup (Erik Rose)
* Moved FastFixtureTestCase in from test-utils, so now all the
  fixture-bundling stuff is in one library. (Erik Rose)
* Added the REUSE_DB setting for faster startup and shutdown. (Erik Rose)
* Fixed a crash when printing options with certain verbosities. (Daniel Abel)
* Broke hard dependency on MySQL. Support PostgreSQL. (Roger Hu)
* Support SQLite, both memory- and disk-based. (Roger Hu and Erik Rose)
* Nail down versions of the package requirements. (Daniel Mizyrycki)

.. Omit older changes from package

0.1.3 (2010-04-15)
~~~~~~~~~~~~~~~~~~
* Even better coverage support (rozza)
* README fixes (carljm and ionelmc)
* optparse OptionGroups are handled better (outofculture)
* nose plugins are loaded before listing options

0.1.2 (2010-08-14)
~~~~~~~~~~~~~~~~~~
* run_tests API support (carjm)
* better coverage numbers (rozza & miracle2k)
* support for adding custom nose plugins (kumar303)

0.1.1 (2010-06-01)
~~~~~~~~~~~~~~~~~~
* Cleaner installation (Michael Fladischer)

0.1 (2010-05-18)
~~~~~~~~~~~~~~~~
* Class-based test runner (Antti Kaihola)
* Django 1.2 compatibility (Antti Kaihola)
* Mapping Django verbosity to nose verbosity

0.0.3 (2009-12-31)
~~~~~~~~~~~~~~~~~~
* Python 2.4 support (Blake Winton)
* GeoDjango spatial database support (Peter Baumgartner)
* Return the number of failing tests on the command line

0.0.2 (2009-10-01)
~~~~~~~~~~~~~~~~~~
* rst readme (Rob Madole)

0.0.1 (2009-10-01)
~~~~~~~~~~~~~~~~~~
* birth!
