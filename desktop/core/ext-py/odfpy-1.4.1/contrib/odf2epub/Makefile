all: odf odf2epub.1 

txt: odf2epub.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.txt odf

odf:
	ln -s ../../odf
