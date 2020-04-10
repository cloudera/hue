all: odf odt2tracwiki.1 

txt: odt2tracwiki.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.txt odf

odf:
	ln -s ../../odf
