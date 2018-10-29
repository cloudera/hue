;; Initialize tests  -*- lexical-binding: t -*-

(defun init-rst-ert (&optional with-buffer)
  "Initialize tests.
Prepare for buffer using tests if WITH-BUFFER."
  (when with-buffer
    (add-to-list 'load-path ".")
    (load "ert-buffer" nil t)
    (if (equal (car load-path) ".")
	(setq load-path (cdr load-path))))

  (add-to-list 'load-path "..")
  (load "rst.el" nil t)
  (if (equal (car load-path) "..")
      (setq load-path (cdr load-path)))

  ;; Emacs 24 should have a patch in `testcover-after` declaring a
  ;; `gv-expander'.
  (if (< emacs-major-version 24)
      ;; Define a setf-method for `testcover-after' so `ert' tests can be run
      ;; without problems.
      (defsetf testcover-after (idx val) (store)
	(list 'progn
	      (list 'testcover-after idx val)
	      ;; FIXME: Though it solves the problem it is not really correct
	      ;;        because `val' is only a temporary variable here.
	      (list 'setf val store)))))

;; Clean up `load-path' if set caller just to load this file.
(if (equal (car load-path) ".")
    (setq load-path (cdr load-path)))
