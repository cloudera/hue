// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.entities.history;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import javax.inject.Inject;

import org.apache.hadoop.conf.Configuration;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos;

public class VertexEntityType extends HistoryEntityType {

  public static final Set<String> EVENT_TYPES = new HashSet<>(Arrays.asList(
    "VERTEX_INITIALIZED",
    "VERTEX_STARTED",
    "VERTEX_CONFIGURE_DONE",
    "VERTEX_FINISHED",
    "VERTEX_COMMIT_STARTED",
    "VERTEX_GROUP_COMMIT_STARTED",
    "VERTEX_GROUP_COMMIT_FINISHED"
  ));

  @Inject
  public VertexEntityType(Configuration configuration) {
    super("VERTEX", "TEZ", EVENT_TYPES, configuration);
  }

  @Override
  public String getEntityId(HistoryLoggerProtos.HistoryEventProto event) {
    return event.getVertexId();
  }

}
