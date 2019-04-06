all: odf odf2zwikimoin.1 

txt: odf2zwikimoin.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.txt odf

odf:
	ln -s ../../odf
