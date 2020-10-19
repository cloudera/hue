// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.parsers;

import java.util.Map;

import lombok.Value;

/**
 * Stores the parse result after the text has been parsed
 */
@Value
public class QueryParseResult {
  private final String predicate;
  private final Map<String, Object> parameterBindings;
  private final boolean queryHighLightRequired;
}
