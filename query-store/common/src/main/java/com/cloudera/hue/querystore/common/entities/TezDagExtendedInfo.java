// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.entities;

import java.time.LocalDateTime;

import com.cloudera.hue.querystore.common.CompressionUtil;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import lombok.Data;

@Data
public class TezDagExtendedInfo implements JdbiEntity {
  private Long id;
  private Long dagInfoId;
  private Long hiveQueryId;
  private String diagnostics;

  @JsonIgnore
  private byte[] dagPlanCompressed;
  @JsonIgnore
  private byte[] vertexNameIdMappingCompressed;
  @JsonIgnore
  private byte[] countersCompressed;

  @JsonIgnore
  private LocalDateTime createdAt;

  public ObjectNode getDagPlan() {
    return CompressionUtil.getInstance().getValue(dagPlanCompressed, ObjectNode.class);
  }

  public void setDagPlan(ObjectNode dagPlan) {
    dagPlanCompressed = CompressionUtil.getInstance().compressValue(dagPlan);
  }

  public ObjectNode getVertexNameIdMapping() {
    return CompressionUtil.getInstance().getValue(vertexNameIdMappingCompressed,
        ObjectNode.class);
  }

  public void setVertexNameIdMapping(ObjectNode mapping) {
    vertexNameIdMappingCompressed = CompressionUtil.getInstance().compressValue(mapping);
  }

  public ArrayNode getCounters() {
    return CompressionUtil.getInstance().getValue(countersCompressed, ArrayNode.class);
  }

  public void setCounters(ArrayNode counters) {
    countersCompressed = CompressionUtil.getInstance().compressValue(counters);
  }
}
