;; Tests for operations on toc  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert t)

(ert-deftest toc-asserts ()
  "Check some assertions."
  (should (equal ert-Buf-point-char "\^@"))
  (should (equal ert-Buf-mark-char "\^?"))
  )

(setq title "=====
Title
=====

"
      headers "Header A
========

Header B
========

Subheader B.a
-------------

SubSubheader B.a.1
~~~~~~~~~~~~~~~~~~

Subheader B.b
-------------

Header C
========")

(ert-deftest rst-toc-insert ()
  "Tests `rst-toc-insert'."
  ;; Set customizable variables to defaults
  (let ((rst-toc-indent 2)
	(rst-toc-insert-style 'fixed)
	(rst-toc-insert-number-separator " - ")
	(rst-toc-insert-max-level nil)
	(indent-tabs-mode nil))
    (should (ert-equal-buffer
	     '(rst-toc-insert)
	     ""
	     t))
    ;; Can't identify a title so do nothing - that's actually a (MIS-)FEATURE
    (should (ert-equal-buffer
	     '(rst-toc-insert)
	     (concat "\^@" headers)
	     t))
    ;; Can't identify a title so do nothing - that's actually a (MIS-)FEATURE
    (should (ert-equal-buffer
	     (rst-toc-insert)
	     (concat "\^@\n" headers)
	     t))
    ;; Won't work on a section title
    (should (ert-equal-buffer
	     '(rst-toc-insert)
	     (concat title "\^@" headers)
	     t))
    ;; No indentation
    (let ((rst-toc-indent 1))
      (should (ert-equal-buffer
	       '(rst-toc-insert)
	       (concat title "\^@THIS IS DELETED\n\n" headers)
	       (concat title "1 - Header A
2 - Header B
 2.1 - Subheader B.a
  2.1.1 - SubSubheader B.a.1
 2.2 - Subheader B.b
3 - Header C\^@

" headers))))
    ;; Indentation
    (let ((rst-toc-insert-style 'listed)
	  (rst-preferred-bullets '(?+))
	  (rst-toc-indent 1))
      (should (ert-equal-buffer
	       '(rst-toc-insert)
	       (concat title "  \^@\n\n" headers)
	       (concat title "  + Header A
  + Header B
    + Subheader B.a
      + SubSubheader B.a.1
    + Subheader B.b
  + Header C\^@

" headers))))
    ;; Only first level
    (let ((rst-toc-insert-style 'plain))
      (should (ert-equal-buffer
	       '(rst-toc-insert 1)
	       (concat title "  \^@\n\n" headers)
	       (concat title "  Header A
  Header B
  Header C\^@

" headers))))
    ;; Prefix and indentation
    (let ((rst-toc-insert-style 'aligned)
	  (headers-add "

C_1
---

C_2
---

C_3
---

C_4
---

C_5
---

C_6
---

C_7
---

C_8
---

C_9
---

C_10
----
"))
      (should (ert-equal-buffer
	       '(rst-toc-insert)
	       (concat title "..  \^@\n\n" headers headers-add)
	       (concat title "..  1 - Header A
    2 - Header B
        2.1 - Subheader B.a
              2.1.1 - SubSubheader B.a.1
        2.2 - Subheader B.b
    3 - Header C
        3. 1 - C_1
        3. 2 - C_2
        3. 3 - C_3
        3. 4 - C_4
        3. 5 - C_5
        3. 6 - C_6
        3. 7 - C_7
        3. 8 - C_8
        3. 9 - C_9
        3.10 - C_10\^@

" headers headers-add))))
      )
    )

(ert-deftest rst-toc-update ()
  "Tests `rst-toc-update'."
  (let ((contents ".. contents:: Inhalt\n")
	(fields "   :bla: blub\n   :local:\n")
	(old "..  1  Header A
    2  Header B
    3  Header C")
	(new "..
    1  Header A
    2  Header B
      2.1  Subheader B.a
        2.1.1  SubSubheader B.a.1
      2.2  Subheader B.b
    3  Header C")
	(indent-tabs-mode nil))
    ;; Set customizable variables to defaults
    (let ((rst-toc-indent 2)
	  (rst-toc-insert-style 'fixed)
	  (rst-toc-insert-number-separator "  ")
	  (rst-toc-insert-max-level nil))
      (should (ert-equal-buffer
	       '(rst-toc-update)
	       (concat title contents fields old "\n\n" headers "\^@")
	       (concat title contents fields new "\n\n" headers "\^@")))
      (should (ert-equal-buffer
	       '(rst-toc-update)
	       (concat title contents old "\n\n" headers "\^@")
	       (concat title contents new "\n\n" headers "\^@")))
      (should (ert-equal-buffer
	       '(rst-toc-update)
	       (concat title contents ".." "\n\n" headers "\^@")
	       (concat title contents new "\n\n" headers "\^@")))
      (should (ert-equal-buffer
	       '(rst-toc-update)
	       (concat title contents ".." "\^@")
	       (concat title contents ".." "\^@")))
      )
    ))

(defun toc ()
  "Call `rst-toc' and copy special buffer to target buffer.
Return line number link is pointing to in original buffer or nil for no link."
  (rst-toc)
  (let ((txt (buffer-substring-no-properties (point-min) (point-max)))
	(pt (point))
	(mrk (mark t))
	(lnk (condition-case nil
		 (progn
		   (rst-toc-mode-follow-link-kill)
		   t)
	       (error nil))))
    (setq lnk (and lnk (line-number-at-pos)))
    (delete-region (point-min) (point-max))
    (insert txt)
    (set-mark mrk)
    (goto-char pt)
    lnk))

(ert-deftest rst-toc ()
  "Tests `rst-toc'."
  ;; Set customizable variables to defaults
  (let ((rst-toc-indent 2)
	(indent-tabs-mode nil))
    (should (ert-equal-buffer
	     '(toc)
	     "No section title at all
\^@"
	     "\^@"
	     ))
    (should (ert-equal-buffer-return
	     '(toc)
	     (concat title headers "\n\^@")
	     "Title
  Header A
  Header B
    Subheader B.a
      SubSubheader B.a.1
    Subheader B.b
\^@  Header C
"
	     20))
    (should (ert-equal-buffer-return
	     '(toc)
	     (concat title "Header A
========

Header B
========

Subh\^@eader B.a
-------------

SubSubheader B.a.1
~~~~~~~~~~~~~~~~~~

Subheader B.b
-------------

Header C
========
")
	     "Title
  Header A
  Header B
\^@    Subheader B.a
      SubSubheader B.a.1
    Subheader B.b
  Header C
"
	     11))
    (should (ert-equal-buffer-return
	     '(toc)
	     (concat "\^@\n\n" title headers "\n")
	     "\^@Title
  Header A
  Header B
    Subheader B.a
      SubSubheader B.a.1
    Subheader B.b
  Header C
"
	     4))
    (should (ert-equal-buffer-return
	     '(toc)
	     (concat title "Header A
========

Header B
========

Subheader B.a
-------------

SubSubheader B.a.1
~~~~~~~~~~~~~~~~~~
\^@
Subheader B.b
-------------

Header C
========
")
	     "Title
  Header A
  Header B
    Subheader B.a
\^@      SubSubheader B.a.1
    Subheader B.b
  Header C
"
	     14))
    ))

(defun toc-follow (level)
  (rst-toc-insert level)
  (back-to-indentation)
  (call-interactively #'rst-toc-follow-link))

(ert-deftest rst-toc-follow-link ()
  "Tests `rst-toc-follow-link'."
  (let ((rst-toc-insert-style 'plain))
    (should-error (ert-equal-buffer
		   '(toc-follow 1)
		   ""
		   "")
		  :type 'error)
    (should (ert-equal-buffer
	     '(toc-follow 1)
	     (concat title "  \^@\n\n" headers)
	     (concat title "  Header A
  Header B
  Header C

Header A
========

Header B
========

Subheader B.a
-------------

SubSubheader B.a.1
~~~~~~~~~~~~~~~~~~

Subheader B.b
-------------

\^@Header C
========")))
    ))

(defun toc-mode-return (kill)
  (rst-toc)
  (rst-toc-mode-return kill)
  (let ((buf (get-buffer rst-toc-buffer-name)))
    (when buf
      (kill-buffer buf)
      t)))

(ert-deftest rst-toc-mode-return ()
  "Tests `rst-toc-mode-return'."
  (should-error (ert-equal-buffer
		 '(rst-toc-mode-return)
		 ""
		 t)
		:type 'error)
  (should (ert-equal-buffer-return
	   '(toc-mode-return nil)
	   (concat title "  \^@\n\n" headers)
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(toc-mode-return t)
	   (concat title "  \^@\n\n" headers)
	   t
	   nil))
  )
