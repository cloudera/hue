// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.entities.history;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import javax.inject.Inject;

import org.apache.hadoop.conf.Configuration;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos;

public class DAGEntityType extends HistoryEntityType {

  public static final Set<String> EVENT_TYPES = new HashSet<>(Arrays.asList(
    "DAG_SUBMITTED",
    "DAG_INITIALIZED",
    "DAG_STARTED",
    "DAG_FINISHED",
    "DAG_KILL_REQUEST",
    "DAG_COMMIT_STARTED",
    "DAG_RECOVERED"
  ));

  @Inject
  public DAGEntityType(Configuration configuration) {
    super("DAG", "TEZ", EVENT_TYPES, configuration);
  }

  @Override
  public String getEntityId(HistoryLoggerProtos.HistoryEventProto event) {
    return event.getDagId();
  }

}
