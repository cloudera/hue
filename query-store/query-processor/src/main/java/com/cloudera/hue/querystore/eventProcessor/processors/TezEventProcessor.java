// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors;

import org.apache.hadoop.fs.Path;

import com.cloudera.hue.querystore.eventProcessor.eventdefs.TezHSEvent;

public interface TezEventProcessor {
  ProcessingStatus processValidEvent(TezHSEvent event, Path filePath);
  TezEventType[] validEvents();
}
