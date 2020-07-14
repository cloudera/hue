// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.tez;

import java.util.Map;
import java.util.Optional;

import javax.inject.Inject;
import javax.inject.Provider;

import org.apache.hadoop.fs.Path;
import org.apache.tez.common.ATSConstants;

import com.cloudera.hue.querystore.common.entities.VertexInfo;
import com.cloudera.hue.querystore.common.repository.VertexInfoRepository;
import com.cloudera.hue.querystore.common.repository.transaction.DASTransaction;
import com.cloudera.hue.querystore.eventProcessor.eventdefs.TezHSEvent;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventType;
import com.cloudera.hue.querystore.eventProcessor.processors.util.ProcessorHelper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class VertexFinishedProcessor implements TezEventProcessor {

  private final ProcessorHelper helper;
  private final Provider<VertexInfoRepository> vertexInfoRepositoryProvider;

  @Inject
  public VertexFinishedProcessor(ProcessorHelper helper,
                                 Provider<VertexInfoRepository> vertexInfoRepositoryProvider) {
    this.helper = helper;
    this.vertexInfoRepositoryProvider = vertexInfoRepositoryProvider;
  }

  @Override
  @DASTransaction
  public ProcessingStatus processValidEvent(TezHSEvent event, Path filePath) {
    VertexInfoRepository vertexInfoRepository = vertexInfoRepositoryProvider.get();
    String vertexId = event.getVertexId();
    Optional<VertexInfo> vertexInfoOptional = vertexInfoRepository.findByVertexId(vertexId);
    if (vertexInfoOptional.isPresent()) {
      Map<String, String> otherInfo = event.getOtherInfo();
      VertexInfo vertexInfo = vertexInfoOptional.get();
      vertexInfo.setEndTime(event.getEventTime());
      vertexInfo.setStatus(otherInfo.get(ATSConstants.STATUS));
      vertexInfo.setCounters(getCounters(otherInfo.get(ATSConstants.COUNTERS)));
      vertexInfo.setStats(helper.parseData(otherInfo.get(ATSConstants.STATS), ObjectNode.class));

      // metrics
      vertexInfo.setCompletedTaskCount(
          Integer.valueOf(otherInfo.get(ATSConstants.NUM_COMPLETED_TASKS)));
      vertexInfo.setSucceededTaskCount(
          Integer.valueOf(otherInfo.get(ATSConstants.NUM_SUCCEEDED_TASKS)));
      vertexInfo.setFailedTaskCount(
          Integer.valueOf(otherInfo.get(ATSConstants.NUM_FAILED_TASKS)));
      vertexInfo.setKilledTaskCount(
          Integer.valueOf(otherInfo.get(ATSConstants.NUM_KILLED_TASKS)));

      vertexInfo.setFailedTaskAttemptCount(
          Integer.valueOf(otherInfo.get(ATSConstants.NUM_FAILED_TASKS_ATTEMPTS)));
      vertexInfo.setKilledTaskAttemptCount(
          Integer.valueOf(otherInfo.get(ATSConstants.NUM_KILLED_TASKS_ATTEMPTS)));
      vertexInfoRepository.save(vertexInfo);
    } else {
      log.error("Failed to get process event of type {}, Vertex info not found for id {}",
          event.getEventType(), vertexId);
      return new ProcessingStatus(new RuntimeException("Vertex info not found for id " + vertexId));
    }
    return ProcessingStatus.SUCCESS;
  }

  private ArrayNode getCounters(String counters) {
    ObjectNode countersNode = helper.parseData(counters, ObjectNode.class);
    return (ArrayNode) countersNode.get("counterGroups");
  }

  @Override
  public TezEventType[] validEvents() {
    return new TezEventType[] { TezEventType.VERTEX_FINISHED };
  }
}
