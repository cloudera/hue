;; Tests for font-locking code  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert t)

(ert-deftest font-lock--asserts ()
  "Check some assertions."
  (should (equal ert-Buf-point-char "\^@"))
  (should (equal ert-Buf-mark-char "\^?"))
  )

(ert-deftest rst-forward-indented-block ()
  "Tests `rst-forward-indented-block'."
  (should (ert-equal-buffer-return
	   '(rst-forward-indented-block)
	   "\^@abc"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-forward-indented-block)
	   (concat "  \^@abc

def")
	   (concat "  abc
\^@
def")
	   7))
  (should (ert-equal-buffer-return
	   '(rst-forward-indented-block)
	   (concat "  \^@abc
def")
	   (concat "  abc
\^@def")
	   7))
  (should (ert-equal-buffer-return
	   '(rst-forward-indented-block)
	   (concat "  \^@abc
  def
ghi")
	   (concat "  abc
  def
\^@ghi")
	   13))
  (should (ert-equal-buffer-return
	   '(rst-forward-indented-block)
	   (concat "  \^@abc
  def

ghi")
	   (concat "  abc
  def
\^@
ghi")
	   13))
  (should (ert-equal-buffer-return
	   '(rst-forward-indented-block)
	   (concat "  \^@abc

  def

ghi")
	   (concat "  abc

  def
\^@
ghi")
	   14))
  (should (ert-equal-buffer-return
	   '(rst-forward-indented-block)
	   (concat "  \^@abc


    def


ghi")
	   (concat "  abc


    def
\^@

ghi")
	   17))
  (should (ert-equal-buffer-return
	   '(rst-forward-indented-block)
	   (concat "  \^@abc
    def
ghi")
	   (concat "  abc
    def
\^@ghi")
	   15))
  (should (ert-equal-buffer-return
	   '(rst-forward-indented-block)
	   (concat "  \^@abc

    def")
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-forward-indented-block)
	   (concat "\^@abc
  def
ghi
")
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(rst-forward-indented-block)
	   (concat "abc\^@ def
ghi
")
	   (concat "abc def
\^@ghi
")
	   9))
  (should (ert-equal-buffer-return
	   '(rst-forward-indented-block)
	   (concat "abc\^@ def
ghi")
	   (concat "abc def
\^@ghi")
	   9))
  (should (ert-equal-buffer-return
	   '(rst-forward-indented-block)
	   (concat ".. \^@abc
   def

   ghi

jkl
")
	   (concat ".. abc
   def

   ghi
\^@
jkl
")
	   23))
  )

(defun extend-region (beg end)
  "Wrapper for `rst-font-lock-extend-region-internal'.
Uses and sets region and returns t if region has been changed."
  (interactive "r")
  (let ((r (rst-font-lock-extend-region-internal beg end)))
    (when r
      (goto-char (car r))
      (set-mark (cdr r))
      t)))

(ert-deftest rst-font-lock-extend-region-internal-indent ()
  "Tests `rst-font-lock-extend-region-internal'."
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "\^@abc\^?"
	   t
	   nil
	   t))
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "\^@  abc\^?"
	   t
	   nil
	   t))
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "  abc
\^@  def\^?"
	   "\^@  abc
  def\^?"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "  abc
\^@  def
\^?  ghi
uvw"
	   "\^@  abc
  def
  ghi
\^?uvw"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "xyz
abc
\^@  def
\^?  ghi"
	   "xyz
\^@abc
  def
  ghi\^?"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "xyz
  abc::
\^@  def
\^?  ghi
uvw"
	   "xyz
\^@  abc::
  def
  ghi
\^?uvw"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "xyz
  .. abc
\^@     def
\^?uvw"
	   "xyz
\^@  .. abc
     def
\^?uvw"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "xyz
  .. abc
     123
\^@       def
\^?
uvw"
	   "xyz
\^@  .. abc
     123
       def
\^?
uvw"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "xyz

  .. abc

     123

\^@       def
\^?
uvw"
	   "xyz

\^@  .. abc

     123

       def
\^?
uvw"
	   t
	   t))
  )

(ert-deftest rst-font-lock-extend-region-internal-adornment ()
  "Tests `rst-font-lock-extend-region-internal'."
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "\^@===\^?"
	   t
	   nil
	   t))
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "abc
\^@===\^?"
	   "\^@abc
===\^?"
	   t
	   t))
  (should (ert-equal-buffer-return ; Quite complicated without the trailing newline
	   '(extend-region)
	   "\^@abc
\^?==="
	   t
	   nil
	   t))
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "\^@abc
\^?===
"
	   "\^@abc
===
\^?"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "===
abc
\^@===
\^?"
	   "\^@===
abc
===
\^?"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "\^@===
\^?abc
===
"
	   "\^@===
abc
===
\^?"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "def

===
\^@abc
===
\^?"
	   "def

\^@===
abc
===
\^?"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(extend-region)
	   "def

\^@===
abc
\^?===

xyz"
	   "def

\^@===
abc
===
\^?
xyz"
	   t
	   t))
  )
