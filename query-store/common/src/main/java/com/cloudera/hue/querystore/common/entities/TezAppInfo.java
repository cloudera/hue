// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.entities;

import java.time.LocalDateTime;

import com.cloudera.hue.querystore.common.CompressionUtil;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.databind.node.ObjectNode;

import lombok.Data;
import lombok.ToString;

@Data
@ToString(of = {"id", "appId", "submitTime"})
public class TezAppInfo implements JdbiEntity {
  private Long id;
  private String appId;
  private Long submitTime;

  @JsonIgnore
  private byte[] configCompressed;

  @JsonIgnore
  private LocalDateTime createdAt;

  public ObjectNode getConfig() {
    return CompressionUtil.getInstance().getValue(configCompressed, ObjectNode.class);
  }

  public void setConfig(ObjectNode config) {
    configCompressed = CompressionUtil.getInstance().compressValue(config);
  }
}
