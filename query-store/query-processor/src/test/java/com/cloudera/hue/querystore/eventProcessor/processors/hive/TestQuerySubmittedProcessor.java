// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.hive;

import java.util.HashMap;

import javax.inject.Provider;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.HiveQueryExtendedInfo;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.HiveQueryExtendedInfoRepository;
import com.cloudera.hue.querystore.eventProcessor.eventdefs.HiveHSEvent;
import com.cloudera.hue.querystore.eventProcessor.processors.util.ProcessorHelper;
import com.fasterxml.jackson.databind.ObjectMapper;

public class TestQuerySubmittedProcessor {

  @Mock Provider<HiveQueryBasicInfoRepository> hiveQueryRepositoryProvider;

  @Mock Provider<HiveQueryExtendedInfoRepository> queryDetailsRepositoryProvider;

  private ProcessorHelper helper = new ProcessorHelper(new ObjectMapper());

  private QuerySubmittedProcessor querySubmittedProcessor;

  private ObjectMapper objectMapper = new ObjectMapper();

  @Before
  public void setUp() throws Exception {
    MockitoAnnotations.initMocks(this);
    querySubmittedProcessor = new QuerySubmittedProcessor(helper,
        hiveQueryRepositoryProvider, queryDetailsRepositoryProvider, objectMapper);
  }

  @Test
  public void enrichmentFromEvent() throws Exception {
    HiveHSEvent event = new HiveHSEvent();
    HiveQueryExtendedInfo queryDetails = new HiveQueryExtendedInfo();
    HiveQueryBasicInfo hiveQuery = new HiveQueryBasicInfo();

    event.setOtherInfo(new HashMap<>());
    querySubmittedProcessor.enrichFromEvent(event, hiveQuery, queryDetails);
    Assert.assertEquals("Invalid CBO check, expects No", false, hiveQuery.isUsedCbo());

    event.getOtherInfo().put("QUERY", "{\"queryText\":\"Text\", \"queryPlan\":{\"cboInfo\": \"Some text\"}}");
    querySubmittedProcessor.enrichFromEvent(event, hiveQuery, queryDetails);
    Assert.assertEquals("Invalid CBO check, expects Yes", true, hiveQuery.isUsedCbo());

    event.getOtherInfo().put("QUERY", "{\"queryText\":\"Text\", \"queryPlan\":{}}");
    querySubmittedProcessor.enrichFromEvent(event, hiveQuery, queryDetails);
    Assert.assertEquals("Invalid CBO check, expects No", false, hiveQuery.isUsedCbo());
  }

}