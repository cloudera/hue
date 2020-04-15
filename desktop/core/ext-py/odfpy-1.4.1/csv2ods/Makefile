all: odf csv2ods.1 

txt: csv2ods.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.1 *~ *.txt odf test.csv test2.ods test3.ods
odf:
	ln -s ../odf

test: clean odf
	@echo 1,2,3,4 > test.csv
	@echo 5,6,7,8 >> test.csv
	@echo 9,10,11,12 >> test.csv
	@python2 csv2ods -i test.csv -o test2.ods
	@python3 csv2ods -i test.csv -o test3.ods
	@echo created files test.csv, test2.ods and test3.ods
