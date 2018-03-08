default: test lint

test:
	python test_ipaddress.py

lint:
	@(python --version 2>&1 | grep -q ' 2\.6\.') || flake8 ipaddress.py test_ipaddress.py

pypi:
	python setup.py sdist bdist upload

clean:
	rm -rf -- build dist ipaddress.egg-info

.PHONY: default test clean pypi lint

