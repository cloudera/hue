// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.parsers;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import org.apache.commons.lang3.StringUtils;

import com.cloudera.hue.querystore.orm.EntityField;
import com.cloudera.hue.querystore.orm.EntityTable;

import lombok.extern.slf4j.Slf4j;

/**
 * Query text parser for performing the basic search
 */
@Slf4j
public class BasicSearchParser implements SearchQueryParser {
  private static final String BASE_PREDICATE = "(%s.%s @@ plainto_tsquery('english', :basicSearchText) = true " +
    "OR %s.query_id = :basicSearchText " +
    "OR %s.dag_id = :basicSearchText " +
    "OR %s.application_id = :basicSearchText)";

  private static final String NO_PREDICATE = "true";
  private final EntityTable hiveTable;
  private final EntityTable dagTable;

  public BasicSearchParser(EntityTable hiveTable, EntityTable dagTable) {
    this.hiveTable = hiveTable;
    this.dagTable = dagTable;
  }

  @Override
  public QueryParseResult parse(String queryText) {

    if (StringUtils.isEmpty(queryText)) {
      return new QueryParseResult(NO_PREDICATE, new HashMap<>(), false);
    }

    log.debug("Trigram query generated for query text '{}'", queryText);
    Map<String, Object> parametersMap = new HashMap<>();
    parametersMap.put("basicSearchText", queryText);

    Optional<EntityField> queryFtsColumn = hiveTable.getFields().stream().filter(x -> !StringUtils.isEmpty(x.getTsVectorColumnName())).findFirst();

    if (!queryFtsColumn.isPresent()) {
      log.error("Failed to find the FTS column name from the entity class");
      throw new RuntimeException("Failed to find the FTS column name from the entity class");
    }

    String hiveTablePrefix = hiveTable.getTablePrefix();
    String dagTablePrefix = dagTable.getTablePrefix();

    String predicate = String.format(BASE_PREDICATE,
      hiveTablePrefix, queryFtsColumn.get().getTsVectorColumnName(),
      hiveTablePrefix,
      dagTablePrefix,
      dagTablePrefix
    );

    return new QueryParseResult(predicate, parametersMap, true);
  }
}
