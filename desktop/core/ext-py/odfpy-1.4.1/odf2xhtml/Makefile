all: odf odf2xhtml.1 

txt: odf2xhtml.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.1 *.txt odf

odf:
	ln -s ../odf

test: clean odf
	@echo ============== output by Python2 ====================
	@python2 odf2xhtml ../tests/examples/headerfooter.odt
	@echo =====================================================
	@echo
	@echo ============== output by Python3 ====================
	@python3 odf2xhtml ../tests/examples/headerfooter.odt
	@echo =====================================================
