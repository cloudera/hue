;; Tests for operations on list items  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert t)

(ert-deftest items-asserts ()
  "Check some assertions."
  (should (equal ert-Buf-point-char "\^@"))
  (should (equal ert-Buf-mark-char "\^?"))
  )

(defun find-begs (beg-re)
  (rst-find-begs (region-beginning) (region-end) beg-re))

(ert-deftest rst-find-begs ()
  "Tests `rst-find-begs'."
  (should (ert-equal-buffer-return
	   '(find-begs 'itmany-beg-1)
	   "\^@1 Normal paragraph.

* 22 A bullet

* 37 Another bullet

58 Another normal paragraph.

\^?"
	   t '((22 . 0)
	       (37 . 0))))
  (should (ert-equal-buffer-return
	   '(find-begs 'itmany-beg-1)
	   "1 Normal paragraph.

\^?* 22 A bullet

* 37 Another bullet

\^@58 Another normal paragraph.

"
	   t '((22 . 0)
	       (37 . 0))))
  (should (ert-equal-buffer-return
	   '(find-begs 'itmany-beg-1)
	   "1 Normal paragraph.

\^?* 22 A bullet

* 37 Another bullet

1. 58 An enum.

2. 74 Another enum.

\^@95 Another normal paragraph.

"
	   t '((22 . 0)
	       (37 . 0)
	       (58 . 0)
	       (74 . 0))))
  (should (ert-equal-buffer-return
	   '(find-begs 'bul-beg)
	     "\^@
- 2 one
+ 10 two
* 19 three
\^?"
	     t '((2 . 0)
		 (10 . 0)
		 (19 . 0))))
  (should (ert-equal-buffer-return
	   '(find-begs 'bul-beg)
	     "
- 2 one\^@
+ 10 two
* 19 three
\^?"
	     t '((2 . 0)
		 (10 . 0)
		 (19 . 0))))
  (should (ert-equal-buffer-return
	   '(find-begs 'bul-beg)
	     "+ 1 zero
\^@- 10 one
+ 19 two
* 28 three\^?
"
	     t '((10 . 0)
		 (19 . 0)
		 (28 . 0))))
  (should (ert-equal-buffer-return
	   '(find-begs 'bul-beg)
	   "\^@
- 2 one

  + 11 two

* 23 three
\^?"
	   t '((2 . 0)
	       (13 . 2)
	       (23 . 0))))
  (should (ert-equal-buffer-return
	   '(find-begs 'bul-beg)
	   "\^@Normal paragraph

* 19 bullet

  * 32 three

Another normal paragraph
\^?"
	   t '((19 . 0)
	       (34 . 2))))
    )

(ert-deftest rst-find-begs-BUGS ()
  "Exposes bugs in `rst-find-begs'."
  :expected-result :failed ;; These are bugs
  (should (ert-equal-buffer-return
	   '(find-begs 'bul-beg)
	   "\^@Normal paragraph
* 18 bullet
  * 30 three
Another normal paragraph
\^?"
	   t '((18 . 0)
	       (32 . 2))))
  (should (ert-equal-buffer-return
	   '(find-begs 'bul-beg)
	     "\^@
- 2 one
  + 10 two
* 21 three
\^?"
	     t '((2 . 0)
		 (12 . 2)
		 (19 . 0))))
  )

(ert-deftest rst-convert-bullets-to-enumeration ()
  "Tests `rst-convert-bullets-to-enumeration'."
  (should (ert-equal-buffer
	   '(rst-convert-bullets-to-enumeration)
"\^@Normal paragraph.

* A bullet

* Another bullet

Another normal paragraph.

\^?"
"\^@Normal paragraph.

1. A bullet

2. Another bullet

Another normal paragraph.

\^?" t))
  (should (ert-equal-buffer
	   '(rst-convert-bullets-to-enumeration)
"Normal paragraph.

\^?* A bullet

* Another bullet

\^@Another normal paragraph.

"
"Normal paragraph.

\^?1. A bullet

2. Another bullet

\^@Another normal paragraph.

" t))
  (should (ert-equal-buffer
	   '(rst-convert-bullets-to-enumeration)
"Normal paragraph.

\^?* A bullet

* Another bullet

1. A bullet

2. Another bullet

\^@Another normal paragraph.

"
		      
"Normal paragraph.

\^?1. A bullet

2. Another bullet

3. A bullet

4. Another bullet

\^@Another normal paragraph.

" t))
  )

(ert-deftest rst-convert-bullets-to-enumeration-BUGS ()
  "Exposes bugs in `rst-convert-bullets-to-enumeration'."
  :expected-result :failed ;; These are bugs
  (should (ert-equal-buffer
	   '(rst-convert-bullets-to-enumeration)
"\^@Normal paragraph.

* A bullet

* Another bullet

  * A bullet

  * Another bullet

Another normal paragraph.

\^?"
"\^@Normal paragraph.

1. A bullet

2. Another bullet

  * A bullet

  * Another bullet

Another normal paragraph.

\^?" t))
  )

(ert-deftest rst-insert-list-continue ()
  "Tests `rst-insert-list' when continuing a list."
  (should (ert-equal-buffer
	   '(rst-insert-list)
"* Some text\^@\n"
"* Some text
* \^@\n"))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"* Some \^@text\n"
"* Some text
* \^@\n"))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"* \^@Some text\n"
"* Some text
* \^@\n"))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"* Some text
  - A deeper hyphen bullet\^@\n"
"* Some text
  - A deeper hyphen bullet
  - \^@\n"))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"* Some text
  - \^@Some text\n"
"* Some text
  - Some text
  - \^@\n"))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"1. Some text\^@\n"
"1. Some text
2. \^@\n"))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"2. Some text\^@\n"
"2. Some text
3. \^@\n"))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"a) Some text\^@\n"
"a) Some text
b) \^@\n"))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"(A) Some text\^@\n"
"(A) Some text
\(B) \^@\n"))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"(I) Some text\^@\n"
"(I) Some text
\(J) \^@\n"))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"(I) Some text\^@\n"
"(I) Some text
\(J) \^@\n"))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"(h) Some text
\(i) Some text\^@\n"
"(h) Some text
\(i) Some text
\(j) \^@\n"))
  (should (ert-equal-buffer
	   '(rst-insert-list t)
"(i) Some text\^@\n"
"(i) Some text
\(ii) \^@\n"))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"(IV) Some text
\(V) Some text\^@\n"
"(IV) Some text
\(V) Some text
\(VI) \^@\n"))
  )

(ert-deftest rst-insert-list-continue-BUGS ()
  "Exposes bugs in `rst-insert-list-continue'."
  :expected-result :failed ;; These are bugs
  (should (ert-equal-buffer
	   '(rst-insert-list)
"(iv) Some text

\(v) Some text\^@\n"
"(iv) Some text

\(v) Some text
\(vi) \^@\n")))

(ert-deftest rst-insert-list-new ()
  "Tests `rst-insert-list' when inserting a new list."
  (should (ert-equal-buffer
	   '(rst-insert-list)
"\^@
"
"* \^@
" '("*")))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"
\^@
"
"
- \^@
" '("-")))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"
\^@

"
"
#. \^@

" '("#.")))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"\^@
"
"5) \^@
" '("1)" 5)))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"\^@
"
"(i) \^@
" '("(i)" "")))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"\^@
"
"IV. \^@
" '("I." 4)))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"Some line\^@
"
"Some line

c. \^@
" '("a." "c")))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"Some line
\^@
"
"Some line

B) \^@
" '("A)" "B")))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"Some line

\^@
"
"Some line

IV. \^@
" '("I." 4)))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"Some line
\^@Another line
"
"Some line
Another line

* \^@
" '("*")))
  )

(ert-deftest rst-insert-list-new-BUGS ()
  "Exposes bugs in `rst-insert-list' when inserting a new list."
  :expected-result :failed ;; These are bugs
  (should (ert-equal-buffer
	   '(rst-insert-list)
"\^@    \n"
"* \^@
" '("*")))
  (should (ert-equal-buffer
	   '(rst-insert-list)
"Some line
\^@
Another line
"
"Some line

* \^@

Another line
" '("*")))
  )

(ert-deftest rst-straighten-bullets-region ()
  "Tests `rst-straighten-bullets-region'."
  (let ((rst-preferred-bullets '(?* ?-)))
    (should (ert-equal-buffer
	     '(rst-straighten-bullets-region)
	     "\^@\^?"
	     "\^@\^?"
	     t))
    (should (ert-equal-buffer
	     '(rst-straighten-bullets-region)
	     "\^@
- one
+ two
* three
\^?"
	     "\^@
* one
* two
* three
\^?"
	     t))
    (should (ert-equal-buffer
	     '(rst-straighten-bullets-region)
	     "- one\^@
+ two\^?"
	     "* one\^@
* two\^?"
	     t))
    (should (ert-equal-buffer
	     '(rst-straighten-bullets-region)
	     "+ zero
\^@- one
+ two
* three\^?
- four"
	     "+ zero
\^@* one
* two
* three\^?
- four"
	     t))
    (should (ert-equal-buffer
	     '(rst-straighten-bullets-region)
	     "\^@
- one

  + two

* three
\^?"
	     "\^@
* one

  - two

* three
\^?"
	     t))
    (should (ert-equal-buffer
	     '(rst-straighten-bullets-region)
	     "\^@
- one

  - two

* three
\^?"
	     "\^@
* one

  - two

* three
\^?"
	     t))
    (should (ert-equal-buffer
	     '(rst-straighten-bullets-region)
	     "\^@
+ one

  * two

+ three
\^?"
	     "\^@
* one

  - two

* three
\^?"
	     t))
    )
  (let ((rst-preferred-bullets nil))
    (should (ert-equal-buffer
	     '(rst-straighten-bullets-region)
	     "\^@
- one
+ two
* three
\^?"
	     "\^@
- one
+ two
* three
\^?"
	     t))
    ))

(ert-deftest rst-straighten-bullets-region-BUGS ()
  "Tests `rst-straighten-bullets-region'."
  :expected-result :failed ;; These are bugs
  (let ((rst-preferred-bullets '(?* ?-)))
    (should (ert-equal-buffer
	     '(rst-straighten-bullets-region)
	     "\^@
- one
  + two
* three
\^?"
	     "\^@
* one
  - two
* three
\^?"
	     t))
    (should (ert-equal-buffer
	     '(rst-straighten-bullets-region)
	     "\^@
- one
  + two
* three
\^?"
	     "\^@
* one
  - two
* three
\^?"
	     t))
    (should (ert-equal-buffer
	     '(rst-straighten-bullets-region)
	     "\^@
+ one
  * two
+ three
\^?"
	     "\^@
* one
  - two
* three
\^?"
	     t))
    ))

(defun arabic-roman-roundtrip (arabic roman)
  "Convert ARABIC to roman, compare it to ROMAN and convert this back.
Return t if roundtrip is correct."
  (let ((cvt-roman (rst-arabic-to-roman arabic))
	(cvt-arabic (rst-roman-to-arabic roman)))
    (and (equal roman cvt-roman) (equal arabic cvt-arabic))))

(ert-deftest arabic-roman-roundtrip ()
  "Test `rst-arabic-to-roman' and `rst-roman-to-arabic'."

  ;; Test invalid arabic numbers.
  (should-error (arabic-roman-roundtrip -1 "I")
		:type 'wrong-type-argument)
  (should-error (arabic-roman-roundtrip 0 "I")
		:type 'wrong-type-argument)
  (should-error (arabic-roman-roundtrip nil "I")
		:type 'wrong-type-argument)

  ;; Test invalid roman numbers.
  (should-error (arabic-roman-roundtrip 1 nil)
		:type 'wrong-type-argument)
  (should-error (arabic-roman-roundtrip 1 "NoRoman")
		:type 'wrong-type-argument)
  (should-error (arabic-roman-roundtrip 1 "")
		:type 'wrong-type-argument)

  ;; Test values.
  (should (arabic-roman-roundtrip 1 "I"))
  (should (arabic-roman-roundtrip 4 "IV"))
  (should (arabic-roman-roundtrip 5 "V"))
  (should (arabic-roman-roundtrip 10 "X"))
  (should (arabic-roman-roundtrip 20 "XX"))
  (should (arabic-roman-roundtrip 1999 "MCMXCIX"))
  (should (arabic-roman-roundtrip 2000 "MM"))
  (should (arabic-roman-roundtrip 3333 "MMMCCCXXXIII"))
  (should (arabic-roman-roundtrip 444 "CDXLIV"))
  )
