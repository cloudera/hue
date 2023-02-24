package com.cloudera.hue.querystore.common.dto;

import com.cloudera.hue.querystore.orm.EntityField;
import com.cloudera.hue.querystore.orm.EntityTable;

import lombok.Getter;

@Getter
public class SortDetails {
  static final String DEFAULT_SORT_COLUMN = "start_time";
  static final String DEFAULT_SORT_ORDER = "DESC";

  private String columnName;
  private String order;

  public SortDetails(QuerySearchParams params, EntityTable tableInfo) {
    String[] parts = params.getSortText().split(":", 2);

    String columnName = tableInfo.getDbFieldName(parts[0]);
    this.columnName = columnName == null ? DEFAULT_SORT_COLUMN : columnName;

    this.order = DEFAULT_SORT_ORDER;
    if(parts.length == 2 && parts[1].toUpperCase() == "ASC") {
      this.order = "ASC";
    }
  }
}
