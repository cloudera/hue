// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.tez;

import java.util.Collection;
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
public class VertexStartedProcessor implements TezEventProcessor {

  private final Provider<VertexInfoRepository> vertexInfoRepositoryProvider;
  @Inject
  public VertexStartedProcessor(Provider<VertexInfoRepository> vertexInfoRepositoryProvider) {
    this.vertexInfoRepositoryProvider = vertexInfoRepositoryProvider;
  }

  @Override
  @DASTransaction
  public ProcessingStatus processValidEvent(TezHSEvent event, Path filePath) {
    VertexInfoRepository vertexInfoRepository = vertexInfoRepositoryProvider.get();
    Collection<VertexInfo> allByDagId = vertexInfoRepository.findAllByDagId(event.getDagId());

    Map<String, String> otherInfo = event.getOtherInfo();
    String vertexId = event.getVertexId();
    Optional<VertexInfo> vertexInfoOptional = allByDagId.stream()
        .filter(x -> x.getVertexId().equals(vertexId))
        .findFirst();
    if (vertexInfoOptional.isPresent()) {
      VertexInfo vertexInfo = vertexInfoOptional.get();
      vertexInfo.setStartRequestedTime(
          Long.valueOf(otherInfo.get(ATSConstants.START_REQUESTED_TIME)));
      vertexInfo.setStatus(otherInfo.get(ATSConstants.STATUS));
      vertexInfoRepository.save(vertexInfo);
    } else {
      log.error("Failed to get process event of type {}, Vertex info not found for id {}",
          event.getEventType(), vertexId);
      return new ProcessingStatus(new RuntimeException("Vertex info not found for id " + vertexId));
    }
    return ProcessingStatus.SUCCESS;
  }

  @Override
  public TezEventType[] validEvents() {
    return new TezEventType[]{TezEventType.VERTEX_STARTED};
  }
}
