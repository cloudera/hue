// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.entities.history;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import javax.inject.Inject;

import org.apache.hadoop.conf.Configuration;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos;

public class TaskAttemptEntityType extends HistoryEntityType {

  public static final Set<String> EVENT_TYPES = new HashSet<>(Arrays.asList(
    "TASK_ATTEMPT_STARTED",
    "TASK_ATTEMPT_FINISHED"
  ));

  @Inject
  public TaskAttemptEntityType(Configuration configuration) {
    super("TASK_ATTEMPT", "TEZ", EVENT_TYPES, configuration);
  }

  @Override
  public String getEntityId(HistoryLoggerProtos.HistoryEventProto event) {
    return event.getTaskAttemptId();
  }

}
