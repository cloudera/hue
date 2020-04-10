all: odf odscell.1

txt: odscell.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.txt odf
odf:
	ln -s ../../odf
