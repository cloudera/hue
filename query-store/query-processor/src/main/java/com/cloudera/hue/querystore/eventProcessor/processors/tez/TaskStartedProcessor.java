// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.tez;

import java.util.Optional;

import javax.inject.Inject;
import javax.inject.Provider;

import org.apache.hadoop.fs.Path;

import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.HiveQueryExtendedInfo;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.HiveQueryExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagBasicInfoRepository;
import com.cloudera.hue.querystore.eventProcessor.eventdefs.TezHSEvent;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventType;
import com.cloudera.hue.querystore.eventProcessor.processors.util.ProcessorHelper;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class TaskStartedProcessor implements TezEventProcessor {

  private Provider<HiveQueryBasicInfoRepository> hiveQueryRepositoryProvider;
  private Provider<TezDagBasicInfoRepository> dagInfoRepositoryProvider;
  private Provider<HiveQueryExtendedInfoRepository> queryDetailsRepositoryProvider;
  private ProcessorHelper processorHelper;

  @Inject
  public TaskStartedProcessor(Provider<HiveQueryBasicInfoRepository> hiveQueryRepositoryProvider,
                              Provider<TezDagBasicInfoRepository> dagInfoRepositoryProvider,
                              Provider<HiveQueryExtendedInfoRepository> queryDetailsRepositoryProvider,
                              ProcessorHelper processorHelper) {
    this.hiveQueryRepositoryProvider = hiveQueryRepositoryProvider;
    this.dagInfoRepositoryProvider = dagInfoRepositoryProvider;
    this.queryDetailsRepositoryProvider = queryDetailsRepositoryProvider;
    this.processorHelper = processorHelper;
  }

  @Override
  public ProcessingStatus processValidEvent(TezHSEvent event, Path filePath) {
    Long eventTime = event.getEventTime();
    String dagId = event.getDagId();
    Optional<TezDagBasicInfo> dagInfo = dagInfoRepositoryProvider.get().findByDagId(dagId);
    if (dagInfo.isPresent()) {
      HiveQueryBasicInfoRepository hiveQueryRepository = hiveQueryRepositoryProvider.get();
      Optional<HiveQueryBasicInfo> hiveQueryOptional = hiveQueryRepository.findOne(dagInfo.get().getHiveQueryId());
      if (hiveQueryOptional.isPresent()) {
        HiveQueryBasicInfo hiveQuery = hiveQueryOptional.get();
        if (hiveQuery.getFirstTaskStartedTime() == null || hiveQuery.getFirstTaskStartedTime() > eventTime) {
          log.info("updating the hive_query with FirstTaskStartedTime : {} for id : {}", eventTime, hiveQuery.getId());
          hiveQuery.setFirstTaskStartedTime(eventTime);
          Optional<HiveQueryExtendedInfo> queryDetailsOptional = queryDetailsRepositoryProvider.get().findByHiveQueryTableId(hiveQuery.getId());
          queryDetailsOptional.ifPresent(queryDetails -> processorHelper.updateWaitingTime(queryDetails, hiveQuery));
          hiveQueryRepository.save(hiveQuery);
        }
      } else {
        log.error("Failed to find the HiveQuery for Dag Id: {}", dagId);
        return new ProcessingStatus(null);
      }
    } else {
      log.error("Failed to find the DagInfo for Dag Id: {} ", dagId);
      return new ProcessingStatus(null);
    }

    return ProcessingStatus.SUCCESS;
  }

  @Override
  public TezEventType[] validEvents() {
    return new TezEventType[]{TezEventType.TASK_STARTED};
  }
}
