;; In the ~/init.el file, write:
;; (setq load-path (cons "c:\\sf\\ctypes" load-path)
;; (require 'ctypes-dev)
;;
;; Try M-x customize-group ctypes-dev
;;
;; Based on twisted-dev.el

(provide 'ctypes-dev)

(defgroup ctypes-dev nil
  "Various ctypes development utilities"
  :group 'development)

(defcustom ctypes-dev-directory "c:\\sf\\ctypes_dist"
  "ctypes root directory"
  :group 'ctypes-dev
  :type 'string)

(setenv "PYTHONPATH" ctypes-dev-directory)

(defmacro with-cd (dirname &rest code)
  `(let ((old-dirname default-directory)
	 (start-buffer (current-buffer)))
     (cd ,dirname)
     (unwind-protect (progn ,@code)
       (let ((end-buffer (current-buffer)))
	 ;; (cd ,dirname)
	 (set-buffer start-buffer)
	 (cd old-dirname)
	 (set-buffer end-buffer)))))

(defun ctypes-dev-build ()
  (interactive)
  (with-cd ctypes-dev-directory
	   (compile "python setup.py build")))

(defun ctypes-dev-build-debug ()
  (interactive)
  (with-cd ctypes-dev-directory
	   (compile "py_d setup.py build -g")))

(defun ctypes-dev-rebuild ()
  (interactive)
  (with-cd ctypes-dev-directory
	   (compile "python setup.py build -f")))

(defun ctypes-dev-test ()
  (interactive)
  (with-cd (concat ctypes-dev-directory "\\unittests")
	   (compile "python runtests.py")))

(defun ctypes-dev-test-debug ()
  (interactive)
  (with-cd (concat ctypes-dev-directory "\\unittests")
	   (compile "py_d runtests.py")))

(defun comtypes-test ()
  (interactive)
  (with-cd (concat ctypes-dev-directory "\\comtypes\\unittests")
	   (compile "python runtests.py")))

(defun comtypes-test-debug ()
  (interactive)
  (with-cd (concat ctypes-dev-directory "\\comtypes\\unittests")
	   (compile "py_d runtests.py")))

(define-minor-mode ctypes-dev-mode
  "Toggle ctypes-dev mode.
With no argument, this command toggles the mode.
Non-null prefix argument turns on the mode.
Null prefix argument turns off the mode."
 ;; The initial value.
 nil
 ;; The indicator for the mode line.
 " ctypes"
 ;; The minor mode bindings.
 '(
;;   ([f6] . ctypes-dev-genapidoc)
;;   ([f7] . ctypes-dev-gendoc)
   ('(shift f8) . ctypes-dev-build-debug)
   ([f8] . ctypes-dev-build)
   ('(shift f9) . ctypes-dev-test-debug)
   ([f9] . ctypes-dev-test)
   ([f10] . comtypes-test)
   ('(shift f10) . comtypes-test-debug)
;;   ([f11] . ctypes-dev-grep)
;;   ([f12] . ctypes-dev-gendocs)
))


(add-hook
 'find-file-hooks
 (lambda ()
   (let ((full-ctypes-path (expand-file-name ctypes-dev-directory)))
     (if (> (length (buffer-file-name)) (length full-ctypes-path))
	 (if (string=
	      (substring (buffer-file-name) 0 (length full-ctypes-path))
	      full-ctypes-path)
	     (ctypes-dev-mode)
	   )))))

;(add-hook
; 'python-mode-hook
; (lambda ()
;   (ctypes-dev-mode t)))