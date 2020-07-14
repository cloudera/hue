// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors;

import com.cloudera.hue.querystore.eventProcessor.eventdefs.HiveHSEvent;

public interface HiveEventProcessor {
  ProcessingStatus process(HiveHSEvent event);
  HiveEventType[] validEvents();
}
