// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors;

import org.apache.tez.dag.history.HistoryEventType;
import org.junit.Test;

public class TezEventTypeTest {
  @Test
  public void testEnumsValid() {
    for (TezEventType type : TezEventType.values()) {
      HistoryEventType.valueOf(type.name());
    }
  }
}
