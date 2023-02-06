// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.services;

/**
 * Utility to perform search-query sanitization
 */
public class StandardizeParamsUtility {
  private static final int DEFAULT_SEARCH_DURATION = 7 * 24 * 60 * 60 * 1000;
  private static final int MAX_LIMIT = 100;

  public static String sanitizeQuery(String queryText) {
    return queryText == null ? "" : queryText;
  }

  public static int sanitizeOffset(Integer offset) {
    return offset == null ? 0 : offset;
  }

  public static int sanitizeLimit(Integer limit) {
    return limit == null ? MAX_LIMIT : limit > MAX_LIMIT ? MAX_LIMIT : limit;
  }

  public static Long sanitizeStartTime(Long startTime, Long endTime) {
    if (startTime == null && endTime == null) {
      return System.currentTimeMillis() - DEFAULT_SEARCH_DURATION;
    } else if (startTime == null){
      return endTime - DEFAULT_SEARCH_DURATION;
    } else {
      return startTime;
    }
  }

  public static Long sanitizeEndTime(Long startTime, Long endTime) {
    if (startTime == null && endTime == null) {
      return System.currentTimeMillis();
    } else if (endTime == null){
      return startTime + DEFAULT_SEARCH_DURATION;
    } else {
      return endTime;
    }
  }
}
