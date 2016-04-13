from __future__ import absolute_import

from django.contrib import admin
from django.core.paginator import Paginator

from .models import (Event, Child, Parent, Genre, Band, Musician, Group,
    Quartet, Membership, ChordsMusician, ChordsBand, Invitation, Swallow)


site = admin.AdminSite(name="admin")

class CustomPaginator(Paginator):
    def __init__(self, queryset, page_size, orphans=0, allow_empty_first_page=True):
        super(CustomPaginator, self).__init__(queryset, 5, orphans=2,
            allow_empty_first_page=allow_empty_first_page)


class EventAdmin(admin.ModelAdmin):
    list_display = ['event_date_func']

    def event_date_func(self, event):
        return event.date

site.register(Event, EventAdmin)


class ParentAdmin(admin.ModelAdmin):
    list_filter = ['child__name']
    search_fields = ['child__name']


class ChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']
    list_per_page = 10
    list_filter = ['parent', 'age']

    def get_queryset(self, request):
        return super(ChildAdmin, self).get_queryset(request).select_related("parent__name")


class CustomPaginationAdmin(ChildAdmin):
    paginator = CustomPaginator


class FilteredChildAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']
    list_per_page = 10

    def get_queryset(self, request):
        return super(FilteredChildAdmin, self).get_queryset(request).filter(
            name__contains='filtered')


class BandAdmin(admin.ModelAdmin):
    list_filter = ['genres']


class GroupAdmin(admin.ModelAdmin):
    list_filter = ['members']


class QuartetAdmin(admin.ModelAdmin):
    list_filter = ['members']


class ChordsBandAdmin(admin.ModelAdmin):
    list_filter = ['members']


class InvitationAdmin(admin.ModelAdmin):
    list_display = ('band', 'player')
    list_select_related = ('player',)


class DynamicListDisplayChildAdmin(admin.ModelAdmin):
    list_display = ('parent', 'name', 'age')

    def get_list_display(self, request):
        my_list_display = super(DynamicListDisplayChildAdmin, self).get_list_display(request)
        if request.user.username == 'noparents':
            my_list_display = list(my_list_display)
            my_list_display.remove('parent')
        return my_list_display

class DynamicListDisplayLinksChildAdmin(admin.ModelAdmin):
    list_display = ('parent', 'name', 'age')
    list_display_links = ['parent', 'name']

    def get_list_display_links(self, request, list_display):
        return ['age']

site.register(Child, DynamicListDisplayChildAdmin)

class SwallowAdmin(admin.ModelAdmin):
    actions = None # prevent ['action_checkbox'] + list(list_display)
    list_display = ('origin', 'load', 'speed')

site.register(Swallow, SwallowAdmin)

class DynamicListFilterChildAdmin(admin.ModelAdmin):
    list_filter = ('parent', 'name', 'age')

    def get_list_filter(self, request):
        my_list_filter = super(DynamicListFilterChildAdmin, self).get_list_filter(request)
        if request.user.username == 'noparents':
            my_list_filter = list(my_list_filter)
            my_list_filter.remove('parent')
        return my_list_filter

