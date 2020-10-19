// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.parsers;

import java.util.HashMap;
import java.util.Map;

import lombok.Value;

@Value
public class TimeRangeParseResult {
  private final String timeRangeExpression;
  private final Map<String, Object> parameterBindings;

  public static TimeRangeParseResult empty() {
    return new TimeRangeParseResult("true", new HashMap<>());
  }
}
