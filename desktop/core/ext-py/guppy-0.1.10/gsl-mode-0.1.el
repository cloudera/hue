;;; gsl-mode.el --- Major mode for editing GSL.
;;; Based on a copy of python-mode.el.

;; Copyright (C) 2005 Sverker Nilsson
;; Copyright (C) 1992,1993,1994  Tim Peters

;; Author: 2005      Sverker Nilsson
;;         1995-1997 Barry A. Warsaw
;;         1992-1994 Tim Peters

;; Maintainer:    sverker.is@home.se
;; Created:       Jun 20, 2005
;; Version:       0.1
;; Last Modified: Nov 23, 2005
;; Keywords: gsl guppy specification language

;; This software is provided as-is, without express or implied
;; warranty.  Permission to use, copy, modify, distribute or sell this
;; software, without fee, for any purpose and by any individual or
;; organization, is hereby granted, provided that the above copyright
;; notice and this paragraph appear in all copies.
;;
;;; Commentary:

;; This is a major mode for editing GSL, the Guppy Specifcation Language.
;;
;; The following statements, placed in your .emacs file or
;; site-init.el, will cause this file to be autoloaded, and
;; gsl-mode invoked, when visiting .gsl files (assuming this file is
;; in your load-path):
;;
;;	(autoload 'gsl-mode "gsl-mode" "GSL editing mode." t)
;;	(setq auto-mode-alist
;;	      (cons '("\\.gsl$" . gsl-mode) auto-mode-alist))
;;
;;     (Where you have installed eg by copying gsl-mode-0.1 to gsl-mode.)

;;; Code:


;; user definable variables
;; vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

(defvar gsl-mode-hook nil
  "*Hook called by `gsl-mode'.")

;; constants

(defconst gsl-indent-offset 1
  "*Indentation increment. This version of gsl-mode only supports 1.")

(defconst gsl-mode-version "0.1"
  "`gsl-mode' version number.")

(defconst gsl-help-address "sverker.is@home.se"
  "Address accepting submission of bug reports.")

(defun gsl-mode-version ()
  "Echo the current version of `gsl-mode' in the minibuffer."
  (interactive)
  (message "Using `gsl-mode' version %s" gsl-mode-version)
  (gsl-keep-region-active))

(defun gsl-submit-bug-report (enhancement-p)
  "Submit via mail a bug report on `gsl-mode'.
With \\[universal-argument] just submit an enhancement request."
  (interactive
   (list (not (y-or-n-p
	       "Is this a bug report? (hit `n' to send other comments) "))))
  (let ((reporter-prompt-for-summary-p (if enhancement-p
					   "(Very) brief summary: "
					 t)))
    (require 'reporter)
    (reporter-submit-bug-report
     gsl-help-address			;address
     (concat "gsl-mode " gsl-mode-version) ;pkgname
     ;; varlist
     (if enhancement-p nil
       '()
       )
     nil				;pre-hooks
     nil				;post-hooks
     "Dear Sverker,")			;salutation
    (if enhancement-p nil
      (set-mark (point))
      (insert 
"[Please replace this text with a sufficiently large code sample\n\
and an exact recipe so that I can reproduce your problem.  Failure\n\
to do so may mean a greater delay in fixing the bug.]\n\n")
      (exchange-point-and-mark)
      (gsl-keep-region-active))))


(defun gsl-current-indentation ()
  (save-excursion
    (beginning-of-line)
    (while (looking-at "\\.")
      (forward-char 1))
    (current-column)))

(defun gsl-compute-indentation ()
  (save-excursion
    (forward-line -1)
    (beginning-of-line)
    (while (and (not (looking-at "\\."))
		(not (forward-line -1))))
    (gsl-current-indentation)))

(defun gsl-outdent-p ()
  nil
  )

(defun gsl-indent-to (need)
  (save-excursion
    (beginning-of-line)
    (setq change (- need (gsl-current-indentation)))
    (if (> change 0)
	(insert-char ?. change)
      (delete-char (- change)))))

(defun gsl-back-to-indentation ()
  (beginning-of-line)
  (forward-char (gsl-current-indentation)))


(defun gsl-indent-line (&optional arg)
  "Fix the indentation of the current line according to GSL rules.

This function is normally bound to `indent-line-function' so
\\[indent-for-tab-command] will call it."
  (interactive "P")
  (let* ((ci (current-indentation))
	 (move-to-indentation-p (<= (current-column) ci))
	 (need (gsl-compute-indentation)))
    (gsl-indent-to need)
    (if move-to-indentation-p (gsl-back-to-indentation))))


(defun gsl-keep-region-active ()
  ;; do whatever is necessary to keep the region active in XEmacs.
  ;; Ignore byte-compiler warnings you might see.  Also note that
  ;; FSF's Emacs 19 does it differently and doesn't its policy doesn't
  ;; require us to take explicit action.
  (and (boundp 'zmacs-region-stays)
       (setq zmacs-region-stays t)))


(defun gsl-shift-region (start end count)
  (save-excursion
    (goto-char end)   (beginning-of-line) (setq end (point))
    (goto-char start) (beginning-of-line) (setq start (point))
    (if (> count 0)
	(while (< (point) end)
	  (if (looking-at "\\.")
	      (progn
		(insert-char ?. count)
		(setq end (+ end count))))
	  (forward-line 1)
	  )
      (while (< (point) end)
	(if (looking-at "\\.\\.")
	    (progn
	      (delete-char (- count))
	      (setq end (+ end count)))
	  )
	(forward-line 1)
      )
      )
    ))


(defun gsl-shift-region-left (start end &optional count)
  "Shift region of GSL code to the left.
The lines from the line containing the start of the current region up
to (but not including) the line containing the end of the region are
shifted to the left, by `gsl-indent-offset' columns.

If a prefix argument is given, the region is instead shifted by that
many columns.  With no active region, outdent only the current line.
You cannot outdent the region if any line is already at column zero."
  (interactive
   (let ((p (point))
	 (m (mark))
	 (arg current-prefix-arg))
     (if m
	 (list (min p m) (max p m) arg)
       (list p (save-excursion (forward-line 1) (point)) arg))))
  (setq count (prefix-numeric-value
	       (or count gsl-indent-offset)))

  ;; if any line starting with dots has less than count+1 dots,
  ;; don't shift the region
  (save-excursion
    (goto-char start)
    (while (< (point) end)
      (beginning-of-line 1)
      (if (looking-at "\\.")
	  (progn
	    (setq x 0)
	    (while (< x count)
	      (forward-char 1)
	      (if (not (looking-at "\\."))
		  (error "Region is at left edge."))
	      (setq x (+ x 1)))))
      (forward-line 1)))
  (gsl-shift-region start end (- count))
  (gsl-keep-region-active))

(defun gsl-shift-region-right (start end &optional count)
  "Shift region of GSL code to the right.
The lines from the line containing the start of the current region up
to (but not including) the line containing the end of the region are
shifted to the right, by `gsl-indent-offset' columns.

If a prefix argument is given, the region is instead shifted by that
many columns.  With no active region, indent only the current line."
  (interactive
   (let ((p (point))
	 (m (mark))
	 (arg current-prefix-arg))
     (if m
	 (list (min p m) (max p m) arg)
       (list p (save-excursion (forward-line 1) (point)) arg))))
  (gsl-shift-region start end (prefix-numeric-value
			      (or count gsl-indent-offset)))
  (gsl-keep-region-active))



(if nil
    ()
  (setq gsl-mode-map (make-sparse-keymap))
  (define-key gsl-mode-map "\C-c<"    'gsl-shift-region-left)
  (define-key gsl-mode-map "\C-c\C-l" 'gsl-shift-region-left)
  (define-key gsl-mode-map "\C-c>"    'gsl-shift-region-right)
  (define-key gsl-mode-map "\C-c\C-r" 'gsl-shift-region-right)
  (define-key gsl-mode-map "\C-c?"    'gsl-describe-mode)
  (define-key gsl-mode-map "\C-c\C-b" 'gsl-submit-bug-report)
  (define-key gsl-mode-map "\C-c\C-v" 'gsl-mode-version)
  )


;;;###autoload
(defun gsl-mode ()
  "Major mode for editing GSL files.
To submit a problem report, enter `\\[gsl-submit-bug-report]' from a
`gsl-mode' buffer.  Do `\\[gsl-describe-mode]' for detailed documentation.

This mode knows about GSL dotted indentation.
Paragraphs are separated by blank lines only.

COMMANDS
\\{gsl-mode-map}
"
  (interactive)
  ;; set up local variables
  (kill-all-local-variables)
  (make-local-variable 'indent-line-function)
  (setq major-mode             'gsl-mode
	mode-name              "GSL"
	indent-line-function   'gsl-indent-line
	)

  (use-local-map gsl-mode-map)

  ;; run the mode hook
  (run-hooks 'gsl-mode-hook)
  )




;; Documentation functions

;; dump the long form of the mode blurb; does the usual doc escapes,
;; plus lines of the form ^[vc]:name$ to suck variable & command docs
;; out of the right places, along with the keys they're on & current
;; values
(defun gsl-dump-help-string (str)
  (with-output-to-temp-buffer "*Help*"
    (let ((locals (buffer-local-variables))
	  funckind funcname func funcdoc
	  (start 0) mstart end
	  keys )
      (while (string-match "^%\\([vc]\\):\\(.+\\)\n" str start)
	(setq mstart (match-beginning 0)  end (match-end 0)
	      funckind (substring str (match-beginning 1) (match-end 1))
	      funcname (substring str (match-beginning 2) (match-end 2))
	      func (intern funcname))
	(princ (substitute-command-keys (substring str start mstart)))
	(cond
	 ((equal funckind "c")		; command
	  (setq funcdoc (documentation func)
		keys (concat
		      "Key(s): "
		      (mapconcat 'key-description
				 (where-is-internal func py-mode-map)
				 ", "))))
	 ((equal funckind "v")		; variable
	  (setq funcdoc (documentation-property func 'variable-documentation)
		keys (if (assq func locals)
			 (concat
			  "Local/Global values: "
			  (prin1-to-string (symbol-value func))
			  " / "
			  (prin1-to-string (default-value func)))
		       (concat
			"Value: "
			(prin1-to-string (symbol-value func))))))
	 (t				; unexpected
	  (error "Error in py-dump-help-string, tag `%s'" funckind)))
	(princ (format "\n-> %s:\t%s\t%s\n\n"
		       (if (equal funckind "c") "Command" "Variable")
		       funcname keys))
	(princ funcdoc)
	(terpri)
	(setq start end))
      (princ (substitute-command-keys (substring str start))))
    (print-help-return-message)))



(defun gsl-describe-mode ()
  "Dump long form of gsl-mode docs."
  (interactive)
  (gsl-dump-help-string "Major mode for editing GSL files.
Knows about GSL indentation. 

KINDS OF LINES

Each physical line in the file is either a `markup line'
(the line starts with a dot character '.') or a `text line'
(the line starts with some other character). Text lines starting
with a dot may be entered by quoting by a backslash ('\\')).

INDENTATION

Unlike most programming languages, GSL uses indentation, and only
indentation, to specify block structure. Unlike other programming
languages the indentation is not based on blanks but on another
special character; currently this is fixed to be the '.' character.
The indentation that can be supplied automatically by GSL-mode is
just a guess: only you know the block structure you intend, so only
you can supply correct indentation.

Primarily for entering new code:

\t\\[indent-for-tab-command]\t indent line appropriately
\t\\[newline-and-indent]\t insert newline, then indent

The \\[indent-for-tab-command] and \\[newline-and-indent] keys will indent the current line to reproduce
the same indentation as the closest preceding markup line.

Primarily for reindenting existing code:

\t\\[gsl-shift-region-left]\t shift region left
\t\\[gsl-shift-region-right]\t shift region right

The indentation of the markup lines in the region is changed by +/- 1
or the argument given. Text lines in the region will not be changed.

OTHER COMMANDS

Use \\[gsl-mode-version] to see the current version of gsl-mode.

Use \\[gsl-submit-bug-report] to submit a bug report or enhancement proposal.

This text is displayed via the \\[gsl-describe-mode] command.

HOOKS

Entering GSL mode calls with no arguments the value of the variable
`gsl-mode-hook', if that value exists and is not nil; see the `Hooks'
section of the Elisp manual for details.

"))




(provide 'gsl-mode)
;;; gsl-mode.el ends here
