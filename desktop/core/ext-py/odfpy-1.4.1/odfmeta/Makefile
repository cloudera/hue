all: odf odfmeta.1 

txt: odfmeta.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.1 *~ *.txt odf
odf:
	ln -s ../odf

test: clean odf
	@echo ============= output by Python2 =======================
	@python2 odfmeta ../tests/examples/pythagoras.ods
	@echo ============= output by Python3 =======================
	@python3 odfmeta ../tests/examples/pythagoras.ods
