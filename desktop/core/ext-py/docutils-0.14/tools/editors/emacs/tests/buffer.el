;;; buffer.el --- Test the test support for buffers  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "ert-buffer" nil t)

;; ****************************************************************************
;; `ert-Buf'

(defun roundtrip-ert-Buf (in)
  (with-temp-buffer
    (ert-Buf--to-buffer (ert-Buf-from-string in))
    (ert-Buf-string (ert-Buf-from-buffer))))

(ert-deftest ert-Buf ()
  "Tests for functions working with `ert-Buf's."
  (should (equal (concat ert-Buf-point-char "abc\n")
		 (roundtrip-ert-Buf (concat ert-Buf-point-char "abc\n"))))
  (should (equal (concat "a" ert-Buf-point-char "bc\n")
		 (roundtrip-ert-Buf (concat "a" ert-Buf-point-char "bc\n"))))
  (should (equal (concat "ab" ert-Buf-point-char "c\n")
		 (roundtrip-ert-Buf (concat "ab" ert-Buf-point-char "c\n"))))
  (should (equal (concat "abc" ert-Buf-point-char "\n")
		 (roundtrip-ert-Buf (concat "abc" ert-Buf-point-char "\n"))))
  (should (equal (concat "abc\n" ert-Buf-point-char)
		 (roundtrip-ert-Buf (concat "abc\n" ert-Buf-point-char))))
  (should (equal (concat ert-Buf-point-char "abc\n" ert-Buf-mark-char "")
		 (roundtrip-ert-Buf
		  (concat ert-Buf-point-char "abc\n" ert-Buf-mark-char ""))))
  (should (equal (concat ert-Buf-mark-char "abc\n" ert-Buf-point-char)
		 (roundtrip-ert-Buf
		  (concat ert-Buf-mark-char "abc\n" ert-Buf-point-char))))
  (should (equal (concat "a" ert-Buf-mark-char ert-Buf-point-char "bc\n")
		 (roundtrip-ert-Buf
		  (concat "a" ert-Buf-point-char "" ert-Buf-mark-char "bc\n"))))
  (should (equal (concat "ab" ert-Buf-mark-char "" ert-Buf-point-char "c\n")
		 (roundtrip-ert-Buf
		  (concat "ab" ert-Buf-mark-char ert-Buf-point-char "c\n"))))
  (should-error (ert-Buf-from-string
		 (concat "ab" ert-Buf-point-char ert-Buf-point-char "c\n")))
  (should-error (ert-Buf-from-string
		 (concat "ab" ert-Buf-mark-char ert-Buf-mark-char "c\n")))
  )

(ert-deftest ert-Buf--from-argument ()
  "Test `ert-Buf--from-argument'."
  (let ((marked-a (ert-Buf-from-string
		   (concat ert-Buf-point-char "a" ert-Buf-mark-char))))
    (should (not (ert-Buf--from-argument nil nil)))
    (should (equal (ert-Buf--from-argument ?a nil)
		   (ert-Buf-from-string "a")))
    (should (equal (ert-Buf--from-argument ert-Buf-point-char nil)
		   (ert-Buf-from-string ert-Buf-point-char)))
    (should (equal (ert-Buf--from-argument '("a" "b") nil)
		   (ert-Buf-from-string "ab")))
    (should (equal (ert-Buf--from-argument `("a" ,ert-Buf-point-char "b") nil)
		   (ert-Buf-from-string (concat "a" ert-Buf-point-char "b"))))
    (should (equal (ert-Buf--from-argument marked-a nil) marked-a))
    (should-error (ert-Buf--from-argument -1 nil))
    (should-error (ert-Buf--from-argument [0] nil))
    (should-error (ert-Buf--from-argument t nil))
    (should-error (ert-Buf--from-argument t t))
    (should (eq (ert-Buf--from-argument t marked-a) marked-a))
  ))

;; ****************************************************************************
;; Advice `ert-completing-read'

(defvar read-fun-args nil
  "Input for for functions reading the minibuffer.
Consists of a list of functions and their argument lists to be
run successively. Prompt is omitted.")

(defun insert-reads ()
  (interactive)
  (while read-fun-args
    (let* ((fun-arg (pop read-fun-args))
	   (result (apply (car fun-arg) "" (cdr fun-arg))))
      (insert (if (integerp result)
		  (int-to-string result)
		result) "\n"))))

(defun test-reads (inputs fun-args result)
  (setq read-fun-args fun-args)
  (ert-equal-buffer '(insert-reads) "" result inputs))

(ert-deftest reads ()
  "Tests for functions using `completing-read's."
  (should (test-reads '(5) '((read-number)) "5\n"))
  (should (test-reads nil nil ""))
  (should-error (test-reads '("") nil "")) ;; Too much input.
  (should-error (test-reads '(5) '((read-number)
				   (read-number)) "")) ;; Too less input.
  (should (test-reads '("") '((completing-read nil)) "\n"))
  (should (test-reads '("" "") '((completing-read nil)
				 (completing-read nil)) "\n\n"))
  (should (test-reads '("a" "b") '((completing-read nil)
				   (completing-read nil)) "a\nb\n"))
  (should (test-reads '("a" "b") '((completing-read ("a" "b"))
				   (completing-read ("a" "b"))) "a\nb\n"))
  (should (test-reads '("a" "b") '((completing-read ("a" "b"))
				   (completing-read ("a"))) "a\nb\n"))
  (should-error (test-reads '("a" "b")
			    '((completing-read ("a" "b"))
			      (completing-read ("a") nil t)) "a\nb\n")) ;; Invalid input.
  (should (test-reads '("a" "")
		      '((completing-read ("a" "b"))
			(completing-read ("a") nil t)) "a\n\n"))
  (should-error (test-reads '("a" "")
			    '((completing-read ("a" "b"))
			      (completing-read ("a") nil 'non-empty)) "a\n\n"))
  (should (test-reads '("x") '((read-string)) "x\n"))
  (should (test-reads '("") '((read-string nil nil "x")) "x\n"))
  (should (test-reads '("y") '((read-string nil nil "x")) "y\n"))
  (should (test-reads '("") '((read-number 5)) "5\n"))
  (should (test-reads '(0) '((read-number 5)) "0\n"))
  )

;; ****************************************************************************
;; Test main functions

(ert-deftest ert-equal-buffer ()
  "Tests for `ert-equal-buffer'."
  (should (ert-equal-buffer '(insert "foo")
			    (concat ert-Buf-point-char ert-Buf-mark-char)
			    (concat ert-Buf-mark-char "foo"
				    ert-Buf-point-char)))
  (should (ert-equal-buffer '(delete-region)
			    (concat ert-Buf-mark-char "foo"
				    ert-Buf-point-char)
			    (concat ert-Buf-point-char ert-Buf-mark-char)
			    t))
  (should (ert-equal-buffer '(delete-region 1 4)
			    "foo"
			    ""))
  (should-error (ert-equal-buffer '(delete-region 0 3)
			    (concat "foo")
			    "") :type 'args-out-of-range)
  (should (ert-equal-buffer '(goto-char 4)
			    "foo"
			    (concat "foo" ert-Buf-point-char)))
  )

(ert-deftest ert-equal-buffer-return ()
  "Tests for `ert-equal-buffer-return'."
  (should (ert-equal-buffer-return '(buffer-substring-no-properties 4 1)
				   "foo"
				   t
				   "foo"))
  (should (ert-equal-buffer-return '(delete-and-extract-region 1 4)
				   "foo"
				   ""
				   "foo"))
  (should (ert-equal-buffer-return '(point)
				   ert-Buf-point-char
				   t
				   1))
  (should (ert-equal-buffer-return '(point)
				   (concat " " ert-Buf-point-char)
				   t
				   2))
  (should (ert-equal-buffer-return '(region-beginning)
				   (concat ert-Buf-point-char " "
					   ert-Buf-mark-char)
				   t
				   1))
  (should (ert-equal-buffer-return '(region-end)
				   (concat ert-Buf-mark-char " "
					   ert-Buf-point-char)
				   t
				   2))
  (should (ert-equal-buffer-return '(following-char)
				   (concat ert-Buf-point-char "A")
				   t
				   ?A))
  (should (ert-equal-buffer-return '(following-char)
				   (concat "A" ert-Buf-point-char)
				   t
				   0))
  )
