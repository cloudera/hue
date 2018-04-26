;; Tests for class `rst-Ado'  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert nil)

(ert-deftest rst-Ado-new-transition ()
  "Test `rst-Ado-new-transition'."
  (should (rst-Ado-p (rst-Ado-new-transition)))
  )

(ert-deftest rst-Ado-new-simple ()
  "Test `rst-Ado-new-simple'."
  (should-error (rst-Ado-new-simple nil)
		:type 'wrong-type-argument)
  (should-error (rst-Ado-new-simple "=")
		:type 'wrong-type-argument)

  (should-error (rst-Ado-new-simple ?a)
		:type 'wrong-type-argument)

  (should (rst-Ado-p (rst-Ado-new-simple ?=)))
  )

(ert-deftest rst-Ado-new-over-and-under ()
  "Test `rst-Ado-new-over-and-under'."
  (should-error (rst-Ado-new-over-and-under nil)
		:type 'wrong-type-argument)
  (should-error (rst-Ado-new-over-and-under "=")
		:type 'wrong-type-argument)

  (should-error (rst-Ado-new-over-and-under ?a)
		:type 'wrong-type-argument)

  (should (rst-Ado-p (rst-Ado-new-over-and-under ?=)))
  )

(ert-deftest rst-Ado-new-invert ()
  "Test `rst-Ado-new-invert'."
  (let ((dbl-eq (rst-Ado-new-over-and-under ?=))
	(spl-eq (rst-Ado-new-simple ?=))
	(tsn (rst-Ado-new-transition)))
    (should (rst-Ado-equal (rst-Ado-new-invert dbl-eq) spl-eq))
    (should (rst-Ado-equal (rst-Ado-new-invert spl-eq) dbl-eq))
    (should (rst-Ado-equal (rst-Ado-new-invert tsn) tsn))
    ))

(ert-deftest rst-Ado-is-transition ()
  "Test `rst-Ado-is-transition'."
  (should-error (rst-Ado-is-transition nil)
		:type 'wrong-type-argument)
  (should-error (rst-Ado-is-transition 3)
		:type 'wrong-type-argument)

  (should (rst-Ado-is-transition (rst-Ado-new-transition)))

  (should-not (rst-Ado-is-transition (rst-Ado-new-simple ?=)))
  )

(ert-deftest rst-Ado-is-section ()
  "Test `rst-Ado-is-section'."
  (should-error (rst-Ado-is-section nil)
		:type 'wrong-type-argument)
  (should-error (rst-Ado-is-section 3)
		:type 'wrong-type-argument)

  (should (rst-Ado-is-section (rst-Ado-new-simple ?=)))

  (should-not (rst-Ado-is-section (rst-Ado-new-transition)))
  )

(ert-deftest rst-Ado-is-simple ()
  "Test `rst-Ado-is-simple'."
  (should-error (rst-Ado-is-simple nil)
		:type 'wrong-type-argument)
  (should-error (rst-Ado-is-simple 3)
		:type 'wrong-type-argument)

  (should (rst-Ado-is-simple (rst-Ado-new-simple ?=)))

  (should-not (rst-Ado-is-simple (rst-Ado-new-transition)))
  (should-not (rst-Ado-is-simple (rst-Ado-new-over-and-under ?=)))
  )

(ert-deftest rst-Ado-is-over-and-under ()
  "Test `rst-Ado-is-over-and-under'."
  (should-error (rst-Ado-is-over-and-under nil)
		:type 'wrong-type-argument)
  (should-error (rst-Ado-is-over-and-under 3)
		:type 'wrong-type-argument)

  (should (rst-Ado-is-over-and-under (rst-Ado-new-over-and-under ?=)))

  (should-not (rst-Ado-is-over-and-under (rst-Ado-new-transition)))
  (should-not (rst-Ado-is-over-and-under (rst-Ado-new-simple ?=)))
  )

(ert-deftest rst-Ado-equal ()
  "Test `rst-Ado-equal'."
  (let ((dbl-eq (rst-Ado-new-over-and-under ?=))
	(dbl-pl (rst-Ado-new-over-and-under ?+))
	(spl-eq (rst-Ado-new-simple ?=))
	(spl-pl (rst-Ado-new-simple ?+))
	(tsn (rst-Ado-new-transition)))
    (should-error (rst-Ado-equal nil dbl-eq)
		  :type 'wrong-type-argument)
    (should-error (rst-Ado-equal dbl-eq nil)
		  :type 'wrong-type-argument)
    (should-error (rst-Ado-equal dbl-eq 3)
		  :type 'wrong-type-argument)
    (should-error (rst-Ado-equal 'some-sym dbl-eq)
		  :type 'wrong-type-argument)

    (should (rst-Ado-equal dbl-eq dbl-eq))
    (should (rst-Ado-equal spl-eq spl-eq))
    (should (rst-Ado-equal spl-pl spl-pl))

    (should-not (rst-Ado-equal dbl-eq dbl-pl))
    (should-not (rst-Ado-equal dbl-eq spl-eq))
    (should-not (rst-Ado-equal dbl-eq spl-pl))
    (should-not (rst-Ado-equal dbl-eq tsn))
    (should-not (rst-Ado-equal spl-eq spl-pl))
    (should-not (rst-Ado-equal spl-eq tsn))
    ))

(ert-deftest rst-Ado-position ()
  "Test `rst-Ado-position'."
  (let ((dbl-eq (rst-Ado-new-over-and-under ?=))
	(dbl-pl (rst-Ado-new-over-and-under ?+))
	(spl-eq (rst-Ado-new-simple ?=))
	(spl-pl (rst-Ado-new-simple ?+))
	(tsn- (rst-Ado-new-transition)))
    (let* ((tsn (list tsn-))
	   (spl_tsn (cons spl-eq tsn))
	   (dbl_spl_tsn (cons dbl-eq spl_tsn)))
      (should-error (rst-Ado-position nil nil)
		    :type 'wrong-type-argument)
      (should-error (rst-Ado-position 3 nil)
		    :type 'wrong-type-argument)
      (should-error (rst-Ado-position dbl-eq '(3))
		    :type 'wrong-type-argument)

      (should (equal (rst-Ado-position tsn- dbl_spl_tsn) 2))
      (should (equal (rst-Ado-position tsn- tsn) 0))
      (should (equal (rst-Ado-position spl-eq dbl_spl_tsn) 1))
      (should (equal (rst-Ado-position dbl-eq dbl_spl_tsn) 0))

      (should-not (rst-Ado-position dbl-pl dbl_spl_tsn))
      (should-not (rst-Ado-position spl-pl dbl_spl_tsn))
    )))
