---
title: "0.4.1"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -41
tags: ['skipIndexing']
---

### v0.4.1, released April 7, 2010

Cloudera Desktop 0.4.1 is a minor bugfix release.

KEY BUG FIXES

- Pagination in the Beeswax application is now available in the UI.

- The tarball build now succeeds if a previous version's 
  Cloudera Desktop plugins are installed.

- Error messages are propagated correctly in Python 2.4.

- Desktop can now run on port 80.

- Package dependencies on python-dev are now more accurate.

KNOWN BUGS

- After a successful upload with Linux's flash player (which may warn you about
  hanging your computer), the upload screen does not clear.  Click the red
  (x) button to clear it.
