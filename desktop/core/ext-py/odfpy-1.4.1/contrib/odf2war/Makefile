all: odf odf2war.1 

txt: odf2war.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.txt odf

odf:
	ln -s ../odf
