// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.orm;

import java.util.List;

import lombok.Value;

/**
 * Represent a table meta info
 */
@Value
public class EntityTable {
  private final String tableName;
  private final String tablePrefix;
  private final List<EntityField> fields;
  private final Class<?> entityClass;

  public String getDbFieldName(String entityFieldName) {
    for(EntityField field : fields) {
      if(field.getEntityFieldName() == entityFieldName) {
        return field.getDbFieldName();
      }
    }
    return null;
  }
}
