project := opentracing

pytest := PYTHONDONTWRITEBYTECODE=1 py.test --tb short -rxs \
	--cov-config .coveragerc --cov $(project) tests

html_report := --cov-report=html
test_args := --cov-report xml --cov-report term-missing

.PHONY: clean-pyc clean-build docs clean testbed
.DEFAULT_GOAL : help

help:
	@echo "bootstrap - initialize local environement for development. Requires virtualenv."
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "testbed - run testbed scenarios with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"

check-virtual-env:
	@echo virtual-env: $${VIRTUAL_ENV?"Please run in virtual-env"}

bootstrap: check-virtual-env
	pip install -r requirements.txt
	pip install -r requirements-test.txt
	python setup.py develop

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -rf {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -f coverage.xml
	rm -fr htmlcov/

lint:
	flake8 $(project) tests

test:
	$(pytest) $(test_args)

testbed:
	PYTHONDONTWRITEBYTECODE=1 python -m testbed

jenkins:
	pip install -r requirements.txt
	pip install -r requirements-test.txt
	python setup.py develop
	CLAY_CONFIG=config/test.yaml $(pytest) $(test_args) --junit-xml=jenkins.xml

coverage:
	coverage run --source $(project) setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	pip show -q opentracing || python setup.py develop
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

release: clean
	@echo Please see README
#	python setup.py sdist upload
#	python setup.py bdist_wheel upload

dist: clean
	@echo Please see README
#	python setup.py sdist
#	python setup.py bdist_wheel
#	ls -l dist

install:
	pip install -r requirements.txt
	pip install -r requirements-test.txt
	echo skipping pip install -r requirements-doc.txt
	python setup.py install
