;; Tests for class `rst-Hdr'  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert nil)

(ert-deftest rst-Hdr-new-ok ()
  "Test `rst-Hdr-new' with valid values."
  (should (rst-Hdr-p (rst-Hdr-new (rst-Ado-new-simple ?~) 0)))
  (should (rst-Hdr-p (rst-Hdr-new (rst-Ado-new-over-and-under ?~) 0)))
  (should (rst-Hdr-p (rst-Hdr-new (rst-Ado-new-over-and-under ?+) 10)))
  )

(ert-deftest rst-Hdr-new-wrong-type ()
  "Test `rst-Hdr-new' with wrong types."
  (should-error (rst-Hdr-new (rst-Ado-new-simple ?~) nil)
  		:type 'wrong-type-argument)
  (should-error (rst-Hdr-new (rst-Ado-new-simple ?~) "10")
		:type 'wrong-type-argument)
  )

(ert-deftest rst-Hdr-new-invalid ()
  "Test `rst-Hdr-new' with invalid values."
  (should-error (rst-Hdr-new (rst-Ado-new-simple ?=) 10)
		:type 'args-out-of-range)
  (should-error (rst-Hdr-new (rst-Ado-new-over-and-under ?=) -10)
		:type 'args-out-of-range)
  (should-error (rst-Hdr-new (rst-Ado-new-transition) 0)
		:type 'args-out-of-range)
  )

(ert-deftest rst-Hdr-new-lax-ok ()
  "Test `rst-Hdr-new-lax' with valid values."
  (should (rst-Hdr-p (rst-Hdr-new-lax (rst-Ado-new-simple ?~) 0)))
  (should (rst-Hdr-p (rst-Hdr-new-lax (rst-Ado-new-over-and-under ?~) 0)))
  (should (rst-Hdr-p (rst-Hdr-new-lax (rst-Ado-new-over-and-under ?+) 10)))
  (should (rst-Hdr-p (rst-Hdr-new-lax (rst-Ado-new-simple ?=) 10)))
  (should (rst-Hdr-p (rst-Hdr-new-lax (rst-Ado-new-over-and-under ?=) -10)))
  )

(ert-deftest rst-Hdr-new-lax-wrong-type ()
  "Test `rst-Hdr-new-lax' with wrong types."
  (should-error (rst-Hdr-new-lax nil 0)
		:type 'wrong-type-argument)
  (should-error (rst-Hdr-new-lax "=" 0)
		:type 'wrong-type-argument)
  )

(ert-deftest rst-Hdr-new-invert ()
  "Test `rst-Hdr-new-invert'."
  (let* ((dbl-eq (rst-Ado-new-over-and-under ?=))
	 (spl-eq (rst-Ado-new-simple ?=))
	 (dbl-eq-1 (rst-Hdr-new dbl-eq 1))
	 (dbl-eq-0 (rst-Hdr-new dbl-eq 0))
	 (spl-eq-0 (rst-Hdr-new spl-eq 0)))
    (should (equal (rst-Hdr-new-invert dbl-eq 0) spl-eq-0))
    (should (equal (rst-Hdr-new-invert dbl-eq 1) spl-eq-0))
    (should (equal (rst-Hdr-new-invert spl-eq 0) dbl-eq-0))
    (should (equal (rst-Hdr-new-invert spl-eq 1) dbl-eq-1))
    ))

(ert-deftest rst-Hdr-preferred-adornments ()
  "Test `rst-Hdr-preferred-adornments'."
  (let* ((dbl-eq (rst-Ado-new-over-and-under ?=))
	 (spl-dt (rst-Ado-new-simple ?.))
	 (dbl-eq-1 (rst-Hdr-new dbl-eq 1))
	 (dbl-eq-0 (rst-Hdr-new dbl-eq 0))
	 (spl-dt-0 (rst-Hdr-new spl-dt 0))
	 (rst-preferred-adornments '((?= over-and-under 1)
				     (?= over-and-under 0)
				     (?. simple 0))))
    (should (equal (rst-Hdr-preferred-adornments)
		   (list dbl-eq-1 dbl-eq-0 spl-dt-0)))))

(ert-deftest rst-Hdr-member-ado ()
  "Test `rst-Hdr-member-ado'."
  (let ((dbl-eq-1 (rst-Hdr-new (rst-Ado-new-over-and-under ?=) 1))
	(dbl-eq-3 (rst-Hdr-new (rst-Ado-new-over-and-under ?=) 3))
	(dbl-eq-0 (rst-Hdr-new (rst-Ado-new-over-and-under ?=) 0))
	(dbl-pl-0 (rst-Hdr-new (rst-Ado-new-over-and-under ?+) 0))
	(spl-pl-0 (rst-Hdr-new (rst-Ado-new-simple ?+) 0))
	(spl-td-0 (rst-Hdr-new (rst-Ado-new-simple ?~) 0))
	(spl-eq-0 (rst-Hdr-new (rst-Ado-new-simple ?=) 0)))
    (let* ((spk (list spl-pl-0))
	   (spl_spk (cons spl-eq-0 spk))
	   (dbl_spl_spk (cons dbl-eq-0 spl_spk)))
      (should-error (rst-Hdr-member-ado nil nil)
		    :type 'wrong-type-argument)
      (should-error (rst-Hdr-member-ado 3 nil)
		    :type 'wrong-type-argument)

      (should (eq (rst-Hdr-member-ado spl-pl-0 dbl_spl_spk) spk))
      (should (eq (rst-Hdr-member-ado spl-pl-0 spk) spk))
      (should (eq (rst-Hdr-member-ado spl-eq-0 dbl_spl_spk) spl_spk))
      (should (eq (rst-Hdr-member-ado dbl-eq-3 dbl_spl_spk) dbl_spl_spk))

      (should-not (rst-Hdr-member-ado dbl-pl-0 dbl_spl_spk))
      (should-not (rst-Hdr-member-ado spl-td-0 dbl_spl_spk))
    )))

(ert-deftest rst-Hdr-get-char ()
  "Test `rst-Hdr-get-char'."
  (should-error (rst-Hdr-get-char nil)
		:type 'wrong-type-argument)
  (should-error (rst-Hdr-get-char "=")
		:type 'wrong-type-argument)

  (should (equal (rst-Hdr-get-char (rst-Hdr-new (rst-Ado-new-simple ?=) 0))
	  ?=))
  )

(ert-deftest rst-Hdr-is-over-and-under ()
  "Test `rst-Hdr-is-over-and-under'."
  (should-error (rst-Hdr-is-over-and-under nil)
		:type 'wrong-type-argument)
  (should-error (rst-Hdr-is-over-and-under "=")
		:type 'wrong-type-argument)

  (should (rst-Hdr-is-over-and-under
	   (rst-Hdr-new (rst-Ado-new-over-and-under ?=) 0)))
  (should-not (rst-Hdr-is-over-and-under
	       (rst-Hdr-new (rst-Ado-new-simple ?=) 0)))
  )
