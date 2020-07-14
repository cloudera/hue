// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.eventdefs;

import java.util.List;
import java.util.Map;

public class HiveHSEvent {
  private String eventType;
  private String hiveQueryId;
  private long timestamp;
  private String executionMode;
  private String requestUser;
  private String user;
  private String queue;
  private String operationId;
  private List<String> tablesWritten;
  private List<String> tablesRead;
  private Map<String, String> otherInfo;

  public String getEventType() {
    return eventType;
  }

  public void setEventType(String eventType) {
    this.eventType = eventType;
  }

  public String getHiveQueryId() {
    return hiveQueryId;
  }

  public void setHiveQueryId(String hiveQueryId) {
    this.hiveQueryId = hiveQueryId;
  }

  public long getTimestamp() {
    return timestamp;
  }

  public void setTimestamp(long timestamp) {
    this.timestamp = timestamp;
  }

  public String getExecutionMode() {
    return executionMode;
  }

  public void setExecutionMode(String executionMode) {
    this.executionMode = executionMode;
  }

  public String getRequestUser() {
    return requestUser;
  }

  public void setRequestUser(String requestUser) {
    this.requestUser = requestUser;
  }

  public String getUser() {
    return user;
  }

  public void setUser(String user) {
    this.user = user;
  }

  public String getQueue() {
    return queue;
  }

  public void setQueue(String queue) {
    this.queue = queue;
  }

  public String getOperationId() {
    return operationId;
  }

  public void setOperationId(String operationId) {
    this.operationId = operationId;
  }

  public List<String> getTablesWritten() {
    return tablesWritten;
  }

  public void setTablesWritten(List<String> tablesWritten) {
    this.tablesWritten = tablesWritten;
  }

  public List<String> getTablesRead() {
    return tablesRead;
  }

  public void setTablesRead(List<String> tablesRead) {
    this.tablesRead = tablesRead;
  }

  public Map<String, String> getOtherInfo() {
    return otherInfo;
  }

  public void setOtherInfo(Map<String, String> otherInfo) {
    this.otherInfo = otherInfo;
  }
}
