// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.dispatchers;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.inject.Inject;

import org.apache.hadoop.fs.Path;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos.HistoryEventProto;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos.KVPair;

import com.cloudera.hue.querystore.eventProcessor.eventdefs.TezHSEvent;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventType;
import com.cloudera.hue.querystore.eventProcessor.processors.tez.DagFinishedProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.tez.DagInitializedProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.tez.DagStartedProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.tez.DagSubmittedProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.tez.TaskAttemptFinishedProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.tez.TaskAttemptedProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.tez.TaskFinishedProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.tez.TaskStartedProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.tez.TezAppLaunchedEventProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.tez.VertexConfigureDoneProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.tez.VertexFinishedProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.tez.VertexInitializedProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.tez.VertexStartedProcessor;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class TezEventDispatcher implements EventDispatcher<HistoryEventProto> {
  private final Map<String, List<TezEventProcessor>> processors = new HashMap<>();

  @Inject
  public TezEventDispatcher(DagSubmittedProcessor dagSubmittedProcessor,
                             DagInitializedProcessor dagInitializedProcessor,
                             DagStartedProcessor dagStartedProcessor,
                             DagFinishedProcessor dagFinishedProcessor,
                             VertexInitializedProcessor vertexInitializedProcessor,
                             VertexStartedProcessor vertexStartedProcessor,
                             VertexConfigureDoneProcessor vertexConfigureDoneProcessor,
                             VertexFinishedProcessor vertexFinishedProcessor,
                             TaskAttemptedProcessor taskAttemptedProcessor,
                             TaskStartedProcessor taskStartedProcessor,
                             TaskAttemptFinishedProcessor taskAttemptFinishedProcessor,
                             TaskFinishedProcessor taskFinishedProcessor,
                             TezAppLaunchedEventProcessor appLaunchedEventProcessor) {
    TezEventProcessor tezProc[] = {
      dagSubmittedProcessor,
      dagInitializedProcessor,
      dagStartedProcessor,
      dagFinishedProcessor,
      vertexInitializedProcessor,
      vertexStartedProcessor,
      vertexConfigureDoneProcessor,
      vertexFinishedProcessor,
      taskAttemptedProcessor,
      taskStartedProcessor,
      taskAttemptFinishedProcessor,
      taskFinishedProcessor,
      appLaunchedEventProcessor
    };
    for (TezEventProcessor processor : tezProc) {
      for (TezEventType evt : processor.validEvents()) {
        String name = evt.name().toUpperCase();
        List<TezEventProcessor> list = processors.get(name);
        if (list == null) {
          list = new ArrayList<>();
          processors.put(name, list);
        }
        list.add(processor);
      }
    }
  }

  @Override
  public ProcessingStatus process(HistoryEventProto event, Path filePath) {
    if (!processors.containsKey(event.getEventType().toUpperCase())) {
      return ProcessingStatus.SKIP;
    }
    return processValidEvent(convert(event), filePath);
  }

  private TezHSEvent convert(HistoryEventProto tezProtobufEvent) {
    TezHSEvent tezHSEvent = new TezHSEvent();
    tezHSEvent.setEventType(tezProtobufEvent.getEventType().toString());
    tezHSEvent.setEventTime(tezProtobufEvent.getEventTime());
    tezHSEvent.setUser(tezProtobufEvent.getUser());
    tezHSEvent.setApplicationId(tezProtobufEvent.getAppId());
    tezHSEvent.setApplicationAttemptId(tezProtobufEvent.getAppAttemptId());
    tezHSEvent.setDagId(tezProtobufEvent.getDagId());
    tezHSEvent.setVertexId(tezProtobufEvent.getVertexId());
    tezHSEvent.setTaskId(tezProtobufEvent.getTaskId());
    tezHSEvent.setTaskAttemptId(tezProtobufEvent.getTaskAttemptId());
    tezHSEvent.setOtherInfo(convertListToMap(tezProtobufEvent.getEventDataList()));
    return tezHSEvent;
  }

  private Map<String, String> convertListToMap(List<KVPair> otherInfoList) {
    Map<String, String> otherInfo = new HashMap<>();
    for (KVPair info : otherInfoList) {
      otherInfo.put(info.getKey(), info.getValue());
    }
    return otherInfo;
  }

  private ProcessingStatus processValidEvent(TezHSEvent event, Path filePath) {
    log.info("processing Event of type {}, ", event.getEventType());
    ProcessingStatus processingStatus = null;
    for (TezEventProcessor processor : processors.get(event.getEventType().toUpperCase())) {
      processingStatus = processor.processValidEvent(event, filePath);
      ProcessingStatus.Status status = processingStatus.getStatus();
      if (status == ProcessingStatus.Status.SUCCESS || status == ProcessingStatus.Status.FINISH) {
        log.debug("Event of type {}, processed successfully", event.getEventType());
        break;
      } else if (status == ProcessingStatus.Status.ERROR) {
        log.error("Failed to process event of type {}", event.getEventType(), processingStatus.getError());
        break;
      }
    }

    if (processingStatus != null && processingStatus.getStatus() == ProcessingStatus.Status.SKIP) {
      log.info("No valid processor found for processing event of type {}", event.getEventType());
    }
    return processingStatus;
  }
}
