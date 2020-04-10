all: odf syntaxhighlight.1 

txt: syntaxhighlight.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.txt odf
odf:
	ln -s ../../odf
