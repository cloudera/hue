// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.debugBundler.framework;

import static org.mockito.Mockito.when;

import java.util.Collection;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import com.cloudera.hue.debugBundler.entities.history.DAGEntityType;
import com.cloudera.hue.debugBundler.entities.history.HistoryEntity;
import com.cloudera.hue.debugBundler.framework.Params.DagParams;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;

public class HistoryEventsArtifactTest {

  @Mock private ObjectMapper objectMapper;
  @Mock private HistoryEventReader.HistoryEventIterator iterator;
  @Mock private HistoryEventReader historyEventReader;

  private long NOW = new Date().getTime();

  private Configuration configuration = new Configuration();

  private DAGEntityType dagEntityType;
  private Path sourceFile = new Path("/test");
  private HistoryEventsArtifact historyEventsArtifact;

  @Before
  public void setUp() throws Exception {
    MockitoAnnotations.initMocks(this);

    dagEntityType = new DAGEntityType(configuration);

    historyEventsArtifact = new HistoryEventsArtifact(dagEntityType, sourceFile, new DagParams(0, null, null));
    historyEventsArtifact.historyEventReader = historyEventReader;

    when(historyEventReader.getIterator(sourceFile)).thenReturn(iterator);
  }

  @After
  public void tearDown() throws Exception {
  }

  private HistoryLoggerProtos.HistoryEventProto constructDagEvent(String dagId, String eventType, Map<String, String> dataMap) {
    HistoryLoggerProtos.HistoryEventProto.Builder builder = HistoryLoggerProtos.HistoryEventProto.newBuilder();
    builder.setEventType(eventType);
    builder.setDagId(dagId);
    builder.setAppId("app_" + dagId);
    builder.setEventTime(NOW);

    for (Map.Entry<String, String> item : dataMap.entrySet()) {
      HistoryLoggerProtos.KVPair.Builder kvBuilder = HistoryLoggerProtos.KVPair.newBuilder();
      kvBuilder.setKey(item.getKey());
      kvBuilder.setValue(item.getValue());
      builder.addEventData(kvBuilder.build());
    }

    return builder.build();
  }

  @Test
  public void readAndCompactEntities() throws Exception {
    when(iterator.hasNext())
      .thenReturn(true)
      .thenReturn(true)
      .thenReturn(true)
      .thenReturn(false);
    when(iterator.next())
      .thenReturn(constructDagEvent("dag_1", "DAG_SUBMITTED",
        ImmutableMap.of("d1_k1", "d1_v1", "d1_k2", "d1_v2")))
      .thenReturn(constructDagEvent("dag_2", "DAG_SUBMITTED",
        ImmutableMap.of("d2_k1", "d2_v1", "d2_k2", "d2_v2")))
      .thenReturn(constructDagEvent("dag_1", "DAG_INITIALIZED",
        ImmutableMap.of("d1_k3", "d1_v3", "d1_k4", "d1_v4")))
      .thenReturn(null);

    Collection<HistoryEntity> historyEntities = historyEventsArtifact.readAndCompactEntities();
    Iterator<HistoryEntity> iterator = historyEntities.iterator();

    Assert.assertEquals("Invalid number of entities", 2, historyEntities.size());

    HistoryEntity entity = iterator.next();
    Assert.assertEquals("Invalid entity id", "dag_1", entity.getEntityId());
    Assert.assertEquals("Invalid entity type", "DAG", entity.getEntityTypeName());

    Assert.assertEquals("Invalid event count", 2, entity.getEvents().size());
    Assert.assertEquals("Invalid entity time", Long.toString(NOW), entity.getEvents().get(0).get("eventTime"));
    Assert.assertEquals("Invalid entity time", Long.toString(NOW), entity.getEvents().get(1).get("eventTime"));

    Assert.assertEquals("Invalid entity time", "2", entity.getEvents().get(0).get("eventDataCount"));

    Assert.assertEquals("Invalid property count", 2, entity.getProperties().size());
    Assert.assertEquals("Invalid app id", "app_dag_1", entity.getProperties().get("appId"));
    Assert.assertEquals("Invalid dag id", "dag_1", entity.getProperties().get("dagId"));

    entity = iterator.next();
    Assert.assertEquals("Invalid entity", "dag_2", entity.getEntityId());
    Assert.assertEquals("Invalid entity type", "DAG", entity.getEntityTypeName());

    Assert.assertEquals("Invalid event count", 1, entity.getEvents().size());
    Assert.assertEquals("Invalid entity time", Long.toString(NOW), entity.getEvents().get(0).get("eventTime"));

    Assert.assertEquals("Invalid property count", 2, entity.getProperties().size());
    Assert.assertEquals("Invalid app id", "app_dag_2", entity.getProperties().get("appId"));
    Assert.assertEquals("Invalid dag id", "dag_2", entity.getProperties().get("dagId"));
  }

  @Test
  public void readAndCompactEntitiesTestProperties() throws Exception {
    final String APP_ID = "test_dag_1";
    final String APP_AT_ID = "test_dag_1";
    final String DAG_ID = "test_dag_1";
    final String VERTEX_ID = "test_dag_1";
    final String TASK_ID = "test_dag_1";
    final String TASK_AT_ID = "test_dag_1";
    final String USER = "test_user";

    HistoryLoggerProtos.HistoryEventProto.Builder builder1 = HistoryLoggerProtos.HistoryEventProto.newBuilder();
    builder1.setEventType("DAG_SUBMITTED").setDagId(DAG_ID)
      .setAppId(APP_ID)
      .setTaskId(TASK_ID)
      .setUser(USER);

    HistoryLoggerProtos.HistoryEventProto.Builder builder2 = HistoryLoggerProtos.HistoryEventProto.newBuilder();
    builder2.setEventType("DAG_INITIALIZED").setDagId(DAG_ID)
      .setAppAttemptId(APP_AT_ID)
      .setVertexId(VERTEX_ID)
      .setTaskAttemptId(TASK_AT_ID);

    //Properties from both builder1 & builder2 would be merged into one map
    when(iterator.hasNext())
      .thenReturn(true)
      .thenReturn(true)
      .thenReturn(false);
    when(iterator.next())
      .thenReturn(builder1.build())
      .thenReturn(builder2.build())
      .thenReturn(null);

    Collection<HistoryEntity> historyEntities = historyEventsArtifact.readAndCompactEntities();
    HashMap<String, String> properties = historyEntities.iterator().next().getProperties();

    Assert.assertEquals("Invalid number of entities", 1, historyEntities.size());

    Assert.assertEquals("Invalid appId value", APP_ID, properties.get("appId"));
    Assert.assertEquals("Invalid appAttemptId value", APP_AT_ID, properties.get("appAttemptId"));
    Assert.assertEquals("Invalid dagId value", DAG_ID, properties.get("dagId"));
    Assert.assertEquals("Invalid vertexId value", VERTEX_ID, properties.get("vertexId"));
    Assert.assertEquals("Invalid taskId value", TASK_ID, properties.get("taskId"));
    Assert.assertEquals("Invalid taskAttemptId value", TASK_AT_ID, properties.get("taskAttemptId"));
    Assert.assertEquals("Invalid user value", USER, properties.get("user"));
  }

}