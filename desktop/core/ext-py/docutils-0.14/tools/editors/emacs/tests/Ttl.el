;; Tests for class `rst-Ttl'  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert t)

(setq buf-lines
"Simple
======

----------
  Double
----------

 Candidate
\^@
~~~~~~~~~~
   Half

**********
"
      ado-spl (rst-Ado-new-simple ?=)
      txt-spl-beg 1
      txt-spl-end 7
      und-spl-beg 8
      und-spl-end 14
      mtc-spl (list txt-spl-beg und-spl-end
		    nil nil
		    txt-spl-beg txt-spl-end
		    und-spl-beg und-spl-end)
      ind-spl 0
      hdr-spl (rst-Hdr-new ado-spl 0)
      txt-spl "Simple"
      ado-dbl (rst-Ado-new-over-and-under ?-)
      ovr-dbl-beg 16
      ovr-dbl-end 26
      txt-dbl-beg 27
      txt-dbl-end 35
      und-dbl-beg 36
      und-dbl-end 46
      mtc-dbl (list ovr-dbl-beg und-dbl-end
		    ovr-dbl-beg ovr-dbl-end
		    txt-dbl-beg txt-dbl-end
		    und-dbl-beg und-dbl-end)
      ind-dbl 2
      hdr-dbl (rst-Hdr-new ado-dbl 2)
      txt-dbl "Double"
      ado-cnd nil
      txt-cnd-beg 48
      txt-cnd-end 58
      mtc-cnd (list txt-cnd-beg txt-cnd-end
		    nil nil
		    txt-cnd-beg txt-cnd-end
		    nil nil)
      ind-cnd 1
      txt-cnd "Candidate"
      ado-hlf (rst-Ado-new-over-and-under ?~)
      ovr-hlf-beg 60
      ovr-hlf-end 70
      txt-hlf-beg 71
      txt-hlf-end 78
      mtc-hlf (list ovr-hlf-beg txt-hlf-end
		    ovr-hlf-beg ovr-hlf-end
		    txt-hlf-beg txt-hlf-end
		    nil nil)
      mtc-hlf (list ovr-hlf-beg txt-hlf-end
		    ovr-hlf-beg ovr-hlf-end
		    txt-hlf-beg txt-hlf-end
		    nil nil)
      ind-hlf 3
      txt-hlf "Half"
      ado-trn (rst-Ado-new-transition)
      txt-trn-beg 80
      txt-trn-end 90
      mtc-trn (list txt-trn-beg txt-trn-end
		    nil nil
		    txt-trn-beg txt-trn-end
		    nil nil)
      ind-trn nil
      txt-trn nil
      )

(ert-deftest rst-Ttl-asserts ()
  "Check some assertions."
  (should (equal ert-Buf-point-char "\^@"))
  (should (equal ert-Buf-mark-char "\^?"))
  )

(ert-deftest rst-Ttl--new ()
  "Test `rst-Ttl--new'."
  ;; Check type checking of ado argument.
  (should-error (rst-Ttl--new hdr-spl mtc-spl ind-spl txt-spl)
		:type 'wrong-type-argument)

  ;; Check type and value checking of match argument.
  (should-error (rst-Ttl--new ado-spl 1 ind-spl txt-spl)
		:type 'wrong-type-argument)
  (should-error (rst-Ttl--new ado-spl nil ind-spl txt-spl)
		:type 'wrong-type-argument)
  (should-error (rst-Ttl--new ado-spl '(1 2 3) ind-spl txt-spl)
		:type 'wrong-type-argument)
  (should-error (rst-Ttl--new ado-spl '(1 2 "3" 4 5 6 7 8) ind-spl txt-spl)
		:type 'wrong-type-argument)
  (should-error (rst-Ttl--new nil '(1 2 3 4 5 6 7 8) ind-spl txt-spl)
		:type 'args-out-of-range)

  ;; Check value checking of match argument for tranisitions.
  (should-error (rst-Ttl--new ado-trn (list nil nil
					    nil nil
					    txt-spl-beg txt-spl-end
					    und-spl-beg und-spl-end)
			      ind-spl txt-trn)
		:type 'args-out-of-range)
  (should-error (rst-Ttl--new ado-trn (list txt-spl-beg und-spl-end
					    txt-spl-beg txt-spl-end
					    und-spl-beg und-spl-end
					    nil nil)
			      ind-spl txt-trn)
		:type 'args-out-of-range)
  (should-error (rst-Ttl--new ado-trn (list txt-spl-beg und-spl-end
					    nil nil
					    txt-spl-beg txt-spl-end
					    und-spl-beg und-spl-end)
			      ind-spl txt-trn)
		:type 'args-out-of-range)
  (should-error (rst-Ttl--new ado-trn (list txt-spl-beg und-spl-end
					    nil nil
					    nil nil
					    und-spl-beg und-spl-end)
			      ind-spl txt-trn)
		:type 'args-out-of-range)

  ;; Check value checking of match argument for simple section header.
  (should-error (rst-Ttl--new ado-spl (list nil nil
					    nil nil
					    txt-spl-beg txt-spl-end
					    und-spl-beg und-spl-end)
			      ind-spl txt-spl)
		:type 'args-out-of-range)
  (should-error (rst-Ttl--new ado-spl (list txt-spl-beg und-spl-end
					    txt-spl-beg txt-spl-end
					    und-spl-beg und-spl-end
					    und-spl-beg und-spl-end)
			      ind-spl txt-spl)
		:type 'args-out-of-range)
  (should-error (rst-Ttl--new ado-spl (list txt-spl-beg und-spl-end
					    nil nil
					    txt-spl-beg txt-spl-end
					    nil nil)
			      ind-spl txt-spl)
		:type 'args-out-of-range)

  ;; Check value checking of match argument for double section header.
  (should-error (rst-Ttl--new ado-dbl (list nil nil
					    ovr-dbl-beg ovr-dbl-end
					    txt-dbl-beg txt-dbl-end
					    und-dbl-beg und-dbl-end)
			      ind-dbl txt-dbl)
		:type 'args-out-of-range)
  (should-error (rst-Ttl--new ado-dbl (list ovr-dbl-beg und-dbl-end
					    nil nil
					    txt-dbl-beg txt-dbl-end
					    und-dbl-beg und-dbl-end)
			      ind-dbl txt-dbl)
		:type 'args-out-of-range)
  (should-error (rst-Ttl--new ado-dbl (list ovr-dbl-beg und-dbl-end
					    ovr-dbl-beg ovr-dbl-end
					    nil nil
					    und-dbl-beg und-dbl-end)
			      ind-dbl txt-dbl)
		:type 'args-out-of-range)

  ;; Check type and value checking of indent argument.
  (should-error (rst-Ttl--new ado-trn mtc-trn 1 txt-trn)
		:type 'wrong-type-argument)
  (should-error (rst-Ttl--new ado-spl mtc-spl nil txt-spl)
		:type 'wrong-type-argument)
  (should-error (rst-Ttl--new ado-spl mtc-spl -1 txt-spl)
		:type 'wrong-type-argument)

  ;; Check type and value checking of text argument.
  (should-error (rst-Ttl--new ado-trn mtc-trn ind-trn "Text")
		:type 'wrong-type-argument)
  (should-error (rst-Ttl--new ado-spl mtc-spl ind-spl nil)
		:type 'wrong-type-argument)
  (should-error (rst-Ttl--new ado-spl mtc-spl ind-spl 3)
		:type 'wrong-type-argument)
  (should-error (rst-Ttl--new ado-trn mtc-spl ind-spl txt-spl)
		:type 'args-out-of-range)

  (should (rst-Ttl-p (rst-Ttl--new ado-spl mtc-spl ind-spl txt-spl)))
  (should (rst-Ttl-p (rst-Ttl--new ado-dbl mtc-dbl ind-dbl txt-dbl)))
  (should (rst-Ttl-p (rst-Ttl--new ado-cnd mtc-cnd ind-cnd txt-cnd)))
  (should (rst-Ttl-p (rst-Ttl--new ado-hlf mtc-hlf ind-hlf txt-hlf)))
  (should (rst-Ttl-p (rst-Ttl--new ado-trn mtc-trn ind-trn txt-trn)))

  ;; Check setting of header.
  (should (equal (rst-Ttl-hdr (rst-Ttl--new ado-spl mtc-spl ind-spl txt-spl))
		 (rst-Hdr-new ado-spl ind-spl)))
  (should (equal (rst-Ttl-hdr (rst-Ttl--new ado-dbl mtc-dbl ind-dbl txt-dbl))
		 (rst-Hdr-new ado-dbl ind-dbl)))
  (should (equal (rst-Ttl-hdr (rst-Ttl--new ado-hlf mtc-hlf ind-hlf txt-hlf))
		 (rst-Hdr-new ado-hlf ind-hlf)))
  (should-not (rst-Ttl-hdr (rst-Ttl--new ado-cnd mtc-cnd ind-cnd txt-cnd)))
  (should-not (rst-Ttl-hdr (rst-Ttl--new ado-trn mtc-cnd nil txt-trn)))

  )

(ert-deftest rst-Ttl-get-title-beginning ()
  "Test `rst-Ttl-get-title-beginning'."
  (should (equal (rst-Ttl-get-title-beginning
		  (rst-Ttl--new ado-spl mtc-spl ind-spl txt-spl)) txt-spl-beg))
  (should (equal (rst-Ttl-get-title-beginning
		  (rst-Ttl--new ado-dbl mtc-dbl ind-dbl txt-dbl)) txt-dbl-beg))
  (should (equal (rst-Ttl-get-title-beginning
		  (rst-Ttl--new ado-hlf mtc-hlf ind-hlf txt-hlf)) txt-hlf-beg))
  (should (equal (rst-Ttl-get-title-beginning
		  (rst-Ttl--new ado-cnd mtc-cnd ind-cnd txt-cnd)) txt-cnd-beg))
  )

(ert-deftest rst-Ttl-get-beginning_end ()
  "Test `rst-Ttl-get-beginning' and `rst-Ttl-get-end'."
  (should (equal (rst-Ttl-get-beginning
		  (rst-Ttl--new ado-spl mtc-spl ind-spl txt-spl)) txt-spl-beg))
  (should (equal (rst-Ttl-get-end
		  (rst-Ttl--new ado-spl mtc-spl ind-spl txt-spl)) und-spl-end))
  (should (equal (rst-Ttl-get-beginning
		  (rst-Ttl--new ado-dbl mtc-dbl ind-dbl txt-dbl)) ovr-dbl-beg))
  (should (equal (rst-Ttl-get-end
		  (rst-Ttl--new ado-dbl mtc-dbl ind-dbl txt-dbl)) und-dbl-end))
  (should (equal (rst-Ttl-get-beginning
		  (rst-Ttl--new ado-hlf mtc-hlf ind-hlf txt-hlf)) ovr-hlf-beg))
  (should (equal (rst-Ttl-get-end
		  (rst-Ttl--new ado-hlf mtc-hlf ind-hlf txt-hlf)) txt-hlf-end))
  (should (equal (rst-Ttl-get-beginning
		  (rst-Ttl--new ado-cnd mtc-cnd ind-cnd txt-cnd)) txt-cnd-beg))
  (should (equal (rst-Ttl-get-end
		  (rst-Ttl--new ado-cnd mtc-cnd ind-cnd txt-cnd)) txt-cnd-end))
  )

(ert-deftest rst-Ttl-from-buffer ()
  "Test `rst-Ttl-from-buffer'."
  (let ((ttl-spl (rst-Ttl--new ado-spl mtc-spl ind-spl txt-spl))
	(ttl-dbl (rst-Ttl--new ado-dbl mtc-dbl ind-dbl txt-dbl))
	(ttl-cnd (rst-Ttl--new nil mtc-cnd ind-cnd txt-cnd))
	(ttl-hlf (rst-Ttl--new ado-hlf mtc-hlf ind-hlf txt-hlf))
	(ttl-trn (rst-Ttl--new ado-trn mtc-trn ind-trn txt-trn)))

    ;; Check type checking of beg-txt argument.
    (should-error (rst-Ttl-from-buffer nil nil nil nil nil)
		  :type 'wrong-type-argument)

    (should (ert-equal-buffer-return
	     '(rst-Ttl-from-buffer
	       ado-spl nil txt-spl-beg und-spl-beg txt-spl)
	     buf-lines
	     t
	     ttl-spl))
    (should (ert-equal-buffer-return
	     '(rst-Ttl-from-buffer
	       ado-dbl ovr-dbl-beg txt-dbl-beg und-dbl-beg txt-dbl)
	     buf-lines
	     t
	     ttl-dbl))
    (should (ert-equal-buffer-return
	     '(rst-Ttl-from-buffer
	       nil nil txt-cnd-beg nil txt-cnd)
	     buf-lines
	     t
	     ttl-cnd))
    (should (ert-equal-buffer-return
	     '(rst-Ttl-from-buffer
	       ado-hlf ovr-hlf-beg txt-hlf-beg nil txt-hlf)
	     buf-lines
	     t
	     ttl-hlf))
    (should (ert-equal-buffer-return
	     '(rst-Ttl-from-buffer
	       ado-trn nil txt-trn-beg nil txt-trn)
	     buf-lines
	     t
	     ttl-trn))
    ))

(defun ttl-contains (pnt)
  "Run `rst-Ttl-contains' on current buffer comparing first title with point."
  (interactive "d")
  (rst-Ttl-contains (car (rst-all-ttls-compute)) pnt))

(ert-deftest rst-Ttl-contains ()
  "Test `rst-Ttl-contains'."
  (should-error (rst-Ttl-contains nil nil)
		:type 'wrong-type-argument)

  (should (ert-equal-buffer-return
	   '(ttl-contains nil)
	   "
===
\^@One
===
"
	   nil
	   0
	   t))
  (should (ert-equal-buffer-return
	   '(ttl-contains nil)
	   "
\^@===
One
===
"
	   nil
	   0
	   t))
  (should (ert-equal-buffer-return
	   '(ttl-contains nil)
	   "
===
One
===\^@
"
	   nil
	   0
	   t))
  (should (ert-equal-buffer-return
	   '(ttl-contains nil)
	   "
\^@One
===
"
	   nil
	   0
	   t))
  (should (ert-equal-buffer-return
	   '(ttl-contains nil)
	   "
One
===\^@
"
	   nil
	   0
	   t))
  (should (ert-equal-buffer-return
	   '(ttl-contains nil)
	   "\^@
One
===
"
	   nil
	   1
	   t))
  (should (ert-equal-buffer-return
	   '(ttl-contains nil)
	   "
One
===
\^@"
	   nil
	   -1
	   t))
  )
