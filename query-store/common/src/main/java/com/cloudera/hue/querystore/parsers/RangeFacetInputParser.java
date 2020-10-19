// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.parsers;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import com.cloudera.hue.querystore.common.dto.FieldInformation;
import com.cloudera.hue.querystore.common.dto.SearchRequest;
import com.cloudera.hue.querystore.orm.EntityField;

public class RangeFacetInputParser implements GenericParser<FacetParseResult, List<SearchRequest.RangeFacet>> {

  private final Set<String> facetableFieldNames;
  private final Map<String, EntityField> entityFieldMap;

  private static int facetCount = 0;

  public RangeFacetInputParser(List<EntityField> entityFieldList, List<FieldInformation> fields) {
    facetableFieldNames = fields.stream()
      .filter(FieldInformation::isRangeFacetable)
      .map(FieldInformation::getFieldName)
      .collect(Collectors.toSet());

    this.entityFieldMap = extractEntityFieldMap(entityFieldList.stream()
      .filter(x -> facetableFieldNames.contains(x.getEntityFieldName()))
      .collect(Collectors.toList())
    );
  }

  private Map<String, EntityField> extractEntityFieldMap(List<EntityField> entityFieldList) {
    return entityFieldList.stream()
      .collect(
        Collectors.toMap(EntityField::getExternalFieldName, y -> y)
      );
  }


  @Override
  public FacetParseResult parse(List<SearchRequest.RangeFacet> facets) {
    Map<String, Object> parameterBindings = new HashMap<>();
    if (facets == null || facets.size() == 0)
      return FacetParseResult.empty();

    Set<SearchRequest.RangeFacet> filteredFacets = facets.stream()
      .filter(x -> facetableFieldNames.contains(x.getField()))
      .collect(Collectors.toSet());

    Set<String> expressions = filteredFacets.stream().map(x -> {
      String maxBindParameter = getNextBindParameterName();
      parameterBindings.put(maxBindParameter, x.getMax());

      String minBindParameter = getNextBindParameterName();
      parameterBindings.put(minBindParameter, x.getMin());
      EntityField entityField = entityFieldMap.get(x.getField());

      String dbColumnName = entityField.getEntityPrefix() + "." + entityField.getDbFieldName();
      return dbColumnName + " BETWEEN :" + minBindParameter + " AND :" + maxBindParameter;
    }).collect(Collectors.toSet());

    // If empty values list was provided
    if(parameterBindings.size() == 0) return FacetParseResult.empty();

    String expression = String.join(" AND ", expressions);
    return new FacetParseResult(expression, parameterBindings);
  }

  private String getNextBindParameterName() {
    facetCount++;
    if (facetCount > 100000) facetCount = 0;
    return "rangeFacet" + facetCount;
  }
}
