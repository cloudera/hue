// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.tez;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.Collections;
import java.util.Optional;

import org.apache.hadoop.fs.Path;
import org.apache.tez.common.ATSConstants;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import com.cloudera.hue.querystore.common.entities.VertexInfo;
import com.cloudera.hue.querystore.common.repository.VertexInfoRepository;
import com.cloudera.hue.querystore.eventProcessor.eventdefs.TezHSEvent;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventType;
import com.google.inject.Provider;

public class VertexConfigureDoneProcessorTest {

  private @Mock VertexInfoRepository vInfoRepo;
  private @Mock Provider<VertexInfoRepository> provider;
  private VertexConfigureDoneProcessor processor;

  @Before
  public void setUp() throws Exception {
    MockitoAnnotations.initMocks(this);
    when(provider.get()).thenReturn(vInfoRepo);
    processor = new VertexConfigureDoneProcessor(provider);
  }

  @Test
  public void testProcessUpdate() {
    String vertexId = "vertex_1";
    VertexInfo vInfo = new VertexInfo();
    vInfo.setVertexId(vertexId);
    when(vInfoRepo.findByVertexId(vertexId)).thenReturn(Optional.of(vInfo));

    TezHSEvent event = new TezHSEvent();
    event.setVertexId(vertexId);
    event.setEventType(TezEventType.VERTEX_CONFIGURE_DONE.name());
    event.setOtherInfo(Collections.singletonMap(ATSConstants.NUM_TASKS, "10"));
    ProcessingStatus status = processor.processValidEvent(event , new Path("/"));

    Assert.assertEquals(ProcessingStatus.Status.SUCCESS, status.getStatus());
    Assert.assertEquals(10, vInfo.getTaskCount());
    verify(vInfoRepo).save(vInfo);
  }

  @Test
  public void testProcessNoNumTasks() {
    String vertexId = "vertex_1";
    VertexInfo vInfo = new VertexInfo();
    vInfo.setVertexId(vertexId);
    vInfo.setTaskCount(3);
    when(vInfoRepo.findByVertexId(vertexId)).thenReturn(Optional.of(vInfo));

    TezHSEvent event = new TezHSEvent();
    event.setVertexId(vertexId);
    event.setEventType(TezEventType.VERTEX_CONFIGURE_DONE.name());
    event.setOtherInfo(Collections.emptyMap());
    ProcessingStatus status = processor.processValidEvent(event , new Path("/"));

    Assert.assertEquals(ProcessingStatus.Status.SUCCESS, status.getStatus());
    Assert.assertEquals(3, vInfo.getTaskCount());
    verify(vInfoRepo, times(0)).save(vInfo);
  }

  @Test
  public void testProcessNoVertex() {
    String vertexId = "vertex_1";
    when(vInfoRepo.findByVertexId(vertexId)).thenReturn(Optional.empty());

    TezHSEvent event = new TezHSEvent();
    event.setVertexId(vertexId);
    event.setEventType(TezEventType.VERTEX_CONFIGURE_DONE.name());
    event.setOtherInfo(Collections.singletonMap(ATSConstants.NUM_TASKS, "10"));
    ProcessingStatus status = processor.processValidEvent(event , new Path("/"));

    Assert.assertEquals(ProcessingStatus.Status.ERROR, status.getStatus());
    verify(vInfoRepo, times(0)).save(any());
  }
}
