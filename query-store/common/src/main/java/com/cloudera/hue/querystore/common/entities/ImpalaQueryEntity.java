// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.entities;

import com.cloudera.hue.querystore.orm.EntityTable;
import com.cloudera.hue.querystore.orm.annotation.ColumnInfo;
import com.cloudera.hue.querystore.orm.annotation.EntityFieldProcessor;
import com.cloudera.hue.querystore.orm.annotation.SearchQuery;

import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Entity for Impala Query
 */
@Data
@NoArgsConstructor
@SearchQuery(prefix = "iq", table="impala_query")
public class ImpalaQueryEntity implements JdbiEntity {
  public static final EntityTable TABLE_INFORMATION = EntityFieldProcessor.process(ImpalaQueryEntity.class);
  public ImpalaQueryEntity(
      Long id,

      String queryId,
      String queryText,
      String status,
      String queryType,

      Long startTime,
      Long endTime,
      Long duration,

      String userName,
      String coordinator,

      Long cpuTime,
      Long rowsProduced,
      Long peakMemory,
      Long hdfsBytesRead,

      String sourceFiles) {
    this.id = id;

    this.queryId = queryId;
    this.queryText = queryText;
    this.status = status;
    this.queryType = queryType;

    this.startTime = startTime;
    this.endTime = endTime;
    this.duration = duration;

    this.userName = userName;
    this.coordinator = coordinator;

    this.cpuTime = cpuTime;
    this.rowsProduced = rowsProduced;
    this.peakMemory = peakMemory;
    this.hdfsBytesRead = hdfsBytesRead;

    this.sourceFiles = sourceFiles;
  }

  @ColumnInfo(columnName="id", exclude = true, id=true)
  private Long id;

  // version field for tracking and failing on dirty writes
  @ColumnInfo(columnName="version", exclude = true)
  private Integer version;

  @ColumnInfo(columnName="query_id", searchable = true)
  private String queryId;

  @ColumnInfo(columnName="query_text", searchable = true)
  private String queryText;

  @ColumnInfo(columnName="status", searchable = true, sortable = true, facetable = true)
  private String status;

  @ColumnInfo(columnName="query_type", searchable = true, sortable = true, facetable = true)
  private String queryType;

  @ColumnInfo(columnName="start_time", searchable = true, sortable = true, rangeFacetable = true)
  private Long startTime;

  @ColumnInfo(columnName="end_time", searchable = true, sortable = true, rangeFacetable = true)
  private Long endTime;

  @ColumnInfo(columnName="duration", searchable = true, sortable = true, rangeFacetable = true)
  private Long duration;

  @ColumnInfo(columnName="user_name", searchable = true, sortable = true, facetable = true)
  private String userName;

  @ColumnInfo(columnName="coordinator", searchable = true, sortable = true, facetable = true)
  private String coordinator;

  @ColumnInfo(columnName="cpu_time", searchable = true, sortable = true, rangeFacetable = true)
  private Long cpuTime;

  @ColumnInfo(columnName="rows_produced", searchable = true, sortable = true, rangeFacetable = true)
  private Long rowsProduced;

  @ColumnInfo(columnName="peak_memory", searchable = true, sortable = true, rangeFacetable = true)
  private Long peakMemory;

  @ColumnInfo(columnName="hdfs_bytes_read", searchable = true, sortable = true, rangeFacetable = true)
  private Long hdfsBytesRead;

  @ColumnInfo(columnName="source_files")
  private String sourceFiles;

  public enum Status {
    STARTED, RUNNING, SUCCESS, ERROR
  }
}
