// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.parsers;

import java.util.HashMap;
import java.util.Map;

import lombok.Value;

@Value
public class FacetParseResult {
  private final String facetExpression;
  private final Map<String, Object> parameterBindings;

  public static FacetParseResult empty() {
    return new FacetParseResult("true", new HashMap<>());
  }
}
