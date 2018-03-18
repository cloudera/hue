from __future__ import unicode_literals

from django.test.utils import override_settings


override_session_serializer = override_settings(
    SESSION_SERIALIZER='django.contrib.sessions.serializers.PickleSerializer')
