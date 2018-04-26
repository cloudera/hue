;; Tests for comment handling  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert t)

(ert-deftest comment-asserts ()
  "Check some assertions."
  (should (equal ert-Buf-point-char "\^@"))
  (should (equal ert-Buf-mark-char "\^?"))
  )

(defun cmnt-insert ()
  "Wrapper to insert comment via `comment-dwim'.
Must be called on a line conaining at most whitespace."
  (let ((fc fill-column))
    (rst-mode)
    (setq fill-column fc)
    (comment-dwim nil)))

(ert-deftest comment-insert ()
  "Tests for inserting a comment."
  (let ((rst-indent-width 2)
	(rst-indent-comment 3)
	(fill-column 20))
    (should (ert-equal-buffer
	     '(cmnt-insert)
	     "\^@"
	     ".. \^@"
	     ))
    (should (ert-equal-buffer
	     '(cmnt-insert)
	     "
   \^@"
	     "
.. \^@"
	     ))
    (should (ert-equal-buffer
	     '(cmnt-insert)
	     "
* bla

   \^@"
	     "
* bla

  .. \^@"
	     ))
    (should (ert-equal-buffer
	     '(cmnt-insert)
	     "
:Field: Content

\^@"
	     "
:Field: Content

	.. \^@"
	     ))
    ))

(defun cmnt-indent (continue)
  "Wrapper for `comment-indent'."
  (let ((fc fill-column))
    (rst-mode)
    (setq fill-column fc)
    (comment-indent continue)))

(ert-deftest comment-indent ()
  "Tests for `comment-indent'."
  (let ((rst-indent-width 2)
	(rst-indent-comment 3)
	(fill-column 20))
    (should (ert-equal-buffer
	     '(cmnt-indent nil)
	     "\^@"
	     ".. \^@"
	     ))
    (should (ert-equal-buffer
	     '(cmnt-indent nil)
	     "
   \^@"
	     "
.. \^@"
	     ))
    (should (ert-equal-buffer
	     '(cmnt-indent nil)
	     ".. comment\^@"
	     ".. \^@comment"
	     ))
    (should (ert-equal-buffer
	     '(cmnt-indent nil)
	     "
* bla

.. comment\^@"
	     "
* bla

  .. \^@comment"
	     ))
    (should (ert-equal-buffer
	     '(cmnt-indent nil)
	     "
:Field: Content

\^@"
	     "
:Field: Content

	.. \^@"
	     ))
    (should (ert-equal-buffer
	     '(cmnt-indent nil)
	     "
:Field: Content

.. comment\^@"
	     "
:Field: Content

	.. \^@comment"
	     ))
    ))

(defun uncmnt-region ()
  "Wrapper for `uncomment-region'."
  (let ((fc fill-column))
    (rst-mode)
    (setq fill-column fc)
    (call-interactively 'uncomment-region)))

(ert-deftest uncomment-region ()
  "Tests for `uncomment-region'."
  (let ((rst-indent-width 2)
	(rst-indent-comment 3)
	(fill-column 20))
    (should (ert-equal-buffer
	     '(uncmnt-region)
	     "\^?..
   com\^@ment"
	     "\^?com\^@ment"
	     ))
    (should (ert-equal-buffer
	     '(uncmnt-region)
	     "\^?..
   com\^@ment

   bla
"
	     "\^?com\^@ment

   bla
"
	     ))
    (should (ert-equal-buffer
	     '(uncmnt-region)
	     "\^?..
   comment

   bl\^@a
"
	     "\^?comment

bl\^@a
"
	     ))
    ))

(defun cmnt-region ()
  "Wrapper for `comment-region'."
  (let ((fc fill-column))
    (rst-mode)
    (setq fill-column fc)
    (call-interactively 'comment-region)))

(ert-deftest comment-region ()
  "Tests for `comment-region'."
  (let ((rst-indent-width 2)
	(rst-indent-comment 3)
	(fill-column 20))
    (should (ert-equal-buffer
	     '(cmnt-region)
	     "\^?com\^@ment"
	     "\^?..
   com\^@ment"
	     ))
    (should (ert-equal-buffer
	     '(cmnt-region)
	     "\^?com\^@ment

   bla
"
	     "\^?..
   com\^@ment

   bla
"
	     ))
    (should (ert-equal-buffer
	     '(cmnt-region)
	     "\^?comment

bl\^@a
"
	     "\^?..
   comment

   bl\^@a
"
	     ))
    ))

;; comment-kill could be tested but since there are no suffix comments in
;; reStructuredText this makes little sense
