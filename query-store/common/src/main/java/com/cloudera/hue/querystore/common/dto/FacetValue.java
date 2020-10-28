// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dto;

import java.util.List;

import lombok.Value;

/**
 * Stores the facet values including the count
 */
@Value
public class FacetValue {
  private final String facetField;
  private final List<FacetEntry> values;
}
