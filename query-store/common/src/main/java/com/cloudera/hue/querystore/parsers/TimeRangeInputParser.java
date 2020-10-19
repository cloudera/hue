// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.parsers;

import java.util.HashMap;
import java.util.Map;

import com.cloudera.hue.querystore.common.util.Pair;
import com.cloudera.hue.querystore.orm.EntityTable;

public class TimeRangeInputParser implements GenericParser<TimeRangeParseResult, Pair<Long, Long>> {

  private static final String START_TIME_PARAM_NAME = "startTime";
  private static final String END_TIME_PARAM_NAME = "endTime";
  private static final String TIME_EXPRESSION_TEMPLATE = "%s.start_time >= :startTime AND " +
    "%s.start_time <= :endTime"; // TODO: Generalize this to get the table columns from annotations.

  private final EntityTable hiveQueryTable;

  public TimeRangeInputParser(EntityTable hiveQueryTable) {
    this.hiveQueryTable = hiveQueryTable;
  }

  @Override
  public TimeRangeParseResult parse(Pair<Long, Long> timeRange) {
    long startTime = timeRange.getFirst();
    long endTime = timeRange.getSecond();

    Map<String, Object> parameterBindingMap = new HashMap<>();
    parameterBindingMap.put(START_TIME_PARAM_NAME, startTime);
    parameterBindingMap.put(END_TIME_PARAM_NAME, endTime);

    String expression = String.format(TIME_EXPRESSION_TEMPLATE, hiveQueryTable.getTablePrefix(),
        hiveQueryTable.getTablePrefix(), hiveQueryTable.getTablePrefix());

    return new TimeRangeParseResult(expression, parameterBindingMap);
  }
}
