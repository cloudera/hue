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
The building blocks of a query:
- A Selection (which despite its name, doesn't have to appear in a SELECT clause) is
  a column or a constant value, with optional functions applied to it.
- A QTable is a table used in a query, and can return the columns it has.
- A BooleanCondition is a boolean/logical operator on one or more Selections, or other
  BooleanCondition's.
- A WHERE clause is just a BooleanCondition.
- A Join is a bunch of tables, plus a BooleanCondition.

  SELECT
    x.foo AS foo,                       <- ColumnSelection
    1,                                  <- ConstSelection
    2 + y.bar,                          <- FunctionSelection of two other Selections
    LOG10(10)                           <- FunctionSelection of a ConstSelection
  FROM
    table_x x JOIN table_y y            <- Two Tables
    ON
      x.foo = y.bar                     <- A LogicalUnion with one BooleanCondition
  WHERE                                 <- A LogicalUnion
    x.fred = y.bar OR                      ... its lhs is another BooleanCondition
    ( x.num > SIN(10) AND                  ... its rhs is a LogicalUnion of two BooleanCondition's
      x.num < 100 )
"""

import logging
from beeswax import common
from beeswax import db_utils

LOG = logging.getLogger(__name__)

#
# TODO(bc): Complex type support missing, e.g. array subscript, struct member access.
# TODO(bc): Missing CLUSTERBY, DISTRIBUTE BY, TRANSFORM
# TODO(bc): Missing subquery
#

class QTable(object):
  def __init__(self, table_name, alias=None):
    self.name = table_name
    self.alias = alias or None          # Canonical alias == None, when it has no alias
    self.columns = None                 # None, or a list of Column's

  def __cmp__(self, obj):
    return cmp((self.name, self.alias), (obj.name, obj.alias))

  def manifest(self, is_from=False):
    """If the QTable shows up in a FROM clause, we show 'name alias'. Otherwise just either one"""
    res = self.name
    if is_from:
      if self.alias:
        res = "%s %s" % (res, self.alias)
    else:
      if self.alias:
        return self.alias
    return res

  def get_columns(self):
    """
    get_columns() -> List of (cached) column names
    May raise ttypes.NoSuchObjectException if the table name is bogus.
    """
    if self.columns is None:
      ttable = db_utils.meta_client().get_table("default", self.name)
      self.columns = [ c.name for c in ttable.sd.cols ]
    return self.columns


class _Selection(object):
  """
  An abstract selection with distinct and aggregation.
  """
  def __init__(self):
    self._agg = None
    self.distinct = False

  def set_aggregation(self, agg):
    if agg not in common.AGGREGATIONS:
      raise KeyError("%s is not a valid aggregation" % (agg,))
    self._agg = agg

  @property
  def aggregation(self):
    return self._agg

  def manifest(self, name, alias=None, is_select=False):
    res = name
    if is_select:
      if self.distinct:
        res = 'DISTINCT ' + res
      if self.aggregation:
        res = '%s(%s)' % (self.aggregation, res)
      if alias:
        res = '%s AS %s' % (res, alias)
    return res


class ConstSelection(_Selection):
  """Simple selection of a constant."""
  def __init__(self, value, alias=None):
    _Selection.__init__(self)
    self.value = str(value)
    try:
      # Try to be smart and detect numbers vs strings
      _ = float(value)
    except ValueError:
      # Not a number. Need quotes.
      self.value = '"%s"' % (self.value.replace('"', '\\"'),)
    self.alias = alias or None

  def manifest(self, is_select=False):
    return _Selection.manifest(self, self.value, self.alias, is_select)


class ColumnSelection(_Selection):
  """Simple selection of a column from a table."""
  def __init__(self, table, column, alias=None):
    _Selection.__init__(self)
    self.table = table                  # QTable object
    self.column = column
    self.alias = alias

  def manifest(self, is_select=False, is_sort=False):
    if is_sort and self.alias:
      return self.alias                 # HQL requires 'SORT BY <alias>'
    name = '%s.%s' % (self.table.manifest(), self.column)
    return _Selection.manifest(self, name, self.alias, is_select)


class FunctionSelection(_Selection):
  """Application of a function on ColumnSelection(s)."""
  # TODO(bc)  This is very tedious to get right. Might use FreeFormSelection instead.
  def __init__(self, fn_name, args, alias):
    """
    fn_name is the literal function name, e.g. '+', '!', 'LOG'.
    args is a list of ColumnSelection(s) and constant(s), to which the function applies in order.
    E.g.  FunctionSelection('-', [ ColumnSelection(tbl, n), 3 ], 'header')
          -> SELECT ... tbl.n - 3 AS header ...
    E.g.  FunctionSelection('LOG10', [ ColumnSelection(tbl, n), ], 'header')
          -> SELECT ... log10(tbl.n) AS header ...
    """
    _Selection.__init__(self)
    self.fn_name = fn_name
    self.args = args
    self.alias = alias

  def manifest(self):
    return "TODO_FunctionSelection_manifest"


class FreeFormSelection(_Selection):
  """The users can enter whatever the hack they want"""
  def __init__(self, str, alias=None):
    _Selection.__init__(self)
    self.str = str
    self.alias = alias

  def manifest(self, is_select=False):
    return _Selection.manifest(self, str, self.alias, is_select)


class BooleanCondition(object):
  """Represents an atomic condition that evaluates into True or False."""
  def __init__(self, lhs_selection, relation, rhs_selection=None):
    """
    For unary relational operators, e.g. "IS NULL", "NOT", rhs may be None.
    lhs and rhs are _Selection objects.
    """
    assert isinstance(lhs_selection, _Selection)
    assert rhs_selection is None or isinstance(rhs_selection, _Selection)
    if relation not in common.RELATION_OPS:
      raise ValueError("%s is not a valid operator" % (relation,))
    self._lhs = lhs_selection
    self._rhs = rhs_selection
    self._relation = relation

  def is_joinable(self):
    """Whether this can be used as a JOIN condition."""
    return isinstance(self._rhs, ColumnSelection) and \
          isinstance(self._lhs, ColumnSelection) and \
          self._relation == '=' and \
          self._lhs != self._rhs

  def manifest(self):
    if self._relation in common.RELATION_OPS_UNARY:
      if self._relation == 'NOT':
        return 'NOT %s' % (self._lhs.manifest(),)
      return '%s %s' % (self._lhs.manifest(), self._relation)
    return '%s %s %s' % (self._lhs.manifest(), self._relation, self._rhs.manifest())


class LogicalUnion(object):
  """Represents a tree of BooleanCondition objects, AND/OR'ed together."""
  def __init__(self, union_type):
    assert union_type in ('AND', 'OR')
    self.union_type = union_type
    self.cond_list = [ ]                 # A list of BooleanCondition
    self.sub_unions = [ ]                # A list of sub-LogicalUnion

  def is_empty(self):
    return self.size() == 0

  def size(self):
    return len(self.cond_list) + len(self.sub_unions)

  def add_cond(self, boolean_cond):
    assert isinstance(boolean_cond, BooleanCondition)
    self.cond_list.append(boolean_cond)

  def add_subunion(self, union_cond):
    assert isinstance(union_cond, LogicalUnion)
    self.sub_unions.append(union_cond)

  def compact(self):
    """Get rid of unions that only consist of one other union"""
    for child in self.sub_unions:
      child.compact()
    if len(self.cond_list) == 0 and len(self.sub_unions) == 1:
      copy = self.sub_unions[0]
      self.union_type = copy.union_type
      self.cond_list = copy.cond_list
      self.sub_unions = copy.sub_unions

  def is_joinable(self):
    return all([ cond.is_joinable() for cond in self.cond_list ]) and \
            all([ child.is_joinable() for child in self.sub_unions ])

  def split_join_condition(self):
    """
    split_join_condition() -> join-able LogicalUnion

    Split this LogicalUnion into two. Return a join-able LogicalUnion, and
    modifies this object to contain WHERE clause conditions. This is needed because
    HIVE is not smart enough to optimize the join from the WHERE clause.

    Theoretically, (which we don't do), we should convert self to CNF, then pick
    out all the join-able subconditions. In practice, this is too hairy.
    """
    res = LogicalUnion('AND')
    if self.union_type == 'OR' and self.size() != 1:
      # Since we're not in conjunctive form, just return an empty condition.
      # Note that AND/OR doesn't matter if we're a singleton.
      return res

    where_cond_list = [ ]
    for cond in self.cond_list:
      if cond.is_joinable():
        res.add_cond(cond)
      else:
        where_cond_list.append(cond)

    where_sub_unions = [ ]
    for child in self.sub_unions:                 # Split sub_unions recursively
      j_child = child.split_join_condition()
      if not j_child.is_empty():
        res.add_subunion(j_child)
      if not child.is_empty():
        where_sub_unions.append(child)

    self.cond_list = where_cond_list
    self.sub_unions = where_sub_unions
    return res

  def manifest(self, level=0):
    if self.is_empty():
      return ''
    atoms = [ cond.manifest() for cond in self.cond_list ] + \
            [ child.manifest(level+1) for child in self.sub_unions ]
    connector = '\n' + '     ' * level + ' %s ' % (self.union_type)
    return '( ' + connector.join(atoms) + ' )'
