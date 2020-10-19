// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.entities;

import java.time.LocalDateTime;

import com.cloudera.hue.querystore.orm.EntityTable;
import com.cloudera.hue.querystore.orm.annotation.ColumnInfo;
import com.cloudera.hue.querystore.orm.annotation.EntityFieldProcessor;
import com.cloudera.hue.querystore.orm.annotation.SearchQuery;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.ToString;

/**
 * Entity for representing the dag information
 */
@Data
@ToString(exclude = {"details"}) // excluded big objects
@NoArgsConstructor
@SearchQuery(prefix = "di", table="dag_info")
public class TezDagBasicInfo implements JdbiEntity {
  public static final EntityTable TABLE_INFORMATION = EntityFieldProcessor.process(TezDagBasicInfo.class);

  public TezDagBasicInfo(Long id,
                 String dagId,
                 String dagName,
                 String applicationId,
                 Long initTime,
                 Long startTime,
                 Long endTime,
                 String status,
                 String amWebserviceVer,
                 String amLogUrl,
                 String queueName,
                 String callerId,
                 String callerType) {
    this.id = id;
    this.dagId = dagId;
    this.dagName = dagName;
    this.applicationId = applicationId;
    this.initTime = initTime;
    this.startTime = startTime;
    this.endTime = endTime;
    this.status = status;
    this.amWebserviceVer = amWebserviceVer;
    this.amLogUrl = amLogUrl;
    this.queueName = queueName;
    this.callerId = callerId;
    this.callerType = callerType;
  }

  @ColumnInfo(columnName="id", exclude = true, id=true)
  public Long id;

  @ColumnInfo(columnName="dag_id", sortable = true, searchable = true)
  private String dagId;

  @ColumnInfo(columnName="dag_name", sortable = true, searchable = true)
  private String dagName;

  @ColumnInfo(columnName="application_id", searchable = true)
  private String applicationId;

  @ColumnInfo(columnName="init_time", fieldName = "dagInitTime")
  private Long initTime;

  @ColumnInfo(columnName="start_time", fieldName = "dagStartTime")
  private Long startTime;

  @ColumnInfo(columnName="end_time", fieldName = "dagEndTime")
  private Long endTime;

  @ColumnInfo(columnName="status", fieldName = "dagStatus")
  private String status;

  @ColumnInfo(columnName="am_webservice_ver", searchable = true)
  private String amWebserviceVer;

  @ColumnInfo(columnName="am_log_url", searchable = true)
  private String amLogUrl;

  @ColumnInfo(columnName="queue_name", sortable = true, searchable = true, fieldName = "dagQueueName")
  private String queueName;

  @ColumnInfo(columnName="caller_id", sortable = true, searchable = true)
  private String callerId;

  @ColumnInfo(columnName="caller_type", sortable = true)
  private String callerType;

  @ColumnInfo(columnName="hive_query_id")
  private Long hiveQueryId;

  @JsonIgnore
  @ColumnInfo(columnName="created_at", exclude = true)
  private LocalDateTime createdAt;

  @JsonInclude(JsonInclude.Include.NON_NULL)
  private HiveQueryExtendedInfo details;

  @ColumnInfo(columnName="source_file", sortable = true)
  private String sourceFile;

  public static enum Status {
    SUBMITTED, RUNNING, SUCCEEDED, FAILED, KILLED, ERROR
  }
}
