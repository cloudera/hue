// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.hive;

import java.util.Map;
import java.util.Optional;

import javax.inject.Inject;
import javax.inject.Provider;

import org.apache.hadoop.hive.ql.hooks.HiveProtoLoggingHook;

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
import com.fasterxml.jackson.databind.node.ObjectNode;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class QueryCompletedProcessor implements HiveEventProcessor {
  private final ProcessorHelper helper;
  private final Provider<HiveQueryBasicInfoRepository> hiveQueryRepositoryProvider;
  private final Provider<HiveQueryExtendedInfoRepository> queryDetailsRepositoryProvider;

  @Inject
  public QueryCompletedProcessor(ProcessorHelper helper,
                                 Provider<HiveQueryBasicInfoRepository> hiveQueryRepositoryProvider,
                                 Provider<HiveQueryExtendedInfoRepository> queryDetailsRepositoryProvider) {
    this.helper = helper;
    this.hiveQueryRepositoryProvider = hiveQueryRepositoryProvider;
    this.queryDetailsRepositoryProvider = queryDetailsRepositoryProvider;
  }


  @Override
  @DASTransaction
  public ProcessingStatus process(HiveHSEvent event) {
    log.info("processing query completed event for {}", event.getHiveQueryId());
    HiveQueryBasicInfoRepository repository = hiveQueryRepositoryProvider.get();
    HiveQueryExtendedInfoRepository queryDetailsRepository = queryDetailsRepositoryProvider.get();
    String hiveQueryId = event.getHiveQueryId();
    Optional<HiveQueryBasicInfo> hiveQueryOptional = repository.findByHiveQueryId(hiveQueryId);
    if (!hiveQueryOptional.isPresent()) {
      log.error("No entry found in database for id {}. Cannot process completed event", hiveQueryId);
      return new ProcessingStatus(new RuntimeException(
          "No entry found in database for id '" + hiveQueryId + "'. Cannot process completed event"));
    }

    HiveQueryBasicInfo hiveQuery = hiveQueryOptional.get();

    hiveQuery.setEndTime(event.getTimestamp());

    Map<String, String> otherInfo = event.getOtherInfo();

    Optional<HiveQueryExtendedInfo> detailsOptional = queryDetailsRepository.findByHiveQueryId(hiveQueryId);
    if (detailsOptional.isPresent()) {
      HiveQueryExtendedInfo details = detailsOptional.get();
      String perf = otherInfo.get(HiveProtoLoggingHook.OtherInfoType.PERF.name());
      details.setPerf(helper.parseData(perf, ObjectNode.class));

      if(hiveQuery.getFirstTaskStartedTime() != null && hiveQuery.getFirstTaskStartedTime() > 0) {
        helper.updateWaitingTime(details, hiveQuery);
      }
      queryDetailsRepository.save(details);
    }

    Boolean status = Boolean.valueOf(
        otherInfo.get(HiveProtoLoggingHook.OtherInfoType.STATUS.name()));
    if(status){
      hiveQuery.setStatus(HiveQueryBasicInfo.Status.SUCCESS.toString());
    }else{
      hiveQuery.setStatus(HiveQueryBasicInfo.Status.ERROR.toString());
    }
    repository.save(hiveQuery);
    return ProcessingStatus.SUCCESS;
  }

  @Override
  public HiveEventType[] validEvents() {
    return new HiveEventType[] {HiveEventType.QUERY_COMPLETED};
  }
}
