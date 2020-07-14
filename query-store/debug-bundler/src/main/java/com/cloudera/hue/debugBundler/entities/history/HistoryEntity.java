// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.entities.history;

import java.util.ArrayList;
import java.util.HashMap;

public class HistoryEntity {
  private HistoryEntityType entityType;
  private String entityId;

  private HashMap<String, String> properties;
  private ArrayList<HashMap<String, String>> events;

  public HistoryEntity(HistoryEntityType entityType, String id) {
    this.entityType = entityType;
    this.entityId = id;

    this.events = new ArrayList<>();
    this.properties = new HashMap<>();
  }

  public String getEntityTypeName() {
    return entityType.getName();
  }

  public String getEntityId() {
    return entityId;
  }

  public ArrayList<HashMap<String, String>> getEvents() {
    return events;
  }

  public HashMap<String, String> getProperties() {
    return properties;
  }

  public void addEvent(HashMap<String, String> eventData) {
    events.add(eventData);
  }

  public void addProperties(HashMap<String, String> props) {
    properties.putAll(props);
  }
}
