#!/usr/bin/env make

EMACS = /usr/bin/emacs
ERT = ~/lib/emacs/ert
RST_EL = ../rst.el

EMACS_ERT_PFX = $(EMACS) --batch --quick --directory=$(ERT) --load=ert.el
EMACS_ERT_SFX = --funcall=ert-run-tests-batch-and-exit

ERT_TESTS := $(filter-out ert-%,$(wildcard *.el))

EMACS_COMPILE_PFX = $(EMACS) --batch --quick --eval '(progn		\
    (setq byte-compile-error-on-warn t)					\
    (kill-emacs (if (byte-compile-file
EMACS_COMPILE_SFX = ) 0 1)))'

all: compile tests

tests:
	$(EMACS_ERT_PFX) $(addprefix -l ,$(ERT_TESTS)) $(EMACS_ERT_SFX)

compile:
	$(EMACS_COMPILE_PFX) "$(RST_EL)" $(EMACS_COMPILE_SFX)

clean:
