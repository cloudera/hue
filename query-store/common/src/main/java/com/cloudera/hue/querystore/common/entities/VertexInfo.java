// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.entities;

import java.time.LocalDateTime;

import com.cloudera.hue.querystore.common.CompressionUtil;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import lombok.Data;

/**
 * Entity for representing the vertex information for a dag
 */
@Data
public class VertexInfo implements JdbiEntity {

  public Long id;

  private String name;
  private String vertexId;
  private Long dagId;
  private String domainId;

  private int taskCount;
  private int succeededTaskCount;
  private int completedTaskCount;
  private int failedTaskCount;
  private int killedTaskCount;
  private int failedTaskAttemptCount;
  private int killedTaskAttemptCount;

  private String className;

  private Long startTime;
  private Long endTime;

  private Long initRequestedTime;
  private Long startRequestedTime;

  private String status;

  @JsonIgnore
  private byte[] countersCompressed;
  @JsonIgnore
  private byte[] statsCompressed;
  @JsonIgnore
  private byte[] eventsCompressed;

  @JsonIgnore
  private LocalDateTime createdAt;

  public ArrayNode getCounters() {
    return CompressionUtil.getInstance().getValue(countersCompressed, ArrayNode.class);
  }

  public void setCounters(ArrayNode counters) {
    countersCompressed = CompressionUtil.getInstance().compressValue(counters);
  }

  public ObjectNode getStats() {
    return CompressionUtil.getInstance().getValue(statsCompressed, ObjectNode.class);
  }

  public void setStats(ObjectNode stats) {
    statsCompressed = CompressionUtil.getInstance().compressValue(stats);
  }

  public ArrayNode getEvents() {
    return CompressionUtil.getInstance().getValue(eventsCompressed, ArrayNode.class);
  }

  public void setEvents(ArrayNode events) {
    eventsCompressed = CompressionUtil.getInstance().compressValue(events);
  }
}
