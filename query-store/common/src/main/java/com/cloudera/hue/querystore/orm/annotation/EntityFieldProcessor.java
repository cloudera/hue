// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.orm.annotation;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.IntStream;

import org.apache.commons.lang.StringUtils;

import com.cloudera.hue.querystore.orm.EntityField;
import com.cloudera.hue.querystore.orm.EntityTable;

import lombok.extern.slf4j.Slf4j;

/**
 * Processes the Annotations on the Entity class and returns the EntityField information for the entity class
 */
@Slf4j
public class EntityFieldProcessor {
  private static final Set<String> prefixesSeen = new HashSet<>();
  private static final String ALPHABETS = "abcdefghijklmnopqrstuvwxyz";
  private static final int[] sizes = {3, 4, 5, 6, 7};

  public static EntityTable process(Class<?> entityClass) {
    List<EntityField> fields = new ArrayList<>();
    String searchQueryPrefix = null;
    String tableName = null;

    if (entityClass.isAnnotationPresent(SearchQuery.class)) {
      SearchQuery sqAnno = entityClass.getAnnotation(SearchQuery.class);
      tableName = sqAnno.table();

      if (!StringUtils.isEmpty(sqAnno.prefix())) {
        if (prefixesSeen.contains(sqAnno.prefix())) {
          log.warn("while processing {}, '{}' prefix already seen before, using a random string " +
              "as entity prefix",entityClass.getName(), sqAnno.prefix());
          searchQueryPrefix = generateRandomString();
        } else {
          searchQueryPrefix = sqAnno.prefix();
        }
      } else {
        searchQueryPrefix = generateRandomString();
      }
      prefixesSeen.add(searchQueryPrefix);

      for (Field field : entityClass.getDeclaredFields()) {
        if (Modifier.isStatic(field.getModifiers())) {
          continue;
        }

        if (!field.isAnnotationPresent(ColumnInfo.class)) {
          continue;
        }

        ColumnInfo columnInfo = field.getAnnotation(ColumnInfo.class);

        boolean isIdField = columnInfo.id();
        boolean isSortable = columnInfo.sortable();
        boolean isSearchable = columnInfo.searchable();
        boolean highlightRequired = columnInfo.highlightRequired();
        boolean isFacetable = columnInfo.facetable();
        boolean isRangeFacetable = columnInfo.rangeFacetable();
        boolean excludeFromFieldsInfo = columnInfo.exclude();
        String tsVectorColumnName = null;
        String highlightProjectionName = "";
        String dbFieldName = columnInfo.columnName();
        String entityFieldName = field.getName();
        String externalFieldName = entityFieldName;
        String displayName = null;

        if (isFacetable && !isSearchable) {
          log.error("'{}' field should be searchable if faceting is required", entityFieldName);
          throw new RuntimeException("'" + entityFieldName + "' field should be searchable if faceting is required");
        }

        if (isFacetable && isRangeFacetable) {
          log.error("'{}' field cannot be facetable and rangefacetable at the same time.", entityFieldName);
          throw new RuntimeException("'" + entityFieldName + "' field cannot be facetable and rangefacetable at the same time.");
        }

        if (!StringUtils.isEmpty(columnInfo.highlightProjectionName())) {
          highlightProjectionName = columnInfo.highlightProjectionName();
        }

        if (!StringUtils.isEmpty(columnInfo.fieldName())) {
          externalFieldName = columnInfo.fieldName();
        }

        if(!StringUtils.isEmpty(columnInfo.tsVectorColumnName())) {
          tsVectorColumnName = columnInfo.tsVectorColumnName();
        }

        displayName = StringUtils.isEmpty(columnInfo.displayName())
            ? getDisplayNameFromFieldName(externalFieldName) : columnInfo.displayName();

        if (displayName == null) {
          displayName = getDisplayNameFromFieldName(entityFieldName);
        }
        EntityField entityField = new EntityField(isIdField, isSearchable, isSortable,
          entityFieldName, dbFieldName, externalFieldName, searchQueryPrefix, highlightRequired,
          highlightProjectionName, tsVectorColumnName, isFacetable, isRangeFacetable, displayName,
          excludeFromFieldsInfo);
        fields.add(entityField);
      }
    } else {
      log.warn("{} is not an entity", entityClass.getName());
    }

    return new EntityTable(tableName, searchQueryPrefix, fields, entityClass);
  }

  private static String getDisplayNameFromFieldName(String fieldName) {
    String capitalize = StringUtils.capitalize(fieldName);
    return capitalize.replaceAll("([A-Z])", " $1").trim();
  }

  private static String generateRandomString() {
    int length = sizes[(int) (sizes.length * Math.random())];
    StringBuilder builder = new StringBuilder();
    IntStream.range(0, length).forEach(x -> {
      builder.append(ALPHABETS.charAt((int) (ALPHABETS.length() * Math.random())));
    });

    String prefix = builder.toString();
    return prefixesSeen.contains(prefix) ? generateRandomString() : prefix;
  }
}
