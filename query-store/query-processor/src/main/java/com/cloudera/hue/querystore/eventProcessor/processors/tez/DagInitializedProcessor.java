// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.tez;

import java.util.Collection;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

import javax.inject.Inject;
import javax.inject.Provider;

import org.apache.hadoop.fs.Path;
import org.apache.tez.common.ATSConstants;

import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.entities.TezDagExtendedInfo;
import com.cloudera.hue.querystore.common.entities.VertexInfo;
import com.cloudera.hue.querystore.common.repository.TezDagBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.VertexInfoRepository;
import com.cloudera.hue.querystore.common.repository.transaction.DASTransaction;
import com.cloudera.hue.querystore.eventProcessor.eventdefs.TezHSEvent;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventType;
import com.cloudera.hue.querystore.eventProcessor.processors.util.ProcessorHelper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class DagInitializedProcessor implements TezEventProcessor {

  private final ProcessorHelper helper;
  private final Provider<TezDagBasicInfoRepository> dagInfoRepositoryProvider;
  private final Provider<TezDagExtendedInfoRepository> dagDetailsRepositoryProvider;
  private final Provider<VertexInfoRepository> vertexInfoRepositoryProvider;

  @Inject
  public DagInitializedProcessor(ProcessorHelper helper,
                                 Provider<TezDagBasicInfoRepository> dagInfoRepositoryProvider,
                                 Provider<TezDagExtendedInfoRepository> dagDetailsRepositoryProvider,
                                 Provider<VertexInfoRepository> vertexInfoRepositoryProvider) {
    this.helper = helper;
    this.dagInfoRepositoryProvider = dagInfoRepositoryProvider;
    this.dagDetailsRepositoryProvider = dagDetailsRepositoryProvider;
    this.vertexInfoRepositoryProvider = vertexInfoRepositoryProvider;
  }

  @Override
  @DASTransaction
  public ProcessingStatus processValidEvent(TezHSEvent event, Path filePath) {
    TezDagBasicInfoRepository dagInfoRepository = dagInfoRepositoryProvider.get();
    TezDagExtendedInfoRepository dagDetailsRepository = dagDetailsRepositoryProvider.get();

    String dagId = event.getDagId();
    Optional<TezDagBasicInfo> dagInfoOptional = dagInfoRepository.findByDagId(dagId);

    // TODO: Change all event processors to accept events out of order too, which can happen
    // if new files are created because of different app attempts (recovery).
    if (!dagInfoOptional.isPresent()) {
      log.error("Dag Information not found for dag id: {}. Cannot process event", dagId);
      return new ProcessingStatus(new RuntimeException("Dag Info not found for dagId: " + dagId));
    }

    TezDagBasicInfo dagInfo = dagInfoOptional.get();

    Map<String, String> otherInfo = event.getOtherInfo();
    dagInfo.setInitTime(event.getEventTime());
    // TODO: We should add the following state
    // dagInfo.setStatus(DagInfo.Status.INITIALIZED.name());

    ObjectNode vertexNameIdMapping = helper.parseData(
        otherInfo.get(ATSConstants.VERTEX_NAME_ID_MAPPING), ObjectNode.class);

    Optional<TezDagExtendedInfo> dagDetailsOptional = dagDetailsRepository.findByDagId(dagId);
    if (dagDetailsOptional.isPresent()) {
      TezDagExtendedInfo dagDetails = dagDetailsOptional.get();
      dagDetails.setVertexNameIdMapping(vertexNameIdMapping);
      dagDetailsRepository.save(dagDetails);
    }

    createVerticesIfNotPresent(vertexNameIdMapping, dagInfo);

    dagInfoRepository.save(dagInfo);
    return ProcessingStatus.SUCCESS;
  }

  private void createVerticesIfNotPresent(ObjectNode vertexNameIdMapping, TezDagBasicInfo dagInfo) {
    VertexInfoRepository repository = vertexInfoRepositoryProvider.get();
    Collection<VertexInfo> allByDagId = repository.findAllByDagId(dagInfo.getDagId());

    Set<String> vertexIds = allByDagId.stream().map(VertexInfo::getVertexId).collect(Collectors.toSet());

    vertexNameIdMapping.fieldNames().forEachRemaining((x) -> {
      String vertexId = vertexNameIdMapping.get(x).asText();
      if(!vertexIds.contains(vertexId)) {
        VertexInfo vertexInfo = new VertexInfo();
        vertexInfo.setVertexId(vertexId);
        vertexInfo.setName(x);
        vertexInfo.setDagId(dagInfo.getId());
        vertexInfo.setCreatedAt(dagInfo.getCreatedAt());
        repository.save(vertexInfo);
      }
    });
  }

  @Override
  public TezEventType[] validEvents() {
    return new TezEventType[]{TezEventType.DAG_INITIALIZED};
  }
}
