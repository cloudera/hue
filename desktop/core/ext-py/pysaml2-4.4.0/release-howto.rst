Releasing software
-------------------

When releasing a new version, the following steps should be taken:

1. Make sure all automated tests pass.

2. Fill in the release date in ``CHANGES``. Make sure the changelog is
   complete. Commit this change.

3. Make sure the package metadata in ``setup.py`` is up-to-date. You can
   verify the information by re-generating the egg info::

     python setup.py  egg_info

   and inspecting ``src/pysaml2.egg-info/PKG-INFO``. You should also make sure
   that the long description renders as valid reStructuredText. You can
   do this by using the ``rst2html.py`` utility from docutils_::

     python setup.py --long-description | rst2html > test.html

   If this will produce warning or errors, PyPI will be unable to render
   the long description nicely. It will treat it as plain text instead.

4. Update the version in the setup.py file and the doc conf.py file. Commit
   these changes.

5. Create a release tag::

      bzr tag X.Y.Z

6. Push these changes to Launchpad::

      bzr push

7. Create a source distribution and upload it to PyPI using the following
   command::

      python setup.py register sdist upload

8. Upload the documentation to PyPI. First you need to generate the html
   version of the documentation::

      cd doc
      make clean
      make html
      cd _build/html
      zip -r pysaml2-docs.zip *

   now go to http://pypi.python.org/pypi?%3Aaction=pkg_edit&name=pysaml2 and
   submit the pysaml2-docs.zip file in the form at the bottom of that page.

9. Create a new release at Launchpad. If no milestone was created for this
   release in the past, create it now at https://launchpad.net/pysaml2/main
   Then create a release for that milestone. You can copy the section of
   the CHANGES file that matches this release in the appropiate field of
   the Launchpad form. Finally, add a download file for that release.

10. Send an email to the pysaml2 list announcing this release


**Important:** Once released to PyPI or any other public download location,
a released egg may *never* be removed, even if it has proven to be a faulty
release ("brown bag release"). In such a case it should simply be superseded
immediately by a new, improved release.

.. _docutils: http://docutils.sourceforge.net/

This document is based on http://svn.zope.org/*checkout*/Sandbox/philikon/foundation/releasing-software.txt
