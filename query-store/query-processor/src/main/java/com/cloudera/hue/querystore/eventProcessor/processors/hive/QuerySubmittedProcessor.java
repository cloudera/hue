// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.hive;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Map;
import java.util.Optional;

import javax.inject.Inject;
import javax.inject.Provider;

import org.apache.hadoop.hive.ql.hooks.HiveProtoLoggingHook.OtherInfoType;

import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.HiveQueryExtendedInfo;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.HiveQueryExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.transaction.DASTransaction;
import com.cloudera.hue.querystore.eventProcessor.eventdefs.HiveHSEvent;
import com.cloudera.hue.querystore.eventProcessor.processors.HiveEventProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.HiveEventType;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.hue.querystore.eventProcessor.processors.util.ProcessorHelper;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class QuerySubmittedProcessor implements HiveEventProcessor {
  public static final String DUMMY_EVENT_KEY = "dummyEvent";

  @Data
  @AllArgsConstructor
  @NoArgsConstructor
  public static class QueryData {
    @JsonProperty("queryText")
    private String query;

    @JsonProperty("queryPlan")
    private ObjectNode explainPlan;
  }


  private final static String CBO_INFO_KEY = "cboInfo";

  private final ProcessorHelper helper;
  private final Provider<HiveQueryBasicInfoRepository> hqRepoProvider;
  private final Provider<HiveQueryExtendedInfoRepository> qdRepoProvider;

  private final ObjectMapper objectMapper;


  @Inject
  public QuerySubmittedProcessor(ProcessorHelper helper,
                                 Provider<HiveQueryBasicInfoRepository> hqRepoProvider,
                                 Provider<HiveQueryExtendedInfoRepository> qdRepoProvider, ObjectMapper objectMapper) {
    this.helper = helper;
    this.hqRepoProvider = hqRepoProvider;
    this.qdRepoProvider = qdRepoProvider;
    this.objectMapper = objectMapper;
  }

  @DASTransaction
  @Override
  public ProcessingStatus process(HiveHSEvent event) {
    HiveQueryBasicInfoRepository queryRepository = hqRepoProvider.get();
    HiveQueryExtendedInfoRepository queryDetailsRepository = qdRepoProvider.get();
    String hiveQueryId = event.getHiveQueryId();
    boolean isDummyEvent = isDummy(event);
    if (isDummyEvent) {
      log.info("Processing dummy query submitted event generated in the path for other events");
    }

    Optional<HiveQueryBasicInfo> queryOptional = queryRepository.findByHiveQueryId(hiveQueryId);
    Optional<HiveQueryExtendedInfo> queryDetails = queryDetailsRepository.findByHiveQueryId(hiveQueryId);

    if (queryOptional.isPresent()) {
      if (isDummyEvent) {
        log.warn("Hive Query with id {} is already present. Dummy event processing not required.", hiveQueryId);
        return ProcessingStatus.SUCCESS;
      } else {
        log.info("Hive Query with id {} is already present. Enriching the record.", hiveQueryId);
      }
    }

    HiveQueryExtendedInfo details = queryDetails.orElse(new HiveQueryExtendedInfo());
    HiveQueryBasicInfo query = queryOptional.orElse(new HiveQueryBasicInfo());

    enrichFromEvent(event, query, details);

    HiveQueryBasicInfo savedHiveQuery = queryRepository.save(query);
    details.setHiveQueryId(savedHiveQuery.getId());
    queryDetailsRepository.save(details);

    return ProcessingStatus.SUCCESS;
  }

  private boolean isDummy(HiveHSEvent event) {
    Map<String, String> otherInfo = event.getOtherInfo();
    String isDummy = otherInfo.getOrDefault(DUMMY_EVENT_KEY, "false");
    return Boolean.valueOf(isDummy);
  }

  @Override
  public HiveEventType[] validEvents() {
    return new HiveEventType[]{HiveEventType.QUERY_SUBMITTED};
  }

  @VisibleForTesting
  void enrichFromEvent(HiveHSEvent event, final HiveQueryBasicInfo query, final HiveQueryExtendedInfo details) {
    query.setQueryId(event.getHiveQueryId());
    query.setStartTime(event.getTimestamp());

    if (query.getStatus() == null) {
      query.setStatus(HiveQueryBasicInfo.Status.STARTED.toString());
    }

    query.setRequestUser(event.getRequestUser());
    query.setUserId(event.getUser());
    query.setExecutionMode(event.getExecutionMode());
    if (query.getQueueName() == null) {
      // if queue was not already set in dag flow before this update it.
      query.setQueueName(event.getQueue());
    }
    query.setOperationId(event.getOperationId());
    query.setTablesWritten(helper.processTablesReadWrite(event.getTablesWritten()));
    query.setTablesRead(helper.processTablesReadWrite(event.getTablesRead()));

    Map<String, Integer> dbUsed = helper.getDatabasesUsedInQuery(event.getTablesRead(), event.getTablesWritten() );

    query.setDatabasesUsed(objectMapper.createArrayNode().add(objectMapper.valueToTree(dbUsed)));

    Map<String, String> otherInfo = event.getOtherInfo();

    query.setThreadId(otherInfo.get(OtherInfoType.THREAD_NAME.name()));
    query.setSessionId(otherInfo.get(OtherInfoType.SESSION_ID.name()));
    query.setHiveInstanceAddress(otherInfo.get(OtherInfoType.HIVE_ADDRESS.name()));
    query.setUsedCbo(false);

    QueryData queryData = helper.parseData(
        otherInfo.get(OtherInfoType.QUERY.name()), QueryData.class);
    if (queryData != null) {
      query.setQuery(queryData.getQuery());

      ObjectNode explainPlan = queryData.getExplainPlan();
      details.setExplainPlan(explainPlan);

      if (explainPlan.has(CBO_INFO_KEY)) {
        query.setUsedCbo(true);
      }
      details.setExplainPlan(queryData.getExplainPlan());
    }

    details.setConfiguration(helper.parseData(
        otherInfo.get(OtherInfoType.CONF.name()), ObjectNode.class));

    query.setCreatedAt(LocalDateTime.ofInstant(Instant.ofEpochMilli(event.getTimestamp()), ZoneId.systemDefault()));
    details.setCreatedAt(query.getCreatedAt());
  }
}
