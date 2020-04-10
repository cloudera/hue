all: odf odf2xml.1 

txt: odf2xml.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.1 *~ *.txt odf
odf:
	ln -s ../odf

test: clean odf
	@echo ========================= output by Python2 =====================
	@python2 odf2xml ../tests/examples/headerfooter.odt
	@echo ========================= output by Python3 =====================
	@python3 odf2xml ../tests/examples/headerfooter.odt
