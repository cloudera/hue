package com.cloudera.hue.querystore.common.dto;

import java.util.HashMap;
import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class QuerySearchParams {
  private String text;
  private String sortText;
  private Long startTime;
  private Long endTime;
  private List<Facet> facets;

  private Integer limit;
  private Integer offset;

  public QuerySearchParams() {}

  public HashMap<String, List<Object>> getFacetMap() {
    HashMap<String, List<Object>> map = new HashMap<>();
    for(Facet facet : facets) {
      map.put(facet.field, facet.values);
    }
    return map;
  }

  @Getter
  public static class Facet {
    private String field;
    private List<Object> values;
  }
}
