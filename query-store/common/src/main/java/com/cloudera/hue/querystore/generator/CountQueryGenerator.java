// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.generator;

import java.util.List;

import com.cloudera.hue.querystore.orm.EntityTable;


/**
 * Generates the Native query for counting the hive and dag info returned by search query
 */
public class CountQueryGenerator {
  private final String projectionName;
  private final EntityTable hiveQuery;
  private final EntityTable dagInfo;
  private final List<String> predicates;

  public CountQueryGenerator(EntityTable hiveQuery, EntityTable dagInfo, String projectionName,
      List<String> predicates) {
    this.hiveQuery = hiveQuery;
    this.dagInfo = dagInfo;
    this.projectionName = projectionName;
    this.predicates = predicates;
  }

  private static void addTable(StringBuilder builder, EntityTable table) {
    builder.append(table.getTableName());
    builder.append(' ');
    builder.append(table.getTablePrefix());
  }

  public String generate() {
    StringBuilder builder = new StringBuilder(2048);
    builder.append("SELECT count(*) AS ");
    builder.append(projectionName);
    builder.append(" FROM ");
    addTable(builder, hiveQuery);
    builder.append(" LEFT OUTER JOIN ");
    addTable(builder, dagInfo);
    builder.append(" ON ");
    builder.append(hiveQuery.getTablePrefix());
    builder.append(".id = ");
    builder.append(dagInfo.getTablePrefix());
    builder.append(".hive_query_id");
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
    builder.append(' ');
    return builder.toString();
  }
}
