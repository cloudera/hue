// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.tez;

import javax.inject.Inject;

import org.apache.hadoop.fs.Path;

import com.cloudera.hue.querystore.eventProcessor.eventdefs.TezHSEvent;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventType;

public class TaskFinishedProcessor implements TezEventProcessor {

  @Inject
  public TaskFinishedProcessor() {
  }

  @Override
  public ProcessingStatus processValidEvent(TezHSEvent event, Path filePath) {
    // Nothing to do as of now
    return ProcessingStatus.SUCCESS;
  }

  @Override
  public TezEventType[] validEvents() {
    return new TezEventType[]{TezEventType.TASK_FINISHED};
  }
}
