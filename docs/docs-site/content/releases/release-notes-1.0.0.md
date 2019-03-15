---
title: "1.0.0"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -1000
tags: ['skipIndexing']
---

### HUE v1.0, released Aug 13, 2010


HUE is a web interface for Hadoop, and a platform for building custom
applications with a rich framework. The 1.0 release delivers several new
features:

* File Browser and Beeswax has basic internationalization (i18n) support. UTF-8
  works well. Data in other encoding show up with replacement characters.
* HUE automatically validates its configuration, detects errors and alerts the
  administrator.
* File Browser can now handle viewing large directories.
* There is a centralized logging mechanism of front-end errors to help debugging.
* Tables now support multi-select for bulk operations. Also added support
  for +shift+\+select and +shift++keyboard controls.
* Art buttons can be disabled.

The majority of bug fixes in HUE 1.0 are for small UI glitches across different
browsers. To highlight some other key areas:

* Made keyboard shortcuts more consistent across operating systems.
* Improved window sizing to better handle a small browser window.
* Continuous improvement on Internet Explorer 8.
* Improved documentation.


Application Compatibility
-------------------------

The Hadoop file system library (+hadoop.fs.hadoopfs+) now takes and returns
unicode strings for all file paths. Other than that, HUE 1.0 is compatible with
applications written for HUE 0.9.x.

At the UI framework level, we migrated most elements from JFrame filters to
Behaviour. This allows us to manage memory better and scale better as we
introduce more behaviour patterns. The changes are backward compatible, but SDK
developers should start using the new behaviour patterns. We have updated the
JFrame Gallery examples, and added new ones, to demonstrate the usage.


List of All Bugs Fixed
----------------------

* HUE-27. Convert collection of JFrameFilters to Behaviors
* HUE-36. Allow form controls and the like to work in elements that toggle splitviews
* HUE-47. FitText filter isn't garbage collecting right
* HUE-48. Beeswax error box too small
* HUE-54. beeswax can't handle unicode data
* HUE-57. Add support for shift selecting multiple checkboxes
* HUE-58. Add atime field to the stat dictionary returned by hadoop.fs.stats and hadoop.fs.listdir_stats
* HUE-59. i18n support in filebrowser
* HUE-60. View to allow frontend to log warnings/errors.
* HUE-62. Allow HtmlTable context menu for multiple rows
* HUE-63. Removing HTMLTableKeys reference
* HUE-65. Make dbug.(info|warn|error) messages use the log_frontend_event feature of HUE-60
* HUE-66. beeswax create table UI mess
* HUE-67. beeswax_server email notification should ignore SSL warnings
* HUE-68. Resizing of browser window confuses app windows
* HUE-69: JobBrowser: Kill Job not displaying an OK on a succesful kill and double-click behavior not enabled.
* HUE-70. Job Designer UI needs a little love (partial refresh, sizeTo scrolling)
* HUE-71. Deprecate build/env/bin/desktop
* HUE-72. Chrome doesn't replace the toolbar every load
* HUE-73. Chrome doesn't always size tables to 100% width.
* HUE-76. Rework File Viewer navigation UI
* HUE-78. Hue windows can be moved completely off the desktop
* HUE-79. Side-by-side select no longer works with the recent HtmlTable update
* HUE-80. Job Designer Default for "New Jar" is wrong
* HUE-81. Remove automatic desktop rotation
* HUE-82. Update JFrame to use dbug.error when filters, linkers, renderers fail. Change default renderer to not fail gracefully.
* HUE-83. Save As... dialog is no longer working.
* HUE-84. hadoop.fs.hadoopfs_test:test_i18n_namespace failing
* HUE-86. Some cleanup for beeswax
* HUE-87. Making active user list available across server restarts.
* HUE-88. Hue-Hadoop connectivity is not appropriately thread-safe
* HUE-89. FileBrowser failing to profer useful error messages on upload
* HUE-90. Useradmin table squashed together
* HUE-92. When saving a Beeswax query that is > 64 chars an error is produced but not shown to the user.
* HUE-93. The chown form of filebrowser contains useless fields
* HUE-94. There is no indication that you've clicked the save button in the file editor
* HUE-95. Chrome shows a fuzzy blue outline when the editor has focus.
* HUE-96. Change service name of HDFS and MR client libraries to include string "HUE Plugin"
* HUE-98. Fixing various IE issues.
* HUE-99. Application buttons in menu appear in different orders in different browsers
* HUE-100. Update art-widgets hash to fix IE issues.
* HUE-101. Incorporate new HtmlTable and be explicit about which tables are selectable.
* HUE-102. The file browser edit view "Save as" dialog box shows the "upload a file" button
* HUE-103. Dock bar application switching alternates into windows that aren't on top
* HUE-104. Keyboard window shortcuts should use alt for all OSes
* HUE-105. Child widget instances sometimes steal focus from their parents
* HUE-106. Make Jobsub use common JFrame filters
* HUE-107. FileBrowser loads very slowly for large directories
* HUE-108. JobBrowser task pager squished
* HUE-109. Double clicking in file browser search box in chrome does not select all text there
* HUE-110. Add support for disabled art buttons
* HUE-111. Several files in the desktop/core/static/js/Source/BehaviorFilters are missing copyright headers
* HUE-112. Correctly register 'last access time'. Add test for 'last access time'.
* HUE-114. Jar selector for job designer should be a file chooser app not a text box
* HUE-115. Alternating clicking "+" and "-" JFrame buttons does weird visuals things
* HUE-116: Auto detect config errors and alert admin
* HUE-117. Add some icons from the confluence wiki into hue for the help page
* HUE-119. Chrome failed file upload hides error message
* HUE-120. Anchor tags within frames don't work
* HUE-121. Proper UTF-8 support for help pages
* HUE-122. Create a JFrame gallery that illustrates anchor tag scrolling
* HUE-124. Improve help pages
* HUE-125. 'supervisor -d' creates world writable logs
* HUE-126. get_current_users can get into a bad state
* HUE-127. Delay filling popups so VML elements work in IE
* HUE-128. Error 12030 or 12031 on logout attempt in IE
* HUE-130. Correcting HUE-128
* HUE-131. Improve administration documentation
* HUE-132. Create SelectWithOther Behavior Filter and propagate across Hue
* HUE-134. FileViewer missing view_gzip icon
* HUE-135. Hue should not be adding pre tags to help documents
* HUE-136. Hue could do a better css job, especially for help documents
* HUE-137. Make double click delegators more stable and prevent any links with no href from breaking the desktop
* HUE-143. Some apps don't correctly link to their help page.
* HUE-145. Launching HUE help app after closing it fails
* HUE-146. dbug.* methods don't work with string formatting
* HUE-148. Update the beeswax doc's with paul's new wiki docs
* HUE-151. Beeswax query wait doesn't refresh
* HUE-152. Doc: Mention how to start HUE by hand (w/o supervisor)
* HUE-153. Problems with meta refresh handling
* HUE-154. Mousing over a link in a selected row in a table shows the wrong colors (chrome)
* HUE-155. desktop.conf circular import i18n


Project Information
-------------------
Homepage: http://github.com/cloudera/hue
