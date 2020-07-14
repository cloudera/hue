// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.tez;

import javax.inject.Inject;
import javax.inject.Provider;

import org.apache.hadoop.fs.Path;
import org.apache.tez.common.ATSConstants;

import com.cloudera.hue.querystore.common.entities.TezAppInfo;
import com.cloudera.hue.querystore.common.repository.TezAppInfoRepository;
import com.cloudera.hue.querystore.eventProcessor.eventdefs.TezHSEvent;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventType;
import com.cloudera.hue.querystore.eventProcessor.processors.util.ProcessorHelper;
import com.fasterxml.jackson.databind.node.ObjectNode;

public class TezAppLaunchedEventProcessor implements TezEventProcessor {
  private final ProcessorHelper helper;
  private final Provider<TezAppInfoRepository> tezAppInfoRepoProvider;

  @Inject
  public TezAppLaunchedEventProcessor(ProcessorHelper helper, Provider<TezAppInfoRepository> tezAppInfoRepoProvider) {
    this.helper = helper;
    this.tezAppInfoRepoProvider = tezAppInfoRepoProvider;
  }

  @Override
  public ProcessingStatus processValidEvent(TezHSEvent event, Path filePath) {
    TezAppInfo appInfo = new TezAppInfo();
    appInfo.setAppId(event.getApplicationId());
    appInfo.setSubmitTime(event.getEventTime());
    appInfo.setConfig(helper.parseData(
        event.getOtherInfo().get(ATSConstants.CONFIG), ObjectNode.class));
    tezAppInfoRepoProvider.get().save(appInfo);
    return ProcessingStatus.SUCCESS;
  }

  @Override
  public TezEventType[] validEvents() {
    return new TezEventType[]{TezEventType.APP_LAUNCHED};
  }
}
