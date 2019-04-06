all: odf odfuserfield.1 

txt: odfuserfield.txt

%.1: %.docbook 
	xmlto man $<

%.txt: %.docbook 
	xmlto txt $<

clean:
	rm -f *.1 *~ *.txt odf userfieldsFilledByPython*
odf:
	ln -s ../odf

test: clean odf
	@echo =============== output by Python2 =========================
	@echo ========= list userfields from ../tests/examples/userfields.odt
	@python2 odfuserfield -l ../tests/examples/userfields.odt
	@echo ========= injection of values =============================
	@python odfuserfield -o userfieldsFilledByPython2.odt \
	  -s username:jdoe -s firstname:John -s lastname:Doe \
	  -s "address:10 Downing Street" ../tests/examples/userfields.odt
	@echo ========= extraction of values =============================
	python odfuserfield -X username -X firstname -X lastname \
	  -X address userfieldsFilledByPython2.odt
	@echo ============================================================
	@echo
	@echo =============== output by Python3 =========================
	@echo ========= list userfields from ../tests/examples/userfields.odt
	@python3 odfuserfield -l ../tests/examples/userfields.odt
	@echo ========= injection of values =============================
	@python odfuserfield -o userfieldsFilledByPython3.odt \
	  -s username:jdoe -s firstname:John -s lastname:Doe \
	  -s "address:10 Downing Street" ../tests/examples/userfields.odt
	@echo ========= extraction of values =============================
	python odfuserfield -X username -X firstname -X lastname \
	  -X address userfieldsFilledByPython3.odt
	@echo ============================================================
