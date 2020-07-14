// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.tez;

import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.io.IOException;
import java.util.Optional;

import javax.inject.Provider;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.HiveQueryExtendedInfo;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.HiveQueryExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagBasicInfoRepository;
import com.cloudera.hue.querystore.eventProcessor.eventdefs.TezHSEvent;
import com.cloudera.hue.querystore.eventProcessor.processors.util.ProcessorHelper;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

public class TaskStartedProcessorTest {

  @Mock
  private Provider<TezDagBasicInfoRepository> dagInfoRepositoryProvider;
  @Mock
  private Provider<HiveQueryBasicInfoRepository> hiveQueryRepositoryProvider;
  @Mock
  private Provider<HiveQueryExtendedInfoRepository> queryDetailsRepositoryProvider;
  @Mock
  private TezDagBasicInfoRepository dagInfoRepository;
  @Mock
  private HiveQueryBasicInfoRepository hiveQueryRepository;
  @Mock
  private HiveQueryExtendedInfoRepository queryDetailsRepository;

  private ObjectMapper objectMapper = new ObjectMapper();

  private ProcessorHelper processorHelper = new ProcessorHelper(objectMapper);

  private TaskStartedProcessor taskStartedProcessor;


  @Before
  public void setup(){
    MockitoAnnotations.initMocks(this);
    taskStartedProcessor = new TaskStartedProcessor(hiveQueryRepositoryProvider, dagInfoRepositoryProvider, queryDetailsRepositoryProvider, processorHelper);
    when(dagInfoRepositoryProvider.get()).thenReturn(dagInfoRepository);
    when(hiveQueryRepositoryProvider.get()).thenReturn(hiveQueryRepository);
    when(queryDetailsRepositoryProvider.get()).thenReturn(queryDetailsRepository);
  }

  @Test
  public void testProcessValidEvent() throws IOException {
    int parseTime = 1;
    int compileTime = 237;
    int tezBuildDag = 48;

    String perfJson = String.format("\n" +
        "{\n" +
        "  \"parse\": %s,\n" +
        "  \"compile\": %s,\n" +
        "  \"runTasks\": 786,\n" +
        "  \"TezRunDag\": 454,\n" +
        "  \"optimizer\": 0,\n" +
        "  \"TezBuildDag\": %s,\n" +
        "  \"TezCompiler\": 6,\n" +
        "  \"TezSubmitDag\": 15,\n" +
        "  \"TezGetSession\": 0,\n" +
        "  \"serializePlan\": 2,\n" +
        "  \"semanticAnalyze\": 218,\n" +
        "  \"RenameOrMoveFiles\": 1,\n" +
        "  \"TezRunVertex.Map 1\": 0,\n" +
        "  \"partition-retrieving\": 0,\n" +
        "  \"TezCreateVertex.Map 1\": 23,\n" +
        "  \"acquireReadWriteLocks\": 12,\n" +
        "  \"TezRunVertex.Reducer 2\": 0,\n" +
        "  \"TezCreateVertex.Reducer 2\": 19,\n" +
        "  \"RemoveTempOrDuplicateFiles\": 0,\n" +
        "  \"PreHook.org.apache.hadoop.hive.ql.hooks.HiveProtoLoggingHook\": 12,\n" +
        "  \"PostHook.org.apache.hadoop.hive.ql.stats.OperatorStatsReaderHook\": 0\n" +
        "}", parseTime, compileTime, tezBuildDag);

    TezHSEvent tezHSEvent = new TezHSEvent();
    String dagId = "some-dag-id";
    Long eventTime = 10000l;
    tezHSEvent.setDagId(dagId);
    tezHSEvent.setEventTime(eventTime);

    Long hiveQueryId = 1l;
    Long hiveStartTime = 5000l;
    HiveQueryBasicInfo hiveQuery = new HiveQueryBasicInfo();
    hiveQuery.setId(hiveQueryId);
    hiveQuery.setStartTime(hiveStartTime);

    HiveQueryExtendedInfo queryDetails = new HiveQueryExtendedInfo();
    queryDetails.setHiveQueryId(hiveQueryId);

    TezDagBasicInfo dagInfo = new TezDagBasicInfo();
    dagInfo.setDagId(dagId);
    dagInfo.setHiveQueryId(hiveQueryId);

    when(dagInfoRepository.findByDagId(dagId)).thenReturn(Optional.of(dagInfo));
    when(hiveQueryRepository.findOne(hiveQueryId)).thenReturn(Optional.of(hiveQuery));
    when(queryDetailsRepository.findByHiveQueryTableId(hiveQueryId)).thenReturn(Optional.of(queryDetails));

    JsonNode perfJsonNode = objectMapper.readTree(perfJson);
    queryDetails.setPerf((ObjectNode) perfJsonNode);

    taskStartedProcessor.processValidEvent(tezHSEvent, null);

//    first event.
    Assert.assertEquals(eventTime, hiveQuery.getFirstTaskStartedTime());
    Assert.assertEquals(Long.valueOf(eventTime - hiveStartTime - parseTime - tezBuildDag - compileTime), hiveQuery.getWaitingTime() );

    verify(hiveQueryRepository, times(1)).save(hiveQuery);

//    second event with early time.
    Long secondEventTime = 6000l;
    tezHSEvent.setEventTime(secondEventTime);

    taskStartedProcessor.processValidEvent(tezHSEvent, null);

    Assert.assertEquals(secondEventTime, hiveQuery.getFirstTaskStartedTime());
    Assert.assertEquals(Long.valueOf(secondEventTime - hiveStartTime - parseTime - tezBuildDag - compileTime), hiveQuery.getWaitingTime() );

    verify(hiveQueryRepository, times(2)).save(hiveQuery); // 1 earlier and second time now.

//    third event with late time.
    Long thirdEventTime = 7000l;
    tezHSEvent.setEventTime(thirdEventTime);

    taskStartedProcessor.processValidEvent(tezHSEvent, null);

    Assert.assertEquals(secondEventTime, hiveQuery.getFirstTaskStartedTime()); // same as before
    Assert.assertEquals(Long.valueOf(secondEventTime - hiveStartTime - parseTime - tezBuildDag - compileTime), hiveQuery.getWaitingTime() ); // same as before

    verify(hiveQueryRepository, times(2)).save(hiveQuery); // no new save invocations.
  }
}