---
title: "0.9.1"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -91
tags: ['skipIndexing']
---

### HUE v0.9.1, released July 21, 2010


HUE 0.9.1 is mainly a bug-fix release. Most notably:

* A lot of installation related issues have been corrected.
* The JFrame filtering system now supports garbage collection of individual
  elements, which fixes memory leak on partial refresh.
* IE compatibility has improved.
* User manual has been updated.

This release also includes a few small features:

* New multi-select widget for the front-end.
* A new configuration variable, +http_500_debug_mode+, turns on debugging for
  internal server error.
* The +app_reg+ tool registers and display the application's author.

List of All Bugs Fixed
----------------------
* HUE-2. app_reg does not install conf/*.ini
* HUE-3. Prod install contains jframegallery
* HUE-4. User manual S2.1 incorrect
* HUE-5. libs/hadoop should be more lenient looking for jars
* HUE-8. beeswax import data doesn't work
* HUE-10. Makefile.vars: DESKTOP_PLUGIN_DIR incorrect
* HUE-12. Drop down box to select user for chown
* HUE-13. app_reg should show app's author
* HUE-14. make processing ext-py unnecessarily
* HUE-15. Explicitly specifying default for jobtracker.thrift.address for consistency with hdfs-site.xml
* HUE-16. Provide a way to tell hudson.sh to skip cleaning the checkout.
* HUE-17. 'make install' fails if the working tree is not clean
* HUE-18. tests in 'help' app should not depend on useradmin
* HUE-19. Add get_content_summaries call to NameNode plugin.
* HUE-21. Create new JFrame Filter system that allows for individual element
* HUE-22. Allow relcoation of a Hue installation
* HUE-23. Integrate IE Compatible Protovis
* HUE-24. Filesize Sorting doesn't work
* HUE-25. Allow multi-select for moving multiple users into a group
* HUE-26. UserAdmin js file throws error in IE
* HUE-28. confparse wasn't handling continued lines correctly
* HUE-29. Set HADOOP_LOG_DIR for mini_cluster.py
* HUE-30: Add support for Behavior Filters to add keyboard events to JFrame instance
* HUE-32. User manual update
* HUE-33. Protovis version has bug wherein mark events do not have their index properly set
* HUE-34. Make Splitview's fixed side be the one with the explicit size
* HUE-35. create icons for tiny file browser and a "go up" folder
* HUE-36. Allow form controls and the like to work in elements that toggle splitviews
* HUE-40. virtualenv_support missing setuptools for py2.6
* HUE-42. Toolbar buttons look messed up in Chrome
* HUE-44. Filebrowser: move file ok button does nothing while no file/folder is selected
* HUE-46. Bump version number for 0.9.1 release
* HUE-47. FitText filter isn't garbage collecting right
* HUE-49. create table syntax error for partition table
* HUE-50. Removing desktop/core/ext-py/python-ldap-2.3.11.
* HUE-51. Hue needs a 500 template
* HUE-53. Fix various IE compatibility issues.
* HUE-56. 0.9.1 release notes

Project Information
-------------------
Homepage: http://github.com/cloudera/hue
