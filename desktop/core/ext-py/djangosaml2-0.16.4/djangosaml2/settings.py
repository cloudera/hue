from django.conf import settings

SAML_DJANGO_USER_MAIN_ATTRIBUTE = getattr(
    settings, 'SAML_DJANGO_USER_MAIN_ATTRIBUTE', 'username')
SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP = getattr(
    settings, 'SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP', '')
