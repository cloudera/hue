// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.parsers;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import org.apache.commons.lang3.StringUtils;

import com.cloudera.hue.querystore.common.repository.SortRequest.Direction;
import com.cloudera.hue.querystore.orm.EntityField;

/**
 * Sort input parser
 */
public class SortInputParser implements GenericParser<SortParseResult, String> {

  private final Map<String, EntityField> entityFieldMap;
  private final Set<String> allowedSortFields;

  public SortInputParser(List<EntityField> entityFieldList) {
    this.allowedSortFields = extractAllowedSortFields(entityFieldList);
    this.entityFieldMap = extractEntityFieldMap(entityFieldList.stream()
      .filter(x -> allowedSortFields.contains(x.getEntityFieldName()))
      .collect(Collectors.toList())
    );
  }

  private Map<String, EntityField> extractEntityFieldMap(List<EntityField> entityFieldList) {
    return entityFieldList.stream()
      .collect(
        Collectors.toMap(EntityField::getExternalFieldName, y -> y)
      );
  }

  private Set<String> extractAllowedSortFields(List<EntityField> entityFieldList) {
    return entityFieldList.stream()
      .filter(EntityField::isSortable)
      .map(EntityField::getExternalFieldName)
      .collect(Collectors.toSet());
  }

  @Override
  public SortParseResult parse(String parseInput) {
    if (StringUtils.isEmpty(parseInput)) {
      return SortParseResult.empty();
    }

    String[] inputs = parseInput.split(",");
    boolean sortingRequired = inputs.length > 0;
    String sortExpression = extractSortingString(inputs);

    return new SortParseResult(sortingRequired, sortExpression);
  }

  private String extractSortingString(String[] inputs) {
    StringBuilder builder = new StringBuilder();
    boolean first = true;
    for (String input : inputs) {
      String[] parts = input.trim().split(":");
      if (parts.length != 2) {
        throw new IllegalArgumentException("Invalid sort field: " + input);
      }
      Direction direction = Direction.valueOf(parts[1].toUpperCase());
      if (!allowedSortFields.contains(parts[0])) {
        throw new RuntimeException("Field not sortable: " + parts[0]);
      }
      if (!first) {
        builder.append(", ");
      }
      EntityField e = entityFieldMap.get(parts[0]);
      builder.append(e.getEntityPrefix());
      builder.append('.');
      builder.append(e.getDbFieldName());
      builder.append(' ');
      builder.append(direction);
      first = false;
    }
    return builder.toString();
  }
}
