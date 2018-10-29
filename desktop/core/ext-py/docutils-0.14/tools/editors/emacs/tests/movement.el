;; Tests for various movement commands  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert t)

(ert-deftest movement-asserts ()
  "Check some assertions."
  (should (equal ert-Buf-point-char "\^@"))
  (should (equal ert-Buf-mark-char "\^?"))
  )

(defun fwd-para ()
  "Wrapper to call `forward-paragraph'."
  (rst-mode)
  (forward-paragraph))

(ert-deftest forward-paragraph ()
  "Tests for `forward-paragraph'."
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "
:Field: Content
\^@
  More content
  over several

  * An item
    with multi
"
	   "
:Field: Content

  More content
  over several
\^@
  * An item
    with multi
"
	   0
	   ))


  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "\^@
This is
a short
para"
	   "
This is
a short
para\^@"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "\^@
This is
a short
para
"
	   "
This is
a short
para
\^@"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "\^@
This is
a short
para

"
	   "
This is
a short
para
\^@
"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "\^@
This is
a short
para


"
	   "
This is
a short
para
\^@

"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "
\^@This is
a short
para

"
	   "
This is
a short
para
\^@
"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "
This is
a short
\^@para

"
	   "
This is
a short
para
\^@
"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "
This is
a short
\^@para

"
	   "
This is
a short
para
\^@
"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "
This is
\^@a short
  para

"
	   "
This is
a short
  para
\^@
"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "
This is
a short
\^@para

This is
a short
para

"
	   "
This is
a short
para
\^@
This is
a short
para

"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "
\^@* An item

* Another item
"
	   "
* An item
\^@
* Another item
"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "
\^@* An item
* Another item
"
	   "
* An item
\^@* Another item
"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "
\^@:Field: Content

  More content
  over several

  * An item
    with multi
"
	   "
:Field: Content
\^@
  More content
  over several

  * An item
    with multi
"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "
:Field: Content
\^@
  More content
  over several

  * An item
    with multi
"
	   "
:Field: Content

  More content
  over several
\^@
  * An item
    with multi
"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "
:Field: Content

  More content
  over several
\^@
  * An item
    with multi
"
	   "
:Field: Content

  More content
  over several

  * An item
    with multi
\^@"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "\^@
.. |s| d::
  :F: Content

    More content
    over several
  * An item
    with multi
"
	   "
.. |s| d::
\^@  :F: Content

    More content
    over several
  * An item
    with multi
"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "
.. |s| d::
\^@  :F: Content

    More content
    over several
  * An item
    with multi
"
	   "
.. |s| d::
  :F: Content
\^@
    More content
    over several
  * An item
    with multi
"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "
.. |s| d::
  :F: Content
\^@
    More content
    over several
  * An item
    with multi
"
	   "
.. |s| d::
  :F: Content

    More content
    over several
\^@  * An item
    with multi
"
	   0
	   ))
  (should (ert-equal-buffer-return
	   '(fwd-para)
	   "
.. |s| d::
  :F: Content

    More content
    over several
\^@  * An item
    with multi
"
	   "
.. |s| d::
  :F: Content

    More content
    over several
  * An item
    with multi
\^@"
	   0
	   ))
  )

(ert-deftest rst-forward-section ()
  "Tests for `rst-forward-section'."
  (should (ert-equal-buffer
	   '(rst-forward-section -1)
	   "
========
\^@Header 1
========

Some text

Header 2
========
"
	   "\^@
========
Header 1
========

Some text

Header 2
========
"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 1)
	   "\^@"
	   "\^@"))
  (should (ert-equal-buffer
	   '(rst-forward-section 1)
	   "
Some text\^@

More text
"
	   "
Some text

More text
\^@"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 1)
	   "
Some text

More text
\^@"
	   "
Some text

More text
\^@"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section -1)
	   "
Some text

More text
\^@"
	   "\^@
Some text

More text
"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 1)
	   "
\^@Header 1
========

Some text
"
	   "
Header 1
========

Some text
\^@"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 1)
	   "
Header 1\^@
========

Some text
"
	   "
Header 1
========

Some text
\^@"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 1)
	   "
Header 1
===\^@=====

Some text
"
	   "
Header 1
========

Some text
\^@"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 1)
	   "
Header 1\^@
========

Some text

Header 2
========
"
	   "
Header 1
========

Some text

\^@Header 2
========
"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 1)
	   "
Header 1
========

\^@Some text

Header 2
========
"
	   "
Header 1
========

Some text

\^@Header 2
========
"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 1)
	   "
Header 1
========\^@

Some text

Header 2
========
"
	   "
Header 1
========

Some text

\^@Header 2
========
"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 1)
	   "
========
\^@Header 1
========

Some text

Header 2
========
"
	   "
========
Header 1
========

Some text

\^@Header 2
========
"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 1)
	   "
\^@========
Header 1
========

Some text

Header 2
========
"
	   "
========
Header 1
========

Some text

\^@Header 2
========
"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section -1)
	   "
========
Header 1
========

Some text

\^@Header 2
========
"
	   "
========
\^@Header 1
========

Some text

Header 2
========
"
	   ))

; ****

  (should (ert-equal-buffer
	   '(rst-forward-section 2)
	   "\^@
========
Header 1
========

Some text

Header 2
========
"
	   "
========
Header 1
========

Some text

\^@Header 2
========
"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 3)
	   "
========
\^@Header 1
========

Some text

Header 2
========

Header 3
========

Header 4
========
"
	   "
========
Header 1
========

Some text

Header 2
========

Header 3
========

\^@Header 4
========
"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 3)
	   "\^@
========
Header 1
========

Some text

Header 2
========
"
	   "
========
Header 1
========

Some text

Header 2
========
\^@"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 0)
	   "
========
Header 1\^@
========

Some text

Header 2
========
"
	   "
========
\^@Header 1
========

Some text

Header 2
========
"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 0)
	   "
========\^@
Header 1
========

Some text

Header 2
========
"
	   "
========
\^@Header 1
========

Some text

Header 2
========
"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 0)
	   "
========
Header 1
========\^@

Some text

Header 2
========
"
	   "
========
\^@Header 1
========

Some text

Header 2
========
"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section 0)
	   "
========
Header 1
========

Some text\^@

Header 2
========
"
	   "
========
Header 1
========

Some text\^@

Header 2
========
"
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section -)
	   "
========
Header 1
========

Some text

\^@Header 2
========
"
	   "
========
\^@Header 1
========

Some text

Header 2
========
"
	   t))
  (should (ert-equal-buffer
	   '(rst-forward-section nil)
	   "
========
\^@Header 1
========

Some text

Header 2
========
"
	   "
========
Header 1
========

Some text

\^@Header 2
========
"
	   t
	   ))
  (should (ert-equal-buffer
	   '(rst-forward-section (4))
	   "\^@
========
Header 1
========

Some text

Header 2
========
"
	   "
========
Header 1
========

Some text

Header 2
========
\^@"
	   t))
  (should (ert-equal-buffer
	   '(rst-backward-section nil)
	   "
========
Header 1
========

Some text

\^@Header 2
========
"
	   "
========
\^@Header 1
========

Some text

Header 2
========
"
	   t))
  )
