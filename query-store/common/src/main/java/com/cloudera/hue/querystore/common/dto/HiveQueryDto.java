// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dto;

import java.time.LocalDateTime;
import java.util.Collection;

import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.HiveQueryExtendedInfo;
import com.fasterxml.jackson.databind.node.ArrayNode;

import lombok.Getter;

@Getter
public class HiveQueryDto {

  private HiveQueryExtendedInfo details;
  private Collection<DagDto> dags;

  private final Long id;
  private final String queryId;
  private final Long startTime;
  private final String query;
  private final String highlightedQuery;
  private final Long endTime;
  private final Long elapsedTime;
  private final String status;
  private final String queueName;
  private final String userId;
  private final String requestUser;
  private final Long cpuTime;
  private final Long physicalMemory;
  private final Long virtualMemory;
  private final Long dataRead;
  private final Long dataWritten;
  private final String operationId;
  private final String clientIpAddress;
  private final String hiveInstanceAddress;
  private final String hiveInstanceType;
  private final String sessionId;
  private final String logId;
  private final String threadId;
  private final String executionMode;
  private final ArrayNode tablesRead;
  private final ArrayNode tablesWritten;
  private final ArrayNode databasesUsed;
  private final String domainId;
  private final String llapAppId;
  private final Boolean usedCBO;
  // private final Boolean processed;
  private final LocalDateTime createdAt;

  public HiveQueryDto(HiveQueryBasicInfo hiveQuery){
    this.id = hiveQuery.getId();
    this.queryId = hiveQuery.getQueryId();
    this.query = hiveQuery.getQuery();
    this.highlightedQuery = hiveQuery.getHighlightedQuery();
    this.startTime = hiveQuery.getStartTime();
    this.endTime = hiveQuery.getEndTime();
    this.elapsedTime = hiveQuery.getElapsedTime();
    this.status = hiveQuery.getStatus();
    this.queueName = hiveQuery.getQueueName();
    this.userId = hiveQuery.getUserId();
    this.requestUser = hiveQuery.getRequestUser();
    this.cpuTime = hiveQuery.getCpuTime();
    this.physicalMemory = hiveQuery.getPhysicalMemory();
    this.virtualMemory = hiveQuery.getVirtualMemory();
    this.dataRead = hiveQuery.getDataRead();
    this.dataWritten = hiveQuery.getDataWritten();
    this.operationId = hiveQuery.getOperationId();
    this.clientIpAddress = hiveQuery.getClientIpAddress();
    this.hiveInstanceAddress = hiveQuery.getHiveInstanceAddress();
    this.hiveInstanceType = hiveQuery.getHiveInstanceType();
    this.sessionId = hiveQuery.getSessionId();
    this.logId = hiveQuery.getLogId();
    this.threadId = hiveQuery.getThreadId();
    this.executionMode = hiveQuery.getExecutionMode();
    this.tablesRead = hiveQuery.getTablesRead();
    this.tablesWritten = hiveQuery.getTablesWritten();
    this.databasesUsed = hiveQuery.getDatabasesUsed();
    this.domainId = hiveQuery.getDomainId();
    this.llapAppId = hiveQuery.getLlapAppId();
    this.usedCBO = hiveQuery.isUsedCbo();
    // this.processed = hiveQuery.getProcessed();
    this.createdAt = hiveQuery.getCreatedAt();
  }

  public HiveQueryDto(HiveQueryBasicInfo hiveQuery, HiveQueryExtendedInfo details, Collection<DagDto> dags){
    this(hiveQuery);
    this.details = details;
    this.dags = dags;
  }

  public void setQueryDetails(HiveQueryExtendedInfo details) {
    this.details = details;
  }

  public void setDags(Collection<DagDto> dags) {
    this.dags = dags;
  }
}
