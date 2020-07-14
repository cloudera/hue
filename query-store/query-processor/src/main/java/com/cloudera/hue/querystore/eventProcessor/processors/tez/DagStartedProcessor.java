// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.tez;

import java.io.IOException;
import java.util.Map;
import java.util.Optional;

import javax.inject.Inject;
import javax.inject.Provider;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.tez.common.ATSConstants;
import org.apache.tez.dag.api.TezConfiguration;

import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.repository.TezDagBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.transaction.DASTransaction;
import com.cloudera.hue.querystore.eventProcessor.eventdefs.TezHSEvent;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventType;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class DagStartedProcessor implements TezEventProcessor {

  private final Provider<TezDagBasicInfoRepository> dagInfoRepositoryProvider;
  private final boolean splitEvents;

  @Inject
  public DagStartedProcessor(Provider<TezDagBasicInfoRepository> dagInfoRepositoryProvider,
      DasConfiguration config, Configuration hadoopConfiguration) {
    this.dagInfoRepositoryProvider = dagInfoRepositoryProvider;
    try {
      String tezBaseDir = config.getString(TezConfiguration.TEZ_HISTORY_LOGGING_PROTO_BASE_DIR, null);
      this.splitEvents = new Path(tezBaseDir).getFileSystem(hadoopConfiguration).getScheme().equals("s3a");
    } catch (IllegalArgumentException | IOException e) {
      throw new RuntimeException("Unexpected error while trying to read tez events path: ", e);
    }
  }

  @Override
  @DASTransaction
  public ProcessingStatus processValidEvent(TezHSEvent event, Path filePath) {
    TezDagBasicInfoRepository dagInfoRepository = dagInfoRepositoryProvider.get();

    String dagId = event.getDagId();
    Optional<TezDagBasicInfo> dagInfoOptional = dagInfoRepository.findByDagId(dagId);

    if (!dagInfoOptional.isPresent()) {
      log.error("Dag Information not found for dag id: {}. Cannot process event", dagId);
      return new ProcessingStatus(new RuntimeException("Dag Info not found for dagId: " + dagId));
    }

    TezDagBasicInfo dagInfo = dagInfoOptional.get();
    dagInfo.setStartTime(event.getEventTime());
    Map<String, String> otherInfo = event.getOtherInfo();
    String otherStatus = otherInfo.get(ATSConstants.STATUS);
    dagInfo.setStatus(TezDagBasicInfo.Status.valueOf(otherStatus.toUpperCase()).name());
    dagInfoRepository.save(dagInfo);
    return splitEvents ? ProcessingStatus.FINISH : ProcessingStatus.SUCCESS;
  }

  @Override
  public TezEventType[] validEvents() {
    return new TezEventType[]{TezEventType.DAG_STARTED};
  }
}
