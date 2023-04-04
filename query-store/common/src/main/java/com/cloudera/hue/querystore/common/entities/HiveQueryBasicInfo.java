// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.entities;

import java.time.LocalDateTime;

import com.cloudera.hue.querystore.orm.EntityTable;
import com.cloudera.hue.querystore.orm.annotation.ColumnInfo;
import com.cloudera.hue.querystore.orm.annotation.EntityFieldProcessor;
import com.cloudera.hue.querystore.orm.annotation.SearchQuery;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.databind.node.ArrayNode;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.FieldNameConstants;

/**
 * Entity for Hive Query
 */
@Data
@NoArgsConstructor
@FieldNameConstants
@SearchQuery(prefix = "hq", table="hive_query")
public class HiveQueryBasicInfo implements JdbiEntity {
  public static final EntityTable TABLE_INFORMATION = EntityFieldProcessor.process(HiveQueryBasicInfo.class);
  public HiveQueryBasicInfo(Long id,
                   String queryId,
                   String query,
                   String highlightedQuery,
                   Long startTime,
                   Long endTime,
                   Long elapsedTime,
                   String status,
                   String queueName,
                   String userId,
                   String requestUser,
                   Long cpuTime,
                   Long physicalMemory,
                   Long virtualMemory,
                   Long dataRead,
                   Long dataWritten,
                   String operationId,
                   String clientIpAddress,
                   String hiveInstanceAddress,
                   String hiveInstanceType,
                   String sessionId,
                   String logId,
                   String threadId,
                   String executionMode,
                   ArrayNode tablesRead,
                   ArrayNode tablesWritten,
                   ArrayNode databasesUsed,
                   String domainId,
                   String llapAppId,
                   boolean usedCBO,
                   Long firstTaskStartedTime,
                   Long waitingTime) {
    this.id = id;
    this.queryId = queryId;
    this.query = query;
    this.highlightedQuery = highlightedQuery;
    this.startTime = startTime;
    this.endTime = endTime;
    this.elapsedTime = elapsedTime;
    this.status = status;
    this.queueName = queueName;
    this.userId = userId;
    this.requestUser = requestUser;
    this.cpuTime = cpuTime;
    this.physicalMemory = physicalMemory;
    this.virtualMemory = virtualMemory;
    this.dataRead = dataRead;
    this.dataWritten = dataWritten;
    this.operationId = operationId;
    this.clientIpAddress = clientIpAddress;
    this.hiveInstanceAddress = hiveInstanceAddress;
    this.hiveInstanceType = hiveInstanceType;
    this.sessionId = sessionId;
    this.logId = logId;
    this.threadId = threadId;
    this.executionMode = executionMode;
    this.tablesRead = tablesRead;
    this.tablesWritten = tablesWritten;
    this.databasesUsed = databasesUsed;
    this.domainId = domainId;
    this.llapAppId = llapAppId;
    this.usedCbo = usedCBO;
    this.firstTaskStartedTime = firstTaskStartedTime;
    this.waitingTime = waitingTime;
  }

  @ColumnInfo(columnName="id", exclude = true, id=true)
  private Long id;

  @ColumnInfo(columnName="query_id", searchable = true, sortable = true)
  private String queryId;

  @ColumnInfo(columnName="query", tsVectorColumnName = "query_fts", highlightRequired = true,
	      highlightProjectionName = "highlighted_query")
  private String query;


  private String highlightedQuery;

  @ColumnInfo(columnName="start_time", searchable = true, sortable = true)
  private Long startTime;

  @ColumnInfo(columnName="end_time", searchable = true, sortable = true)
  private Long endTime;

  @ColumnInfo(columnName="elapsed_time", searchable = true, sortable = true, rangeFacetable = true)
  private Long elapsedTime;

  @ColumnInfo(columnName="status", searchable = true, sortable = true, facetable = true)
  private String status;

  @ColumnInfo(columnName="queue_name", searchable = true, sortable = true, facetable = true)
  private String queueName;

  @ColumnInfo(columnName="user_id", searchable = true, sortable = true, facetable = true)
  private String userId;

  @ColumnInfo(columnName="request_user", searchable = true, sortable = true, facetable = true)
  private String requestUser;

  @ColumnInfo(columnName="cpu_time", searchable = true, sortable = true, rangeFacetable = true)
  private Long cpuTime;

  @ColumnInfo(columnName="physical_memory", searchable = true, sortable = true, rangeFacetable = true)
  private Long physicalMemory;

  @ColumnInfo(columnName="virtual_memory", searchable = true, sortable = true, rangeFacetable = true)
  private Long virtualMemory;

  @ColumnInfo(columnName="data_read", searchable = true, sortable = true, rangeFacetable = true)
  private Long dataRead;

  @ColumnInfo(columnName="data_written", searchable = true, sortable = true, rangeFacetable = true)
  private Long dataWritten;

  @ColumnInfo(columnName="operation_id", searchable = true)
  private String operationId;

  @ColumnInfo(columnName="client_ip_address", searchable = true)
  private String clientIpAddress;

  @ColumnInfo(columnName="hive_instance_address", searchable = true)
  private String hiveInstanceAddress;

  @ColumnInfo(columnName="hive_instance_type", searchable = true)
  private String hiveInstanceType;

  @ColumnInfo(columnName="session_id", searchable = true)
  private String sessionId;

  @ColumnInfo(columnName="log_id", searchable = true)
  private String logId;

  @ColumnInfo(columnName="thread_id", searchable = true)
  private String threadId;

  @ColumnInfo(columnName="execution_mode", searchable = true, facetable = true)
  private String executionMode;

  @ColumnInfo(columnName="tables_read", searchable = true, facetable = false)
  private ArrayNode tablesRead;

  @ColumnInfo(columnName="tables_written", searchable = true, facetable = false)
  private ArrayNode tablesWritten;

  @ColumnInfo(columnName="databases_used", searchable = false, facetable = false)
  private ArrayNode databasesUsed;

  @ColumnInfo(columnName="domain_id", searchable = true)
  private String domainId;

  @ColumnInfo(columnName="llap_app_id", searchable = true)
  private String llapAppId;

  @ColumnInfo(columnName="used_cbo", searchable = true, facetable = true)
  private boolean usedCbo = false;

  @ColumnInfo(columnName="first_task_started_time", exclude = true)
  private Long firstTaskStartedTime;

  /*
   * This is a derived field. Its value is firstTaskStartedTime - startTime -
   *    (queryDetails.perf.parse + queryDetails.perf.compile + queryDetails.perf.TezBuildDag)
   */
  @ColumnInfo(columnName="waiting_time", searchable = true, sortable = true)
  private Long waitingTime;

  @JsonIgnore
  @ColumnInfo(columnName="created_at", exclude = true)
  private LocalDateTime createdAt;

  /*
   * its a derived field. its value is
   * Summations of total runtime across all containers / executors.
   * For Tez Queries : org.apache.tez.common.counters.TaskCounter:CPU_MILLIESECONDS +
   *        org.apache.tez.common.counters.DAGCounter:AM_CPU_MILLISECONDS
   * For LLAP Queries : org.apache.hadoop.hive.llap.counters.LlapWmCounters:SPECULATIVE_RUNNING_NS +
   *        org.apache.tez.common.counters.DAGCounter:AM_CPU_MILLISECONDS
   */
  @ColumnInfo(columnName="resource_utilization", searchable = true, sortable = true)
  private Long resourceUtilization;

  /**
   * version field for tracking and failing on dirty writes
    */
  @ColumnInfo(columnName="version", exclude = true)
  private Integer version;

  @JsonIgnore
  public boolean isComplete() {
    return status.equals(Status.SUCCESS.name()) || status.equals(Status.ERROR.name());
  }

  public enum Status {
    STARTED, RUNNING, SUCCESS, ERROR
  }
}
