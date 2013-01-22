PAPER = a4
MKHOWTO = python tools/mkhowto --$(PAPER)

default: html

all: ps html text dvi

dvi ps text: pyOpenSSL.tex
	$(MKHOWTO) --$@ $^

html: pyOpenSSL.tex
	$(MKHOWTO) --html --iconserver . $^
	-rm -rf html
	mv pyOpenSSL html

clean:
	rm -rf html pyOpenSSL.dvi pyOpenSSL.ps pyOpenSSL.txt \
	    pyOpenSSL.l2h pyOpenSSL.how

.PHONY: default all html dvi ps text clean
