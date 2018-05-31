from django.contrib import admin

from .models import OpenIDProvider, OpenIDUser


class OpenIDProviderAdmin(admin.ModelAdmin):
    list_display = ('issuer', 'client_id')
    list_filter = ('signing_alg',)


class OpenIDUserAdmin(admin.ModelAdmin):
    list_display = ('sub', 'user')
    list_filter = ('issuer',)


admin.site.register(OpenIDProvider, OpenIDProviderAdmin)
admin.site.register(OpenIDUser, OpenIDUserAdmin)
