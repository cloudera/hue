
check:
	PYTHONPATH=$(shell pwd) python manage.py test --verbosity=2 django_openid_auth

run-example-consumer:
	PYTHONPATH=$(shell pwd) python manage.py syncdb --migrate
	PYTHONPATH=$(shell pwd) python manage.py runserver

.PHONY: check run-example-consumer
