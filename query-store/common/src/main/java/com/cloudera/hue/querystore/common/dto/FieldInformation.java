// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dto;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import java.util.stream.Collectors;

import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.orm.EntityField;

import lombok.Value;

/**
 * DTO to store the Field Information
 */
@Value
public class FieldInformation {
  private static volatile List<FieldInformation> fieldsInformation = null;

  private final String fieldName;
  private final String displayName;
  private final boolean searchable;
  private final boolean sortable;
  private final boolean facetable;
  private final boolean rangeFacetable;
  public static List<FieldInformation> getFieldsInformation() {
    if (fieldsInformation == null) {
      synchronized (FieldInformation.class) {
        Function<EntityField, FieldInformation> entityFieldConsumer = x -> new FieldInformation(
          x.getExternalFieldName(), x.getDisplayName(), x.isSearchable(), x.isSortable(), x.isFacetable(),
          x.isRangeFacetable());
        ArrayList<FieldInformation> fields = new ArrayList<>();
        fields.addAll(HiveQueryBasicInfo.TABLE_INFORMATION.getFields().stream()
          .filter(x -> !x.isExclude())
          .map(entityFieldConsumer)
          .collect(Collectors.toList()));
        fields.addAll(TezDagBasicInfo.TABLE_INFORMATION.getFields().stream()
          .filter(x -> !x.isExclude())
          .map(entityFieldConsumer)
          .collect(Collectors.toList()));
        fieldsInformation = fields;
      }
    }
    return fieldsInformation;
  }
}