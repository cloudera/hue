;; Tests for functions around indentation  -*- lexical-binding: t -*-

(add-to-list 'load-path ".")
(load "init" nil t)
(init-rst-ert t)

(ert-deftest indent-asserts ()
  "Check some assertions."
  (should (equal ert-Buf-point-char "\^@"))
  (should (equal ert-Buf-mark-char "\^?"))
  )

(defun indent-for-tab (&optional count)
  "Wrapper to call `indent-for-tab-command' COUNT times defaulting to 1."
  (setq count (or count 1))
  (rst-mode)
  (dotimes (i count)
    (indent-for-tab-command)))

(ert-deftest indent-for-tab-command ()
  "Tests for `indent-for-tab-command'."
  (let ((rst-indent-width 2)
	(rst-indent-field 2)
	(rst-indent-literal-normal 3)
	(rst-indent-literal-minimized 2)
	(rst-indent-comment 3))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "\^@"
	     t
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
* a
\^@"
	     "
* a
  \^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
* a
  \^@"
	     "
* a
\^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
* a

* b\^@"
	     "
* a

  * b\^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
* a

  * b\^@"
	     "
* a

* b\^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
* a

\^@* b"
	     "
* a

  \^@* b"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
* a

  \^@* b"
	     "
* a

\^@* b"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
* a
  * b
    XV. c
  * d
* e
\^@"
	     "
* a
  * b
    XV. c
  * d
* e
  \^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
* a
  * b
    XV. c
  * d
* e
  \^@"
	     "
* a
  * b
    XV. c
  * d
* e
\^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
* a
  * b
    XV. c
  * d
 * e\^@"
	     "
* a
  * b
    XV. c
  * d
    * e\^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
* a
  * b
    XV. c
  * d
    * e\^@"
	     "
* a
  * b
    XV. c
  * d
  * e\^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
* a
  * b
    XV. c
  * d
  * e\^@"
	     "
* a
  * b
    XV. c
  * d
* e\^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
* a
  * b
    XV. c
  * d
* e\^@"
	     "
* a
  * b
    XV. c
  * d
    * e\^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
                   \^@"
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
                 \^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
                 \^@"
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
               \^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
               \^@"
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
             \^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
             \^@"
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
            \^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
            \^@"
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
          \^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
          \^@"
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
        \^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
        \^@"
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
      \^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
      \^@"
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
   \^@"
	     ))
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
   \^@"
	     "
.. [CIT]

     citation

   .. |sub| dir:: Same

        * a

          * b

             :f: val::
\^@"
	     ))
  ))

(ert-deftest indent-for-tab-command-BUGS ()
  "Exposes bugs for `indent-for-tab-command'."
  :expected-result :failed ;; These are bugs
  (let ((rst-indent-width 2)
	(rst-indent-field 2)
	(rst-indent-literal-normal 3)
	(rst-indent-literal-minimized 2)
	(rst-indent-comment 3))
    ;; Bug https://sourceforge.net/p/docutils/bugs/299/
    (should (ert-equal-buffer
	     '(indent-for-tab)
	     "
Lorem ipsum dolor sit amet, consectetur adipisicing elit
:other:`something` sed do eiusmod tempor incididunt ut
\^@"
	     "
Lorem ipsum dolor sit amet, consectetur adipisicing elit
:other:`something` sed do eiusmod tempor incididunt ut
\^@"
	     ))))
