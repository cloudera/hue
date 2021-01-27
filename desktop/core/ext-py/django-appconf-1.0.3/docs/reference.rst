=========
Reference
=========

.. currentmodule:: appconf

.. class:: AppConf

    A representation of a template tag. For example::

        class MyAppConf(AppConf):
            SETTING_1 = "one"
            SETTING_2 = (
                "two",
            )

    .. method:: configure_*(value)

        Method for each of the app settings for custom configuration
        which gets the value passed of the class attribute or the
        appropriate override value of the :attr:`~appconf.AppConf.Meta.holder`
        settings, e.g.::

            class MyAppConf(AppConf):
                DEPLOYMENT_MODE = "dev"

                def configure_deployment_mode(self, value):
                    if on_production():
                        value = "prod"
                    return value

        The method **must return** the value to be use for the setting in
        question.

    .. automethod:: configure
    .. autoattribute:: configured_data

        The dictionary attribute which can be used to do any further custom
        configuration handling in the :meth:`~appconf.AppConf.configure`
        method, e.g. if multiple settings depend on each other.

.. class:: AppConf.Meta

    An ``AppConf`` takes options via a ``Meta`` inner class::

        class MyAppConf(AppConf):
            SETTING_1 = "one"
            SETTING_2 = (
                "two",
            )

            class Meta:
                proxy = False
                prefix = 'myapp'
                required = ['SETTING_3', 'SETTING_4']
                holder = 'django.conf.settings'

    .. attribute:: prefix

        Explicitly choose a prefix for all settings handled by the
        ``AppConf`` class. If not given, the prefix will be the capitalized
        class module name.

        For example, ``acme`` would turn into settings like
        ``ACME_SETTING_1``.

    .. attribute:: required

        A list of settings that must be defined. If any of the specified
        settings are not defined, ``ImproperlyConfigured`` will be raised.

        .. versionadded:: 0.6

    .. attribute:: holder

        The global settings holder to use when looking for overrides and
        when setting the configured values.

        Defaults to ``'django.conf.settings'``.

    .. attribute:: proxy

        A boolean, if set to ``True`` will enable proxying attribute access
        to the :attr:`~appconf.AppConf.Meta.holder`.
