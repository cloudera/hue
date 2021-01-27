Usage
=====

It's strongly recommended to use the usual ``from django.conf import settings``
in your own code to access the configured settings.

But you can also **OPTIONALLY** use your app's own settings object directly,
by instantiating it in place::

    from myapp.models import MyAppConf

    myapp_settings = MyAppConf()

    print myapp_settings.SETTING_1

Note that accessing the settings that way means they don't have a prefix.

``AppConf`` instances don't automatically work as proxies for the global
settings. But you can enable this if you want by setting the ``proxy``
attribute of the inner ``Meta`` class to ``True``::

    from appconf import AppConf

    class MyAppConf(AppConf):
        SETTING_1 = "one"
        SETTING_2 = (
            "two",
        )

        class Meta:
            proxy = True

    myapp_settings = MyAppConf()

    if "myapp" in myapp_settings.INSTALLED_APPS:
        print "yay, myapp is installed!"

In case you want to override some settings programmatically, you can
simply pass the value when instantiating the ``AppConf`` class::

    from myapp.models import MyAppConf

    myapp_settings = MyAppConf(SETTING_1='something completely different')

    if 'different' in myapp_settings.SETTING_1:
        print "yay, I'm different!"

Custom configuration
--------------------

Each of the settings can be individually configured with callbacks.
For example, in case a value of a setting depends on other settings
or other dependencies. The following example sets one setting to a
different value depending on a global setting::

    from django.conf import settings
    from appconf import AppConf

    class MyCustomAppConf(AppConf):
        ENABLED = True

        def configure_enabled(self, value):
            return value and not settings.DEBUG

The value of ``MYAPP_ENABLED`` will vary depending on the
value of the global ``DEBUG`` setting.

Each of the app settings can be customized by providing
a method ``configure_<lower_setting_name>`` that takes the default
value as defined in the class attributes of the ``AppConf`` subclass
or the override value from the global settings as the only parameter.
The method **must return** the value to be use for the setting in
question.

After each of the ``configure_*`` methods has been called, the ``AppConf``
class will additionally call a main ``configure`` method, which can
be used to do any further custom configuration handling, e.g. if multiple
settings depend on each other. For that a ``configured_data`` dictionary
is provided in the setting instance::

    from django.conf import settings
    from appconf import AppConf

    class MyCustomAppConf(AppConf):
        ENABLED = True
        MODE = 'development'

        def configure_enabled(self, value):
            return value and not settings.DEBUG

        def configure(self):
            mode = self.configured_data['MODE']
            enabled = self.configured_data['ENABLED']
            if not enabled and mode != 'development':
                print "WARNING: app not enabled in %s mode!" % mode
            return self.configured_data

.. note::

    Don't forget to return the configured data in your custom ``configure``
    method if you edit it.
