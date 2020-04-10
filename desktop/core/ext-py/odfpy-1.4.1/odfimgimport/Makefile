all: odf odfimgimport.1 

txt: odfimgimport.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.1 *.txt odf textWithImages-fetchedBy*
odf:
	ln -s ../odf

test: clean odf
	@python2 odfimgimport -o textWithImages-fetchedByPython2.odt \
	  textWithImages.odt
	@python3 odfimgimport -o textWithImages-fetchedByPython3.odt \
	  textWithImages.odt
	@echo created textWithImages-fetchedByPython2.odt and \
	  textWithImages-fetchedByPython3.odt
