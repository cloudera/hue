// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dto;

import java.util.List;

public class SearchRequest {
  private  String type;
  private  String text;
  private  String sortText;
  private  Long startTime;
  private  Long endTime;
  private  Integer limit;
  private  Integer offset;
  private  List<Facet> facets;
  private  List<RangeFacet> rangeFacets;

  public SearchRequest() {

  }

  public SearchRequest(String type, String text, String sortText, Long startTime, Long endTime, Integer limit,
    Integer offset, List<Facet> facets, List<RangeFacet> rangeFacets) {
    this.type = type;
    this.text = text;
    this.sortText = sortText;
    this.startTime = startTime;
    this.endTime = endTime;
    this.limit = limit;
    this.offset = offset;
    this.facets = facets;
    this.rangeFacets = rangeFacets;
  }

  public String getType() {
    return type;
  }

  public String getText() {
    return text;
  }

  public String getSortText() {
    return sortText;
  }

  public Long getStartTime() {
    return startTime;
  }

  public Long getEndTime() {
    return endTime;
  }

  public Integer getLimit() {
    return limit;
  }

  public Integer getOffset() {
    return offset;
  }

  public List<Facet> getFacets() {
    return facets;
  }

  public List<RangeFacet> getRangeFacets() {
    return rangeFacets;
  }

  public static class Facet {
    private String field;
    private List<Object> values;
    public Facet() { }

    public String getField() {
      return field;
    }

    public void setField(String field) {
      this.field = field;
    }

    public List<Object> getValues() {
      return values;
	}

    public void setValues(List<Object> values) {
      this.values = values;
    }
  }

  public static class RangeFacet {
    private String field;
    private Object max;
    private Object min;
    public RangeFacet() { }

    public String getField() {
      return field;
    }

    public void setField(String field) {
      this.field = field;
    }

    public Object getMax() {
      return max;
    }

    public void setMax(Object max) {
      this.max = max;
    }

    public Object getMin() {
      return min;
    }

    public void setMin(Object min) {
      this.min = min;
    }
  }

  public static class SearchRequestWrapper {
    private SearchRequest search;
    public SearchRequestWrapper() { }

    public SearchRequestWrapper(SearchRequest search) {
      this.search = search;
    }

    public SearchRequest getSearch() {
      return search;
    }

    public void setSearch(SearchRequest search) {
      this.search = search;
    }
  }
}
