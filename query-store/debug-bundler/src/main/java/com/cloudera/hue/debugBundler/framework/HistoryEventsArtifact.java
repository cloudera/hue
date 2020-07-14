// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.framework;

import java.io.IOException;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;

import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos.HistoryEventProto;

import com.cloudera.hue.debugBundler.entities.history.HistoryEntity;
import com.cloudera.hue.debugBundler.entities.history.HistoryEntityType;
import com.cloudera.hue.debugBundler.framework.Params.DagParams;
import com.google.common.annotations.VisibleForTesting;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class HistoryEventsArtifact implements Artifact {
  private static final String FILE_EXT = ".json";

  private final org.apache.hadoop.fs.Path sourceFile;
  private final HistoryEntityType entityType;
  private final DagParams dagParams;

  @VisibleForTesting
  HistoryEventReader historyEventReader;

  public HistoryEventsArtifact(HistoryEntityType entityType, org.apache.hadoop.fs.Path sourceFile, DagParams dagParams) {
    this.entityType = entityType;
    this.sourceFile = sourceFile;
    this.dagParams = dagParams;

    this.historyEventReader = new HistoryEventReader(entityType.getConfiguration());
  }

  private HashMap<String, String> extractProperties(HistoryEventProto event) {
    HashMap<String, String> properties = new HashMap<>();

    if(event.hasAppId()) {
      properties.put("appId", event.getAppId());
    }

    if(event.hasAppAttemptId()) {
      properties.put("appAttemptId", event.getAppAttemptId());
    }

    if(event.hasDagId()) {
      properties.put("dagId", event.getDagId());
    }

    if(event.hasVertexId()) {
      properties.put("vertexId", event.getVertexId());
    }

    if(event.hasTaskId()) {
      properties.put("taskId", event.getTaskId());
    }

    if(event.hasTaskAttemptId()) {
      properties.put("taskAttemptId", event.getTaskAttemptId());
    }

    if(event.hasUser()) {
      properties.put("user", event.getUser());
    }

    return properties;
  }

  @VisibleForTesting
  Collection<HistoryEntity> readAndCompactEntities() {

    HashMap<String, HistoryEntity> entities = new HashMap<>();

    try (HistoryEventReader.HistoryEventIterator iterator = historyEventReader.getIterator(sourceFile)) {
      while (iterator.hasNext()) {
        HistoryEventProto event = iterator.next();

        String eventName = event.getEventType();
        if(entityType.isRelatedEvent(eventName)) {
          String entityId = entityType.getEntityId(event);

          HistoryEntity entity = entities.get(entityId);
          if(entity == null) {
            entity = new HistoryEntity(entityType, entityId);
            entities.put(entityId, entity);
          }

          entity.addProperties(extractProperties(event));

          HashMap<String, String> dataMap = constructDataMap(event.getEventDataList());
          dataMap.put("eventType", eventName);
          dataMap.put("eventDataCount", Integer.toString(event.getEventDataCount()));
          dataMap.put("eventTime", Long.toString(event.getEventTime()));
          entity.addEvent(dataMap);
        }
      }
    } catch (IOException e) {
      log.error("Error trying to create reader {}: ", e);
    }
    return entities.values();
  }

  private HashMap<String, String> constructDataMap(List<HistoryLoggerProtos.KVPair> dataMap) {
    HashMap<String, String> map = new HashMap<>();

    for (HistoryLoggerProtos.KVPair kvPair : dataMap) {
      map.put(kvPair.getKey(), kvPair.getValue());
    }

    return map;
  }

  @Override
  public String getName() {
    return dagParams.getDir(entityType.getPath() + FILE_EXT);
  }

  @Override
  public Object getData() throws ArtifactDownloadException {
    String entityTypeName = entityType.getName().toLowerCase();
    try {
      Collection<HistoryEntity> entities = readAndCompactEntities();
      HashMap<String, Object> data = new HashMap<String, Object>();
      data.put(entityTypeName, entities);
      return data;
    }
    catch(Exception e) {
      throw new ArtifactDownloadException("Error trying to fetch " + entityTypeName + " details.", e);
    }
  }

  @Override
  public Object getContext() {
    return dagParams;
  }
}
