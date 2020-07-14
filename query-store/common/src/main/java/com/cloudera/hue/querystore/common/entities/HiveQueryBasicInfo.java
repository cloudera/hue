// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.entities;

import java.time.LocalDateTime;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.databind.node.ArrayNode;

import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Entity for Hive Query
 */
@Data
@NoArgsConstructor
public class HiveQueryBasicInfo implements JdbiEntity {
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
    this.usedCBO = usedCBO;
    this.firstTaskStartedTime = firstTaskStartedTime;
    this.waitingTime = waitingTime;
  }

  private Long id;
  private String queryId;
  private String query;
  private String highlightedQuery;
  private Long startTime;
  private Long endTime;
  private Long elapsedTime;
  private String status;
  private String queueName;
  private String userId;
  private String requestUser;
  private Long cpuTime;
  private Long physicalMemory;
  private Long virtualMemory;
  private Long dataRead;
  private Long dataWritten;
  private String operationId;
  private String clientIpAddress;
  private String hiveInstanceAddress;
  private String hiveInstanceType;
  private String sessionId;
  private String logId;
  private String threadId;
  private String executionMode;
  private ArrayNode tablesRead;
  private ArrayNode tablesWritten;
  private ArrayNode databasesUsed;
  private String domainId;
  private String llapAppId;
  private boolean usedCBO = false;
  private Long firstTaskStartedTime;

  /*
   * This is a derived field. Its value is firstTaskStartedTime - startTime -
   *    (queryDetails.perf.parse + queryDetails.perf.compile + queryDetails.perf.TezBuildDag)
   */
  private Long waitingTime;

  @JsonIgnore
  private LocalDateTime createdAt;

  /*
   * its a derived field. its value is
   * Summations of total runtime across all containers / executors.
   * For Tez Queries : org.apache.tez.common.counters.TaskCounter:CPU_MILLIESECONDS +
   *        org.apache.tez.common.counters.DAGCounter:AM_CPU_MILLISECONDS
   * For LLAP Queries : org.apache.hadoop.hive.llap.counters.LlapWmCounters:SPECULATIVE_RUNNING_NS +
   *        org.apache.tez.common.counters.DAGCounter:AM_CPU_MILLISECONDS
   */
  private Long resourceUtilization;

  /**
   * version field for tracking and failing on dirty writes
    */
  private Integer version;

  @JsonIgnore
  public boolean isComplete() {
    return status.equals(Status.SUCCESS.name()) || status.equals(Status.ERROR.name());
  }

  public enum Status {
    STARTED, RUNNING, SUCCESS, ERROR
  }
}
