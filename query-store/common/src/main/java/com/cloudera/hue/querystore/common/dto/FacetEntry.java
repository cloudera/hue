// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dto;

import javax.annotation.Nullable;

import com.fasterxml.jackson.annotation.JsonIgnore;

import lombok.Data;

@Data
public class FacetEntry {
  @JsonIgnore
  @Nullable
  private String type;
  @JsonIgnore
  @Nullable
  private boolean first;
  @Nullable
  private String key;
  @Nullable
  private Long value;
}
