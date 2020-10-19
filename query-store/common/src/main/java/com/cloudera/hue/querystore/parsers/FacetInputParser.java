// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.parsers;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import com.cloudera.hue.querystore.common.dto.FieldInformation;
import com.cloudera.hue.querystore.common.dto.SearchRequest;
import com.cloudera.hue.querystore.orm.EntityField;

public class FacetInputParser implements GenericParser<FacetParseResult, List<SearchRequest.Facet>> {

  private final Set<String> facetableFieldNames;
  private final Map<String, EntityField> entityFieldMap;

  private static volatile int facetCount = 0;

  public FacetInputParser(List<EntityField> entityFieldList, List<FieldInformation> fields) {
    facetableFieldNames = fields.stream()
      .filter(FieldInformation::isFacetable)
      .map(FieldInformation::getFieldName)
      .collect(Collectors.toSet());

    this.entityFieldMap = extractEntityFieldMap(entityFieldList.stream()
      .filter(x -> facetableFieldNames.contains(x.getEntityFieldName()))
    );
  }

  private Map<String, EntityField> extractEntityFieldMap(Stream<EntityField> entityFieldList) {
    return entityFieldList
      .collect(
        Collectors.toMap(EntityField::getExternalFieldName, y -> y)
      );
  }


  @Override
  public FacetParseResult parse(List<SearchRequest.Facet> facets) {
    Map<String, Object> parameterBindings = new HashMap<>();
    if (facets == null || facets.size() == 0)
      return FacetParseResult.empty();

    Set<SearchRequest.Facet> filteredFacets = facets.stream()
      .filter(x -> facetableFieldNames.contains(x.getField()))
      .collect(Collectors.toSet());

    Set<String> facetBindParameters = filteredFacets.stream().map(x -> {
      EntityField entityField = entityFieldMap.get(x.getField());
      String dbColumnName = entityField.getEntityPrefix() + "." + entityField.getDbFieldName();

      if (x.getValues().isEmpty()) {
        return dbColumnName + " IS NULL";
      }

      if (entityField.isJsonArrayField()) {
        String jsonFragment = getFacetFragmentAfterJsonProcessing(x, parameterBindings);
        return dbColumnName + " @> ANY ( ARRAY["  + jsonFragment + "]::jsonb[])";
      } else {
        String fragment = getFacetFragmentAfterNormalProcessing(parameterBindings, x);
        return dbColumnName + " IN (" + fragment + ")";
      }
    }).collect(Collectors.toSet());

    String expression = String.join(" AND ", facetBindParameters);
    return new FacetParseResult(expression, parameterBindings);
  }

  private String getFacetFragmentAfterNormalProcessing(Map<String, Object> parameterBindings, SearchRequest.Facet x) {
    return x.getValues().stream().map(y -> {
      String bindParameterName = getNextBindParameterName();
      parameterBindings.put(bindParameterName, y);
      return ":" + bindParameterName;
    }).collect(Collectors.joining(", "));
  }

  private String getFacetFragmentAfterJsonProcessing(SearchRequest.Facet x, Map<String, Object> parameterBindings) {
    // Hack to mitigate the issue that JPA does not process bind parameters within single quotes
    Stream<String> parameters = x.getValues().stream().map(y -> {
      String value = (String) y;
      String[] splits = value.split("\\.");
      String table = splits[1];
      String database = splits[0];
      return "[{\"table\": \"" + table + "\", \"database\": \"" + database + "\"}]";
    });

    return parameters.map(y -> {
      String paramName = getNextBindParameterName();
      parameterBindings.put(paramName, y);
      return ":" + paramName;
    }).collect(Collectors.joining(", "));
  }

  private String getNextBindParameterName() {
    facetCount++;
    if (facetCount > 100000) facetCount = 0;
    return "facet" + facetCount;
  }
}
