all: odf xml2odf.1 

txt: xml2odf.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.1 *~ *.txt odf definitionlistsOutput*
odf:
	ln -s ../odf

test: clean odf
	@echo =============== output by Python2 ===================
	@python3 xml2odf -o definitionlistsOutput2.odt definitionlists.xml
	@echo created definitionlistsOutput2.odt
	@echo =============== output by Python3 ===================
	@python3 xml2odf -o definitionlistsOutput3.odt definitionlists.xml
	@echo created definitionlistsOutput3.odt
