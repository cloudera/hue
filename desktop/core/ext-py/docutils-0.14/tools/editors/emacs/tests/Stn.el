;; Tests for class `rst-Stn'  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert nil)

(ert-deftest rst-Stn-new ()
  "Test `rst-Stn-new'."
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
	 ;; Header C
	 ;; ========
	 ;;
	 ;; Missing node C.a.1
	 ;; ~~~~~~~~~~~~~~~~~~
	 ;; "
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

    (should-error (rst-Stn-new "" 0 nil)
		  :type 'wrong-type-argument)
    (should-error (rst-Stn-new nil "0" nil)
		  :type 'wrong-type-argument)
    (should-error (rst-Stn-new nil 0 "")
		  :type 'wrong-type-argument)
    (should-error (rst-Stn-new nil 0 '(1))
		:type 'wrong-type-argument)

    (should-error (rst-Stn-new nil 0 nil)
		:type 'args-out-of-range)

    (should-error (rst-Stn-new ttl-T -1 nil)
		  :type 'args-out-of-range)

    (should (rst-Stn-p
	     (rst-Stn-new ttl-T 0 nil)))
    (should (rst-Stn-p
	     (rst-Stn-new
	      ttl-T 0
	      (list (rst-Stn-new ttl-A 1 nil)))))
    (should (rst-Stn-p
	     (rst-Stn-new
	      ttl-T 0
	      (list (rst-Stn-new ttl-A 1 nil)
		    (rst-Stn-new ttl-B 1 nil)
		    (rst-Stn-new ttl-C 1 nil)))))
    (should (rst-Stn-p
	     (rst-Stn-new
	      ttl-T 0
	      (list (rst-Stn-new ttl-A 1 nil)
		    (rst-Stn-new
		     ttl-B 1
		     (list (rst-Stn-new
			    ttl-Ba 2
			    (list (rst-Stn-new ttl-Ba1 3 nil)))))
		    (rst-Stn-new
		     ttl-C 1
		     (list (rst-Stn-new
			    ttl-Ca 2
			    (list (rst-Stn-new ttl-Ca1 3 nil)))))))))
  ))

(ert-deftest rst-Stn-get-title-beginning ()
  "Test `rst-Stn-get-title-beginning'."
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
	 ;; Header C
	 ;; ========
	 ;;
	 ;; Missing node C.a.1
	 ;; ~~~~~~~~~~~~~~~~~~
	 ;; "
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
      (should-error (rst-Stn-get-title-beginning "")
		    :type 'wrong-type-argument)

      (should (equal (rst-Stn-get-title-beginning stn-T) 7))
      (should (equal (rst-Stn-get-title-beginning stn-B) 39))
      (should (equal (rst-Stn-get-title-beginning stn-A) 20))
      (should (equal (rst-Stn-get-title-beginning stn-C) 126))
      (should (equal (rst-Stn-get-title-beginning stn-Ca) 145))
      )))

(ert-deftest rst-Stn-get-text ()
  "Test `rst-Stn-get-text'."
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
	 ;; Header C
	 ;; ========
	 ;;
	 ;; Missing node C.a.1
	 ;; ~~~~~~~~~~~~~~~~~~
	 ;; "
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
      (should-error (rst-Stn-get-text "")
		    :type 'wrong-type-argument)

      (should (equal (rst-Stn-get-text stn-T) "Title"))
      (should (equal (rst-Stn-get-text stn-B "Default") "Header B"))
      (should (equal (rst-Stn-get-text stn-Ca "Default") "Default"))
      (should (rst-Stn-get-text stn-Ca))
      )))

(ert-deftest rst-Stn-is-top ()
  "Test `rst-Stn-is-top'."
  (let* (;; "
	 ;; =====
	 ;; Title
	 ;; =====
	 ;; "
	 (ado-T (rst-Ado-new-over-and-under ?=))
	 (ttl-T (rst-Ttl--new ado-T '(1 18 1 6 7 12 13 18) 0
			      "Title")))
    (let ((stn-T (rst-Stn-new ttl-T 0 nil)))
      (should-error (rst-Stn-is-top nil)
		    :type 'wrong-type-argument)
      (should (rst-Stn-is-top (rst-Stn-new
			       nil -1
			       (list stn-T))))
      (should-not (rst-Stn-is-top stn-T))
      )))
