package com.cloudera.hue.querystore.common.dto;

import java.util.Collection;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
public class QuerySearchResult<T> {
  private Collection<T> queries;
  private MetaInfo meta;

  public QuerySearchResult(Collection<T> queries, long size, QuerySearchParams searchParams, long updateTime) {
    this.queries = queries;
    this.meta = new MetaInfo(searchParams.getLimit(), searchParams.getOffset(), size, updateTime);
  }

  @Getter
  @AllArgsConstructor
  public class MetaInfo {
    private int limit;
    private int offset;
    private long size;
    private long updateTime;
  }
}
