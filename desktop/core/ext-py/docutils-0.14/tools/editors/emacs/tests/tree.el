;; Tests for `rst-all-stn' and relatives  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert t)

(ert-deftest toc-asserts ()
  "Check some assertions."
  (should (equal ert-Buf-point-char "\^@"))
  (should (equal ert-Buf-mark-char "\^?"))
  )

(ert-deftest rst-all-stn ()
  "Tests `rst-all-stn'."
  (let* ((title "=====
Title
=====

")
	 (headers "Header A
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
")
	 (ado-T (rst-Ado-new-over-and-under ?=))
	 (ttl-T (rst-Ttl--new ado-T '(1 18 1 6 7 12 13 18) 0
			      "Title"))
	 (ado-A (rst-Ado-new-simple ?=))
	 (ttl-A (rst-Ttl--new ado-A '(20 37 nil nil 20 28 29 37) 0
			      "Header A"))
	 (ttl-B (rst-Ttl--new ado-A '(39 56 nil nil 39 47 48 56) 0
			      "Header B"))
	 (ado-Ba (rst-Ado-new-simple ?-))
	 (ttl-Ba (rst-Ttl--new ado-Ba '(58 85 nil nil 58 71 72 85) 0
			       "Subheader B.a"))
	 (ado-Ba1 (rst-Ado-new-simple ?~))
	 (ttl-Ba1 (rst-Ttl--new ado-Ba1 '(87 124 nil nil 87 105 106 124) 0
				"SubSubheader B.a.1"))
	 (ttl-C (rst-Ttl--new ado-A '(126 143 nil nil 126 134 135 143) 0
			      "Header C"))
	 (ttl-Ca nil)
	 (ttl-Ca1 (rst-Ttl--new ado-Ba1 '(145 182 nil nil 145 163 164 182) 0
				"Missing node C.a.1")))
    (let* ((stn-Ca (rst-Stn-new
		    ttl-Ca 2
		    (list (rst-Stn-new ttl-Ca1 3 nil))))
	   (stn-C (rst-Stn-new
		   ttl-C 1
		   (list stn-Ca)))
	   (stn-A (rst-Stn-new ttl-A 1 nil))
	   (stn-B (rst-Stn-new
		   ttl-B 1
		   (list (rst-Stn-new
			  ttl-Ba 2
			  (list (rst-Stn-new ttl-Ba1 3 nil))))))
	   (stn-T (rst-Stn-new
		   ttl-T 0
		   (list stn-A
			 stn-B
			 stn-C))))
      (should (ert-equal-buffer-return
	       '(rst-all-stn)
	       ""
	       t
	       nil
	       ))
      (should (ert-equal-buffer-return
	       '(rst-all-stn)
	       title
	       t
	       (rst-Stn-new
		nil -1
		(list (rst-Stn-new ttl-T 0 nil)))
	       ))
      (should (ert-equal-buffer-return
	       '(rst-all-stn)
	       (concat title headers)
	       t
	       (rst-Stn-new
		nil -1
		(list stn-T))
	       ))
      )))

(ert-deftest rst-stn-containing-point ()
  "Tests `rst-stn-containing-point'."
  (let* (;; "
	 ;; =====
	 ;; Title
	 ;; =====
	 ;; 
	 ;; Header A
	 ;; ========
	 ;; 
	 ;; Header B
	 ;; ========
	 ;; 
	 ;; Subheader B.a
	 ;; -------------
	 ;; 
	 ;; SubSubheader B.a.1
	 ;; ~~~~~~~~~~~~~~~~~~
	 ;; 
	 ;; Subheader B.b
	 ;; -------------
	 ;; 
	 ;; Header C
	 ;; ========
	 ;; 
	 ;; Missing node C.a.1
	 ;; ~~~~~~~~~~~~~~~~~~
	 ;; "
	 (title "=====
Title
=====

")
	 (ado-T (rst-Ado-new-over-and-under ?=))
	 (ttl-T (rst-Ttl--new ado-T '(1 18 1 6 7 12 13 18) 0
			      "Title"))
	 (ado-A (rst-Ado-new-simple ?=))
	 (ttl-A (rst-Ttl--new ado-A '(20 37 nil nil 20 28 29 37) 0
			      "Header A"))
	 (ttl-B (rst-Ttl--new ado-A '(39 56 nil nil 39 47 48 56) 0
			      "Header B"))
	 (ado-Ba (rst-Ado-new-simple ?-))
	 (ttl-Ba (rst-Ttl--new ado-Ba '(58 85 nil nil 58 71 72 85) 0
			       "Subheader B.a"))
	 (ado-Ba1 (rst-Ado-new-simple ?~))
	 (ttl-Ba1 (rst-Ttl--new ado-Ba1 '(87 124 nil nil 87 105 106 124) 0
				"SubSubheader B.a.1"))
	 (ttl-Bb (rst-Ttl--new ado-Ba '(126 153 nil nil 126 139 140 153) 0
			       "Subheader B.b"))
	 (ttl-C (rst-Ttl--new ado-A '(155 172 nil nil 155 163 164 172) 0
			      "Header C"))
	 (ttl-Ca nil)
	 (ttl-Ca1 (rst-Ttl--new ado-Ba1 '(164 211 nil nil 164 192 193 211) 0
				"Missing node C.a.1")))
    (let* ((stn-Ca (rst-Stn-new
		    ttl-Ca 2
		    (list (rst-Stn-new ttl-Ca1 3 nil))))
	   (stn-C (rst-Stn-new
		   ttl-C 1
		   (list stn-Ca)))
	   (stn-A (rst-Stn-new ttl-A 1 nil))
	   (stn-Ba (rst-Stn-new
		    ttl-Ba 2
		    (list (rst-Stn-new ttl-Ba1 3 nil))))
	   (stn-Bb (rst-Stn-new ttl-Bb 2 nil))
	   (stn-B (rst-Stn-new
		   ttl-B 1
		   (list stn-Ba
			 stn-Bb)))
	   (stn-T (rst-Stn-new
		   ttl-T 0
		   (list stn-A
			 stn-B
			 stn-C))))
      (should (ert-equal-buffer-return
	       '(rst-stn-containing-point (rst-all-stn))
	       "\^@"
	       t
	       nil
	       ))
      (should (ert-equal-buffer-return
	       '(rst-stn-containing-point (rst-all-stn))
	       (concat "\^@" title)
	       t
	       nil
	       ))
      (should (ert-equal-buffer-return
	       '(rst-stn-containing-point (rst-all-stn))
	       (concat title "\^@")
	       t
	       (rst-Stn-new ttl-T 0 nil)
	       ))
      (should (ert-equal-buffer-return
	       '(rst-stn-containing-point (rst-all-stn))
	       (concat title "\^@Header A
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
	       t
	       stn-A
	       ))
      (should (ert-equal-buffer-return
	       '(rst-stn-containing-point (rst-all-stn))
	       (concat title "Header A
========

Header B
========
\^@
Subheader B.a
-------------

SubSubheader B.a.1
~~~~~~~~~~~~~~~~~~

Subheader B.b
-------------

Header C
========")
	       t
	       stn-B
	       ))
      (should (ert-equal-buffer-return
	       '(rst-stn-containing-point (rst-all-stn))
	       (concat title "Header A
========

Header B
========

Subheader B.a\^@
-------------

SubSubheader B.a.1
~~~~~~~~~~~~~~~~~~

Subheader B.b
-------------

Header C
========")
	       t
	       stn-Ba
	       ))
      (should (ert-equal-buffer-return
	       '(rst-stn-containing-point (rst-all-stn))
	       (concat title "Header A
========

Header B
========

Subheader B.a
-------------

SubSubheader B.a.1
~~~~~~~~~~~~~~~~~~

S\^@ubheader B.b
-------------

Header C
========")
	       t
	       stn-Bb
	       ))
    )))
