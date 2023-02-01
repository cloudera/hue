// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.generator;

import java.util.Iterator;
import java.util.List;

import com.cloudera.hue.querystore.orm.EntityField;
import com.cloudera.hue.querystore.orm.EntityTable;

/**
 * Generates the Native query for hive and dag info search
 */
public class SearchQueryGenerator {
  private final String offsetParameterBinding;
  private final String limitParameterBinding;
  private final List<String> predicates;
  private final String sortFragment;
  private final EntityTable hiveQuery;
  private final EntityTable dagInfo;

  public SearchQueryGenerator(EntityTable hiveQuery, EntityTable dagInfo,
	      String offsetParameterBinding, String limitParameterBinding,
	      String sortFragment, List<String> predicates) {
    this.hiveQuery = hiveQuery;
    this.dagInfo = dagInfo;
    this.offsetParameterBinding = offsetParameterBinding;
    this.limitParameterBinding = limitParameterBinding;
    this.predicates = predicates;
    this.sortFragment = sortFragment;
  }

  private static void addFields(StringBuilder builder, EntityTable table, boolean isLastField) {
    Iterator<EntityField> iterator = table.getFields().iterator();
    while (iterator.hasNext()) {
      EntityField field = iterator.next();
      builder.append(field.getEntityPrefix());
      builder.append(".");
      builder.append(field.getDbFieldName());
      builder.append(" AS ");
      builder.append(field.getEntityPrefix());
      builder.append(field.getDbFieldName());
      if (!isLastField || iterator.hasNext()) {
        builder.append(", ");
      }
    }
  }

  private static void addTable(StringBuilder builder, EntityTable table) {
    builder.append(table.getTableName());
    builder.append(' ');
    builder.append(table.getTablePrefix());
  }

  public String generate() {
    StringBuilder builder = new StringBuilder(2048);
    builder.append("SELECT ");
    addFields(builder, hiveQuery, false);
    addFields(builder, dagInfo, true);
    builder.append(" FROM ");
    addTable(builder, hiveQuery);
    builder.append(" LEFT OUTER JOIN ");
    addTable(builder, dagInfo);
    builder.append(" ON ");
    builder.append(hiveQuery.getTablePrefix());
    builder.append(".id = ");
    builder.append(dagInfo.getTablePrefix());
    builder.append(".hive_query_id");
    addPredicate(builder, predicates);
    builder.append(' ');
    builder.append(sortFragment);
    builder.append(" OFFSET :");
    builder.append(offsetParameterBinding);
    builder.append(" LIMIT :");
    builder.append(limitParameterBinding);
    return builder.toString();
  }

  public void addPredicate(StringBuilder builder, List<String> predicates) {
    boolean isFirst = true;
    for (String predicate : predicates) {
      if (isFirst) {
        builder.append(" WHERE ");
        isFirst = false;
      } else {
        builder.append(" AND ");
      }
      builder.append(predicate);
    }
  }
}
