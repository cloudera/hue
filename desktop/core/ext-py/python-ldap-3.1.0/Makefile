PYTHON=python3
LCOV_INFO=build/lcov.info
LCOV_REPORT=build/lcov_report
LCOV_REPORT_OPTIONS=--show-details -no-branch-coverage \
	--title "python-ldap LCOV report"
SCAN_REPORT=build/scan_report
PYTHON_SUPP=/usr/share/doc/python3-devel/valgrind-python.supp
AUTOPEP8_OPTS=--aggressive

.NOTPARALLEL:

.PHONY: all
all:

.PHONY: clean
clean:
	rm -rf build dist *.egg-info .tox MANIFEST
	rm -f .coverage .coverage.*
	find . \( -name '*.py[co]' -or -name '*.so*' -or -name '*.dylib' \) \
	    -delete
	find . -depth -name __pycache__ -exec rm -rf {} \;

build:
	mkdir -p build

# LCOV report (measuring test coverage for C code)
.PHONY: lcov-clean lcov-coverage lcov-report lcov-open lcov
lcov-clean:
	rm -rf $(LCOV_INFO) $(LCOV_REPORT)
	if [ -d build ]; then find build -name '*.gc??' -delete; fi

lcov-coverage:
	WITH_GCOV=1 tox -e py27,py36

$(LCOV_INFO): build
	lcov --capture --directory build --output-file $(LCOV_INFO)

$(LCOV_REPORT): $(LCOV_INFO)
	genhtml --output-directory $(LCOV_REPORT) \
		$(LCOV_REPORT_OPTIONS) $(LCOV_INFO)

lcov-report: $(LCOV_REPORT)

lcov-open: $(LCOV_REPORT)
	xdg-open $(LCOV_REPORT)/index.html

lcov: lcov-clean
	$(MAKE) lcov-coverage
	$(MAKE) lcov-report

# clang-analyzer for static C code analysis
.PHONY: scan-build
scan-build:
	scan-build -o $(SCAN_REPORT) --html-title="python-ldap scan report" \
		-analyze-headers --view \
		$(PYTHON) setup.py clean --all build

# valgrind memory checker
.PHONY: valgrind
$(PYTHON_SUPP):
	@ >&2 echo "valgrind-python.supp not found"
	@ >&2 echo "install Python development files and run:"
	@ >&2 echo "    $(MAKE) valgrind PYTHON_SUPP=/your/path/to/valgrind-python.supp"
	exit 1;

valgrind: build $(PYTHON_SUPP)
	valgrind \
	    --leak-check=full \
	    --track-fds=yes \
	    --suppressions=$(PYTHON_SUPP) \
	    --suppressions=Misc/python-ldap.supp \
	    --gen-suppressions=all \
	    --log-file=build/valgrind.log \
	    $(PYTHON) setup.py test

	@grep -A7 "blocks are definitely lost" build/valgrind.log; \
	if [ $$? == 0 ]; then \
	    echo "Found definitive leak, see build/valgrind.log"; \
	    exit 1; \
	fi

# Code autoformatter
.PHONY: autoformat indent autopep8
autoformat: indent autopep8

indent:
	indent Modules/*.c Modules/*.h
	rm -f Modules/*.c~ Modules/*.h~

autopep8:
	$(PYTHON) -m autopep8 -r -i -j0 $(AUTOPEP8_OPTS) \
	    Demo Lib Tests setup.py
