// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dto;

import lombok.Value;

/**
 * DTO to store the Field Information
 */
@Value
public class FieldInformation {
  private final String fieldName;
  private final String displayName;
  private final boolean searchable;
  private final boolean sortable;
  private final boolean facetable;
  private final boolean rangeFacetable;
}
