// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.entities;

import java.time.LocalDateTime;

import com.cloudera.hue.querystore.common.CompressionUtil;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.databind.node.ObjectNode;

import lombok.Data;
import lombok.ToString;

@Data
@ToString(of = {"id", "hiveQueryId"})  // removed all others as they are big objects
public class HiveQueryExtendedInfo implements JdbiEntity {
  private Long id;
  private Long hiveQueryId;

  @JsonIgnore
  private byte[] perfCompressed;
  @JsonIgnore
  private byte[] explainPlanCompressed;
  @JsonIgnore
  private byte[] configurationCompressed;

  @JsonIgnore
  private LocalDateTime createdAt;

  public ObjectNode getPerf() {
    return CompressionUtil.getInstance().getValue(perfCompressed, ObjectNode.class);
  }

  public void setPerf(ObjectNode perf) {
    perfCompressed = CompressionUtil.getInstance().compressValue(perf);
  }

  public ObjectNode getExplainPlan() {
    return CompressionUtil.getInstance().getValue(explainPlanCompressed, ObjectNode.class);
  }

  public void setExplainPlan(ObjectNode explainPlan) {
    explainPlanCompressed = CompressionUtil.getInstance().compressValue(explainPlan);
  }

  public ObjectNode getConfiguration() {
    return CompressionUtil.getInstance().getValue(configurationCompressed, ObjectNode.class);
  }

  public void setConfiguration(ObjectNode config) {
    configurationCompressed = CompressionUtil.getInstance().compressValue(config);
  }
}
