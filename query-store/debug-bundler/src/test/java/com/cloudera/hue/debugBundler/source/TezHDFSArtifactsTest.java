// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.source;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;

import org.apache.hadoop.conf.Configuration;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.MockitoAnnotations;

import com.cloudera.hue.debugBundler.entities.history.DAGEntityType;
import com.cloudera.hue.debugBundler.entities.history.HistoryEntity;
import com.cloudera.hue.debugBundler.entities.history.TaskAttemptEntityType;
import com.cloudera.hue.debugBundler.entities.history.TaskEntityType;
import com.cloudera.hue.debugBundler.entities.history.VertexEntityType;
import com.cloudera.hue.debugBundler.framework.Artifact;
import com.cloudera.hue.debugBundler.framework.HistoryEventsArtifact;
import com.cloudera.hue.debugBundler.framework.Params;
import com.cloudera.hue.debugBundler.framework.Params.DagParams;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.repository.TezDagBasicInfoRepository;
import com.fasterxml.jackson.databind.ObjectMapper;

public class TezHDFSArtifactsTest {

  @Mock private TezDagBasicInfoRepository dagBasicRepo;
  @Mock private ObjectMapper objectMapper;

  private Configuration configuration = new Configuration();

  private DAGEntityType dagEntityType;
  private VertexEntityType vertexEntityType;
  private TaskEntityType taskEntityType;
  private TaskAttemptEntityType taskAttemptEntityType;

  TezHDFSArtifacts tezHDFSArtifacts;

  @Before
  public void setUp() throws Exception {
    MockitoAnnotations.initMocks(this);

    dagEntityType = new DAGEntityType(configuration);
    vertexEntityType = new VertexEntityType(configuration);
    taskEntityType = new TaskEntityType(configuration);
    taskAttemptEntityType = new TaskAttemptEntityType(configuration);

    tezHDFSArtifacts = new TezHDFSArtifacts(dagBasicRepo, dagEntityType, vertexEntityType, taskEntityType,
        taskAttemptEntityType, objectMapper);
  }

  @After
  public void tearDown() throws Exception {
  }

  @Test
  public void getArtifacts() throws Exception {
    Params params = new Params();
    params.getDagParams().add(new DagParams(0, "dagId", null));

    Mockito.when(dagBasicRepo.findByDagId(Mockito.any())).thenReturn(Optional.empty());
    List<Artifact> artifacts = tezHDFSArtifacts.getArtifacts(params);
    Assert.assertEquals("Invalid number of artifacts", 0, artifacts.size());

    TezDagBasicInfo dagInfo = new TezDagBasicInfo();
    dagInfo.setSourceFile("/test");
    Mockito.when(dagBasicRepo.findByDagId(Mockito.any())).thenReturn(Optional.of(dagInfo));
    artifacts = tezHDFSArtifacts.getArtifacts(params);
    Assert.assertEquals("Invalid number of artifacts", 4, artifacts.size());
  }

  @Test
  public void updateParams() throws Exception {
    String nodeId = "ctr-e138-1518143905142-420783-01-000006.hwx.site:25454";

    Params params = new Params();
    DagParams param = new DagParams(0, "dagId", null);
    params.getDagParams().add(param);

    Artifact taskAttemptArtifact = new HistoryEventsArtifact(taskAttemptEntityType,
        new org.apache.hadoop.fs.Path("/test"), param);

    String taskAttemptKey = taskAttemptEntityType.getName().toLowerCase();

    HashMap<String, Object> dataMap = new HashMap<String, Object>();
    dataMap.put(taskAttemptKey, new ArrayList<HistoryEntity>());
    tezHDFSArtifacts.updateParams(params, taskAttemptArtifact, dataMap);
    Assert.assertTrue("Finish not set", param.getTaskLogs().isFinishedContainers());
    Assert.assertEquals("Log was added", 0, param.getTaskLogs().containersCount());

    params = new Params();
    param = new DagParams(0, "dagId", null);
    params.getDagParams().add(param);
    taskAttemptArtifact = new HistoryEventsArtifact(taskAttemptEntityType,
        new org.apache.hadoop.fs.Path("/test"), param);

    HashMap<String, String> hashMap = new HashMap<>();
    hashMap.put("completedLogsURL", "http://ctr-e138-1518143905142-420783-01-000003.hwx.site:8188/ws/v1/applicationhistory/containers/container_1532921752698_0002_01_000002/logs/hive_20180730071634_84e7218c-c6dd-439a-a153-607277a143b3-dag_1532921752698_0004_43.log.done?nm.id=" + nodeId + "\"");
    HistoryEntity historyEntity = new HistoryEntity(taskAttemptEntityType, "1");
    historyEntity.getEvents().add(hashMap);
    ArrayList<HistoryEntity> entities = new ArrayList<HistoryEntity>();
    entities.add(historyEntity);
    dataMap = new HashMap<String, Object>();
    dataMap.put(taskAttemptKey, entities);

    tezHDFSArtifacts.updateParams(params, taskAttemptArtifact, dataMap);
    Assert.assertTrue("Finish not set", param.getTaskLogs().isFinishedContainers());
    Assert.assertEquals("Log was not added", 1, param.getTaskLogs().containersCount());
  }

}