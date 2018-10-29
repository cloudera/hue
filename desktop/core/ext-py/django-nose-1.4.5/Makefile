.PHONY: clean clean-build clean-pyc clean-test docs qa lint coverage jslint qa-all install-jslint test test-all coverage-console release sdist

help:
	@echo "clean - remove all artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation"
	@echo "lint - check style with flake8"
	@echo "qa - run linters and test coverage"
	@echo "qa-all - run QA plus tox and packaging"
	@echo "release - package and upload a release"
	@echo "sdist - package"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "test-release - upload a release to the PyPI test server"

clean: clean-build clean-pyc clean-test

qa: lint coverage

qa-all: qa sdist test-all

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . \( -name \*.pyc -o -name \*.pyo -o -name __pycache__ \) -delete
	find . -name '*~' -delete

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

lint:
	flake8 .

test:
	./manage.py test

test-all:
	COVERAGE=1 tox --skip-missing-interpreters

coverage-console:
	coverage erase
	COVERAGE=1 ./runtests.sh
	coverage combine
	coverage report -m

coverage: coverage-console
	coverage html
	open htmlcov/index.html

release: sdist
	twine upload dist/*
	python -m webbrowser -n https://pypi.python.org/pypi/django-nose

# Add [test] section to ~/.pypirc, https://test.pypi.org/legacy/
test-release: sdist
	twine upload --repository test dist/*
	python -m webbrowser -n https://testpypi.python.org/pypi/django-nose

sdist: clean
	python setup.py sdist bdist_wheel
	ls -l dist
	check-manifest
	pyroma dist/`ls -t dist | grep tar.gz | head -n1`
