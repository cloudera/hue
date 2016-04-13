import collections
import sys

from django.conf import settings
from django.core.management.color import color_style
from django.utils.encoding import force_str
from django.utils.itercompat import is_iterable
from django.utils import six


class ModelErrorCollection:
    def __init__(self, outfile=sys.stdout):
        self.errors = []
        self.outfile = outfile
        self.style = color_style()

    def add(self, context, error):
        self.errors.append((context, error))
        self.outfile.write(self.style.ERROR(force_str("%s: %s\n" % (context, error))))


def get_validation_errors(outfile, app=None):
    """
    Validates all models that are part of the specified app. If no app name is provided,
    validates all models of all installed apps. Writes errors, if any, to outfile.
    Returns number of errors.
    """
    from django.db import models, connection
    from django.db.models.loading import get_app_errors
    from django.db.models.deletion import SET_NULL, SET_DEFAULT

    e = ModelErrorCollection(outfile)

    for (app_name, error) in get_app_errors().items():
        e.add(app_name, error)

    for cls in models.get_models(app, include_swapped=True):
        opts = cls._meta

        # Check swappable attribute.
        if opts.swapped:
            try:
                app_label, model_name = opts.swapped.split('.')
            except ValueError:
                e.add(opts, "%s is not of the form 'app_label.app_name'." % opts.swappable)
                continue
            if not models.get_model(app_label, model_name):
                e.add(opts, "Model has been swapped out for '%s' which has not been installed or is abstract." % opts.swapped)
            # No need to perform any other validation checks on a swapped model.
            continue

        # If this is the current User model, check known validation problems with User models
        if settings.AUTH_USER_MODEL == '%s.%s' % (opts.app_label, opts.object_name):
            # Check that REQUIRED_FIELDS is a list
            if not isinstance(cls.REQUIRED_FIELDS, (list, tuple)):
                e.add(opts, 'The REQUIRED_FIELDS must be a list or tuple.')

            # Check that the USERNAME FIELD isn't included in REQUIRED_FIELDS.
            if cls.USERNAME_FIELD in cls.REQUIRED_FIELDS:
                e.add(opts, 'The field named as the USERNAME_FIELD should not be included in REQUIRED_FIELDS on a swappable User model.')

            # Check that the username field is unique
            if not opts.get_field(cls.USERNAME_FIELD).unique:
                e.add(opts, 'The USERNAME_FIELD must be unique. Add unique=True to the field parameters.')

        # Model isn't swapped; do field-specific validation.
        for f in opts.local_fields:
            if f.name == 'id' and not f.primary_key and opts.pk.name == 'id':
                e.add(opts, '"%s": You can\'t use "id" as a field name, because each model automatically gets an "id" field if none of the fields have primary_key=True. You need to either remove/rename your "id" field or add primary_key=True to a field.' % f.name)
            if f.name.endswith('_'):
                e.add(opts, '"%s": Field names cannot end with underscores, because this would lead to ambiguous queryset filters.' % f.name)
            if (f.primary_key and f.null and
                    not connection.features.interprets_empty_strings_as_nulls):
                # We cannot reliably check this for backends like Oracle which
                # consider NULL and '' to be equal (and thus set up
                # character-based fields a little differently).
                e.add(opts, '"%s": Primary key fields cannot have null=True.' % f.name)
            if isinstance(f, models.CharField):
                try:
                    max_length = int(f.max_length)
                    if max_length <= 0:
                        e.add(opts, '"%s": CharFields require a "max_length" attribute that is a positive integer.' % f.name)
                except (ValueError, TypeError):
                    e.add(opts, '"%s": CharFields require a "max_length" attribute that is a positive integer.' % f.name)
            if isinstance(f, models.DecimalField):
                decimalp_ok, mdigits_ok = False, False
                decimalp_msg = '"%s": DecimalFields require a "decimal_places" attribute that is a non-negative integer.'
                try:
                    decimal_places = int(f.decimal_places)
                    if decimal_places < 0:
                        e.add(opts, decimalp_msg % f.name)
                    else:
                        decimalp_ok = True
                except (ValueError, TypeError):
                    e.add(opts, decimalp_msg % f.name)
                mdigits_msg = '"%s": DecimalFields require a "max_digits" attribute that is a positive integer.'
                try:
                    max_digits = int(f.max_digits)
                    if max_digits <= 0:
                        e.add(opts,  mdigits_msg % f.name)
                    else:
                        mdigits_ok = True
                except (ValueError, TypeError):
                    e.add(opts, mdigits_msg % f.name)
                invalid_values_msg = '"%s": DecimalFields require a "max_digits" attribute value that is greater than or equal to the value of the "decimal_places" attribute.'
                if decimalp_ok and mdigits_ok:
                    if decimal_places > max_digits:
                        e.add(opts, invalid_values_msg % f.name)
            if isinstance(f, models.FileField) and not f.upload_to:
                e.add(opts, '"%s": FileFields require an "upload_to" attribute.' % f.name)
            if isinstance(f, models.ImageField):
                try:
                    from django.utils.image import Image
                except ImportError:
                    e.add(opts, '"%s": To use ImageFields, you need to install Pillow. Get it at https://pypi.python.org/pypi/Pillow.' % f.name)
            if isinstance(f, models.BooleanField) and getattr(f, 'null', False):
                e.add(opts, '"%s": BooleanFields do not accept null values. Use a NullBooleanField instead.' % f.name)
            if isinstance(f, models.FilePathField) and not (f.allow_files or f.allow_folders):
                e.add(opts, '"%s": FilePathFields must have either allow_files or allow_folders set to True.' % f.name)
            if isinstance(f, models.GenericIPAddressField) and not getattr(f, 'null', False) and getattr(f, 'blank', False):
                e.add(opts, '"%s": GenericIPAddressField can not accept blank values if null values are not allowed, as blank values are stored as null.' % f.name)
            if f.choices:
                if isinstance(f.choices, six.string_types) or not is_iterable(f.choices):
                    e.add(opts, '"%s": "choices" should be iterable (e.g., a tuple or list).' % f.name)
                else:
                    for c in f.choices:
                        if isinstance(c, six.string_types) or not is_iterable(c) or len(c) != 2:
                            e.add(opts, '"%s": "choices" should be a sequence of two-item iterables (e.g. list of 2 item tuples).' % f.name)
            if f.db_index not in (None, True, False):
                e.add(opts, '"%s": "db_index" should be either None, True or False.' % f.name)

            # Perform any backend-specific field validation.
            connection.validation.validate_field(e, opts, f)

            # Check if the on_delete behavior is sane
            if f.rel and hasattr(f.rel, 'on_delete'):
                if f.rel.on_delete == SET_NULL and not f.null:
                    e.add(opts, "'%s' specifies on_delete=SET_NULL, but cannot be null." % f.name)
                elif f.rel.on_delete == SET_DEFAULT and not f.has_default():
                    e.add(opts, "'%s' specifies on_delete=SET_DEFAULT, but has no default value." % f.name)

            # Check to see if the related field will clash with any existing
            # fields, m2m fields, m2m related objects or related objects
            if f.rel:
                if f.rel.to not in models.get_models():
                    # If the related model is swapped, provide a hint;
                    # otherwise, the model just hasn't been installed.
                    if not isinstance(f.rel.to, six.string_types) and f.rel.to._meta.swapped:
                        e.add(opts, "'%s' defines a relation with the model '%s.%s', which has been swapped out. Update the relation to point at settings.%s." % (f.name, f.rel.to._meta.app_label, f.rel.to._meta.object_name, f.rel.to._meta.swappable))
                    else:
                        e.add(opts, "'%s' has a relation with model %s, which has either not been installed or is abstract." % (f.name, f.rel.to))
                # it is a string and we could not find the model it refers to
                # so skip the next section
                if isinstance(f.rel.to, six.string_types):
                    continue

                # Make sure the related field specified by a ForeignKey is unique
                if f.requires_unique_target:
                    if len(f.foreign_related_fields) > 1:
                        has_unique_field = False
                        for rel_field in f.foreign_related_fields:
                            has_unique_field = has_unique_field or rel_field.unique
                        if not has_unique_field:
                            e.add(opts, "Field combination '%s' under model '%s' must have a unique=True constraint" % (','.join([rel_field.name for rel_field in f.foreign_related_fields]), f.rel.to.__name__))
                    else:
                        if not f.foreign_related_fields[0].unique:
                            e.add(opts, "Field '%s' under model '%s' must have a unique=True constraint." % (f.foreign_related_fields[0].name, f.rel.to.__name__))

                rel_opts = f.rel.to._meta
                rel_name = f.related.get_accessor_name()
                rel_query_name = f.related_query_name()
                if not f.rel.is_hidden():
                    for r in rel_opts.fields:
                        if r.name == rel_name:
                            e.add(opts, "Accessor for field '%s' clashes with field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.name, f.name))
                        if r.name == rel_query_name:
                            e.add(opts, "Reverse query name for field '%s' clashes with field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.name, f.name))
                    for r in rel_opts.local_many_to_many:
                        if r.name == rel_name:
                            e.add(opts, "Accessor for field '%s' clashes with m2m field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.name, f.name))
                        if r.name == rel_query_name:
                            e.add(opts, "Reverse query name for field '%s' clashes with m2m field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.name, f.name))
                    for r in rel_opts.get_all_related_many_to_many_objects():
                        if r.get_accessor_name() == rel_name:
                            e.add(opts, "Accessor for field '%s' clashes with related m2m field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.get_accessor_name(), f.name))
                        if r.get_accessor_name() == rel_query_name:
                            e.add(opts, "Reverse query name for field '%s' clashes with related m2m field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.get_accessor_name(), f.name))
                    for r in rel_opts.get_all_related_objects():
                        if r.field is not f:
                            if r.get_accessor_name() == rel_name:
                                e.add(opts, "Accessor for field '%s' clashes with related field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.get_accessor_name(), f.name))
                            if r.get_accessor_name() == rel_query_name:
                                e.add(opts, "Reverse query name for field '%s' clashes with related field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.get_accessor_name(), f.name))

        seen_intermediary_signatures = []
        for i, f in enumerate(opts.local_many_to_many):
            # Check to see if the related m2m field will clash with any
            # existing fields, m2m fields, m2m related objects or related
            # objects
            if f.rel.to not in models.get_models():
                # If the related model is swapped, provide a hint;
                # otherwise, the model just hasn't been installed.
                if not isinstance(f.rel.to, six.string_types) and f.rel.to._meta.swapped:
                    e.add(opts, "'%s' defines a relation with the model '%s.%s', which has been swapped out. Update the relation to point at settings.%s." % (f.name, f.rel.to._meta.app_label, f.rel.to._meta.object_name, f.rel.to._meta.swappable))
                else:
                    e.add(opts, "'%s' has an m2m relation with model %s, which has either not been installed or is abstract." % (f.name, f.rel.to))

                # it is a string and we could not find the model it refers to
                # so skip the next section
                if isinstance(f.rel.to, six.string_types):
                    continue

            # Check that the field is not set to unique.  ManyToManyFields do not support unique.
            if f.unique:
                e.add(opts, "ManyToManyFields cannot be unique.  Remove the unique argument on '%s'." % f.name)

            if f.rel.through is not None and not isinstance(f.rel.through, six.string_types):
                from_model, to_model = cls, f.rel.to
                if from_model == to_model and f.rel.symmetrical and not f.rel.through._meta.auto_created:
                    e.add(opts, "Many-to-many fields with intermediate tables cannot be symmetrical.")
                seen_from, seen_to, seen_self = False, False, 0
                for inter_field in f.rel.through._meta.fields:
                    rel_to = getattr(inter_field.rel, 'to', None)
                    if from_model == to_model:  # relation to self
                        if rel_to == from_model:
                            seen_self += 1
                        if seen_self > 2:
                            e.add(opts, "Intermediary model %s has more than "
                                "two foreign keys to %s, which is ambiguous "
                                "and is not permitted." % (
                                    f.rel.through._meta.object_name,
                                    from_model._meta.object_name
                                )
                            )
                    else:
                        if rel_to == from_model:
                            if seen_from:
                                e.add(opts, "Intermediary model %s has more "
                                    "than one foreign key to %s, which is "
                                    "ambiguous and is not permitted." % (
                                        f.rel.through._meta.object_name,
                                         from_model._meta.object_name
                                     )
                                 )
                            else:
                                seen_from = True
                        elif rel_to == to_model:
                            if seen_to:
                                e.add(opts, "Intermediary model %s has more "
                                    "than one foreign key to %s, which is "
                                    "ambiguous and is not permitted." % (
                                        f.rel.through._meta.object_name,
                                        rel_to._meta.object_name
                                    )
                                )
                            else:
                                seen_to = True
                if f.rel.through not in models.get_models(include_auto_created=True):
                    e.add(opts, "'%s' specifies an m2m relation through model "
                        "%s, which has not been installed." % (f.name, f.rel.through)
                    )
                signature = (f.rel.to, cls, f.rel.through)
                if signature in seen_intermediary_signatures:
                    e.add(opts, "The model %s has two manually-defined m2m "
                        "relations through the model %s, which is not "
                        "permitted. Please consider using an extra field on "
                        "your intermediary model instead." % (
                            cls._meta.object_name,
                            f.rel.through._meta.object_name
                        )
                    )
                else:
                    seen_intermediary_signatures.append(signature)
                if not f.rel.through._meta.auto_created:
                    seen_related_fk, seen_this_fk = False, False
                    for field in f.rel.through._meta.fields:
                        if field.rel:
                            if not seen_related_fk and field.rel.to == f.rel.to:
                                seen_related_fk = True
                            elif field.rel.to == cls:
                                seen_this_fk = True
                    if not seen_related_fk or not seen_this_fk:
                        e.add(opts, "'%s' is a manually-defined m2m relation "
                            "through model %s, which does not have foreign keys "
                            "to %s and %s" % (f.name, f.rel.through._meta.object_name,
                                f.rel.to._meta.object_name, cls._meta.object_name)
                        )
            elif isinstance(f.rel.through, six.string_types):
                e.add(opts, "'%s' specifies an m2m relation through model %s, "
                    "which has not been installed" % (f.name, f.rel.through)
                )

            rel_opts = f.rel.to._meta
            rel_name = f.related.get_accessor_name()
            rel_query_name = f.related_query_name()
            # If rel_name is none, there is no reverse accessor (this only
            # occurs for symmetrical m2m relations to self). If this is the
            # case, there are no clashes to check for this field, as there are
            # no reverse descriptors for this field.
            if rel_name is not None:
                for r in rel_opts.fields:
                    if r.name == rel_name:
                        e.add(opts, "Accessor for m2m field '%s' clashes with field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.name, f.name))
                    if r.name == rel_query_name:
                        e.add(opts, "Reverse query name for m2m field '%s' clashes with field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.name, f.name))
                for r in rel_opts.local_many_to_many:
                    if r.name == rel_name:
                        e.add(opts, "Accessor for m2m field '%s' clashes with m2m field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.name, f.name))
                    if r.name == rel_query_name:
                        e.add(opts, "Reverse query name for m2m field '%s' clashes with m2m field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.name, f.name))
                for r in rel_opts.get_all_related_many_to_many_objects():
                    if r.field is not f:
                        if r.get_accessor_name() == rel_name:
                            e.add(opts, "Accessor for m2m field '%s' clashes with related m2m field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.get_accessor_name(), f.name))
                        if r.get_accessor_name() == rel_query_name:
                            e.add(opts, "Reverse query name for m2m field '%s' clashes with related m2m field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.get_accessor_name(), f.name))
                for r in rel_opts.get_all_related_objects():
                    if r.get_accessor_name() == rel_name:
                        e.add(opts, "Accessor for m2m field '%s' clashes with related field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.get_accessor_name(), f.name))
                    if r.get_accessor_name() == rel_query_name:
                        e.add(opts, "Reverse query name for m2m field '%s' clashes with related field '%s.%s'. Add a related_name argument to the definition for '%s'." % (f.name, rel_opts.object_name, r.get_accessor_name(), f.name))

        # Check ordering attribute.
        if opts.ordering:
            for field_name in opts.ordering:
                if field_name == '?':
                    continue
                if field_name.startswith('-'):
                    field_name = field_name[1:]
                if opts.order_with_respect_to and field_name == '_order':
                    continue
                # Skip ordering in the format field1__field2 (FIXME: checking
                # this format would be nice, but it's a little fiddly).
                if '__' in field_name:
                    continue
                # Skip ordering on pk. This is always a valid order_by field
                # but is an alias and therefore won't be found by opts.get_field.
                if field_name == 'pk':
                    continue
                try:
                    opts.get_field(field_name, many_to_many=False)
                except models.FieldDoesNotExist:
                    e.add(opts, '"ordering" refers to "%s", a field that doesn\'t exist.' % field_name)

        # Check unique_together.
        for ut in opts.unique_together:
            validate_local_fields(e, opts, "unique_together", ut)
        if not isinstance(opts.index_together, collections.Sequence):
            e.add(opts, '"index_together" must a sequence')
        else:
            for it in opts.index_together:
                validate_local_fields(e, opts, "index_together", it)

    return len(e.errors)


def validate_local_fields(e, opts, field_name, fields):
    from django.db import models

    if not isinstance(fields, collections.Sequence):
        e.add(opts, 'all %s elements must be sequences' % field_name)
    else:
        for field in fields:
            try:
                f = opts.get_field(field, many_to_many=True)
            except models.FieldDoesNotExist:
                e.add(opts, '"%s" refers to %s, a field that doesn\'t exist.' % (field_name, field))
            else:
                if isinstance(f.rel, models.ManyToManyRel):
                    e.add(opts, '"%s" refers to %s. ManyToManyFields are not supported in %s.' % (field_name, f.name, field_name))
                if f not in opts.local_fields:
                    e.add(opts, '"%s" refers to %s. This is not in the same model as the %s statement.' % (field_name, f.name, field_name))
