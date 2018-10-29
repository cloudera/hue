;; Tests for various functions handling adornments  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert t)

(ert-deftest adornment-asserts ()
  "Check some assertions."
  (should (equal ert-Buf-point-char "\^@"))
  (should (equal ert-Buf-mark-char "\^?"))
  )

(defun ttl-at-point ()
  "Wrapper for calling `rst-ttl-at-point'."
  (apply-ttl-match (rst-ttl-at-point)))

(ert-deftest rst-ttl-at-point ()
  "Tests for `rst-ttl-at-point'."
  (should (ert-equal-buffer-return
	   '(ttl-at-point)
	   "

Du bon vin tous les jours.
\^@
"
	   "

\^@Du bon vin tous les jours.

"
	   '(nil 0 nil "Du bon vin tous les jours." nil)
	   ))
  (should (ert-equal-buffer-return
	   '(ttl-at-point)
	   "
\^@
Du bon vin tous les jours.

"
	   "

\^@Du bon vin tous les jours.

"
	   '(nil 0 nil "Du bon vin tous les jours." nil)
	   ))
  (should (ert-equal-buffer-return
	   '(ttl-at-point)
	   "

Du bon vin tous les jours.
------\^@-----
"
	   "

\^@Du bon vin tous les jours.
-----------
"
	   (list
	    (rst-Ado-new-simple ?-) 0
	    nil "Du bon vin tous les jours." "-----------")
	   ))
  (should (ert-equal-buffer-return
	   '(ttl-at-point)
	   "
------\^@-----
Du bon vin tous les jours.

"
	   "
-----------
\^@Du bon vin tous les jours.

"
	   (list
	    (rst-Ado-new-over-and-under ?-) 0
	    "-----------" "Du bon vin tous les jours." nil)
	   ))
  (should (ert-equal-buffer-return
	   '(ttl-at-point)
	   "
\^@-----------
Du bon vin tous les jours.
-----------

"
	   "
-----------
\^@Du bon vin tous les jours.
-----------

"
	   (list
	    (rst-Ado-new-over-and-under ?-) 0
	    "-----------" "Du bon vin tous les jours." "-----------")
	   ))
  (should (ert-equal-buffer-return
	   '(ttl-at-point)
	   "
\^@===========
Du bon vin tous les jours.
-----------
"
	   "
\^@===========
Du bon vin tous les jours.
-----------
"
	   nil
	   ))
  (should (ert-equal-buffer-return
	   '(ttl-at-point)
	   "
Du bon vin tous les jours.
\^@-----------
Du bon vin tous les jours.
-----------

"
	   "
Du bon vin tous les jours.
-----------
\^@Du bon vin tous les jours.
-----------

" ; This is not how the parser works but looks more logical
	   (list
	    (rst-Ado-new-over-and-under ?-) 0
	    "-----------" "Du bon vin tous les jours." "-----------")
	   ))
  (should (ert-equal-buffer-return
	   '(ttl-at-point)
	   "

\^@===========

"
	   "

\^@===========

"
	   nil
	   ))
  (should (ert-equal-buffer-return
	   '(ttl-at-point)
	   "\^@"
	   "\^@"
	   nil
	   ))
  (should (ert-equal-buffer-return
	   '(ttl-at-point)
	   "\^@
"
	   "\^@
"
	   nil
	   ))
  (should (ert-equal-buffer-return
	   '(ttl-at-point)
	   "
Line 1
\^@
Line 2

"
	   "
\^@Line 1

Line 2

"
	   '(nil 0 nil "Line 1" nil)
	   ))
  (should (ert-equal-buffer-return
	   '(ttl-at-point)
	   "
=====================================
   Project Idea: Panorama Stitcher
====================================

:Author: Martin Blais <blais@furius.ca>
\^@
Another Title
=============
"
	   "
=====================================
   Project Idea: Panorama Stitcher
====================================

\^@:Author: Martin Blais <blais@furius.ca>

Another Title
=============
"
	   '(nil 0 nil ":Author: Martin Blais <blais@furius.ca>" nil)
	   ))
  )

(setq text-1
"===============================
   Project Idea: My Document
===============================

:Author: Martin Blais

Introduction
============

This is the introduction.

Notes
-----

Some notes.

Main Points
===========

Yep.

Super Point
-----------

~~~~~~~~~~~
\^@ Sub Point
~~~~~~~~~~~

Isn't this fabulous?

Conclusion
==========

That's it, really.

")

(setq text-2
"

Previous
--------

Current\^@
~~~~~~~

Next
++++

")

(setq text-3
"

Previous
--------

Current\^@
~~~~~~~

  Next
  ++++

")

(setq text-4
"

Previous
--------

Current\^@
~~~~~~~

Next
++++

Same
~~~~

")

(defun find-all-adornments ()
  "Call `rst-all-ttls' and return conses of line and `rst-Ado'."
  (mapcar (lambda (ttl)
	    (cons (line-number-at-pos (rst-Ttl-get-title-beginning ttl))
		  (rst-Ttl-ado ttl)))
	  (rst-all-ttls-compute)))

(ert-deftest rst-all-ttls ()
  "Tests for `rst-all-ttls'."
  (should (ert-equal-buffer-return
	   (find-all-adornments)
	   ""
	   t
	   nil
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-adornments)
	   "
  Not a valid section header because of indentation
===================================================
"
	   t
	   nil
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-adornments)
	   "
Only a...

===================================================

...transition
"
	   t
	   nil
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-adornments)
	   "
=======================================================
Not a valid section header because of missing underline

"
	   t
	   nil
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-adornments)
	   "
=====================================================
Not a valid section header because of wrong underline
-----------------------------------------------------
"
	   t
	   nil
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-adornments)
	   "
Valid simple section header
===========================
"
	   t
	   (list
	    (cons 2 (rst-Ado-new-simple ?=)))
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-adornments)
	   "
=======================================
  Valid over and under section header
=======================================
"
	   t
	   (list
	    (cons 3 (rst-Ado-new-over-and-under ?=)))
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-adornments)
	   text-1
	   t
	   (list
	    (cons 2 (rst-Ado-new-over-and-under ?=))
	    (cons 7 (rst-Ado-new-simple ?=))
	    (cons 12 (rst-Ado-new-simple ?-))
	    (cons 17 (rst-Ado-new-simple ?=))
	    (cons 22 (rst-Ado-new-simple ?-))
	    (cons 26 (rst-Ado-new-over-and-under ?~))
	    (cons 31 (rst-Ado-new-simple ?=)))
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-adornments)
	   text-2
	   t
	   (list
	    (cons 3 (rst-Ado-new-simple ?-))
	    (cons 6 (rst-Ado-new-simple ?~))
	    (cons 9 (rst-Ado-new-simple ?+)))
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-adornments)
	   text-3
	   t
	   (list
	    (cons 3 (rst-Ado-new-simple ?-))
	    (cons 6 (rst-Ado-new-simple ?~)))
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-adornments)
	   "=====
Title
=====

Header A
========

Header B
========

Subheader B.a
-------------

SubSubheader B.a.1
~~~~~~~~~~~~~~~~~~

Header C
========

Missing node C.a.1
~~~~~~~~~~~~~~~~~~
"
	   t
	   (list
	    (cons 2 (rst-Ado-new-over-and-under ?=))
	    (cons 5 (rst-Ado-new-simple ?=))
	    (cons 8 (rst-Ado-new-simple ?=))
	    (cons 11 (rst-Ado-new-simple ?-))
	    (cons 14 (rst-Ado-new-simple ?~))
	    (cons 17 (rst-Ado-new-simple ?=))
	    (cons 20 (rst-Ado-new-simple ?~)))
	   ))
  )

(ert-deftest rst-hdr-hierarchy ()
  "Tests for `rst-hdr-hierarchy'."
  (let ( ;; Set customizable variables to defined values
	(rst-default-indent 5))
    (should (ert-equal-buffer-return
	     '(rst-hdr-hierarchy)
	     text-1
	     t
	     (list
	      (rst-Hdr-new (rst-Ado-new-over-and-under ?=) 3)
	      (rst-Hdr-new (rst-Ado-new-simple ?=) 0)
	      (rst-Hdr-new (rst-Ado-new-simple ?-) 0)
	      (rst-Hdr-new (rst-Ado-new-over-and-under ?~) 1))
	     ))
    (should (ert-equal-buffer-return
	     '(rst-hdr-hierarchy)
	     (concat text-1
		     "
=========
No indent
=========
")
	     t
	     (list
	      (rst-Hdr-new (rst-Ado-new-over-and-under ?=) 5)
	      (rst-Hdr-new (rst-Ado-new-simple ?=) 0)
	      (rst-Hdr-new (rst-Ado-new-simple ?-) 0)
	      (rst-Hdr-new (rst-Ado-new-over-and-under ?~) 1))
	     ))
  ))

(ert-deftest rst-get-hierarchy-ignore ()
  "Tests for `rst-hdr-hierarchy' with ignoring a line."
  (should (ert-equal-buffer-return
	   '(rst-hdr-hierarchy (point))
	   text-1
	   t
	   (list
	    (rst-Hdr-new (rst-Ado-new-over-and-under ?=) 3)
	    (rst-Hdr-new (rst-Ado-new-simple ?=) 0)
	    (rst-Hdr-new (rst-Ado-new-simple ?-) 0))
	   ))
  (should (ert-equal-buffer-return
	   '(rst-hdr-hierarchy (point))
	   text-4
	   t
	   (list
	    (rst-Hdr-new (rst-Ado-new-simple ?-) 0)
	    (rst-Hdr-new (rst-Ado-new-simple ?~) 0)
	    (rst-Hdr-new (rst-Ado-new-simple ?+) 0))
	   ))
  )

(ert-deftest rst-adornment-level ()
  "Tests for `rst-adornment-level'."
  (should (ert-equal-buffer-return
	   '(rst-adornment-level (rst-Ado-new-transition))
	   text-1
	   t
	   t
	   ))
  (should (ert-equal-buffer-return
	   '(rst-adornment-level (rst-Ado-new-over-and-under ?=))
	   text-1
	   t
	   1
	   ))
  (should (ert-equal-buffer-return
	   '(rst-adornment-level (rst-Ado-new-simple ?=))
	   text-1
	   t
	   2
	   ))
  (should (ert-equal-buffer-return
	   '(rst-adornment-level (rst-Ado-new-simple ?-))
	   text-1
	   t
	   3
	   ))
  (should (ert-equal-buffer-return
	   '(rst-adornment-level (rst-Ado-new-over-and-under ?~))
	   text-1
	   t
	   4
	   ))
  (should (ert-equal-buffer-return
	   '(rst-adornment-level (rst-Ado-new-simple ?#))
	   text-1
	   t
	   5
	   ))
  )

(ert-deftest rst-adornment-complete-p ()
  "Tests for `rst-adornment-complete-p'."
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-simple ?=) 0)
	   "Vaudou\^@"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 0)
	   "Vaudou\^@
======"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-simple ?=) 0)
	   "

\^@Vaudou

"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-simple ?=) 0)
	   "
\^@Vaudou
======
"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 0)
	   "
======
\^@Vaudou
======
"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 2)
	   "
==========
\^@  Vaudou
==========
"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-simple ?=) 0)
	   "
\^@Vaudou
=====
"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-simple ?=) 0)
	   "
\^@Vaudou
=======
"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-simple ?=) 0)
	   "
\^@Vaudou
===-==
"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 0)
	   "
======
\^@Vaudou
=====
"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 0)
	   "
=====
\^@Vaudou
======
"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 0)
	   "
======
\^@Vaudou
===-==
"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 0)
	   "
===-==
\^@Vaudou
======
"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 0)
	   "
======
\^@Vaudou

"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 0)
	   "
======
\^@Vaudou
------
"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 0)
	   "
==========
  \^@Vaudou
=========
"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 0)
	   "
=========
  \^@Vaudou
==========
"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 0)
	   "
==========
  \^@Vaudou
===-======
"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 0)
	   "
===-======
  \^@Vaudou
==========
"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 0)
	   "
==========
  \^@Vaudou

"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-adornment-complete-p (rst-Ado-new-over-and-under ?=) 0)
	   "
==========
  \^@Vaudou
----------
"
	   t
	   nil))
  )

(ert-deftest rst-get-previous-hdr ()
  "Tests for `rst-get-previous-hdr'."
  (should (ert-equal-buffer-return
	   '(rst-get-previous-hdr)
	   "

Previous
--------

\^@Current

Next
++++

"
	   t
	   (rst-Hdr-new (rst-Ado-new-simple ?-) 0)))
  (should (ert-equal-buffer-return
	   '(rst-get-previous-hdr)
	   "

Previous
--------

Current\^@
~~~~~~~

Next
++++

"
	   t
	   (rst-Hdr-new (rst-Ado-new-simple ?-) 0)))
  )

(defun apply-ttl-match (ttl)
  "Apply the match in TTL to the buffer and return important data.
Puts point at the beginning of the title line. Return a list
consisting of the `rst-Ado', the indent and the three matched
texts. Return nil if TTL is nil. Checks whether embedded match
groups match match group 0."
  (when ttl
    (let ((match (rst-Ttl-match ttl)))
      (set-match-data match)
      (let ((whole (match-string-no-properties 0))
	    (over (match-string-no-properties 1))
	    (text (match-string-no-properties 2))
	    (under (match-string-no-properties 3))
	    (gather ""))
	(if over
	    (setq gather (concat gather over "\n")))
	(if text
	    (setq gather (concat gather text "\n")))
	(if under
	    (setq gather (concat gather under "\n")))
	(if (not (string= (substring gather 0 -1) whole))
	    (error "Match 0 '%s' doesn't match concatenated parts '%s'"
		   whole gather))
	(goto-char (match-beginning 2))
	(list (rst-Ttl-ado ttl) (rst-Ttl-indent ttl) over text under)))))

(defun classify-adornment (beg end)
  "Wrapper for calling `rst-classify-adornment'."
  (interactive "r")
  (apply-ttl-match (rst-classify-adornment
		    (buffer-substring-no-properties beg end) end)))

(defun classify-adornment-accept (beg end)
  "Wrapper for calling `rst-classify-adornment'."
  (interactive "r")
  (apply-ttl-match (rst-classify-adornment
		    (buffer-substring-no-properties beg end) end t)))

(ert-deftest rst-classify-adornment ()
  "Tests for `rst-classify-adornment'."
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "

Du bon vin tous les jours
\^@=========================\^?

"
	   nil
	   (list
	    (rst-Ado-new-simple ?=) 0
	    nil "Du bon vin tous les jours" "=========================")
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "

Du bon vin tous les jours
\^@====================\^?

"
	   nil
	   (list
	    (rst-Ado-new-simple ?=) 0
	    nil "Du bon vin tous les jours" "====================")
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "\^@====================\^?
Du bon vin tous les jours"
	   nil
	   nil
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment-accept)
	   "\^@====================\^?
Du bon vin tous les jours"
	   nil
	   (list
	    (rst-Ado-new-over-and-under ?=) 0
	    "====================" "Du bon vin tous les jours" nil)
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "

     Du bon vin tous les jours
\^@====================\^?

"
	   nil
	   (list
	    (rst-Ado-new-simple ?=) 5
	    nil "     Du bon vin tous les jours" "====================")
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "     Du bon vin tous les jours
\^@====================\^?
"
	   nil
	   (list
	    (rst-Ado-new-simple ?=) 5
	    nil "     Du bon vin tous les jours" "====================")
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "

Du bon vin tous les jours
\^@-\^?
"
	   nil
	   nil
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "

Du bon vin tous les jours
\^@--\^?
"
	   nil
	   nil
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "

Du bon vin tous les jours
\^@---\^?
"
	   nil
	   (list
	    (rst-Ado-new-simple ?-) 0
	    nil "Du bon vin tous les jours" "---")
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "
\^@~~~~~~~~~~~~~~~~~~~~~~~~~\^?
Du bon vin tous les jours
~~~~~~~~~~~~~~~~~~~~~~~~~

"
	   nil
	   (list
	    (rst-Ado-new-over-and-under ?~) 0
	    "~~~~~~~~~~~~~~~~~~~~~~~~~" "Du bon vin tous les jours" "~~~~~~~~~~~~~~~~~~~~~~~~~")
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "~~~~~~~~~~~~~~~~~~~~~~~~~
Du bon vin tous les jours
\^@~~~~~~~~~~~~~~~~~~~~~~~~~\^?

"
	   nil
	   (list
	    (rst-Ado-new-over-and-under ?~) 0
	    "~~~~~~~~~~~~~~~~~~~~~~~~~" "Du bon vin tous les jours" "~~~~~~~~~~~~~~~~~~~~~~~~~")
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "
\^@~~~~~~~~~~~~~~~~~~~~~~~~~\^?
   Du bon vin tous les jours
~~~~~~~~~~~~~~~~~~~~~~~~~

"
	   nil
	   (list
	    (rst-Ado-new-over-and-under ?~) 3
	    "~~~~~~~~~~~~~~~~~~~~~~~~~" "   Du bon vin tous les jours" "~~~~~~~~~~~~~~~~~~~~~~~~~")
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "
\^@~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\^?
Du bon vin tous les jours
~~~~~~~~~~~~~~~~~~~

"
	   nil
	   (list
	    (rst-Ado-new-over-and-under ?~) 0
	    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" "Du bon vin tous les jours" "~~~~~~~~~~~~~~~~~~~")
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "
---------------------------
Du bon vin tous les jours
\^@~~~~~~~~~~~~~~~~~~~~~~~~~~~\^?

"
	   nil
	   nil
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "\^@---------------------------\^?"
	   nil
	   (list
	    (rst-Ado-new-transition) nil
	    nil "---------------------------" nil)
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "
\^@===\^?
"
	   nil
	   (list
	    (rst-Ado-new-transition) nil
	    nil "===" nil)
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "
\^@---------------------------\^?
Du bon vin tous les jours
~~~~~~~~~~~~~~~~~~~~~~~~~~~

"
	   nil
	   nil
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "
=========================
Du bon vin tous les jours
\^@=========================\^?
Du bon vin

"
	   nil
	   (list
	    (rst-Ado-new-over-and-under ?=) 0
	    "=========================" "Du bon vin tous les jours" "=========================")
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "
=========================
Du bon vin tous les jours
=========================
Du bon vin
\^@----------\^?

"
	   nil
	   (list
	    (rst-Ado-new-simple ?-) 0
	    nil "Du bon vin" "----------")
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "
=========================
Du bon vin tous les jours
=========================
\^@----------\^?
Du bon vin
----------

"
	   nil
	   (list
	    (rst-Ado-new-over-and-under ?-) 0
	    "----------" "Du bon vin" "----------")
	   t))
  (should (ert-equal-buffer-return
	   '(classify-adornment)
	   "
=========================
Du bon vin tous les jours
=========================
--------------
  Du bon vin
\^@--------------\^?

"
	   nil
	   (list
	    (rst-Ado-new-over-and-under ?-) 2
	     "--------------" "  Du bon vin" "--------------")
	   t))
  )

(defun display-adornments-hierarchy ()
  "Wrapper for calling `rst-display-hdr-hierarchy'."
  (rst-display-hdr-hierarchy)
  (let ((source (get-buffer "*rest section hierarchy*")))
    (delete-region (point-min) (point-max))
    (insert (with-current-buffer source
	      (buffer-substring (point-min) (point-max))))
    (kill-buffer source)))

(ert-deftest rst-display-hdr-hierarchy ()
  "Tests for `rst-display-hdr-hierarchy'."
  (should (ert-equal-buffer
	   '(display-adornments-hierarchy)
	   ""
	   "
"
	   ))
  (should (ert-equal-buffer
	   '(display-adornments-hierarchy)
	   "
First
-----

Second
======

First again
-----------

Second again
============

+++++
Third
+++++

"
	   "
Section Level 1
---------------


Section Level 2
===============


+++++++++++++++
Section Level 3
+++++++++++++++
"
	     ))
    )

(ert-deftest rst-adjust-region ()
  "Tests for `rst-adjust-region'."
  (let ((rst-preferred-adornments '((?= over-and-under 1)
				    (?= simple 0)
				    (?- simple 0)
				    (?~ simple 0)
				    (?+ simple 0)
				    (?` simple 0)
				    (?# simple 0)
				    (?@ simple 0))))
    (should (ert-equal-buffer
	     '(rst-adjust-region nil)
	     "\^@\^?"
	     t
	     ))
    (should (ert-equal-buffer
	     '(rst-adjust-region nil)
	     "
First
-----
\^@
Second
======
\^?
First again
-----------

Second again
============

+++++
Third
+++++

"
	     "
First
-----
\^@
Second
------
\^?
First again
-----------

Second again
============

+++++
Third
+++++

"
	     ))
    (should (ert-equal-buffer
	     '(rst-adjust-region nil)
	     "
First
-----

Second
======

First again
-----------
\^@
Second again
============

+++++
Third
+++++
\^?
"
	     "
First
-----

Second
======

First again
-----------
\^@
Second again
------------

Third
=====
\^?
"
	     ))
    (should (ert-equal-buffer
	     '(rst-adjust-region nil)
	     "
First
-----

Second
======
\^@
First again
-----------
\^?
Second again
============

+++++
Third
+++++

"
	     "
First
-----

Second
======

=============
 First again
=============

Second again
============

+++++
Third
+++++

"
	     ))
    (should (ert-equal-buffer
	     '(rst-adjust-region t)
	     "
First
-----

Second
======
\^@
First again
-----------
\^?
Second again
============

+++++
Third
+++++

"
	     "
First
-----

Second
======
\^@
First again
===========
\^?
Second again
============

+++++
Third
+++++

"
	     ))
    (should (ert-equal-buffer
	     '(rst-adjust-region t)
	     "
First
-----

Second
======

First again
-----------

Second again
============
\^@
+++++
Third
+++++
\^?
"
	     "
First
-----

Second
======

First again
-----------

Second again
============

=======
 Third
=======

"
	     ))
  ))

(ert-deftest rst-straighten-sections ()
  "Tests for `rst-straighten-sections'."
  (let ((rst-preferred-adornments '((?= over-and-under 1)
				    (?= simple 0)
				    (?- simple 0)
				    (?~ simple 0)
				    (?+ simple 0)
				    (?` simple 0)
				    (?# simple 0)
				    (?@ simple 0))))
    (should (ert-equal-buffer
	     '(rst-straighten-sections)
	     ""
	     t
	     ))
    (should (ert-equal-buffer
	     '(rst-straighten-sections)
	     "
First
-----

Second
======

First again
-----------

Second again
============

+++++
Third
+++++

"
	     "
=======
 First
=======

Second
======

=============
 First again
=============

Second again
============

Third
-----

"
	     ))
  ))

(defun find-all-levels ()
  "Call `rst-all-ttls-with-level' and return conses of line and level."
  (mapcar (cl-function
	   (lambda ((ttl . level))
	     (cons (line-number-at-pos (rst-Ttl-get-title-beginning ttl))
		   level)))
	  (rst-all-ttls-with-level)))

(ert-deftest rst-all-ttls-with-level ()
  "Tests for `rst-all-ttls-with-level'."
  (should (ert-equal-buffer-return
	   '(find-all-levels)
	   ""
	   t
	   nil
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-levels)
	   "
  Not a valid section header because of indentation
===================================================
"
	   t
	   nil
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-levels)
	   "
Valid simple section header
===========================
"
	   t
	   (list
	    '(2 . 0))
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-levels)
	   "
=======================================
  Valid over and under section header
=======================================
"
	   t
	   (list
	    '(3 . 0))
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-levels)
	   text-1
	   t
	   '(
	     (2 . 0)
	     (7 . 1)
	     (12 . 2)
	     (17 . 1)
	     (22 . 2)
	     (26 . 3)
	     (31 . 1))
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-levels)
	   text-2
	   t
	   '(
	     (3 . 0)
	     (6 . 1)
	     (9 . 2))
	   ))
  (should (ert-equal-buffer-return
	   '(find-all-levels)
	   text-3
	   t
	   '(
	     (3 . 0)
	     (6 . 1))
	   ))
  )

(defun update-section (char simplep indent)
  "Call `rst-update-section' with proper header."
  (rst-update-section
   (rst-Hdr-new (if simplep
		    (rst-Ado-new-simple char)
		  (rst-Ado-new-over-and-under char)) indent)))

(ert-deftest rst-update-section ()
  "Tests for `rst-update-section'."
  (should (ert-equal-buffer
	   '(update-section ?= t 0)
	   "

\^@abc

"
	   "

abc\^@
===

"
   
	   ))
  (should (ert-equal-buffer
	   '(update-section ?= nil 2)
	   "

\^@abc

"
	   "

=======
  abc\^@
=======

"
   
	   ))
  (should (ert-equal-buffer
	   '(update-section ?= nil 2)
	   "

def
---
\^@abc

"
	   "

def
---
=======
  abc\^@
=======

"
   
	   ))
  (should (ert-equal-buffer
	   '(update-section ?= nil 2)
	   "

---
\^@abc

"
	   "

=======
  abc\^@
=======

"
   
	   ))
  (should (ert-equal-buffer
	   '(update-section ?= t 0)
	   "\^@abc

"
	   "abc\^@
===

"
   
	   ))
  (should (ert-equal-buffer
	   '(update-section ?= nil 0)
	   "\^@abc

"
	   "===
abc\^@
===

"
   
	   ))
  (should (ert-equal-buffer
	   '(update-section ?= t 0)
	   "\^@abc"
	   "abc\^@
===
"
   
	   ))
  (should (ert-equal-buffer
	   '(update-section ?= t 0)
	   "\^@abc
"
	   "abc\^@
===
"
   
	   ))
  (should (ert-equal-buffer
	   '(update-section ?= t 0)
	   "\^@abc
 "
	   "abc\^@
===
 "
   
	   ))
  (should (ert-equal-buffer
	   '(update-section ?= t 0)
	   "===
\^@abc
===
"
	   "abc\^@
===
"
   
	   ))
  )
