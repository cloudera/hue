
check:
	PYTHONPATH=$(shell pwd) python example_consumer/manage.py test \
	   --verbosity=2 django_openid_auth

run-example-consumer:
	PYTHONPATH=$(shell pwd) python example_consumer/manage.py syncdb
	PYTHONPATH=$(shell pwd) python example_consumer/manage.py runserver

.PHONY: check run-example-consumer
