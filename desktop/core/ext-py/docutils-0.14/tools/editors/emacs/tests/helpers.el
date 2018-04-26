;; Tests for helper functions and macros.  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert t)

(ert-deftest helpers-asserts ()
  "Check some assertions."
  (should (equal ert-Buf-point-char "\^@"))
  (should (equal ert-Buf-mark-char "\^?"))
  )

(ert-deftest rst-destructuring-dolist ()
  "Test `rst-destructuring-dolist'."
  (should (equal nil (rst-destructuring-dolist (i nil)
		       (signal 'error nil))))
  (should (equal t (rst-destructuring-dolist (i nil t)
		     (signal 'error nil))))
  (should (let (res)
	    (rst-destructuring-dolist (e '(1) res)
	      (setq res (not (boundp '--rst-destructuring-dolist-var--))))))
  (should (equal
	   '((4 . 3) (2 . 1))
	   (let (res)
	     (rst-destructuring-dolist ((l &rest r) '((1 . 2) (3 . 4)) res)
	       (push (cons r l) res)))))
  (should (equal
	   '((6 5 4) (3 2 1))
	   (let (res)
	     (rst-destructuring-dolist ((l m r) '((1 2 3) (4 5 6)) res)
	       (push (list r m l) res)))))
  (should (equal
	   '(3 2 1)
	   (let (res)
	     (rst-destructuring-dolist (e '(1 2 3) res)
	       (push e res)))))
  (should (equal
  	   '(30 20 10)
  	   (let (res)
  	     (rst-destructuring-dolist ((e &aux (a 10)) '((1) (2) (3)) res)
  	       (push (* e a) res)
  	       (setq a (+ a a))))))
  (should (equal
  	   '(30 20 10)
  	   (let (res)
  	     (rst-destructuring-dolist ((&rest e &aux (a 10)) '(1 2 3) res)
  	       (push (* e a) res)
  	       (setq a (+ a a))))))
  )

(ert-deftest rst-forward-line-strict ()
  "Test `rst-forward-line-strict'."
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict 1)
	     "\^@"
	     t
	     nil))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict 0)
	     "\^@"
	     t
	     t))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict -1)
	     "\^@"
	     t
	     nil))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict 1)
	     "abc\^@"
	     t
	     nil))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict 0)
	     "abc\^@"
	     "\^@abc"
	     t))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict -1)
	     "abc\^@"
	     t
	     nil))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict 1)
	     "abc\^@
"
	     "abc
\^@"
	     t))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict 2)
	     "abc\^@
"
	     t
	     nil))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict 0)
	     "abc\^@
"
	     "\^@abc
"
	     t))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict -1)
	     "abc
\^@"
	     "\^@abc
"
	     t))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict -2)
	     "abc
\^@"
	     t
	     nil))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict 1 1)
	     "\^@"
	     t
	     nil))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict 1 2)
	     "\^@"
	     t
	     nil))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict 1 4)
	     "\^@abc"
	     "abc\^@"
	     t))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict 1 4)
	     "abc\^@"
	     t
	     nil))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict 1 3)
	     "\^@abc"
	     "abc\^@"
	     t))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict 1 5)
	     "abc\^@
"
	     "abc
\^@"
	     t))
  (should (ert-equal-buffer-return
	   '(rst-forward-line-strict 2 5)
	     "abc\^@
"
	     t
	     nil))
  )

(defun forward-line-looking-at (n &rest rst-res)
  "Call `rst-forward-line-looking-at'. If match is returned
return t if `(match-beginning 0)' satisfies `(bolp)'
and `(match-end 0)' matches mark."
  (rst-forward-line-looking-at
   n rst-res
   #'(lambda (mtcd)
       (when mtcd
	 (and (bolp)
	      (= (match-end 0) (mark)))))))

(ert-deftest rst-forward-line-looking-at ()
  "Test `rst-forward-line-looking-at'."
  (should (ert-equal-buffer-return
	   '(forward-line-looking-at 0)
	   "\^@\^?"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(forward-line-looking-at 1)
	   "\^@\^?"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(forward-line-looking-at 1)
	   "\^@
\^?"
	   t
	   t))
  (should (ert-equal-buffer-return
	   '(forward-line-looking-at 1)
	   "\^@
  .. \^?"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(forward-line-looking-at 1 'exm-sta)
	   "\^@
  .. \^?
"
	   t
	   nil))
  (should (ert-equal-buffer-return
	   '(forward-line-looking-at 1 'exm-beg)
	   "\^@
  .. \^?
"
	   t
	   t))
  )

(ert-deftest rst-delete-entire-line ()
  "Test `rst-delete-entire-line'."
  (should (ert-equal-buffer
	   '(rst-delete-entire-line 0)
	   "\^@"
	   t))
  (should (ert-equal-buffer
	   '(rst-delete-entire-line 0)
	   " \^@"
	   "\^@"))
  (should (ert-equal-buffer
	   '(rst-delete-entire-line 1)
	   "\^@
abc
"
	   "\^@
"))
  (should (ert-equal-buffer
	   '(rst-delete-entire-line 2)
	   "\^@
abc
"
	   t))
  (should (ert-equal-buffer
	   '(rst-delete-entire-line 3)
	   "\^@
abc
"
	   t))
  (should (ert-equal-buffer
	   '(rst-delete-entire-line 0)
	   "
\^@abc
"
	   "
\^@"))
  (should (ert-equal-buffer
	   '(rst-delete-entire-line -1)
	   "
abc
\^@"
	   "
\^@"))
  )
