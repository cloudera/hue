// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.entities.history;

import java.util.Set;

import org.apache.hadoop.conf.Configuration;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos.HistoryEventProto;

public abstract class HistoryEntityType {

  private Configuration configuration;

  private final String name;
  private final String source;
  private final Set<String> eventTypes;

  public HistoryEntityType(String name, String source, Set<String> eventTypes, Configuration configuration) {
    this.name = name;
    this.source = source;
    this.eventTypes = eventTypes;

    this.configuration = configuration;
  }

  public Configuration getConfiguration() {
    return configuration;
  }

  public String getName() {
    return name;
  }

  public String getPath() {
    return source + "/" + name;
  }

  public boolean isRelatedEvent(String eventName) {
    return eventTypes.contains(eventName);
  }

  public abstract String getEntityId(HistoryEventProto event);
}
