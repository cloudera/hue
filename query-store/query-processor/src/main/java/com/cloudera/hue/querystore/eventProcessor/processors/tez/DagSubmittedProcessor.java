// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.tez;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Map;
import java.util.Optional;

import javax.inject.Inject;
import javax.inject.Provider;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.hive.ql.hooks.proto.HiveHookEvents.HiveHookEventProto;
import org.apache.hadoop.hive.ql.hooks.proto.HiveHookEvents.MapFieldEntry;
import org.apache.tez.common.ATSConstants;

import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.entities.TezDagExtendedInfo;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.transaction.DASTransaction;
import com.cloudera.hue.querystore.eventProcessor.dispatchers.HiveEventDispatcher;
import com.cloudera.hue.querystore.eventProcessor.eventdefs.TezHSEvent;
import com.cloudera.hue.querystore.eventProcessor.processors.HiveEventType;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventType;
import com.cloudera.hue.querystore.eventProcessor.processors.hive.QuerySubmittedProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.util.ProcessorHelper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class DagSubmittedProcessor implements TezEventProcessor {
  private final ProcessorHelper helper;
  private final Provider<HiveQueryBasicInfoRepository> hiveQueryRepositoryProvider;
  private final Provider<TezDagBasicInfoRepository> dagInfoRepositoryProvider;
  private final Provider<TezDagExtendedInfoRepository> dagDetailsRepositoryProvider;
  private final HiveEventDispatcher hiveEventDispatcher;

  @Inject
  public DagSubmittedProcessor(ProcessorHelper helper,
                               Provider<HiveQueryBasicInfoRepository> hiveQueryRepositoryProvider,
                               Provider<TezDagBasicInfoRepository> dagInfoRepositoryProvider,
                               Provider<TezDagExtendedInfoRepository> dagDetailsRepositoryProvider,
                               HiveEventDispatcher hiveEventDispatcher) {
    this.helper = helper;
    this.hiveQueryRepositoryProvider = hiveQueryRepositoryProvider;
    this.dagInfoRepositoryProvider = dagInfoRepositoryProvider;
    this.dagDetailsRepositoryProvider = dagDetailsRepositoryProvider;
    this.hiveEventDispatcher = hiveEventDispatcher;
  }

  @Override
  @DASTransaction
  public ProcessingStatus processValidEvent(TezHSEvent event, Path filePath) {
    HiveQueryBasicInfoRepository hiveQueryRepository = hiveQueryRepositoryProvider.get();
    TezDagBasicInfoRepository dagInfoRepository = dagInfoRepositoryProvider.get();
    TezDagExtendedInfoRepository dagDetailsRepository = dagDetailsRepositoryProvider.get();

    Map<String, String> otherInfo = event.getOtherInfo();

    // TODO: We should refine this further by CALLER_CONTEXT_TYPE.
    HiveQueryBasicInfo hiveQuery = null;
    String hiveQueryId = otherInfo.get(ATSConstants.CALLER_CONTEXT_ID);
    if (hiveQueryId != null) {
      Optional<HiveQueryBasicInfo> firstHiveQuery = hiveQueryRepository.findByHiveQueryId(hiveQueryId);
      if (!firstHiveQuery.isPresent()) {
        log.warn("Processing {} event for DagId: {}. Hive Query not found with id: {}. " +
            "Processing a dummy 'QUERY_SUBMITTED' event.", event.getEventType(), event.getDagId(),
            hiveQueryId);
        HiveHookEventProto eventProto = createDummyQuerySubmittedEvent(event);
        hiveEventDispatcher.process(eventProto, filePath, 0l);
        firstHiveQuery = hiveQueryRepository.findByHiveQueryId(hiveQueryId);
      }
      hiveQuery = firstHiveQuery.get();
    } else {
      log.warn("Caller context id is null for dag_id: {}", event.getDagId());
    }

    // Check if the dag information is already present, then update it.
    Optional<TezDagBasicInfo> firstDagInfo = dagInfoRepository.findByDagId(event.getDagId());

    TezDagBasicInfo dagInfo;
    if (firstDagInfo.isPresent()) {
      log.warn("Dag information for dag id {} already present. Updating the record.", event.getDagId());
      dagInfo = firstDagInfo.get();
    } else {
      dagInfo = new TezDagBasicInfo();
      dagInfo.setCreatedAt(LocalDateTime.now()); // Needs a revisit for timezone data.
    }

    dagInfo.setDagId(event.getDagId());
    dagInfo.setApplicationId(event.getApplicationId());
    dagInfo.setDagName(otherInfo.get(ATSConstants.DAG_NAME));
    dagInfo.setStartTime(event.getEventTime());
    dagInfo.setStatus(TezDagBasicInfo.Status.SUBMITTED.name());
    String appAttempId = event.getApplicationAttemptId();
    int ind = appAttempId.lastIndexOf('_');
    String attemptId = "0";
    if (ind > 0) {
      attemptId = appAttempId.substring(ind + 1);
    }

    dagInfo.setAmLogUrl(otherInfo.get(ATSConstants.IN_PROGRESS_LOGS_URL + "_" +  attemptId));
    if (hiveQuery != null) {
      dagInfo.setHiveQueryId(hiveQuery.getId());
      dagInfo.setCreatedAt(hiveQuery.getCreatedAt());
    } else {
      dagInfo.setCreatedAt(LocalDateTime.ofInstant(Instant.ofEpochMilli(event.getEventTime()), ZoneId.systemDefault()));
    }
    dagInfo.setQueueName(otherInfo.get(ATSConstants.DAG_QUEUE_NAME));
    dagInfo.setCallerId(otherInfo.get(ATSConstants.CALLER_CONTEXT_ID));
    dagInfo.setCallerType(otherInfo.get(ATSConstants.CALLER_CONTEXT_TYPE));
    dagInfo.setAmWebserviceVer(otherInfo.get(ATSConstants.DAG_AM_WEB_SERVICE_VERSION));
    dagInfo.setSourceFile(filePath.toString());
    dagInfoRepository.save(dagInfo);

    TezDagExtendedInfo dagDetails = null;
    Optional<TezDagExtendedInfo> dagDetailsOptional = dagDetailsRepository.findByDagId(event.getDagId());
    if (dagDetailsOptional.isPresent()) {
      dagDetails = dagDetailsOptional.get();
    } else {
      dagDetails = new TezDagExtendedInfo();
      if (hiveQuery != null) {
        dagDetails.setHiveQueryId(hiveQuery.getId());
      }
    }
    dagDetails.setDagInfoId(dagInfo.getId());
    dagDetails.setDagPlan(helper.parseData(otherInfo.get(ATSConstants.DAG_PLAN),
        ObjectNode.class));
    dagDetails.setCreatedAt(dagInfo.getCreatedAt());
    dagDetailsRepository.save(dagDetails);

    if (hiveQuery != null && dagInfo.getQueueName() != null) {
      hiveQuery.setQueueName(dagInfo.getQueueName());
      hiveQueryRepository.save(hiveQuery);
    }

    return ProcessingStatus.SUCCESS;
  }

  private HiveHookEventProto createDummyQuerySubmittedEvent(TezHSEvent event) {
    HiveHookEventProto.Builder builder = HiveHookEventProto.newBuilder();
    builder.setEventType(HiveEventType.QUERY_SUBMITTED.toString());
    Map<String, String> otherInfo = event.getOtherInfo();
    String hiveQueryId = otherInfo.get(ATSConstants.CALLER_CONTEXT_ID);
    builder.setHiveQueryId(hiveQueryId);
    builder.setTimestamp(event.getEventTime());
    builder.setUser(event.getUser());
    builder.setRequestUser(event.getUser());
    builder.addOtherInfo(
        MapFieldEntry.newBuilder().setKey(QuerySubmittedProcessor.DUMMY_EVENT_KEY).setValue("true").build());
    return builder.build();
  }

  @Override
  public TezEventType[] validEvents() {
    return new TezEventType[]{TezEventType.DAG_SUBMITTED};
  }
}
