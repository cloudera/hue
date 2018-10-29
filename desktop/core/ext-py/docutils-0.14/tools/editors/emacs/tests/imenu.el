;; Tests for rst-imenu-create-index  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert t)

(ert-deftest imenu-asserts ()
  "Check some assertions."
  (should (equal ert-Buf-point-char "\^@"))
  (should (equal ert-Buf-mark-char "\^?"))
  )

(ert-deftest rst-imenu-create-index ()
  "Tests for `rst-imenu-create-index'."
    (should (ert-equal-buffer-return
	     '(rst-imenu-create-index)
	     "
"
	     t
	     nil))
    (should (ert-equal-buffer-return
	     '(rst-imenu-create-index)
	     "
Some normal text.
"
	     t
	     nil))
    (should (ert-equal-buffer-return
	     '(rst-imenu-create-index)
	     "
Header
======"
	     t
	     '(("=Header" . 2))))
    (should (ert-equal-buffer-return
	     '(rst-imenu-create-index)
	     "
============
  Indented
============"
	     t
	     '(("=Indented=" . 15))))
    (should (ert-equal-buffer-return
	     '(rst-imenu-create-index)
	     "
~~~~~~~~~~~~~~
Over and under
~~~~~~~~~~~~~~"
	     t
	     '(("~Over and under~" . 17))))
    (should (ert-equal-buffer-return
	     '(rst-imenu-create-index)
	     "
Header
======

Subheader
---------"
	     t
	     '(("=Header"
		("=Header" . 2)
		("-Subheader" . 17)))))
    (should (ert-equal-buffer-return
	     '(rst-imenu-create-index)
	     "
Header
======

Subheader
---------

With space
----------"
	     t
	     '(("=Header"
		("=Header" . 2)
		("-Subheader" . 17)
		("-With space" . 38)))))
    (should (ert-equal-buffer-return
	     '(rst-imenu-create-index)
	     "
Header
======

Subheader
---------

With space
----------

Top level again
==============="
	     t
	     '(("=Header"
		("=Header" . 2)
		("-Subheader" . 17)
		("-With space" . 38))
	       ("=Top level again" . 61))))
    (should (ert-equal-buffer-return
	     '(rst-imenu-create-index)
	     "
Header
======

Subheader
---------

With space
----------

Sub sub
~~~~~~~

Top level again
==============="
	     t
	     '(("=Header"
		("=Header" . 2)
		("-Subheader" . 17)
		("-With space"
		 ("-With space" . 38)
		 ("~Sub sub" . 61)))
	       ("=Top level again" . 78))))
    )

;; FIXME: Test missing intermediate sections.
;; FIXME: Test document titles.
