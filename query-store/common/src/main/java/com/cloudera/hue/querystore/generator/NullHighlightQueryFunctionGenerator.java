// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.generator;

import com.cloudera.hue.querystore.orm.EntityField;

/**
 * Returns the Native query fragment which enables the highlighting of the matched queries
 */
public class NullHighlightQueryFunctionGenerator {
  private static final String HIGHLIGHT_QUERY_FUNCTION = "NULL AS %s";

  public String generate(EntityField highlightField) {
    return String.format(HIGHLIGHT_QUERY_FUNCTION, highlightField.getHighlightProjectionColumnName());
  }
}
