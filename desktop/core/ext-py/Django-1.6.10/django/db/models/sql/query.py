"""
Create SQL statements for QuerySets.

The code in here encapsulates all of the SQL construction so that QuerySets
themselves do not have to (and could be backed by things other than SQL
databases). The abstraction barrier only works one way: this module has to know
all about the internals of models in order to get the information it needs.
"""

import copy

from django.utils.datastructures import SortedDict
from django.utils.encoding import force_text
from django.utils.tree import Node
from django.utils import six
from django.db import connections, DEFAULT_DB_ALIAS
from django.db.models.constants import LOOKUP_SEP
from django.db.models.aggregates import refs_aggregate
from django.db.models.expressions import ExpressionNode
from django.db.models.fields import FieldDoesNotExist
from django.db.models.related import PathInfo
from django.db.models.sql import aggregates as base_aggregates_module
from django.db.models.sql.constants import (QUERY_TERMS, ORDER_DIR, SINGLE,
        ORDER_PATTERN, JoinInfo, SelectInfo)
from django.db.models.sql.datastructures import EmptyResultSet, Empty, MultiJoin
from django.db.models.sql.expressions import SQLEvaluator
from django.db.models.sql.where import (WhereNode, Constraint, EverythingNode,
    ExtraWhere, AND, OR, EmptyWhere)
from django.core.exceptions import FieldError

__all__ = ['Query', 'RawQuery']


class RawQuery(object):
    """
    A single raw SQL query
    """

    def __init__(self, sql, using, params=None):
        self.params = params or ()
        self.sql = sql
        self.using = using
        self.cursor = None

        # Mirror some properties of a normal query so that
        # the compiler can be used to process results.
        self.low_mark, self.high_mark = 0, None  # Used for offset/limit
        self.extra_select = {}
        self.aggregate_select = {}

    def clone(self, using):
        return RawQuery(self.sql, using, params=self.params)

    def convert_values(self, value, field, connection):
        """Convert the database-returned value into a type that is consistent
        across database backends.

        By default, this defers to the underlying backend operations, but
        it can be overridden by Query classes for specific backends.
        """
        return connection.ops.convert_values(value, field)

    def get_columns(self):
        if self.cursor is None:
            self._execute_query()
        converter = connections[self.using].introspection.table_name_converter
        return [converter(column_meta[0])
                for column_meta in self.cursor.description]

    def __iter__(self):
        # Always execute a new query for a new iterator.
        # This could be optimized with a cache at the expense of RAM.
        self._execute_query()
        if not connections[self.using].features.can_use_chunked_reads:
            # If the database can't use chunked reads we need to make sure we
            # evaluate the entire query up front.
            result = list(self.cursor)
        else:
            result = self.cursor
        return iter(result)

    def __repr__(self):
        return "<RawQuery: %r>" % (self.sql % tuple(self.params))

    def _execute_query(self):
        self.cursor = connections[self.using].cursor()
        self.cursor.execute(self.sql, self.params)


class Query(object):
    """
    A single SQL query.
    """
    # SQL join types. These are part of the class because their string forms
    # vary from database to database and can be customised by a subclass.
    INNER = 'INNER JOIN'
    LOUTER = 'LEFT OUTER JOIN'

    alias_prefix = 'T'
    query_terms = QUERY_TERMS
    aggregates_module = base_aggregates_module

    compiler = 'SQLCompiler'

    def __init__(self, model, where=WhereNode):
        self.model = model
        self.alias_refcount = {}
        # alias_map is the most important data structure regarding joins.
        # It's used for recording which joins exist in the query and what
        # type they are. The key is the alias of the joined table (possibly
        # the table name) and the value is JoinInfo from constants.py.
        self.alias_map = {}
        self.table_map = {}     # Maps table names to list of aliases.
        self.join_map = {}
        self.default_cols = True
        self.default_ordering = True
        self.standard_ordering = True
        self.used_aliases = set()
        self.filter_is_sticky = False
        self.included_inherited_models = {}

        # SQL-related attributes
        # Select and related select clauses as SelectInfo instances.
        # The select is used for cases where we want to set up the select
        # clause to contain other than default fields (values(), annotate(),
        # subqueries...)
        self.select = []
        # The related_select_cols is used for columns needed for
        # select_related - this is populated in compile stage.
        self.related_select_cols = []
        self.tables = []    # Aliases in the order they are created.
        self.where = where()
        self.where_class = where
        self.group_by = None
        self.having = where()
        self.order_by = []
        self.low_mark, self.high_mark = 0, None  # Used for offset/limit
        self.distinct = False
        self.distinct_fields = []
        self.select_for_update = False
        self.select_for_update_nowait = False
        self.select_related = False

        # SQL aggregate-related attributes
        self.aggregates = SortedDict() # Maps alias -> SQL aggregate function
        self.aggregate_select_mask = None
        self._aggregate_select_cache = None

        # Arbitrary maximum limit for select_related. Prevents infinite
        # recursion. Can be changed by the depth parameter to select_related().
        self.max_depth = 5

        # These are for extensions. The contents are more or less appended
        # verbatim to the appropriate clause.
        self.extra = SortedDict()  # Maps col_alias -> (col_sql, params).
        self.extra_select_mask = None
        self._extra_select_cache = None

        self.extra_tables = ()
        self.extra_order_by = ()

        # A tuple that is a set of model field names and either True, if these
        # are the fields to defer, or False if these are the only fields to
        # load.
        self.deferred_loading = (set(), True)

    def __str__(self):
        """
        Returns the query as a string of SQL with the parameter values
        substituted in (use sql_with_params() to see the unsubstituted string).

        Parameter values won't necessarily be quoted correctly, since that is
        done by the database interface at execution time.
        """
        sql, params = self.sql_with_params()
        return sql % params

    def sql_with_params(self):
        """
        Returns the query as an SQL string and the parameters that will be
        subsituted into the query.
        """
        return self.get_compiler(DEFAULT_DB_ALIAS).as_sql()

    def __deepcopy__(self, memo):
        result = self.clone(memo=memo)
        memo[id(self)] = result
        return result

    def prepare(self):
        return self

    def get_compiler(self, using=None, connection=None):
        if using is None and connection is None:
            raise ValueError("Need either using or connection")
        if using:
            connection = connections[using]

        # Check that the compiler will be able to execute the query
        for alias, aggregate in self.aggregate_select.items():
            connection.ops.check_aggregate_support(aggregate)

        return connection.ops.compiler(self.compiler)(self, connection, using)

    def get_meta(self):
        """
        Returns the Options instance (the model._meta) from which to start
        processing. Normally, this is self.model._meta, but it can be changed
        by subclasses.
        """
        return self.model._meta

    def clone(self, klass=None, memo=None, **kwargs):
        """
        Creates a copy of the current instance. The 'kwargs' parameter can be
        used by clients to update attributes after copying has taken place.
        """
        obj = Empty()
        obj.__class__ = klass or self.__class__
        obj.model = self.model
        obj.alias_refcount = self.alias_refcount.copy()
        obj.alias_map = self.alias_map.copy()
        obj.table_map = self.table_map.copy()
        obj.join_map = self.join_map.copy()
        obj.default_cols = self.default_cols
        obj.default_ordering = self.default_ordering
        obj.standard_ordering = self.standard_ordering
        obj.included_inherited_models = self.included_inherited_models.copy()
        obj.select = self.select[:]
        obj.related_select_cols = []
        obj.tables = self.tables[:]
        obj.where = self.where.clone()
        obj.where_class = self.where_class
        if self.group_by is None:
            obj.group_by = None
        else:
            obj.group_by = self.group_by[:]
        obj.having = self.having.clone()
        obj.order_by = self.order_by[:]
        obj.low_mark, obj.high_mark = self.low_mark, self.high_mark
        obj.distinct = self.distinct
        obj.distinct_fields = self.distinct_fields[:]
        obj.select_for_update = self.select_for_update
        obj.select_for_update_nowait = self.select_for_update_nowait
        obj.select_related = self.select_related
        obj.related_select_cols = []
        obj.aggregates = self.aggregates.copy()
        if self.aggregate_select_mask is None:
            obj.aggregate_select_mask = None
        else:
            obj.aggregate_select_mask = self.aggregate_select_mask.copy()
        # _aggregate_select_cache cannot be copied, as doing so breaks the
        # (necessary) state in which both aggregates and
        # _aggregate_select_cache point to the same underlying objects.
        # It will get re-populated in the cloned queryset the next time it's
        # used.
        obj._aggregate_select_cache = None
        obj.max_depth = self.max_depth
        obj.extra = self.extra.copy()
        if self.extra_select_mask is None:
            obj.extra_select_mask = None
        else:
            obj.extra_select_mask = self.extra_select_mask.copy()
        if self._extra_select_cache is None:
            obj._extra_select_cache = None
        else:
            obj._extra_select_cache = self._extra_select_cache.copy()
        obj.extra_tables = self.extra_tables
        obj.extra_order_by = self.extra_order_by
        obj.deferred_loading = copy.copy(self.deferred_loading[0]), self.deferred_loading[1]
        if self.filter_is_sticky and self.used_aliases:
            obj.used_aliases = self.used_aliases.copy()
        else:
            obj.used_aliases = set()
        obj.filter_is_sticky = False

        obj.__dict__.update(kwargs)
        if hasattr(obj, '_setup_query'):
            obj._setup_query()
        return obj

    def convert_values(self, value, field, connection):
        """Convert the database-returned value into a type that is consistent
        across database backends.

        By default, this defers to the underlying backend operations, but
        it can be overridden by Query classes for specific backends.
        """
        return connection.ops.convert_values(value, field)

    def resolve_aggregate(self, value, aggregate, connection):
        """Resolve the value of aggregates returned by the database to
        consistent (and reasonable) types.

        This is required because of the predisposition of certain backends
        to return Decimal and long types when they are not needed.
        """
        if value is None:
            if aggregate.is_ordinal:
                return 0
            # Return None as-is
            return value
        elif aggregate.is_ordinal:
            # Any ordinal aggregate (e.g., count) returns an int
            return int(value)
        elif aggregate.is_computed:
            # Any computed aggregate (e.g., avg) returns a float
            return float(value)
        else:
            # Return value depends on the type of the field being processed.
            return self.convert_values(value, aggregate.field, connection)

    def get_aggregation(self, using):
        """
        Returns the dictionary with the values of the existing aggregations.
        """
        if not self.aggregate_select:
            return {}

        # If there is a group by clause, aggregating does not add useful
        # information but retrieves only the first row. Aggregate
        # over the subquery instead.
        if self.group_by is not None:
            from django.db.models.sql.subqueries import AggregateQuery
            query = AggregateQuery(self.model)

            obj = self.clone()

            # Remove any aggregates marked for reduction from the subquery
            # and move them to the outer AggregateQuery.
            for alias, aggregate in self.aggregate_select.items():
                if aggregate.is_summary:
                    query.aggregate_select[alias] = aggregate
                    del obj.aggregate_select[alias]

            try:
                query.add_subquery(obj, using)
            except EmptyResultSet:
                return dict(
                    (alias, None)
                    for alias in query.aggregate_select
                )
        else:
            query = self
            self.select = []
            self.default_cols = False
            self.extra = {}
            self.remove_inherited_models()

        query.clear_ordering(True)
        query.clear_limits()
        query.select_for_update = False
        query.select_related = False
        query.related_select_cols = []

        result = query.get_compiler(using).execute_sql(SINGLE)
        if result is None:
            result = [None for q in query.aggregate_select.items()]

        return dict([
            (alias, self.resolve_aggregate(val, aggregate, connection=connections[using]))
            for (alias, aggregate), val
            in zip(query.aggregate_select.items(), result)
        ])

    def get_count(self, using):
        """
        Performs a COUNT() query using the current filter constraints.
        """
        obj = self.clone()
        if len(self.select) > 1 or self.aggregate_select or (self.distinct and self.distinct_fields):
            # If a select clause exists, then the query has already started to
            # specify the columns that are to be returned.
            # In this case, we need to use a subquery to evaluate the count.
            from django.db.models.sql.subqueries import AggregateQuery
            subquery = obj
            subquery.clear_ordering(True)
            subquery.clear_limits()

            obj = AggregateQuery(obj.model)
            try:
                obj.add_subquery(subquery, using=using)
            except EmptyResultSet:
                # add_subquery evaluates the query, if it's an EmptyResultSet
                # then there are can be no results, and therefore there the
                # count is obviously 0
                return 0

        obj.add_count_column()
        number = obj.get_aggregation(using=using)[None]

        # Apply offset and limit constraints manually, since using LIMIT/OFFSET
        # in SQL (in variants that provide them) doesn't change the COUNT
        # output.
        number = max(0, number - self.low_mark)
        if self.high_mark is not None:
            number = min(number, self.high_mark - self.low_mark)

        return number

    def has_results(self, using):
        q = self.clone()
        q.clear_select_clause()
        q.add_extra({'a': 1}, None, None, None, None, None)
        q.set_extra_mask(['a'])
        q.clear_ordering(True)
        q.set_limits(high=1)
        compiler = q.get_compiler(using=using)
        return bool(compiler.execute_sql(SINGLE))

    def combine(self, rhs, connector):
        """
        Merge the 'rhs' query into the current one (with any 'rhs' effects
        being applied *after* (that is, "to the right of") anything in the
        current query. 'rhs' is not modified during a call to this function.

        The 'connector' parameter describes how to connect filters from the
        'rhs' query.
        """
        assert self.model == rhs.model, \
                "Cannot combine queries on two different base models."
        assert self.can_filter(), \
                "Cannot combine queries once a slice has been taken."
        assert self.distinct == rhs.distinct, \
            "Cannot combine a unique query with a non-unique query."
        assert self.distinct_fields == rhs.distinct_fields, \
            "Cannot combine queries with different distinct fields."

        self.remove_inherited_models()
        # Work out how to relabel the rhs aliases, if necessary.
        change_map = {}
        conjunction = (connector == AND)

        # Determine which existing joins can be reused. When combining the
        # query with AND we must recreate all joins for m2m filters. When
        # combining with OR we can reuse joins. The reason is that in AND
        # case a single row can't fulfill a condition like:
        #     revrel__col=1 & revrel__col=2
        # But, there might be two different related rows matching this
        # condition. In OR case a single True is enough, so single row is
        # enough, too.
        #
        # Note that we will be creating duplicate joins for non-m2m joins in
        # the AND case. The results will be correct but this creates too many
        # joins. This is something that could be fixed later on.
        reuse = set() if conjunction else set(self.tables)
        # Base table must be present in the query - this is the same
        # table on both sides.
        self.get_initial_alias()
        # Now, add the joins from rhs query into the new query (skipping base
        # table).
        for alias in rhs.tables[1:]:
            table, _, join_type, lhs, join_cols, nullable, join_field = rhs.alias_map[alias]
            promote = (join_type == self.LOUTER)
            # If the left side of the join was already relabeled, use the
            # updated alias.
            lhs = change_map.get(lhs, lhs)
            new_alias = self.join(
                (lhs, table, join_cols), reuse=reuse,
                outer_if_first=not conjunction, nullable=nullable,
                join_field=join_field)
            if promote:
                self.promote_joins([new_alias])
            # We can't reuse the same join again in the query. If we have two
            # distinct joins for the same connection in rhs query, then the
            # combined query must have two joins, too.
            reuse.discard(new_alias)
            change_map[alias] = new_alias
            if not rhs.alias_refcount[alias]:
                # The alias was unused in the rhs query. Unref it so that it
                # will be unused in the new query, too. We have to add and
                # unref the alias so that join promotion has information of
                # the join type for the unused alias.
                self.unref_alias(new_alias)

        # So that we don't exclude valid results in an OR query combination,
        # all joins exclusive to either the lhs or the rhs must be converted
        # to an outer join. RHS joins were already set to outer joins above,
        # so check which joins were used only in the lhs query.
        if not conjunction:
            rhs_used_joins = set(change_map.values())
            to_promote = [alias for alias in self.tables
                          if alias not in rhs_used_joins]
            self.promote_joins(to_promote, True)

        # Now relabel a copy of the rhs where-clause and add it to the current
        # one.
        if rhs.where:
            w = rhs.where.clone()
            w.relabel_aliases(change_map)
            if not self.where:
                # Since 'self' matches everything, add an explicit "include
                # everything" where-constraint so that connections between the
                # where clauses won't exclude valid results.
                self.where.add(EverythingNode(), AND)
        elif self.where:
            # rhs has an empty where clause.
            w = self.where_class()
            w.add(EverythingNode(), AND)
        else:
            w = self.where_class()
        self.where.add(w, connector)

        # Selection columns and extra extensions are those provided by 'rhs'.
        self.select = []
        for col, field in rhs.select:
            if isinstance(col, (list, tuple)):
                new_col = change_map.get(col[0], col[0]), col[1]
                self.select.append(SelectInfo(new_col, field))
            else:
                new_col = col.relabeled_clone(change_map)
                self.select.append(SelectInfo(new_col, field))

        if connector == OR:
            # It would be nice to be able to handle this, but the queries don't
            # really make sense (or return consistent value sets). Not worth
            # the extra complexity when you can write a real query instead.
            if self.extra and rhs.extra:
                raise ValueError("When merging querysets using 'or', you "
                        "cannot have extra(select=...) on both sides.")
        self.extra.update(rhs.extra)
        extra_select_mask = set()
        if self.extra_select_mask is not None:
            extra_select_mask.update(self.extra_select_mask)
        if rhs.extra_select_mask is not None:
            extra_select_mask.update(rhs.extra_select_mask)
        if extra_select_mask:
            self.set_extra_mask(extra_select_mask)
        self.extra_tables += rhs.extra_tables

        # Ordering uses the 'rhs' ordering, unless it has none, in which case
        # the current ordering is used.
        self.order_by = rhs.order_by[:] if rhs.order_by else self.order_by
        self.extra_order_by = rhs.extra_order_by or self.extra_order_by

    def deferred_to_data(self, target, callback):
        """
        Converts the self.deferred_loading data structure to an alternate data
        structure, describing the field that *will* be loaded. This is used to
        compute the columns to select from the database and also by the
        QuerySet class to work out which fields are being initialised on each
        model. Models that have all their fields included aren't mentioned in
        the result, only those that have field restrictions in place.

        The "target" parameter is the instance that is populated (in place).
        The "callback" is a function that is called whenever a (model, field)
        pair need to be added to "target". It accepts three parameters:
        "target", and the model and list of fields being added for that model.
        """
        field_names, defer = self.deferred_loading
        if not field_names:
            return
        orig_opts = self.get_meta()
        seen = {}
        must_include = {orig_opts.concrete_model: set([orig_opts.pk])}
        for field_name in field_names:
            parts = field_name.split(LOOKUP_SEP)
            cur_model = self.model
            opts = orig_opts
            for name in parts[:-1]:
                old_model = cur_model
                source = opts.get_field_by_name(name)[0]
                if is_reverse_o2o(source):
                    cur_model = source.model
                else:
                    cur_model = source.rel.to
                opts = cur_model._meta
                # Even if we're "just passing through" this model, we must add
                # both the current model's pk and the related reference field
                # (if it's not a reverse relation) to the things we select.
                if not is_reverse_o2o(source):
                    must_include[old_model].add(source)
                add_to_dict(must_include, cur_model, opts.pk)
            field, model, _, _ = opts.get_field_by_name(parts[-1])
            if model is None:
                model = cur_model
            if not is_reverse_o2o(field):
                add_to_dict(seen, model, field)

        if defer:
            # We need to load all fields for each model, except those that
            # appear in "seen" (for all models that appear in "seen"). The only
            # slight complexity here is handling fields that exist on parent
            # models.
            workset = {}
            for model, values in six.iteritems(seen):
                for field, m in model._meta.get_fields_with_model():
                    if field in values:
                        continue
                    add_to_dict(workset, m or model, field)
            for model, values in six.iteritems(must_include):
                # If we haven't included a model in workset, we don't add the
                # corresponding must_include fields for that model, since an
                # empty set means "include all fields". That's why there's no
                # "else" branch here.
                if model in workset:
                    workset[model].update(values)
            for model, values in six.iteritems(workset):
                callback(target, model, values)
        else:
            for model, values in six.iteritems(must_include):
                if model in seen:
                    seen[model].update(values)
                else:
                    # As we've passed through this model, but not explicitly
                    # included any fields, we have to make sure it's mentioned
                    # so that only the "must include" fields are pulled in.
                    seen[model] = values
            # Now ensure that every model in the inheritance chain is mentioned
            # in the parent list. Again, it must be mentioned to ensure that
            # only "must include" fields are pulled in.
            for model in orig_opts.get_parent_list():
                if model not in seen:
                    seen[model] = set()
            for model, values in six.iteritems(seen):
                callback(target, model, values)


    def deferred_to_columns_cb(self, target, model, fields):
        """
        Callback used by deferred_to_columns(). The "target" parameter should
        be a set instance.
        """
        table = model._meta.db_table
        if table not in target:
            target[table] = set()
        for field in fields:
            target[table].add(field.column)


    def table_alias(self, table_name, create=False):
        """
        Returns a table alias for the given table_name and whether this is a
        new alias or not.

        If 'create' is true, a new alias is always created. Otherwise, the
        most recently created alias for the table (if one exists) is reused.
        """
        current = self.table_map.get(table_name)
        if not create and current:
            alias = current[0]
            self.alias_refcount[alias] += 1
            return alias, False

        # Create a new alias for this table.
        if current:
            alias = '%s%d' % (self.alias_prefix, len(self.alias_map) + 1)
            current.append(alias)
        else:
            # The first occurence of a table uses the table name directly.
            alias = table_name
            self.table_map[alias] = [alias]
        self.alias_refcount[alias] = 1
        self.tables.append(alias)
        return alias, True

    def ref_alias(self, alias):
        """ Increases the reference count for this alias. """
        self.alias_refcount[alias] += 1

    def unref_alias(self, alias, amount=1):
        """ Decreases the reference count for this alias. """
        self.alias_refcount[alias] -= amount

    def promote_joins(self, aliases, unconditional=False):
        """
        Promotes recursively the join type of given aliases and its children to
        an outer join. If 'unconditional' is False, the join is only promoted if
        it is nullable or the parent join is an outer join.

        Note about join promotion: When promoting any alias, we make sure all
        joins which start from that alias are promoted, too. When adding a join
        in join(), we make sure any join added to already existing LOUTER join
        is generated as LOUTER. This ensures we don't ever have broken join
        chains which contain first a LOUTER join, then an INNER JOIN, that is
        this kind of join should never be generated: a LOUTER b INNER c. The
        reason for avoiding this type of join chain is that the INNER after
        the LOUTER will effectively remove any effect the LOUTER had.
        """
        aliases = list(aliases)
        while aliases:
            alias = aliases.pop(0)
            if self.alias_map[alias].join_cols[0][1] is None:
                # This is the base table (first FROM entry) - this table
                # isn't really joined at all in the query, so we should not
                # alter its join type.
                continue
            parent_alias = self.alias_map[alias].lhs_alias
            parent_louter = (parent_alias
                and self.alias_map[parent_alias].join_type == self.LOUTER)
            already_louter = self.alias_map[alias].join_type == self.LOUTER
            if ((unconditional or self.alias_map[alias].nullable
                 or parent_louter) and not already_louter):
                data = self.alias_map[alias]._replace(join_type=self.LOUTER)
                self.alias_map[alias] = data
                # Join type of 'alias' changed, so re-examine all aliases that
                # refer to this one.
                aliases.extend(
                    join for join in self.alias_map.keys()
                    if (self.alias_map[join].lhs_alias == alias
                        and join not in aliases))

    def reset_refcounts(self, to_counts):
        """
        This method will reset reference counts for aliases so that they match
        the value passed in :param to_counts:.
        """
        for alias, cur_refcount in self.alias_refcount.copy().items():
            unref_amount = cur_refcount - to_counts.get(alias, 0)
            self.unref_alias(alias, unref_amount)

    def promote_disjunction(self, aliases_before, alias_usage_counts,
                            num_childs):
        """
        This method is to be used for promoting joins in ORed filters.

        The principle for promotion is: any alias which is used (it is in
        alias_usage_counts), is not used by every child of the ORed filter,
        and isn't pre-existing needs to be promoted to LOUTER join.
        """
        for alias, use_count in alias_usage_counts.items():
            if use_count < num_childs and alias not in aliases_before:
                self.promote_joins([alias])

    def change_aliases(self, change_map):
        """
        Changes the aliases in change_map (which maps old-alias -> new-alias),
        relabelling any references to them in select columns and the where
        clause.
        """
        assert set(change_map.keys()).intersection(set(change_map.values())) == set()

        def relabel_column(col):
            if isinstance(col, (list, tuple)):
                old_alias = col[0]
                return (change_map.get(old_alias, old_alias), col[1])
            else:
                return col.relabeled_clone(change_map)
        # 1. Update references in "select" (normal columns plus aliases),
        # "group by", "where" and "having".
        self.where.relabel_aliases(change_map)
        self.having.relabel_aliases(change_map)
        if self.group_by:
            self.group_by = [relabel_column(col) for col in self.group_by]
        self.select = [SelectInfo(relabel_column(s.col), s.field)
                       for s in self.select]
        self.aggregates = SortedDict(
            (key, relabel_column(col)) for key, col in self.aggregates.items())

        # 2. Rename the alias in the internal table/alias datastructures.
        for ident, aliases in self.join_map.items():
            del self.join_map[ident]
            aliases = tuple([change_map.get(a, a) for a in aliases])
            ident = (change_map.get(ident[0], ident[0]),) + ident[1:]
            self.join_map[ident] = aliases
        for old_alias, new_alias in six.iteritems(change_map):
            alias_data = self.alias_map[old_alias]
            alias_data = alias_data._replace(rhs_alias=new_alias)
            self.alias_refcount[new_alias] = self.alias_refcount[old_alias]
            del self.alias_refcount[old_alias]
            self.alias_map[new_alias] = alias_data
            del self.alias_map[old_alias]

            table_aliases = self.table_map[alias_data.table_name]
            for pos, alias in enumerate(table_aliases):
                if alias == old_alias:
                    table_aliases[pos] = new_alias
                    break
            for pos, alias in enumerate(self.tables):
                if alias == old_alias:
                    self.tables[pos] = new_alias
                    break
        for key, alias in self.included_inherited_models.items():
            if alias in change_map:
                self.included_inherited_models[key] = change_map[alias]

        # 3. Update any joins that refer to the old alias.
        for alias, data in six.iteritems(self.alias_map):
            lhs = data.lhs_alias
            if lhs in change_map:
                data = data._replace(lhs_alias=change_map[lhs])
                self.alias_map[alias] = data
        # 4. Update the temporary _lookup_joins list
        if hasattr(self, '_lookup_joins'):
            self._lookup_joins = [change_map.get(lj, lj) for lj in self._lookup_joins]

    def bump_prefix(self, exceptions=()):
        """
        Changes the alias prefix to the next letter in the alphabet and
        relabels all the aliases. Even tables that previously had no alias will
        get an alias after this call (it's mostly used for nested queries and
        the outer query will already be using the non-aliased table name).

        Subclasses who create their own prefix should override this method to
        produce a similar result (a new prefix and relabelled aliases).

        The 'exceptions' parameter is a container that holds alias names which
        should not be changed.
        """
        current = ord(self.alias_prefix)
        assert current < ord('Z')
        prefix = chr(current + 1)
        self.alias_prefix = prefix
        change_map = SortedDict()
        for pos, alias in enumerate(self.tables):
            if alias in exceptions:
                continue
            new_alias = '%s%d' % (prefix, pos)
            change_map[alias] = new_alias
            self.tables[pos] = new_alias
        self.change_aliases(change_map)

    def get_initial_alias(self):
        """
        Returns the first alias for this query, after increasing its reference
        count.
        """
        if self.tables:
            alias = self.tables[0]
            self.ref_alias(alias)
        else:
            alias = self.join((None, self.get_meta().db_table, None))
        return alias

    def count_active_tables(self):
        """
        Returns the number of tables in this query with a non-zero reference
        count. Note that after execution, the reference counts are zeroed, so
        tables added in compiler will not be seen by this method.
        """
        return len([1 for count in self.alias_refcount.values() if count])

    def join(self, connection, reuse=None, outer_if_first=False,
             nullable=False, join_field=None):
        """
        Returns an alias for the join in 'connection', either reusing an
        existing alias for that join or creating a new one. 'connection' is a
        tuple (lhs, table, join_cols) where 'lhs' is either an existing
        table alias or a table name. 'join_cols' is a tuple of tuples containing
        columns to join on ((l_id1, r_id1), (l_id2, r_id2)). The join corresponds
        to the SQL equivalent of::

            lhs.l_id1 = table.r_id1 AND lhs.l_id2 = table.r_id2

        The 'reuse' parameter can be either None which means all joins
        (matching the connection) are reusable, or it can be a set containing
        the aliases that can be reused.

        If 'outer_if_first' is True and a new join is created, it will have the
        LOUTER join type.

        A join is always created as LOUTER if the lhs alias is LOUTER to make
        sure we do not generate chains like t1 LOUTER t2 INNER t3.

        If 'nullable' is True, the join can potentially involve NULL values and
        is a candidate for promotion (to "left outer") when combining querysets.

        The 'join_field' is the field we are joining along (if any).
        """
        lhs, table, join_cols = connection
        assert lhs is None or join_field is not None
        existing = self.join_map.get(connection, ())
        if reuse is None:
            reuse = existing
        else:
            reuse = [a for a in existing if a in reuse]
        for alias in reuse:
            if join_field and self.alias_map[alias].join_field != join_field:
                # The join_map doesn't contain join_field (mainly because
                # fields in Query structs are problematic in pickling), so
                # check that the existing join is created using the same
                # join_field used for the under work join.
                continue
            self.ref_alias(alias)
            return alias

        # No reuse is possible, so we need a new alias.
        alias, _ = self.table_alias(table, True)
        if not lhs:
            # Not all tables need to be joined to anything. No join type
            # means the later columns are ignored.
            join_type = None
        elif outer_if_first or self.alias_map[lhs].join_type == self.LOUTER:
            # We need to use LOUTER join if asked by outer_if_first or if the
            # LHS table is left-joined in the query.
            join_type = self.LOUTER
        else:
            join_type = self.INNER
        join = JoinInfo(table, alias, join_type, lhs, join_cols or ((None, None),), nullable,
                        join_field)
        self.alias_map[alias] = join
        if connection in self.join_map:
            self.join_map[connection] += (alias,)
        else:
            self.join_map[connection] = (alias,)
        return alias

    def setup_inherited_models(self):
        """
        If the model that is the basis for this QuerySet inherits other models,
        we need to ensure that those other models have their tables included in
        the query.

        We do this as a separate step so that subclasses know which
        tables are going to be active in the query, without needing to compute
        all the select columns (this method is called from pre_sql_setup(),
        whereas column determination is a later part, and side-effect, of
        as_sql()).
        """
        opts = self.get_meta()
        root_alias = self.tables[0]
        seen = {None: root_alias}

        for field, model in opts.get_fields_with_model():
            if model not in seen:
                self.join_parent_model(opts, model, root_alias, seen)
        self.included_inherited_models = seen

    def join_parent_model(self, opts, model, alias, seen):
        """
        Makes sure the given 'model' is joined in the query. If 'model' isn't
        a parent of 'opts' or if it is None this method is a no-op.

        The 'alias' is the root alias for starting the join, 'seen' is a dict
        of model -> alias of existing joins. It must also contain a mapping
        of None -> some alias. This will be returned in the no-op case.
        """
        if model in seen:
            return seen[model]
        chain = opts.get_base_chain(model)
        if chain is None:
            return alias
        curr_opts = opts
        for int_model in chain:
            if int_model in seen:
                return seen[int_model]
            # Proxy model have elements in base chain
            # with no parents, assign the new options
            # object and skip to the next base in that
            # case
            if not curr_opts.parents[int_model]:
                curr_opts = int_model._meta
                continue
            link_field = curr_opts.get_ancestor_link(int_model)
            _, _, _, joins, _ = self.setup_joins(
                [link_field.name], curr_opts, alias)
            curr_opts = int_model._meta
            alias = seen[int_model] = joins[-1]
        return alias or seen[None]

    def remove_inherited_models(self):
        """
        Undoes the effects of setup_inherited_models(). Should be called
        whenever select columns (self.select) are set explicitly.
        """
        for key, alias in self.included_inherited_models.items():
            if key:
                self.unref_alias(alias)
        self.included_inherited_models = {}


    def add_aggregate(self, aggregate, model, alias, is_summary):
        """
        Adds a single aggregate expression to the Query
        """
        opts = model._meta
        field_list = aggregate.lookup.split(LOOKUP_SEP)
        if len(field_list) == 1 and aggregate.lookup in self.aggregates:
            # Aggregate is over an annotation
            field_name = field_list[0]
            col = field_name
            source = self.aggregates[field_name]
            if not is_summary:
                raise FieldError("Cannot compute %s('%s'): '%s' is an aggregate" % (
                    aggregate.name, field_name, field_name))
        elif ((len(field_list) > 1) or
            (field_list[0] not in [i.name for i in opts.fields]) or
            self.group_by is None or
            not is_summary):
            # If:
            #   - the field descriptor has more than one part (foo__bar), or
            #   - the field descriptor is referencing an m2m/m2o field, or
            #   - this is a reference to a model field (possibly inherited), or
            #   - this is an annotation over a model field
            # then we need to explore the joins that are required.

            field, sources, opts, join_list, path = self.setup_joins(
                field_list, opts, self.get_initial_alias())

            # Process the join chain to see if it can be trimmed
            targets, _, join_list = self.trim_joins(sources, join_list, path)

            # If the aggregate references a model or field that requires a join,
            # those joins must be LEFT OUTER - empty join rows must be returned
            # in order for zeros to be returned for those aggregates.
            self.promote_joins(join_list, True)

            col = targets[0].column
            source = sources[0]
            col = (join_list[-1], col)
        else:
            # The simplest cases. No joins required -
            # just reference the provided column alias.
            field_name = field_list[0]
            source = opts.get_field(field_name)
            col = field_name

        # Add the aggregate to the query
        aggregate.add_to_query(self, alias, col=col, source=source, is_summary=is_summary)

    def build_filter(self, filter_expr, branch_negated=False, current_negated=False,
                     can_reuse=None):
        """
        Builds a WhereNode for a single filter clause, but doesn't add it
        to this Query. Query.add_q() will then add this filter to the where
        or having Node.

        The 'branch_negated' tells us if the current branch contains any
        negations. This will be used to determine if subqueries are needed.

        The 'current_negated' is used to determine if the current filter is
        negated or not and this will be used to determine if IS NULL filtering
        is needed.

        The difference between current_netageted and branch_negated is that
        branch_negated is set on first negation, but current_negated is
        flipped for each negation.

        Note that add_filter will not do any negating itself, that is done
        upper in the code by add_q().

        The 'can_reuse' is a set of reusable joins for multijoins.

        The method will create a filter clause that can be added to the current
        query. However, if the filter isn't added to the query then the caller
        is responsible for unreffing the joins used.
        """
        arg, value = filter_expr
        parts = arg.split(LOOKUP_SEP)
        if not parts:
            raise FieldError("Cannot parse keyword query %r" % arg)

        # Work out the lookup type and remove it from the end of 'parts',
        # if necessary.
        lookup_type = 'exact'  # Default lookup type
        num_parts = len(parts)
        if (len(parts) > 1 and parts[-1] in self.query_terms
                and arg not in self.aggregates):
            # Traverse the lookup query to distinguish related fields from
            # lookup types.
            lookup_model = self.model
            for counter, field_name in enumerate(parts):
                try:
                    lookup_field = lookup_model._meta.get_field(field_name)
                except FieldDoesNotExist:
                    # Not a field. Bail out.
                    lookup_type = parts.pop()
                    break
                # Unless we're at the end of the list of lookups, let's attempt
                # to continue traversing relations.
                if (counter + 1) < num_parts:
                    try:
                        lookup_model = lookup_field.rel.to
                    except AttributeError:
                        # Not a related field. Bail out.
                        lookup_type = parts.pop()
                        break

        clause = self.where_class()
        # Interpret '__exact=None' as the sql 'is NULL'; otherwise, reject all
        # uses of None as a query value.
        if value is None:
            if lookup_type != 'exact':
                raise ValueError("Cannot use None as a query value")
            lookup_type = 'isnull'
            value = True
        elif callable(value):
            value = value()
        elif isinstance(value, ExpressionNode):
            # If value is a query expression, evaluate it
            value = SQLEvaluator(value, self, reuse=can_reuse)
        # For Oracle '' is equivalent to null. The check needs to be done
        # at this stage because join promotion can't be done at compiler
        # stage. Using DEFAULT_DB_ALIAS isn't nice, but it is the best we
        # can do here. Similar thing is done in is_nullable(), too.
        if (connections[DEFAULT_DB_ALIAS].features.interprets_empty_strings_as_nulls and
                lookup_type == 'exact' and value == ''):
            value = True
            lookup_type = 'isnull'

        for alias, aggregate in self.aggregates.items():
            if alias in (parts[0], LOOKUP_SEP.join(parts)):
                clause.add((aggregate, lookup_type, value), AND)
                return clause

        opts = self.get_meta()
        alias = self.get_initial_alias()
        allow_many = not branch_negated

        try:
            field, sources, opts, join_list, path = self.setup_joins(
                    parts, opts, alias, can_reuse, allow_many,
                    allow_explicit_fk=True)
            if can_reuse is not None:
                can_reuse.update(join_list)
            # split_exclude() needs to know which joins were generated for the
            # lookup parts
            self._lookup_joins = join_list
        except MultiJoin as e:
            return self.split_exclude(filter_expr, LOOKUP_SEP.join(parts[:e.level]),
                                      can_reuse, e.names_with_path)

        if (lookup_type == 'isnull' and value is True and not current_negated and
                len(join_list) > 1):
            # If the comparison is against NULL, we may need to use some left
            # outer joins when creating the join chain. This is only done when
            # needed, as it's less efficient at the database level.
            self.promote_joins(join_list)

        # Process the join list to see if we can remove any inner joins from
        # the far end (fewer tables in a query is better). Note that join
        # promotion must happen before join trimming to have the join type
        # information available when reusing joins.
        targets, alias, join_list = self.trim_joins(sources, join_list, path)

        if hasattr(field, 'get_lookup_constraint'):
            constraint = field.get_lookup_constraint(self.where_class, alias, targets, sources,
                                                     lookup_type, value)
        else:
            constraint = (Constraint(alias, targets[0].column, field), lookup_type, value)
        clause.add(constraint, AND)
        if current_negated and (lookup_type != 'isnull' or value is False):
            self.promote_joins(join_list)
            if (lookup_type != 'isnull' and (
                    self.is_nullable(targets[0]) or
                    self.alias_map[join_list[-1]].join_type == self.LOUTER)):
                # The condition added here will be SQL like this:
                # NOT (col IS NOT NULL), where the first NOT is added in
                # upper layers of code. The reason for addition is that if col
                # is null, then col != someval will result in SQL "unknown"
                # which isn't the same as in Python. The Python None handling
                # is wanted, and it can be gotten by
                # (col IS NULL OR col != someval)
                #   <=>
                # NOT (col IS NOT NULL AND col = someval).
                clause.add((Constraint(alias, targets[0].column, None), 'isnull', False), AND)
        return clause

    def add_filter(self, filter_clause):
        self.where.add(self.build_filter(filter_clause), 'AND')

    def need_having(self, obj):
        """
        Returns whether or not all elements of this q_object need to be put
        together in the HAVING clause.
        """
        if not isinstance(obj, Node):
            return (refs_aggregate(obj[0].split(LOOKUP_SEP), self.aggregates)
                    or (hasattr(obj[1], 'contains_aggregate')
                        and obj[1].contains_aggregate(self.aggregates)))
        return any(self.need_having(c) for c in obj.children)

    def split_having_parts(self, q_object, negated=False):
        """
        Returns a list of q_objects which need to go into the having clause
        instead of the where clause. Removes the splitted out nodes from the
        given q_object. Note that the q_object is altered, so cloning it is
        needed.
        """
        having_parts = []
        for c in q_object.children[:]:
            # When constucting the having nodes we need to take care to
            # preserve the negation status from the upper parts of the tree
            if isinstance(c, Node):
                # For each negated child, flip the in_negated flag.
                in_negated = c.negated ^ negated
                if c.connector == OR and self.need_having(c):
                    # A subtree starting from OR clause must go into having in
                    # whole if any part of that tree references an aggregate.
                    q_object.children.remove(c)
                    having_parts.append(c)
                    c.negated = in_negated
                else:
                    having_parts.extend(
                        self.split_having_parts(c, in_negated)[1])
            elif self.need_having(c):
                q_object.children.remove(c)
                new_q = self.where_class(children=[c], negated=negated)
                having_parts.append(new_q)
        return q_object, having_parts

    def add_q(self, q_object):
        """
        A preprocessor for the internal _add_q(). Responsible for
        splitting the given q_object into where and having parts and
        setting up some internal variables.
        """
        if not self.need_having(q_object):
            where_part, having_parts = q_object, []
        else:
            where_part, having_parts = self.split_having_parts(
                q_object.clone(), q_object.negated)
        used_aliases = self.used_aliases
        clause = self._add_q(where_part, used_aliases)
        self.where.add(clause, AND)
        for hp in having_parts:
            clause = self._add_q(hp, used_aliases)
            self.having.add(clause, AND)
        if self.filter_is_sticky:
            self.used_aliases = used_aliases

    def _add_q(self, q_object, used_aliases, branch_negated=False,
               current_negated=False):
        """
        Adds a Q-object to the current filter.
        """
        connector = q_object.connector
        current_negated = current_negated ^ q_object.negated
        branch_negated = branch_negated or q_object.negated
        target_clause = self.where_class(connector=connector,
                                         negated=q_object.negated)
        # Treat case NOT (a AND b) like case ((NOT a) OR (NOT b)) for join
        # promotion. See ticket #21748.
        effective_connector = connector
        if current_negated:
            effective_connector = OR if effective_connector == AND else AND
        if effective_connector == OR:
            alias_usage_counts = dict()
            aliases_before = set(self.tables)
        for child in q_object.children:
            if effective_connector == OR:
                refcounts_before = self.alias_refcount.copy()
            if isinstance(child, Node):
                child_clause = self._add_q(
                    child, used_aliases, branch_negated,
                    current_negated)
            else:
                child_clause = self.build_filter(
                    child, can_reuse=used_aliases, branch_negated=branch_negated,
                    current_negated=current_negated)
            target_clause.add(child_clause, connector)
            if effective_connector == OR:
                used = alias_diff(refcounts_before, self.alias_refcount)
                for alias in used:
                    alias_usage_counts[alias] = alias_usage_counts.get(alias, 0) + 1
        if effective_connector == OR:
            self.promote_disjunction(aliases_before, alias_usage_counts,
                                     len(q_object.children))
        return target_clause

    def names_to_path(self, names, opts, allow_many, allow_explicit_fk):
        """
        Walks the names path and turns them PathInfo tuples. Note that a
        single name in 'names' can generate multiple PathInfos (m2m for
        example).

        'names' is the path of names to travle, 'opts' is the model Options we
        start the name resolving from, 'allow_many' and 'allow_explicit_fk'
        are as for setup_joins().

        Returns a list of PathInfo tuples. In addition returns the final field
        (the last used join field), and target (which is a field guaranteed to
        contain the same value as the final field).
        """
        path, names_with_path = [], []
        for pos, name in enumerate(names):
            cur_names_with_path = (name, [])
            if name == 'pk':
                name = opts.pk.name
            try:
                field, model, direct, m2m = opts.get_field_by_name(name)
            except FieldDoesNotExist:
                for f in opts.fields:
                    if allow_explicit_fk and name == f.attname:
                        # XXX: A hack to allow foo_id to work in values() for
                        # backwards compatibility purposes. If we dropped that
                        # feature, this could be removed.
                        field, model, direct, m2m = opts.get_field_by_name(f.name)
                        break
                else:
                    available = opts.get_all_field_names() + list(self.aggregate_select)
                    raise FieldError("Cannot resolve keyword %r into field. "
                                     "Choices are: %s" % (name, ", ".join(available)))
            # Check if we need any joins for concrete inheritance cases (the
            # field lives in parent, but we are currently in one of its
            # children)
            if model:
                # The field lives on a base class of the current model.
                # Skip the chain of proxy to the concrete proxied model
                proxied_model = opts.concrete_model

                for int_model in opts.get_base_chain(model):
                    if int_model is proxied_model:
                        opts = int_model._meta
                    else:
                        final_field = opts.parents[int_model]
                        targets = (final_field.rel.get_related_field(),)
                        opts = int_model._meta
                        path.append(PathInfo(final_field.model._meta, opts, targets, final_field, False, True))
                        cur_names_with_path[1].append(PathInfo(final_field.model._meta, opts, targets, final_field, False, True))
            if hasattr(field, 'get_path_info'):
                pathinfos = field.get_path_info()
                if not allow_many:
                    for inner_pos, p in enumerate(pathinfos):
                        if p.m2m:
                            cur_names_with_path[1].extend(pathinfos[0:inner_pos + 1])
                            names_with_path.append(cur_names_with_path)
                            raise MultiJoin(pos + 1, names_with_path)
                last = pathinfos[-1]
                path.extend(pathinfos)
                final_field = last.join_field
                opts = last.to_opts
                targets = last.target_fields
                cur_names_with_path[1].extend(pathinfos)
                names_with_path.append(cur_names_with_path)
            else:
                # Local non-relational field.
                final_field = field
                targets = (field,)
                break

        if pos != len(names) - 1:
            if pos == len(names) - 2:
                raise FieldError(
                    "Join on field %r not permitted. Did you misspell %r for "
                    "the lookup type?" % (name, names[pos + 1]))
            else:
                raise FieldError("Join on field %r not permitted." % name)
        return path, final_field, targets

    def setup_joins(self, names, opts, alias, can_reuse=None, allow_many=True,
                    allow_explicit_fk=False, outer_if_first=False):
        """
        Compute the necessary table joins for the passage through the fields
        given in 'names'. 'opts' is the Options class for the current model
        (which gives the table we are starting from), 'alias' is the alias for
        the table to start the joining from.

        The 'can_reuse' defines the reverse foreign key joins we can reuse. It
        can be None in which case all joins are reusable or a set of aliases
        that can be reused. Note that non-reverse foreign keys are always
        reusable when using setup_joins().

        If 'allow_many' is False, then any reverse foreign key seen will
        generate a MultiJoin exception.

        The 'allow_explicit_fk' controls if field.attname is allowed in the
        lookups.

        Returns the final field involved in the joins, the target field (used
        for any 'where' constraint), the final 'opts' value, the joins and the
        field path travelled to generate the joins.

        The target field is the field containing the concrete value. Final
        field can be something different, for example foreign key pointing to
        that value. Final field is needed for example in some value
        conversions (convert 'obj' in fk__id=obj to pk val using the foreign
        key field for example).
        """
        joins = [alias]
        # First, generate the path for the names
        path, final_field, targets = self.names_to_path(
            names, opts, allow_many, allow_explicit_fk)
        # Then, add the path to the query's joins. Note that we can't trim
        # joins at this stage - we will need the information about join type
        # of the trimmed joins.
        for pos, join in enumerate(path):
            opts = join.to_opts
            if join.direct:
                nullable = self.is_nullable(join.join_field)
            else:
                nullable = True
            connection = alias, opts.db_table, join.join_field.get_joining_columns()
            reuse = can_reuse if join.m2m else None
            alias = self.join(
                connection, reuse=reuse, nullable=nullable, join_field=join.join_field,
                outer_if_first=outer_if_first)
            joins.append(alias)
        if hasattr(final_field, 'field'):
            final_field = final_field.field
        return final_field, targets, opts, joins, path

    def trim_joins(self, targets, joins, path):
        """
        The 'target' parameter is the final field being joined to, 'joins'
        is the full list of join aliases. The 'path' contain the PathInfos
        used to create the joins.

        Returns the final target field and table alias and the new active
        joins.

        We will always trim any direct join if we have the target column
        available already in the previous table. Reverse joins can't be
        trimmed as we don't know if there is anything on the other side of
        the join.
        """
        for pos, info in enumerate(reversed(path)):
            if len(joins) == 1 or not info.direct:
                break
            join_targets = set(t.column for t in info.join_field.foreign_related_fields)
            cur_targets = set(t.column for t in targets)
            if not cur_targets.issubset(join_targets):
                break
            targets = tuple(r[0] for r in info.join_field.related_fields if r[1].column in cur_targets)
            self.unref_alias(joins.pop())
        return targets, joins[-1], joins

    def split_exclude(self, filter_expr, prefix, can_reuse, names_with_path):
        """
        When doing an exclude against any kind of N-to-many relation, we need
        to use a subquery. This method constructs the nested query, given the
        original exclude filter (filter_expr) and the portion up to the first
        N-to-many relation field.

        As an example we could have original filter ~Q(child__name='foo').
        We would get here with filter_expr = child__name, prefix = child and
        can_reuse is a set of joins usable for filters in the original query.

        We will turn this into equivalent of:
            WHERE NOT (pk IN (SELECT parent_id FROM thetable
                              WHERE name = 'foo' AND parent_id IS NOT NULL))

        It might be worth it to consider using WHERE NOT EXISTS as that has
        saner null handling, and is easier for the backend's optimizer to
        handle.
        """
        # Generate the inner query.
        query = Query(self.model)
        query.where.add(query.build_filter(filter_expr), AND)
        query.bump_prefix()
        query.clear_ordering(True)
        # Try to have as simple as possible subquery -> trim leading joins from
        # the subquery.
        trimmed_prefix, contains_louter = query.trim_start(names_with_path)
        query.remove_inherited_models()

        # Add extra check to make sure the selected field will not be null
        # since we are adding a IN <subquery> clause. This prevents the
        # database from tripping over IN (...,NULL,...) selects and returning
        # nothing
        if self.is_nullable(query.select[0].field):
            alias, col = query.select[0].col
            query.where.add((Constraint(alias, col, query.select[0].field), 'isnull', False), AND)

        condition = self.build_filter(
            ('%s__in' % trimmed_prefix, query),
            current_negated=True, branch_negated=True, can_reuse=can_reuse)
        if contains_louter:
            or_null_condition = self.build_filter(
                ('%s__isnull' % trimmed_prefix, True),
                current_negated=True, branch_negated=True, can_reuse=can_reuse)
            condition.add(or_null_condition, OR)
            # Note that the end result will be:
            # (outercol NOT IN innerq AND outercol IS NOT NULL) OR outercol IS NULL.
            # This might look crazy but due to how IN works, this seems to be
            # correct. If the IS NOT NULL check is removed then outercol NOT
            # IN will return UNKNOWN. If the IS NULL check is removed, then if
            # outercol IS NULL we will not match the row.
        return condition

    def set_empty(self):
        self.where = EmptyWhere()
        self.having = EmptyWhere()

    def is_empty(self):
        return isinstance(self.where, EmptyWhere) or isinstance(self.having, EmptyWhere)

    def set_limits(self, low=None, high=None):
        """
        Adjusts the limits on the rows retrieved. We use low/high to set these,
        as it makes it more Pythonic to read and write. When the SQL query is
        created, they are converted to the appropriate offset and limit values.

        Any limits passed in here are applied relative to the existing
        constraints. So low is added to the current low value and both will be
        clamped to any existing high value.
        """
        if high is not None:
            if self.high_mark is not None:
                self.high_mark = min(self.high_mark, self.low_mark + high)
            else:
                self.high_mark = self.low_mark + high
        if low is not None:
            if self.high_mark is not None:
                self.low_mark = min(self.high_mark, self.low_mark + low)
            else:
                self.low_mark = self.low_mark + low

    def clear_limits(self):
        """
        Clears any existing limits.
        """
        self.low_mark, self.high_mark = 0, None

    def can_filter(self):
        """
        Returns True if adding filters to this instance is still possible.

        Typically, this means no limits or offsets have been put on the results.
        """
        return not self.low_mark and self.high_mark is None

    def clear_select_clause(self):
        """
        Removes all fields from SELECT clause.
        """
        self.select = []
        self.default_cols = False
        self.select_related = False
        self.set_extra_mask(())
        self.set_aggregate_mask(())

    def clear_select_fields(self):
        """
        Clears the list of fields to select (but not extra_select columns).
        Some queryset types completely replace any existing list of select
        columns.
        """
        self.select = []

    def add_distinct_fields(self, *field_names):
        """
        Adds and resolves the given fields to the query's "distinct on" clause.
        """
        self.distinct_fields = field_names
        self.distinct = True

    def add_fields(self, field_names, allow_m2m=True):
        """
        Adds the given (model) fields to the select set. The field names are
        added in the order specified.
        """
        alias = self.get_initial_alias()
        opts = self.get_meta()

        try:
            for name in field_names:
                field, targets, u2, joins, path = self.setup_joins(
                        name.split(LOOKUP_SEP), opts, alias, None, allow_m2m,
                        allow_explicit_fk=True, outer_if_first=True)

                # Trim last join if possible
                targets, final_alias, remaining_joins = self.trim_joins(targets, joins[-2:], path)
                joins = joins[:-2] + remaining_joins

                self.promote_joins(joins[1:])
                for target in targets:
                    self.select.append(SelectInfo((final_alias, target.column), target))
        except MultiJoin:
            raise FieldError("Invalid field name: '%s'" % name)
        except FieldError:
            if LOOKUP_SEP in name:
                # For lookups spanning over relationships, show the error
                # from the model on which the lookup failed.
                raise
            else:
                names = sorted(opts.get_all_field_names() + list(self.extra)
                               + list(self.aggregate_select))
                raise FieldError("Cannot resolve keyword %r into field. "
                                 "Choices are: %s" % (name, ", ".join(names)))
        self.remove_inherited_models()

    def add_ordering(self, *ordering):
        """
        Adds items from the 'ordering' sequence to the query's "order by"
        clause. These items are either field names (not column names) --
        possibly with a direction prefix ('-' or '?') -- or ordinals,
        corresponding to column positions in the 'select' list.

        If 'ordering' is empty, all ordering is cleared from the query.
        """
        errors = []
        for item in ordering:
            if not ORDER_PATTERN.match(item):
                errors.append(item)
        if errors:
            raise FieldError('Invalid order_by arguments: %s' % errors)
        if ordering:
            self.order_by.extend(ordering)
        else:
            self.default_ordering = False

    def clear_ordering(self, force_empty):
        """
        Removes any ordering settings. If 'force_empty' is True, there will be
        no ordering in the resulting query (not even the model's default).
        """
        self.order_by = []
        self.extra_order_by = ()
        if force_empty:
            self.default_ordering = False

    def set_group_by(self):
        """
        Expands the GROUP BY clause required by the query.

        This will usually be the set of all non-aggregate fields in the
        return data. If the database backend supports grouping by the
        primary key, and the query would be equivalent, the optimization
        will be made automatically.
        """
        self.group_by = []

        for col, _ in self.select:
            self.group_by.append(col)

    def add_count_column(self):
        """
        Converts the query to do count(...) or count(distinct(pk)) in order to
        get its size.
        """
        if not self.distinct:
            if not self.select:
                count = self.aggregates_module.Count('*', is_summary=True)
            else:
                assert len(self.select) == 1, \
                        "Cannot add count col with multiple cols in 'select': %r" % self.select
                count = self.aggregates_module.Count(self.select[0].col)
        else:
            opts = self.get_meta()
            if not self.select:
                count = self.aggregates_module.Count(
                    (self.join((None, opts.db_table, None)), opts.pk.column),
                    is_summary=True, distinct=True)
            else:
                # Because of SQL portability issues, multi-column, distinct
                # counts need a sub-query -- see get_count() for details.
                assert len(self.select) == 1, \
                        "Cannot add count col with multiple cols in 'select'."

                count = self.aggregates_module.Count(self.select[0].col, distinct=True)
            # Distinct handling is done in Count(), so don't do it at this
            # level.
            self.distinct = False

        # Set only aggregate to be the count column.
        # Clear out the select cache to reflect the new unmasked aggregates.
        self.aggregates = {None: count}
        self.set_aggregate_mask(None)
        self.group_by = None

    def add_select_related(self, fields):
        """
        Sets up the select_related data structure so that we only select
        certain related models (as opposed to all models, when
        self.select_related=True).
        """
        field_dict = {}
        for field in fields:
            d = field_dict
            for part in field.split(LOOKUP_SEP):
                d = d.setdefault(part, {})
        self.select_related = field_dict
        self.related_select_cols = []

    def add_extra(self, select, select_params, where, params, tables, order_by):
        """
        Adds data to the various extra_* attributes for user-created additions
        to the query.
        """
        if select:
            # We need to pair any placeholder markers in the 'select'
            # dictionary with their parameters in 'select_params' so that
            # subsequent updates to the select dictionary also adjust the
            # parameters appropriately.
            select_pairs = SortedDict()
            if select_params:
                param_iter = iter(select_params)
            else:
                param_iter = iter([])
            for name, entry in select.items():
                entry = force_text(entry)
                entry_params = []
                pos = entry.find("%s")
                while pos != -1:
                    entry_params.append(next(param_iter))
                    pos = entry.find("%s", pos + 2)
                select_pairs[name] = (entry, entry_params)
            # This is order preserving, since self.extra_select is a SortedDict.
            self.extra.update(select_pairs)
        if where or params:
            self.where.add(ExtraWhere(where, params), AND)
        if tables:
            self.extra_tables += tuple(tables)
        if order_by:
            self.extra_order_by = order_by

    def clear_deferred_loading(self):
        """
        Remove any fields from the deferred loading set.
        """
        self.deferred_loading = (set(), True)

    def add_deferred_loading(self, field_names):
        """
        Add the given list of model field names to the set of fields to
        exclude from loading from the database when automatic column selection
        is done. The new field names are added to any existing field names that
        are deferred (or removed from any existing field names that are marked
        as the only ones for immediate loading).
        """
        # Fields on related models are stored in the literal double-underscore
        # format, so that we can use a set datastructure. We do the foo__bar
        # splitting and handling when computing the SQL colum names (as part of
        # get_columns()).
        existing, defer = self.deferred_loading
        if defer:
            # Add to existing deferred names.
            self.deferred_loading = existing.union(field_names), True
        else:
            # Remove names from the set of any existing "immediate load" names.
            self.deferred_loading = existing.difference(field_names), False

    def add_immediate_loading(self, field_names):
        """
        Add the given list of model field names to the set of fields to
        retrieve when the SQL is executed ("immediate loading" fields). The
        field names replace any existing immediate loading field names. If
        there are field names already specified for deferred loading, those
        names are removed from the new field_names before storing the new names
        for immediate loading. (That is, immediate loading overrides any
        existing immediate values, but respects existing deferrals.)
        """
        existing, defer = self.deferred_loading
        field_names = set(field_names)
        if 'pk' in field_names:
            field_names.remove('pk')
            field_names.add(self.get_meta().pk.name)

        if defer:
            # Remove any existing deferred names from the current set before
            # setting the new names.
            self.deferred_loading = field_names.difference(existing), False
        else:
            # Replace any existing "immediate load" field names.
            self.deferred_loading = field_names, False

    def get_loaded_field_names(self):
        """
        If any fields are marked to be deferred, returns a dictionary mapping
        models to a set of names in those fields that will be loaded. If a
        model is not in the returned dictionary, none of it's fields are
        deferred.

        If no fields are marked for deferral, returns an empty dictionary.
        """
        # We cache this because we call this function multiple times
        # (compiler.fill_related_selections, query.iterator)
        try:
            return self._loaded_field_names_cache
        except AttributeError:
            collection = {}
            self.deferred_to_data(collection, self.get_loaded_field_names_cb)
            self._loaded_field_names_cache = collection
            return collection

    def get_loaded_field_names_cb(self, target, model, fields):
        """
        Callback used by get_deferred_field_names().
        """
        target[model] = set([f.name for f in fields])

    def set_aggregate_mask(self, names):
        "Set the mask of aggregates that will actually be returned by the SELECT"
        if names is None:
            self.aggregate_select_mask = None
        else:
            self.aggregate_select_mask = set(names)
        self._aggregate_select_cache = None

    def set_extra_mask(self, names):
        """
        Set the mask of extra select items that will be returned by SELECT,
        we don't actually remove them from the Query since they might be used
        later
        """
        if names is None:
            self.extra_select_mask = None
        else:
            self.extra_select_mask = set(names)
        self._extra_select_cache = None

    def _aggregate_select(self):
        """The SortedDict of aggregate columns that are not masked, and should
        be used in the SELECT clause.

        This result is cached for optimization purposes.
        """
        if self._aggregate_select_cache is not None:
            return self._aggregate_select_cache
        elif self.aggregate_select_mask is not None:
            self._aggregate_select_cache = SortedDict([
                (k,v) for k,v in self.aggregates.items()
                if k in self.aggregate_select_mask
            ])
            return self._aggregate_select_cache
        else:
            return self.aggregates
    aggregate_select = property(_aggregate_select)

    def _extra_select(self):
        if self._extra_select_cache is not None:
            return self._extra_select_cache
        elif self.extra_select_mask is not None:
            self._extra_select_cache = SortedDict([
                (k,v) for k,v in self.extra.items()
                if k in self.extra_select_mask
            ])
            return self._extra_select_cache
        else:
            return self.extra
    extra_select = property(_extra_select)

    def trim_start(self, names_with_path):
        """
        Trims joins from the start of the join path. The candidates for trim
        are the PathInfos in names_with_path structure that are m2m joins.

        Also sets the select column so the start matches the join.

        This method is meant to be used for generating the subquery joins &
        cols in split_exclude().

        Returns a lookup usable for doing outerq.filter(lookup=self). Returns
        also if the joins in the prefix contain a LEFT OUTER join.
        _"""
        all_paths = []
        for _, paths in names_with_path:
            all_paths.extend(paths)
        contains_louter = False
        # Trim and operate only on tables that were generated for
        # the lookup part of the query. That is, avoid trimming
        # joins generated for F() expressions.
        lookup_tables = [t for t in self.tables if t in self._lookup_joins or t == self.tables[0]]
        for trimmed_paths, path in enumerate(all_paths):
            if path.m2m:
                break
            if self.alias_map[lookup_tables[trimmed_paths + 1]].join_type == self.LOUTER:
                contains_louter = True
            self.unref_alias(lookup_tables[trimmed_paths])
        # The path.join_field is a Rel, lets get the other side's field
        join_field = path.join_field.field
        # Build the filter prefix.
        paths_in_prefix = trimmed_paths
        trimmed_prefix = []
        for name, path in names_with_path:
            if paths_in_prefix - len(path) < 0:
                break
            trimmed_prefix.append(name)
            paths_in_prefix -= len(path)
        trimmed_prefix.append(
            join_field.foreign_related_fields[0].name)
        trimmed_prefix = LOOKUP_SEP.join(trimmed_prefix)
        # Lets still see if we can trim the first join from the inner query
        # (that is, self). We can't do this for LEFT JOINs because we would
        # miss those rows that have nothing on the outer side.
        if self.alias_map[lookup_tables[trimmed_paths + 1]].join_type != self.LOUTER:
            select_fields = [r[0] for r in join_field.related_fields]
            select_alias = lookup_tables[trimmed_paths + 1]
            self.unref_alias(lookup_tables[trimmed_paths])
            extra_restriction = join_field.get_extra_restriction(
                self.where_class, None, lookup_tables[trimmed_paths + 1])
            if extra_restriction:
                self.where.add(extra_restriction, AND)
        else:
            # TODO: It might be possible to trim more joins from the start of the
            # inner query if it happens to have a longer join chain containing the
            # values in select_fields. Lets punt this one for now.
            select_fields = [r[1] for r in join_field.related_fields]
            select_alias = lookup_tables[trimmed_paths]
        self.select = [SelectInfo((select_alias, f.column), f) for f in select_fields]
        return trimmed_prefix, contains_louter

    def is_nullable(self, field):
        """
        A helper to check if the given field should be treated as nullable.

        Some backends treat '' as null and Django treats such fields as
        nullable for those backends. In such situations field.null can be
        False even if we should treat the field as nullable.
        """
        # We need to use DEFAULT_DB_ALIAS here, as QuerySet does not have
        # (nor should it have) knowledge of which connection is going to be
        # used. The proper fix would be to defer all decisions where
        # is_nullable() is needed to the compiler stage, but that is not easy
        # to do currently.
        if ((connections[DEFAULT_DB_ALIAS].features.interprets_empty_strings_as_nulls)
            and field.empty_strings_allowed):
            return True
        else:
            return field.null

def get_order_dir(field, default='ASC'):
    """
    Returns the field name and direction for an order specification. For
    example, '-foo' is returned as ('foo', 'DESC').

    The 'default' param is used to indicate which way no prefix (or a '+'
    prefix) should sort. The '-' prefix always sorts the opposite way.
    """
    dirn = ORDER_DIR[default]
    if field[0] == '-':
        return field[1:], dirn[1]
    return field, dirn[0]


def add_to_dict(data, key, value):
    """
    A helper function to add "value" to the set of values for "key", whether or
    not "key" already exists.
    """
    if key in data:
        data[key].add(value)
    else:
        data[key] = set([value])

def is_reverse_o2o(field):
    """
    A little helper to check if the given field is reverse-o2o. The field is
    expected to be some sort of relation field or related object.
    """
    return not hasattr(field, 'rel') and field.field.unique

def alias_diff(refcounts_before, refcounts_after):
    """
    Given the before and after copies of refcounts works out which aliases
    have been added to the after copy.
    """
    # Use -1 as default value so that any join that is created, then trimmed
    # is seen as added.
    return set(t for t in refcounts_after
               if refcounts_after[t] > refcounts_before.get(t, -1))
