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

"""
Views for the Report Generator.

The Report Generator has a root level MultiForm, which contains a
ReportColumnFormset, and a UnionMultiForm. The ReportColumnFormset is just a
collection of ReportColumnForm's. The tricky bit is in the UnionMultiForm.

One can think of a UnionMultiForm as a logical statement:
    AND(x=1, y=2, z=3)
When a UnionMultiForm is created, it initially only consists of:
    * "bool"          - a ReportConditionBoolForm; the "AND"
    * "conds"         - a ReportConditionFormset; the "x=1, y=2, z=3" list
    * "mgmt"          - a ManagementForm; to allow adding sub-conditions

But a UnionMultiForm may contain sub-conditions (i.e. other UnionMultiForm).
Using the example above:
    AND(x=1, y=2, z=3, OR(a=4, b=5))
When we add the sub-condition OR(a=4, b=5), we need to dynamically extend the
parent UnionMultiForm to hold a child UnionMultiForm. We name the nth child form
"sub<n>". From the same example, the parent UnionMultiForm will have:
    * "bool"          - a ReportConditionBoolForm; the "AND"
    * "conds"         - a ReportConditionFormset; the "x=1, y=2, z=3" list
    * "mgmt"          - a ManagementForm; to allow adding sub-conditions
    * "sub0"          - a UnionMultiForm; the "OR(a=4, b=5)"

When we handle the view, we always first create a initial UnionMultiForm with no
sub-conditions, because we do not know whether there is any. Then we look at
the POST data to figure out what sub-UnionMultiForm's we should have (see
fixup_union()).
"""

import logging

import beeswax.forms

from django import forms

from beeswax import common
from beeswax.report import report_gen
from desktop.lib.django_forms import BaseSimpleFormSet, ManagementForm, MultiForm
from desktop.lib.django_forms import simple_formset_factory, SubmitButton

LOG = logging.getLogger(__name__)

SUB_UNION_PREFIX = 'sub'

def fixup_union(parent_mform, subform_name, data, is_root=False):
  """
  Create child union mforms dynamically. Note that the parent_mform may be invalid.
  The parent_mform is a MultiForm, in which the subform_name is a UnionMultiForm we
  need to fix.

  This method performs this dynamic construction of the child UnionMultiForm.
  Note that it applies to existing child forms (i.e. the child form exists and the
  user is submitting the query), as well as a newly added child (i.e. the user just
  clicked 'ADD' to add a sub-condition).

  We figure out the number of children from the mgmt form. Note that this is actually
  a count of the number of children we have ever had. It is a max of the number of
  children, some of which may have been deleted.

  For each child <i>, our strategy is to test if 'sub<i>' exists in the POST data.
  If so, we create a sub-UnionMultiForm for that child. And we do it recursively.
  """
  global SUB_UNION_PREFIX

  union_mform = getattr(parent_mform, subform_name)
  mgmt_form = union_mform.mgmt
  if not mgmt_form.is_valid():
    raise forms.ValidationError('Missing ManagementForm for conditions')
  n_children = mgmt_form.form_counts()

  # This removes our current subform (union_mform) and any children.
  if mgmt_form.cleaned_data['remove']:
    parent_mform.remove_subform(subform_name)
    LOG.debug('Removed subform: %s' % (union_mform,))
    # If we just removed the root union, add back an empty one.
    if is_root:
      parent_mform.add_subform('union', UnionMultiForm, data=None)
      LOG.debug('Adding root union back')
    return

  # Note that some of the n_children could be non-existent (i.e. deleted)
  for i in range(0, n_children):
    child_name = '%s%d' % (SUB_UNION_PREFIX, i)
    if not union_mform.has_subform_data(child_name, data):
      LOG.debug('Skipping over non-existent subform: %s %s' % (union_mform, child_name))
      continue
    union_mform.add_subform(child_name, UnionMultiForm, data)
    LOG.debug('Instantiating subform: %s %s' % (union_mform, child_name))
    # The child may have grand-children
    fixup_union(union_mform, child_name, data)

  if mgmt_form.cleaned_data['add']:
    id = mgmt_form.new_form_id()
    child_name = '%s%d' % (SUB_UNION_PREFIX, id)
    union_mform.add_subform(child_name, UnionMultiForm)
    LOG.debug('Added subform: %s %s' % (union_mform, child_name))


def construct_query(mform):
  """Take a root level MultiForm and return a query string"""
  columns = mform.columns
  selection_list = [ ]
  for form in columns.forms:
    if form.cleaned_data['display']:
      selection_list.append(form.selection)

  select_clause_atoms = [ sel.manifest(is_select=True) for sel in selection_list ]
  select_clause = 'SELECT %s' % (', '.join(select_clause_atoms))

  from_clause_atoms = [ t.manifest(is_from=True) for t in columns.qtable_list ]
  from_clause = '\nFROM\n  %s' % (' JOIN \n  '.join(from_clause_atoms))

  # where clause
  table_alias_dict = { }
  for qt in columns.qtable_list:
    alias = qt.alias or qt.name
    table_alias_dict[alias] = qt
  where_union_cond = _extract_condition(mform.union, table_alias_dict)
  join_union_cond = where_union_cond.split_join_condition()
  if where_union_cond.is_empty():
    where_clause = ''
  else:
    where_union_cond.compact()
    where_clause = '\nWHERE\n' + where_union_cond.manifest()

  # join condition
  if join_union_cond.is_empty():
    join_on_clause = ''
  else:
    join_union_cond.compact()
    join_on_clause = '\nON ' + join_union_cond.manifest()

  # group_list is a list of forms that specify grouping
  group_list = filter(lambda form: form.cleaned_data.get('group_order', ''), columns.forms)
  if group_list:
    group_list.sort(lambda f1, f2:
                      cmp(f1.cleaned_data['group_order'], f2.cleaned_data['group_order']))
    group_clause_atoms = [ form.selection.manifest() for form in group_list ]
    group_clause = '\nGROUP BY %s' % (', '.join(group_clause_atoms))
  else:
    group_clause = ''

  # sort_list is a list of forms that specify sorting
  sort_list = filter(lambda form: form.cleaned_data.get('sort', ''), columns.forms)
  if sort_list:
    sort_list.sort(lambda f1, f2:
                      cmp(f1.cleaned_data['sort_order'], f2.cleaned_data['sort_order']))
    sort_clause_atoms = [ '%s %s' % (form.selection.manifest(is_sort=True),
                                     form.cleaned_data['sort_hql'])
                          for form in sort_list ]
    sort_clause = '\nSORT BY %s' % (', '.join(sort_clause_atoms))
  else:
    sort_clause = ''

  return select_clause + from_clause + join_on_clause + where_clause + group_clause + sort_clause


def _extract_condition(union_mform, table_alias_dict):
  """
  Extract LogicalUnion's from each form in union_mform, and recurse into the child union.
  Returns a LogicalUnion.
  """
  global SUB_UNION_PREFIX
  if not union_mform.is_valid():
    assert False, 'UnionMultiForm is not valid'
    return None

  op = union_mform.bool.cleaned_data['bool']
  res = report_gen.LogicalUnion(op)
  for cond_form in union_mform.conds.forms:
    res.add_cond(cond_form.get_boolean_condition(table_alias_dict))

  n_children = union_mform.mgmt.form_counts()
  for i in range(0, n_children):
    child_name = '%s%d' % (SUB_UNION_PREFIX, i)
    try:
      sub_form = getattr(union_mform, child_name)
      res.add_subunion(_extract_condition(sub_form, table_alias_dict))
    except AttributeError:
      LOG.debug('Subform not found: %s %s' % (union_mform, child_name))
      continue

  return res


def _field_source_check(true_source, field_name, field_value, is_from_table):
  """
  Some fields come from a table (is_from_table). And they should be specified iff
  the true_source (what the user selected) says "table". The same holds for constant
  source. This function verifies that constraint and would raise ValidationError.

  Returns whether this field is required.
  """
  if bool(true_source == 'table') ^ bool(is_from_table):
    if field_value:
      raise forms.ValidationError('%s value not applicable with %s source' %
                                  (field_name, true_source))
    return False
  elif not field_value:
    raise forms.ValidationError('%s value missing' % (field_name,))
  return True


###########
# Columns
###########

class ReportColumnForm(forms.Form):
  """
  A form representing a column in the report.
  """
  # If not 'display', then source must be 'table'
  display = forms.BooleanField(label='Display', required=False, initial=True)

  # Shown iff 'display'. 'source' is not required, but will be set during clean
  source = forms.ChoiceField(label='Source', required=False, initial='table',
                                choices=common.to_choices(common.SELECTION_SOURCE))
  # Shown iff 'display'
  agg = forms.ChoiceField(label='Aggregate', required=False,
                                choices=common.to_choices(common.AGGREGATIONS))
  # Shown iff 'display'
  distinct = forms.BooleanField(label="Distinct", required=False)

  # Shown iff 'source' is 'constant'
  constant = forms.CharField(label='Constant value', required=False)

  # Shown iff 'source' is 'table'
  table_alias = common.HiveIdentifierField(label='Table alias', required=False)
  # Shown iff 'source' is 'table'
  col = forms.CharField(label='From column', required=False)
  # Shown iff 'display', and 'source' is 'table'
  col_alias = common.HiveIdentifierField(label='Column alias', required=False)
  # Shown iff 'display', and 'source' is 'table'
  sort = forms.ChoiceField(label='Sort', required=False,
                                choices=common.to_choices(common.SORT_OPTIONS))
  # Shown iff 'sort'
  sort_order = forms.IntegerField(label='Sort order', required=False, min_value=1)
  # Shown iff 'display', and 'source' is 'table'
  group_order = forms.IntegerField(label='Group order', required=False, min_value=1)

  def __init__(self, *args, **kwargs):
    forms.Form.__init__(self, *args, **kwargs)
    # Shown iff 'source' is 'table'
    self.fields['table'] = common.HiveTableChoiceField(label='From table', required=False)

  def _display_check(self):
    """Reconcile 'display' with 'source'"""
    src = self.cleaned_data.get('source')
    if not self.cleaned_data.get('display'):
      if src and src != 'table':
        raise forms.ValidationError('Source must be "table" when not displaying column')
      self.cleaned_data['source'] = 'table'
      if self.cleaned_data.get('col_alias'):
        raise forms.ValidationError('Column alias not applicable when not displaying column')
    else:
      if not src:
        raise forms.ValidationError('Source value missing')


  def clean_display(self):
    """Make sure display is set"""
    return self.cleaned_data.get('display', False)


  def clean_sort(self):
    """Set sort_hql accordingly"""
    dir = self.cleaned_data.get('sort')
    if dir == 'ascending':
      self.cleaned_data['sort_hql'] = 'ASC'
    elif dir == 'descending':
      self.cleaned_data['sort_hql'] = 'DESC'
    elif self.cleaned_data.has_key('sort_hql'):
      del self.cleaned_data['sort_hql']
    return dir


  def clean(self):
    self.qtable = None
    self.selection = None

    self._display_check()

    if self.cleaned_data.get('sort') and not self.cleaned_data['sort_hql']:
      raise KeyError()

    # Verify that the 'source' field is consistent with the other fields
    source = self.cleaned_data.get('source')
    if not source:
      return None                       # No point since we can't get source

    constant_val = self.cleaned_data.get('constant')
    _field_source_check(source, 'Constant', constant_val, is_from_table=False)

    table_val = self.cleaned_data.get('table')
    _field_source_check(source, 'From table', table_val, is_from_table=True)

    col_val = self.cleaned_data.get('col')
    _field_source_check(source, 'From column', col_val, is_from_table=True)

    if self.cleaned_data.get('sort', '') and not self.cleaned_data.get('sort_order', ''):
      raise forms.ValidationError('Sort order missing')

    if table_val:
      # Column must belong to the table
      self.qtable = report_gen.QTable(table_val, self.cleaned_data.get('table_alias'))
      if col_val == '*':
        if self.cleaned_data.get('col_alias'):
          raise forms.ValidationError('Alias not applicable for selecting "*"')
      elif col_val not in self.qtable.get_columns():
        raise forms.ValidationError('Invalid column name "%s"' % (col_val,))
      # ColumnSelection object
      self.selection = report_gen.ColumnSelection(self.qtable,
                                                  col_val,
                                                  self.cleaned_data.get('col_alias'))
    else:
      # ConstSelection object
      self.selection = report_gen.ConstSelection(constant_val,
                                                 self.cleaned_data.get('col_alias'))
    self.selection.distinct = self.cleaned_data.get('distinct', False)
    self.selection.set_aggregation(self.cleaned_data.get('agg', ''))

    if self.errors:
      delattr(self, 'selection')
    return self.cleaned_data


class ReportColumnBaseFormset(BaseSimpleFormSet):
  def clean(self):
    self.qtable_list = None
    if filter(None, [ not f.is_valid() for f in self.forms ]):
      return

    qt_by_name = { }                    # Dictionary of name -> [ QTable list ]
    n_display = 0
    for form in self.forms:
      if form.cleaned_data['display']:
        n_display += 1

      # Gather a list of QTables (qtable_list) involved, and check for naming collision
      if form.cleaned_data['source'] != 'table':
        continue

      curr = form.qtable
      qt_list = qt_by_name.get(curr.name, [ ])
      for qt in qt_list:
        # Error if a table has alias but another doesn't. (Tables with the same name.)
        if bool(curr.alias) ^ bool(qt.alias):
          raise forms.ValidationError('Ambiguous table "%s" without alias' % (qt.name,))
        if curr.alias == qt.alias:
          # Duplicate. Don't update.
          break
      else:
        qt_list.append(curr)
        qt_by_name[curr.name] = qt_list

    self.qtable_list = sum([ tbl_list for tbl_list in qt_by_name.values() ], [ ])
    if not self.qtable_list:
      raise forms.ValidationError('Not selecting from any table column')
    if n_display == 0:
      raise forms.ValidationError('Not displaying any selection')


ReportColumnFormset = simple_formset_factory(ReportColumnForm,
                                             formset=ReportColumnBaseFormset,
                                             initial=(None,))

###########
# Condition
###########

class ReportConditionForm(forms.Form):
  l_source = forms.ChoiceField(label='Source', initial='table',
                              choices=common.to_choices(common.SELECTION_SOURCE))
  l_table = forms.CharField(label='Table name/alias', required=False)
  l_col = forms.CharField(label='Column name', required=False)
  l_constant = forms.CharField(label='Constant', required=False)
  op = forms.ChoiceField(label='Condition',
                              choices=common.to_choices(common.RELATION_OPS))
  r_source = forms.ChoiceField(label='Source', required=False, initial='table',
                              choices=common.to_choices(common.SELECTION_SOURCE))
  r_table = forms.CharField(label='Table name/alias', required=False)
  r_col = forms.CharField(label='Column name', required=False)
  r_constant = forms.CharField(label='Constant', required=False)


  def clean(self):
    if self.errors:
      return

    # Verify unary operators constraints
    check_right = True
    op = self.cleaned_data['op']
    if op in common.RELATION_OPS_UNARY:
      if self.cleaned_data.get('r_source') or self.cleaned_data.get('r_cond'):
        raise forms.ValidationError('Operator %s does not take the right operand' % (op,))
      check_right = False
    else:
      if not self.cleaned_data.get('l_source') or not self.cleaned_data.get('r_source'):
        raise forms.ValidationError('Operator %s takes both operands' % (op,))

    # Verify the lhs values match the source
    l_source = self.cleaned_data['l_source']
    l_constant = self.cleaned_data.get('l_constant')
    _field_source_check(l_source, 'Constant (Left)', l_constant, is_from_table=False)
    l_table = self.cleaned_data.get('l_table')
    _field_source_check(l_source, 'Table (Left)', l_table, is_from_table=True)
    l_col = self.cleaned_data.get('l_col')
    _field_source_check(l_source, 'Column (Left)', l_col, is_from_table=True)

    if check_right:
      # Verify the rhs values match the source
      r_source = self.cleaned_data['r_source']
      r_constant = self.cleaned_data.get('r_constant')
      _field_source_check(r_source, 'Constant (Right)', r_constant, is_from_table=False)
      r_table = self.cleaned_data.get('r_table')
      _field_source_check(r_source, 'Table (Right)', r_table, is_from_table=True)
      r_col = self.cleaned_data.get('r_col')
      _field_source_check(r_source, 'Column (Right)', r_col, is_from_table=True)
    return self.cleaned_data


  def get_boolean_condition(self, table_alias_dict):
    if not self.is_valid():
      assert False, 'ReportConditionForm is not valid'
      return None

    op = self.cleaned_data['op']
    lhs = self._make_selection(table_alias_dict, is_left=True)
    if op in common.RELATION_OPS_UNARY:
      return report_gen.BooleanCondition(lhs, op)

    rhs = self._make_selection(table_alias_dict, is_left=False)
    return report_gen.BooleanCondition(lhs, op, rhs)


  def _make_selection(self, table_alias_dict, is_left):
    if is_left:
      prefix = 'l_'
    else:
      prefix = 'r_'

    source = self.cleaned_data[prefix + 'source']
    if source == 'table':
      table = self.cleaned_data[prefix + 'table']
      col = self.cleaned_data[prefix + 'col']
      try:
        return report_gen.ColumnSelection(table_alias_dict[table], col)
      except KeyError:
        raise forms.ValidationError('Unknown table "%s" in condition' % (table,))

    constant = self.cleaned_data[prefix + 'constant']
    return report_gen.ConstSelection(constant)

ReportConditionFormset = simple_formset_factory(ReportConditionForm,
                                                initial=(None,))


class ReportConditionBoolForm(forms.Form):
  bool = forms.ChoiceField(label='And/Or', required=True,
                           choices=common.to_choices([ 'AND', 'OR' ]))


class UnionManagementForm(ManagementForm):
  def __init__(self, *args, **kwargs):
    ManagementForm.__init__(self, *args, **kwargs)
    remove = forms.BooleanField(label='Remove', widget=SubmitButton, required=False)
    remove.widget.label = '-'
    self.fields['remove'] = remove


class UnionMultiForm(MultiForm):
  def __init__(self, *args, **kwargs):
    MultiForm.__init__(self,
                       mgmt=UnionManagementForm,
                       bool=ReportConditionBoolForm,
                       conds=ReportConditionFormset,
                       *args, **kwargs)


def report_form():
  """report_form() -> A MultiForm object for report generator"""
  return MultiForm(columns=ReportColumnFormset,
                    union=UnionMultiForm,
                    saveform=beeswax.forms.SaveForm)
