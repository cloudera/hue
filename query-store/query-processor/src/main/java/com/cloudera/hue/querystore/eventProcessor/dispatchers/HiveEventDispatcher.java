// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.dispatchers;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.inject.Inject;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.hive.conf.HiveConf.ConfVars;
import org.apache.hadoop.hive.ql.hooks.proto.HiveHookEvents.HiveHookEventProto;
import org.apache.hadoop.hive.ql.hooks.proto.HiveHookEvents.MapFieldEntry;

import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.cloudera.hue.querystore.eventProcessor.eventdefs.HiveHSEvent;
import com.cloudera.hue.querystore.eventProcessor.processors.HiveEventProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.HiveEventType;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.hue.querystore.eventProcessor.processors.hive.QueryCompletedProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.hive.QuerySubmittedProcessor;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class HiveEventDispatcher implements EventDispatcher<HiveHookEventProto> {

  private final Map<String, List<HiveEventProcessor>> processors = new HashMap<>();
  private final boolean splitEvents;

  @Inject
  public HiveEventDispatcher(QuerySubmittedProcessor submittedProcessor,
      QueryCompletedProcessor completedProcessor, DasConfiguration config, Configuration hadoopConfiguration) {
    HiveEventProcessor[] hiveProcs = {submittedProcessor, completedProcessor};
    for (HiveEventProcessor processor : hiveProcs) {
      for (HiveEventType evt : processor.validEvents()) {
        String name = evt.name().toUpperCase();
        List<HiveEventProcessor> list = processors.get(name);
        if (list == null) {
          list = new ArrayList<>();
          processors.put(name, list);
        }
        list.add(processor);
      }
    }
    try {
      String hiveBaseDir = config.getString(ConfVars.HIVE_PROTO_EVENTS_BASE_PATH.varname, null);
      this.splitEvents = new Path(hiveBaseDir).getFileSystem(hadoopConfiguration).getScheme().equals("s3a");
    } catch (IllegalArgumentException | IOException e) {
      throw new RuntimeException("Unexpected error while trying to read hive events path: ", e);
    }
  }

  @Override
  public ProcessingStatus process(HiveHookEventProto event, Path filePath, Long eventOffset) {
    if (!processors.containsKey(event.getEventType().toUpperCase())) {
      return ProcessingStatus.SKIP;
    }
    return processValidEvent(convert(event));
  }

  private HiveHSEvent convert(HiveHookEventProto hiveProtobufEvent) {
    HiveHSEvent hiveHSEvent = new HiveHSEvent();
    hiveHSEvent.setEventType(hiveProtobufEvent.getEventType().toString());
    hiveHSEvent.setHiveQueryId(hiveProtobufEvent.getHiveQueryId());
    hiveHSEvent.setTimestamp(hiveProtobufEvent.getTimestamp());
    hiveHSEvent.setExecutionMode(hiveProtobufEvent.getExecutionMode());
    hiveHSEvent.setUser(hiveProtobufEvent.getUser());
    hiveHSEvent.setRequestUser(hiveProtobufEvent.getRequestUser());
    hiveHSEvent.setQueue(hiveProtobufEvent.getQueue());
    hiveHSEvent.setOperationId(hiveProtobufEvent.getOperationId());
    hiveHSEvent.setTablesWritten(hiveProtobufEvent.getTablesWrittenList());
    hiveHSEvent.setTablesRead(hiveProtobufEvent.getTablesReadList());
    hiveHSEvent.setOtherInfo(convertListToMap(hiveProtobufEvent.getOtherInfoList()));
    return hiveHSEvent;
  }

  private Map<String, String> convertListToMap(List<MapFieldEntry> otherInfoList) {
    Map<String, String> otherInfo = new HashMap<>();
    for (MapFieldEntry info : otherInfoList) {
      otherInfo.put(info.getKey(), info.getValue());
    }
    return otherInfo;
  }

  private ProcessingStatus processValidEvent(HiveHSEvent event) {
    log.info("processing Event of type {}, ", event.getEventType());

    ProcessingStatus processingStatus = null;

    for (HiveEventProcessor processor : processors.get(event.getEventType().toUpperCase())) {
      processingStatus = processor.process(event);
      ProcessingStatus.Status status = processingStatus.getStatus();
      if (status == ProcessingStatus.Status.SUCCESS) {
        if (splitEvents) {
          processingStatus = ProcessingStatus.FINISH;
        }
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
