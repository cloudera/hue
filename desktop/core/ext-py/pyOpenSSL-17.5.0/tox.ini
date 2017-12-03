[tox]
envlist = {pypy,py26,py27,py34,py35,py36}{,-cryptographyMaster,-cryptographyMinimum},py27-twistedMaster,pypi-readme,check-manifest,flake8,docs,coverage-report

[testenv]
whitelist_externals =
    openssl
passenv = ARCHFLAGS CFLAGS LC_ALL LDFLAGS PATH LD_LIBRARY_PATH TERM
extras =
    test
deps =
    coverage>=4.2
    cryptographyMaster: git+https://github.com/pyca/cryptography.git
    cryptographyMinimum: cryptography==2.1.4
setenv =
    # Do not allow the executing environment to pollute the test environment
    # with extra packages.
    PYTHONPATH=
    PIP_NO_BINARY=cryptography
commands =
    openssl version
    coverage run --parallel -m OpenSSL.debug
    coverage run --parallel -m pytest -v {posargs}

[testenv:py27-twistedMaster]
deps =
    # [tls,conch] syntax doesn't work here so we enumerate all dependencies.
    git+https://github.com/twisted/twisted
    idna
    service_identity
passenv = ARCHFLAGS CFLAGS LC_ALL LDFLAGS PATH LD_LIBRARY_PATH TERM
commands =
    python -c "import OpenSSL.SSL; print(OpenSSL.SSL.SSLeay_version(OpenSSL.SSL.SSLEAY_VERSION))"
    python -c "import cryptography; print(cryptography.__version__)"
    python -m twisted.trial --reporter=text twisted

[testenv:py35-urllib3Master]
basepython=python3.5
deps =
    pyasn1
    ndg-httpsclient
passenv = ARCHFLAGS CFLAGS LC_ALL LDFLAGS PATH LD_LIBRARY_PATH TERM
whitelist_externals =
    rm
commands =
    python -c "import OpenSSL.SSL; print(OpenSSL.SSL.SSLeay_version(OpenSSL.SSL.SSLEAY_VERSION))"
    python -c "import cryptography; print(cryptography.__version__)"
    {toxinidir}/.travis/install_urllib3.sh
    pytest urllib3/test
    rm -rf ./urllib3

[testenv:flake8]
deps =
     flake8
skip_install = true
commands =
     flake8 src tests examples setup.py

[testenv:pypi-readme]
deps =
    readme_renderer
skip_install = true
commands =
    python setup.py check -r -s

[testenv:check-manifest]
deps =
    check-manifest
skip_install = true
commands =
    check-manifest

[testenv:docs]
extras =
    docs
basepython = python2.7
commands =
     sphinx-build -W -b html doc doc/_build/html

[testenv:coverage-report]
deps = coverage>=4.2
skip_install = true
commands =
    coverage combine
    coverage report
