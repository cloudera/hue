// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.parsers;

import lombok.Value;

/**
 * Stores the result of parsing the sort string
 */
@Value
public class SortParseResult {
  private final boolean sortingRequired;
  private final String sortExpression;

  public static SortParseResult empty() {
    return new SortParseResult(false, "");
  }
}
