// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.eventdefs;

import java.util.Map;

public class TezHSEvent {
  private String eventType;
  private Long eventTime;
  private String user;
  private String applicationId;
  private String applicationAttemptId;
  private String dagId;
  private String vertexId;
  private String taskId;
  private String taskAttemptId;
  private Map<String, String> otherInfo;

  public String getEventType() {
    return eventType;
  }

  public void setEventType(String eventType) {
    this.eventType = eventType;
  }

  public Long getEventTime() {
    return eventTime;
  }

  public void setEventTime(Long eventTime) {
    this.eventTime = eventTime;
  }

  public String getUser() {
    return user;
  }

  public void setUser(String user) {
    this.user = user;
  }

  public String getApplicationId() {
    return applicationId;
  }

  public void setApplicationId(String applicationId) {
    this.applicationId = applicationId;
  }

  public String getApplicationAttemptId() {
    return applicationAttemptId;
  }

  public void setApplicationAttemptId(String applicationAttemptId) {
    this.applicationAttemptId = applicationAttemptId;
  }

  public String getDagId() {
    return dagId;
  }

  public void setDagId(String dagId) {
    this.dagId = dagId;
  }

  public String getVertexId() {
    return vertexId;
  }

  public void setVertexId(String vertexId) {
    this.vertexId = vertexId;
  }

  public String getTaskId() {
    return taskId;
  }

  public void setTaskId(String taskId) {
    this.taskId = taskId;
  }

  public String getTaskAttemptId() {
    return taskAttemptId;
  }

  public void setTaskAttemptId(String taskAttemptId) {
    this.taskAttemptId = taskAttemptId;
  }

  public Map<String, String> getOtherInfo() {
    return otherInfo;
  }

  public void setOtherInfo(Map<String, String> otherInfo) {
    this.otherInfo = otherInfo;
  }
}
