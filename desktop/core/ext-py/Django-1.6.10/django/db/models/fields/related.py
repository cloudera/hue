from operator import attrgetter

from django.db import connection, connections, router
from django.db.backends import util
from django.db.models import signals, get_model
from django.db.models.fields import (AutoField, Field, IntegerField,
    PositiveIntegerField, PositiveSmallIntegerField, FieldDoesNotExist)
from django.db.models.related import RelatedObject, PathInfo
from django.db.models.query import QuerySet
from django.db.models.deletion import CASCADE
from django.utils.encoding import smart_text
from django.utils import six
from django.utils.deprecation import RenameMethodsBase
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import curry, cached_property
from django.core import exceptions
from django import forms

RECURSIVE_RELATIONSHIP_CONSTANT = 'self'

pending_lookups = {}


def add_lazy_relation(cls, field, relation, operation):
    """
    Adds a lookup on ``cls`` when a related field is defined using a string,
    i.e.::

        class MyModel(Model):
            fk = ForeignKey("AnotherModel")

    This string can be:

        * RECURSIVE_RELATIONSHIP_CONSTANT (i.e. "self") to indicate a recursive
          relation.

        * The name of a model (i.e "AnotherModel") to indicate another model in
          the same app.

        * An app-label and model name (i.e. "someapp.AnotherModel") to indicate
          another model in a different app.

    If the other model hasn't yet been loaded -- almost a given if you're using
    lazy relationships -- then the relation won't be set up until the
    class_prepared signal fires at the end of model initialization.

    operation is the work that must be performed once the relation can be resolved.
    """
    # Check for recursive relations
    if relation == RECURSIVE_RELATIONSHIP_CONSTANT:
        app_label = cls._meta.app_label
        model_name = cls.__name__

    else:
        # Look for an "app.Model" relation

        if isinstance(relation, six.string_types):
            try:
                app_label, model_name = relation.split(".")
            except ValueError:
                # If we can't split, assume a model in current app
                app_label = cls._meta.app_label
                model_name = relation
        else:
            # it's actually a model class
            app_label = relation._meta.app_label
            model_name = relation._meta.object_name

    # Try to look up the related model, and if it's already loaded resolve the
    # string right away. If get_model returns None, it means that the related
    # model isn't loaded yet, so we need to pend the relation until the class
    # is prepared.
    model = get_model(app_label, model_name,
                      seed_cache=False, only_installed=False)
    if model:
        operation(field, model, cls)
    else:
        key = (app_label, model_name)
        value = (cls, field, operation)
        pending_lookups.setdefault(key, []).append(value)


def do_pending_lookups(sender, **kwargs):
    """
    Handle any pending relations to the sending model. Sent from class_prepared.
    """
    key = (sender._meta.app_label, sender.__name__)
    for cls, field, operation in pending_lookups.pop(key, []):
        operation(field, sender, cls)

signals.class_prepared.connect(do_pending_lookups)


#HACK
class RelatedField(Field):
    def db_type(self, connection):
        '''By default related field will not have a column
           as it relates columns to another table'''
        return None

    def contribute_to_class(self, cls, name, virtual_only=False):
        sup = super(RelatedField, self)

        # Store the opts for related_query_name()
        self.opts = cls._meta

        if hasattr(sup, 'contribute_to_class'):
            sup.contribute_to_class(cls, name, virtual_only=virtual_only)

        if not cls._meta.abstract and self.rel.related_name:
            related_name = self.rel.related_name % {
                'class': cls.__name__.lower(),
                'app_label': cls._meta.app_label.lower()
            }
            self.rel.related_name = related_name
        other = self.rel.to
        if isinstance(other, six.string_types) or other._meta.pk is None:
            def resolve_related_class(field, model, cls):
                field.rel.to = model
                field.do_related_class(model, cls)
            add_lazy_relation(cls, self, other, resolve_related_class)
        else:
            self.do_related_class(other, cls)

    def set_attributes_from_rel(self):
        self.name = self.name or (self.rel.to._meta.model_name + '_' + self.rel.to._meta.pk.name)
        if self.verbose_name is None:
            self.verbose_name = self.rel.to._meta.verbose_name
        self.rel.set_field_name()

    def do_related_class(self, other, cls):
        self.set_attributes_from_rel()
        self.related = RelatedObject(other, cls, self)
        if not cls._meta.abstract:
            self.contribute_to_related_class(other, self.related)

    def related_query_name(self):
        # This method defines the name that can be used to identify this
        # related object in a table-spanning query. It uses the lower-cased
        # object_name by default, but this can be overridden with the
        # "related_name" option.
        return self.rel.related_query_name or self.rel.related_name or self.opts.model_name


class RenameRelatedObjectDescriptorMethods(RenameMethodsBase):
    renamed_methods = (
        ('get_query_set', 'get_queryset', PendingDeprecationWarning),
        ('get_prefetch_query_set', 'get_prefetch_queryset', PendingDeprecationWarning),
    )


class SingleRelatedObjectDescriptor(six.with_metaclass(RenameRelatedObjectDescriptorMethods)):
    # This class provides the functionality that makes the related-object
    # managers available as attributes on a model class, for fields that have
    # a single "remote" value, on the class pointed to by a related field.
    # In the example "place.restaurant", the restaurant attribute is a
    # SingleRelatedObjectDescriptor instance.
    def __init__(self, related):
        self.related = related
        self.cache_name = related.get_cache_name()

    def is_cached(self, instance):
        return hasattr(instance, self.cache_name)

    def get_queryset(self, **db_hints):
        db = router.db_for_read(self.related.model, **db_hints)
        return self.related.model._base_manager.using(db)

    def get_prefetch_queryset(self, instances):
        rel_obj_attr = attrgetter(self.related.field.attname)
        instance_attr = lambda obj: obj._get_pk_val()
        instances_dict = dict((instance_attr(inst), inst) for inst in instances)
        query = {'%s__in' % self.related.field.name: instances}
        qs = self.get_queryset(instance=instances[0]).filter(**query)
        # Since we're going to assign directly in the cache,
        # we must manage the reverse relation cache manually.
        rel_obj_cache_name = self.related.field.get_cache_name()
        for rel_obj in qs:
            instance = instances_dict[rel_obj_attr(rel_obj)]
            setattr(rel_obj, rel_obj_cache_name, instance)
        return qs, rel_obj_attr, instance_attr, True, self.cache_name

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        try:
            rel_obj = getattr(instance, self.cache_name)
        except AttributeError:
            related_pk = instance._get_pk_val()
            if related_pk is None:
                rel_obj = None
            else:
                params = {}
                for lh_field, rh_field in self.related.field.related_fields:
                    params['%s__%s' % (self.related.field.name, rh_field.name)] = getattr(instance, rh_field.attname)
                try:
                    rel_obj = self.get_queryset(instance=instance).get(**params)
                except self.related.model.DoesNotExist:
                    rel_obj = None
                else:
                    setattr(rel_obj, self.related.field.get_cache_name(), instance)
            setattr(instance, self.cache_name, rel_obj)
        if rel_obj is None:
            raise self.related.model.DoesNotExist("%s has no %s." % (
                                                  instance.__class__.__name__,
                                                  self.related.get_accessor_name()))
        else:
            return rel_obj

    def __set__(self, instance, value):
        # The similarity of the code below to the code in
        # ReverseSingleRelatedObjectDescriptor is annoying, but there's a bunch
        # of small differences that would make a common base class convoluted.

        # If null=True, we can assign null here, but otherwise the value needs
        # to be an instance of the related class.
        if value is None and self.related.field.null == False:
            raise ValueError('Cannot assign None: "%s.%s" does not allow null values.' %
                                (instance._meta.object_name, self.related.get_accessor_name()))
        elif value is not None and not isinstance(value, self.related.model):
            raise ValueError('Cannot assign "%r": "%s.%s" must be a "%s" instance.' %
                                (value, instance._meta.object_name,
                                 self.related.get_accessor_name(), self.related.opts.object_name))
        elif value is not None:
            if instance._state.db is None:
                instance._state.db = router.db_for_write(instance.__class__, instance=value)
            elif value._state.db is None:
                value._state.db = router.db_for_write(value.__class__, instance=instance)
            elif value._state.db is not None and instance._state.db is not None:
                if not router.allow_relation(value, instance):
                    raise ValueError('Cannot assign "%r": the current database router prevents this relation.' % value)

        related_pk = tuple([getattr(instance, field.attname) for field in self.related.field.foreign_related_fields])
        if None in related_pk:
            raise ValueError('Cannot assign "%r": "%s" instance isn\'t saved in the database.' %
                                (value, instance._meta.object_name))

        # Set the value of the related field to the value of the related object's related field
        for index, field in enumerate(self.related.field.local_related_fields):
            setattr(value, field.attname, related_pk[index])

        # Since we already know what the related object is, seed the related
        # object caches now, too. This avoids another db hit if you get the
        # object you just set.
        setattr(instance, self.cache_name, value)
        setattr(value, self.related.field.get_cache_name(), instance)


class ReverseSingleRelatedObjectDescriptor(six.with_metaclass(RenameRelatedObjectDescriptorMethods)):
    # This class provides the functionality that makes the related-object
    # managers available as attributes on a model class, for fields that have
    # a single "remote" value, on the class that defines the related field.
    # In the example "choice.poll", the poll attribute is a
    # ReverseSingleRelatedObjectDescriptor instance.
    def __init__(self, field_with_rel):
        self.field = field_with_rel
        self.cache_name = self.field.get_cache_name()

    def is_cached(self, instance):
        return hasattr(instance, self.cache_name)

    def get_queryset(self, **db_hints):
        db = router.db_for_read(self.field.rel.to, **db_hints)
        rel_mgr = self.field.rel.to._default_manager
        # If the related manager indicates that it should be used for
        # related fields, respect that.
        if getattr(rel_mgr, 'use_for_related_fields', False):
            return rel_mgr.using(db)
        else:
            return QuerySet(self.field.rel.to).using(db)

    def get_prefetch_queryset(self, instances):
        rel_obj_attr = self.field.get_foreign_related_value
        instance_attr = self.field.get_local_related_value
        instances_dict = dict((instance_attr(inst), inst) for inst in instances)
        related_field = self.field.foreign_related_fields[0]

        # FIXME: This will need to be revisited when we introduce support for
        # composite fields. In the meantime we take this practical approach to
        # solve a regression on 1.6 when the reverse manager in hidden
        # (related_name ends with a '+'). Refs #21410.
        # The check for len(...) == 1 is a special case that allows the query
        # to be join-less and smaller. Refs #21760.
        if self.field.rel.is_hidden() or len(self.field.foreign_related_fields) == 1:
            query = {'%s__in' % related_field.name: set(instance_attr(inst)[0] for inst in instances)}
        else:
            query = {'%s__in' % self.field.related_query_name(): instances}

        qs = self.get_queryset(instance=instances[0]).filter(**query)
        # Since we're going to assign directly in the cache,
        # we must manage the reverse relation cache manually.
        if not self.field.rel.multiple:
            rel_obj_cache_name = self.field.related.get_cache_name()
            for rel_obj in qs:
                instance = instances_dict[rel_obj_attr(rel_obj)]
                setattr(rel_obj, rel_obj_cache_name, instance)
        return qs, rel_obj_attr, instance_attr, True, self.cache_name

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        try:
            rel_obj = getattr(instance, self.cache_name)
        except AttributeError:
            val = self.field.get_local_related_value(instance)
            if None in val:
                rel_obj = None
            else:
                params = dict(
                    (rh_field.attname, getattr(instance, lh_field.attname))
                    for lh_field, rh_field in self.field.related_fields)
                qs = self.get_queryset(instance=instance)
                extra_filter = self.field.get_extra_descriptor_filter(instance)
                if isinstance(extra_filter, dict):
                    params.update(extra_filter)
                    qs = qs.filter(**params)
                else:
                    qs = qs.filter(extra_filter, **params)
                # Assuming the database enforces foreign keys, this won't fail.
                rel_obj = qs.get()
                if not self.field.rel.multiple:
                    setattr(rel_obj, self.field.related.get_cache_name(), instance)
            setattr(instance, self.cache_name, rel_obj)
        if rel_obj is None and not self.field.null:
            raise self.field.rel.to.DoesNotExist(
                "%s has no %s." % (self.field.model.__name__, self.field.name))
        else:
            return rel_obj

    def __set__(self, instance, value):
        # If null=True, we can assign null here, but otherwise the value needs
        # to be an instance of the related class.
        if value is None and self.field.null == False:
            raise ValueError('Cannot assign None: "%s.%s" does not allow null values.' %
                                (instance._meta.object_name, self.field.name))
        elif value is not None and not isinstance(value, self.field.rel.to):
            raise ValueError('Cannot assign "%r": "%s.%s" must be a "%s" instance.' %
                                (value, instance._meta.object_name,
                                 self.field.name, self.field.rel.to._meta.object_name))
        elif value is not None:
            if instance._state.db is None:
                instance._state.db = router.db_for_write(instance.__class__, instance=value)
            elif value._state.db is None:
                value._state.db = router.db_for_write(value.__class__, instance=instance)
            elif value._state.db is not None and instance._state.db is not None:
                if not router.allow_relation(value, instance):
                    raise ValueError('Cannot assign "%r": the current database router prevents this relation.' % value)

        # If we're setting the value of a OneToOneField to None, we need to clear
        # out the cache on any old related object. Otherwise, deleting the
        # previously-related object will also cause this object to be deleted,
        # which is wrong.
        if value is None:
            # Look up the previously-related object, which may still be available
            # since we've not yet cleared out the related field.
            # Use the cache directly, instead of the accessor; if we haven't
            # populated the cache, then we don't care - we're only accessing
            # the object to invalidate the accessor cache, so there's no
            # need to populate the cache just to expire it again.
            related = getattr(instance, self.cache_name, None)

            # If we've got an old related object, we need to clear out its
            # cache. This cache also might not exist if the related object
            # hasn't been accessed yet.
            if related is not None:
                setattr(related, self.field.related.get_cache_name(), None)

        # Set the value of the related field
        for lh_field, rh_field in self.field.related_fields:
            try:
                setattr(instance, lh_field.attname, getattr(value, rh_field.attname))
            except AttributeError:
                setattr(instance, lh_field.attname, None)

        # Since we already know what the related object is, seed the related
        # object caches now, too. This avoids another db hit if you get the
        # object you just set.
        setattr(instance, self.cache_name, value)
        if value is not None and not self.field.rel.multiple:
            setattr(value, self.field.related.get_cache_name(), instance)


class ForeignRelatedObjectsDescriptor(object):
    # This class provides the functionality that makes the related-object
    # managers available as attributes on a model class, for fields that have
    # multiple "remote" values and have a ForeignKey pointed at them by
    # some other model. In the example "poll.choice_set", the choice_set
    # attribute is a ForeignRelatedObjectsDescriptor instance.
    def __init__(self, related):
        self.related = related   # RelatedObject instance

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        return self.related_manager_cls(instance)

    def __set__(self, instance, value):
        manager = self.__get__(instance)
        # If the foreign key can support nulls, then completely clear the related set.
        # Otherwise, just move the named objects into the set.
        if self.related.field.null:
            manager.clear()
        manager.add(*value)

    @cached_property
    def related_manager_cls(self):
        # Dynamically create a class that subclasses the related model's default
        # manager.
        superclass = self.related.model._default_manager.__class__
        rel_field = self.related.field
        rel_model = self.related.model

        class RelatedManager(superclass):
            def __init__(self, instance):
                super(RelatedManager, self).__init__()
                self.instance = instance
                self.core_filters= {'%s__exact' % rel_field.name: instance}
                self.model = rel_model

            def get_queryset(self):
                try:
                    return self.instance._prefetched_objects_cache[rel_field.related_query_name()]
                except (AttributeError, KeyError):
                    db = self._db or router.db_for_read(self.model, instance=self.instance)
                    qs = super(RelatedManager, self).get_queryset().using(db).filter(**self.core_filters)
                    empty_strings_as_null = connections[db].features.interprets_empty_strings_as_nulls
                    for field in rel_field.foreign_related_fields:
                        val = getattr(self.instance, field.attname)
                        if val is None or (val == '' and empty_strings_as_null):
                            return qs.none()
                    qs._known_related_objects = {rel_field: {self.instance.pk: self.instance}}
                    return qs

            def get_prefetch_queryset(self, instances):
                rel_obj_attr = rel_field.get_local_related_value
                instance_attr = rel_field.get_foreign_related_value
                instances_dict = dict((instance_attr(inst), inst) for inst in instances)
                db = self._db or router.db_for_read(self.model, instance=instances[0])
                query = {'%s__in' % rel_field.name: instances}
                qs = super(RelatedManager, self).get_queryset().using(db).filter(**query)
                # Since we just bypassed this class' get_queryset(), we must manage
                # the reverse relation manually.
                for rel_obj in qs:
                    instance = instances_dict[rel_obj_attr(rel_obj)]
                    setattr(rel_obj, rel_field.name, instance)
                cache_name = rel_field.related_query_name()
                return qs, rel_obj_attr, instance_attr, False, cache_name

            def add(self, *objs):
                for obj in objs:
                    if not isinstance(obj, self.model):
                        raise TypeError("'%s' instance expected, got %r" % (self.model._meta.object_name, obj))
                    setattr(obj, rel_field.name, self.instance)
                    obj.save()
            add.alters_data = True

            def create(self, **kwargs):
                kwargs[rel_field.name] = self.instance
                db = router.db_for_write(self.model, instance=self.instance)
                return super(RelatedManager, self.db_manager(db)).create(**kwargs)
            create.alters_data = True

            def get_or_create(self, **kwargs):
                # Update kwargs with the related object that this
                # ForeignRelatedObjectsDescriptor knows about.
                kwargs[rel_field.name] = self.instance
                db = router.db_for_write(self.model, instance=self.instance)
                return super(RelatedManager, self.db_manager(db)).get_or_create(**kwargs)
            get_or_create.alters_data = True

            # remove() and clear() are only provided if the ForeignKey can have a value of null.
            if rel_field.null:
                def remove(self, *objs):
                    val = rel_field.get_foreign_related_value(self.instance)
                    for obj in objs:
                        # Is obj actually part of this descriptor set?
                        if rel_field.get_local_related_value(obj) == val:
                            setattr(obj, rel_field.name, None)
                            obj.save()
                        else:
                            raise rel_field.rel.to.DoesNotExist("%r is not related to %r." % (obj, self.instance))
                remove.alters_data = True

                def clear(self):
                    self.update(**{rel_field.name: None})
                clear.alters_data = True

        return RelatedManager


def create_many_related_manager(superclass, rel):
    """Creates a manager that subclasses 'superclass' (which is a Manager)
    and adds behavior for many-to-many related objects."""
    class ManyRelatedManager(superclass):
        def __init__(self, model=None, query_field_name=None, instance=None, symmetrical=None,
                     source_field_name=None, target_field_name=None, reverse=False,
                     through=None, prefetch_cache_name=None):
            super(ManyRelatedManager, self).__init__()
            self.model = model
            self.query_field_name = query_field_name

            source_field = through._meta.get_field(source_field_name)
            source_related_fields = source_field.related_fields

            self.core_filters = {}
            for lh_field, rh_field in source_related_fields:
                self.core_filters['%s__%s' % (query_field_name, rh_field.name)] = getattr(instance, rh_field.attname)

            self.instance = instance
            self.symmetrical = symmetrical
            self.source_field = source_field
            self.source_field_name = source_field_name
            self.target_field_name = target_field_name
            self.reverse = reverse
            self.through = through
            self.prefetch_cache_name = prefetch_cache_name
            self.related_val = source_field.get_foreign_related_value(instance)
            # Used for single column related auto created models
            self._fk_val = self.related_val[0]
            if None in self.related_val:
                raise ValueError('"%r" needs to have a value for field "%s" before '
                                 'this many-to-many relationship can be used.' %
                                 (instance, source_field_name))
            # Even if this relation is not to pk, we require still pk value.
            # The wish is that the instance has been already saved to DB,
            # although having a pk value isn't a guarantee of that.
            if instance.pk is None:
                raise ValueError("%r instance needs to have a primary key value before "
                                 "a many-to-many relationship can be used." %
                                 instance.__class__.__name__)


        def _get_fk_val(self, obj, field_name):
            """
            Returns the correct value for this relationship's foreign key. This
            might be something else than pk value when to_field is used.
            """
            fk = self.through._meta.get_field(field_name)
            if fk.rel.field_name and fk.rel.field_name != fk.rel.to._meta.pk.attname:
                attname = fk.rel.get_related_field().get_attname()
                return fk.get_prep_lookup('exact', getattr(obj, attname))
            else:
                return obj.pk

        def get_queryset(self):
            try:
                return self.instance._prefetched_objects_cache[self.prefetch_cache_name]
            except (AttributeError, KeyError):
                db = self._db or router.db_for_read(self.instance.__class__, instance=self.instance)
                return super(ManyRelatedManager, self).get_queryset().using(db)._next_is_sticky().filter(**self.core_filters)

        def get_prefetch_queryset(self, instances):
            instance = instances[0]
            db = self._db or router.db_for_read(instance.__class__, instance=instance)
            query = {'%s__in' % self.query_field_name: instances}
            qs = super(ManyRelatedManager, self).get_queryset().using(db)._next_is_sticky().filter(**query)

            # M2M: need to annotate the query in order to get the primary model
            # that the secondary model was actually related to. We know that
            # there will already be a join on the join table, so we can just add
            # the select.

            # For non-autocreated 'through' models, can't assume we are
            # dealing with PK values.
            fk = self.through._meta.get_field(self.source_field_name)
            join_table = self.through._meta.db_table
            connection = connections[db]
            qn = connection.ops.quote_name
            qs = qs.extra(select=dict(
                ('_prefetch_related_val_%s' % f.attname,
                '%s.%s' % (qn(join_table), qn(f.column))) for f in fk.local_related_fields))
            return (qs,
                    lambda result: tuple([getattr(result, '_prefetch_related_val_%s' % f.attname) for f in fk.local_related_fields]),
                    lambda inst: tuple([getattr(inst, f.attname) for f in fk.foreign_related_fields]),
                    False,
                    self.prefetch_cache_name)

        # If the ManyToMany relation has an intermediary model,
        # the add and remove methods do not exist.
        if rel.through._meta.auto_created:
            def add(self, *objs):
                self._add_items(self.source_field_name, self.target_field_name, *objs)

                # If this is a symmetrical m2m relation to self, add the mirror entry in the m2m table
                if self.symmetrical:
                    self._add_items(self.target_field_name, self.source_field_name, *objs)
            add.alters_data = True

            def remove(self, *objs):
                self._remove_items(self.source_field_name, self.target_field_name, *objs)

                # If this is a symmetrical m2m relation to self, remove the mirror entry in the m2m table
                if self.symmetrical:
                    self._remove_items(self.target_field_name, self.source_field_name, *objs)
            remove.alters_data = True

        def clear(self):
            self._clear_items(self.source_field_name)

            # If this is a symmetrical m2m relation to self, clear the mirror entry in the m2m table
            if self.symmetrical:
                self._clear_items(self.target_field_name)
        clear.alters_data = True

        def create(self, **kwargs):
            # This check needs to be done here, since we can't later remove this
            # from the method lookup table, as we do with add and remove.
            if not self.through._meta.auto_created:
                opts = self.through._meta
                raise AttributeError("Cannot use create() on a ManyToManyField which specifies an intermediary model. Use %s.%s's Manager instead." % (opts.app_label, opts.object_name))
            db = router.db_for_write(self.instance.__class__, instance=self.instance)
            new_obj = super(ManyRelatedManager, self.db_manager(db)).create(**kwargs)
            self.add(new_obj)
            return new_obj
        create.alters_data = True

        def get_or_create(self, **kwargs):
            db = router.db_for_write(self.instance.__class__, instance=self.instance)
            obj, created = \
                super(ManyRelatedManager, self.db_manager(db)).get_or_create(**kwargs)
            # We only need to add() if created because if we got an object back
            # from get() then the relationship already exists.
            if created:
                self.add(obj)
            return obj, created
        get_or_create.alters_data = True

        def _add_items(self, source_field_name, target_field_name, *objs):
            # source_field_name: the PK fieldname in join table for the source object
            # target_field_name: the PK fieldname in join table for the target object
            # *objs - objects to add. Either object instances, or primary keys of object instances.

            # If there aren't any objects, there is nothing to do.
            from django.db.models import Model
            if objs:
                new_ids = set()
                for obj in objs:
                    if isinstance(obj, self.model):
                        if not router.allow_relation(obj, self.instance):
                            raise ValueError('Cannot add "%r": instance is on database "%s", value is on database "%s"' %
                                               (obj, self.instance._state.db, obj._state.db))
                        fk_val = self._get_fk_val(obj, target_field_name)
                        if fk_val is None:
                            raise ValueError('Cannot add "%r": the value for field "%s" is None' %
                                             (obj, target_field_name))
                        new_ids.add(self._get_fk_val(obj, target_field_name))
                    elif isinstance(obj, Model):
                        raise TypeError("'%s' instance expected, got %r" % (self.model._meta.object_name, obj))
                    else:
                        new_ids.add(obj)
                db = router.db_for_write(self.through, instance=self.instance)
                vals = self.through._default_manager.using(db).values_list(target_field_name, flat=True)
                vals = vals.filter(**{
                    source_field_name: self._fk_val,
                    '%s__in' % target_field_name: new_ids,
                })
                new_ids = new_ids - set(vals)

                if self.reverse or source_field_name == self.source_field_name:
                    # Don't send the signal when we are inserting the
                    # duplicate data row for symmetrical reverse entries.
                    signals.m2m_changed.send(sender=self.through, action='pre_add',
                        instance=self.instance, reverse=self.reverse,
                        model=self.model, pk_set=new_ids, using=db)
                # Add the ones that aren't there already
                self.through._default_manager.using(db).bulk_create([
                    self.through(**{
                        '%s_id' % source_field_name: self._fk_val,
                        '%s_id' % target_field_name: obj_id,
                    })
                    for obj_id in new_ids
                ])

                if self.reverse or source_field_name == self.source_field_name:
                    # Don't send the signal when we are inserting the
                    # duplicate data row for symmetrical reverse entries.
                    signals.m2m_changed.send(sender=self.through, action='post_add',
                        instance=self.instance, reverse=self.reverse,
                        model=self.model, pk_set=new_ids, using=db)

        def _remove_items(self, source_field_name, target_field_name, *objs):
            # source_field_name: the PK colname in join table for the source object
            # target_field_name: the PK colname in join table for the target object
            # *objs - objects to remove

            # If there aren't any objects, there is nothing to do.
            if objs:
                # Check that all the objects are of the right type
                old_ids = set()
                for obj in objs:
                    if isinstance(obj, self.model):
                        old_ids.add(self._get_fk_val(obj, target_field_name))
                    else:
                        old_ids.add(obj)
                # Work out what DB we're operating on
                db = router.db_for_write(self.through, instance=self.instance)
                # Send a signal to the other end if need be.
                if self.reverse or source_field_name == self.source_field_name:
                    # Don't send the signal when we are deleting the
                    # duplicate data row for symmetrical reverse entries.
                    signals.m2m_changed.send(sender=self.through, action="pre_remove",
                        instance=self.instance, reverse=self.reverse,
                        model=self.model, pk_set=old_ids, using=db)
                # Remove the specified objects from the join table
                self.through._default_manager.using(db).filter(**{
                    source_field_name: self._fk_val,
                    '%s__in' % target_field_name: old_ids
                }).delete()
                if self.reverse or source_field_name == self.source_field_name:
                    # Don't send the signal when we are deleting the
                    # duplicate data row for symmetrical reverse entries.
                    signals.m2m_changed.send(sender=self.through, action="post_remove",
                        instance=self.instance, reverse=self.reverse,
                        model=self.model, pk_set=old_ids, using=db)

        def _clear_items(self, source_field_name):
            db = router.db_for_write(self.through, instance=self.instance)
            # source_field_name: the PK colname in join table for the source object
            if self.reverse or source_field_name == self.source_field_name:
                # Don't send the signal when we are clearing the
                # duplicate data rows for symmetrical reverse entries.
                signals.m2m_changed.send(sender=self.through, action="pre_clear",
                    instance=self.instance, reverse=self.reverse,
                    model=self.model, pk_set=None, using=db)
            self.through._default_manager.using(db).filter(**{
                source_field_name: self.related_val
            }).delete()
            if self.reverse or source_field_name == self.source_field_name:
                # Don't send the signal when we are clearing the
                # duplicate data rows for symmetrical reverse entries.
                signals.m2m_changed.send(sender=self.through, action="post_clear",
                    instance=self.instance, reverse=self.reverse,
                    model=self.model, pk_set=None, using=db)

    return ManyRelatedManager


class ManyRelatedObjectsDescriptor(object):
    # This class provides the functionality that makes the related-object
    # managers available as attributes on a model class, for fields that have
    # multiple "remote" values and have a ManyToManyField pointed at them by
    # some other model (rather than having a ManyToManyField themselves).
    # In the example "publication.article_set", the article_set attribute is a
    # ManyRelatedObjectsDescriptor instance.
    def __init__(self, related):
        self.related = related   # RelatedObject instance

    @cached_property
    def related_manager_cls(self):
        # Dynamically create a class that subclasses the related
        # model's default manager.
        return create_many_related_manager(
            self.related.model._default_manager.__class__,
            self.related.field.rel
        )

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        rel_model = self.related.model

        manager = self.related_manager_cls(
            model=rel_model,
            query_field_name=self.related.field.name,
            prefetch_cache_name=self.related.field.related_query_name(),
            instance=instance,
            symmetrical=False,
            source_field_name=self.related.field.m2m_reverse_field_name(),
            target_field_name=self.related.field.m2m_field_name(),
            reverse=True,
            through=self.related.field.rel.through,
        )

        return manager

    def __set__(self, instance, value):
        if not self.related.field.rel.through._meta.auto_created:
            opts = self.related.field.rel.through._meta
            raise AttributeError("Cannot set values on a ManyToManyField which specifies an intermediary model. Use %s.%s's Manager instead." % (opts.app_label, opts.object_name))

        manager = self.__get__(instance)
        manager.clear()
        manager.add(*value)


class ReverseManyRelatedObjectsDescriptor(object):
    # This class provides the functionality that makes the related-object
    # managers available as attributes on a model class, for fields that have
    # multiple "remote" values and have a ManyToManyField defined in their
    # model (rather than having another model pointed *at* them).
    # In the example "article.publications", the publications attribute is a
    # ReverseManyRelatedObjectsDescriptor instance.
    def __init__(self, m2m_field):
        self.field = m2m_field

    @property
    def through(self):
        # through is provided so that you have easy access to the through
        # model (Book.authors.through) for inlines, etc. This is done as
        # a property to ensure that the fully resolved value is returned.
        return self.field.rel.through

    @cached_property
    def related_manager_cls(self):
        # Dynamically create a class that subclasses the related model's
        # default manager.
        return create_many_related_manager(
            self.field.rel.to._default_manager.__class__,
            self.field.rel
        )

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        manager = self.related_manager_cls(
            model=self.field.rel.to,
            query_field_name=self.field.related_query_name(),
            prefetch_cache_name=self.field.name,
            instance=instance,
            symmetrical=self.field.rel.symmetrical,
            source_field_name=self.field.m2m_field_name(),
            target_field_name=self.field.m2m_reverse_field_name(),
            reverse=False,
            through=self.field.rel.through,
        )

        return manager

    def __set__(self, instance, value):
        if not self.field.rel.through._meta.auto_created:
            opts = self.field.rel.through._meta
            raise AttributeError("Cannot set values on a ManyToManyField which specifies an intermediary model.  Use %s.%s's Manager instead." % (opts.app_label, opts.object_name))

        manager = self.__get__(instance)
        # clear() can change expected output of 'value' queryset, we force evaluation
        # of queryset before clear; ticket #19816
        value = tuple(value)
        manager.clear()
        manager.add(*value)

class ForeignObjectRel(object):
    def __init__(self, field, to, related_name=None, limit_choices_to=None,
                 parent_link=False, on_delete=None, related_query_name=None):
        try:
            to._meta
        except AttributeError:  # to._meta doesn't exist, so it must be RECURSIVE_RELATIONSHIP_CONSTANT
            assert isinstance(to, six.string_types), "'to' must be either a model, a model name or the string %r" % RECURSIVE_RELATIONSHIP_CONSTANT

        self.field = field
        self.to = to
        self.related_name = related_name
        self.related_query_name = related_query_name
        self.limit_choices_to = {} if limit_choices_to is None else limit_choices_to
        self.multiple = True
        self.parent_link = parent_link
        self.on_delete = on_delete

    def is_hidden(self):
        "Should the related object be hidden?"
        return self.related_name and self.related_name[-1] == '+'

    def get_joining_columns(self):
        return self.field.get_reverse_joining_columns()

    def get_extra_restriction(self, where_class, alias, related_alias):
        return self.field.get_extra_restriction(where_class, related_alias, alias)

    def set_field_name(self):
        """
        Sets the related field's name, this is not available until later stages
        of app loading, so set_field_name is called from
        set_attributes_from_rel()
        """
        # By default foreign object doesn't relate to any remote field (for
        # example custom multicolumn joins currently have no remote field).
        self.field_name = None

class ManyToOneRel(ForeignObjectRel):
    def __init__(self, field, to, field_name, related_name=None, limit_choices_to=None,
                 parent_link=False, on_delete=None, related_query_name=None):
        super(ManyToOneRel, self).__init__(
            field, to, related_name=related_name, limit_choices_to=limit_choices_to,
            parent_link=parent_link, on_delete=on_delete, related_query_name=related_query_name)
        self.field_name = field_name

    def get_related_field(self):
        """
        Returns the Field in the 'to' object to which this relationship is
        tied.
        """
        data = self.to._meta.get_field_by_name(self.field_name)
        if not data[2]:
            raise FieldDoesNotExist("No related field named '%s'" %
                    self.field_name)
        return data[0]

    def set_field_name(self):
        self.field_name = self.field_name or self.to._meta.pk.name


class OneToOneRel(ManyToOneRel):
    def __init__(self, field, to, field_name, related_name=None, limit_choices_to=None,
                 parent_link=False, on_delete=None, related_query_name=None):
        super(OneToOneRel, self).__init__(field, to, field_name,
                related_name=related_name, limit_choices_to=limit_choices_to,
                parent_link=parent_link, on_delete=on_delete, related_query_name=related_query_name,
        )
        self.multiple = False


class ManyToManyRel(object):
    def __init__(self, to, related_name=None, limit_choices_to=None,
                 symmetrical=True, through=None, db_constraint=True, related_query_name=None):
        if through and not db_constraint:
            raise ValueError("Can't supply a through model and db_constraint=False")
        self.to = to
        self.related_name = related_name
        self.related_query_name = related_query_name
        if limit_choices_to is None:
            limit_choices_to = {}
        self.limit_choices_to = limit_choices_to
        self.symmetrical = symmetrical
        self.multiple = True
        self.through = through
        self.db_constraint = db_constraint

    def is_hidden(self):
        "Should the related object be hidden?"
        return self.related_name and self.related_name[-1] == '+'

    def get_related_field(self):
        """
        Returns the field in the to' object to which this relationship is tied
        (this is always the primary key on the target model). Provided for
        symmetry with ManyToOneRel.
        """
        return self.to._meta.pk


class ForeignObject(RelatedField):
    requires_unique_target = True
    generate_reverse_relation = True

    def __init__(self, to, from_fields, to_fields, **kwargs):
        self.from_fields = from_fields
        self.to_fields = to_fields

        if 'rel' not in kwargs:
            kwargs['rel'] = ForeignObjectRel(
                self, to,
                related_name=kwargs.pop('related_name', None),
                related_query_name=kwargs.pop('related_query_name', None),
                limit_choices_to=kwargs.pop('limit_choices_to', None),
                parent_link=kwargs.pop('parent_link', False),
                on_delete=kwargs.pop('on_delete', CASCADE),
            )
        kwargs['verbose_name'] = kwargs.get('verbose_name', None)

        super(ForeignObject, self).__init__(**kwargs)

    def resolve_related_fields(self):
        if len(self.from_fields) < 1 or len(self.from_fields) != len(self.to_fields):
            raise ValueError('Foreign Object from and to fields must be the same non-zero length')
        related_fields = []
        for index in range(len(self.from_fields)):
            from_field_name = self.from_fields[index]
            to_field_name = self.to_fields[index]
            from_field = (self if from_field_name == 'self'
                          else self.opts.get_field_by_name(from_field_name)[0])
            to_field = (self.rel.to._meta.pk if to_field_name is None
                        else self.rel.to._meta.get_field_by_name(to_field_name)[0])
            related_fields.append((from_field, to_field))
        return related_fields

    @property
    def related_fields(self):
        if not hasattr(self, '_related_fields'):
            self._related_fields = self.resolve_related_fields()
        return self._related_fields

    @property
    def reverse_related_fields(self):
        return [(rhs_field, lhs_field) for lhs_field, rhs_field in self.related_fields]

    @property
    def local_related_fields(self):
        return tuple([lhs_field for lhs_field, rhs_field in self.related_fields])

    @property
    def foreign_related_fields(self):
        return tuple([rhs_field for lhs_field, rhs_field in self.related_fields])

    def get_local_related_value(self, instance):
        return self.get_instance_value_for_fields(instance, self.local_related_fields)

    def get_foreign_related_value(self, instance):
        return self.get_instance_value_for_fields(instance, self.foreign_related_fields)

    @staticmethod
    def get_instance_value_for_fields(instance, fields):
        ret = []
        for field in fields:
            # Gotcha: in some cases (like fixture loading) a model can have
            # different values in parent_ptr_id and parent's id. So, use
            # instance.pk (that is, parent_ptr_id) when asked for instance.id.
            if field.primary_key:
                ret.append(instance.pk)
            else:
                ret.append(getattr(instance, field.attname))
        return tuple(ret)

    def get_attname_column(self):
        attname, column = super(ForeignObject, self).get_attname_column()
        return attname, None

    def get_joining_columns(self, reverse_join=False):
        source = self.reverse_related_fields if reverse_join else self.related_fields
        return tuple([(lhs_field.column, rhs_field.column) for lhs_field, rhs_field in source])

    def get_reverse_joining_columns(self):
        return self.get_joining_columns(reverse_join=True)

    def get_extra_descriptor_filter(self, instance):
        """
        Returns an extra filter condition for related object fetching when
        user does 'instance.fieldname', that is the extra filter is used in
        the descriptor of the field.

        The filter should be either a dict usable in .filter(**kwargs) call or
        a Q-object. The condition will be ANDed together with the relation's
        joining columns.

        A parallel method is get_extra_restriction() which is used in
        JOIN and subquery conditions.
        """
        return {}

    def get_extra_restriction(self, where_class, alias, related_alias):
        """
        Returns a pair condition used for joining and subquery pushdown. The
        condition is something that responds to as_sql(qn, connection) method.

        Note that currently referring both the 'alias' and 'related_alias'
        will not work in some conditions, like subquery pushdown.

        A parallel method is get_extra_descriptor_filter() which is used in
        instance.fieldname related object fetching.
        """
        return None

    def get_path_info(self):
        """
        Get path from this field to the related model.
        """
        opts = self.rel.to._meta
        from_opts = self.model._meta
        return [PathInfo(from_opts, opts, self.foreign_related_fields, self, False, True)]

    def get_reverse_path_info(self):
        """
        Get path from the related model to this field's model.
        """
        opts = self.model._meta
        from_opts = self.rel.to._meta
        pathinfos = [PathInfo(from_opts, opts, (opts.pk,), self.rel, not self.unique, False)]
        return pathinfos

    def get_lookup_constraint(self, constraint_class, alias, targets, sources, lookup_type,
                              raw_value):
        from django.db.models.sql.where import SubqueryConstraint, Constraint, AND, OR
        root_constraint = constraint_class()
        assert len(targets) == len(sources)

        def get_normalized_value(value):

            from django.db.models import Model
            if isinstance(value, Model):
                value_list = []
                for source in sources:
                    # Account for one-to-one relations when sent a different model
                    while not isinstance(value, source.model) and source.rel:
                        source = source.rel.to._meta.get_field(source.rel.field_name)
                    value_list.append(getattr(value, source.attname))
                return tuple(value_list)
            elif not isinstance(value, tuple):
                return (value,)
            return value

        is_multicolumn = len(self.related_fields) > 1
        if (hasattr(raw_value, '_as_sql') or
                hasattr(raw_value, 'get_compiler')):
            root_constraint.add(SubqueryConstraint(alias, [target.column for target in targets],
                                                   [source.name for source in sources], raw_value),
                                AND)
        elif lookup_type == 'isnull':
            root_constraint.add(
                (Constraint(alias, targets[0].column, targets[0]), lookup_type, raw_value), AND)
        elif (lookup_type == 'exact' or (lookup_type in ['gt', 'lt', 'gte', 'lte']
                                         and not is_multicolumn)):
            value = get_normalized_value(raw_value)
            for index, source in enumerate(sources):
                root_constraint.add(
                    (Constraint(alias, targets[index].column, sources[index]), lookup_type,
                     value[index]), AND)
        elif lookup_type in ['range', 'in'] and not is_multicolumn:
            values = [get_normalized_value(value) for value in raw_value]
            value = [val[0] for val in values]
            root_constraint.add(
                (Constraint(alias, targets[0].column, sources[0]), lookup_type, value), AND)
        elif lookup_type == 'in':
            values = [get_normalized_value(value) for value in raw_value]
            for value in values:
                value_constraint = constraint_class()
                for index, target in enumerate(targets):
                    value_constraint.add(
                        (Constraint(alias, target.column, sources[index]), 'exact', value[index]),
                        AND)
                root_constraint.add(value_constraint, OR)
        else:
            raise TypeError('Related Field got invalid lookup: %s' % lookup_type)
        return root_constraint

    @property
    def attnames(self):
        return tuple([field.attname for field in self.local_related_fields])

    def get_defaults(self):
        return tuple([field.get_default() for field in self.local_related_fields])

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(ForeignObject, self).contribute_to_class(cls, name, virtual_only=virtual_only)
        setattr(cls, self.name, ReverseSingleRelatedObjectDescriptor(self))

    def contribute_to_related_class(self, cls, related):
        # Internal FK's - i.e., those with a related name ending with '+' -
        # and swapped models don't get a related descriptor.
        if not self.rel.is_hidden() and not related.model._meta.swapped:
            setattr(cls, related.get_accessor_name(), ForeignRelatedObjectsDescriptor(related))
            if self.rel.limit_choices_to:
                cls._meta.related_fkey_lookups.append(self.rel.limit_choices_to)


class ForeignKey(ForeignObject):
    empty_strings_allowed = False
    default_error_messages = {
        'invalid': _('%(model)s instance with pk %(pk)r does not exist.')
    }
    description = _("Foreign Key (type determined by related field)")

    def __init__(self, to, to_field=None, rel_class=ManyToOneRel,
                 db_constraint=True, **kwargs):
        try:
            to_name = to._meta.object_name.lower()
        except AttributeError:  # to._meta doesn't exist, so it must be RECURSIVE_RELATIONSHIP_CONSTANT
            assert isinstance(to, six.string_types), "%s(%r) is invalid. First parameter to ForeignKey must be either a model, a model name, or the string %r" % (self.__class__.__name__, to, RECURSIVE_RELATIONSHIP_CONSTANT)
        else:
            assert not to._meta.abstract, "%s cannot define a relation with abstract class %s" % (self.__class__.__name__, to._meta.object_name)
            # For backwards compatibility purposes, we need to *try* and set
            # the to_field during FK construction. It won't be guaranteed to
            # be correct until contribute_to_class is called. Refs #12190.
            to_field = to_field or (to._meta.pk and to._meta.pk.name)

        if 'db_index' not in kwargs:
            kwargs['db_index'] = True

        self.db_constraint = db_constraint

        kwargs['rel'] = rel_class(
            self, to, to_field,
            related_name=kwargs.pop('related_name', None),
            related_query_name=kwargs.pop('related_query_name', None),
            limit_choices_to=kwargs.pop('limit_choices_to', None),
            parent_link=kwargs.pop('parent_link', False),
            on_delete=kwargs.pop('on_delete', CASCADE),
        )
        super(ForeignKey, self).__init__(to, ['self'], [to_field], **kwargs)

    @property
    def related_field(self):
        return self.foreign_related_fields[0]

    def get_reverse_path_info(self):
        """
        Get path from the related model to this field's model.
        """
        opts = self.model._meta
        from_opts = self.rel.to._meta
        pathinfos = [PathInfo(from_opts, opts, (opts.pk,), self.rel, not self.unique, False)]
        return pathinfos

    def validate(self, value, model_instance):
        if self.rel.parent_link:
            return
        super(ForeignKey, self).validate(value, model_instance)
        if value is None:
            return

        using = router.db_for_read(model_instance.__class__, instance=model_instance)
        qs = self.rel.to._default_manager.using(using).filter(
                **{self.rel.field_name: value}
             )
        qs = qs.complex_filter(self.rel.limit_choices_to)
        if not qs.exists():
            raise exceptions.ValidationError(
                self.error_messages['invalid'],
                code='invalid',
                params={'model': self.rel.to._meta.verbose_name, 'pk': value},
            )

    def get_attname(self):
        return '%s_id' % self.name

    def get_attname_column(self):
        attname = self.get_attname()
        column = self.db_column or attname
        return attname, column

    def get_validator_unique_lookup_type(self):
        return '%s__%s__exact' % (self.name, self.related_field.name)

    def get_default(self):
        "Here we check if the default value is an object and return the to_field if so."
        field_default = super(ForeignKey, self).get_default()
        if isinstance(field_default, self.rel.to):
            return getattr(field_default, self.related_field.attname)
        return field_default

    def get_db_prep_save(self, value, connection):
        if value == '' or value == None:
            return None
        else:
            return self.related_field.get_db_prep_save(value,
                connection=connection)

    def value_to_string(self, obj):
        if not obj:
            # In required many-to-one fields with only one available choice,
            # select that one available choice. Note: For SelectFields
            # we have to check that the length of choices is *2*, not 1,
            # because SelectFields always have an initial "blank" value.
            if not self.blank and self.choices:
                choice_list = self.get_choices_default()
                if len(choice_list) == 2:
                    return smart_text(choice_list[1][0])
        return super(ForeignKey, self).value_to_string(obj)

    def contribute_to_related_class(self, cls, related):
        super(ForeignKey, self).contribute_to_related_class(cls, related)
        if self.rel.field_name is None:
            self.rel.field_name = cls._meta.pk.name

    def formfield(self, **kwargs):
        db = kwargs.pop('using', None)
        if isinstance(self.rel.to, six.string_types):
            raise ValueError("Cannot create form field for %r yet, because "
                             "its related model %r has not been loaded yet" %
                             (self.name, self.rel.to))
        defaults = {
            'form_class': forms.ModelChoiceField,
            'queryset': self.rel.to._default_manager.using(db).complex_filter(self.rel.limit_choices_to),
            'to_field_name': self.rel.field_name,
        }
        defaults.update(kwargs)
        return super(ForeignKey, self).formfield(**defaults)

    def db_type(self, connection):
        # The database column type of a ForeignKey is the column type
        # of the field to which it points. An exception is if the ForeignKey
        # points to an AutoField/PositiveIntegerField/PositiveSmallIntegerField,
        # in which case the column type is simply that of an IntegerField.
        # If the database needs similar types for key fields however, the only
        # thing we can do is making AutoField an IntegerField.
        rel_field = self.related_field
        if (isinstance(rel_field, AutoField) or
                (not connection.features.related_fields_match_type and
                isinstance(rel_field, (PositiveIntegerField,
                                       PositiveSmallIntegerField)))):
            return IntegerField().db_type(connection=connection)
        return rel_field.db_type(connection=connection)


class OneToOneField(ForeignKey):
    """
    A OneToOneField is essentially the same as a ForeignKey, with the exception
    that always carries a "unique" constraint with it and the reverse relation
    always returns the object pointed to (since there will only ever be one),
    rather than returning a list.
    """
    description = _("One-to-one relationship")

    def __init__(self, to, to_field=None, **kwargs):
        kwargs['unique'] = True
        super(OneToOneField, self).__init__(to, to_field, OneToOneRel, **kwargs)

    def contribute_to_related_class(self, cls, related):
        setattr(cls, related.get_accessor_name(),
                SingleRelatedObjectDescriptor(related))

    def formfield(self, **kwargs):
        if self.rel.parent_link:
            return None
        return super(OneToOneField, self).formfield(**kwargs)

    def save_form_data(self, instance, data):
        if isinstance(data, self.rel.to):
            setattr(instance, self.name, data)
        else:
            setattr(instance, self.attname, data)


def create_many_to_many_intermediary_model(field, klass):
    from django.db import models
    managed = True
    if isinstance(field.rel.to, six.string_types) and field.rel.to != RECURSIVE_RELATIONSHIP_CONSTANT:
        to_model = field.rel.to
        to = to_model.split('.')[-1]

        def set_managed(field, model, cls):
            field.rel.through._meta.managed = model._meta.managed or cls._meta.managed
        add_lazy_relation(klass, field, to_model, set_managed)
    elif isinstance(field.rel.to, six.string_types):
        to = klass._meta.object_name
        to_model = klass
        managed = klass._meta.managed
    else:
        to = field.rel.to._meta.object_name
        to_model = field.rel.to
        managed = klass._meta.managed or to_model._meta.managed
    name = '%s_%s' % (klass._meta.object_name, field.name)
    if field.rel.to == RECURSIVE_RELATIONSHIP_CONSTANT or to == klass._meta.object_name:
        from_ = 'from_%s' % to.lower()
        to = 'to_%s' % to.lower()
    else:
        from_ = klass._meta.model_name
        to = to.lower()
    meta = type('Meta', (object,), {
        'db_table': field._get_m2m_db_table(klass._meta),
        'managed': managed,
        'auto_created': klass,
        'app_label': klass._meta.app_label,
        'db_tablespace': klass._meta.db_tablespace,
        'unique_together': (from_, to),
        'verbose_name': '%(from)s-%(to)s relationship' % {'from': from_, 'to': to},
        'verbose_name_plural': '%(from)s-%(to)s relationships' % {'from': from_, 'to': to},
    })
    # Construct and return the new class.
    return type(str(name), (models.Model,), {
        'Meta': meta,
        '__module__': klass.__module__,
        from_: models.ForeignKey(klass, related_name='%s+' % name, db_tablespace=field.db_tablespace, db_constraint=field.rel.db_constraint),
        to: models.ForeignKey(to_model, related_name='%s+' % name, db_tablespace=field.db_tablespace, db_constraint=field.rel.db_constraint)
    })


class ManyToManyField(RelatedField):
    description = _("Many-to-many relationship")

    def __init__(self, to, db_constraint=True, **kwargs):
        try:
            assert not to._meta.abstract, "%s cannot define a relation with abstract class %s" % (self.__class__.__name__, to._meta.object_name)
        except AttributeError:  # to._meta doesn't exist, so it must be RECURSIVE_RELATIONSHIP_CONSTANT
            assert isinstance(to, six.string_types), "%s(%r) is invalid. First parameter to ManyToManyField must be either a model, a model name, or the string %r" % (self.__class__.__name__, to, RECURSIVE_RELATIONSHIP_CONSTANT)
            # Python 2.6 and earlier require dictionary keys to be of str type,
            # not unicode and class names must be ASCII (in Python 2.x), so we
            # forcibly coerce it here (breaks early if there's a problem).
            to = str(to)

        kwargs['verbose_name'] = kwargs.get('verbose_name', None)
        kwargs['rel'] = ManyToManyRel(to,
            related_name=kwargs.pop('related_name', None),
            related_query_name=kwargs.pop('related_query_name', None),
            limit_choices_to=kwargs.pop('limit_choices_to', None),
            symmetrical=kwargs.pop('symmetrical', to == RECURSIVE_RELATIONSHIP_CONSTANT),
            through=kwargs.pop('through', None),
            db_constraint=db_constraint,
        )

        self.db_table = kwargs.pop('db_table', None)
        if kwargs['rel'].through is not None:
            assert self.db_table is None, "Cannot specify a db_table if an intermediary model is used."

        super(ManyToManyField, self).__init__(**kwargs)

    def _get_path_info(self, direct=False):
        """
        Called by both direct and indirect m2m traversal.
        """
        pathinfos = []
        int_model = self.rel.through
        linkfield1 = int_model._meta.get_field_by_name(self.m2m_field_name())[0]
        linkfield2 = int_model._meta.get_field_by_name(self.m2m_reverse_field_name())[0]
        if direct:
            join1infos = linkfield1.get_reverse_path_info()
            join2infos = linkfield2.get_path_info()
        else:
            join1infos = linkfield2.get_reverse_path_info()
            join2infos = linkfield1.get_path_info()
        pathinfos.extend(join1infos)
        pathinfos.extend(join2infos)
        return pathinfos

    def get_path_info(self):
        return self._get_path_info(direct=True)

    def get_reverse_path_info(self):
        return self._get_path_info(direct=False)

    def get_choices_default(self):
        return Field.get_choices(self, include_blank=False)

    def _get_m2m_db_table(self, opts):
        "Function that can be curried to provide the m2m table name for this relation"
        if self.rel.through is not None:
            return self.rel.through._meta.db_table
        elif self.db_table:
            return self.db_table
        else:
            return util.truncate_name('%s_%s' % (opts.db_table, self.name),
                                      connection.ops.max_name_length())

    def _get_m2m_attr(self, related, attr):
        "Function that can be curried to provide the source accessor or DB column name for the m2m table"
        cache_attr = '_m2m_%s_cache' % attr
        if hasattr(self, cache_attr):
            return getattr(self, cache_attr)
        for f in self.rel.through._meta.fields:
            if hasattr(f, 'rel') and f.rel and f.rel.to == related.model:
                setattr(self, cache_attr, getattr(f, attr))
                return getattr(self, cache_attr)

    def _get_m2m_reverse_attr(self, related, attr):
        "Function that can be curried to provide the related accessor or DB column name for the m2m table"
        cache_attr = '_m2m_reverse_%s_cache' % attr
        if hasattr(self, cache_attr):
            return getattr(self, cache_attr)
        found = False
        for f in self.rel.through._meta.fields:
            if hasattr(f, 'rel') and f.rel and f.rel.to == related.parent_model:
                if related.model == related.parent_model:
                    # If this is an m2m-intermediate to self,
                    # the first foreign key you find will be
                    # the source column. Keep searching for
                    # the second foreign key.
                    if found:
                        setattr(self, cache_attr, getattr(f, attr))
                        break
                    else:
                        found = True
                else:
                    setattr(self, cache_attr, getattr(f, attr))
                    break
        return getattr(self, cache_attr)

    def value_to_string(self, obj):
        data = ''
        if obj:
            qs = getattr(obj, self.name).all()
            data = [instance._get_pk_val() for instance in qs]
        else:
            # In required many-to-many fields with only one available choice,
            # select that one available choice.
            if not self.blank:
                choices_list = self.get_choices_default()
                if len(choices_list) == 1:
                    data = [choices_list[0][0]]
        return smart_text(data)

    def contribute_to_class(self, cls, name):
        # To support multiple relations to self, it's useful to have a non-None
        # related name on symmetrical relations for internal reasons. The
        # concept doesn't make a lot of sense externally ("you want me to
        # specify *what* on my non-reversible relation?!"), so we set it up
        # automatically. The funky name reduces the chance of an accidental
        # clash.
        if self.rel.symmetrical and (self.rel.to == "self" or self.rel.to == cls._meta.object_name):
            self.rel.related_name = "%s_rel_+" % name

        super(ManyToManyField, self).contribute_to_class(cls, name)

        # The intermediate m2m model is not auto created if:
        #  1) There is a manually specified intermediate, or
        #  2) The class owning the m2m field is abstract.
        #  3) The class owning the m2m field has been swapped out.
        if not self.rel.through and not cls._meta.abstract and not cls._meta.swapped:
            self.rel.through = create_many_to_many_intermediary_model(self, cls)

        # Add the descriptor for the m2m relation
        setattr(cls, self.name, ReverseManyRelatedObjectsDescriptor(self))

        # Set up the accessor for the m2m table name for the relation
        self.m2m_db_table = curry(self._get_m2m_db_table, cls._meta)

        # Populate some necessary rel arguments so that cross-app relations
        # work correctly.
        if isinstance(self.rel.through, six.string_types):
            def resolve_through_model(field, model, cls):
                field.rel.through = model
            add_lazy_relation(cls, self, self.rel.through, resolve_through_model)

    def contribute_to_related_class(self, cls, related):
        # Internal M2Ms (i.e., those with a related name ending with '+')
        # and swapped models don't get a related descriptor.
        if not self.rel.is_hidden() and not related.model._meta.swapped:
            setattr(cls, related.get_accessor_name(), ManyRelatedObjectsDescriptor(related))

        # Set up the accessors for the column names on the m2m table
        self.m2m_column_name = curry(self._get_m2m_attr, related, 'column')
        self.m2m_reverse_name = curry(self._get_m2m_reverse_attr, related, 'column')

        self.m2m_field_name = curry(self._get_m2m_attr, related, 'name')
        self.m2m_reverse_field_name = curry(self._get_m2m_reverse_attr, related, 'name')

        get_m2m_rel = curry(self._get_m2m_attr, related, 'rel')
        self.m2m_target_field_name = lambda: get_m2m_rel().field_name
        get_m2m_reverse_rel = curry(self._get_m2m_reverse_attr, related, 'rel')
        self.m2m_reverse_target_field_name = lambda: get_m2m_reverse_rel().field_name

    def set_attributes_from_rel(self):
        pass

    def value_from_object(self, obj):
        "Returns the value of this field in the given model instance."
        return getattr(obj, self.attname).all()

    def save_form_data(self, instance, data):
        setattr(instance, self.attname, data)

    def formfield(self, **kwargs):
        db = kwargs.pop('using', None)
        defaults = {
            'form_class': forms.ModelMultipleChoiceField,
            'queryset': self.rel.to._default_manager.using(db).complex_filter(self.rel.limit_choices_to)
        }
        defaults.update(kwargs)
        # If initial is passed in, it's a list of related objects, but the
        # MultipleChoiceField takes a list of IDs.
        if defaults.get('initial') is not None:
            initial = defaults['initial']
            if callable(initial):
                initial = initial()
            defaults['initial'] = [i._get_pk_val() for i in initial]
        return super(ManyToManyField, self).formfield(**defaults)
