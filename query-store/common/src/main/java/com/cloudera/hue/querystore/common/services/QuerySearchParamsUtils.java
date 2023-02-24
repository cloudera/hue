package com.cloudera.hue.querystore.common.services;

import java.util.ArrayList;
import java.util.List;

import com.cloudera.hue.querystore.common.dto.QuerySearchParams;
import com.cloudera.hue.querystore.common.dto.QuerySearchParams.Facet;

public class QuerySearchParamsUtils {
  private static final int DEFAULT_SEARCH_DURATION = 7 * 24 * 60 * 60 * 1000; // 7 days
  private static final int MAX_LIMIT = 100;

  public static QuerySearchParams standardize(QuerySearchParams params) {
    return new QuerySearchParams(
      standardizeStr(params.getText()),
      standardizeStr(params.getSortText()),
      standardizeStartTime(params.getStartTime(), params.getEndTime()),
      standardizeEndTime(params.getStartTime(), params.getEndTime()),
      standardizeFacets(params.getFacets()),

      standardizeLimit(params.getLimit()),
      standardizeOffset(params.getOffset()));
  }

  private static String standardizeStr(String text) {
    return text == null ? "" : text;
  }

  private static Long standardizeStartTime(Long startTime, Long endTime) {
    if (startTime == null && endTime == null) {
      return System.currentTimeMillis() - DEFAULT_SEARCH_DURATION;
    } else if (startTime == null){
      return endTime - DEFAULT_SEARCH_DURATION;
    } else {
      return startTime;
    }
  }

  private static Long standardizeEndTime(Long startTime, Long endTime) {
    if (startTime == null && endTime == null) {
      return System.currentTimeMillis();
    } else if (endTime == null){
      return startTime + DEFAULT_SEARCH_DURATION;
    } else {
      return endTime;
    }
  }

  private static List<Facet> standardizeFacets(List<Facet> facets) {
    if(facets == null) {
      facets = new ArrayList<Facet>();
    }
    return facets;
  }

  private static int standardizeLimit(Integer limit) {
    if(limit == null || limit <= 0) {
      limit = MAX_LIMIT;
    } else {
      limit = Math.min(limit, MAX_LIMIT);
    }
    return limit;
  }

  private static int standardizeOffset(Integer offset) {
    return offset == null ? 0 : offset;
  }
}
