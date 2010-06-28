
.. _installation:

Installation
============

South's current release is :ref:`0.7 RC1 <0-7-release-notes>`.

There are a few different ways to install South:

 - :ref:`Using easy_install <installation-easy-install>` (or pip), which is recommended if you want stable releases.
 - :ref:`Using a Mercurial checkout <installation-mercurial>`, recommended if you want cutting-edge features.
 - :ref:`Using our downloadable archives <installation-archives>`, useful if you don't have easy_install or Mercurial.
 
Some Linux distributions are also starting to include South in their package
repositories; if you're running unstable Debian you can
``apt-get install python-django-south``, and on new Fedoras you can use
``yum install Django-south``. Note that this may give you an older version - 
check the version before using the packages.

South should work with versions of Django from 0.97-pre through to 1.2, although
some features (such as multi-db) may not be available for older Django versions.


.. _installation-easy-install:
 
Using easy_install
------------------

If you have easy_install available on your system, just type::

 easy_install South
 
If you've already got an old version of South, and want to upgrade, use::

 easy_install -U South
 
That's all that's needed to install the package; you'll now want to
:ref:`configure your Django installation <installation-configure>`.


.. _installation-mercurial:

Using Mercurial
---------------

You can install directly from our Mercurial repo, allowing you to recieve
updates and bugfixes as soon as they're made. You'll need Mercurial installed
on your system; if it's not already, you'll want to get it. The package name
is ``mercurial`` on most Linux distributions; OSX and Windows users can download
packages from http://mercurial.berkwood.com.

Make sure you're in a directory where you want the ``south`` directory to
appear, and run::

 hg clone http://bitbucket.org/andrewgodwin/south/
 
To update an existing Mercurial checkout to the newest version, run::

 hg pull
 hg up -C tip
 
(Rather than running from tip, you can also use the ``stableish`` tag, which is
manually set on reasonably stable trunk commits, or pick a version number tag.)

Once you have this directory, move onto :ref:`installation-from-directory`.


.. _installation-archives:

Using downloadable archives
---------------------------

If you're averse to using Mercurial, and don't have easy_install available, then
you can install from one of our ``.tar.gz`` files.

First, download the archive of your choice from
`our releases page <http://aeracode.org/releases/south>`_, and extract it to
create a ``south`` folder. Then, proceed with our instructions for
:ref:`installation-from-directory`.



.. _installation-from-directory:

Installing from a directory
---------------------------

If you've obtained a copy of South using either Mercurial or a downloadable
archive, you'll need to install the copy you have system-wide. Try running::

 python setup.py develop
 
If that fails, you don't have ``setuptools`` or an equivalent installed; either
install them, or run::

 python setup.py install
 
Note that ``develop`` sets the installed version to run from the directory you
just created, while ``install`` copies all the files to Python's
``site-packages`` folder, meaning that if you update your checkout you'll need
to re-run ``install``.

You could also install South locally for only one project, by either including
with your project and modifying ``sys.path`` in your settings file, or
(preferably) by using virtualenv, pip and a requirements.txt. A tutorial in how
to use these is outside the scope of this documentation, but `there are
tutorials elsewhere <http://www.saltycrane.com/blog/2009/05/notes-using-pip-and-virtualenv-django/>`_.

Once you've done one of those, you'll want to
:ref:`configure your Django installation <installation-configure>`.


.. _installation-configure:

Configuring your Django installation
------------------------------------

Now you've installed South system-wide, you'll need to configure Django to use
it. Doing so is simple; just edit your ``settings.py`` and add ``'south'`` to
the end of ``INSTALLED_APPS``.

If Django doesn't seem to pick this up, check that you're not overriding 
``INSTALLED_APPS`` elsewhere, and that you can run ``import south`` from inside
``./manage.py shell`` with no errors.

Now South is loaded into your project and ready to go, you'll probably want to
take a look at our :ref:`tutorial`.
