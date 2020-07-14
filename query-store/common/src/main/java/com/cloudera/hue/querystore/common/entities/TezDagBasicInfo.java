// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.entities;

import java.time.LocalDateTime;

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
public class TezDagBasicInfo implements JdbiEntity {

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

  public Long id;

  private String dagId;

  private String dagName;

  private String applicationId;

  private Long initTime;

  private Long startTime;

  private Long endTime;

  private String status;

  private String amWebserviceVer;

  private String amLogUrl;

  private String queueName;

  private String callerId;

  private String callerType;

  private Long hiveQueryId;

  @JsonIgnore
  private LocalDateTime createdAt;

  @JsonInclude(JsonInclude.Include.NON_NULL)
  private HiveQueryExtendedInfo details;

  private String sourceFile;

  public static enum Status {
    SUBMITTED, RUNNING, SUCCEEDED, FAILED, KILLED, ERROR
  }
}
