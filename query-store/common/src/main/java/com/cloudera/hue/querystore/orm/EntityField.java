// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.orm;

import lombok.Value;

@Value
public class EntityField {
  private final boolean idField;
  private final boolean searchable;
  private final boolean sortable;
  private final String entityFieldName;
  private final String dbFieldName;
  private final String externalFieldName;
  private final String entityPrefix;
  private final boolean highlightRequired;
  private final String highlightProjectionColumnName;
  private final String tsVectorColumnName;
  private final boolean facetable;
  private final boolean rangeFacetable;
  private final String displayName;
  private final boolean exclude;

  public boolean isJsonArrayField() {
    return "tablesRead".equalsIgnoreCase(entityFieldName) || "tablesWritten".equalsIgnoreCase(entityFieldName);
  }
}
