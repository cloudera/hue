;;; ert-buffer.el --- Support functions for running ert tests on buffers  -*- lexical-binding: t -*-

;; Copyright (C) 2010-2012  Free Software Foundation, Inc.

;; Author: Stefan Merten <smerten@oekonux.de>,

;; This file is part of GNU Emacs.

;; GNU Emacs is free software: you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; GNU Emacs is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with GNU Emacs.  If not, see <http://www.gnu.org/licenses/>.

;;; Commentary:
;; 
;; Some functions need a buffer to run on.  They may use the buffer content as
;; well as point and mark as input and may modify all of them.  In addition
;; they may return some result.  Here are some support functions to test such
;; functions using `ert'.
;;
;; Use `ert-equal-buffer' and/or `ert-equal-buffer-return' for your `should'
;; forms.
;;
;; You may use the constants `ert-Buf-point-char' and `ert-Buf-mark-char' in
;; constructing comparison strings to represent point or mark, respectively.
;;
;; Examples:
;;
;;   (should (ert-equal-buffer '(insert "foo")
;;                             ; Insertion of "foo"...
;;   			       (concat ert-Buf-point-char ert-Buf-mark-char)
;;                             ; ...into an empty buffer with point and mark...
;;   			       (concat ert-Buf-mark-char "foo"
;;   				       ert-Buf-point-char)))
;;                             ; ...should result in a buffer containing "foo"
;;                             ; with point and mark moved appropriately.
;;
;;   (should (ert-equal-buffer '(delete-region)
;;                             ; Deleting region...
;;                             `(,ert-Buf-mark-char "foo" ,ert-Buf-point-char)
;;                             ; ...in a region spanning the whole buffer...
;;                             (concat ert-Buf-point-char ert-Buf-mark-char)
;;                             ; ...should result in an empty buffer...
;;                             t))
;;                             ; ...when called interactively.
;;
;;   (should (ert-equal-buffer-return '(point)
;;                                    ; Returning the point...
;;                                    ert-Buf-point-char
;;                                    ; ...in an empty buffer...
;;                                    t
;;                                    ; ...without changing the result buffer...
;;                                    1))
;;                                    ; ...should return 1.

;;; Code:

(eval-when-compile
  (require 'cl))
(require 'ert)

;; ****************************************************************************
;; `ert-Buf' and related functions

(defconst ert-Buf-point-char "\^@"
  "Special character used to mark the position of point in a `ert-Buf'.")

(defconst ert-Buf-mark-char "\^?"
  "Special character used to mark the position of mark in a `ert-Buf'.")

(defstruct (ert-Buf
	    (:constructor nil) ; No default constructor.
	    (:constructor ert-Buf-from-string
			  (string
			   &aux
			   (analysis (ert-Buf--parse-string string))
			   (content (car analysis))
			   (point (cadr analysis))
			   (mark (caddr analysis))))
	    (:constructor ert-Buf-from-buffer
			  (&aux
			   (content (buffer-substring-no-properties
				     (point-min) (point-max)))
			   (point (point))
			   (mark (mark t))
			   (string
			    (ert-Buf--create-string content point mark)))))
  "Structure to hold comparable information about a buffer.
`ert-Buf-from-string' constructs a structure from a given STRING.
`ert-Buf-from-buffer' constructs a structure from the current
buffer."
  (content nil :read-only t) ; Pure string content without any special markup.
  (point nil :read-only t) ; Position of point.
  (mark nil :read-only t) ; Position of mark.
  (string nil :read-only t) ; String representation.
  )

(defun ert-Buf--parse-string (string)
  "Parse STRING and return clean results.
Return a list consisting of the cleaned content, the position of
point if `ert-Buf-point-char' was found and the the position of mark
if `ert-Buf-mark-char' was found."
  (with-temp-buffer
    (let ((case-fold-search nil)
	  fnd point-fnd mark-fnd)
      (insert string)
      (goto-char (point-min))
      (while (re-search-forward
	      (concat "[" ert-Buf-point-char ert-Buf-mark-char "]") nil t)
	(setq fnd (match-string 0))
	(replace-match "")
	(cond
	 ((equal fnd ert-Buf-point-char)
	  (if point-fnd
	      (error "Duplicate point"))
	  (setq point-fnd (point)))
	 ((equal fnd ert-Buf-mark-char)
	  (if mark-fnd
	      (error "Duplicate mark"))
	  (setq mark-fnd (point)))
	 (t
	  (error "Unexpected marker found"))))
      (list (buffer-substring-no-properties (point-min) (point-max))
	    point-fnd mark-fnd))))

(defun ert-Buf--create-string (content point mark)
  "Create a string representation from CONTENT, POINT and MARK."
  (with-temp-buffer
    (insert content)
    (let (pnt-chs)
      (if point
	  (setq pnt-chs (nconc pnt-chs (list (cons point ert-Buf-point-char)))))
      (if mark
	  (setq pnt-chs (nconc pnt-chs (list (cons mark ert-Buf-mark-char)))))
      ;; Sort pairs so the highest position is last.
      (setq pnt-chs (sort pnt-chs (lambda (el1 el2) (> (car el1) (car el2)))))
      (while pnt-chs
	(goto-char (caar pnt-chs))
	(insert (cdar pnt-chs))
	(setq pnt-chs (cdr pnt-chs)))
      (buffer-substring-no-properties (point-min) (point-max)))))

(defun ert-Buf--to-buffer (buf)
  "Set current buffer according to BUF."
  (insert (ert-Buf-content buf))
  (if (ert-Buf-point buf)
      (goto-char (ert-Buf-point buf)))
  (if (ert-Buf-mark buf)
      (set-mark (ert-Buf-mark buf))))

(defun ert-Buf--from-argument (arg other)
  "Interpret ARG as input for an `ert-Buf', convert it and return the `ert-Buf'.
ARG may be one of the types described in
`ert-equal-buffer-return' or nil which is also returned."
  (cond
   ((not arg)
    nil)
   ((eq arg t)
    (when (or (not other) (eq other t))
      (error "First argument to `ert-Buf--from-argument' t requires a non-nil, non-t second argument"))
    (ert-Buf--from-argument other nil))
   ((characterp arg)
    (ert-Buf-from-string (char-to-string arg)))
   ((stringp arg)
    (ert-Buf-from-string arg))
   ((ert-Buf-p arg)
    arg)
   ((listp arg)
    (ert-Buf-from-string (apply 'concat arg)))
   (t
    (error "Unknown type for `ert-Buf--from-argument'"))))

;; ****************************************************************************
;; Runners

(defvar ert--inputs nil
  "Variable to hold the strings to give successively to `ert-completing-read'.")

(defadvice completing-read (around ert-completing-read first
				   (prompt collection &optional predicate
					   require-match initial-input hist
					   def inherit-input-method))
  "Advice `completing-read' to accept input from `ert--inputs'."
  (if (not ert--inputs)
      (error "No more input strings in `ert--inputs'"))
  (let* ((input (pop ert--inputs)))
    (setq ad-return-value
	  (cond
	   ((eq (try-completion input collection predicate) t) ;; Perfect match.
	    input)
	   ((not require-match) ;; Non-matching input allowed.
	    input)
	   ((and (equal input "")
		 (eq require-match t)) ;; Empty input and this is allowed.
	    input)
	   (t
	    (error
	     "Input '%s' is not allowed for `completing-read' expecting %s"
	     input collection))))))

(defadvice read-string (around ert-read-string first
			       (prompt &optional initial-input history
				       default-value inherit-input-method))
  "Advice `read-string' to accept input from `ert--inputs'."
  (if (not ert--inputs)
      (error "No more input strings in `ert--inputs'"))
  (let* ((input (pop ert--inputs)))
    (setq ad-return-value
	  (if (and (equal input "") default-value)
	      default-value
	    input))))

(defadvice read-number (around ert-read-number first
			       (prompt &optional default))
  "Advice `read-number' to accept input from `ert--inputs'."
  (if (not ert--inputs)
      (error "No more input strings in `ert--inputs'"))
  (let* ((input (pop ert--inputs)))
    (setq ad-return-value
	  (if (and (equal input "") default)
	      default
	    input))))

(defun ert--run-test-with-buffer (buf form interactive)
  "With a buffer filled with `ert-Buf' BUF evaluate function form FORM.
Return a cons consisting of the return value and a `ert-Buf'.  If
INTERACTIVE is non-nil FORM is evaluated in an interactive
environment."
  (with-temp-buffer
    (ert-Buf--to-buffer buf)
    (let ((act-return
	   (cond
	    ((not interactive)
	     (eval form))
	    ((eq interactive t)
	     (let ((current-prefix-arg (cadr form)))
	       (call-interactively (car form))))
	    ((listp interactive)
	     (setq ert--inputs interactive)
	     (ad-activate 'read-string)
	     (ad-activate 'read-number)
	     (ad-activate 'completing-read)
	     (unwind-protect
		 (let ((current-prefix-arg (cadr form)))
		   (call-interactively (car form)))
	       (progn
		 (ad-deactivate 'completing-read)
		 (ad-deactivate 'read-number)
		 (ad-deactivate 'read-string)))
	     (if ert--inputs
		 (error "%d input strings left over"
			(length ert--inputs))))))
	  (act-buf (ert-Buf-from-buffer)))
      (cons act-return act-buf))))

(defun ert--compare-test-with-buffer (result buf ignore-return exp-return)
  "Compare RESULT of test with expected buffer BUF.
RESULT is a return value from `ert--run-test-with-buffer'.
Return a list of booleans where t stands for a successful test of
this kind:

* Content of output buffer
* Point in output buffer
* Return value

IGNORE-RETURN, EXP-RETURN are described in `ert--equal-buffer'."
  (let ((act-return (car result))
	(act-buf (cdr result)))
    (list
     (or (not buf)
	 (equal (ert-Buf-content act-buf) (ert-Buf-content buf)))
     (or
      (not buf)
      (not (ert-Buf-point buf))
      (equal (ert-Buf-point act-buf) (ert-Buf-point buf)))
     (or ignore-return
	 (equal act-return exp-return)))))

(defun ert--equal-buffer (form input exp-output ignore-return exp-return interactive)
  "Run tests for `ert-equal-buffer-return' and `ert-equal-buffer'.
FORM, INPUT and EXP-OUTPUT are as described for
`ert-equal-buffer-return'.  Ignore return value if IGNORE-RETURN
or compare the return value to EXP-RETURN.  INTERACTIVE is as
described for `ert-equal-buffer-return'.  Return t if equal."
  (catch 'return
    (dolist (elem (ert--compare-test-with-buffer
		   (ert--run-test-with-buffer
		    (ert-Buf--from-argument input exp-output) form interactive)
		   (ert-Buf--from-argument exp-output input)
		   ignore-return exp-return) t)
      (unless elem
	(throw 'return nil)))))

(defun ert-equal-buffer-return (form input exp-output exp-return &optional interactive)
  "Evaluate function form FORM with a buffer and compare results.
The buffer is filled with INPUT.  Compare the buffer content to
EXP-OUTPUT if this is non-nil.  Compare the return value to
EXP-RETURN.  Return t if buffer and return value are equal to the
expected values.

INPUT and EXP-OUTPUT represent the input buffer or the expected
output buffer, respectively. They can be one of the following:

* nil in which case the respective buffer is not used. Makes
  sense only for EXP-OUTPUT.
* t in which case the other buffer is used unchanged. The other
  buffer must not be nil or t in this case.
* A character which is converted to a one character string.
* A string.
* A list of strings which are concatenated using `concat'. This
  can be used to shorten the form describing the buffer when used
  with quote or backquote.
* An `ert-Buf' object.

All input variants which end up in a string are parsed by
`ert-Buf-from-string'.

If INTERACTIVE is nil FORM is evaluated with no special context.
If INTERACTIVE is non-nil FORM is evaluated interactively and
`current-prefix-arg' is set to the cadr of FORM (i.e\. the first
argument in FORM) and thus must comply to the format of
`current-prefix-arg'.  If INTERACTIVE is t `call-interactively'
is used normally.  If INTERACTIVE is a list of strings the
elements of the list are given to (advised forms of) functions
reading from the minibuffer as user input strings.  This allows
simulating interactive user input.

FORM usually needs to be quoted.

Return t if buffer and return value equal the expected values."
  (ert--equal-buffer form input exp-output nil exp-return interactive))

(defun ert-equal-buffer (form input exp-output &optional interactive)
  "Like `ert-equal-buffer-return' but the return value of FORM is ignored.
INPUT, EXP-OUTPUT and INTERACTIVE are described in
`ert-equal-buffer-return'."
  (ert--equal-buffer form input exp-output t nil interactive))

;; ****************************************************************************
;; Explainers

(defun ert--equal-buffer-explain (form input exp-output ignore-return exp-return interactive)
  "Explain why `ert--equal-buffer' failed with these parameters.
Return the explanation.  FORM, INPUT, EXP-OUTPUT,
IGNORE-RETURN, EXP-RETURN, INTERACTIVE are described in
`ert--equal-buffer'."
  (let ((test-result (ert--run-test-with-buffer
		      (ert-Buf--from-argument input exp-output)
		      form interactive))
	(exp-buf (ert-Buf--from-argument exp-output input)))
    (destructuring-bind (ok-string ok-point ok-return)
	(ert--compare-test-with-buffer
	 test-result
	 (ert-Buf--from-argument exp-output input) ignore-return exp-return)
      (let (result)
	(if (not ok-return)
	    (push (list 'different-return-values
			(ert--explain-not-equal (car test-result) exp-return))
		  result))
	(if (not ok-point)
	    (push (list 'different-points
			(ert-Buf-string (cdr test-result))
			(ert-Buf-string exp-buf))
		  result))
	(if (not ok-string)
	    (push (list 'different-buffer-contents
			(ert--explain-not-equal
			 (ert-Buf-content (cdr test-result))
			 (ert-Buf-content exp-buf)))
		  result))
	result))))

(defun ert-equal-buffer-return-explain (form input exp-output exp-return &optional interactive)
  "Explain why `ert-equal-buffer-return' failed with these parameters.
Return the explanation.  FORM, INPUT, EXP-OUTPUT, EXP-RETURN,
INTERACTIVE are described in `ert--equal-buffer'."
  (ert--equal-buffer-explain
   form input exp-output nil exp-return interactive))

(put 'ert-equal-buffer-return 'ert-explainer 'ert-equal-buffer-return-explain)

(defun ert-equal-buffer-explain (form input exp-output &optional interactive)
  "Explain why `ert-equal-buffer' failed with these parameters.
Return the explanation.  FORM, INPUT, EXP-OUTPUT, EXP-RETURN,
INTERACTIVE are described in `ert--equal-buffer'."
  (ert--equal-buffer-explain
   form input exp-output t nil interactive))

(put 'ert-equal-buffer 'ert-explainer 'ert-equal-buffer-explain)

; LocalWords:  foo minibuffer

;; Local Variables:
;;   sentence-end-double-space: t
;; End:

(provide 'ert-buffer)

;;; ert-buffer.el ends here
