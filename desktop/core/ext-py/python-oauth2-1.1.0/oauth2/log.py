"""
Logging support

There are two loggers available:

* ``oauth2.application``: Logging of uncaught exceptions
* ``oauth2.general``: General purpose logging of debug errors and warnings

If logging has not been configured, you will likely see this error:

.. code-block:: python

    No handlers could be found for logger "oauth2.application"

Make sure that logging is configured to avoid this:

.. code-block:: python

    import logging
    logging.basicConfig()

"""
import logging

app_log = logging.getLogger("oauth2.application")
gen_log = logging.getLogger("oauth2.general")
