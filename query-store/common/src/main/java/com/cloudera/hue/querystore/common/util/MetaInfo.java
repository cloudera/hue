// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.util;


import com.cloudera.hue.querystore.common.repository.PageData;

import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.ToString;

/**
 * Object returned by APIs whose results require Meta information
 */
@Getter
@EqualsAndHashCode
@ToString
public class MetaInfo {
  private int limit;
  private int offset;
  private long size;
  private long updateTime;

  private MetaInfo() {
  }

  public static Builder builder() {
    return new Builder();
  }

  public static class Builder {
    private final MetaInfo metaInfo;

    public Builder() {
      this.metaInfo = new MetaInfo();
    }

    public <T> Builder fromPageData(PageData<T> pageData, long updateTime) {
      metaInfo.limit = pageData.getLimit();
      metaInfo.offset = pageData.getOffset();
      metaInfo.size = pageData.getCount();
      metaInfo.updateTime = updateTime;

      return this;
    }

    public MetaInfo build() {
      return metaInfo;
    }
  }
}
