#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Extra form fields and widgets.

import logging
import json
import urllib

from django.forms import Widget, Field
from django import forms
from django.forms.utils import ErrorList, ValidationError, flatatt
from django.forms.fields import MultiValueField, CharField, ChoiceField, BooleanField
from django.forms.widgets import MultiWidget, Select, TextInput, Textarea, HiddenInput, Input
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.encoding import python_2_unicode_compatible, force_unicode

import desktop.lib.i18n
from desktop.lib.i18n import smart_str


LOG = logging.getLogger(__name__)

try:
  from django.utils.encoding import StrAndUnicode
except ImportError:
  from django.utils.encoding import python_2_unicode_compatible

  @python_2_unicode_compatible
  class StrAndUnicode(object):
    def __str__(self):
      return self.code

class SplitDateTimeWidget(forms.MultiWidget):
  """
  A Widget that splits datetime input into two <input type="text"> boxes.
  The date_class and time_class attributes specify class names to be given
  specifically to the corresponding DateInput and TimeInput widgets.
  """
  date_format = formats.get_format('DATE_INPUT_FORMATS')[0]
  time_format = formats.get_format('TIME_INPUT_FORMATS')[0]

  def __init__(self, attrs=None, date_format=None, time_format=None, date_class='date', time_class='time'):
    date_attrs = dict(attrs)
    time_attrs = dict(attrs)
    if 'class' in date_attrs:
      date_classes = [clss for clss in date_attrs['class'].split() if clss != date_class]
      date_classes.append(date_class)
      date_attrs['class'] = ' '.join(date_classes)
    else:
      date_attrs['class'] = date_class
    if 'class' in time_attrs:
      time_classes = [clss for clss in time_attrs['class'].split() if clss != time_class]
      time_classes.append(time_class)
      time_attrs['class'] = ' '.join(time_classes)
    else:
      time_attrs['class'] = time_class
    widgets = (forms.DateInput(attrs=date_attrs, format=date_format),
               forms.TimeInput(attrs=time_attrs, format=time_format))
    del attrs['class']
    super(SplitDateTimeWidget, self).__init__(widgets, attrs)

  def decompress(self, value):
    if value:
      return [value.date(), value.time().replace(microsecond=0)]
    return [None, None]

class MultipleInputWidget(Widget):
  """
  Together with MultipleInputField, represents repeating a form element many times,
  and representing a list of values for that element.
  This could be made generic to work with any widget, but currently
  renders itself as a regular old <input>.
  """
  def __init__(self, attrs=None):
    super(MultipleInputWidget, self).__init__(attrs)

  def render(self, name, value, attrs=None):
    if value is None:
      value = ()
    if attrs is None or "count" not in attrs:
      count = 5
    else:
      count = attrs["count"]

    count = max(len(value) + 1, count)

    s = ""
    for i in range(count):
      if value is not None and i < len(value):
        v = value[i]
        s += '<input name="%s" value="%s"></input>' % (name, v)
      else:
        s += '<input name="%s"></input>' % name
    return s

  def value_from_datadict(self, data, files, name):
    # Sometimes this is a QueryDict, and sometimes ar regular dict,
    # so we adapt:
    non_empty = lambda x: len(x) != 0
    return filter(non_empty, data.getlist(name))

class MultipleInputField(Field):
  widget = MultipleInputWidget

  def __init__(self, *args, **kwargs):
    super(MultipleInputField, self).__init__(*args, **kwargs)

  def clean(self, value):
    return value

OTHER_VAL, OTHER_PRES = "__other__", "Other..."

class ChoiceOrOtherWidget(MultiWidget):
  """
  Together with ChoiceOrOtherField represents a drop-down and an "other"
  text-box.

  This may not map well onto an AJAX model, since in that world
  the JS presentation will handle sending only one value.
  """
  def __init__(self, attrs=None, choices=()):
    self.choices = choices
    self.values = [ val for pres, val in choices if val != OTHER_VAL ]
    widgets = (
      Select(attrs=attrs, choices=choices),
      TextInput(attrs=attrs)
    )
    super(ChoiceOrOtherWidget, self).__init__(widgets, attrs)

  def decompress(self, value):
    if value in self.values:
      return [value, ""]
    else:
      return [OTHER_VAL, value]

class ChoiceOrOtherField(MultiValueField):
  def __init__(self, choices, initial=None, *args, **kwargs):
    assert not kwargs.get('required', False), "required=True is not supported"

    allchoices = [ x for x in choices ] # Force choices into a list.
    allchoices.append( (OTHER_VAL, OTHER_PRES) )
    self.widget = ChoiceOrOtherWidget(choices=allchoices)
    choice_initial, other_initial = None, None
    if initial is not None:
      # Match initial against one of the values
      if initial in [ x for x, y in choices ]:
        choice_initial = initial
      else:
        choice_initial = OTHER_VAL
        other_initial = initial

    fields = [
      ChoiceField(required=False, choices=allchoices),
      CharField(required=False)
    ]
    # Be careful not to make the initial value a tuple;
    # it's checked explicitly to be a list in MultiWidget's
    # render.
    super(ChoiceOrOtherField, self).__init__(fields, initial=[choice_initial, other_initial], *args, **kwargs)

  def compress(self, data_list):
    if len(data_list) == 0:
      return None
    if data_list[0] == OTHER_VAL:
      return data_list[1]
    else:
      if data_list[1]:
        raise ValidationError("Either select from the drop-down or select %s" % OTHER_PRES)
      return data_list[0]

class KeyValueWidget(Textarea):
  def render(self, name, value, attrs=None):
    # If we have a dictionary, render back into a string.
    if isinstance(value, dict):
      value = " ".join("=".join([k, v]) for k, v in value.iteritems())
    return super(KeyValueWidget, self).render(name, value, attrs)

class KeyValueField(CharField):
  """
  Represents an input area for key/value pairs in the following format:
  "<key1>=<val1> <key2>=<value2>...."
  clean() returns a dictionary of parsed key/value pairs.
  """
  widget = KeyValueWidget

  def __init__(self, *args, **kwargs):
    super(KeyValueField, self).__init__(*args, **kwargs)

  def clean(self, value):
    """Converts the raw key=val text to a dictionary of key/val pairs"""
    super(KeyValueField, self).clean(value)
    try:
      return dict(kvpair.split('=', 2) for kvpair in value.split())
    except Exception:
      raise ValidationError("Not in key=value format.")

class UnicodeEncodingField(ChoiceOrOtherField):
  """
  The cleaned value of the field is the actual encoding, not a tuple
  """
  CHOICES = [
    ('utf-8', 'Unicode UTF8'),
    ('utf-16', 'Unicode UTF16'),
    ('latin_1', 'Western ISO-8859-1'),
    ('latin_9', 'Western ISO-8859-15'),
    ('cyrillic', 'Cryrillic'),
    ('arabic', 'Arabic'),
    ('greek', 'Greek'),
    ('hebrew', 'Hebrew'),
    ('shift_jis', 'Japanese (Shift-JIS)'),
    ('euc-jp', 'Japanese (EUC-JP)'),
    ('iso2022_jp', 'Japanese (ISO-2022-JP)'),
    ('euc-kr', 'Korean (EUC-KR)'),
    ('iso2022-kr', 'Korean (ISO-2022-KR)'),
    ('gbk', 'Chinese Simplified (GBK)'),
    ('big5hkscs', 'Chinese Traditional (Big5-HKSCS)'),
    ('ascii', 'ASCII'),
  ]

  def __init__(self, initial=None, *args, **kwargs):
    ChoiceOrOtherField.__init__(self, UnicodeEncodingField.CHOICES, initial, *args, **kwargs)

  def clean(self, value):
    encoding = value[0] == OTHER_VAL and value[1] or value[0]
    if encoding and not desktop.lib.i18n.validate_encoding(encoding):
      raise forms.ValidationError("'%s' encoding is not available" % (encoding,))
    return encoding


class MultiForm(object):
  """
  Initialize this with the necessary sub-forms, and then
  call bind(request).

  TODO(philip): Should users use this by extending
  it?  Or is this really a forms.Field subclass.
  """
  def __init__(self, prefix='', **kwargs):
    """
    prefix is prepended to the prefix of the member forms
    Keyword arguments are:
      key=form_class, key2=form_class2, ...
    The form_class can be a Form, a Formset, or a MultiForm.
    It is currently not possible to specify ctor arguments to the form_class.
    """
    self._form_types = kwargs
    self._is_bound = False
    self._prefix = prefix

  def __str__(self):
    return 'MultForm at %s' % (self._prefix)

  def add_prefix(self, name):
    """Returns the subform name with a prefix prepended, if the prefix is set"""
    return self._prefix and ('%s.%s' % (self._prefix, name)) or name

  def get_subforms(self):
    """get_subforms() -> An iterator over (name, subform)"""
    assert self._is_bound
    return self._forms.iteritems()

  def has_subform_data(self, subform_name, data):
    """Test if data contains any information bound for the subform"""
    prefix = self.add_prefix(subform_name)
    return len([ k.startswith(prefix) for k in data.keys() ]) != 0

  def add_subform(self, name, form_cls, data=None):
    """Dynamically extend this MultiForm to include a new subform"""
    self._form_types[name] = form_cls
    self._bind_one(name, form_cls, data)

  def remove_subform(self, name):
    """Dynamically remove a subform. Raises KeyError."""
    del self._form_types[name]
    if self._forms.has_key(name):
      del self._forms[name]

  def bind(self, data=None, instances=None):
    self._is_bound = True
    self._forms = {}
    for key, form_cls in self._form_types.iteritems():
      instance = instances is not None and instances.get(key) or None
      self._bind_one(key, form_cls, data, instance=instance)

  def _bind_one(self, key, form_cls, data=None, instance=None):
    prefix = self.add_prefix(key)
    if issubclass(form_cls, MultiForm):
      member = form_cls(prefix=prefix)
      member.bind(data=data)
    elif instance is not None:
      member = form_cls(data=data, prefix=prefix, instance=instance)
    else:
      member = form_cls(data=data, prefix=prefix)
    self._forms[key] = member

  def __getattr__(self, key):
    assert self._is_bound
    return self._forms.get(key)

  def is_valid(self):
    assert self._is_bound
    r = True
    # Explicitly iterate through all of them; we don't want
    # to abort early, since we want each form's is_valid to be run.
    for f in self._forms.values():
      if not f.is_valid():
        LOG.error(smart_str(f.errors))
        r = False
    return r

class SubmitButton(Input):
  """
  A widget that presents itself as a submit button.
  """
  input_type = "submit"

  def render(self, name, value, attrs=None):
    if value is None:
      value = 'True'

    extra_attrs = dict(type=self.input_type, name=name)
    if self.attrs:
      extra_attrs.update(self.attrs)
    final_attrs = self.build_attrs(attrs, extra_attrs=extra_attrs)

    if value != '':
      # Only add the 'value' attribute if a value is non-empty.
      final_attrs['value'] = force_unicode(value)
    return mark_safe(u'<button%s>%s</button>' % (flatatt(final_attrs), getattr(self, "label", "Submit")))


class ManagementForm(forms.Form):
  add = BooleanField(widget=SubmitButton,required=False)
  next_form_id = forms.IntegerField(widget=forms.HiddenInput, initial=0)

  def __init__(self, add_label='+', *args, **kwargs):
    super(ManagementForm, self).__init__(*args, **kwargs)
    self.fields["add"].label = add_label
    self.fields["add"].widget.label = add_label

  def new_form_id(self):
    """
    new_form_id() -> The id for the next member of the formset. Increment hidden value.

    The ManagementForm needs to keep track of a monotonically increasing id, so that
    new member forms don't reuse ids of deleted forms.
    """
    # Hack. self.data is supposed to be immutable.
    res = self.form_counts()
    data2 = self.data.copy()
    data2[self.add_prefix('next_form_id')] = str(res + 1)
    self.data = data2
    return res

  def form_counts(self):
    """form_counts() -> The max number of forms, some could be non-existent (deleted)."""
    try:
      return int(self.data[ self.add_prefix('next_form_id') ])
    except KeyError:
      return self.fields['next_form_id'].initial


class BaseSimpleFormSet(StrAndUnicode):
  """
  Manages multiple instances of the same form, and easily modifies how many of said
  form there are.

  This is similar to django.forms.formsets.BaseFormSet,
  but is hopefully simpler.

  We take a base form (that's passed in via the simple_formset_factory
  machinery), and initialize it with prefix="prefix/N/", for integer
  values of N.  "perfix/add" specifies generating an extra empty one,
  and "prefix/N/_delete" specifies deleting them.

  """
  def __init__(self, data=None, prefix=None, initial=None):
    self.is_bound = data is not None
    assert prefix, "Prefix is required."
    self.prefix = prefix
    # The initial is sometimes set before the ctor, especially when used in a MultiForm,
    # which doesn't allow passing custom ctor arguments.
    self.initial = initial or getattr(self, 'initial', initial)
    self.data = data
    self._non_form_errors = None
    self._errors = None
    self._construct_forms()

  def make_prefix(self, i):
    return "%s-%s" % (self.prefix, i)

  def _construct_mgmt_form(self):
    if self.data:
      form = ManagementForm(data=self.data, prefix=self.prefix, add_label=self.add_label)
      if not form.is_valid():
        raise forms.ValidationError('Management form missing for %s' % (self.prefix))
    else:
      # A new unbound formset
      n_initial = self.initial and len(self.initial) or 0
      form = ManagementForm(prefix=self.prefix,
                            add_label=self.add_label,
                            initial={ 'next_form_id': n_initial })
    self.management_form = form

  def empty_form(self):
    f = self.form(prefix=self.make_prefix("TEMPLATE"))
    f.fields["_exists"] = BooleanField(initial=True, widget=HiddenInput)
    f.fields["_deleted"] = BooleanField(initial=True, required=False, widget=SubmitButton)
    return f

  def _construct_forms(self):
    self._construct_mgmt_form()

    self.forms = []
    if not self.is_bound:
      if self.initial is not None:
        for i, data in enumerate(self.initial):
          self.forms.append(self.form(initial=data, prefix=self.make_prefix(i)))
      else:
        self.forms = []
    else:
      for i in range(0, self.management_form.form_counts()):
        # Since the form might be "not valid", you can't use
        # cleaned_data to get at these fields.
        if self.make_prefix(i) + "-_exists" in self.data:
          if self.data.get(self.make_prefix(i) + "-_deleted") != "True":
            f = self.form(data=self.data, prefix=self.make_prefix(i))
            self.forms.append(f)

    if self.management_form.is_valid() and self.management_form.cleaned_data["add"]:
      self.add_form()

    for f in self.forms:
      f.fields["_exists"] = BooleanField(initial=True, widget=HiddenInput)
      # Though _deleted is marked as initial=True, the value is only transmitted
      # if this is the button that's clicked, so the real default is False.
      f.fields["_deleted"] = BooleanField(initial=True, required=False, widget=SubmitButton)
      f.fields["_deleted"].widget.label = "(x)"

  def add_form(self):
    """Programatically add a form"""
    prefix = self.make_prefix(self.management_form.new_form_id())
    member = self.form(prefix=prefix)
    self.forms.append(member)

  def clean(self):
    """Hook for custom cleaning."""
    pass

  def full_clean(self):
    """Simlar to formsets.py:full_clean"""
    self._errors = []
    if not self.is_bound:
      return
    for f in self.forms:
      self._errors.append(f.errors)
    try:
      self.clean()
    except ValidationError, e:
      self._non_form_errors = e.messages

  @property
  def errors(self):
    if self._errors is None:
      self.full_clean()
    return self._errors

  def non_form_errors(self):
    if self._non_form_errors is not None:
      return self._non_form_errors
    return ErrorList()

  def is_valid(self):
    if not self.is_bound:
      return False
    valid = True
    # Iterate through all, to find all errors, not just first ones.
    for i, f in enumerate(self.forms):
      if bool(self.errors[i]) or not f.is_valid():
        valid = False

    return valid and not bool(self.non_form_errors())

def simple_formset_factory(form, add_label="+", formset=BaseSimpleFormSet, initial=None):
  """Return a FormSet for the given form class."""
  attrs = {
    'form': form,
    'add_label': add_label,
    'initial': initial
  }
  return type(form.__name__ + 'SimpleFormSet', (formset,), attrs)

class DependencyAwareForm(forms.Form):
  """
  Inherit from this class and add
  (condition name, condition value, child name) tuples
  to self.dependencies to describe dependencies between
  certain form fields.

  The semantic meaning is that the field named "child name"
  is required if and only if the field "condition name"
  has value "condition value".

  For an example, visit the jframegallery ("fields with dependencies").
  """
  def clean(self):
    ret = super(DependencyAwareForm, self).clean()
    if self.errors:
      return
    for cond, required_value, child in self.dependencies:
      if self.cleaned_data.get(cond, None) == required_value:
        child_val = self.cleaned_data.get(child)
        if child_val in [None, '']:
          self._errors.setdefault(child, []).append("%s is required if %s is %s" % (child, cond, str(required_value)))
    return ret

  def _calculate_data(self):
    """
    Returns a "dict" with mappings between ids, desired values, and ids.
    """
    def data(cond, required_value, child):
      """Calculates data for single item."""
      return self.add_prefix(cond), str(required_value), self.add_prefix(child)

    return [ data(*x) for x in self.dependencies ]

  def render_dep_metadata(self):
    return urllib.quote_plus(json.dumps(self._calculate_data(), separators=(',', ':')))
