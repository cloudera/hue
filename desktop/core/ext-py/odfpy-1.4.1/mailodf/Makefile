all: odf mailodf.1 

txt: mailodf.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.1 *~ *.txt odf
odf:
	ln -s ../odf

test: clean odf
	@echo -n "Please input your local email for the test > "; read to; \
	  python2 mailodf -f python2@python.org -s "F.Y.I" ../tests/examples/ol.odp "$$to"; \
	  python3 mailodf -f python3@python.org -s "F.Y.I" ../tests/examples/ol.odp "$$to"
	@echo 'You should receive two e-mails, one from python2@python.org'
	@echo 'and the second from python3@python.org, with subjects: "F.Y.I"'
