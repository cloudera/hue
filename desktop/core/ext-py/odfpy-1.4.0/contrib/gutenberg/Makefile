all: odf gbtext2odt.1 

txt: gbtext2odt.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.txt odf
odf:
	ln -s ../../odf
