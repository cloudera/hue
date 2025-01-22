Getting Started
===============

Prepare Database and Preload example data
````
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver
````

Test IdP
========

Congratulations, you have finished configuring the SP side of the federation.
Now you need to send the entity id and the metadata of this new SP to the
 IdP administrators so they can add it to their list of trusted services.

You can get this information starting your Django development server and
 going to the **http://localhost:8000/saml2/metadata/** url. If you have included
 the djangosaml2 urls under a different url prefix you need to correct this
 url.

There are many saml2 idps suitable for testing, such as [samltest.id](https://samltest.id/).
 If you are looking for a django IdP, you can try [uniAuth](https://github.com/UniversitaDellaCalabria/uniAuth) or
 [djangosaml2idp](https://github.com/OTA-Insight/djangosaml2idp/).
