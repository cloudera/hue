;; Tests for rst-adjust  -*- lexical-binding: t -*-
;;
;; These tests are for all use cases not only "filling" an existing adornment

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert t)

(ert-deftest adjust-uc-asserts ()
  "Check some assertions."
  (should (equal ert-Buf-point-char "\^@"))
  (should (equal ert-Buf-mark-char "\^?"))
  )

;; Each test tests a line in the use case chart. The conditions fixed by the
;; chart entry are noted before the test. The varying conditions are noted for
;; the individual test. A condition marked with "<" follows from another
;; condition setting.

(defun rst-ert-adjust-section (toggle-style reverse)
  "Call `rst-adjust-section' turning error messages into t."
  (and (rst-adjust-section toggle-style reverse) t))

;; :Prf: No preferences
;; :Sel: No adornment around point
;; :Prv: < No previous header
;; :Hie: < No hierarchy beyond current header
;; :Cur: < Does not apply
(ert-deftest rst-adjust-section-prf-N-sel-N-prv-N-hie-N-cur-!-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments nil))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
Document Title\^@
"
	     t
	     t))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
Document Title\^@
"
	     t
	     t))
    ))

;; :Prf: No preferences
;; :Sel: No adornment around point
;; :Prv: < No previous header
;; :Hie: < Existing
;; :Cur: < Does not apply
(ert-deftest rst-adjust-section-prf-N-sel-N-prv-N-hie-!-cur-!-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments nil))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
Document Title\^@

Hie 1
=====

Hie 1.1
-------
"
	     "
Document Title
==============

Hie 1
=====

Hie 1.1
-------
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
Document Title\^@

Hie 1
=====

Hie 1.1
-------
"
	     "
Document Title
==============

Hie 1
=====

Hie 1.1
-------
"
	     nil))
    ))

;; :Prf: No preferences
;; :Sel: No adornment around point
;; :Prv: < Disadvised
;; :Hie: < Existing
;; :Cur: < Does not apply
(ert-deftest rst-adjust-section-prf-N-sel-N-prv-D-hie-!-cur-!-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments nil))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
Document Title
==============

Hie 1\^@

Hie 1.1
-------
"
	     "
Document Title
==============

Hie 1
=====

Hie 1.1
-------
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
Document Title
==============

Hie 1\^@

Hie 1.1
-------
"
	     "
Document Title
==============

Hie 1
-----

Hie 1.1
-------
"
	     nil))
    ))

;; :Prf: No preferences
;; :Sel: Existing header around point
;; :Prv: < No previous header
;; :Hie: < No hierarchy beyond current header
;; :Cur: < Disadvised
(ert-deftest rst-adjust-section-prf-N-sel-E-prv-N-hie-N-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments nil))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
Document Title\^@
==============
"
	     t
	     t))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
Document Title\^@
==============
"
	     t
	     t))
    ))

;; :Prf: No preferences
;; :Sel: Existing header around point
;; :Prv: < No previous header
;; :Hie: < Multiple occurrence in the middle of existing hierarchy
;; :Cur: < Disadvised
(ert-deftest rst-adjust-section-prf-N-sel-E-prv-N-hie-M-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments nil))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
Hie 1\^@
-----

Hie 2
=====

Hie 2.1
-------

Hie 2.1.1
~~~~~~~~~
"
	     "
Hie 1
~~~~~

Hie 2
=====

Hie 2.1
-------

Hie 2.1.1
~~~~~~~~~
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
Hie 1\^@
-----

Hie 2
=====

Hie 2.1
-------

Hie 2.1.1
~~~~~~~~~
"
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 2.1.1
~~~~~~~~~
"
	     nil))
    ))

;; :Prf: No preferences
;; :Sel: Existing header around point
;; :Prv: < No previous header
;; :Hie: < Last in existing hierarchy
;; :Cur: < Disadvised
(ert-deftest rst-adjust-section-prf-N-sel-E-prv-N-hie-L-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments nil))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
Hie 1\^@
=====

Hie 2
=====

Hie 2.1
-------

Hie 2.1.1
~~~~~~~~~
"
	     "
Hie 1
~~~~~

Hie 2
=====

Hie 2.1
-------

Hie 2.1.1
~~~~~~~~~
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
Hie 1\^@
~~~~~

Hie 2
=====

Hie 2.1
-------

Hie 2.1.1
~~~~~~~~~
"
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 2.1.1
~~~~~~~~~
"
	     nil))
    ))

;; :Prf: No preferences
;; :Sel: Existing header around point
;; :Prv: < No previous header
;; :Hie: < Once in existing hierarchy
;; :Cur: < Disadvised
;; :Dir: Down
(ert-deftest rst-adjust-section-prf-N-sel-E-prv-N-hie-O-cur-D-dir-D ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments nil))
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
Hie 1\^@
$$$$$

Hie 2
=====

Hie 2.1
-------

Hie 2.1.1
~~~~~~~~~
"
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 2.1.1
~~~~~~~~~
"
	     nil))
    ))

;; :Prf: No preferences
;; :Sel: Existing header around point
;; :Prv: < No previous header
;; :Hie: < Once in existing hierarchy
;; :Cur: < Disadvised
;; :Dir: Up
(ert-deftest rst-adjust-section-prf-N-sel-E-prv-N-hie-O-cur-D-dir-U ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments nil))
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
Hie 1\^@
$$$$$

Hie 2
=====

Hie 2.1
-------

Hie 2.1.1
~~~~~~~~~
"
	     "
Hie 1
~~~~~

Hie 2
=====

Hie 2.1
-------

Hie 2.1.1
~~~~~~~~~
"
	     nil))
    ))

;; :Prf: No preferences
;; :Sel: Existing header around point
;; :Prv: < Disadvised previous header
;; :Hie: < Multiple occurrence in the middle of existing hierarchy
;; :Cur: < Disadvised
(ert-deftest rst-adjust-section-prf-N-sel-E-prv-D-hie-M-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments nil))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 3\^@
-----

Hie 3.1.1
~~~~~~~~~
"
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 3
=====

Hie 3.1.1
~~~~~~~~~
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 2.1.1\^@
---------

Hie 2.1.2
~~~~~~~~~
"
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 2.1.1
~~~~~~~~~

Hie 2.1.2
~~~~~~~~~
"
	     nil))
    ))

;; :Prf: No preferences
;; :Sel: Existing header around point
;; :Prv: < Disadvised previous header
;; :Hie: < Breaking single entry in the middle of existing hierarchy
;; :Cur: < Disadvised
(ert-deftest rst-adjust-section-prf-N-sel-E-prv-D-hie-B-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments nil))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
Hie 1
=====

Hie 2
=====

Hie 3\^@
$$$$$

Hie 3.1
~~~~~~~
"
	     "
Hie 1
=====

Hie 2
=====

Hie 3
=====

Hie 3.1
~~~~~~~
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1\^@
$$$$$$$

Hie 2.2
~~~~~~~
"
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
~~~~~~~

Hie 2.2
~~~~~~~
"
	     nil))
    ))

;; :Prf: No preferences
;; :Sel: Existing header around point
;; :Prv: < Disadvised previous header
;; :Hie: < Last in existing hierarchy
;; :Cur: < Disadvised
(ert-deftest rst-adjust-section-prf-N-sel-E-prv-D-hie-L-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments nil))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 2.2\^@
~~~~~~~

Hie 2.2.1
~~~~~~~~~
"
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 2.2
-------

Hie 2.2.1
~~~~~~~~~
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 3\^@
~~~~~

Hie 3.1.1
~~~~~~~~~
"
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 3
=====

Hie 3.1.1
~~~~~~~~~
"
	     nil))
    ))

;; :Prf: No preferences
;; :Sel: Existing header around point
;; :Prv: < Disadvised previous header
;; :Hie: < Once in existing hierarchy
;; :Cur: < Disadvised
(ert-deftest rst-adjust-section-prf-N-sel-E-prv-D-hie-O-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments nil))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 2.2\^@
~~~~~~~

Hie 3
=====
"
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 2.2
-------

Hie 3
=====
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 3\^@
~~~~~

Hie 4
=====
"
	     "
Hie 1
=====

Hie 2
=====

Hie 2.1
-------

Hie 3
=====

Hie 4
=====
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: No adornment around point
;; :Prv: < No previous header
;; :Hie: < No hierarchy beyond current header
;; :Cur: < Does not apply
;; :Dir: Irrelevant
(ert-deftest rst-adjust-section-prf-P-sel-N-prv-N-hie-N-cur-!-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
Document Title\^@
"
	     "
::::::::::::::::
 Document Title
::::::::::::::::
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
Document Title\^@
"
	     "
::::::::::::::::
 Document Title
::::::::::::::::
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: No adornment around point
;; :Prv: < No previous header
;; :Hie: < Existing
;; :Cur: < Does not apply
;; :Dir: Down
(ert-deftest rst-adjust-section-prf-P-sel-N-prv-N-hie-!-cur-!-dir-D ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
Document Title\^@

Hie 1
=====

Hie 1.1
-------
"
	     "
Document Title
==============

Hie 1
=====

Hie 1.1
-------
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: No adornment around point
;; :Prv: < No previous header
;; :Hie: < Existing
;; :Cur: < Does not apply
;; :Dir: Up
(ert-deftest rst-adjust-section-prf-P-sel-N-prv-N-hie-!-cur-!-dir-U ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
Document Title\^@

Hie 1
=====

Hie 1.1
-------
"
	     "
::::::::::::::::
 Document Title
::::::::::::::::

Hie 1
=====

Hie 1.1
-------
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Disadvised previous header
;; :Hie: < Multiple occurrence in the middle of existing hierarchy
;; :Cur: Disadvised
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-D-hie-M-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
==============
Document Title
==============

Additional title\^@
================

Hie 1.1
-------

Hie 2
=====
"
	     "
==============
Document Title
==============

================
Additional title
================

Hie 1.1
-------

Hie 2
=====
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
==============
Document Title
==============

Hie 1.0\^@
=======

Hie 1.1
-------

Hie 2
=====
"
	     "
==============
Document Title
==============

Hie 1.0
-------

Hie 1.1
-------

Hie 2
=====
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Disadvised previous header
;; :Hie: < Multiple occurrence in the middle of existing hierarchy
;; :Cur: Successor exists in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-D-hie-M-cur-S-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
==============
Document Title
==============

Additional title\^@
::::::::::::::::

Hie 1.1
-------

Hie 2
:::::
"
	     "
==============
Document Title
==============

================
Additional title
================

Hie 1.1
-------

Hie 2
:::::
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
==============
Document Title
==============

Hie 1.0\^@
:::::::

Hie 1.1
-------

Hie 2
:::::
"
	     "
==============
Document Title
==============

Hie 1.0
-------

Hie 1.1
-------

Hie 2
:::::
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Disadvised previous header
;; :Hie: < Multiple occurrence in the middle of existing hierarchy
;; :Cur: Last in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-D-hie-M-cur-L-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
==============
Document Title
==============

Additional title\^@
................

Hie 1.1
-------

Hie 2
.....
"
	     "
==============
Document Title
==============

================
Additional title
================

Hie 1.1
-------

Hie 2
.....
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
==============
Document Title
==============

Hie 1.0\^@
.......

Hie 1.1
-------

Hie 2
.....
"
	     "
==============
Document Title
==============

Hie 1.0
-------

Hie 1.1
-------

Hie 2
.....
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Disadvised previous header
;; :Hie: < Breaking single entry in the middle of existing hierarchy
;; :Cur: Disadvised
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-D-hie-B-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
==============
Document Title
==============

Additional title\^@
$$$$$$$$$$$$$$$$

Hie 1.1
-------

Hie 2
.....
"
	     "
==============
Document Title
==============

================
Additional title
================

Hie 1.1
-------

Hie 2
.....
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
==============
Document Title
==============

Hie 1.0\^@
$$$$$$$

Hie 1.1
-------

Hie 2
.....
"
	     "
==============
Document Title
==============

Hie 1.0
-------

Hie 1.1
-------

Hie 2
.....
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Disadvised previous header
;; :Hie: < Breaking single entry in the middle of existing hierarchy
;; :Cur: Successor exists in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-D-hie-B-cur-S-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
==============
Document Title
==============

Additional title\^@
::::::::::::::::

Hie 1.1
-------

Hie 2
=====
"
	     "
==============
Document Title
==============

================
Additional title
================

Hie 1.1
-------

Hie 2
=====
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
==============
Document Title
==============

Hie 1.0\^@
:::::::

Hie 1.1
-------

Hie 2
=====
"
	     "
==============
Document Title
==============

Hie 1.0
-------

Hie 1.1
-------

Hie 2
=====
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Disadvised previous header
;; :Hie: < Breaking single entry in the middle of existing hierarchy
;; :Cur: Last in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-D-hie-B-cur-L-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
==============
Document Title
==============

Additional title\^@
................

Hie 1.1
-------

Hie 2
=====
"
	     "
==============
Document Title
==============

================
Additional title
================

Hie 1.1
-------

Hie 2
=====
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
==============
Document Title
==============

Hie 1.0\^@
.......

Hie 1.1
-------

Hie 2
=====
"
	     "
==============
Document Title
==============

Hie 1.0
-------

Hie 1.1
-------

Hie 2
=====
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Disadvised previous header
;; :Hie: < Last in existing hierarchy for given direction
;; :Cur: Disadvised (i.e. not in preferences)
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-D-hie-L-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
==============
Document Title
==============

Hie 1
=====

Hie 1.1
-------

=========
Hie 1.1.1\^@
=========
"
	     "
==============
Document Title
==============

Hie 1
=====

Hie 1.1
-------

:::::::::::
 Hie 1.1.1
:::::::::::
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
==============
Document Title
==============

Hie 1
=====

Hie 1.1
-------

Additional title\^@
~~~~~~~~~~~~~~~~
"
	     "
==============
Document Title
==============

Hie 1
=====

Hie 1.1
-------

================
Additional title
================
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Disadvised previous header
;; :Hie: < Last in existing hierarchy for given direction
;; :Cur: Successor exists in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-D-hie-L-cur-S-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
-------

:::::::::
Hie 1.1.1\^@
:::::::::
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
-------

Hie 1.1.1
:::::::::
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
-------

:::::
Hie 2\^@
:::::
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
-------

.....
Hie 2
.....
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Disadvised previous header
;; :Hie: < Last in existing hierarchy for given direction
;; :Cur: Successor exists in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-D-hie-L-cur-S-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
-------

:::::::::
Hie 1.1.1\^@
:::::::::
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
-------

Hie 1.1.1
:::::::::
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
-------

:::::
Hie 2\^@
:::::
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
-------

.....
Hie 2
.....
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Disadvised previous header
;; :Hie: < Last in existing hierarchy for given direction
;; :Cur: Last in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-D-hie-L-cur-L-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
-------

Hie 1.2\^@
.......
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
-------

Hie 1.2
-------
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
-------

Another title\^@
.............
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
-------

:::::::::::::
Another title
:::::::::::::
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Disadvised previous header
;; :Hie: Once in existing hierarchy at beginning or end of hierarchy
;; :Cur: Disadvised (i.e. not in preferences)
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-D-hie-O-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
=======

Hie 1.2\^@
-------
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
=======

Hie 1.2
=======
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
=======

Other title\^@
-----------
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
=======

:::::::::::
Other title
:::::::::::
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Disadvised previous header
;; :Hie: Once in existing hierarchy at beginning or end of hierarchy
;; :Cur: Successor exists in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-D-hie-O-cur-S-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
=======

Hie 1.2\^@
:::::::
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
=======

Hie 1.2
=======
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
=======

Other title\^@
:::::::::::
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
=======

:::::::::::
Other title
:::::::::::
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Disadvised previous header
;; :Hie: Once in existing hierarchy at beginning or end of hierarchy
;; :Cur: Last in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-D-hie-O-cur-L-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
=======

Hie 1.2\^@
.......
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
=======

Hie 1.2
=======
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
=======

Other title\^@
...........
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
=======

:::::::::::
Other title
:::::::::::
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Preferences contain previous header
;; :Hie: < Multiple occurrence in the middle of existing hierarchy
;; :Cur: Disadvised (i.e. not in preferences)
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-P-hie-M-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 2\^@
=====

Hie 1.2
=======

Hie 1.2.1
---------
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

.....
Hie 2
.....

Hie 1.2
=======

Hie 1.2.1
---------
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.x.1\^@
=========

Hie 1.2
=======

Hie 1.2.1
---------
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.x.1
---------

Hie 1.2
=======

Hie 1.2.1
---------
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Preferences contain previous header
;; :Hie: < Multiple occurrence in the middle of existing hierarchy
;; :Cur: Successor exists in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-P-hie-M-cur-S-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 2\^@
:::::

Hie 1.2
:::::::

Hie 1.2.1
---------
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

.....
Hie 2
.....

Hie 1.2
:::::::

Hie 1.2.1
---------
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.x.1\^@
:::::::::

Hie 1.2
:::::::

Hie 1.2.1
---------
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.x.1
---------

Hie 1.2
:::::::

Hie 1.2.1
---------
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Preferences contain previous header
;; :Hie: < Multiple occurrence in the middle of existing hierarchy
;; :Cur: Last in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-P-hie-M-cur-L-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 2\^@
.....

Hie 1.2
.......

Hie 1.2.1
---------
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

.....
Hie 2
.....

Hie 1.2
.......

Hie 1.2.1
---------
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.x.1\^@
.........

Hie 1.2
.......

Hie 1.2.1
---------
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.x.1
---------

Hie 1.2
.......

Hie 1.2.1
---------
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Preferences contain previous header
;; :Hie: < Breaking single entry in the middle of existing hierarchy
;; :Cur: Disadvised (i.e. not in preferences)
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-P-hie-B-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 2\^@
=====

Hie 1.1.1
---------
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

.....
Hie 2
.....

Hie 1.1.1
---------
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.x.1\^@
=========

Hie 1.1.1
---------
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.x.1
---------

Hie 1.1.1
---------
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Preferences contain previous header
;; :Hie: < Breaking single entry in the middle of existing hierarchy
;; :Cur: Successor exists in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-P-hie-B-cur-S-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 2\^@
=====

Hie 1.1.1
.........
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

.....
Hie 2
.....

Hie 1.1.1
.........
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.x.1\^@
=========

Hie 1.1.1
.........
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.x.1
.........

Hie 1.1.1
.........
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Preferences contain previous header
;; :Hie: < Breaking single entry in the middle of existing hierarchy
;; :Cur: Last in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-P-hie-B-cur-L-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 2\^@
.....

Hie 1.1.1
---------
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

.....
Hie 2
.....

Hie 1.1.1
---------
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.x.1\^@
.........

Hie 1.1.1
---------
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.x.1
---------

Hie 1.1.1
---------
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Preferences contain previous header
;; :Hie: < Last in existing hierarchy for given direction
;; :Cur: Disadvised (i.e. not in preferences)
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-P-hie-L-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
==============
Document Title
==============

.....
Hie 1
.....

=======
Hie 1.1\^@
=======

Hie 1.2
-------
"
	     "
==============
Document Title
==============

.....
Hie 1
.....

Hie 1.1
:::::::

Hie 1.2
-------
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
==============
Document Title
==============

.....
Hie 1
.....

Hie 1.1\^@
-------

Hie 1.2
-------
"
	     "
==============
Document Title
==============

.....
Hie 1
.....

Hie 1.1
:::::::

Hie 1.2
-------
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Preferences contain previous header
;; :Hie: < Last in existing hierarchy for given direction
;; :Cur: Successor exists in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-P-hie-L-cur-S-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

:::::::
Hie 1.1\^@
:::::::

Hie 1.2
-------
"
	     "
::::::::::::::
Document Title
::::::::::::::

.....
Hie 1
.....

Hie 1.1
:::::::

Hie 1.2
-------
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
==============
Document Title
==============

.....
Hie 1
.....

Hie 1.1\^@
:::::::

Hie 1.2
:::::::
"
	     "
==============
Document Title
==============

.....
Hie 1
.....

Hie 1.1
.......

Hie 1.2
:::::::
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Preferences contain previous header
;; :Hie: < Last in existing hierarchy for given direction
;; :Cur: Last in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-P-hie-L-cur-L-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
Document Title
..............

.....
Hie 1
.....

Hie 1.1\^@
.......

Hie 1.2
-------
"
	     "
Document Title
..............

.....
Hie 1
.....

Hie 1.1
:::::::

Hie 1.2
-------
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
==============
Document Title
==============

.....
Hie 1
.....

Hie 1.1\^@
.......

Hie 1.2
.......
"
	     "
==============
Document Title
==============

.....
Hie 1
.....

Hie 1.1
:::::::

Hie 1.2
.......
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Preferences contain previous header
;; :Hie: < Once in existing hierarchy at beginning or end of hierarchy
;; :Cur: Disadvised (i.e. not in preferences)
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-P-hie-O-cur-D-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
==============
Document Title
==============

.....
Hie 1
.....

Hie 2\^@
=====
"
	     "
==============
Document Title
==============

.....
Hie 1
.....

.....
Hie 2
.....
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
==============
Document Title
==============

.....
Hie 1
.....

Title\^@
=====
"
	     "
==============
Document Title
==============

.....
Hie 1
.....

=====
Title
=====
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Preferences contain previous header
;; :Hie: < Once in existing hierarchy at beginning or end of hierarchy
;; :Cur: Successor exists in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-P-hie-O-cur-S-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
==============
Document Title
==============

.....
Hie 1
.....

Hie 2\^@
:::::
"
	     "
==============
Document Title
==============

.....
Hie 1
.....

.....
Hie 2
.....
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
==============
Document Title
==============

.....
Hie 1
.....

Title\^@
:::::
"
	     "
==============
Document Title
==============

.....
Hie 1
.....

=====
Title
=====
"
	     nil))
    ))

;; :Prf: Preferences exist
;; :Sel: < Existing adornment around point
;; :Prv: Preferences contain previous header
;; :Hie: < Once in existing hierarchy at beginning or end of hierarchy
;; :Cur: Last in preferences
;; :Dir: Any
(ert-deftest rst-adjust-section-prf-P-sel-E-prv-P-hie-O-cur-L-dir-? ()
  (let ((rst-new-adornment-down nil)
	(rst-default-indent 3)
	(rst-preferred-adornments '((?: over-and-under 1)
				    (?. over-and-under 1)
				    (?: simple 0)
				    (?. simple 0))))
    ;; :Dir: Up
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil nil)
	     "
==============
Document Title
==============

.....
Hie 1
.....

Hie 2\^@
.....
"
	     "
==============
Document Title
==============

.....
Hie 1
.....

.....
Hie 2
.....
"
	     nil))
    ;; :Dir: Down
    (should (ert-equal-buffer-return
	     '(rst-ert-adjust-section nil t)
	     "
==============
Document Title
==============

.....
Hie 1
.....

Title\^@
.....
"
	     "
==============
Document Title
==============

.....
Hie 1
.....

=====
Title
=====
"
	     nil))
    ))
