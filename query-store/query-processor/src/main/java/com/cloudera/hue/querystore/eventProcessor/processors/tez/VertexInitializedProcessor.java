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

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class VertexInitializedProcessor implements TezEventProcessor {
  private final Provider<VertexInfoRepository> vertexInfoRepositoryProvider;

  @Inject
  public VertexInitializedProcessor(Provider<VertexInfoRepository> vertexInfoRepositoryProvider) {
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
      vertexInfo.setStartTime(event.getEventTime());
      vertexInfo.setClassName(otherInfo.get(ATSConstants.PROCESSOR_CLASS_NAME));
      vertexInfo.setInitRequestedTime(
          Long.valueOf(otherInfo.get(ATSConstants.INIT_REQUESTED_TIME)));
      vertexInfo.setStatus("INITIALIZED");
      vertexInfo.setTaskCount(Integer.valueOf(otherInfo.get(ATSConstants.NUM_TASKS)));
      vertexInfoRepository.save(vertexInfo);
    } else {
      log.error("Failed to process event of type {}, Vertex info not found for id {}",
          event.getEventType(), vertexId);
      return new ProcessingStatus(new RuntimeException("Vertex info not found for id " + vertexId));
    }
    return ProcessingStatus.SUCCESS;
  }

  @Override
  public TezEventType[] validEvents() {
    return new TezEventType[] { TezEventType.VERTEX_INITIALIZED };
  }
}
