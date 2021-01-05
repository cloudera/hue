Changelog
=========

0.6.2 (2017-12-18)
------------------

- compatibility with Django 2.0 added


0.6.1 (2017-12-18)
------------------

* compatibility with Django 1.11 added

0.6.0 - 2017-04-25
------------------

* compatibility with unsupported Django versions (<1.8) is dropped
* compatibility with Django 1.10+ middlewares was added

0.5.1 - 2016-03-30
------------------

* make imports absolute in babel templatetags
* strip quotes from translations via _()
* fix links in docs
* Add support for "trimmed" blocktrans content

0.5.0 - 2016-02-29
------------------

* Add compatibility for Django-1.9

0.4.0 - 2015-04-22
------------------

* Add compatibility for Django 1.8
* Add compatibility for latest django master
* Various python 3 fixes


0.3.9 - 2014-12-24
------------------

* Fix dependencies on Django/Babel to use lower-case egg names.

0.3.8 - 2014-10-14
------------------

* Fix old reference to `babeldjango` module in entry points.

0.3.7 - 2014-10-14
------------------

* Fix Python 3.x compatibility in `babel makemessages` command.

0.3.6 - 2014-10-05
------------------

* Django 1.7 compatibility


0.3.5 - 2014-09-10
------------------

* Create .po and .pot files if not existing, plus it's specific base directories.


0.3.4 - 2014-05-25
------------------

* Fixed django compatibility

0.3.3 - 2014-04-22
------------------

* Fixed release builds


0.3.2 - 2014-04-22
------------------

* Initial testing infrastructure
* Add management command `babel` with `makemessages` and `compilemessages`
  labels. Mimics django's `makemessages` and `compilemessages` commands.
* Various unicode fixes


0.3.1 - 2013-12-11
------------------

* fix relative import in template tags


0.3.0 - 2013-12-11
------------------

* Rename package to django_babel


0.2.3 - 2013-12-11
------------------

* Rename package on PyPI
* Use GitHub as source control


.. _`master`: https://github.com/python-babel/django-babel
